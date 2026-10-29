import html
from pathlib import Path
import tempfile
import unittest

import check_seo as seo


class SeoGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.en = seo.SITE + '/en/posts/example/'
        self.ko = seo.SITE + '/ko/posts/example/'
        self.pairs = [('en', self.en), ('ko', self.ko), ('x-default', self.en)]
        self.page(self.en, 'en', self.pairs)
        self.page(self.ko, 'ko', self.pairs)
        self.sitemap([(self.en, self.pairs), (self.ko, self.pairs)])

    def page(self, url, language, pairs, *, canonical=None, extra=''):
        path = self.root / url.removeprefix(seo.SITE).strip('/') / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        links = ''.join(f'<link rel="alternate" hreflang="{html.escape(lang)}" href="{html.escape(href)}">' for lang, href in pairs)
        path.write_text(f'<html lang="{language}"><head><link rel="canonical" href="{canonical or url}">{links}{extra}</head><body><h1>Example</h1></body></html>')

    def sitemap(self, rows):
        nodes = []
        for url, pairs in rows:
            links = ''.join(f'<xhtml:link rel="alternate" hreflang="{html.escape(lang)}" href="{html.escape(href)}"/>' for lang, href in pairs)
            nodes.append(f'<url><loc>{html.escape(url)}</loc>{links}</url>')
        (self.root / 'sitemap.xml').write_text(f'<urlset xmlns="{seo.SM[1:-1]}" xmlns:xhtml="{seo.XHTML[1:-1]}">{"".join(nodes)}</urlset>')

    def errors(self):
        return '\n'.join(seo.audit(self.root)[0])

    def test_valid_bilingual_and_single_language_pages_and_optional_sitemap_alternates(self):
        only = seo.SITE + '/ko/posts/untranslated/'
        self.page(only, 'ko', [('ko', only)])
        self.sitemap([(self.en, self.pairs), (self.ko, self.pairs), (only, [])])
        errors, stats = seo.audit(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats['sitemapByLanguage'], {'en': 1, 'ko': 2})
        self.assertEqual(stats['htmlAlternateEdges'], 7)

    def test_rejects_noindex_none_redirect_and_wrong_canonical_targets(self):
        for options in [{'extra': '<meta name="robots" content="noindex,follow">'},
                        {'extra': '<meta name="Googlebot" content="none">'},
                        {'extra': '<meta http-equiv="refresh" content="0;url=/en/">'},
                        {'canonical': self.en}]:
            with self.subTest(options=options):
                self.page(self.ko, 'ko', self.pairs, **options)
                self.assertIn('alternate is missing, redirected, noindex or not self-canonical', self.errors())
                self.assertIn('sitemap target', self.errors())

    def test_rejects_missing_target_and_nonreciprocal_links(self):
        path = self.root / 'ko/posts/example/index.html'
        path.unlink()
        self.assertIn('alternate is missing', self.errors())
        self.page(self.ko, 'ko', [('ko', self.ko)])
        self.assertIn('does not link back', self.errors())

    def test_rejects_wrong_language_duplicate_labels_and_missing_self(self):
        self.page(self.ko, 'ja', self.pairs)
        self.assertIn('language disagrees', self.errors())
        self.page(self.ko, 'ko', self.pairs + [('ko', self.ko)])
        self.assertIn('duplicate hreflang', self.errors())
        self.page(self.ko, 'ko', [('en', self.en), ('x-default', self.en)])
        self.assertIn('must include itself', self.errors())

    def test_rejects_relative_external_query_fragment_and_unknown_locale_links(self):
        for href in ['/ko/posts/example/', '//youdozi.github.io/ko/', 'https://other.example/ko/', self.ko + '?a=1', self.ko + '#part']:
            with self.subTest(href=href):
                self.page(self.en, 'en', [('en', self.en), ('ko', href), ('x-default', self.en)])
                self.assertIn('absolute clean site URL', self.errors())
        self.page(self.en, 'en', self.pairs + [('xx', self.ko)])
        self.assertIn('unsupported hreflang', self.errors())

    def test_enforces_existing_english_fallback_policy(self):
        self.page(self.en, 'en', [('en', self.en), ('ko', self.ko), ('x-default', self.ko)])
        self.assertIn('English alternate as x-default', self.errors())
        self.page(self.ko, 'ko', [('ko', self.ko), ('x-default', self.ko)])
        self.assertIn('requires an English counterpart', self.errors())

    def test_rejects_sitemap_html_disagreement_duplicate_loc_and_bad_namespace(self):
        self.sitemap([(self.en, [('en', self.en)]), (self.ko, self.pairs)])
        self.assertIn('sitemap and HTML hreflang disagree', self.errors())
        self.sitemap([(self.en, self.pairs), (self.en, self.pairs)])
        self.assertIn('Duplicate sitemap loc', self.errors())
        self.sitemap([])
        self.assertIn('Sitemap must contain public URLs', self.errors())
        (self.root / 'sitemap.xml').write_text('<urlset/>')
        with self.assertRaisesRegex(ValueError, 'namespaced'):
            seo.audit(self.root)

    def test_noindex_search_and_verification_pages_do_not_enter_the_public_graph(self):
        search = seo.SITE + '/en/search/'
        self.page(search, 'en', [('en', search)], extra='<meta name="robots" content="noindex">')
        (self.root / 'googleverify.html').write_text('google-site-verification: verify')
        errors, stats = seo.audit(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats['htmlPages'], 3)
        self.assertEqual(stats['selfCanonicalIndexablePages'], 2)


if __name__ == '__main__':
    unittest.main()
