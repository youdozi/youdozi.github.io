import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import measurement_audit as audit


def rules():
    return {'schemaVersion': 1, 'property': audit.PROPERTY, 'timeZone': 'Asia/Seoul', 'rules': [
        {'id': 'reviewed-overlap', 'classification': 'suspected', 'reason': 'Minute/path overlap, operator unknown', 'sourceMedium': 'bing / organic', 'minutes': ['202610252241'], 'paths': ['/en/digest/example/']}]}


def ga(value, metric='eventCount'):
    return {'httpStatus': 200, 'data': {'metricHeaders': [{'name': metric}], 'rows': [{'metricValues': [{'value': str(value)}]}]}}


class MeasurementAuditTests(unittest.TestCase):
    def request_plan(self, value=None):
        return audit.plan('2026-10-24', '2026-10-26', '2026-10-25', '2026-10-26', 'Asia/Seoul', value or rules())

    def report(self):
        requests = self.request_plan()
        responses = iter([ga(1, 'sessions')] * 5 + [ga(x) for x in [100, 10, 90, 20, 70]])
        return audit.collect(requests, rules(), lambda body: next(responses), lambda body: {'httpStatus': 200, 'data': {'rows': [{'clicks': 1, 'impressions': 12}]}}, lambda method, params: {'httpStatus': 200, 'data': [{'Url': audit.SITE}]} if method == 'GetUserSites' else {'httpStatus': 200, 'data': []})

    def test_pt_window_maps_to_exact_korean_hours(self):
        window = audit.aligned_window('2026-10-24', '2026-10-26', 'Asia/Seoul')
        self.assertEqual(window['gaStart'], '2026-10-24T16:00:00+09:00')
        self.assertEqual(window['gaEndExclusive'], '2026-10-27T16:00:00+09:00')
        self.assertEqual(len(window['gaHours']), 72)
        self.assertEqual(window['gaHours'][0], '2026102416')
        self.assertEqual(window['gaHours'][-1], '2026102715')

    def test_dst_window_does_not_assume_every_day_has_twenty_four_hours(self):
        self.assertEqual(len(audit.aligned_window('2026-11-01', '2026-11-01', 'Asia/Seoul')['gaHours']), 25)
        self.assertEqual(len(audit.aligned_window('2026-03-08', '2026-03-08', 'Asia/Seoul')['gaHours']), 23)
        with self.assertRaises(ValueError):
            audit.aligned_window('2026-10-26', '2026-10-26', 'Asia/Kolkata')
        for first, last in [('2026-10-26', '2026-10-25'), ('2026-10-01', '2026-10-20')]:
            with self.assertRaises(ValueError):
                audit.span(first, last)

    def test_rules_cannot_claim_confirmed_identity_or_exclude_entire_countries(self):
        for change in ({'classification': 'confirmed'}, {'reason': ''}, {'minutes': ['202602301200']}, {'paths': ['/en/example/?token=secret']}, {'paths': ['/en/../private']}, {'sourceMedium': 'all'}):
            value = rules();value['rules'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                audit.validate_rules(value, 'Asia/Seoul')
        value = rules();value['rules'] *= 2
        with self.assertRaises(ValueError):
            audit.validate_rules(value, 'Asia/Seoul')

    def test_request_plan_separates_page_view_events_without_subtracting_users(self):
        requests = self.request_plan()
        segment = {k: v for k, v in requests['ga'].items() if k.startswith('segment:')}
        for body in segment.values():
            self.assertEqual(body['metrics'], [{'name': 'eventCount'}])
            self.assertIn('page_view', json.dumps(body['dimensionFilter']))
        self.assertIn('notExpression', json.dumps(segment['segment:remainderSensitivityPageViews']))
        self.assertIn('dateHourMinute', json.dumps(segment['segment:suspectedRulePageViews']))
        self.assertIn('dateHour', json.dumps(requests['ga']['aligned:google']))
        self.assertTrue(all(body['dataState'] == 'final' and body['type'] == 'web' for body in requests['gsc'].values()))

    def test_original_data_and_unknown_bing_are_preserved_with_arithmetic_checks(self):
        report = self.report();before = deepcopy(report)
        summary = audit.summarize(report)
        self.assertEqual(report, before)
        self.assertEqual(summary['pageViewScenarios']['rawPageViews'], 100)
        self.assertTrue(all(summary['partitionChecks'].values()))
        self.assertEqual(summary['bingPerformanceState'], 'unknown-or-unavailable')
        self.assertIn('not a verified human audience', summary['warning'])
        report['ga']['segment:remainderSensitivityPageViews'] = ga(69)
        self.assertFalse(audit.summarize(report)['partitionChecks']['nonReviewEqualsSuspectedPlusRemainder'])

    def test_failed_or_empty_responses_are_unknown_not_zero(self):
        report = self.report()
        report['ga']['segment:rawPageViews'] = {'httpStatus': 403, 'error': 'Denied'}
        report['ga']['segment:reviewPageViews'] = {'httpStatus': 200, 'data': {'rowCount': 0}}
        report['gsc']['totals'] = {'httpStatus': 200, 'data': {}}
        summary = audit.summarize(report)
        self.assertIsNone(summary['pageViewScenarios']['rawPageViews'])
        self.assertIsNone(summary['pageViewScenarios']['reviewPageViews'])
        self.assertIsNone(summary['googleClicksAndImpressions'])
        self.assertIsNone(summary['partitionChecks']['rawEqualsReviewPlusNonReview'])

    def test_network_exceptions_do_not_serialize_credentials_and_registered_bing_url_is_used(self):
        requests = self.request_plan();called = []
        def broken(body):
            raise RuntimeError('SECRET_TOKEN https://example/?apikey=PRIVATE_KEY')
        def bing(method, params):
            called.append((method, params))
            return {'httpStatus': 200, 'data': [{'Url': audit.SITE.rstrip('/')}]} if method == 'GetUserSites' else {'httpStatus': 200, 'data': []}
        report = audit.collect(requests, rules(), broken, broken, bing)
        encoded = json.dumps(report)
        self.assertNotIn('SECRET_TOKEN', encoded);self.assertNotIn('PRIVATE_KEY', encoded)
        self.assertTrue(report['apiErrors'])
        self.assertEqual(called[-1][1], {'siteUrl': audit.SITE.rstrip('/')})

    def test_preview_does_not_read_credentials_call_apis_or_write_output(self):
        with patch('sys.argv', ['audit', '--start', '2026-10-24', '--end', '2026-10-26']), patch.object(audit, 'ga_session') as auth, patch.object(audit, 'access_token') as gsc, patch.object(audit, 'save_new') as save, contextlib.redirect_stdout(io.StringIO()):
            audit.main();auth.assert_not_called();gsc.assert_not_called();save.assert_not_called()

    def test_output_inside_repository_is_rejected_before_authentication(self):
        with patch('sys.argv', ['audit', '--live', '--start', '2026-10-24', '--end', '2026-10-26', '--output', str(Path.cwd() / 'private-bad.json')]), patch.object(audit, 'ga_session') as auth, self.assertRaises(ValueError):
            audit.main()
        auth.assert_not_called()

    def test_saved_report_is_offline_and_does_not_requery(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.json';path.write_text(json.dumps(self.report()))
            with patch('sys.argv', ['audit', '--report', str(path)]), patch.object(audit, 'ga_session') as auth, patch.object(audit, 'collect') as collect, contextlib.redirect_stdout(io.StringIO()) as output:
                audit.main();auth.assert_not_called();collect.assert_not_called()
            self.assertIn('GSC', output.getvalue())
