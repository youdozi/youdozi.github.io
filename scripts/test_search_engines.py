import contextlib
from copy import deepcopy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import search_engines as audit


class SearchEngineTests(unittest.TestCase):
    def report(self, url_bing=None, selected=None):
        selected = audit.targets()[:3] if selected is None else selected
        def post(token, url, payload):
            if url.endswith('index:inspect'):
                return {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'PASS', 'googleCanonical': payload['inspectionUrl']}}}}
            return {'httpStatus': 200, 'data': {'rows': []}}
        def get(url, **kwargs):
            self.assertFalse(kwargs['allow_redirects'])
            if url.endswith('sitemap.xml'):
                return SimpleNamespace(status_code=200, text='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{t["url"]}</loc></url>' for t in selected[:2])+'</urlset>')
            target = next(t for t in selected if t['url'] == url)
            redirect = f'<meta http-equiv="refresh" content="0;url={target["expectedCanonical"].removeprefix(audit.SITE.rstrip("/"))}">' if target['kind'] == 'legacy' else ''
            return SimpleNamespace(status_code=200, text=f'<link rel="canonical" href="{target["expectedCanonical"]}">{redirect}', headers={})
        def bing(key, method, params):
            if method == 'GetUserSites': return {'httpStatus': 200, 'data': [{'Url': audit.SITE, 'IsVerified': True, 'AuthenticationCode': 'private-verification-code'}]}
            if method == 'GetUrlInfo' and url_bing is not None: return url_bing(key, method, params)
            if method == 'GetUrlInfo': return {'httpStatus': 200, 'data': {'Url': params['url'], 'HttpStatus': 0, 'LastCrawledDate': '/Date(-62135596800000)/'}}
            return {'httpStatus': 200, 'data': []}
        return audit.collect('private-google-token', 'private-bing-key', selected, datetime(2026, 10, 28, tzinfo=timezone.utc), post, get, bing)

    def test_targets_cover_current_public_files_without_a_fixed_corpus_size(self):
        targets = audit.targets()
        editions = set()
        for path in (audit.ROOT/'src/content/translations').glob('*.json'):
            record = json.loads(path.read_text())
            source = json.loads((audit.ROOT/f"src/content/renewals/{record['renewalId']}.json").read_text())
            editions.update((lang, source['slug']) for lang in ('en', 'ko', record['language']))
        self.assertEqual({(t['language'], t['key']) for t in targets if t['group'] == 'published-digest'}, editions)
        self.assertEqual(sum(t['kind'] == 'home' for t in targets), len(json.loads((audit.ROOT/'src/lib/locales.json').read_text())['locales']))
        self.assertEqual(sum(t['kind'] == 'legacy' for t in targets), 10)
        article_languages = {t['language'] for t in targets if t['kind'] == 'article'}
        self.assertEqual({t['language'] for t in targets if t['kind'] == 'archive'}, article_languages)
        for target in targets:
            if target['kind'] == 'archive':
                self.assertEqual(target['url'], audit.SITE + target['language'] + '/archive/')
                self.assertEqual(target['expectedCanonical'], target['url'])
        self.assertEqual(len({t['url'] for t in targets}), len(targets))

    def test_private_manuscripts_are_ignored_and_shared_public_counterparts_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            for relative in ['content/seo/core-articles.json', 'src/lib/locales.json']:
                target = base/relative; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((audit.ROOT/relative).read_bytes())
            (base/'src/content/renewals').mkdir(parents=True)
            (base/'src/content/translations').mkdir(parents=True)
            source_id = 'a'*16
            (base/f'src/content/renewals/{source_id}.json').write_text(json.dumps({'slug': 'test-public-brief'}))
            for lang in ['zh-CN', 'ja']:
                (base/f'src/content/translations/{lang}-{source_id}.json').write_text(json.dumps({'language': lang, 'renewalId': source_id}))
            private = base/'.pipeline/translations/batches'; private.mkdir(parents=True)
            (private/'not-public.json').write_text(json.dumps({'translations': [{'language': 'de', 'renewalId': source_id}]}))
            targets = audit.targets(base)
            rows = [t for t in targets if t['group'] == 'published-digest']
            self.assertEqual({t['language'] for t in rows}, {'en', 'ko', 'zh-CN', 'ja'})
            self.assertEqual(len(rows), 4)
            self.assertEqual({t['language'] for t in targets if t['kind'] == 'archive'}, {'en', 'ko', 'zh-CN', 'ja'})

    def test_bing_transport_never_follows_redirects_or_discloses_request_errors(self):
        def get(url, **kwargs):
            self.assertTrue(url.startswith(audit.BING_ENDPOINT))
            self.assertFalse(kwargs['allow_redirects'])
            self.assertEqual(kwargs['params']['apikey'], 'PRIVATE')
            raise RuntimeError('https://example/?apikey=PRIVATE')
        result = audit.bing_get('PRIVATE', 'GetUrlInfo', {'url': audit.SITE}, get)
        self.assertEqual(result, {'error': 'RuntimeError'})
        self.assertNotIn('PRIVATE', json.dumps(result))
        with self.assertRaises(ValueError): audit.bing_get('PRIVATE', 'SubmitUrl', {}, get)

    def test_bing_redirects_invalid_json_and_api_errors_are_not_empty_data(self):
        for response in [SimpleNamespace(status_code=302), SimpleNamespace(status_code=403), SimpleNamespace(status_code=200, json=lambda: {'ErrorCode': 1, 'Message': 'PRIVATE'})]:
            result = audit.bing_get('PRIVATE', 'GetFeeds', {}, lambda *a, **k: response)
            self.assertIn('error', result)
            self.assertNotIn('PRIVATE', json.dumps(result))
        response = SimpleNamespace(status_code=400, json=lambda: {'ErrorCode': 4, 'Message': 'PRIVATE'})
        self.assertEqual(audit.bing_get('PRIVATE', 'GetFeeds', {}, lambda *a, **k: response)['apiErrorCode'], 4)

    def test_crawl_sentinel_and_http_status_zero_never_confirm_index_membership(self):
        for date in ['/Date(-62135596800000)/', '/Date(0)/', 'invalid', None]:
            result = audit.bing_url({'httpStatus': 200, 'data': {'Url': audit.SITE, 'LastCrawledDate': date, 'HttpStatus': 0}})
            self.assertEqual(result['observation'], 'no-recorded-crawl')
            self.assertIsNone(result['indexingConfirmed'])
            self.assertIsNone(result['lastCrawledAt'])
        self.assertEqual(audit.bing_date('/Date(1609459200000)/'), '2021-01-01T00:00:00+00:00')
        self.assertIn('error', audit.bing_url({'httpStatus': 200, 'data': {}}))

    def test_collection_preserves_unknowns_and_removes_unneeded_verification_fields(self):
        report = self.report()
        self.assertEqual(report['summary']['en']['googlePass'], 1)
        self.assertEqual(report['summary']['ko']['bingCrawlRecords'], 0)
        self.assertIs(report['urls'][0]['inPublicSitemap'], True)
        self.assertIs(report['urls'][2]['inPublicSitemap'], False)
        self.assertTrue(report['urls'][2]['live']['matchesExpectedStaticRoute'])
        self.assertEqual(report['bingSite']['GetRankAndTrafficStats']['rows'], [])
        value = json.dumps(report)
        for secret in ['private-google-token', 'private-bing-key', 'private-verification-code', 'AuthenticationCode']:
            self.assertNotIn(secret, value)

    def test_archive_routes_flow_through_google_bing_and_static_checks(self):
        selected = [r for r in audit.targets() if r['kind'] == 'archive']
        report = self.report(selected=selected)
        self.assertEqual(len(report['urls']), len(selected))
        for item in report['summary'].values():
            self.assertEqual(item['byGroup'], {'archive': 1})
            self.assertEqual(item['liveMatches'], 1)
            self.assertEqual(item['googlePass'], 1)
            self.assertEqual(item['bingResponses'], 1)
            self.assertEqual(item['bingCrawlRecords'], 0)
        self.assertIn('색인 확정: 불가', audit.format_report(report))

    def test_google_empty_success_and_errors_are_not_a_loss_of_indexing(self):
        before = self.report(); after = deepcopy(before)
        after['urls'][0]['inspection'] = {'httpStatus': 200, 'indexStatus': {}}
        after['urls'][1]['inspection'] = {'httpStatus': 403}
        comparison = audit.compare(before, after)
        self.assertEqual(len(comparison['googleUncomparable']), 2)
        self.assertEqual(comparison['noLongerGooglePass'], [])
        after['urls'][2]['inspection']['indexStatus']['verdict'] = 'NEUTRAL'
        self.assertEqual(audit.compare(before, after)['noLongerGooglePass'], [after['urls'][2]['url']])
        after['urls'].pop()
        with self.assertRaises(ValueError): audit.compare(before, after)

    def test_bing_failed_read_cannot_be_counted_as_a_new_crawl(self):
        before = self.report(); after = deepcopy(before)
        after['urls'][0]['bing'].update({'observation': 'crawl-record-present', 'lastCrawledAt': '2026-10-28'})
        self.assertEqual(audit.compare(before, after)['newBingCrawlRecords'], [after['urls'][0]['url']])
        before['urls'][0]['bing']['error'] = 'Timeout'
        self.assertEqual(audit.compare(before, after)['newBingCrawlRecords'], [])

    def test_selection_migration_only_compares_common_urls(self):
        before = self.report(); after = deepcopy(before)
        removed = after['urls'].pop()
        added = deepcopy(after['urls'][0])
        added.update({'url': audit.SITE + 'en/archive/', 'kind': 'archive', 'group': 'archive'})
        added['bing'].update({'observation': 'crawl-record-present', 'lastCrawledAt': '2026-10-28'})
        after['urls'].append(added)
        after['urls'][0]['inspection']['indexStatus']['verdict'] = 'NEUTRAL'
        frozen = deepcopy((before, after))
        with self.assertRaises(ValueError): audit.compare(before, after)
        result = audit.compare(before, after, allow_selection_change=True)
        self.assertEqual(result['comparedURLCount'], 2)
        self.assertEqual(result['addedURLs'], [added['url']])
        self.assertEqual(result['removedURLs'], [removed['url']])
        self.assertEqual(result['newGooglePass'], [])
        self.assertEqual(result['noLongerGooglePass'], [after['urls'][0]['url']])
        self.assertEqual(result['newBingCrawlRecords'], [])
        self.assertEqual((before, after), frozen)
        after['comparison'] = result
        text = audit.format_report(after)
        self.assertIn('공통 URL 비교 2 · 신규 기준선 1 · 대상 제외 1', text)

    def test_selection_migration_rejects_duplicates_foreign_property_and_disjoint_urls(self):
        before = self.report()
        for mutation in ('duplicate', 'property', 'foreign-url', 'empty', 'disjoint', 'schema'):
            after = deepcopy(before)
            if mutation == 'duplicate': after['urls'].append(deepcopy(after['urls'][0]))
            if mutation == 'property': after['site'] = 'https://outside.example/'
            if mutation == 'foreign-url': after['urls'][0]['url'] = 'https://outside.example/'
            if mutation == 'empty': after['urls'] = []
            if mutation == 'disjoint': after['urls'] = [{'url': audit.SITE + 'en/archive/'}]
            if mutation == 'schema': after['schemaVersion'] = 99
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                audit.compare(before, after, allow_selection_change=True)

    def test_selection_migration_retains_unknown_state_semantics(self):
        before = self.report(); after = deepcopy(before)
        after['urls'].pop()
        after['urls'][0]['inspection'] = {'httpStatus': 200, 'indexStatus': {}}
        result = audit.compare(before, after, allow_selection_change=True)
        self.assertEqual(result['googleUncomparable'], [after['urls'][0]['url']])
        self.assertEqual(result['noLongerGooglePass'], [])

    def test_invalid_selection_is_rejected_before_credentials_or_quota(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder)/'before.json'; snapshot.write_text(json.dumps(self.report()))
            selected = audit.targets()
            for extra in ([], ['--allow-selection-change']):
                previous = self.report()
                if extra: previous['urls'].append(deepcopy(previous['urls'][0]))
                snapshot.write_text(json.dumps(previous))
                with patch('sys.argv', ['search_engines.py', '--live', '--previous', str(snapshot), '--output', str(Path(folder)/'new.json'), *extra]), patch.object(audit, 'access_token') as auth, patch.object(audit, 'collect') as collect, patch.object(audit.Path, 'read_text', autospec=True, side_effect=lambda p: snapshot.read_bytes().decode() if p == snapshot else self.fail('Credentials must not be read')), patch.object(audit, 'targets', return_value=selected), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(audit.main(), 1)
                    auth.assert_not_called(); collect.assert_not_called()

    def test_selection_change_flag_requires_live_previous(self):
        for args in [[], ['--live'], ['--previous', 'missing.json'], ['--live', '--previous', 'missing.json', '--retry-bing', 'missing.json']]:
            with patch('sys.argv', ['search_engines.py', '--allow-selection-change', *args]), patch.object(audit, 'access_token') as auth, patch.object(audit, 'collect') as collect, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(), 1)
                auth.assert_not_called(); collect.assert_not_called()

    def test_live_cli_migrates_selection_without_counting_added_pass_as_a_gain(self):
        before = self.report(); after = deepcopy(before)
        added = deepcopy(after['urls'][0])
        added.update({'url': audit.SITE + 'en/archive/', 'kind': 'archive', 'group': 'archive'})
        after['urls'].append(added)
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder)/'before.json'; output = Path(folder)/'after.json'
            snapshot.write_text(json.dumps(before))
            selected = [{k: r[k] for k in ('url', 'language', 'kind', 'group', 'key', 'expectedCanonical')} for r in after['urls']]
            def read(path):
                if path == snapshot: return snapshot.read_bytes().decode()
                if path == audit.CONFIG/'bing-api-key.txt': return 'PRIVATE KEY'
                self.fail('Unexpected file read')
            with patch('sys.argv', ['search_engines.py', '--live', '--previous', str(snapshot), '--allow-selection-change', '--output', str(output)]), patch.object(audit, 'targets', return_value=selected), patch.object(audit.Path, 'read_text', autospec=True, side_effect=read), patch.object(audit, 'access_token', return_value='PRIVATE TOKEN'), patch.object(audit, 'collect', return_value=after) as collect, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(), 0)
                self.assertEqual(collect.call_args.args[2], selected)
            saved = json.loads(output.read_text())
            self.assertEqual(saved['comparison']['comparedURLCount'], 3)
            self.assertEqual(saved['comparison']['addedURLs'], [added['url']])
            self.assertEqual(saved['comparison']['newGooglePass'], [])
            self.assertEqual(snapshot.read_text(), json.dumps(before))

    def test_retry_only_reads_failed_bing_urls_and_preserves_original_observations(self):
        original = self.report()
        original['urls'][0]['bing'] = {'httpStatus': 400, 'error': 'Bing API request failed'}
        frozen = deepcopy(original); calls = []
        def bing(key, method, params):
            calls.append((method, params))
            return {'httpStatus': 200, 'data': {'Url': params['url'], 'LastCrawledDate': '/Date(1609459200000)/'}}
        with patch.object(audit, 'access_token') as auth, patch.object(audit.growth, 'collect') as google:
            result = audit.retry_bing(original, 'PRIVATE', datetime(2026, 10, 28, tzinfo=timezone.utc), bing, lambda _: None)
            auth.assert_not_called(); google.assert_not_called()
        self.assertEqual(original, frozen)
        self.assertEqual(calls, [('GetUrlInfo', {'siteUrl': audit.SITE, 'url': original['urls'][0]['url']})])
        self.assertEqual(result['bingRetriedURLCount'], 1)
        self.assertEqual(result['urls'][0]['bingPrevious'], original['urls'][0]['bing'])
        self.assertEqual(result['performance'], original['performance'])
        self.assertEqual(result['checkedAt'], original['checkedAt'])
        self.assertEqual(result['urls'][1:], original['urls'][1:])
        self.assertEqual(result['summary']['en']['bingCrawlRecords'], 1)
        with self.assertRaises(ValueError): audit.retry_bing(result, 'PRIVATE', datetime.now(timezone.utc), bing)

    def test_live_collection_stops_bing_after_throttling_and_marks_unrequested_urls(self):
        calls = []
        def bing(key, method, params):
            calls.append(params['url'])
            return {'httpStatus': 400, 'error': 'Bing API request failed', 'apiErrorCode': 5}
        result = self.report(bing)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['urls'][0]['bing']['httpStatus'], 400)
        for row in result['urls'][1:]:
            self.assertTrue(row['bing']['notRequested'])
            self.assertNotIn('httpStatus', row['bing'])
            self.assertIsNotNone(audit.google_state(row))
        self.assertEqual(sum(s['bingDeferred'] for s in result['summary'].values()), 2)

    def test_bing_throttle_stops_the_retry_batch_without_touching_remaining_observations(self):
        original = self.report()
        for row in original['urls']: row['bing'] = {'httpStatus': 400, 'error': 'Earlier read failed'}
        calls = []
        def bing(key, method, params):
            calls.append(params['url'])
            return {'httpStatus': 400, 'error': 'Bing API request failed', 'apiErrorCode': 5}
        result = audit.retry_bing(original, 'PRIVATE', datetime.now(timezone.utc), bing, lambda _: self.fail('Do not sleep or continue after throttling'))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['bingRetriedURLCount'], 1)
        self.assertEqual(result['bingRetryDeferredURLCount'], 2)
        self.assertEqual(result['urls'][1:], original['urls'][1:])
        self.assertEqual(result['urls'][0]['bing']['apiErrorCode'], 5)

    def test_retry_rejects_urls_outside_the_public_selection_without_requests(self):
        report = self.report(); report['urls'][0]['url'] = 'https://outside.example/'
        report['urls'][0]['bing'] = {'httpStatus': 403, 'error': 'Denied'}
        with patch.object(audit, 'bing_get') as bing:
            with self.assertRaises(ValueError): audit.retry_bing(report, 'PRIVATE', datetime.now(timezone.utc), bing)
            bing.assert_not_called()

    def test_offline_report_omits_private_queries_and_does_not_invent_zero_exposure(self):
        report = self.report()
        report['performance']['current']['queries'] = {'rows': [{'keys': ['PRIVATE QUERY']}]}
        value = audit.format_report(report)
        self.assertNotIn('PRIVATE QUERY', value)
        self.assertIn('실적 미제공', value)
        self.assertIn('빈 실적은 노출 0의 증거가 아닙니다', value)
        self.assertIn('색인 확정: 불가', value)
        report['urls'][0]['bing'] = {'httpStatus': 403, 'error': 'Denied'}
        self.assertIn('Bing 크롤링: 조회 실패', audit.format_report(report))
        self.assertEqual(audit.summarize(report)['en']['bingErrors'], 1)

    def test_preview_and_report_do_not_authenticate_fetch_or_write(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder)/'sample.json'; snapshot.write_text(json.dumps(self.report()))
            for args in [[], ['--report', str(snapshot)]]:
                with patch('sys.argv', ['search_engines.py', *args]), patch.object(audit, 'access_token') as auth, patch.object(audit, 'collect') as collect, patch.object(audit, 'save_new') as save, contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(audit.main(), 0)
                    auth.assert_not_called(); collect.assert_not_called(); save.assert_not_called()

    def test_destination_is_checked_before_credentials_or_quota_and_snapshots_are_exclusive(self):
        with patch('sys.argv', ['search_engines.py', '--live', '--output', str(audit.ROOT/'bad-output.json')]), patch.object(audit, 'access_token') as auth, patch.object(audit, 'collect') as collect, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(audit.main(), 1)
            auth.assert_not_called(); collect.assert_not_called()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'private.json'; audit.save_new(output, {'test': True})
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            with self.assertRaises(ValueError): audit.save_new(output, {'replacement': True})
            self.assertEqual(json.loads(output.read_text()), {'test': True})


if __name__ == '__main__': unittest.main()
