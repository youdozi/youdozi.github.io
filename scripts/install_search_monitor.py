#!/usr/bin/env python3
"""Install the current user's Monday 08:37 local search performance LaunchAgent."""
import argparse
import os
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'io.github.youdozi.search-performance'


def specification(root, home):
    output = home / '.local/share/blog-audits/search-monitor'
    return {'Label': LABEL, 'ProgramArguments': ['/bin/sh', str(root / 'scripts/run_search_monitor.sh')],
            'WorkingDirectory': str(root), 'StartCalendarInterval': {'Weekday': 1, 'Hour': 8, 'Minute': 37},
            'RunAtLoad': True, 'StartInterval': 3600,
            'StandardOutPath': str(output / 'weekly.stdout.log'), 'StandardErrorPath': str(output / 'weekly.stderr.log'),
            'ProcessType': 'Background', 'ExitTimeOut': 30, 'ThrottleInterval': 3600}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    home = Path.home(); spec = specification(ROOT, home)
    if not args.install:
        print(plistlib.dumps(spec).decode()); return
    if sys.platform != 'darwin': raise ValueError('LaunchAgent installation requires macOS')
    if not (ROOT / '.venv-search-console/bin/python').is_file(): raise ValueError('Existing search API virtualenv required')
    output = home / '.local/share/blog-audits/search-monitor'
    output.mkdir(parents=True, exist_ok=True, mode=0o700); output.chmod(0o700)
    agents = home / 'Library/LaunchAgents'; agents.mkdir(parents=True, exist_ok=True)
    path = agents / (LABEL + '.plist')
    if path.is_symlink(): raise ValueError('Refusing a symlink LaunchAgent')
    if path.exists() and plistlib.loads(path.read_bytes()).get('Label') != LABEL: raise ValueError('Existing LaunchAgent differs')
    domain = f'gui/{os.getuid()}'
    current = subprocess.run(['launchctl', 'print', domain + '/' + LABEL], capture_output=True)
    if current.returncode == 0:
        subprocess.run(['launchctl', 'bootout', domain + '/' + LABEL], check=True, capture_output=True)
    path.write_bytes(plistlib.dumps(spec)); path.chmod(0o600)
    subprocess.run(['launchctl', 'bootstrap', domain, str(path)], check=True, capture_output=True)
    print('Installed Monday 08:37 local-time performance monitor. Credentials remain local.')


if __name__ == '__main__':
    try: main()
    except Exception as error:
        print('LaunchAgent installation failed: ' + type(error).__name__, file=sys.stderr)
        raise SystemExit(1)
