#!/usr/bin/env python3
"""Build deterministic example ZIPs from published native articles, without network."""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'content/examples/downloads.json'
LANGUAGES = ('en', 'ko')
KEY = r'\d{4}-\d{2}-\d{2}-[a-z0-9.-]+'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    if (not isinstance(value, str) or not value or '\\' in value
            or not re.fullmatch(r'[A-Za-z0-9_./-]+', value)
            or PurePosixPath(value).is_absolute()
            or any(part in ('', '.', '..') for part in value.split('/'))):
        raise ValueError('Invalid example file path')
    return value


def catalog(root=ROOT):
    data = json.loads((Path(root) / CATALOG).read_text())
    if data.get('schemaVersion') != 1 or data.get('languages') != list(LANGUAGES) or not data.get('examples'):
        raise ValueError('Invalid example catalog')
    keys = [row['key'] for row in data['examples']]
    if len(set(keys)) != len(keys) or any(not re.fullmatch(KEY, key) or '..' in key for key in keys):
        raise ValueError('Invalid or duplicate example identity')
    for row in data['examples']:
        if not row.get('files') or not isinstance(row.get('commands'), str) or not row['commands'].strip():
            raise ValueError('Example files and reproduction commands are required')
        if any(not isinstance(row.get(field, {}).get(lang), str) or not row[field][lang].strip()
               for field in ('environment', 'scope') for lang in LANGUAGES):
            raise ValueError('Localized example instructions are required')
    return data['examples']


def scalar(head, field):
    values = re.findall(r'^' + field + r':[ \t]*([^\n]+)$', head, re.M)
    if len(values) != 1:
        raise ValueError('Expected one scalar article field')
    value = values[0].strip()
    if value.startswith('"'):
        value = json.loads(value)
        if not isinstance(value, str): raise ValueError('Expected string scalar')
    elif value.startswith("'"):
        if not re.fullmatch(r"'[^']*'", value): raise ValueError('Unsupported scalar quoting')
        value = value[1:-1]
    return value


def article(root, recipe, language):
    if language not in LANGUAGES or not re.fullmatch(KEY, recipe['key']) or '..' in recipe['key']:
        raise ValueError('Only native article editions have example archives')
    path = Path(root) / f'src/content/posts/{language}/{recipe["key"]}.md'
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError('Example source escapes repository')
    raw = path.read_bytes()
    match = re.fullmatch(r'---\n([\s\S]*?)\n---\n([\s\S]*)', raw.decode())
    if not match:
        raise ValueError('Missing article frontmatter')
    head, body = match.groups()
    # These registered articles use scalar identity fields. Fail closed if their
    # syntax changes; this is not a general YAML parser.
    for field, expected in [('language', language), ('translationKey', recipe['key']), ('routeSlug', recipe['key']),
                            ('kind', 'post'), ('reviewStatus', 'revised')]:
        if scalar(head, field) != expected:
            raise ValueError('Example source is not an eligible native article')
    published = datetime.fromisoformat(scalar(head, 'publishedAt').replace('Z', '+00:00'))
    if published.tzinfo is None or published > datetime.now(timezone.utc):
        raise ValueError('Unpublished article cannot supply a download')
    return raw, body


def project_files(recipe, language, root=ROOT):
    raw, body = article(root, recipe, language)
    files = {}
    for spec in recipe['files']:
        path = safe_path(spec['path'])
        if path in files or spec['language'] not in ('sh', 'python', 'java', 'groovy', 'yaml'):
            raise ValueError('Invalid or duplicate example file')
        fence = r'```' + re.escape(spec['language']) + r'\n([\s\S]*?)\n```[ \t]*(?=\n|$)'
        if spec['selector'] == 'heading':
            pattern = r'^### `' + re.escape(path) + r'`\n\n' + fence
        elif spec['selector'] == 'unique-fence':
            pattern = '^' + fence
        else:
            raise ValueError('Unknown example selector')
        matches = re.findall(pattern, body, re.M)
        if len(matches) != 1:
            raise ValueError(f'Expected one unambiguous source block: {language}/{recipe["key"]}/{path}')
        files[path] = (matches[0] + '\n').encode()
    for spec in recipe.get('inlineFiles', []):
        path = safe_path(spec['path'])
        if path in files or body.count('`' + spec['value'] + '`') != 1 or '\n' in spec['value']:
            raise ValueError('Inline project setup changed or is ambiguous')
        files[path] = (spec['value'] + '\n').encode()
    return raw, files


