import json
from datetime import datetime, timezone
from pathlib import Path
import unittest
from copy import deepcopy

import search_growth as growth


class SearchGrowthTests(unittest.TestCase):
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
