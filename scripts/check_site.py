#!/usr/bin/env python3
"""Check emitted HTML references and migration coverage without network access."""
from technical_publications import technical_records
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin
import json

ROOT = Path('dist').resolve()
SITE = 'https://youdozi.github.io'
LANGUAGES = json.loads(Path('src/lib/locales.json').read_text())['locales']


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()
        self.lang = None
        self.canonical = []
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'h1':
            self.h1 += 1
        for key in ('href', 'src'):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href'))


def main():
    errors = []
    expected_languages = {'en', 'ko'} | {json.loads(p.read_text())['language'] for p in Path('src/content/translations').glob('*.json')}
    expected_languages.update(record['language'] for record in technical_records(Path('.')).values())
    for lang in LANGUAGES:
        if (ROOT/lang/'index.html').exists() != (lang in expected_languages):
            errors.append(f'{lang}: language routes must match approved translations')
    pages = {}
    for file in ROOT.rglob('*.html'):
        if file.parent == ROOT and file.name.startswith(('google', 'naver')):
            continue  # Search-engine ownership files intentionally contain only verification text.
        page = Page(); page.feed(file.read_text(encoding='utf-8'))
        pages[file] = page
        if page.lang not in LANGUAGES:
            errors.append(f'{file.relative_to(ROOT)}: missing language')
        if len(page.canonical) != 1:
            errors.append(f'{file.relative_to(ROOT)}: must have exactly one canonical')
        if file.name != '404.html' and any(lang in file.relative_to(ROOT).parts[:1] for lang in LANGUAGES) and page.h1 != 1:
            errors.append(f'{file.relative_to(ROOT)}: expected one h1, found {page.h1}')
    for file, page in pages.items():
        base = SITE + '/' + file.relative_to(ROOT).as_posix()
        for ref in page.references:
            target = urlsplit(urljoin(base, ref))
            if target.scheme not in ('http', 'https') or target.netloc != 'youdozi.github.io':
                continue
            dest = ROOT / unquote(target.path).lstrip('/')
            if dest.is_dir():
                dest /= 'index.html'
            if not dest.is_file():
                errors.append(f'{file.relative_to(ROOT)}: missing target {ref}')
            elif target.fragment and dest in pages and unquote(target.fragment) not in pages[dest].ids:
                # Old taxonomy fragments are preserved separately in the migration redirects.
                errors.append(f'{file.relative_to(ROOT)}: missing anchor {ref}')
    for lang in LANGUAGES:
        if lang not in expected_languages and (ROOT/lang).exists():
            errors.append(f'{lang}: unpublished language has public output')
    ko = json.loads((ROOT/'ko/search-index.json').read_text())
    en = json.loads((ROOT/'en/search-index.json').read_text())
    indexes = {lang: json.loads((ROOT/lang/'search-index.json').read_text()) for lang in LANGUAGES if (ROOT/lang/'search-index.json').exists()}
    urls = [e['url'] for index in indexes.values() for e in index]
    if len(urls) != len(set(urls)):
        errors.append('duplicate article URLs in search indexes')
    legacy_count = len(list(Path('_posts').rglob('*.markdown')))
    examples = sum('reviewStatus: \"example\"' in p.read_text() for p in Path('src/content/posts/ko').glob('*.md'))
    if len(ko) + examples < legacy_count:
        errors.append(f'migration lost entries: {len(ko)} < {legacy_count}')
    # No build tools, source archives or evidence audit logs in the published tree.
    for name in ('scripts', '_posts', '.pipeline', 'Gemfile', 'package.json'):
        if (ROOT/name).exists():
            errors.append(f'non-public source included: {name}')
    for error in sorted(set(errors)):
        print('[error]', error)
    if not errors:
        counts = ', '.join(f'{lang}: {len(index)}' for lang, index in indexes.items())
        print(f'[ok] Published language indexes: {counts}')
        print(f'[ok] {len(pages)} HTML pages; {len(ko)} Korean / {len(en)} English listed entries; {examples} unlisted examples; internal links, images and anchors verified.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
