import copy
from datetime import datetime
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
import ai_dev_digest as ai
import bilingual_digest as bilingual
import editorial_digest as editorial
import generate_digest as generator
import generate_dev_digest as legacy
from render_digest_review import render
from test_dev_digest import item
from test_bilingual_digest import article,generated_claims,review
from test_ai_dev_digest import BODY


def candidate():
    a=article();a['selection']=editorial.selection_profile(item());a['editorial']=editorial.empty_editorial()
    for lang in ('en','ko'):a['editions'][lang]['review']={'keyChange':[0],'affectedAudience':[],'conditions':[1]}
    return a


class EditorialTests(unittest.TestCase):
    def test_relevance_and_promotional_filters(self):
        self.assertEqual('direct',editorial.selection_profile(item(title='Spring Boot release',summary='Runtime compatibility for production apps.'))['relevance'])
        self.assertEqual('adjacent',editorial.selection_profile(item(title='Database observability update',summary='Query diagnostics for database operators.'))['relevance'])
        self.assertIsNone(editorial.selection_profile(item(title='JavaScript animation toolkit',summary='New animation widgets for frontend designers.')))
        self.assertIsNone(editorial.selection_profile(item(title='Spring webinar register now',summary='Join our live session.')))
        self.assertEqual('review-soon',editorial.selection_profile(item(title='Spring CVE-2026-12345 vulnerability',summary='Authentication update.'))['priority'])

    def test_reviews_only_reference_existing_claims(self):
        a=candidate();self.assertEqual([],editorial.validate_article_editorial(a))
        a['editions']['en']['review']['conditions']=[9]
        self.assertIn('review sections must reference verified claim indices',editorial.validate_article_editorial(a))

    def test_tested_flag_requires_human_report_environment_and_results(self):
        a=candidate();a['editorial']['experiment']['status']='tested'
        self.assertTrue(editorial.validate_article_editorial(a))
        a['editorial']['experiment'].update(reportUrl='https://github.com/youdozi/youdozi.github.io',environment={'en':'Java 21, macOS','ko':'Java 21, macOS'},result={'en':'Reproduced with recorded inputs.','ko':'기록한 입력으로 재현했습니다.'})
        self.assertEqual([],editorial.validate_article_editorial(a))
        a['editorial']['experiment']['reportUrl']='javascript:alert(1)'
        self.assertTrue(editorial.validate_article_editorial(a))

    def test_new_output_cannot_claim_an_ai_written_experiment_or_opinion(self):
        generated=generated_claims();generated['editorial']={'experiment':{'status':'tested'}}
        client=MagicMock();client.model='test';client.generate.side_effect=[generated,review()]
        with patch.object(ai,'Gemini',return_value=client),patch.object(ai,'fetch_document',return_value=ai.Document('https://spring.io/blog/release',BODY,[])):
            result=bilingual.enrich_items([item()])[0]
        self.assertEqual(2,client.generate.call_count)
        self.assertEqual('not_tested',result['editorial']['experiment']['status'])
        self.assertEqual({'en':'','ko':''},result['editorial']['opinion'])
        self.assertEqual('direct',result['selection']['relevance'])

    def test_invalid_review_map_withholds_the_language_pair(self):
        generated=generated_claims();generated['en']['review']['conditions']=[8]
        client=MagicMock();client.model='test';client.generate.return_value=generated
        with patch.object(ai,'fetch_document',return_value=ai.Document('https://spring.io/blog/release',BODY,[])),self.assertRaises(ai.ArticleUnavailable):
            bilingual.summarize_item(item(),client)

    def test_pr_contains_selection_source_sections_and_human_placeholders(self):
        a=candidate();body=render({'date':'2026-10-24','articles':[a]})
        for value in ['선정 이유','추천 독자','검토 우선순위','핵심 변경','영향을 받는 대상','도입 조건','편집 의견','직접 실험 미수행','원문 확인·검토 필요']:
            self.assertIn(value,body)
        self.assertLess(body.index('**핵심 변경**'),body.rindex('<details>'))

    def test_generation_prioritizes_review_signals_then_direct_relevance(self):
        from test_bilingual_digest import PublicationTests
        direct=item(title='Spring runtime update',link='https://spring.io/java-new',score=6,summary='The Spring runtime update describes API compatibility and migration notes for Java backend applications.')
        adjacent=item(title='Database storage update',source='Cloudflare Blog',link='https://blog.cloudflare.com/storage-new',score=12,summary='The database storage update adds observability for backend operators and documents deployment constraints.')
        priority=item(title='Database CVE-2026-12345 vulnerability',source='InfoQ',link='https://www.infoq.com/news/cve-new',score=6,summary='The database authentication patch addresses a critical vulnerability and describes how operators can apply the fix.')
        for candidates,expected in [([adjacent,direct],direct),([direct,priority],priority)]:
            with tempfile.TemporaryDirectory() as tmp:
                def enrich(selected):
                    self.assertEqual([expected.link],[i.link for i in selected])
                    a=article();a['url']=expected.link;a['source']=expected.source_name;return [a]
                with patch.object(legacy,'parse_feed',return_value=candidates):
                    self.assertEqual(0,PublicationTests().run_pipeline(Path(tmp),['--max-items','1'],enrich=enrich))

    def test_saved_metadata_is_checked_by_publication_validator(self):
        now=datetime.now(legacy.KST);a=candidate();a['editorial']['experiment']['status']='tested'
        data={'date':now.date().isoformat(),'publishedAt':now.isoformat(),'articles':[a]}
        self.assertTrue(generator.validate_digest(data))


if __name__=='__main__':unittest.main()
