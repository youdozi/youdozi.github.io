import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

import answer_observation as a

COHORT = json.loads((Path(__file__).parents[1] / 'content/seo/answer-pilot.json').read_text())


class AnswerObservationTests(unittest.TestCase):
    def test_targets_are_exact_paired_public_paths(self):
        rows = a.targets(COHORT)
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({r['url'] for r in rows}), 10)
        for invalid in ['../outside', 'https://example.com', '2023-09-08-path/../../bad']:
            cohort = copy.deepcopy(COHORT); cohort['articles'][0]['key'] = invalid
            with self.assertRaises(ValueError): a.targets(cohort)
        cohort = copy.deepcopy(COHORT); cohort['articles'][0] = cohort['articles'][1]
        with self.assertRaises(ValueError): a.targets(cohort)

    def test_sources_are_domain_labels_not_substring_or_citation_claims(self):
        for source in ['chatgpt.com', 'https://www.perplexity.ai/path', 'claude.ai']:
            self.assertTrue(a.ai_source(source))
        for source in ['evilchatgpt.com', 'chatgpt.com.example.org', '(direct)', 'google', None]:
            self.assertFalse(a.ai_source(source))

    def test_transport_errors_do_not_expose_credentials(self):
        def fail(_): raise RuntimeError('secret-token https://example.org?apikey=secret')
        result = a.safe(fail, {})
        self.assertNotIn('secret', json.dumps(result))
        self.assertIn('error', result)

    def test_pagination_marks_caps_and_preserves_threshold_metadata(self):
        calls = []
        def api(body):
            calls.append(body)
            return {'httpStatus': 200, 'data': {'rows': [{'x': body['startRow']}] * 2,
                'metadata': {'subjectToThresholding': True}, 'dimensionHeaders': [{'name': 'landingPage'}]}}
        result = a.paged(api, {}, 'startRow', 'rows', size=2, max_pages=2)
        self.assertEqual([c['startRow'] for c in calls], [0, 2])
        self.assertEqual(result['state'], 'row-cap-reached')
        self.assertFalse(result['completePagination'])
        self.assertEqual(len(result['pages']), 2)
        self.assertTrue(all(p['metadata']['subjectToThresholding'] for p in result['pages']))
        self.assertEqual(result['dimensionHeaders'][0]['name'], 'landingPage')

    def test_api_failures_and_empty_results_are_distinct(self):
        empty = a.paged(lambda _: {'httpStatus': 200, 'data': {}}, {}, 'startRow', 'rows')
        error = a.paged(lambda _: {'httpStatus': 403, 'error': 'denied'}, {}, 'startRow', 'rows')
        self.assertEqual(empty['state'], 'no-returned-rows')
        self.assertEqual(error['state'], 'error')
        self.assertNotIn('clicks', empty)
        self.assertNotIn('sessions', error)

    def test_collect_scopes_queries_and_labels_unknown_dedicated_reports(self):
        requests = []
        def gsc(body):
            requests.append(body)
            return {'httpStatus': 200, 'data': {}}
        inspections = []
        def inspect(body):
            inspections.append(body)
            return {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}}
        def ga(body):
            self.assertEqual(len(body['dimensionFilter']['filter']['inListFilter']['values']), 10)
            return {'httpStatus': 200, 'data': {
                'dimensionHeaders': [{'name': x} for x in ['landingPage','sessionSource','sessionMedium']],
                'metricHeaders': [{'name': x} for x in ['sessions','engagedSessions']],
                'metadata': {'timeZone': 'Asia/Seoul', 'subjectToThresholding': True},
                'rows': [{'dimensionValues': [{'value': '/en/posts/example/'}, {'value': 'perplexity.ai'}, {'value': 'referral'}],
                          'metricValues': [{'value': '2'}, {'value': '1'}]}]}}
        report = a.collect(COHORT, a.period('2026-09-29','2026-10-26'), gsc, inspect, ga, datetime.now(timezone.utc))
        self.assertEqual(len(inspections), 10)
        self.assertTrue(all(r['type']=='web' and r['dataState']=='final' for r in requests))
        self.assertTrue(all(r['dimensionFilterGroups'][0]['filters'][0]['expression'].startswith('^(?:') for r in requests))
        self.assertEqual(report['dedicatedAIReports']['bing']['state'], 'not-collected')
        self.assertEqual(report['dedicatedAIReports']['google']['state'], 'not-collected')
        self.assertEqual(len(report['aiDomainMatchedAttributionRows']), 1)
        self.assertEqual(a.summary(report)['ga4Timezone'], 'Asia/Seoul')

    def test_comparison_requires_equal_nonoverlapping_windows_and_same_cohort(self):
        def record(start,end): return {'schemaVersion':1,'cohortIdentity':'same','dates':{'start':start,'end':end}}
        before = record('2026-09-29','2026-10-26'); after = record('2026-10-30','2026-11-26')
        result = a.comparison(before, after)
        self.assertFalse(result['causalEffectEstablished'])
        self.assertFalse(result['dedicatedAIVisibilityMeasured'])
        for bad in [record('2026-10-26','2026-11-22'), record('2026-10-30','2026-11-25'), {**after,'cohortIdentity':'different'}]:
            with self.assertRaises(ValueError): a.comparison(before, bad)



