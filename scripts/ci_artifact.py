"""Promote only checked site files from a successful same-repository PR run."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
from zipfile import ZipFile

WORKFLOW = '.github/workflows/site-quality-gates.yml'


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def site_digest(root):
    root = Path(root)
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Site artifacts must not contain symlinks')
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if any(part in ('.git', '.github') for part in path.relative_to(root).parts):
                raise ValueError('Repository metadata in site artifact')
            rows.append([relative, hashlib.sha256(path.read_bytes()).hexdigest()])
    if not rows or not (root / 'index.html').is_file():
        raise ValueError('Site artifact is empty or lacks index.html')
    return hashlib.sha256(json.dumps(rows, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True))


def eligible_pr(pr, repository, sha):
    return (pr.get('merged_at') and pr.get('merge_commit_sha') == sha
            and pr.get('base', {}).get('ref') == 'main'
            and pr.get('head', {}).get('repo', {}).get('full_name') == repository
            and pr.get('base', {}).get('repo', {}).get('full_name') == repository)


def valid_evidence(proof, run, repository, tree):
    return (isinstance(proof, dict) and proof.get('schema') == 1 and proof.get('repository') == repository
            and proof.get('run_id') == run['id'] and proof.get('run_attempt') == run['run_attempt']
            and proof.get('tree') == tree and bool(re.fullmatch(r'[a-f0-9]{64}', proof.get('site_digest', '')))
            and run.get('conclusion') == 'success' and run.get('event') == 'pull_request'
            and run.get('path') == WORKFLOW
            and run.get('repository', {}).get('full_name') == repository
            and run.get('head_repository', {}).get('full_name') == repository)


def read_proof(repository, artifact):
    if artifact.get('expired') or artifact.get('size_in_bytes', 0) > 1048576 or not re.fullmatch(r'sha256:[a-f0-9]{64}', artifact.get('digest', '')):
        return None
    with tempfile.TemporaryFile() as archive:
        subprocess.run(['gh', 'api', f'repos/{repository}/actions/artifacts/{artifact["id"]}/zip'],
                       stdout=archive, check=True)
        archive.seek(0)
        if hashlib.file_digest(archive, 'sha256').hexdigest() != artifact['digest'].split(':')[1]:
            raise ValueError('Evidence archive digest mismatch')
        archive.seek(0)
        with ZipFile(archive) as zipped:
            if zipped.namelist() != ['site-build-evidence.json']:
                raise ValueError('Unexpected evidence archive contents')
            if zipped.getinfo('site-build-evidence.json').file_size > 16384:
                raise ValueError('Oversized evidence')
            return json.loads(zipped.read('site-build-evidence.json'))


def find(repository, sha, tree):
    for pr in api(f'repos/{repository}/commits/{sha}/pulls'):
        if not eligible_pr(pr, repository, sha):
            continue
        head = pr['head']['sha']
        runs = api(f'repos/{repository}/actions/workflows/site-quality-gates.yml/runs?event=pull_request&head_sha={head}&status=success&per_page=20')['workflow_runs']
        for run in runs:
            if run.get('head_sha') != head:
                continue
            artifacts = api(f'repos/{repository}/actions/runs/{run["id"]}/artifacts')['artifacts']
            sites = [a for a in artifacts if a['name'] == 'site-build-output' and not a['expired']]
            evidence = [a for a in artifacts if a['name'] == 'site-build-evidence' and not a['expired']]
            if len(sites) != 1 or len(evidence) != 1:
                continue
            proof = read_proof(repository, evidence[0])
            if proof and valid_evidence(proof, run, repository, tree):
                return {'reuse': 'true', 'run_id': str(run['id']), 'tree': tree, 'site_digest': proof['site_digest']}
    return {'reuse': 'false'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['seal', 'find', 'verify'])
    parser.add_argument('--dist', default='dist')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    tree = git('rev-parse', 'HEAD^{tree}')
    if args.command == 'seal':
        proof = {'schema': 1, 'repository': os.environ['GITHUB_REPOSITORY'],
                 'run_id': int(os.environ['GITHUB_RUN_ID']), 'run_attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
                 'commit': git('rev-parse', 'HEAD'), 'tree': tree, 'site_digest': site_digest(args.dist)}
        args.output.write_text(json.dumps(proof) + '\n')
    elif args.command == 'verify':
        if tree != os.environ['EXPECTED_TREE'] or site_digest(args.dist) != os.environ['EXPECTED_DIGEST']:
            raise SystemExit('Checked site files or source tree changed; refusing deployment')
        print('Verified checked site files and exact merged source tree')
    else:
        try:
            result = find(os.environ['GITHUB_REPOSITORY'], git('rev-parse', 'HEAD'), tree)
        except (subprocess.CalledProcessError, ValueError, KeyError, TypeError):
            # Unavailable evidence cannot authorize reuse; perform a new complete build.
            result = {'reuse': 'false'}
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            for key, value in result.items():
                output.write(f'{key}={value}\n')
        print('Reuse checked PR site' if result['reuse'] == 'true' else 'No matching trusted artifact; build and verify normally')


if __name__ == '__main__':
    main()
