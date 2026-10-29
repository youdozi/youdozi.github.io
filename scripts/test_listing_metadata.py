import html
import json
from pathlib import Path
import tempfile
import unittest
from check_listing_metadata import ListingMetadata, validate_listing, audit, SITE


class ListingTests(unittest.TestCase):
    url = SITE + '/en/posts/page/2/'
    target = SITE + '/en/posts/second-page-item/'

    def graph(self):
        return [
            {'@type': 'CollectionPage', '@id': self.url + '#collection', 'url': self.url, 'name': 'Writing · Page 2', 'description': 'Actual page', 'inLanguage': 'en', 'mainEntity': {'@id': self.url + '#entries'}},
            {'@type': 'ItemList', '@id': self.url + '#entries', 'name': 'Writing · Page 2', 'numberOfItems': 1, 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Title < & 日本語', 'url': self.target}]},
        ]

    def document(self, graph=None, cards=None, noindex=False):
        graph = self.graph() if graph is None else graph
        cards = '<article class="entry-card"><h2><a href="/en/posts/second-page-item/">Title &lt; &amp; 日本語</a></h2><a href="/en/posts/second-page-item/">↗</a></article>' if cards is None else cards
        raw = json.dumps(graph).replace('<', r'\u003c')
        return (f'<html lang="en"><head><link rel="canonical" href="{self.url}">'
                '<meta property="og:title" content="Writing · Page 2"><meta name="description" content="Actual page">'
                + ('<meta name="robots" content="noindex,follow">' if noindex else '')
                + '<script type="application/ld+json">' + raw + '</script></head><body>'
                '<aside><h2><a href="/en/posts/featured/">Featured link</a></h2></aside>'
                '<div data-article-listing>' + cards + '</div></body></html>')

    def errors(self, document=None, target=None, sitemap=None):
        page = ListingMetadata()
        page.feed(document or self.document())
        if target is None:
            target = ListingMetadata()
            target.feed(f'<html lang="en"><head><link rel="canonical" href="{self.target}"></head></html>')
        return '\n'.join(validate_listing(self.url, page, {self.target: target}, {self.target} if sitemap is None else sitemap))

    def test_exact_visible_title_order_and_page_identity(self):
        self.assertEqual(self.errors(), '')
        page = ListingMetadata()
        page.feed(self.document())
        self.assertEqual(page.links, [(self.target, 'Title < & 日本語')])
        self.assertEqual(page.cards, 1)
        for field, value in [('url', SITE + '/en/posts/'), ('inLanguage', 'ko'), ('name', 'Wrong title'), ('description', 'Other description'), ('mainEntity', {'@id': 'wrong'})]:
            graph = self.graph()
            graph[0][field] = value
            with self.subTest(field=field):
                self.assertTrue(self.errors(self.document(graph)))

    def test_other_page_items_wrong_counts_positions_and_names_fail(self):
        for change in ({'url': SITE + '/en/posts/first-page-item/'}, {'name': 'Hidden title'}, {'position': 2}, {'position': True}, {'url': {}}, {'@type': 'Thing'}):
            graph = self.graph()
            graph[1]['itemListElement'][0].update(change)
            with self.subTest(change=change):
                self.assertTrue(self.errors(self.document(graph)))
        for value in (25, True):
            graph = self.graph()
            graph[1]['numberOfItems'] = value
            self.assertIn('count', self.errors(self.document(graph)))
        graph = self.graph()
        graph[1]['itemListElement'] *= 2
        self.assertIn('duplicate', self.errors(self.document(graph)))

    def test_noindex_redirect_missing_sitemap_and_other_language_targets_fail(self):
        for head in ('<meta name="robots" content="noindex">', '<meta http-equiv="refresh" content="0;url=/">'):
            target = ListingMetadata()
            target.feed(f'<html lang="en"><head><link rel="canonical" href="{self.target}">{head}</head></html>')
            self.assertIn('public same-language', self.errors(target=target))
        target = ListingMetadata()
        target.feed(f'<html lang="ko"><head><link rel="canonical" href="{self.target}"></head></html>')
        self.assertIn('public same-language', self.errors(target=target))
        self.assertIn('public same-language', self.errors(sitemap=set()))

    def test_empty_listing_requires_noindex_and_no_invented_collection(self):
        self.assertEqual(self.errors(self.document([], '', True)), '')
        self.assertIn('Empty listing', self.errors(self.document([], '', False)))
        self.assertIn('Empty listing', self.errors(self.document(self.graph(), '', True)))

    def test_missing_graph_duplicate_graph_and_missing_card_titles_fail(self):
        self.assertIn('exactly one CollectionPage', self.errors(self.document([])))
        self.assertIn('exactly one CollectionPage', self.errors(self.document(self.graph() * 2)))
        self.assertIn('one title link', self.errors(self.document(cards='<article class="entry-card">Missing title</article>')))
        self.assertIn('must parse', self.errors(self.document().replace('[{', 'invalid [{', 1)))

    def test_audit_fails_closed_on_missing_listing_pages(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
            errors, counts = audit(folder)
            self.assertIn('No listing pages', errors[0])
            self.assertEqual(counts, {})
