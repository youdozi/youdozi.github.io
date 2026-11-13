"""Check draft contracts and optionally run an existing public-release verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
PROGRAM_SHA256 = '31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8'
SOURCE_COMMIT = 'cff16a343bf5bb7953e5b65df6ab3600107e127d'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verifier', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--proof', type=Path)
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    text = (ROOT / 'article.ko.md').read_text()
    for name in ['verify-example.sh', 'tamper-example.sh']:
        pattern = r'^### `' + re.escape(name) + r'`\n\n```bash\n([\s\S]*?)\n```'
        blocks = re.findall(pattern, text, re.M)
        assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), name
        subprocess.run(['sh', '-n', str(ROOT / name)], check=True)
    for name in ['pickle-credentials-ko.svg', 'pickle-verification-ko.svg']:
        svg = ElementTree.parse(ROOT / name).getroot()
        assert svg.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
        assert not re.search(r'[\u3040-\u30ff]', ''.join(svg.itertext()))
        assert re.search(r'!\[[^\]]+\]\(\./' + re.escape(name) + r'\)', text)
    assert SOURCE_COMMIT in text and PROGRAM_SHA256 in text
    result = {'draftContractsPassed': True, 'sourceCommit': SOURCE_COMMIT,
              'programSHA256': PROGRAM_SHA256, 'verificationExecuted': False,
              'liveServiceAttestationChecked': False, 'iOSBinaryChecked': False,
              'phoneAppControlExecuted': False}
    if any([args.verifier, args.source, args.proof]):
        assert all([args.verifier, args.source, args.proof]), 'Provide verifier, source and proof together'
        assert hashlib.sha256(args.source.read_bytes()).hexdigest() == PROGRAM_SHA256
        command = [str(args.verifier), 'program', '--source', str(args.source), '--release', str(args.proof)]
        original = subprocess.run(command, capture_output=True, text=True, timeout=30)
        assert original.returncode == 0 and PROGRAM_SHA256 in original.stdout, original
        assert 'version 42' in original.stdout and 'ok' in original.stdout
        with tempfile.TemporaryDirectory(prefix='pickle-release-check-') as directory:
            changed = Path(directory) / 'changed-program.js'
            changed.write_bytes(args.source.read_bytes() + b'\n')
            command[3] = str(changed)
            altered = subprocess.run(command, capture_output=True, text=True, timeout=30)
            assert altered.returncode == 1 and 'source_hash' in altered.stdout + altered.stderr, altered
        result.update(verificationExecuted=True, originalExit=0, changedSourceExit=1,
                      originalOutput=original.stdout.strip(), changedSourceOutput=(altered.stdout + altered.stderr).strip())
    if args.result:
        args.result.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
