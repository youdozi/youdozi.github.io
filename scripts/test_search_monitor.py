from datetime import datetime, timedelta, timezone
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import search_monitor as monitor
from install_search_monitor import specification


def response(text, kind='text/html', status=200):
    return SimpleNamespace(text=text, status_code=status, headers={'Content-Type': kind, 'Set-Cookie': 'PRIVATE_COOKIE'})


def public_pages():
    urls = [monitor.SITE + lang + '/' for lang in ('en', 'ko')]
    alternates = ''.join(f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang, url in zip(('en', 'ko', 'x-default'), urls + urls[:1]))
    pages = {monitor.SITE + 'sitemap.xml': response('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>', 'application/xml'),
             monitor.SITE + 'robots.txt': response('User-agent: *\nAllow: /\nSitemap: ' + monitor.SITE + 'sitemap.xml\n', 'text/plain')}
    for url, lang, other in zip(urls, ('en', 'ko'), ('ko_KR', 'en_US')):
        meta = {'og:url': url, 'og:title': 'Title', 'twitter:title': 'Title', 'description': 'Description',
                'og:description': 'Description', 'twitter:description': 'Description', 'og:site_name': 'Site',
                'og:locale': monitor.LOCALES[lang]['ogLocale'], 'og:locale:alternate': other, 'og:type': 'website'}
        head = ''.join(f'<meta property="{key}" content="{value}">' for key, value in meta.items())
        pages[url] = response(f'<html lang="{lang}"><head><link rel="canonical" href="{url}">{alternates}{head}<script type="application/ld+json">[{{"@type":"WebPage"}}]</script></head><body><div class="prose"><img src="/assets/example.svg" alt="Flow"></div></body></html>')
    pages[monitor.SITE + 'assets/example.svg'] = response('<svg/>', 'image/svg+xml')
    return urls, pages


def ga(body):
    dimensions = [d['name'] for d in body.get('dimensions', [])]
    metrics = [m['name'] for m in body['metrics']]
    row = {'metricValues': [{'value': '10'} for _ in metrics]}
    if dimensions: row['dimensionValues'] = [{'value': {'landingPage': '/en/posts/example/', 'sessionSource': 'chatgpt.com', 'sessionMedium': 'referral'}[d]} for d in dimensions]
    return {'httpStatus': 200, 'data': {'dimensionHeaders': [{'name': d} for d in dimensions],
            'metricHeaders': [{'name': m} for m in metrics], 'rows': [row], 'metadata': {'timeZone': 'Asia/Seoul'}}}


def gsc(kind, body):
    return {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}} if kind == 'inspect' else {'rows': [{'clicks': 5, 'impressions': 50}]}}


def bing(method, params):
    return {'httpStatus': 200, 'data': [{'Url': monitor.SITE.rstrip('/')}]} if method == 'GetUserSites' else {'httpStatus': 200, 'data': [] if method == 'GetRankAndTrafficStats' else {'Url': params['url'], 'HttpStatus': 200, 'LastCrawledDate': '/Date(1793491200000)/'}}


