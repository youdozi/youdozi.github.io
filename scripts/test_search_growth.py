import json
from datetime import datetime, timezone
from pathlib import Path
import unittest
from copy import deepcopy
import contextlib
import io
import tempfile
from unittest.mock import patch

import search_growth as growth


class SearchGrowthTests(unittest.TestCase):
    def test_missing_verdict_is_not_an_indexing_loss_or_gain(self):
        before = {'site': growth.SITE, 'checkedAt': 'before', 'windows': {'current': ['a', 'b']},
                  'urls': [{'url': growth.SITE + 'one/', 'kind': 'article', 'live': {},
                            'inspection': {'httpStatus': 200, 'indexStatus': {'verdict': 'PASS'}}}]}
        for state in ({}, None, {'verdict': 'VERDICT_UNSPECIFIED'}):
            after = deepcopy(before)
            after['urls'][0]['inspection']['indexStatus'] = state
            result = growth.compare(before, after)
            self.assertEqual(result['noLongerPass'], [])
            self.assertEqual(result['uncomparableUrls'], [growth.SITE + 'one/'])
            self.assertEqual(growth.summarize(after)['article']['googleUnknownOrError'], 1)
        after['urls'][0]['inspection']['indexStatus'] = {'verdict': 'NEUTRAL'}
        self.assertEqual(growth.compare(before, after)['noLongerPass'], [growth.SITE + 'one/'])

    def test_missing_canonical_and_duplicate_urls_cannot_be_reported_as_changes(self):
        before = {'site': growth.SITE, 'checkedAt': 'before', 'windows': {'current': ['a', 'b']},
                  'urls': [{'url': growth.SITE + 'one/', 'inspection': {'httpStatus': 200, 'indexStatus': {'verdict': 'NEUTRAL'}}}]}
        after = deepcopy(before)
        after['urls'][0]['inspection']['indexStatus'] = {'verdict': 'PASS', 'googleCanonical': growth.SITE + 'one/'}
        result = growth.compare(before, after)
        self.assertEqual(result['newPass'], [growth.SITE + 'one/'])
        self.assertEqual(result['canonicalChanges'], [])
        self.assertEqual(result['canonicalUncomparableUrls'], [growth.SITE + 'one/'])
        before['urls'][0]['inspection']['indexStatus']['googleCanonical'] = growth.SITE + 'old/'
        self.assertEqual(len(growth.compare(before, after)['canonicalChanges']), 1)
        after['urls'].append(deepcopy(after['urls'][0]))
        with self.assertRaises(ValueError): growth.compare(before, after)

    def test_unsafe_output_is_rejected_before_google_authentication(self):
        with patch('sys.argv', ['search_growth.py', '--live', '--output', str(growth.ROOT / 'private.json')]), patch.object(growth, 'access_token') as auth:
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(growth.main(), 1)
            auth.assert_not_called()

    def test_report_cli_does_not_authenticate_collect_or_write(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'snapshot.json'
            snapshot.write_text('{}')
            with patch('sys.argv', ['search_growth.py', '--report', str(snapshot)]), patch.object(growth, 'format_report', return_value='Offline report'), patch.object(growth, 'access_token') as auth, patch.object(growth, 'collect') as collect:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(growth.main(), 0)
                self.assertEqual(output.getvalue().strip(), 'Offline report')
                auth.assert_not_called(); collect.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [snapshot])
            with patch('sys.argv', ['search_growth.py', '--report', str(snapshot), '--live']), patch.object(growth, 'access_token') as auth:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(growth.main(), 1)
                auth.assert_not_called()

    def test_text_report_keeps_query_data_private_and_does_not_invent_zeroes(self):
        report = {'site': growth.SITE, 'checkedAt': '2026-10-27T00:00:00Z',
                  'urls': [{'url': growth.SITE + 'en/posts/example/', 'kind': 'article', 'live': {'matchesExpectedStaticRoute': True},
                            'inspection': {'httpStatus': 403}}],
                  'windows': {'current': ['start', 'end'], 'previous': ['older', 'earlier']},
                  'performance': {p: {'totals': {'httpStatus': 200, 'data': {}},
                                     'queries': {'rows': [{'keys': ['private query']}]}} for p in ['current', 'previous']}}
        text = growth.format_report(report)
        self.assertIn('조회 실패·비교 불가', text)
        self.assertIn('합계 미제공 또는 조회 실패', text)
        self.assertNotIn('private query', text)
        self.assertNotIn('클릭 0', text)
        report['site'] = 'https://other.example/'
        with self.assertRaises(ValueError): growth.format_report(report)

    def test_comparison_never_treats_an_api_error_as_loss_of_indexing(self):
        previous = {'site': growth.SITE, 'checkedAt': 'before', 'windows': {'current': ['a', 'b']},
                    'urls': [{'url': growth.SITE + 'one/', 'inspection': {'httpStatus': 200, 'indexStatus': {'verdict': 'PASS'}}},
                             {'url': growth.SITE + 'two/', 'inspection': {'httpStatus': 200, 'indexStatus': {'verdict': 'NEUTRAL'}}}]}
        current = deepcopy(previous)
        current['urls'][0]['inspection'] = {'httpStatus': 403}
        current['urls'][1]['inspection']['indexStatus'] = {'verdict': 'PASS', 'googleCanonical': growth.SITE + 'two/'}
        result = growth.compare(previous, current)
        self.assertEqual(result['noLongerPass'], [])
        self.assertEqual(result['newPass'], [growth.SITE + 'two/'])
        self.assertEqual(result['uncomparableUrls'], [growth.SITE + 'one/'])
        current['urls'].pop()
        with self.assertRaises(ValueError):
            growth.compare(previous, current)

    def test_targets_keep_twenty_articles_and_ten_distinct_legacy_routes(self):
        registry = json.loads(growth.REGISTRY.read_text())
        items = growth.targets(registry)
        self.assertEqual(sum(t['kind'] == 'article' for t in items), 20)
        self.assertEqual(sum(t['kind'] == 'legacy' for t in items), 10)
        for t in items:
            self.assertTrue(t['url'].startswith(growth.SITE))
            if t['kind'] == 'legacy':
                self.assertIn('/ko/posts/', t['expectedCanonical'])
        registry['articles'][1] = registry['articles'][0]
        with self.assertRaises(ValueError):
            growth.targets(registry)
        registry['articles'][0]['legacyPath'] = '//outside.example/test/'
        with self.assertRaises(ValueError):
            growth.targets(registry)

    def test_windows_use_pt_calendar_days_and_adjacent_nonoverlapping_periods(self):
        # UTC March 10 is still March 9 in Pacific time, after the DST change.
        result = growth.windows(datetime(2026, 3, 10, 1, tzinfo=timezone.utc))
        self.assertEqual(result, {'current': ('2026-02-07', '2026-03-06'),
                                  'previous': ('2026-01-10', '2026-02-06')})

    def test_collection_separates_live_redirects_index_state_errors_and_missing_rows(self):
        selected = growth.targets(json.loads(growth.REGISTRY.read_text()))[:3]
        requests = []

        def post(token, url, payload):
            requests.append((url, payload))
            if url.endswith('index:inspect'):
                if payload['inspectionUrl'] == selected[1]['url']:
                    return {'httpStatus': 403, 'error': 'Denied'}
                status = {'verdict': 'PASS', 'googleCanonical': selected[2]['expectedCanonical']}
                return {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': status}}}
            return {'httpStatus': 200, 'data': {'rows': []}}

        def get(url, **kwargs):
            self.assertFalse(kwargs['allow_redirects'])
            target = next(t for t in selected if t['url'] == url)
            legacy = target['kind'] == 'legacy'
            canonical = target['expectedCanonical']
            redirect = f'<meta http-equiv="refresh" content="0;url={canonical.removeprefix(growth.SITE.rstrip("/"))}">' if legacy else ''
            class Response:
                status_code = 200
                headers = {}
                text = f'<link rel="canonical" href="{canonical}">{redirect}'
            return Response()

        report = growth.collect('private-test-token', selected, datetime(2026, 10, 27, tzinfo=timezone.utc), post, get)
        self.assertEqual(len(requests), 8)  # Five analytics reads and three index reads.
        for url, payload in requests:
            if 'searchAnalytics' in url:
                self.assertEqual(payload['dataState'], 'final')
        self.assertEqual(report['summary']['article']['inspectionResponses'], 1)
        self.assertEqual(report['summary']['article']['googlePass'], 1)
        self.assertEqual(report['summary']['legacy']['liveMatches'], 1)
        self.assertFalse(report['urls'][2]['live']['serverRedirect'])
        self.assertEqual(report['performance']['current']['pages']['rows'], [])
        self.assertIn('omitted rows are not zero', report['searchAnalyticsBasis'])
        self.assertNotIn('private-test-token', json.dumps(report))


if __name__ == '__main__':
    unittest.main()
