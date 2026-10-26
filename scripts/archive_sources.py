"""Versioned archive extraction and bounded transport; legacy evidence stays reproducible."""
from __future__ import annotations
from html.parser import HTMLParser
import json
import re
import subprocess
from urllib.parse import urlsplit
from ai_dev_digest import ArticleParser, compact

EXTRACTOR_VERSIONS = {'article-parser-v1', 'article-parser-v2'}
DEFAULT_EXTRACTOR = 'article-parser-v2'
VOID = {'br','img','hr','input','meta','link','source','wbr','area','base','embed','param','track','col'}
CHROME = {'article__metadata','article__authors','article__actions','article__fromTopic',
          'author-section-full','contentRatingWidget','newsletter','social-share'}


class StableArticleParser(HTMLParser):
    """Prefer explicit body containers; exclude structural chrome, never trim by prose."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else (None, False, None)
        markers = set((attrs.get('class','')+' '+attrs.get('id','')).split())
        hidden = (parent[1] or tag in {'script','style','nav','footer','header','aside','form'}
                  or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
                  or bool(markers & CHROME) or any(m.startswith('related__') for m in markers))
        explicit = ('articleBody' in attrs.get('itemprop','').split() or 'article__data' in markers
                    or bool(markers & {'markdown-body','blog--post'})
                    or any(re.fullmatch(r'(?:article|post|entry|blog)[_-](?:body|content|text)',m,re.I) for m in markers))
        rank = 3 if explicit else 2 if tag == 'article' else 1 if tag == 'main' else 0
        block = parent[2]
        if not hidden and rank and (block is None or rank > self.blocks[block][0]):
            block = len(self.blocks)
            self.blocks.append((rank, []))
        if tag not in VOID:
            self.stack.append((tag, hidden, block))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, value):
        if self.stack:
            _, hidden, block = self.stack[-1]
            if not hidden and block is not None:
                self.blocks[block][1].append(value)

    def extract(self):
        candidates = [(rank,compact(' '.join(parts))) for rank,parts in self.blocks]
        candidates = [c for c in candidates if c[1]]
        return max(candidates,key=lambda c:(c[0],len(c[1])),default=(0,''))[1]

def https(value):
    try:
        u = urlsplit(value)
        return u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password and u.port in (None, 443) and not re.search(r'[\s<>\\]', value)
    except (TypeError, ValueError):
        return False



def extract_body(markup, version):
    if version not in EXTRACTOR_VERSIONS:
        raise ValueError('unsupported article extractor version')
    parser = ArticleParser() if version == 'article-parser-v1' else StableArticleParser()
    parser.feed(markup)
    return parser.extract()


def body_for(documents, document):
    key = (document['url'], document['extractorVersion'])
    return documents[key] if key in documents else documents[document['url']]


def fetch_document(url, extractor_version=DEFAULT_EXTRACTOR):
    if not https(url):
        raise ValueError('unsafe source URL')
    if extractor_version not in EXTRACTOR_VERSIONS:
        raise ValueError('unsupported article extractor version')
    result = None
    for attempt in range(3):
        command = ['curl','--disable','--fail','--silent','--show-error','--location',
                   '--proto','=https','--proto-redir','=https','--max-redirs','5',
                   '--max-time','12','--max-filesize','2500000','--write-out','\n%{json}']
        if attempt:
            command.append('--ipv4')
        try:
            result = subprocess.run(command+[url],text=True,capture_output=True,timeout=17)
        except subprocess.TimeoutExpired:
            if attempt < 2:
                continue
            raise ValueError('source unavailable (transport timeout after 3 bounded attempts)') from None
        if result.returncode == 0:
            break
        if result.returncode not in {5,6,7,28,52,55,56} or attempt == 2:
            raise ValueError(f'source unavailable (curl {result.returncode}, attempt {attempt+1})')
    try:
        markup, metadata = result.stdout.rsplit('\n',1)
        metadata = json.loads(metadata)
        final_url = metadata['url_effective']
    except (ValueError,KeyError,TypeError):
        raise ValueError('source returned invalid transport metadata') from None
    if metadata.get('http_code') != 200:
        raise ValueError(f'source returned HTTP {metadata.get("http_code")}; expected HTTP 200 HTML')
    mime = str(metadata.get('content_type') or '').split(';',1)[0].strip().lower()
    if mime not in {'text/html','application/xhtml+xml'}:
        raise ValueError('source did not return HTML')
    if not https(final_url) or urlsplit(final_url).hostname != urlsplit(url).hostname:
        raise ValueError('source redirected to a different publisher')
    body = extract_body(markup,extractor_version)
    if len(body) < 100:
        raise ValueError('article body unavailable')
    return body
