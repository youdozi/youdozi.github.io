import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from ci_artifact import find, read_proof
from ci_artifact import eligible_pr, valid_evidence, site_digest


class ArtifactTest(unittest.TestCase):
    def test_only_merged_same_repository_pr_can_supply_artifacts(self):
        pr = {'merged_at': 'now', 'merge_commit_sha': 'merged',
              'head': {'repo': {'full_name': 'owner/blog'}},
              'base': {'ref': 'main', 'repo': {'full_name': 'owner/blog'}}}
        self.assertTrue(eligible_pr(pr, 'owner/blog', 'merged'))
        for field, value in [('merged_at', None), ('merge_commit_sha', 'old')]:
            changed = copy.deepcopy(pr); changed[field] = value
            self.assertFalse(eligible_pr(changed, 'owner/blog', 'merged'))
        pr['head']['repo']['full_name'] = 'fork/blog'
        self.assertFalse(eligible_pr(pr, 'owner/blog', 'merged'))

    def test_tree_attempt_workflow_and_success_must_match(self):
        run = {'id': 123, 'run_attempt': 2, 'conclusion': 'success', 'event': 'pull_request',
               'path': '.github/workflows/site-quality-gates.yml',
               'repository': {'full_name': 'owner/blog'}, 'head_repository': {'full_name': 'owner/blog'}}
        proof = {'schema': 1, 'repository': 'owner/blog', 'run_id': 123, 'run_attempt': 2,
                 'tree': 'tree', 'site_digest': 'a' * 64}
        self.assertTrue(valid_evidence(proof, run, 'owner/blog', 'tree'))
        for field, value in [('tree', 'old'), ('run_attempt', 1), ('run_id', 124), ('schema', 0)]:
            changed = {**proof, field: value}
            self.assertFalse(valid_evidence(changed, run, 'owner/blog', 'tree'))
        for field, value in [('conclusion', 'failure'), ('event', 'workflow_dispatch'), ('path', 'other.yml'),
                             ('head_repository', {'full_name': 'fork/blog'})]:
            self.assertFalse(valid_evidence(proof, {**run, field: value}, 'owner/blog', 'tree'))

    def test_expired_or_unverifiable_archive_is_never_downloaded(self):
        with patch('ci_artifact.subprocess.run') as download:
            for artifact in [{'expired': True}, {'expired': False, 'digest': 'missing'},
                             {'digest': 'sha256:' + 'a' * 64, 'size_in_bytes': 2000000}]:
                self.assertIsNone(read_proof('owner/blog', artifact))
            download.assert_not_called()

    def test_missing_evidence_falls_back_instead_of_reusing_old_site(self):
        pr = {'merged_at': 'now', 'merge_commit_sha': 'merged',
              'head': {'sha': 'head', 'repo': {'full_name': 'owner/blog'}},
              'base': {'ref': 'main', 'repo': {'full_name': 'owner/blog'}}}
        run = {'id': 123, 'head_sha': 'head'}
        with patch('ci_artifact.api', side_effect=[[pr], {'workflow_runs': [run]},
                   {'artifacts': [{'name': 'site-build-output', 'expired': False}]}]):
            self.assertEqual(find('owner/blog', 'merged', 'tree'), {'reuse': 'false'})

    def test_file_names_hidden_files_and_bytes_are_bound_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'index.html').write_text('checked')
            first = site_digest(root)
            (root / '.nojekyll').write_text('')
            self.assertNotEqual(first, site_digest(root))
            second = site_digest(root)
            (root / 'index.html').write_text('tampered')
            self.assertNotEqual(second, site_digest(root))
            (root / 'link').symlink_to(root / 'index.html')
            with self.assertRaises(ValueError): site_digest(root)


if __name__ == '__main__':
    unittest.main()