class SearchMonitorTests(unittest.TestCase):
    def test_daily_checks_metadata_reciprocity_and_deduplicated_images_without_credentials(self):
        urls, pages = public_pages(); requested = []
        def get(url, **kwargs):
            requested.append(url); self.assertFalse(kwargs['allow_redirects']); return pages[url]
        with patch.object(monitor, 'headless_gsc_token', side_effect=AssertionError('No credentials')):
            report = monitor.daily(get)
        self.assertEqual(report['state'], 'passed')
        self.assertEqual(len(report['urls']), 2)
        self.assertEqual(requested.count(monitor.SITE + 'assets/example.svg'), 1)
        self.assertNotIn('PRIVATE_COOKIE', json.dumps(report))
        pages[urls[0]].text = pages[urls[0]].text.replace('content="website"', 'content="article"')
        self.assertEqual(monitor.daily(get)['state'], 'failed')

    def test_daily_failed_assets_and_response_errors_do_not_pass(self):
        urls, pages = public_pages()
        pages[monitor.SITE + 'assets/example.svg'] = response('Soft 404', 'text/html')
        self.assertEqual(monitor.daily(lambda url, **kw: pages[url])['state'], 'failed')
        pages.pop(urls[0])
        report = monitor.daily(lambda url, **kw: pages[url])
        self.assertEqual(report['state'], 'failed')
        self.assertGreater(report['summary']['unknown'], 0)

    def test_daily_missing_sitemap_is_reported_and_external_urls_are_rejected(self):
        self.assertEqual(monitor.daily(lambda *a, **kw: response('', status=500))['state'], 'failed')
        for url in ('https://outside.example/en/', monitor.SITE + 'en/?secret=x', monitor.SITE + 'en/../ko/'):
            with self.assertRaises(ValueError): monitor.selected_targets([url])
        with self.assertRaises(ValueError): monitor.selected_targets([monitor.SITE + 'en/'] * 2)

    def test_weekly_dates_are_two_disjoint_seven_day_pt_windows(self):
        now = datetime(2026, 11, 3, 2, tzinfo=timezone.utc)
        spans = monitor.weekly_windows(now)
        self.assertEqual(spans['current'], {'start': '2026-10-24', 'end': '2026-10-30'})
        self.assertEqual(spans['previous'], {'start': '2026-10-17', 'end': '2026-10-23'})

    def test_selection_covers_locales_and_stays_public_and_bounded(self):
        urls = [monitor.SITE + lang + '/' for lang in monitor.LOCALES]
        urls += [monitor.SITE + f'{lang}/posts/2026-11-{day:02}-topic/' for lang in monitor.LOCALES for day in range(1, 10)]
        selected = monitor.index_sample(urls)
        self.assertEqual(len(selected), 32)
        self.assertEqual({r['language'] for r in selected}, set(monitor.LOCALES))
        self.assertTrue(all(r['url'] in urls for r in selected))

    def test_recent_sample_orders_dates_across_posts_and_digests(self):
        urls = [monitor.SITE + f'en/posts/2026-01-0{day}-old/' for day in (1, 2, 3)]
        latest = monitor.SITE + 'en/digest/2026-11-03-new/'
        selected = monitor.index_sample(urls + [latest])
        self.assertIn(latest, [r['url'] for r in selected])

    def test_stats_throttle_defers_bing_urls_and_budget_defers_all_inspections(self):
        urls, _ = public_pages(); calls = []
        def throttled(method, params):
            calls.append(method)
            return {'httpStatus': 429, 'apiErrorCode': 4, 'error': 'throttle'} if method == 'GetRankAndTrafficStats' else bing(method, params)
        report = monitor.weekly(datetime.now(timezone.utc), urls, gsc, ga, throttled, pause=lambda _: None)
        self.assertNotIn('GetUrlInfo', calls)
        self.assertTrue(all(r['bing']['notRequested'] for r in report['indexSample']))
        with patch.object(monitor, 'index_sample', return_value=monitor.selected_targets(urls)):
            def forbidden(*args): raise AssertionError('No API after deadline')
            report = monitor.weekly(datetime.now(timezone.utc), urls, forbidden, forbidden, forbidden, pause=lambda _: None, budget_seconds=0)
        self.assertTrue(all(r['google']['notRequested'] and r['bing']['notRequested'] for r in report['indexSample']))
        self.assertEqual(report['periods']['current']['gscTotals']['error'], 'request-budget-exceeded')

    def test_unexpected_failure_is_private_and_retains_retry_spacing(self):
        _, pages = public_pages()
        with tempfile.TemporaryDirectory() as folder:
            argv = ['search_monitor.py', 'weekly', '--live', '--scheduled', '--output-dir', folder]
            with patch('sys.argv', argv), patch.dict('sys.modules', {'requests': SimpleNamespace(get=lambda url, **kw: pages[url])}), patch.object(monitor, 'live_weekly', side_effect=RuntimeError('PRIVATE_EXCEPTION')):
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(monitor.main(), 2)
            state = json.loads((Path(folder) / 'weekly-state.json').read_text())
            self.assertEqual(state['lastOutcome'], 'failed')
            self.assertFalse(monitor.due(datetime.now(timezone.utc), state))
            reports = [p for p in Path(folder).glob('weekly-*.json') if p.name != 'weekly-state.json']
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0].stat().st_mode & 0o777, 0o600)
            self.assertNotIn('PRIVATE_EXCEPTION', reports[0].read_text())

    def test_headless_refresh_cannot_follow_an_interactive_client_environment(self):
        credential = SimpleNamespace(valid=False, token='TEST_TOKEN', refresh=lambda _: None, to_json=lambda: '{"token":"TEST_TOKEN"}')
        fake = SimpleNamespace(from_authorized_user_file=lambda _: credential)
        with patch.dict('os.environ', {'GOOGLE_OAUTH_CLIENT_FILE': '/must-not-open.json'}), patch.dict('sys.modules', {'google.auth.transport.requests': SimpleNamespace(Request=lambda: None), 'google.oauth2.credentials': SimpleNamespace(Credentials=fake)}), patch.object(monitor, 'private_json') as save:
            self.assertEqual(monitor.headless_gsc_token(), 'TEST_TOKEN')
            save.assert_called_once()

    def test_weekly_observations_preserve_failures_and_do_not_claim_ai_citations(self):
        urls, _ = public_pages()
        report = monitor.weekly(datetime.now(timezone.utc), urls, gsc, ga, bing, pause=lambda _: None)
        self.assertEqual(report['state'], 'passed')
        self.assertEqual(report['changes']['clicks']['absoluteChange'], 0)
        self.assertEqual(len(report['periods']['current']['aiDomainMatchedRows']), 1)
        self.assertEqual(report['dedicatedAIReports']['google'], 'not-collected')
        self.assertIsNone(report['indexSample'][0]['bing']['indexingConfirmed'])
        failed = monitor.weekly(datetime.now(timezone.utc), urls, lambda *a: {'error': 'auth-failure'}, lambda *a: {'error': 'auth-failure'}, bing, pause=lambda _: None)
        self.assertEqual(failed['state'], 'partial-failure')
        self.assertIsNone(failed['changes']['clicks']['absoluteChange'])
        self.assertIsNone(failed['changes']['ga:sessions']['current'])

    def test_bing_throttle_stops_further_url_calls(self):
        urls, _ = public_pages(); calls = []
        def throttled(method, params):
            if method != 'GetUrlInfo': return bing(method, params)
            calls.append(params); return {'httpStatus': 429, 'apiErrorCode': 4, 'error': 'throttle'}
        report = monitor.weekly(datetime.now(timezone.utc), urls, gsc, ga, throttled, pause=lambda _: None)
        self.assertEqual(len(calls), 1)
        self.assertTrue(report['indexSample'][1]['bing']['notRequested'])
        self.assertEqual(report['state'], 'partial-failure')

    def test_bing_retry_preserves_google_performance_and_original_snapshot(self):
        urls, _ = public_pages()
        report = monitor.weekly(datetime.now(timezone.utc), urls, gsc, ga, bing, pause=lambda _: None)
        report.update({'schemaVersion': 1, 'apiErrors': ['bing:url-observation'], 'state': 'partial-failure'})
        report['indexSample'][0]['bing'] = {'error': 'throttle', 'apiErrorCode': 5}
        original = json.dumps(report, sort_keys=True); calls = []
        def observe(method, params): calls.append(method); return bing(method, params)
        result = monitor.retry_bing(report, urls, observe, datetime.now(timezone.utc), pause=lambda _: None)
        self.assertEqual(result['state'], 'passed')
        self.assertEqual(calls, ['GetUrlInfo'])
        self.assertEqual(result['periods'], report['periods'])
        self.assertEqual(result['observedAt'], report['observedAt'])
        self.assertEqual(json.dumps(report, sort_keys=True), original)

    def test_scheduled_bing_retry_does_not_requery_google_or_ga(self):
        urls, pages = public_pages(); now = datetime.now(timezone.utc)
        report = monitor.weekly(now, urls, gsc, ga, bing, pause=lambda _: None)
        report.update({'schemaVersion': 1, 'apiErrors': ['bing:url-observation'], 'state': 'partial-failure'})
        report['indexSample'][0]['bing'] = {'error': 'throttle', 'apiErrorCode': 5}
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder); name = f'weekly-{now:%Y%m%dT%H%M%S%fZ}.json'
            (directory / name).write_text(json.dumps(report))
            (directory / 'weekly-state.json').write_text(json.dumps({'pendingReport': name, 'pendingSlot': monitor.weekly_slot(now).isoformat(), 'attemptedAt': (now - timedelta(hours=7)).isoformat()}))
            config = directory / 'config'; config.mkdir(); (config / 'bing-api-key.txt').write_text('DUMMY')
            argv = ['search_monitor.py', 'weekly', '--live', '--scheduled', '--output-dir', folder]
            with patch('sys.argv', argv), patch.dict('sys.modules', {'requests': SimpleNamespace(get=lambda url, **kw: pages[url])}), patch.object(monitor, 'CONFIG', config), patch.object(monitor, 'live_weekly', side_effect=AssertionError('No Google/GA rescan')), patch.object(monitor, 'bing_get', side_effect=lambda key, method, params: bing(method, params)):
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(monitor.main(), 0)
            state = json.loads((directory / 'weekly-state.json').read_text())
            self.assertEqual(state['successfulSlot'], monitor.weekly_slot(now).isoformat())
            self.assertNotIn('pendingReport', state)
            revised = json.loads(next(path for path in directory.glob('weekly-*.json') if path.name not in (name, 'weekly-state.json')).read_text())
            self.assertEqual(revised['observedAt'], report['observedAt'])
            self.assertIn('bingRecheckedAt', revised)

    def test_failed_prerequisite_preserves_pending_bing_snapshot(self):
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder); name = f'weekly-{now:%Y%m%dT%H%M%S%fZ}.json'
            pending = {'pendingReport': name, 'pendingSlot': monitor.weekly_slot(now).isoformat(),
                       'attemptedAt': (now - timedelta(hours=7)).isoformat()}
            state_path = directory / 'weekly-state.json'
            state_path.write_text(json.dumps(pending))
            argv = ['search_monitor.py', 'weekly', '--live', '--scheduled', '--output-dir', folder]
            with patch('sys.argv', argv), patch.object(monitor, 'sitemap', return_value={'error': 'temporary-failure'}), patch.object(monitor, 'live_weekly') as live:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(monitor.main(), 2)
                live.assert_not_called()
            state = json.loads(state_path.read_text())
            self.assertEqual(state['pendingReport'], name)
            self.assertEqual(state['pendingSlot'], pending['pendingSlot'])
            self.assertFalse(monitor.due(now + timedelta(hours=5), state))
            self.assertTrue(monitor.due(now + timedelta(hours=7), state))

    def test_scheduled_success_and_six_hour_failure_backoff(self):
        now = datetime(2026, 11, 9, 0, tzinfo=timezone.utc)
        slot = monitor.weekly_slot(now)
        self.assertEqual((slot.weekday(), slot.hour, slot.minute), (0, 8, 37))
        self.assertTrue(monitor.due(now, {}))
        self.assertFalse(monitor.due(now, {'successfulSlot': slot.isoformat()}))
        self.assertFalse(monitor.due(now, {'attemptedAt': (now - timedelta(hours=5)).isoformat()}))
        self.assertTrue(monitor.due(now, {'attemptedAt': (now - timedelta(hours=6)).isoformat()}))
        self.assertLess(monitor.weekly_slot(now - timedelta(hours=1)), slot)

    def test_preview_does_not_initialize_auth_or_write(self):
        with patch('sys.argv', ['search_monitor.py', 'weekly']), patch.object(monitor, 'live_weekly') as live, patch.object(monitor, 'headless_gsc_token') as token:
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(monitor.main(), 0)
            live.assert_not_called(); token.assert_not_called()

    def test_unsafe_output_fails_before_credentials_or_network(self):
        with patch('sys.argv', ['search_monitor.py', 'weekly', '--live', '--output-dir', str(monitor.ROOT / '.pipeline')]), patch.object(monitor, 'live_weekly') as live:
            with self.assertRaises(ValueError): monitor.main()
            live.assert_not_called()

    def test_scheduler_retries_due_work_after_login_without_exposing_secrets(self):
        spec = specification(Path('/repo'), Path('/private/home'))
        self.assertEqual(spec['StartCalendarInterval'], {'Weekday': 1, 'Hour': 8, 'Minute': 37})
        self.assertTrue(spec['RunAtLoad']); self.assertEqual(spec['StartInterval'], 3600)
        self.assertNotIn('EnvironmentVariables', spec)
        self.assertIn('run_search_monitor.sh', spec['ProgramArguments'][1])

    def test_workflow_is_public_daily_only_and_never_uses_google_secrets(self):
        workflow = (monitor.ROOT / '.github/workflows/search-monitor.yml').read_text()
        self.assertIn("cron: '17 22 * * *'", workflow)
        self.assertIn("github.event_name != 'pull_request'", workflow)
        self.assertNotIn('secrets.', workflow)
        self.assertNotIn('weekly --live', workflow)
        shell = (monitor.ROOT / 'scripts/run_search_monitor.sh').read_text()
        self.assertIn('!= main', shell); self.assertIn('--scheduled', shell)


if __name__ == '__main__': unittest.main()
