import copy
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime
import check_digests
import generate_dev_digest as legacy
from test_bilingual_digest import article


class SavedDigestTests(unittest.TestCase):
    def data(self):
        now=datetime.now(legacy.KST)
        return {'date':now.date().isoformat(),'publishedAt':now.isoformat(),'articles':[article()]}

    def test_real_saved_files_fail_publication_validation(self):
        for failure in ['source','future','korean_length','evidence','filename']:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as folder:
                data=self.data();a=data['articles'][0]
                if failure=='source':a['url']='https://unapproved.example/news'
                if failure=='future':a['publishedAt']='2099-01-01T00:00:00+00:00'
                if failure=='korean_length':
                    a['editions']['ko']['claims'][0]['text']='가'*300
                    a['editions']['ko']['claims'][1]['text']='나'*200
                    a['editions']['ko']['summary']=' '.join(c['text'] for c in a['editions']['ko']['claims'])
                if failure=='evidence':a['editions']['en']['claims'][0]['evidence'][0]['quote']='short'
                name='2000-01-01' if failure=='filename' else data['date']
                (Path(folder)/(name+'.json')).write_text(json.dumps(data))
                self.assertTrue(check_digests.check_directory(folder))

    def test_real_valid_saved_digest_and_empty_directory_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual([],check_digests.check_directory(folder))
            data=self.data();(Path(folder)/(data['date']+'.json')).write_text(json.dumps(data))
            self.assertEqual([],check_digests.check_directory(folder))


if __name__ == '__main__':unittest.main()
