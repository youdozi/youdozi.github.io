import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from archive_renewal import write
import recheck_archive_sources as recheck

URL='https://www.infoq.com/articles/example/'
QUOTE='The complete supported sentence must remain in the source.'


class HeldRecheckTests(unittest.TestCase):
    def fixture(self, folder, previous=True):
        root=Path(folder);directory=root/'.pipeline/archive-renewal'
        entry={'id':'held','editions':{'ko':{'title':'보류한 원고'}},'attemptedSourceUrls':[URL]}
        if previous:
            draft={'id':'held','editionPublishedAt':{'en':None},'documents':[{'url':URL,'role':'primary','sha256':'a'*64,'fetchedAt':'2026-01-01T00:00:00Z','extractorVersion':'article-parser-v1'}],
                   'editions':{lang:{'claims':[{'text':'요약' if lang=='ko' else 'Summary','evidence':[{'document_id':0,'quote':QUOTE}]}],'followUp':[]} for lang in ('en','ko')}}
            entry['research']={'previousDraft':draft}
        write(directory/'manifest.json',{'items':[{'id':'held','status':'blocked'}]})
        write(directory/'batches/example.json',{'batchId':'example','entries':[entry]})
        before={p:p.read_bytes() for p in directory.rglob('*.json')}
        return root,before

    def test_repeatable_sources_produce_private_candidates_without_mutating_approval_or_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root,before=self.fixture(folder)
            with patch.object(recheck,'fetch_document',return_value=QUOTE+' More evidence.'):
                report=recheck.recheck(root)
            item=report['items'][0];self.assertEqual('source_recheck_passed',item['status'])
            self.assertEqual('article-parser-v2',item['draftCandidate']['documents'][0]['extractorVersion'])
            self.assertIsNone(item['draftCandidate']['editionPublishedAt']['en'])
            self.assertNotIn('approval',item['draftCandidate'])
            for path,body in before.items():self.assertEqual(body,path.read_bytes())
            self.assertFalse(report['publicationStateChanged'])

    def test_readable_sources_do_not_resolve_missing_editorial_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            root,_=self.fixture(folder,previous=False)
            with patch.object(recheck,'fetch_document',return_value=QUOTE):report=recheck.recheck(root)
            self.assertEqual('editorial_evidence_still_required',report['items'][0]['status'])
            self.assertNotIn('draftCandidate',report['items'][0])

    def test_changed_sources_or_missing_quotes_cannot_be_recovered(self):
        for bodies in [[QUOTE,QUOTE+' Changed.'],['Unrelated body.','Unrelated body.']]:
            with self.subTest(bodies=bodies),tempfile.TemporaryDirectory() as folder:
                root,_=self.fixture(folder)
                with patch.object(recheck,'fetch_document',side_effect=bodies):report=recheck.recheck(root)
                self.assertNotEqual('source_recheck_passed',report['items'][0]['status'])
                self.assertNotIn('draftCandidate',report['items'][0])

    def test_challenge_stops_repeated_collection_without_using_old_body(self):
        with tempfile.TemporaryDirectory() as folder:
            root,_=self.fixture(folder)
            with patch.object(recheck,'fetch_document',side_effect=ValueError('HTTP 202')) as fetch:
                report=recheck.recheck(root)
            self.assertEqual(1,fetch.call_count)
            self.assertEqual('source_recheck_incomplete',report['items'][0]['status'])
            self.assertNotIn('draftCandidate',report['items'][0])


    def test_cli_preserves_an_existing_evidence_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json';path.write_text('existing evidence')
            with patch('sys.argv',['recheck','--output',str(path)]),patch.object(recheck,'recheck') as collect,patch('sys.stderr'):
                with self.assertRaises(SystemExit):recheck.main()
            collect.assert_not_called();self.assertEqual('existing evidence',path.read_text())


if __name__=='__main__':unittest.main()
