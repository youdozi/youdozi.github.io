#!/usr/bin/env python3
"""Compare listing JSON-LD to the exact visible cards, offline."""
import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET
from check_metadata import Metadata
from check_seo import SITE, emitted_url

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class ListingMetadata(Metadata):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.listings = 0
        self.cards = 0
        self.links = []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        if 'data-article-listing' in values:
            self.listings += 1
        inside = 'data-article-listing' in values or any('data-article-listing' in a for _, a in self.stack)
        if inside and tag == 'article' and 'entry-card' in values.get('class', '').split():
            self.cards += 1
        card = any(t == 'article' and 'entry-card' in a.get('class', '').split() for t, a in self.stack)
        if inside and card and tag == 'a' and any(t == 'h2' for t, _ in self.stack):
            self.anchor = [values.get('href', ''), []]
        if tag not in VOID:
            self.stack.append((tag, values))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        super().handle_data(data)
        if self.anchor is not None:
            self.anchor[1].append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            self.links.append((urljoin(SITE, self.anchor[0]), ''.join(self.anchor[1])))
            self.anchor = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        super().handle_endtag(tag)


def validate_listing(url, page, pages, sitemap):
    errors = []
    if page.listings != 1:
        errors.append('Listing must have exactly one visible listing region')
    if page.cards != len(page.links):
        errors.append('Every visible card needs one title link')
    try:
        if len(page.jsonld) != 1:
            raise ValueError('Expected one graph')
        graph = json.loads(page.jsonld[0])
        if not isinstance(graph, list) or any(not isinstance(item, dict) for item in graph):
            raise ValueError('Expected a graph array')
    except (ValueError, TypeError):
        return errors + ['Listing JSON-LD must parse as one site graph']
    collections = [x for x in graph if x.get('@type') == 'CollectionPage']
    lists = [x for x in graph if x.get('@type') == 'ItemList']
    if not page.cards:
        if collections or lists or not page.noindex:
            errors.append('Empty listing must remain noindex without collection/list metadata')
        return errors
    if page.noindex or page.canonicals != [url]:
        errors.append('Nonempty listing must be indexable and self-canonical')
    if len(collections) != 1 or len(lists) != 1:
        return errors + ['Nonempty listing needs exactly one CollectionPage and ItemList']
    collection, listing = collections[0], lists[0]
    if collection.get('url') != url or collection.get('@id') != url + '#collection':
        errors.append('Collection identity must use this page canonical URL')
    if collection.get('inLanguage') != page.language:
        errors.append('Collection language must match HTML')
    if collection.get('name') != next(iter(page.meta.get('og:title', [])), None):
        errors.append('Collection name must match the current page title')
    if collection.get('description') != next(iter(page.meta.get('description', [])), None):
        errors.append('Collection description must match page metadata')
    if listing.get('@id') != url + '#entries' or collection.get('mainEntity') != {'@id': url + '#entries'}:
        errors.append('Collection must reference this page ItemList')
    if listing.get('name') != collection.get('name'):
        errors.append('ItemList name must identify this page')
    rows = listing.get('itemListElement')
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        return errors + ['ItemList entries must be ListItem objects']
    if type(listing.get('numberOfItems')) is not int or listing.get('numberOfItems') != page.cards or len(rows) != page.cards:
        errors.append('ItemList count must equal visible cards on this page')
    if [row.get('position') for row in rows] != list(range(1, page.cards + 1)) or any(row.get('@type') != 'ListItem' or type(row.get('position')) is not int for row in rows):
        errors.append('ItemList positions must follow visible card order starting at one')
    normalize = lambda value: ' '.join(value.split()) if isinstance(value, str) else None
    if [(row.get('url'), normalize(row.get('name'))) for row in rows] != [(href, normalize(name)) for href, name in page.links]:
        errors.append('ItemList names, URLs and order must equal visible cards')
    urls = [row.get('url') for row in rows]
    if any(not isinstance(target, str) or not target for target in urls):
        return errors + ['ItemList URLs must be nonempty strings']
    if len(urls) != len(set(urls)):
        errors.append('ItemList must not duplicate articles')
    for target in urls:
        document = pages.get(target)
        if target not in sitemap or document is None or document.noindex or document.refresh or document.canonicals != [target] or document.language != page.language:
            errors.append('ItemList target must be a public same-language sitemap article: ' + str(target))
        elif urlsplit(target).path.strip('/').split('/')[1:2] not in (['posts'], ['digest']):
            errors.append('ItemList target must be an article')
    return errors


def audit(root):
    root = Path(root)
    sitemap = {n.text for n in ET.parse(root / 'sitemap.xml').getroot().iter() if n.tag.endswith('}loc')}
    pages = {}
    for file in root.rglob('*.html'):
        page = ListingMetadata()
        page.feed(file.read_text(encoding='utf-8'))
        pages[emitted_url(root, file)] = page
    errors = []
    counts = Counter()
    for url, page in pages.items():
        if not page.listings:
            continue
        errors.extend(url + ': ' + message for message in validate_listing(url, page, pages, sitemap))
        counts['listingPages'] += 1
        counts['emptyListings'] += not page.cards
        counts['visibleCards'] += page.cards
        counts['language:' + str(page.language)] += 1
    if not counts['listingPages']:
        errors.append('No listing pages found; check the build directory')
    return sorted(set(errors)), dict(sorted(counts.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    errors, summary = audit(args.dist)
    for message in errors:
        print('[error]', message)
    if not errors:
        print('[ok] Listing JSON-LD matches visible cards: ' + json.dumps(summary, sort_keys=True))
    raise SystemExit(bool(errors))
