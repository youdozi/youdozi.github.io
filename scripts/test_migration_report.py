import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import migration_report as migration
import search_growth as growth


def snapshot():
    selected = growth.targets(json.loads(growth.REGISTRY.read_text()))
    return {'site': growth.SITE, 'checkedAt': '2026-10-29T08:00:00Z',
            'windows': {'current': ['2026-09-28', '2026-10-25'], 'previous': ['2026-08-31', '2026-09-27']},
            'urls': [{**r, 'inspection': {'httpStatus': 200, 'indexStatus': {'verdict': 'NEUTRAL'}}} for r in selected],
            'performance': {period: {'pages': {'httpStatus': 200, 'rows': []},
                                     'queries': {'rows': [{'keys': ['SECRET QUERY']}]}} for period in ('current', 'previous')}}


class MigrationReportTests(unittest.TestCase):
    def test_topics_preserve_three_urls_and_do_not_invent_missing_metrics(self):
        source = snapshot(); original = deepcopy(source)
        result = migration.build_report(source, '2026-10-29T09:00:00Z')
        self.assertEqual(len(result['topics']), 10)
        self.assertEqual(result['snapshotVsDeployment'], 'before-deployment')
        self.assertEqual(source, original)
        for topic in result['topics']:
            self.assertEqual(set(topic['editions']), {'en', 'ko', 'legacy'})
            self.assertEqual(topic['editions']['en']['performance']['current']['clicks'], None)
            self.assertEqual(topic['editions']['en']['crawlVsDeployment'], 'unavailable')
        text = migration.format_report(result)
        self.assertNotIn('SECRET QUERY', text)
        self.assertNotIn('클릭 0', text)

    def test_index_and_canonical_selection_and_crawl_time_are_separate(self):
        source = snapshot()
        en, ko, legacy = source['urls'][:3]
        ko['inspection']['indexStatus'] = {'verdict': 'PASS', 'googleCanonical': ko['url'], 'lastCrawlTime': '2026-10-29T06:00:00Z'}
        legacy['inspection']['indexStatus'] = {'verdict': 'PASS', 'googleCanonical': legacy['url'], 'lastCrawlTime': '2026-10-28T06:00:00Z'}
        result = migration.build_report(source, '2026-10-29T05:00:00Z')
        topic = result['topics'][0]
        self.assertEqual(topic['observation'], 'new-indexed-legacy-still-selected')
        self.assertEqual(topic['editions']['ko']['crawlVsDeployment'], 'on-or-after-deployment')
        self.assertEqual(topic['editions']['legacy']['crawlVsDeployment'], 'before-deployment')
        legacy['inspection']['indexStatus']['googleCanonical'] = ko['url']
        self.assertEqual(migration.build_report(source)['topics'][0]['observation'], 'destination-selected-on-both')

    def test_missing_verdict_and_errors_are_unknown_while_explicit_zero_is_preserved(self):
        source = snapshot()
        source['urls'][0]['inspection'] = {'httpStatus': 200, 'indexStatus': {}}
        source['urls'][1]['inspection'] = {'httpStatus': 403}
        source['performance']['current']['pages']['rows'] = [{'keys': [source['urls'][2]['url']], 'clicks': 0, 'impressions': 4, 'position': 7}]
        result = migration.build_report(source)
        self.assertEqual(result['summary']['en']['unknownOrError'], 1)
        self.assertEqual(result['summary']['ko']['unknownOrError'], 1)
        self.assertEqual(result['topics'][0]['editions']['legacy']['performance']['current']['clicks'], 0)

    def test_wrong_property_mapping_duplicate_urls_and_naive_times_fail(self):
        source = snapshot()
        for mutate in (lambda r: r.update(site='https://other.example/'),
                       lambda r: r['urls'].append(deepcopy(r['urls'][0])),
                       lambda r: r['urls'][2].update(expectedCanonical=r['urls'][0]['url']),
                       lambda r: r.update(checkedAt='2026-10-29T08:00:00')):
            bad = deepcopy(source); mutate(bad)
            with self.assertRaises(ValueError): migration.build_report(bad)
        with self.assertRaises(ValueError): migration.build_report(source, '2026-10-29')

    def test_previous_snapshot_comparison_is_read_only_and_rejects_future_observation(self):
        source = snapshot(); before = deepcopy(source); before['checkedAt'] = '2026-10-28T08:00:00Z'
        before['urls'][0]['inspection']['indexStatus']['verdict'] = 'PASS'
        source['urls'][0]['inspection']['indexStatus'] = {}
        result = migration.build_report(source, previous=before)
        self.assertEqual(result['comparison']['noLongerPass'], [])
        self.assertEqual(len(result['comparison']['uncomparableUrls']), 1)
        before['checkedAt'] = '2026-10-30T08:00:00Z'
        with self.assertRaises(ValueError): migration.build_report(source, previous=before)

    def test_cli_never_authenticates_collects_or_writes_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'; path.write_text(json.dumps(snapshot()))
            with patch('sys.argv', ['migration_report.py', '--snapshot', str(path)]), patch.object(growth, 'access_token') as auth, patch.object(growth, 'collect') as collect:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(migration.main(), 0)
                auth.assert_not_called(); collect.assert_not_called()
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_explicit_output_is_private_exclusive_and_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'snapshot.json'; source.write_text(json.dumps(snapshot()))
            output = Path(directory) / 'report.json'
            argv = ['migration_report.py', '--snapshot', str(source), '--output', str(output)]
            with patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(migration.main(), 0)
            original = output.read_bytes()
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertNotIn('SECRET QUERY', output.read_text())
            with patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(migration.main(), 1)
            self.assertEqual(output.read_bytes(), original)
            with patch('sys.argv', argv[:-1] + [str(growth.ROOT / 'unsafe-report.json')]), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(migration.main(), 1)
            self.assertFalse((growth.ROOT / 'unsafe-report.json').exists())


if __name__ == '__main__':
    unittest.main()