def archive_files(recipe, language, root=ROOT):
    raw, files = project_files(recipe, language, root)
    url = f'https://youdozi.github.io/{language}/posts/{recipe["key"]}/'
    if language == 'en':
        readme = f'Example files\n\nArticle: {url}\n\nExtract into a new empty directory and run commands from that directory.\n\nEnvironment\n{recipe["environment"][language]}\n\nCommands\n{recipe["commands"]}\n\nScope\n{recipe["scope"][language]}\n\nRead the article for outputs, conditions and failure cases. PROVENANCE.json records the source and file hashes; hashes establish identity, not correctness.\n'
    else:
        readme = f'예제 파일\n\n원문: {url}\n\n새 빈 디렉터리에 압축을 풀고 그 디렉터리에서 명령을 실행하세요.\n\n실행 환경\n{recipe["environment"][language]}\n\n명령\n{recipe["commands"]}\n\n확인 범위\n{recipe["scope"][language]}\n\n출력·적용 조건·실패 사례는 본문을 함께 읽으세요. PROVENANCE.json에는 원문과 파일 해시를 기록합니다. 해시는 파일의 일치를 확인하며 정확성을 보증하지 않습니다.\n'
    if any(name in files for name in ('README.txt', 'PROVENANCE.json')):
        raise ValueError('Reserved example metadata path')
    files['README.txt'] = readme.encode()
    provenance = {'schemaVersion': 1, 'article': url, 'sourceSha256': digest(raw),
                  'files': {path: digest(content) for path, content in sorted(files.items())}}
    files['PROVENANCE.json'] = (json.dumps(provenance, ensure_ascii=False, indent=2) + '\n').encode()
    return files


def archive_bytes(recipe, language, root=ROOT):
    stream = BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path, content in sorted(archive_files(recipe, language, root).items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return stream.getvalue()


def verified_members(blob, recipe, language, root=ROOT):
    expected = archive_files(recipe, language, root)
    with zipfile.ZipFile(BytesIO(blob)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError('Archive members differ from the source project')
        for info in archive.infolist():
            safe_path(info.filename)
            if info.external_attr >> 16 != 0o100644 or archive.read(info) != expected[info.filename]:
                raise ValueError('Archive content or file type differs from the source')
    return expected


def extract_example(key, directory, expected, root=ROOT):
    """Execution checks consume ZIP bytes, independently comparing source files."""
    recipe = next(row for row in catalog(root) if row['key'] == key)
    members = verified_members(archive_bytes(recipe, 'en', root), recipe, 'en', root)
    code = {name: content for name, content in members.items() if name not in ('README.txt', 'PROVENANCE.json')}
    if not set(expected).issubset(code) or any(code[name] != (text + '\n').encode() for name, text in expected.items()):
        raise ValueError('ZIP project differs from independently extracted article code')
    for name, content in members.items():
        path = Path(directory) / safe_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def generate(output, root=ROOT):
    output = Path(output)
    if output.is_symlink():
        raise ValueError('Example output must not be a symlink')
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'manifest.json').is_symlink():
        raise ValueError('Example manifest must not be a symlink')
    archives = {}
    for recipe in catalog(root):
        if project_files(recipe, 'en', root)[1] != project_files(recipe, 'ko', root)[1]:
            raise ValueError('Paired example code differs')
        for language in LANGUAGES:
            name = f'{recipe["key"]}-{language}.zip'
            if (output / name).is_symlink():
                raise ValueError('Example ZIP output must not be a symlink')
            blob = archive_bytes(recipe, language, root)
            verified_members(blob, recipe, language, root)
            (output / name).write_bytes(blob)
            archives[name] = {'sha256': digest(blob), 'bytes': len(blob)}
    # Remove only files in this generator's namespace, never arbitrary output data.
    for path in output.iterdir():
        if re.fullmatch(KEY + r'-(?:en|ko)\.zip', path.name) and path.name not in archives:
            path.unlink()
    manifest = {'schemaVersion': 1, 'archives': archives}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


class Downloads(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'example-download' in attrs.get('class', '').split():
            self.links.append((attrs.get('href'), 'download' in attrs))


def check_dist(dist, root=ROOT):
    dist = Path(dist)
    directory = dist / 'assets/examples'
    manifest = json.loads((directory / 'manifest.json').read_text())
    expected = {}
    for recipe in catalog(root):
        for language in LANGUAGES:
            name = f'{recipe["key"]}-{language}.zip'
            blob = (directory / name).read_bytes()
            verified_members(blob, recipe, language, root)
            if blob != archive_bytes(recipe, language, root):
                raise ValueError('Published example archive is not deterministic')
            expected[name] = {'sha256': digest(blob), 'bytes': len(blob)}
    if manifest != {'schemaVersion': 1, 'archives': expected} or {p.name for p in directory.iterdir()} != set(expected) | {'manifest.json'}:
        raise ValueError('Published example archive set differs from the catalog')
    links = 0
    for file in dist.rglob('*.html'):
        page = Downloads(); page.feed(file.read_text())
        relative = file.relative_to(dist).as_posix()
        match = re.fullmatch(r'(en|ko)/posts/(' + KEY + r')/index\.html', relative)
        name = f'{match[2]}-{match[1]}.zip' if match else None
        wanted = [('/assets/examples/' + name, True)] if name in expected else []
        if page.links != wanted:
            raise ValueError('Download link differs from the eligible article: ' + relative)
        links += len(page.links)
    if links != len(expected):
        raise ValueError('Missing example article routes')
    return {'archives': len(expected), 'articleDownloadLinks': links, 'networkRequests': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--output', type=Path)
    group.add_argument('--check-dist', type=Path)
    args = parser.parse_args()
    try:
        result = check_dist(args.check_dist) if args.check_dist else {'archives': len(generate(args.output or ROOT / 'public/assets/examples')['archives']), 'networkRequests': 0}
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print('[error] Example archives:', error); return 1
    print('[ok] Example archives:', json.dumps(result)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
