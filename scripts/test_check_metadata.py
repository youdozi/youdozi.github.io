import html
import json
import re
from pathlib import Path
import tempfile
import unittest

import check_metadata as md


class MetadataTests(unittest.TestCase):
    url = md.SITE + '/en/posts/example/'
    published = '2023-09-18T15:00:00.000Z'
    modified = '2026-10-27T05:23:47.316Z'

    def document(self, *, headline='Title < literal', description='A & B', modified=None, extra='', graph_change=None):
        modified = modified or self.modified
        author = {'@id': md.SITE + '/#author', 'url': md.SITE + '/en/about/'}
        article = {'@type': 'BlogPosting', '@id': self.url + '#article', 'url': self.url,
                   'mainEntityOfPage': self.url, 'headline': headline, 'description': description,
                   'inLanguage': 'en', 'datePublished': self.published, 'dateModified': modified,
                   'author': author}
        if graph_change:
            article.update(graph_change)
        fields = {'og:url': self.url, 'og:title': headline, 'twitter:title': headline,
                  'description': description, 'og:description': description, 'twitter:description': description,
                  'og:site_name': 'Site', 'og:type': 'article', 'og:locale': 'en_US',
                  'og:locale:alternate': 'ko_KR', 'article:published_time': self.published,
                  'article:modified_time': modified, 'article:author': author['url']}
        tags = ''.join(f'<meta property="{key}" content="{html.escape(value)}">' for key, value in fields.items())
        raw = json.dumps([article], ensure_ascii=False).replace('<', r'\u003c')
        dates = f'<span class="publication-date"><time datetime="{self.published}">Published</time></span>'
        if modified != self.published:
            dates += f'<span class="modification-date"><time datetime="{modified}">Updated</time></span>'
        return (f'<html lang="en"><head><link rel="canonical" href="{self.url}">'
                f'<link rel="alternate" hreflang="en" href="{self.url}">'
                f'<link rel="alternate" hreflang="ko" href="{md.SITE}/ko/posts/example/">'
                f'{tags}{extra}<script type="application/ld+json">{raw}</script></head>'
                f'<body><h1>{html.escape(headline)}</h1>{dates}</body></html>')

    def errors(self, document):
        page = md.Metadata()
        page.feed(document)
        return '\n'.join(md.validate(self.url, page))

    def test_valid_special_characters_and_same_day_fallback_keep_source_values(self):
        self.assertEqual(self.errors(self.document(headline='Literal </script><script>alert(1)</script> \\u003c')), '')
        self.assertEqual(self.errors(self.document(modified=self.published)), '')

    def test_missing_duplicate_or_invalid_graph_is_rejected(self):
        source = self.document()
        self.assertIn('exactly one JSON-LD', self.errors(source.replace('application/ld+json', 'text/plain')))
        self.assertIn('exactly one JSON-LD', self.errors(source.replace('</head>', '<script type="application/ld+json">[]</script></head>')))
        self.assertIn('must parse', self.errors(source.replace('[{', 'invalid [{', 1)))
        self.assertIn('one BlogPosting', self.errors(source.replace('"BlogPosting"', '"WebPage"')))

    def test_metadata_identity_language_title_and_description_disagreements_fail(self):
        for change, message in [({'url': md.SITE + '/wrong/'}, 'URL identity'),
                                ({'inLanguage': 'ko'}, 'language'),
                                ({'headline': 'Wrong'}, 'visible h1'),
                                ({'description': 'Wrong'}, 'description tags')]:
            with self.subTest(change=change):
                self.assertIn(message, self.errors(self.document(graph_change=change)))

    def test_missing_or_duplicate_social_fields_fail(self):
        self.assertIn('article:published_time', self.errors(self.document().replace('article:published_time', 'missing')))
        self.assertIn('og:title', self.errors(self.document(extra='<meta property="og:title" content="duplicate">')))
        self.assertIn('twitter:title', self.errors(self.document().replace('twitter:title', 'missing')))

    def social_document(self):
        image = md.SITE + '/assets/img/social/example-en.png'
        fields = {'twitter:card': 'summary_large_image', 'og:image': image, 'twitter:image': image,
                  'og:image:type': 'image/png', 'og:image:width': '1200', 'og:image:height': '630',
                  'og:image:alt': 'Synchronous and reactive calls', 'twitter:image:alt': 'Synchronous and reactive calls'}
        extra = ''.join(f'<meta property="{k}" content="{v}">' for k, v in fields.items())
        return self.document(extra=extra, graph_change={'image': image})

    def test_large_image_metadata_agrees_with_article_and_local_asset(self):
        source = self.social_document()
        self.assertEqual(self.errors(source), '')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'en/posts/example/index.html'
            page.parent.mkdir(parents=True)
            page.write_text(source)
            self.assertIn('Social PNG must exist', '\n'.join(md.audit(root)[0]))
            asset = root / 'assets/img/social/example-en.png'
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\0\0\0\rIHDR' + (1200).to_bytes(4, 'big') + (630).to_bytes(4, 'big'))
            self.assertEqual(md.audit(root)[0], [])

    def test_large_image_missing_alt_or_mismatched_social_schema_fields_fail(self):
        source = self.social_document()
        self.assertIn('twitter:image', self.errors(source.replace('property="twitter:image"', 'property="missing"')))
        self.assertIn('BlogPosting image', self.errors(source.replace('"image": "' + md.SITE, '"image": "https://other.invalid')))
        self.assertIn('alternative text', self.errors(source.replace('content="Synchronous and reactive calls"', 'content=""')))

    def test_invalid_reversed_naive_and_mismatched_visible_dates_fail(self):
        for value in ['bad', '2000-01-01T00:00:00Z', '2026-10-27T05:23:47']:
            with self.subTest(value=value):
                self.assertIn('ordered timezone-aware', self.errors(self.document(modified=value)))
        document = self.document().replace(f'datetime="{self.modified}"', 'datetime="2026-10-28T00:00:00Z"')
        self.assertIn('Visible modification', self.errors(document))
        self.assertIn('Visible publication', self.errors(self.document().replace('class="publication-date"', 'class="missing"')))

    def test_author_and_actual_alternate_locale_policy_are_enforced(self):
        self.assertIn('author must match', self.errors(self.document(graph_change={'author': {'url': 'https://other.example/'}})))
        self.assertIn('actual alternate editions', self.errors(self.document().replace('content="ko_KR"', 'content="ja_JP"')))
        self.assertIn('without duplicates', self.errors(self.document(extra='<meta property="og:locale:alternate" content="ko_KR">')))

    def test_double_escaped_values_do_not_silently_disagree_with_visible_text(self):
        document = self.document().replace(r'\u003c', r'\\u003c')
        self.assertIn('visible h1', self.errors(document))

    def test_non_article_routes_exclude_blogposting_and_article_tags(self):
        url = md.SITE + '/en/about/'
        document = self.document().replace(self.url, url)
        page = md.Metadata()
        page.feed(document)
        self.assertIn('other routes must have none', '\n'.join(md.validate(url, page)))
        document = document.replace('"BlogPosting"', '"WebPage"').replace('content="article"', 'content="website"')
        page = md.Metadata()
        page.feed(document)
        self.assertIn('must not emit article metadata', '\n'.join(md.validate(url, page)))
        document = re.sub(r'<meta property="article:[^>]+>', '', document)
        page = md.Metadata()
        page.feed(document)
        self.assertEqual(md.validate(url, page), [])

    def test_audit_excludes_noindex_redirect_and_ownership_files_and_rejects_empty_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.subTest(empty=True):
                self.assertIn('No eligible', '\n'.join(md.audit(root)[0]))
            path = root / 'en/posts/example/index.html'
            path.parent.mkdir(parents=True)
            path.write_text(self.document())
            (root / 'googleverify.html').write_text('google-site-verification: sample')
            (root / 'noindex.html').write_text(self.document(extra='<meta name="robots" content="noindex">'))
            (root / 'redirect.html').write_text(self.document(extra='<meta http-equiv="refresh" content="0;url=/en/">'))
            errors, counts = md.audit(root)
            self.assertEqual(errors, [])
            self.assertEqual(counts, {'pages': 1, 'articles': 1})


if __name__ == '__main__':
    unittest.main()
