import copy
from datetime import datetime,timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import archive_renewal as archive
import publish_archive as publisher

ROOT=Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=archive.read(ROOT/archive.DIRECTORY/'manifest.json')
        cls.batch=archive.read(ROOT/archive.DIRECTORY/'batches/pilot-001.json')
        cls.public=archive.read(next((ROOT/publisher.PUBLIC).glob('*.json')))

    def test_valid_archive_keeps_original_korean_date_and_actual_english_date(self):
        self.assertEqual([],publisher.validate_publication(self.public,self.manifest))
        self.assertEqual(self.public['originalPagePublishedAt'],self.public['editionPublishedAt']['ko'])
        self.assertGreater(self.public['editionPublishedAt']['en'],self.public['editionPublishedAt']['ko'])

    def test_rejects_draft_unverifiable_backdated_or_unapproved_publication(self):
        for kind in ('draft','unverifiable','backdated','original_date','future','approval','source','translation','quote','primary','slug'):
            d=copy.deepcopy(self.public)
            if kind=='draft':d['state']='draft'
            if kind=='unverifiable':d['outcome']='unverifiable_proposal'
            if kind=='backdated':d['editionPublishedAt']['en']=d['originalPagePublishedAt']
            if kind=='original_date':d['editionPublishedAt']['ko']=d['updatedAt']
            if kind=='future':d['updatedAt']='2099-01-01T00:00:00Z'
            if kind=='approval':d['approval']['reviewedBy']=''
            if kind=='source':d['url']='https://spring.io/wrong-source/'
            if kind=='translation':d['editions']['ko']['claims'][0]['text']+=' 999%'
            if kind=='quote':d['editions']['en']['claims'][0]['evidence'][0]['quote']='short'
            if kind=='primary':d['documents'][0]['role']='reporting'
            if kind=='slug':d['slug']='2026-01-01-recent-news'
            with self.subTest(kind=kind):self.assertTrue(publisher.validate_publication(d,self.manifest))

    def test_legacy_patch_preserves_other_articles_and_original_heading(self):
        p=self.public;source=(ROOT/p['sourceFile']).read_text()
        # Restore a sentinel stale summary in just the selected block.
        old=publisher.patch_legacy(source,[p])
        entry=copy.deepcopy(p);entry['editions']['ko']['claims'][0]['text']='교체한 요약 문장입니다.'
        new=publisher.patch_legacy(old,[entry])
        self.assertIn('교체한 요약 문장입니다.',new)
        start=f"### {p['articleNumber']}. "
        before=old.split(start)[0];self.assertTrue(new.startswith(before))
        import re
        next_block=re.search(r'^### '+str(p['articleNumber']+1)+r'\.',old,re.M)
        if next_block:self.assertEqual(old[next_block.start():],new[new.index(next_block[0]):])
        for key in ('publishedAt','archiveBodySha256','legacySource'):
            self.assertEqual(re.search(r'^'+key+r':.*$',source,re.M)[0],re.search(r'^'+key+r':.*$',new,re.M)[0])

    def context(self,folder):
        root=Path(folder);manifest=copy.deepcopy(self.manifest)
        for r in manifest['items']:
            if r['status']=='published':
                r['status']='awaiting_review';r.pop('approval',None);r.pop('publication',None)
        batch=copy.deepcopy(self.batch);batch['entries']=batch['entries'][:1]
        e=batch['entries'][0];r=next(r for r in manifest['items'] if r['id']==e['id'])
        archive.write(root/archive.DIRECTORY/'manifest.json',manifest)
        path=root/r['sourceFile'];path.parent.mkdir(parents=True);path.write_text((ROOT/r['sourceFile']).read_text())
        now=datetime.now(timezone.utc).isoformat(timespec='seconds')
        approval={'reviewedBy':'reviewer','pullRequest':30,'approvedAt':now,'basis':'Explicit test approval'}
        return root,batch,{e['id']:e['archiveDate']+'-test-publication'},approval,now,path

    def test_publisher_requires_exact_selection_and_does_not_publish_blocked_items(self):
        with tempfile.TemporaryDirectory() as folder:
            root,batch,slugs,approval,now,path=self.context(folder)
            records=archive.source_records(ROOT)
            with patch.object(archive,'source_records',return_value=records):
                with self.assertRaisesRegex(ValueError,'exactly'):publisher.publish(root,batch,{},approval,published_at=now,check_sources=False)
                output=publisher.publish(root,batch,slugs,approval,published_at=now,check_sources=False)
                self.assertEqual(1,len(output));self.assertEqual(1,len(list((root/publisher.PUBLIC).glob('*.json'))))
                with self.assertRaises(ValueError):publisher.publish(root,batch,slugs,approval,published_at=now,check_sources=False)
            record=next(r for r in archive.read(root/archive.DIRECTORY/'manifest.json')['items'] if r['id']==batch['entries'][0]['id'])
            self.assertEqual('published',record['status']);self.assertTrue(record['publication'])
        with self.assertRaisesRegex(ValueError,'Blocked'):publisher.publication(self.batch,self.batch['entries'][-1],{},slug='2026-01-01-test',approval={},published_at=now)

    def test_network_failure_cannot_partially_write_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            root,batch,slugs,approval,now,path=self.context(folder);before=path.read_text()
            with patch.object(archive,'source_records',return_value=archive.source_records(ROOT)),patch.object(publisher,'fetch_document',side_effect=ValueError('source unavailable')):
                with self.assertRaisesRegex(ValueError,'unavailable'):publisher.publish(root,batch,slugs,approval,published_at=now)
            self.assertEqual(before,path.read_text());self.assertFalse((root/publisher.PUBLIC).exists())

    def test_failed_write_rolls_back_original_page_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root,batch,slugs,approval,now,path=self.context(folder);before=path.read_text()
            manifest_before=(root/archive.DIRECTORY/'manifest.json').read_text()
            original_write=publisher.write
            def failing_write(dest,data):
                if Path(dest).name=='manifest.json':raise OSError('simulated disk failure')
                return original_write(dest,data)
            with patch.object(archive,'source_records',return_value=archive.source_records(ROOT)),patch.object(publisher,'write',side_effect=failing_write):
                with self.assertRaisesRegex(OSError,'disk failure'):publisher.publish(root,batch,slugs,approval,published_at=now,check_sources=False)
            self.assertEqual(before,path.read_text());self.assertEqual(manifest_before,(root/archive.DIRECTORY/'manifest.json').read_text())
            self.assertEqual([],list((root/publisher.PUBLIC).glob('*.json')))

    def test_public_content_must_match_approved_batch_and_manifest(self):
        self.assertEqual([],publisher.check_publications(ROOT,self.manifest))
        value=copy.deepcopy(self.manifest)
        next(r for r in value['items'] if r['id']==self.public['id'])['status']='blocked'
        self.assertTrue(publisher.check_publications(ROOT,value))


if __name__=='__main__':unittest.main()
