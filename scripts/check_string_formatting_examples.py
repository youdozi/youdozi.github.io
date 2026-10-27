#!/usr/bin/env python3
"""Compile the paired article's standard example, and optionally its JDK 21 preview."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, help='JDK home for the standard example; defaults to JAVA_HOME or PATH')
    parser.add_argument('--preview-jdk', type=Path, help='Optional JDK 21 home for the historical preview')
    args = parser.parse_args()
    blocks = []
    for language in ('en', 'ko'):
        article = Path(f'src/content/posts/{language}/2023-09-23-jdk-21-string-templates.md').read_text()
        blocks.append(re.findall(r'```java\n([\s\S]*?)\n```', article))
    if blocks[0] != blocks[1] or len(blocks[0]) != 2:
        raise SystemExit('English and Korean articles must contain the same two complete Java examples.')

    def run(jdk, classname, code, preview=False):
        def tool(name):
            if jdk:
                return str(jdk / 'bin' / name)
            found = shutil.which(name)
            if not found:
                raise SystemExit(f'{name} is required.')
            return found
        version = subprocess.check_output([tool('javac'), '-version'], text=True).strip()
        if preview and not re.match(r'javac 21(?:\.|$)', version):
            raise SystemExit('The historical preview requires a JDK 21 compiler.')
        with tempfile.TemporaryDirectory(prefix='youdozi-formatting-') as directory:
            path = Path(directory)
            (path / f'{classname}.java').write_text(code)
            subprocess.run([tool('javac'), *(['--enable-preview', '--release', '21'] if preview else ['--release', '17']), f'{classname}.java'], cwd=path, check=True, timeout=30)
            expected = '2 plus 3 equals 5\n' if preview else '2 plus 3 equals 5\n' * 3 + "It's ready\n"
            locales = [[]] if preview else [[], ['-Duser.language=ar', '-Duser.country=EG']]
            for locale in locales:
                output = subprocess.check_output([tool('java'), *locale, *(['--enable-preview'] if preview else []), classname], cwd=path, text=True, timeout=30)
                if output != expected:
                    raise SystemExit(f'{classname}: unexpected output {output!r}')
            print(f'[ok] {classname}: {version}, output matched both published editions.')

    configured = args.jdk or (Path(os.environ['JAVA_HOME']) if os.environ.get('JAVA_HOME') else None)
    run(configured, 'FormattingExample', blocks[0][1])
    if args.preview_jdk:
        run(args.preview_jdk, 'Example', blocks[0][0], preview=True)
    else:
        print('[info] JDK 21 preview not executed; pass --preview-jdk to check it.')


if __name__ == '__main__':
    main()
