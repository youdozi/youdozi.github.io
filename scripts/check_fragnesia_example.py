#!/usr/bin/env python3
"""Execute the exact paired ZIP collector with synthetic OS/package responses only."""
import importlib.util
import json
from pathlib import Path
import re
import runpy
import subprocess
import tempfile
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
from build_example_archives import extract_example, catalog

KEY = '2026-10-31-fragnesia-cve-2026-46300'
RELEASE = '6.8.0-124-generic'
OS = {'ID': 'ubuntu', 'VERSION_ID': '24.04'}


def main():
    sources = []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        code = re.findall(r'^### `kernel-evidence.py`\n\n```python\n([\s\S]*?)\n```', text, re.M)
        assert len(code) == 1
        assert re.findall(r'^```sh\n([\s\S]*?)\n```', text, re.M) == ['python3 kernel-evidence.py']
        output = re.findall(r'^```text\n([\s\S]*?)\n```', text, re.M)
        assert len(output) == 1
        sources.append((code[0], output[0]))
    assert sources[0] == sources[1]
    assert next(r for r in catalog() if r['key'] == KEY)['commands'] == 'python3 kernel-evidence.py'
    names = ['linux-image-' + RELEASE, 'linux-image-unsigned-' + RELEASE]
    ok = subprocess.CompletedProcess([], 0, names[0] + '\t6.8.0-124.124\tinstalled\n', '')
    absent = subprocess.CompletedProcess([], 1, '', '')
    cases = []
    with tempfile.TemporaryDirectory(prefix='youdozi-fragnesia-') as temp:
        root = Path(temp)
        extract_example(KEY, root, {'kernel-evidence.py': sources[0][0]})
        path = root / 'kernel-evidence.py'
        spec = importlib.util.spec_from_file_location('kernel_evidence', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

        def execute(system='Linux', distro=OS, command='/usr/bin/dpkg-query', responses=None, os_error=None):
            with patch('platform.system', return_value=system), patch('platform.release', return_value=RELEASE), patch('platform.freedesktop_os_release', return_value=distro, side_effect=os_error), patch('shutil.which', return_value=command), patch('subprocess.run', side_effect=responses or [ok, absent]) as run:
                data, status = module.collect()
                assert data['patch_status'] == 'not-assessed', 'Inventory must never certify a patch'
                if system != 'Linux' or os_error or not command: run.assert_not_called()
                else:
                    assert run.call_count == 2
                    for i, call in enumerate(run.call_args_list):
                        argv = call.args[0]
                        assert argv[:2] == [command, '-W'] and argv[-1] == names[i]
                        assert argv[2].split(chr(9)) == ['-f=${Package}', '${Version}', '${db:Status-Status}' + chr(10)]
                        assert call.kwargs == dict(capture_output=True, text=True, timeout=5, check=False)
                return data, status

        data, status = execute(); assert status == 0 and data == json.loads(sources[0][1]); cases.append('documented-synthetic-output')
        data, status = execute(system='Darwin'); assert status == 2 and data['error'] == 'linux-required'; cases.append('non-linux-no-query')
        data, status = execute(os_error=OSError('fixture')); assert status == 2 and data['error'] == 'os-evidence-unavailable'; cases.append('missing-os-no-query')
        data, status = execute(command=None); assert status == 0 and data['package_query'] == 'dpkg-query-unavailable'; cases.append('missing-dpkg-no-verdict')
        variants = [
            ('not-found', absent),
            ('query-error', subprocess.CompletedProcess([], 2, '', 'fixture')),
            ('query-error', OSError('fixture')),
            ('query-error', subprocess.TimeoutExpired('fixture', 5)),
            ('unexpected-output', subprocess.CompletedProcess([], 0, 'bad\n', '')),
            ('unexpected-output', subprocess.CompletedProcess([], 0, 'other\t1\tinstalled\n', '')),
            ('not-installed', subprocess.CompletedProcess([], 0, names[0]+'\t1\tconfig-files\n', '')),
        ]
        for index, (expected, response) in enumerate(variants):
            data, status = execute(responses=[response, absent]); assert status == 0 and data['queries'][0]['state'] == expected
            cases.append('query-contract-'+str(index+1)+'-'+expected)
        output = StringIO()
        with patch('platform.system', return_value='Linux'), patch('platform.release', return_value=RELEASE), patch('platform.freedesktop_os_release', return_value=OS), patch('shutil.which', return_value='/usr/bin/dpkg-query'), patch('subprocess.run', side_effect=[ok, absent]), redirect_stdout(output):
            try: runpy.run_path(str(path), run_name='__main__')
            except SystemExit as result: assert result.code == 0
        assert output.getvalue().strip() == sources[0][1]; cases.append('literal-main-output-and-exit')
    print('[ok] '+str(len(cases))+' source-derived ZIP contracts: '+', '.join(cases))
    print('Synthetic OS/package evidence only; no host patching or exploit execution.')


if __name__ == '__main__':
    main()
