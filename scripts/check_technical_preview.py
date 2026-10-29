#!/usr/bin/env python3
"""Check rendered technical fixtures, complete paragraphs, Java, feeds and eight-way alternates."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime

from technical_publications import technical_records
from check_metadata import Metadata
from check_reader_content import normalize, article_file
from check_seo import SITE


class TechnicalHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.text, self.code, self.images = [], [], []
        self.in_pre = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else {'active':False,'skip':False}
        active = parent['active'] or 'prose' in attrs.get('class', '').split()
        skip = parent['skip'] or tag in ('script','style','template') or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        if tag == 'pre' and active and not skip:
            self.in_pre = True
            self.code.append([])
        if tag == 'img' and active and not skip: self.images.append(attrs)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append({'tag':tag,'active':active,'skip':skip})

    def handle_endtag(self, tag):
        index = next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i]['tag'] == tag), None)
        if index is None: return
        if tag == 'pre': self.in_pre = False
        # Inline code/links/emphasis must not invent spaces before CJK text or punctuation.
        if not self.in_pre and tag in ('p','div','h1','h2','h3','h4','table','tr','td','th','pre'):
            self.text.append(' ')
        del self.stack[index:]

    def handle_data(self, data):
        if self.stack and self.stack[-1]['active'] and not self.stack[-1]['skip']:
            if self.in_pre: self.code[-1].append(data)
            else: self.text.append(data)


def expected_paragraphs(body):
    body = re.sub(r'^```[^\n]*\n[\s\S]*?^```\s*$', '', body, flags=re.M)
    body = re.sub(r'!\[[^\]\n]*\]\([^)]+\)', '', body)
    body = re.sub(r'(?<!!)\[([^\]\n]*)\]\([^)]+\)', r'\1', body)
    for chunk in re.split(r'\n\n+', body.strip()):
        if chunk.startswith('| '):
            for row in chunk.splitlines():
                if not re.fullmatch(r'[| :\-]+', row):
                    yield normalize(row.replace('|', ' '))
        else:
            text = re.sub(r'^##\s+', '', chunk).replace('**', '').replace('`', '')
            if text.strip(): yield normalize(text)


def check(base):
    marker = json.loads((base / '.translation-preview-fixture.json').read_text())
    keys = marker.get('technicalFixtureKeys')
    if marker.get('fixtureOnly') is not True or not isinstance(keys, list) or not keys or any(not isinstance(k, str) or not re.fullmatch(r'(?:zh-CN|ja|de|fr|ru|es)-\d{4}-\d{2}-\d{2}-[a-z0-9.-]+', k) for k in keys) or len(set(keys)) != len(keys):
        raise ValueError('Expected isolated technical fixture marker')
    records = technical_records(base)
    selected = {f"{r['language']}-{r['translationKey']}": (url, r) for url, r in records.items()}
    if set(keys) - selected.keys(): raise ValueError('Technical fixture missing')
    dist = base / 'dist'
    sitemap = {n.text for n in ET.parse(dist/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    indexes, feeds, topics, paragraphs = {}, {}, set(), 0
    for key in keys:
        url, record = selected[key]
        if record['approval']['kind'] != 'render-fixture' or record['approval']['reviewedBy'] != 'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL':
            raise ValueError('Technical preview cannot claim human approval')
        lang, slug = record['language'], record['routeSlug']
        if lang not in indexes:
            indexes[lang] = {r['url']: r for r in json.loads((dist/lang/'search-index.json').read_text())}
            feeds[lang] = {i.findtext('link'): i for i in ET.parse(dist/lang/'feed.xml').findall('./channel/item')}
        html = article_file(dist, url).read_text()
        page, body = Metadata(), TechnicalHTML()
        page.feed(html); body.feed(html)
        if normalize(''.join(page.h1)) != normalize(record['title']) or page.meta.get('og:title') != [record['title']] or page.meta.get('description') != [record['description']]:
            raise ValueError('Technical visible title or description changed')
        row = indexes[lang].get(url)
        if not row or row['title'] != record['title'] or row['description'] != record['description']:
            raise ValueError('Technical search metadata changed')
        visible = normalize(''.join(body.text))
        # readerMarkdown leaves inline Markdown in the search index; compare its prose with the same stripping.
        search = normalize(re.sub(r'(?<!!)\[([^\]\n]*)\]\([^)]+\)', r'\1', row['content']).replace('**', '').replace('`', '').replace('|', ' '))
        for paragraph in expected_paragraphs(record['body']):
            if paragraph not in visible or paragraph not in search:
                raise ValueError(f'Technical preview omits a paragraph: {key}')
            paragraphs += 1
        expected_code = re.findall(r'^```java\n([\s\S]*?)^```', record['body'], re.M)
        actual_code = [''.join(c).strip() for c in body.code]
        if [c.strip() for c in expected_code] != actual_code: raise ValueError('Technical Java example changed')
        image = body.images
        expected_asset = f'/assets/diagrams/technical/{key}.svg'
        if len(image) != 1 or image[0].get('src') != expected_asset or not image[0].get('alt') or not (dist/expected_asset.lstrip('/')).is_file():
            raise ValueError('Localized technical diagram missing')
        item = feeds[lang].get(SITE+url)
        if item is None or item.findtext('title') != record['title'] or item.findtext('description') != record['description']:
            raise ValueError('Technical RSS metadata missing or changed')
        if datetime.fromisoformat(item.findtext('{http://www.w3.org/2005/Atom}updated').replace('Z','+00:00')) != datetime.fromisoformat(record['updatedAt'].replace('Z','+00:00')):
            raise ValueError('Technical RSS revision date changed')
        expected = {other: SITE+f'/{other}/posts/{slug}/' for other in ('en','ko','zh-CN','ja','de','fr','ru','es') if other in ('en','ko') or f'/{other}/posts/{slug}/' in records}
        expected['x-default'] = SITE+f'/en/posts/{slug}/'
        for other, target in expected.items():
            if other == 'x-default': continue
            head = Metadata(); head.feed(article_file(dist, target.removeprefix(SITE)).read_text())
            if target not in sitemap or head.canonicals != [target] or head.noindex or head.refresh or dict(head.alternates) != expected:
                raise ValueError('Technical counterpart missing or alternates changed')
        if 'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL' in html: raise ValueError('Internal approval leaked into HTML')
        topics.add(record['translationKey'])
    return {'fixtureEditions':len(keys),'technicalTopics':len(topics),'completeParagraphsAndTableRows':paragraphs,'localizedJavaExamples':len(keys),'localizedDiagrams':len(keys),'rssEditions':len(keys),'fixtureOnly':True}


if __name__ == '__main__':
    print('[ok] Isolated technical publication contracts:', json.dumps(check(Path('.'))))
