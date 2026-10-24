#!/usr/bin/env python3
"""Apply the generator's validation to actual saved digests before check/build."""
import argparse
import json
from pathlib import Path
from generate_digest import validate_digest
import generate_dev_digest as legacy


def check_directory(directory):
    errors = []
    seen = set()
    for path in sorted(Path(directory).glob('*.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            failures = validate_digest(data, seen_links=seen)
            if path.stem != data.get('date'):
                failures.append('filename must match digest date')
            errors.extend(f'{path.name}: {failure}' for failure in failures)
            if not failures:
                seen.update(legacy.normalize_url(a['url']) for a in data['articles'])
        except (OSError, ValueError, TypeError, AttributeError) as error:
            errors.append(f'{path.name}: cannot read digest ({type(error).__name__})')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path('src/content/digests'))
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f'digest directory does not exist: {args.directory}')
    errors = check_directory(args.directory)
    for error in errors:
        print('[error]', error)
    if not errors:
        print('[ok] All saved bilingual digests passed generation/publication validation.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
