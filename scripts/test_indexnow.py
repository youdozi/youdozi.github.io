import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import indexnow as ix


class IndexNowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dist = self.root / 'dist'
        self.dist.mkdir()
        self.state = self.root / 'state.json'
        self.key = 'a' * 32
        (self.dist / ix.KEY_PATH).write_text(self.key)

    def page(self, path='/en/posts/example/', body='original', chrome='footer', **options):
        url = ix.SITE + path
        p = self.dist / path.lstrip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        canonical = options.get('canonical', url)
        extra = options.get('extra', '')
        p.write_text(f'<html><head><title>Example</title><meta name="description" content="summary">'
                     f'<link rel="canonical" href="{canonical}">{extra}</head>'
                     f'<body><header>{chrome}</header><main><p>{body}</p></main><footer>{chrome}</footer></body></html>')
        return url

    def sitemap(self, urls):
        (self.dist / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>')

    def transport(self, status=200):
        calls = []
        def fetch(request):
            calls.append(request)
            if request.get_method() == 'GET':
                return 200, self.key.encode(), ix.SITE + '/' + ix.KEY_PATH
            return status, b'', ix.ENDPOINT
        return calls, fetch

    def test_only_sitemap_pages_are_fingerprinted_and_preview_has_no_side_effects(self):
        url = self.page()
        self.page('/ja/digest/unapproved/')
        (self.dist / '.pipeline').mkdir()
        (self.dist / '.pipeline/draft.json').write_text('{"private":true}')
        self.sitemap([url])
        result = ix.run(self.dist, self.state, fetch=lambda _: self.fail('Preview must not call network'))
        self.assertEqual(result['changedUrls'], 1)
        self.assertFalse(self.state.exists())
        self.assertEqual(set(ix.build_manifest(self.dist)['pages']), {url})

    def test_content_additions_edits_and_deletions_are_detected_but_chrome_is_ignored(self):
        url = self.page(); self.sitemap([url]); before = ix.build_manifest(self.dist)
        self.page(chrome='updated footer')
        self.assertEqual(ix.changed_urls(before, ix.build_manifest(self.dist)), [])
        self.page(body='corrected content'); added = self.page('/ko/digest/new/')
        self.sitemap([url, added]); current = ix.build_manifest(self.dist)
        self.assertEqual(ix.changed_urls(before, current), sorted([url, added]))
        self.sitemap([added]); after = ix.build_manifest(self.dist)
        self.assertEqual(ix.changed_urls(current, after), [url])

    def test_excluded_redirect_and_wrong_canonical_pages_fail_closed(self):
        for options in [{'extra':'<meta name="robots" content="noindex,follow">'},
                        {'extra':'<meta http-equiv="refresh" content="0;url=/en/">'},
                        {'canonical':ix.SITE+'/en/'}]:
            with self.subTest(options=options):
                url = self.page(**options); self.sitemap([url])
                with self.assertRaises(ValueError): ix.build_manifest(self.dist)

    def test_foreign_private_queried_and_traversal_urls_are_rejected(self):
        for url in ['https://attacker.example/en/', ix.SITE+'/.pipeline/draft/',
                    ix.SITE+'/en/review/private/', ix.SITE+'/en/posts/test/?secret=x',
                    ix.SITE+'/en/posts/%2e%2e/', ix.SITE+'/en/posts/a%2fb/',
                    'https://user@youdozi.github.io/en/', ix.SITE+'/en/#fragment']:
            with self.subTest(url=url):
                with self.assertRaises(ValueError): ix.public_url(url)

    def test_spanish_notifications_follow_the_supported_language_policy(self):
        policy = json.loads((Path(__file__).resolve().parents[1] / 'src/lib/locales.json').read_text())
        self.assertEqual(set(ix.LANGUAGES), set(policy['baseLanguages'] + policy['translationLanguages']))
        url = self.page('/es/digest/example/')
        self.sitemap([url])
        calls, fetch = self.transport()
        self.assertEqual(ix.run(self.dist, self.state, submit=True, fetch=fetch)['httpStatus'], 200)
        self.assertEqual(json.loads(calls[1].data)['urlList'], [url])

    def test_acknowledged_notification_updates_state_and_unchanged_rerun_sends_nothing(self):
        url = self.page(); self.sitemap([url]); calls, fetch = self.transport(status=202)
        result = ix.run(self.dist, self.state, submit=True, fetch=fetch)
        self.assertEqual(result['httpStatus'], 202)
        payload = json.loads(calls[1].data)
        self.assertEqual(payload['urlList'], [url])
        self.assertEqual(payload['keyLocation'], ix.SITE+'/'+ix.KEY_PATH)
        self.assertEqual(ix.run(self.dist, self.state, submit=True,
            fetch=lambda _: self.fail('Unchanged pages must not be notified'))['changedUrls'], 0)

    def test_failed_notification_preserves_last_acknowledged_state_for_retry(self):
        url = self.page(); self.sitemap([url]); _, fetch = self.transport()
        ix.run(self.dist, self.state, submit=True, fetch=fetch)
        saved = self.state.read_bytes(); self.page(body='changed')
        _, failure = self.transport(status=429)
        with self.assertRaises(RuntimeError): ix.run(self.dist, self.state, submit=True, fetch=failure)
        self.assertEqual(self.state.read_bytes(), saved)
        calls, success = self.transport()
        self.assertEqual(ix.run(self.dist, self.state, submit=True, fetch=success)['changedUrls'], 1)
        self.assertEqual(len(calls), 2)

    @patch('indexnow.time.sleep')
    def test_key_mismatch_never_posts_and_malformed_state_never_notifies(self, sleep):
        url = self.page(); self.sitemap([url]); calls = []
        def fetch(request):
            calls.append(request)
            return 200, b'wrong-key', request.full_url
        with self.assertRaises(RuntimeError): ix.run(self.dist, self.state, submit=True, fetch=fetch)
        self.assertTrue(all(r.get_method()=='GET' for r in calls))
        self.assertEqual(len(calls), 6)
        self.assertFalse(self.state.exists())
        self.state.write_text('{"schemaVersion":1,"site":"https://other.example","pages":{}}')
        with self.assertRaises(ValueError): ix.run(self.dist, self.state, submit=True,
            fetch=lambda _: self.fail('Malformed state must fail before network'))

    def test_deletions_are_submitted_and_invalid_fingerprints_fail(self):
        deleted = self.page(); keep = self.page('/ko/posts/keep/')
        self.sitemap([deleted, keep]); _, fetch = self.transport()
        ix.run(self.dist, self.state, submit=True, fetch=fetch)
        self.sitemap([keep]); calls, fetch = self.transport()
        ix.run(self.dist, self.state, submit=True, fetch=fetch)
        self.assertEqual(json.loads(calls[1].data)['urlList'], [deleted])
        with self.assertRaises(ValueError): ix.validate_manifest({'schemaVersion':1,'site':ix.SITE,'pages':{keep:'bad'}})


if __name__ == '__main__':
    unittest.main()
