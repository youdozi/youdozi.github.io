from pathlib import Path
import tempfile
import unittest
from urllib.parse import quote

import check_discovery as discovery
from check_seo import SITE, emitted_url


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.article = '/en/posts/example/'
        self.page('/en/', ['/en/archive/'])
        self.page('/en/archive/', [self.article])
        self.page(self.article, [])
        self.sitemap(['/en/', '/en/archive/', self.article])

    def page(self, path, links, extra=''):
        file = self.root / path.strip('/') / 'index.html'
        file.parent.mkdir(parents=True, exist_ok=True)
        language = path.strip('/').split('/')[0]
        url = SITE + quote(path, safe='/')
        file.write_text(f'<html lang="{language}"><head><link rel="canonical" href="{url}">{extra}</head><body>'
                        + ''.join(f'<a href="{href}">Link</a>' for href in links) + '</body></html>')

    def sitemap(self, paths):
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join('<url><loc>' + SITE + quote(path, safe='/') + '</loc></url>' for path in paths) + '</urlset>')

    def test_all_sitemap_articles_are_reachable_with_at_most_two_link_steps(self):
        errors, report = discovery.inspect(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(report['languages']['en']['maxArticleLinkSteps'], 2)
        self.assertEqual(report['languages']['en']['reachableSitemapURLs'], 3)

    def test_noindex_search_is_allowed_but_links_to_empty_lists_fail(self):
        self.page('/en/search/', [], '<meta name="robots" content="noindex">')
        self.page('/en/tags/', [], '<meta name="robots" content="noindex">')
        file = self.root / 'en/tags/index.html'
        file.write_text(file.read_text().replace('</body>', '<div class="empty">Empty</div></body>'))
        self.page('/en/', ['/en/archive/', '/en/search/', '/en/tags/'])
        errors, report = discovery.inspect(self.root)
        self.assertTrue(any('empty noindex' in error for error in errors))
        self.assertEqual(report['emptyDestinationLinks'], 1)

    def test_other_language_menus_cannot_hide_a_missing_same_language_route(self):
        self.page('/ko/', ['/en/archive/'])
        self.page('/ko/posts/example/', [])
        self.sitemap(['/en/', '/en/archive/', self.article, '/ko/', '/ko/posts/example/'])
        errors, _ = discovery.inspect(self.root)
        self.assertTrue(any('/ko/posts/example/' in error and 'not reachable' in error for error in errors))

    def test_noindex_and_redirect_shortcuts_cannot_count_as_public_discovery_paths(self):
        for extra in ['<meta name="robots" content="noindex">', '<meta http-equiv="refresh" content="0;url=/en/posts/example/">']:
            self.page('/en/archive/', [self.article], extra)
            errors, _ = discovery.inspect(self.root)
            self.assertTrue(any('not reachable' in error for error in errors))

    def test_long_chain_fails_even_when_the_article_is_eventually_reachable(self):
        self.page('/en/archive/', ['/en/more/'])
        self.page('/en/more/', [self.article])
        errors, _ = discovery.inspect(self.root)
        self.assertTrue(any('more than two' in error for error in errors))

    def test_native_unicode_paths_are_included_and_fragments_keep_the_same_page(self):
        path = '/en/tags/한글/'
        self.page(path, [self.article])
        self.page('/en/', [path + '#year', '/en/archive/'])
        self.sitemap(['/en/', '/en/archive/', self.article, path])
        errors, report = discovery.inspect(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(report['publicPages'], 4)
        file = self.root / 'en/tags/한글/index.html'
        self.assertEqual(emitted_url(self.root, file), SITE + '/en/tags/%ED%95%9C%EA%B8%80/')

    def test_empty_duplicate_and_invalid_namespace_sitemaps_fail(self):
        self.sitemap([])
        self.assertTrue(discovery.inspect(self.root)[0])
        self.sitemap(['/en/', '/en/'])
        self.assertTrue(discovery.inspect(self.root)[0])
        (self.root / 'sitemap.xml').write_text('<urlset/>')
        with self.assertRaises(ValueError):
            discovery.inspect(self.root)


if __name__ == '__main__':
    unittest.main()
