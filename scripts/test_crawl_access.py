import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import crawl_access as audit


def response(text, kind='text/html', status=200, **headers):
    return SimpleNamespace(text=text, status_code=status, headers={'Content-Type': kind, 'Set-Cookie': 'PRIVATE_COOKIE', **headers})


def fixture():
    base = audit.SITE
    en, ko, legacy = base + 'en/posts/topic/', base + 'ko/posts/topic/', base + 'old/topic/'
    selected = [{'url': url, 'expectedCanonical': ko if url == legacy else url,
                 'language': 'en' if url == en else 'ko', 'kind': 'legacy' if url == legacy else 'article'} for url in (en, ko, legacy)]
    alternates = f'<link rel="alternate" hreflang="en" href="{en}"><link rel="alternate" hreflang="ko" href="{ko}"><link rel="alternate" hreflang="x-default" href="{en}">'
    pages = {}
    for row in selected:
        refresh = '<meta http-equiv="refresh" content="0;url=/ko/posts/topic/">' if row['kind'] == 'legacy' else alternates
        pages[row['url']] = response(f'<html lang="{row["language"]}"><head><link rel="canonical" href="{row["expectedCanonical"]}">{refresh}</head><body>Article</body></html>')
    pages[base + 'robots.txt'] = response('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n', 'text/plain; charset=utf-8')
    pages[base + 'sitemap.xml'] = response('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + url + '</loc></url>' for url in (en, ko)) + '</urlset>', 'application/xml')
    return selected, pages


class CrawlAccessTests(unittest.TestCase):
    def test_scoped_and_repeated_headers_and_conditional_rules(self):
        self.assertEqual(audit.directives(['googlebot: noindex, bingbot: index'])['noindex'], {'googlebot': True, 'bingbot': False})
        self.assertEqual(audit.directives(['otherbot: noindex'])['noindex'], {'googlebot': False, 'bingbot': False})
        self.assertEqual(audit.directives(['googlebot: index', 'none'])['noindex'], {'googlebot': True, 'bingbot': True})
        self.assertTrue(audit.directives(['unavailable_after: 2020-01-01'])['requiresReview'])
        self.assertFalse(audit.directives(['max-snippet: -1, follow'])['requiresReview'])
        r = response('', **{'X-Robots-Tag': 'googlebot: index'})
        r.raw = SimpleNamespace(headers=SimpleNamespace(getlist=lambda name: ['googlebot: index', 'noindex']))
        self.assertEqual(len(audit.header_values(r)), 2)

    def test_robots_only_recognizes_the_current_explicit_policy(self):
        _, pages = fixture(); r = pages[audit.SITE + 'robots.txt']
        self.assertTrue(audit.robots_policy(r)['explicitAllowAll'])
        for bad in (response(r.text + '\nDisallow: /en/', 'text/plain'), response(r.text, 'text/plain', 404),
                    response(r.text, 'text/html'), response('User-agent: *\nDisallow: /*.pdf$', 'text/plain'), None):
            self.assertIsNone(audit.robots_policy(bad)['explicitAllowAll'])

    def test_headers_body_noindex_and_content_types_are_separate_from_canonical(self):
        selected, pages = fixture(); target = selected[0]; r = pages[target['url']]
        r.headers['X-Robots-Tag'] = 'bingbot: noindex'
        self.assertIn('http-header-noindex', audit.page_observation(target, r)['issues'])
        del r.headers['X-Robots-Tag']
        r.text = r.text.replace('<body>', '<body><meta name="robots" content="none">')
        self.assertIn('html-noindex', audit.page_observation(target, r)['issues'])
        r.headers['Content-Type'] = 'application/json'
        self.assertIn('not-html-content-type', audit.page_observation(target, r)['issues'])
        r.headers.pop('Content-Type')
        self.assertIn('missing-content-type', audit.page_observation(target, r)['unknown'])

    def test_collection_is_bounded_and_does_not_capture_cookies_or_call_search_apis(self):
        selected, pages = fixture(); requested = []
        def get(url, **kwargs):
            requested.append(url)
            self.assertFalse(kwargs['allow_redirects'])
            self.assertEqual(kwargs['headers']['User-Agent'], 'youdozi-blog-crawl-audit/1.0')
            return pages[url]
        result = audit.collect(selected, get)
        self.assertEqual(result['summary'], {'checks-passed': 3})
        self.assertEqual(len(requested), 5)
        self.assertNotIn('PRIVATE_COOKIE', json.dumps(result))
        bad = deepcopy(selected); bad[0]['url'] = 'https://outside.example/'
        with self.assertRaises(ValueError): audit.collect(bad, get)
        self.assertEqual(len(requested), 5)

    def test_broken_reciprocity_and_unobserved_alternates_never_pass(self):
        selected, pages = fixture(); en, ko = selected[:2]
        pages[ko['url']].text = pages[ko['url']].text.replace('hreflang="en"', 'hreflang="fr"')
        result = audit.collect(selected, lambda url, **kwargs: pages[url])
        self.assertEqual(result['urls'][0]['state'], 'issue')
        selected, pages = fixture(); pages[en['url']].text = pages[en['url']].text.replace('</head>', '<link rel="alternate" hreflang="fr" href="https://outside.example/alternate/"></head>')
        requested = []
        def get(url, **kwargs): requested.append(url); return pages[url]
        result = audit.collect(selected, get)
        self.assertEqual(result['urls'][0]['state'], 'unknown')
        self.assertEqual(len(requested), 5)
        selected, pages = fixture()
        for row in selected[:2]:
            other = ko['url'] if row['language'] == 'en' else en['url']
            language = 'ko' if row['language'] == 'en' else 'en'
            pages[row['url']].text = pages[row['url']].text.replace(f'<link rel="alternate" hreflang="{language}" href="{other}">', '')
        result = audit.collect(selected, lambda url, **kwargs: pages[url])
        self.assertTrue(all('published-edition-hreflang-missing-or-wrong' in row['issues'] for row in result['urls'][:2]))

    def test_transport_errors_and_unrecognized_policy_remain_unknown(self):
        selected, pages = fixture()
        def get(url, **kwargs):
            if url.endswith(('robots.txt', 'sitemap.xml')): raise RuntimeError('PRIVATE_EXCEPTION_DETAILS')
            return pages[url]
        result = audit.collect(selected, get)
        self.assertEqual(result['summary'], {'unknown': 3})
        self.assertNotIn('PRIVATE_EXCEPTION_DETAILS', json.dumps(result))

    def test_preview_and_report_modes_do_not_collect_or_write(self):
        with patch('sys.argv', ['crawl_access.py']), patch.object(audit, 'collect') as collect:
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 0)
            collect.assert_not_called()
        selected, pages = fixture(); report = audit.collect(selected, lambda url, **kwargs: pages[url])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'; path.write_text(json.dumps(report))
            with patch('sys.argv', ['crawl_access.py', '--report', str(path)]), patch.object(audit, 'collect') as collect:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 0)
                collect.assert_not_called()
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_live_requires_safe_exclusive_private_output_before_any_http_requests(self):
        selected, pages = fixture(); requested = []
        def get(url, **kwargs): requested.append(url); return pages[url]
        with tempfile.TemporaryDirectory() as directory, patch.object(audit, 'targets', return_value=selected), patch.dict('sys.modules', {'requests': SimpleNamespace(get=get)}):
            output = Path(directory) / 'snapshot.json'
            argv = ['crawl_access.py', '--live', '--output', str(output)]
            with patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 0)
            original = output.read_bytes()
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(len(requested), 5)
            with patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 1)
            self.assertEqual(output.read_bytes(), original)
            unsafe = Path(audit.__file__).resolve().parents[1] / 'unsafe-crawl.json'
            with patch('sys.argv', argv[:-1] + [str(unsafe)]), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 1)
            self.assertEqual(len(requested), 5)
            pages[audit.SITE + 'robots.txt'].status_code = 503
            with patch('sys.argv', argv[:-1] + [str(Path(directory) / 'partial.json')]), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(audit.main(), 2)
            self.assertEqual(json.loads((Path(directory) / 'partial.json').read_text())['summary'], {'unknown': 3})


if __name__ == '__main__':
    unittest.main()
