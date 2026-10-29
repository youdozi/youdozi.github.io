from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from xml.sax.saxutils import escape

from check_translation_preview import check

ID = 'a' * 16
KEY = 'es-' + ID
TITLE = 'Fixture translation'


class TranslationPreviewTests(unittest.TestCase):
    def fixture(self, base, editions=1):
        (base/'src/content/translations').mkdir(parents=True)
        (base/'src/content/renewals').mkdir(parents=True)
        (base/'dist/es').mkdir(parents=True)
        (base/'.translation-preview-fixture.json').write_text(json.dumps({'fixtureOnly': True, 'fixtureKeys': [KEY]}))
        rows = []
        for i in range(editions):
            source_id = ID if i == 0 else f'{i:016x}'
            slug = 'fixture-' + str(i)
            record = {'renewalId': source_id, 'language': 'es', 'updatedAt': f'2026-10-{28-i%27:02d}T00:00:00+00:00',
                      'edition': {'title': TITLE, 'claims': ['Claim one.', 'Claim two.'], 'followUp': ['Later restriction.']},
                      'approval': {'reviewedBy': 'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL'}}
            (base/f'src/content/renewals/{source_id}.json').write_text(json.dumps({'slug': slug}))
            (base/f'src/content/translations/es-{source_id}.json').write_text(json.dumps(record))
            rows.append({'url': f'/es/digest/{slug}/', 'title': TITLE, 'content': 'Claim one. Claim two. Later restriction.'})
        for lang in ('en', 'ko', 'es'):
            path = base/f'dist/{lang}/digest/fixture-0/index.html'; path.parent.mkdir(parents=True, exist_ok=True)
            alternates = ''.join(f'<link rel="alternate" hreflang="{other}" href="https://youdozi.github.io/{other}/digest/fixture-0/">' for other in ('en', 'ko', 'es'))
            alternates += '<link rel="alternate" hreflang="x-default" href="https://youdozi.github.io/en/digest/fixture-0/">'
            path.write_text(f'<html lang="{lang}"><head><link rel="canonical" href="https://youdozi.github.io/{lang}/digest/fixture-0/">{alternates}</head><body><article class="article"><h1>{TITLE}</h1><p>Claim one.</p><p>Claim two.</p><p>Later restriction.</p></article></body></html>')
        (base/'dist/es/search-index.json').write_text(json.dumps(rows))
        records = {f'/es/digest/fixture-{i}/': json.loads((base/f'src/content/translations/es-{ID if i == 0 else f"{i:016x}"}.json').read_text()) for i in range(editions)}
        selected = sorted(rows, key=lambda row: records[row['url']]['updatedAt'], reverse=True)[:30]
        items = ''.join('<item><link>https://youdozi.github.io'+row['url']+'</link><description>'+escape(row['content'])+'</description></item>' for row in selected)
        (base/'dist/es/feed.xml').write_text('<rss><channel>'+items+'</channel></rss>')
        (base/'dist/sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://youdozi.github.io/es/digest/fixture-0/</loc></url></urlset>')

    def test_isolated_edition_checks_visible_claims_followup_rss_and_language_group(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); self.fixture(base)
            self.assertEqual(check(base), {'fixtureEditions': 1, 'claimsAndFollowUp': 3, 'languageGroups': 1,
                                           'fixtureEditionsInRSS': 1, 'translationRSSPoliciesChecked': 1, 'fixtureOnly': True})

    def test_missing_visible_claim_cannot_be_satisfied_by_hidden_json_or_search(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); self.fixture(base)
            path = base/'dist/es/digest/fixture-0/index.html'
            path.write_text(path.read_text().replace('<p>Claim two.</p>', '<script type="application/ld+json">"Claim two."</script>'))
            with self.assertRaisesRegex(ValueError, 'omits'): check(base)

    def test_missing_search_claim_and_rss_claim_are_both_rejected(self):
        for surface in ('search', 'rss'):
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as folder:
                base = Path(folder); self.fixture(base)
                path = base/('dist/es/search-index.json' if surface == 'search' else 'dist/es/feed.xml')
                path.write_text(path.read_text().replace('Later restriction.', ''))
                with self.assertRaisesRegex(ValueError, 'omits'): check(base)

    def test_rss_latest_30_selection_and_order_are_verified(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); self.fixture(base, 31)
            self.assertEqual(check(base)['translationRSSPoliciesChecked'], 1)
            path = base/'dist/es/feed.xml'
            path.write_text(path.read_text().replace('fixture-1/', 'fixture-30/'))
            with self.assertRaisesRegex(ValueError, 'latest 30'): check(base)

    def test_mixed_technical_and_news_feed_uses_explicit_per_edition_dates(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); self.fixture(base)
            path = base/'src/content/technical-translations/es/2026-10-01-tech.md'
            path.parent.mkdir(parents=True)
            data = {'state': 'approved', 'kind': 'post', 'language': 'es', 'routeSlug': '2026-10-01-tech', 'updatedAt': '2026-10-29T00:00:00+00:00'}
            path.write_text('---\n'+json.dumps(data)+'\n---\nTechnical body')
            index = base/'dist/es/search-index.json'; rows = json.loads(index.read_text())
            rows.append({'url': '/es/posts/2026-10-01-tech/', 'title': 'Technical title', 'content': 'Technical body'})
            index.write_text(json.dumps(rows))
            feed = base/'dist/es/feed.xml'; content = feed.read_text()
            tech = '<item><link>https://youdozi.github.io/es/posts/2026-10-01-tech/</link><description>Technical body</description></item>'
            feed.write_text(content.replace('<channel>', '<channel>'+tech))
            self.assertEqual(check(base)['translationRSSPoliciesChecked'], 1)
            feed.write_text(content.replace('</channel>', tech+'</channel>'))
            with self.assertRaisesRegex(ValueError, 'latest 30'): check(base)

    def test_missing_sitemap_or_counterpart_alternate_is_rejected(self):
        for surface in ('sitemap', 'alternate'):
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as folder:
                base = Path(folder); self.fixture(base)
                if surface == 'sitemap':
                    path = base/'dist/sitemap.xml'; path.write_text(path.read_text().replace('fixture-0/', 'missing/'))
                else:
                    path = base/'dist/ko/digest/fixture-0/index.html'
                    path.write_text(path.read_text().replace('hreflang="es"', 'hreflang="de"'))
                with self.assertRaises(ValueError): check(base)

    def test_marker_cannot_accept_real_publication_or_path_traversal_as_a_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); self.fixture(base)
            path = base/f'src/content/translations/{KEY}.json'; data = json.loads(path.read_text())
            data['approval']['reviewedBy'] = 'Real reviewer'; path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'synthetic'): check(base)
            marker = base/'.translation-preview-fixture.json'
            marker.write_text(json.dumps({'fixtureOnly': True, 'fixtureKeys': ['../../outside']}))
            with self.assertRaisesRegex(ValueError, 'identity'): check(base)
            marker.write_text(json.dumps({'fixtureOnly': False, 'fixtureKeys': []}))
            with self.assertRaisesRegex(ValueError, 'marker'): check(base)


if __name__ == '__main__': unittest.main()
