#!/usr/bin/env python3
"""Match article reading links to the visible curated guide sections, offline."""
import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

from check_metadata import Metadata
from check_seo import SITE, emitted_url
from check_listing_metadata import VOID


class LearningPage(Metadata):
    def __init__(self):
        super().__init__()
        self.stack, self.paths, self.guide_steps = [], [], []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        attrs = dict(attrs)
        path = None
        if 'data-article-learning-path' in attrs:
            path = {'attrs': attrs, 'links': []}
            self.paths.append(path)
        inside = next((frame[2] for frame in reversed(self.stack) if frame[2] is not None), None)
        group = any('algorithm-group' in frame[1].get('class', '').split() for frame in self.stack)
        if tag == 'a' and (inside is not None or group):
            role = 'guide' if 'data-learning-guide' in attrs else attrs.get('data-learning-direction', 'unexpected')
            self.anchor = {'url': urljoin(SITE, attrs.get('href', '')), 'role': role, 'text': [], 'path': inside}
        if tag not in VOID:
            self.stack.append((tag, attrs, path))

    def handle_data(self, data):
        super().handle_data(data)
        if self.anchor is not None:
            self.anchor['text'].append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            anchor = self.anchor
            result = {'url': anchor['url'], 'role': anchor['role'], 'text': ' '.join(' '.join(anchor['text']).split())}
            if anchor['path'] is not None:
                anchor['path']['links'].append(result)
            else:
                self.guide_steps.append(result)
            self.anchor = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        super().handle_endtag(tag)


def validate(pages, sitemap, languages=('en', 'ko')):
    errors, counts, expected = [], Counter(), {}
    for language in languages:
        index = pages.get(SITE + '/' + language + '/guides/')
        try:
            graph = json.loads(index.jsonld[0])
            lists = [item for item in graph if item.get('@type') == 'ItemList']
            guide_urls = [item['url'] for item in lists[0]['itemListElement']]
            if len(lists) != 1 or not guide_urls or len(guide_urls) != len(set(guide_urls)):
                raise ValueError('Guide index must have one unique ordered list')
        except (AttributeError, IndexError, KeyError, ValueError, TypeError):
            errors.append(language + ': missing or invalid guide index')
            continue
        for guide_url in guide_urls:
            guide = pages.get(guide_url)
            if guide is None or guide.language != language or guide.noindex or guide_url not in sitemap:
                errors.append(guide_url + ': guide must be public in the same language')
                continue
            steps = guide.guide_steps
            if len({step['url'] for step in steps}) != len(steps):
                errors.append(guide_url + ': duplicate curated steps')
            for position, step in enumerate(steps):
                target = pages.get(step['url'])
                if target is None or target.noindex or target.refresh or target.language != language or target.canonicals != [step['url']] or step['url'] not in sitemap or urlsplit(step['url']).path.split('/')[2:3] != ['posts']:
                    errors.append(guide_url + ': step must be a same-language public article')
                    continue
                if len(steps) >= 2:
                    expected.setdefault(step['url'], (guide_url, position, steps))
    for url, page in pages.items():
        if url not in expected:
            if page.paths:
                errors.append(url + ': reading path must belong to a multi-article curated section')
            continue
        if len(page.paths) != 1:
            errors.append(url + ': expected exactly one article reading path')
            continue
        guide_url, position, steps = expected[url]
        path = page.paths[0]
        attrs = path['attrs']
        if attrs.get('data-guide-url') != urlsplit(guide_url).path or attrs.get('data-position') != str(position + 1) or attrs.get('data-total') != str(len(steps)) or not attrs.get('aria-label'):
            errors.append(url + ': guide identity, position, total and accessible name must match')
        wanted = [('guide', guide_url, None)]
        if position:
            wanted.append(('previous', steps[position - 1]['url'], steps[position - 1]['text']))
        if position + 1 < len(steps):
            wanted.append(('next', steps[position + 1]['url'], steps[position + 1]['text']))
        links = path['links']
        if [(link['role'], link['url']) for link in links] != [(role, href) for role, href, _ in wanted]:
            errors.append(url + ': reading neighbors must match guide order without wrapping')
        elif any(not link['text'] or (title and not link['text'].endswith(title)) for link, (_, _, title) in zip(links, wanted)):
            errors.append(url + ': reading links must show the destination article titles')
        counts['articles'] += 1
        counts['language:' + page.language] += 1
        counts['neighborLinks'] += len(wanted) - 1
    if not expected:
        errors.append('No curated article reading paths found')
    return sorted(set(errors)), dict(sorted(counts.items()))


def audit(root):
    root = Path(root)
    pages = {}
    for file in root.rglob('*.html'):
        page = LearningPage(); page.feed(file.read_text(encoding='utf-8'))
        if page.language:
            pages[emitted_url(root, file)] = page
    sitemap = {n.text for n in ET.parse(root / 'sitemap.xml').getroot().iter() if n.tag.endswith('}loc')}
    return validate(pages, sitemap)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    errors, counts = audit(args.dist)
    for error in errors:
        print('[error] ' + error)
    if not errors:
        print('[ok] Article reading paths match visible guide order: ' + json.dumps(counts))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
