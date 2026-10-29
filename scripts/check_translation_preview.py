#!/usr/bin/env python3
"""Check disposable translation fixtures; never approve or publish editions."""
from technical_publications import technical_records
from datetime import datetime
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from check_reader_content import ReaderHTML, normalize, article_file
from check_seo import Head, SITE


def check(base):
    marker = json.loads((base / '.translation-preview-fixture.json').read_text())
    keys = marker.get('fixtureKeys')
    if marker.get('fixtureOnly') is not True or not isinstance(keys, list) or len(set(keys)) != len(keys):
        raise ValueError('Expected isolated fixture marker')
    if any(not isinstance(key, str) or not re.fullmatch(r'(?:zh-CN|ja|de|fr|ru|es)-[a-f0-9]{16}', key) for key in keys):
        raise ValueError('Invalid fixture identity')
    records, languages, by_url = {}, {}, {}
    for path in (base / 'src/content/translations').glob('*.json'):
        record = json.loads(path.read_text())
        source = json.loads((base / f"src/content/renewals/{record['renewalId']}.json").read_text())
        record['previewSlug'] = source['slug']
        records[path.stem] = record
        languages.setdefault(record['renewalId'], {'en', 'ko'}).add(record['language'])
        by_url[f"/{record['language']}/digest/{source['slug']}/"] = record
    by_url.update(technical_records(base))
    dist = base / 'dist'
    sitemap = {node.text for node in ET.parse(dist / 'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    indexes, feeds, cache = {}, {}, {}
    for lang in {records[key]['language'] for key in keys}:
        rows = json.loads((dist / lang / 'search-index.json').read_text())
        indexes[lang] = {row['url']: row for row in rows}
        items = ET.parse(dist / lang / 'feed.xml').findall('./channel/item')
        feeds[lang] = {item.findtext('link'): item for item in items}
        # Both news and approved technical posts supply explicit per-edition dates.
        # Unknown kinds still fail rather than receiving invented feed dates.
        if any(row['url'] not in by_url for row in rows): raise ValueError('Preview RSS date inventory requires extension')
        expected = [SITE + row['url'] for row in sorted(rows, key=lambda row: datetime.fromisoformat(by_url[row['url']]['updatedAt']), reverse=True)[:30]]
        if [item.findtext('link') for item in items] != expected: raise ValueError('Preview RSS is not the latest 30 editions')

    def page(url):
        if url not in cache:
            html = article_file(dist, url).read_text()
            body, head = ReaderHTML(set()), Head()
            body.feed(html); body.close(); head.feed(html)
            cache[url] = (normalize(' '.join(body.text)), head)
        return cache[url]

    claims, groups, in_feed = 0, set(), 0
    for key in keys:
        record = records[key]
        if record['approval']['reviewedBy'] != 'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL':
            raise ValueError('Expected synthetic preview record, not publication approval')
        lang, slug = record['language'], record['previewSlug']
        url = f'/{lang}/digest/{slug}/'
        text, head = page(url)
        row = indexes[lang].get(url)
        if SITE + url not in sitemap or head.canonicals != [SITE + url] or head.noindex or head.refresh:
            raise ValueError('Preview edition missing or not canonical')
        if not row or row['title'] != record['edition']['title'] or normalize(row['title']) not in text:
            raise ValueError('Preview title missing or changed')
        values = record['edition']['claims'] + record['edition']['followUp']
        for value in values:
            if normalize(value) not in text or value not in row['content']:
                raise ValueError('Preview HTML or search omits an exact source-mapped claim')
        claims += len(values)
        if SITE + url in feeds[lang]:
            in_feed += 1
            item = feeds[lang][SITE + url]
            for value in values:
                if value not in item.findtext('description', ''):
                    raise ValueError('Preview RSS omits an exact source-mapped claim')
        expected = {language: SITE + f'/{language}/digest/{slug}/' for language in languages[record['renewalId']]}
        expected['x-default'] = SITE + f'/en/digest/{slug}/'
        for language in languages[record['renewalId']]:
            _, counterpart = page(f'/{language}/digest/{slug}/')
            if dict(counterpart.alternates) != expected: raise ValueError('Preview language counterparts differ')
        groups.add(record['renewalId'])
    return {'fixtureEditions': len(keys), 'claimsAndFollowUp': claims, 'languageGroups': len(groups),
            'fixtureEditionsInRSS': in_feed, 'translationRSSPoliciesChecked': len(feeds), 'fixtureOnly': True}


if __name__ == '__main__':
    try:
        print('[ok] Isolated translation edition contracts:', json.dumps(check(Path('.'))))
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
        print('[error] Isolated translation edition contract failed; private claim text omitted.')
        raise SystemExit(1)
