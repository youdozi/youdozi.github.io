#!/usr/bin/env python3
"""Report missing public technical editions from emitted self-canonical pages."""
import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit

from check_metadata import Metadata
from check_seo import emitted_url


def audit(root):
    root = Path(root)
    policy = json.loads((Path(__file__).resolve().parents[1] / 'src/lib/locales.json').read_text())
    languages = list(policy['locales'])
    if not (root / 'sitemap.xml').is_file():
        raise ValueError('Build the published site before auditing content')
    groups = {}
    counts = Counter()
    for file in sorted(root.glob('*/posts/*/index.html')):
        page = Metadata()
        page.feed(file.read_text())
        url = emitted_url(root, file)
        if page.noindex or page.refresh or page.canonicals != [url]:
            continue
        if page.language not in languages:
            raise ValueError('Unexpected article language')
        key = urlsplit(url).path.rstrip('/').rsplit('/', 1)[-1]
        editions = groups.setdefault(key, {})
        if page.language in editions:
            raise ValueError('Duplicate edition identity')
        editions[page.language] = url
        counts[page.language] += 1
    if not groups:
        raise ValueError('No public technical articles found')
    gaps = []
    for key, editions in sorted(groups.items(), reverse=True):
        missing = [language for language in languages if language not in editions]
        if missing:
            gaps.append({'key': key, 'available': list(editions), 'missing': missing,
                         'sourceURL': editions.get('en') or editions.get('ko') or next(iter(editions.values()))})
    return {'scope': 'Indexable self-canonical /posts/ routes only; excludes news and noindex examples',
            'topics': len(groups), 'publishedEditions': sum(counts.values()),
            'editionsByLanguage': {language: counts[language] for language in languages},
            'completeTopics': len(groups) - len(gaps),
            'missingEditions': sum(len(row['missing']) for row in gaps), 'translationGaps': gaps,
            'limits': ['Missing translations are backlog, not broken routes.',
                       'Edition existence does not establish translation accuracy or source synchronization.',
                       'Run check:technical-publications and check:technical-translations for pinned-source checks.',
                       'Publication dates and code checks do not establish factual freshness.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    print(json.dumps(audit(args.dist), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
