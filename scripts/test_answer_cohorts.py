import contextlib
import copy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import answer_observation as a


class CohortTests(unittest.TestCase):
    def test_default_identity_and_new_pair_remain_separate(self):
        original = json.loads(a.COHORT.read_text())
        self.assertEqual(a.load_cohort(), original)
        self.assertEqual(a.cohort_identity(a.load_cohort()), a.cohort_identity(original))
        new = a.load_cohort('checksum-guide-066')
        self.assertEqual(len(a.targets(original)), 10)
        self.assertEqual(len(a.targets(new)), 2)
        self.assertNotEqual(a.cohort_identity(original), a.cohort_identity(new))
        for invalid in ['../../outside', 'https://example.com', 'unknown']:
            with self.assertRaises(ValueError): a.load_cohort(invalid)

    def test_registry_rejects_escape_symlinks_wrong_identity_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); folder = root / 'content/seo'; folder.mkdir(parents=True)
            registry = json.loads(a.REGISTRY.read_text())
            for name in ['answer-pilot.json', 'answer-checksum.json']:
                (folder / name).write_bytes((a.ROOT / 'content/seo' / name).read_bytes())
            def write(value): (folder / a.REGISTRY.name).write_text(json.dumps(value))
            for change in ['escape', 'duplicate', 'default', 'size', 'identity']:
                data = copy.deepcopy(registry)
                if change == 'escape': data['cohorts'][0]['path'] = 'content/seo/../../secret.json'
                if change == 'duplicate': data['cohorts'].append(data['cohorts'][0])
                if change == 'default': data['default'] = 'unregistered'
                if change == 'size': data['cohorts'][0]['topics'] = 4
                if change == 'identity': data['cohorts'][0]['path'] = 'content/seo/answer-checksum.json'
                write(data)
                with self.assertRaises(ValueError): a.load_cohort(root=root)
            write(registry)
            path = folder / 'answer-pilot.json'; path.unlink(); path.symlink_to(a.COHORT)
            with self.assertRaises(ValueError): a.load_cohort(root=root)

    def test_source_records_reject_unpublished_nonpost_and_escaped_sources(self):
        cohort = a.load_cohort('checksum-guide-066')
        records = a.source_records(cohort)
        self.assertEqual(len(records), 2)
        self.assertTrue(all(len(row['sha256']) == 64 and row['publishedAt'] for row in records.values()))
        key = cohort['articles'][0]['key']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for lang in ['en', 'ko']:
                p = root / f'src/content/posts/{lang}/{key}.md'; p.parent.mkdir(parents=True)
                p.write_bytes((a.ROOT / p.relative_to(root)).read_bytes())
            path = root / f'src/content/posts/en/{key}.md'; original = path.read_text()
            for text in [original.replace('kind: "post"', 'kind: "digest"'), original.replace('publishedAt: "2026-', 'publishedAt: "2999-')]:
                path.write_text(text)
                with self.assertRaises(ValueError): a.source_records(cohort, root)
            path.unlink(); path.symlink_to(a.ROOT / f'src/content/posts/en/{key}.md')
            with self.assertRaises(ValueError): a.source_records(cohort, root)

    def test_index_only_collects_two_inspections_and_no_performance_fields(self):
        calls = []
        def inspect(body):
            calls.append(body)
            return {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'NEUTRAL'}}}}
        report = a.collect_index(a.load_cohort('checksum-guide-066'), inspect, datetime.now(timezone.utc))
        self.assertEqual(len(calls), 2)
        self.assertEqual(report['mode'], 'index-only')
        self.assertNotIn('dates', report); self.assertNotIn('gscWeb', report); self.assertNotIn('ga4Attribution', report)
        self.assertEqual(a.summary(report)['googleIndex']['nonPassVerdict'], 2)
        self.assertEqual(a.summary(report)['ga4'], 'not-collected')
        with self.assertRaises(ValueError): a.comparison(report, report)

    def test_index_summary_distinguishes_errors_unknowns_and_nonpass(self):
        cohort = a.load_cohort()
        report = a.collect_index(cohort, lambda _: {'httpStatus': 200, 'data': {}}, datetime.now(timezone.utc))
        report['inspections'][0]['response'] = {'httpStatus': 403, 'error': 'denied'}
        report['inspections'][1]['response'] = {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}}
        report['inspections'][2]['response'] = {'httpStatus': 200, 'data': {'inspectionResult': {'indexStatusResult': {'verdict': 'FAIL'}}}}
        report['inspections'].pop()
        self.assertEqual(a.summary(report)['googleIndex'], {'pass': 1, 'nonPassVerdict': 1, 'apiError': 1, 'missingVerdict': 6, 'notObserved': 1})

    def test_plan_and_invalid_combinations_never_authenticate(self):
        for extra, status in [(['--index-only'], 0), (['--cohort', 'checksum-guide-066','--index-only'], 0),
                              (['--cohort','unknown','--live'], 1), (['--index-only','--start','2020-01-01'], 1),
                              (['--index-only','--live','--output',str(a.ROOT/'private.json')], 1)]:
            with patch('sys.argv',['answer_observation.py', *extra]), patch.object(a,'access_token') as auth, patch.object(a,'ga_session') as ga:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(a.main(), status)
                auth.assert_not_called(); ga.assert_not_called()

    def test_live_index_does_not_initialize_ga_or_call_search_analytics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            args = ['answer_observation.py','--cohort','checksum-guide-066','--index-only','--live','--output',str(path)]
            def inspect(token, endpoint, payload):
                self.assertTrue(endpoint.endswith('/urlInspection/index:inspect'))
                return {'httpStatus': 200,'data': {'inspectionResult': {'indexStatusResult': {'verdict':'NEUTRAL'}}}}
            with patch('sys.argv',args), patch.object(a,'access_token',return_value='test-secret'), patch.object(a,'google_post',side_effect=inspect) as post, patch.object(a,'ga_session') as ga:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(a.main(),0)
                ga.assert_not_called(); self.assertEqual(post.call_count,2)
            raw = path.read_text(); self.assertNotIn('test-secret',raw)
            report = json.loads(raw); self.assertEqual(len(report['sourcePublications']),2)
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            with patch('sys.argv',['answer_observation.py','--report',str(path)]), patch.object(a,'access_token') as auth:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(a.main(),0)
                auth.assert_not_called()

    def test_full_summary_does_not_print_query_rows_or_merge_api_failures(self):
        empty = lambda _: {'httpStatus':200,'data':{}}
        report = a.collect(a.load_cohort(), a.period('2026-09-29','2026-10-26'),empty,empty,empty,datetime.now(timezone.utc))
        report['gscWeb']['queries']['rows']=[{'keys':['url','private search query']}]
        report['inspections'][0]['response']={'httpStatus':403,'error':'denied'}
        result = a.summary(report)
        self.assertNotIn('private search query',json.dumps(result))
        self.assertEqual(result['googleIndex']['apiError'],1)
        self.assertEqual(result['googleIndex']['missingVerdict'],9)
        self.assertNotIn('googleIndexOtherOrUnknown',result)
        self.assertEqual(result['observedAt'],report['observedAt'])

    def test_live_index_failure_is_saved_and_returns_nonzero_without_ga(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'failed.json'
            args=['answer_observation.py','--cohort','checksum-guide-066','--index-only','--live','--output',str(path)]
            with patch('sys.argv',args),patch.object(a,'access_token',return_value='test-secret'),patch.object(a,'google_post',return_value={'httpStatus':403,'error':'denied'}),patch.object(a,'ga_session') as ga:
                with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(a.main(),1)
                ga.assert_not_called()
            self.assertEqual(a.summary(json.loads(path.read_text()))['googleIndex']['apiError'],2)
            self.assertNotIn('test-secret',path.read_text())


class PublicationCoverageTests(unittest.TestCase):
    def test_published_inside_or_after_window_and_timezone_differences(self):
        url='https://example.org/en/posts/example/'
        report={'dates':{'start':'2026-10-30','end':'2026-11-26'},'sourcePublications':{url:'2026-10-30T03:00:00+00:00'}}
        self.assertEqual(a.publication_coverage(report,url,'America/Los_Angeles'),'declared-before-window')
        self.assertEqual(a.publication_coverage(report,url,'Asia/Seoul'),'partial-window')
        report['sourcePublications'][url]='2026-11-28T00:00:00+00:00'
        self.assertEqual(a.publication_coverage(report,url,'America/Los_Angeles'),'not-yet-published')
        report['sourcePublications'][url]='invalid'
        self.assertEqual(a.publication_coverage(report,url,'Asia/Seoul'),'not-recorded')
        self.assertEqual(a.publication_coverage(report,url,None),'not-recorded')

    def test_partial_or_missing_publication_record_does_not_generate_delta(self):
        url='https://example.org/en/posts/example/'
        def report(start,end,clicks):
            return {'schemaVersion':1,'cohortIdentity':'same','dates':{'start':start,'end':end},'targets':[{'url':url}],
                    'gscWeb':{'pages':{'state':'returned-data','completePagination':True,'rows':[{'keys':[url],'clicks':clicks,'impressions':10}]}}}
        before=report('2026-09-01','2026-09-28',1);after=report('2026-10-01','2026-10-28',2)
        self.assertIsNone(a.comparison(before,after)['pages'][0]['delta'])
        for declared, expected in [('2026-09-20T00:00:00Z',None),('2026-08-01T00:00:00Z',{'clicks':1,'impressions':0})]:
            before['sourcePublications']={url:declared};after['sourcePublications']={url:declared}
            row=a.comparison(before,after)['pages'][0]
            self.assertEqual(row['delta'],expected);self.assertFalse(row['routeAvailabilityVerified'])


if __name__ == '__main__': unittest.main()
