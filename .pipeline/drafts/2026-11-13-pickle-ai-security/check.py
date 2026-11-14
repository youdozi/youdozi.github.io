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
PROOF_SHA256 = 'e6571cfcb2f4c16db9185fc34ba21137214308925b2ba37f366df83bb4964e4b'


def verify_program(verifier, source, proof):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == PROGRAM_SHA256
    assert hashlib.sha256(proof.read_bytes()).hexdigest() == PROOF_SHA256
    command = [str(verifier), 'program', '--source', str(source), '--release', str(proof)]
    original = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert original.returncode == 0 and PROGRAM_SHA256 in original.stdout, original
    assert 'version 42' in original.stdout and 'ok' in original.stdout
    with tempfile.TemporaryDirectory(prefix='pickle-release-check-') as directory:
        changed = Path(directory) / 'changed-program.js'
        changed.write_bytes(source.read_bytes() + b'\n')
        command[3] = str(changed)
        altered = subprocess.run(command, capture_output=True, text=True, timeout=30)
        assert altered.returncode == 1 and 'source_hash' in altered.stdout + altered.stderr, altered
    return dict(verificationExecuted=True, originalExit=0, changedSourceExit=1,
                originalOutput=original.stdout.strip(), changedSourceOutput=(altered.stdout + altered.stderr).strip())


def download_and_verify():
    with tempfile.TemporaryDirectory(prefix='pickle-verifier-build-') as directory:
        scratch = Path(directory)
        repo = scratch / 'credential-enclave'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout',
                        'https://github.com/pickle-com/credential-enclave.git', str(repo)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', SOURCE_COMMIT], cwd=repo, check=True, timeout=30)
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        assert actual == SOURCE_COMMIT
        proof = scratch / 'secure-program.release.json'
        subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                        '--proto', '=https', '--tlsv1.2',
                        'https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json',
                        '--output', str(proof)], check=True, timeout=60)
        assert hashlib.sha256(proof.read_bytes()).hexdigest() == PROOF_SHA256
        target = scratch / 'target'
        subprocess.run(['cargo', '+1.100.0', 'build', '--locked', '-p', 'credential-enclave-verify',
                        '--target-dir', str(target)], cwd=repo, check=True, timeout=300)
        return verify_program(target / 'debug/credential-enclave-verify',
                              repo / 'secure-program/secure-program.js', proof)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verifier', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--proof', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--download-verifier', action='store_true')
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
    published = ROOT.parents[2] / 'src/content/posts/ko/2026-11-13-pickle-ai-security.md'
    if published.exists():
        body = lambda value: value.split('---\n', 2)[2]
        expected = body(text)
        for name in ['pickle-credentials-ko.svg', 'pickle-verification-ko.svg']:
            expected = expected.replace('./' + name, '/assets/img/architecture/' + name)
            assert (ROOT.parents[2] / 'assets/img/architecture' / name).read_bytes() == (ROOT / name).read_bytes(), name
        assert body(published.read_text()) == expected, 'Published body differs from draft'
    result = {'draftContractsPassed': True, 'sourceCommit': SOURCE_COMMIT,
              'programSHA256': PROGRAM_SHA256, 'verificationExecuted': False,
              'liveServiceAttestationChecked': False, 'iOSBinaryChecked': False,
              'phoneAppControlExecuted': False}
    if any([args.verifier, args.source, args.proof]):
        assert not args.download_verifier, 'Choose local or downloaded verifier'
        assert all([args.verifier, args.source, args.proof]), 'Provide verifier, source and proof together'
        result.update(verify_program(args.verifier, args.source, args.proof))
    elif args.download_verifier:
        result.update(download_and_verify())
    if args.result:
        args.result.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
