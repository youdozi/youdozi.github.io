import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch

import archive_renewal as archive

ROOT = Path(__file__).resolve().parents[1]


class ArchiveRenewalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = archive.read(ROOT/archive.DIRECTORY/'manifest.json')
        cls.batch = archive.read(ROOT/archive.DIRECTORY/'batches/pilot-001.json')

    def test_complete_inventory_preserves_examples_and_superseded_item(self):
        records = self.manifest['items']
        self.assertEqual(1125,len(records))
        self.assertEqual(4,sum(r['status']=='excluded_example' for r in records))
        hidden = [r for r in records if r['visibility']=='superseded']
        self.assertEqual(1,len(hidden))
        self.assertEqual('59c87ea544e0e5db',hidden[0]['id'])
        self.assertEqual([],archive.validate_manifest(self.manifest,ROOT))
        self.assertEqual(self.manifest,archive.sync_manifest(ROOT,self.manifest))

    def test_missing_records_and_changed_dates_cannot_silently_resync(self):
        value=copy.deepcopy(self.manifest)
        value['items'][0]['originalPagePublishedAt']='2000-01-01T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'provenance changed'):archive.sync_manifest(ROOT,value)
        value=copy.deepcopy(self.manifest);value['items'][0]['id']='removed-id'
        with self.assertRaisesRegex(ValueError,'disappeared'):archive.sync_manifest(ROOT,value)

    def test_old_sources_are_valid_without_inventing_english_publication(self):
        self.assertEqual([],archive.validate_batch(self.batch,self.manifest))
        for date in ('2026-06-21T00:00:00Z','2026-10-25T00:00:00Z'):
            value=copy.deepcopy(self.batch);value['entries'][0]['editionPublishedAt']['en']=date
            self.assertTrue(archive.validate_batch(value,self.manifest))

    def test_date_experiment_and_method_mutations_are_rejected(self):
        for key,value in [('archiveDate','2026-10-25'),('originalPagePublishedAt','2000-01-01T00:00:00Z'),('experimentStatus','tested')]:
            batch=copy.deepcopy(self.batch);batch['entries'][0][key]=value
            with self.subTest(key=key):self.assertTrue(archive.validate_batch(batch,self.manifest))
        batch=copy.deepcopy(self.batch);batch['reviewMethod']='ai-verified'
        self.assertTrue(archive.validate_batch(batch,self.manifest))
        self.assertTrue(archive.validate_batch(self.batch,self.manifest,now=datetime(2000,1,1,tzinfo=timezone.utc)))

    def test_fixtures_duplicates_and_language_drift_are_rejected(self):
        batch=copy.deepcopy(self.batch);batch['entries'].append(copy.deepcopy(batch['entries'][0]))
        self.assertTrue(archive.validate_batch(batch,self.manifest))
        batch=copy.deepcopy(self.batch);batch['entries'][0]['id']=next(r['id'] for r in self.manifest['items'] if r['visibility']=='example')
        self.assertTrue(archive.validate_batch(batch,self.manifest))
        batch=copy.deepcopy(self.batch);batch['entries'][0]['editions']['ko']['claims'][0]['text']+=' 999%'
        self.assertTrue(archive.validate_batch(batch,self.manifest))
        batch=copy.deepcopy(self.batch)
        batch['entries'][0]['editions']['ko']=copy.deepcopy(batch['entries'][0]['editions']['en'])
        self.assertTrue(archive.validate_batch(batch,self.manifest))

    def test_primary_evidence_and_quote_shapes_are_required(self):
        for failure in ('role','host','quote','id','hash','missing'):
            batch=copy.deepcopy(self.batch);e=batch['entries'][0]
            if failure=='role':e['documents'][1]['role']='reporting'
            if failure=='host':e['documents'][1]['url']='https://unknown.example/announcement'
            if failure=='quote':e['editions']['en']['claims'][0]['evidence'][0]['quote']='short'
            if failure=='id':e['editions']['en']['claims'][0]['evidence'][0]['document_id']=99
            if failure=='hash':e['documents'][1]['sha256']='bad'
            if failure=='missing':e['editions']['en']['claims'][0]['evidence']=[]
            with self.subTest(failure=failure):self.assertTrue(archive.validate_batch(batch,self.manifest))

    def test_exact_content_and_quote_check_detects_changes(self):
        batch=copy.deepcopy(self.batch)
        bodies={d['url']:[] for e in batch['entries'] for d in e['documents']}
        for e in batch['entries']:
            for edition in e['editions'].values():
                for claim in edition['claims']+edition['followUp']:
                    for q in claim['evidence']:bodies[e['documents'][q['document_id']]['url']].append(q['quote'])
        bodies={u:' '.join(quotes) for u,quotes in bodies.items()}
        for e in batch['entries']:
            for d in e['documents']:d['sha256']=hashlib.sha256(bodies[d['url']].encode()).hexdigest()
        self.assertEqual([],archive.validate_batch(batch,self.manifest,documents=bodies))
        claim=batch['entries'][0]['editions']['en']['claims'][0]
        claim['evidence'][0]['quote']='A sentence that is absent from the captured source.'
        self.assertIn('archive quote absent from source',archive.validate_batch(batch,self.manifest,documents=bodies))
        bodies[batch['entries'][0]['documents'][0]['url']]+=' changed'
        self.assertTrue(any('source content changed' in e for e in archive.validate_batch(batch,self.manifest,documents=bodies)))

    def test_unavailable_sources_cannot_contain_verified_claims(self):
        blocked=[e for e in self.batch['entries'] if e['outcome']=='unverifiable_proposal']
        self.assertEqual(2,len(blocked))
        batch=copy.deepcopy(self.batch);e=batch['entries'][-1]
        e['editions']['en']['claims']=[copy.deepcopy(batch['entries'][0]['editions']['en']['claims'][0])]
        self.assertIn('unverifiable sources cannot claim verified facts',archive.validate_batch(batch,self.manifest))

    def test_terminal_dispositions_require_human_review_and_real_pr(self):
        for state in ('approved','published','merged_duplicate','unverifiable_archived','awaiting_review'):
            value=copy.deepcopy(self.manifest);value['items'][0]['status']=state
            with self.subTest(state=state):self.assertTrue(archive.validate_manifest(value))

    def test_batch_assignments_are_bidirectional(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);directory=root/archive.DIRECTORY
            value=copy.deepcopy(self.manifest)
            archive.write(directory/'manifest.json',value)
            shutil.copytree(ROOT/archive.DIRECTORY/'batches',directory/'batches')
            if (ROOT/'src/content/renewals').exists():shutil.copytree(ROOT/'src/content/renewals',root/'src/content/renewals')
            with patch.object(archive,'source_records',return_value=archive.source_records(ROOT)):
                self.assertEqual([],archive.check(root))
                next(r for r in value['items'] if r['batchId'])['batchId']=None
                archive.write(directory/'manifest.json',value)
                self.assertTrue(archive.check(root))

    def test_review_body_is_readable_and_escapes_untrusted_source_text(self):
        manifest=copy.deepcopy(self.manifest)
        identity=self.batch['entries'][0]['id']
        next(r for r in manifest['items'] if r['id']==identity)['originalTitle']='<script>evil</script> @user [click](javascript:alert)'
        body=archive.render(self.batch,manifest)
        self.assertIn('English:',body);self.assertIn('한국어:',body)
        self.assertIn('&#64;user',body);self.assertNotIn('<script>',body)
        self.assertNotIn('[click](javascript:',body)
        self.assertLess(len(body),60000)

    def test_collection_is_private_to_pipeline_and_public_sources_are_unchanged(self):
        # Public content loaders are bounded to src/content; archive drafts remain outside.
        config=(ROOT/'src/content.config.ts').read_text()
        self.assertNotIn('archive-renewal',config)
        self.assertFalse(any((ROOT/'src/content').rglob('pilot-001.json')))
        self.assertFalse(any((ROOT/'public').rglob('pilot-001.json')))
        self.assertEqual([],archive.check(ROOT))

    def test_shared_author_host_is_approved_for_exact_source_only(self):
        batch=archive.read(ROOT/archive.DIRECTORY/'batches/batch-002.json')
        self.assertEqual([],archive.validate_batch(batch,self.manifest))
        entry=next(e for e in batch['entries'] if e['id']=='d9492522fb4514ef')
        entry['documents'][0]['url']='https://dev.to/another-author/unreviewed-post'
        self.assertIn('unapproved primary publisher',archive.validate_batch(batch,self.manifest))

    def test_next_batch_stays_outside_public_collection(self):
        batch=archive.read(ROOT/archive.DIRECTORY/'batches/batch-002.json')
        self.assertEqual(9,sum(e['outcome']=='renewed_draft' for e in batch['entries']))
        self.assertEqual(1,sum(e['outcome']=='unverifiable_proposal' for e in batch['entries']))
        for entry in batch['entries']:
            self.assertIsNone(entry['editionPublishedAt']['en'])
            self.assertFalse((ROOT/'src/content/renewals'/(entry['id']+'.json')).exists())


if __name__=='__main__':unittest.main()
