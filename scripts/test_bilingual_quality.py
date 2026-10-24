import copy
import unittest
from bilingual_quality import validate_editions


def editions():
    return {
        'en':{'title':'AWS Lambda queries S3 data','claims':[{'text':'AWS Lambda queries S3 data in five regions.'},{'text':'The benchmark ingested 1,000 files in 18 seconds.'}], 'review':{'keyChange':[0],'affectedAudience':[],'conditions':[1]}},
        'ko':{'title':'AWS 람다로 S3 데이터 조회','claims':[{'text':'AWS 람다는 5개 리전에서 S3 데이터를 조회한다.'},{'text':'벤치마크에서 파일 1000개를 18초에 수집했다.'}], 'review':{'keyChange':[0],'affectedAudience':[],'conditions':[1]}},
    }


class QualityTests(unittest.TestCase):
    def test_aliases_and_number_formatting_preserve_facts(self):
        self.assertEqual([],validate_editions(editions()))

    def test_observed_title_component_and_number_failures_are_rejected(self):
        for kind in ('title','component','number','order','count','section'):
            value=copy.deepcopy(editions())
            if kind=='title':value['en']['title']='AWS Lambda queries 100x more data'
            if kind=='component':value['ko']['claims'][0]['text']='AWS는 5개 리전에서 데이터를 조회한다.'
            if kind=='number':value['ko']['claims'][1]['text']='벤치마크에서 파일 1000개를 8초에 수집했다.'
            if kind=='order':value['ko']['claims'].reverse()
            if kind=='count':value['ko']['claims'].pop()
            if kind=='section':value['ko']['review']['conditions']=[]
            with self.subTest(kind=kind):self.assertTrue(validate_editions(value))

    def test_matching_facts_do_not_prove_semantic_equivalence(self):
        value=editions();value['ko']['claims'][1]['text']='파일 1000개를 18초에 수집하지 못했다.'
        # The independent semantic reviewer must catch negation; token checks cannot.
        self.assertEqual([],validate_editions(value))
