from pathlib import Path
import tempfile
import unittest

from check_migration import audit, SITE


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.registry = {'articles': [{'key': 'topic', 'legacyPath': '/old/topic/'}]}
        self.put('/en/posts/topic/')
        self.put('/ko/posts/topic/')
        self.put('/old/topic/', to='/ko/posts/topic/')
        self.put('/', to='/en/', noindex=True)
        self.put('/en/')
        self.sitemap(['/en/posts/topic/', '/ko/posts/topic/', '/en/'])

    def put(self, path, to=None, noindex=False, links='', canonical=None):
        directory = self.root / path.strip('/')
        directory.mkdir(parents=True, exist_ok=True)
        target = to or path
        html = '<html lang="' + ('en' if target.startswith('/en/') else 'ko') + '"><head>'
        html += '<link rel="canonical" href="' + (canonical or SITE + target) + '">'
        if to:
            html += '<meta http-equiv="refresh" content="0;url=' + to + '">'
        if noindex:
            html += '<meta name="robots" content="noindex,follow">'
        html += '</head><body>' + ('<a href="' + to + '">Continue</a>' if to else '') + links + '</body></html>'
        (directory / 'index.html').write_text(html)

    def sitemap(self, paths):
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + SITE + p + '</loc></url>' for p in paths) + '</urlset>')

    def errors(self):
        return '\n'.join(audit(self.root, self.registry)[0])

    def test_direct_article_moves_and_excluded_navigation_have_distinct_policies(self):
        errors, counts = audit(self.root, self.registry)
        self.assertEqual(errors, [])
        self.assertEqual(counts, {'articleMoves': 1, 'coreEditions': 2, 'navigationOrExcludedMoves': 1, 'redirects': 2})
        self.put('/old/topic/', to='/ko/posts/topic/', noindex=True)
        self.assertIn('article move must avoid noindex', self.errors())
        path = self.root / 'old/topic/index.html'
        path.write_text(path.read_text().replace('noindex,follow', 'none'))
        self.assertIn('article move must avoid noindex', self.errors())
        self.put('/old/topic/', to='/ko/posts/topic/')
        self.put('/', to='/en/')
        self.assertIn('navigation/example redirects must remain noindex', self.errors())

    def test_chains_cycles_and_missing_destinations_fail(self):
        for target in ['/missing/', '/old/topic/', '/']:
            with self.subTest(target=target):
                self.put('/old/topic/', to=target)
                self.assertIn('destination must exist and be final', self.errors())

    def test_core_identity_sitemap_and_live_link_disagreements_fail(self):
        self.put('/old/topic/', to='/en/posts/topic/')
        self.assertIn('registered Korean edition', self.errors())
        self.put('/old/topic/', to='/ko/posts/topic/', canonical=SITE + '/en/posts/topic/')
        self.assertIn('canonical and visible continuation link', self.errors())
        self.put('/old/topic/', to='/ko/posts/topic/')
        self.sitemap(['/old/topic/', '/ko/posts/topic/', '/en/'])
        errors = self.errors()
        self.assertIn('redirect must not appear in sitemap', errors)
        self.assertIn('/en/posts/topic/: core edition', errors)

    def test_public_links_to_old_routes_fail_even_with_query_or_fragment(self):
        self.put('/en/', links='<a href="/old/topic/?from=home#example">Read</a>')
        self.assertIn('public internal link still points to a redirect', self.errors())


if __name__ == '__main__':
    unittest.main()