class PublicationBoundaryTests(unittest.TestCase):
    def test_deployment_day_and_missing_rows_do_not_create_effects(self):
        def r(start,end): return {'schemaVersion':1,'cohortIdentity':'same','dates':{'start':start,'end':end},'targets':[{'url':'https://example.org/'}]}
        before=r('2026-09-29','2026-10-26');after=r('2026-10-30','2026-11-26')
        result=a.comparison(before,after,'2026-10-30T03:00:00+00:00')
        self.assertEqual(result['deploymentDayPT'],'2026-10-29')
        self.assertIsNone(result['pages'][0]['delta'])
        for timestamp in ['2026-10-30T20:00:00+00:00','2026-10-25T12:00:00+00:00','2026-10-29T00:00:00']:
            with self.assertRaises(ValueError):a.comparison(before,after,timestamp)

    def test_date_labels_alone_do_not_certify_a_publication_boundary(self):
        before={'schemaVersion':1,'cohortIdentity':'same','dates':{'start':'2026-09-29','end':'2026-10-26'}}
        after={**before,'dates':{'start':'2026-10-30','end':'2026-11-26'}}
        self.assertFalse(a.comparison(before,after)['publicationBoundaryVerified'])


class CommandBoundaryTests(unittest.TestCase):
    def test_unsafe_output_is_rejected_before_authentication(self):
        from unittest.mock import patch
        import contextlib, io
        with patch('sys.argv',['answer_observation.py','--live','--output',str(a.ROOT/'aeo-private.json')]), patch.object(a,'access_token') as auth:
            with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(a.main(),1)
            auth.assert_not_called()

    def test_plan_mode_does_not_authenticate_or_collect(self):
        from unittest.mock import patch
        import contextlib, io
        with patch('sys.argv',['answer_observation.py']), patch.object(a,'access_token') as auth, patch.object(a,'collect') as collect:
            with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(a.main(),0)
            auth.assert_not_called();collect.assert_not_called()

    def test_missing_attribution_rows_are_not_zero_sessions(self):
        self.assertIsNone(a.attribution_metrics({'ga4Attribution':{'state':'no-returned-rows','rows':[],'completePagination':True}},'https://example.org/en/posts/test/'))





class CompareCommandTests(unittest.TestCase):
    def test_real_cohort_id_passes_preflight_before_authentication(self):
        import tempfile, contextlib, io
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            baseline=Path(folder)/'baseline.json'
            baseline.write_text(json.dumps({'schemaVersion':1,'cohortId':COHORT['cohortId'],'cohortIdentity':a.cohort_identity(COHORT),'dates':{'start':'2020-08-01','end':'2020-08-28'}}))
            args=['answer_observation.py','--live','--output',str(Path(folder)/'after.json'),'--compare',str(baseline),'--changed-at','2020-09-01T12:00:00+00:00','--start','2020-09-02','--end','2020-09-29']
            with patch('sys.argv',args),patch.object(a,'access_token',side_effect=RuntimeError('test stops before real API')) as auth:
                with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(a.main(),1)
                auth.assert_called_once()





class PropertyTimezoneBoundaryTests(unittest.TestCase):
    def record(self,start,end,zone):
        return {'schemaVersion':1,'cohortIdentity':'same','dates':{'start':start,'end':end},'ga4Attribution':{'metadata':{'timeZone':zone}}}

    def test_pt_next_day_can_still_be_the_ga_deployment_day(self):
        before=self.record('2026-09-29','2026-10-26','Asia/Seoul')
        after=self.record('2026-10-30','2026-11-26','Asia/Seoul')
        with self.assertRaisesRegex(ValueError,'GA property day'):
            a.comparison(before,after,'2026-10-30T03:00:00+00:00')
        after=self.record('2026-10-31','2026-11-27','Asia/Seoul')
        result=a.comparison(before,after,'2026-10-30T03:00:00+00:00')
        self.assertTrue(result['publicationBoundaryVerified'])
        self.assertEqual(result['deploymentDayPT'],'2026-10-29')
        self.assertEqual(result['deploymentDayGA'],'2026-10-30')

    def test_missing_or_changed_ga_timezone_is_not_certified(self):
        before=self.record('2026-09-29','2026-10-26','Asia/Seoul')
        after=self.record('2026-10-31','2026-11-27','America/Los_Angeles')
        with self.assertRaisesRegex(ValueError,'timezone changed'):
            a.comparison(before,after,'2026-10-30T03:00:00+00:00')
        before.pop('ga4Attribution');after.pop('ga4Attribution')
        self.assertFalse(a.comparison(before,after,'2026-10-30T03:00:00+00:00')['publicationBoundaryVerified'])


if __name__ == '__main__': unittest.main()
