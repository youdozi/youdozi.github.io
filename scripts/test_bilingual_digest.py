"""Offline integration tests for language pairs and transactional publication gates."""
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import ai_dev_digest as ai
import bilingual_digest as bilingual
import generate_digest as generator
import generate_dev_digest as legacy
from test_ai_dev_digest import BODY, CLAIMS
from test_dev_digest import item
import test_dev_digest as fixtures

EN_CLAIMS = [
    {"text_en": "Spring Security now requires explicit OAuth scopes for service accounts.", "evidence": [{"document_id": 0, "quote": "requires explicit OAuth scopes for service accounts"}]},
    {"text_en": "The update is in public preview and is not generally available.", "evidence": [{"document_id": 0, "quote": "in public preview, not generally available"}]},
]


def generated_claims():
    return {"en": {"review":{"keyChange":[0],"affectedAudience":[0],"conditions":[1]}, "title": "Spring Security OAuth scope update", "claims": copy.deepcopy(EN_CLAIMS)}, "ko": {"review":{"keyChange":[0],"affectedAudience":[0],"conditions":[1]}, "title": "Spring Security OAuth 범위 업데이트", "claims": copy.deepcopy(CLAIMS)}}


def review():
    return {lang: {"supported": True, "requires_official": True, "title_supported":True, "equivalent":True, "conditions_complete":True, "claims": [{"index": i, "supported": True} for i in range(2)]} for lang in ("en", "ko")}


def article():
    current = item()
    generated = generated_claims()
    return {"id": "test-id", "source": current.source_name, "url": current.link, "publishedAt": current.published_at.isoformat(), "tags": current.topic_tags,
        "editions": {lang: {"title": generated[lang]["title"], "summary": " ".join(c[f"text_{lang}"] for c in generated[lang]["claims"]), "claims": [{"text": c[f"text_{lang}"], "evidence": c["evidence"]} for c in generated[lang]["claims"]]} for lang in ("en", "ko")},
        "model": "test-model", "verification": "source_consistency_checked", "documents": [{"url": "https://spring.io/blog/release", "sha256": hashlib.sha256(BODY.encode()).hexdigest()}]}


class BilingualTests(unittest.TestCase):
    def summarize(self, generated=None, verdict=None):
        client = MagicMock(); client.model = 'test-model'
        client.generate.side_effect = [generated or generated_claims(), verdict or review()]
        with patch.object(ai, 'fetch_document', return_value=ai.Document('https://spring.io/blog/release', BODY, [])):
            result = bilingual.summarize_item(item(), client)
        return result, client

    def test_both_editions_verified_with_two_calls_and_no_full_body_saved(self):
        result, client = self.summarize()
        self.assertEqual(2,client.generate.call_count)
        self.assertEqual({'en','ko'},set(result['editions']))
        self.assertIn('OAuth', result['editions']['en']['summary'])
        self.assertNotIn('body',result['documents'][0])

    def test_korean_failure_blocks_language_pair(self):
        verdict = review(); verdict['ko']['claims'][1]['supported'] = False
        with self.assertRaises(ai.ArticleUnavailable): self.summarize(verdict=verdict)

    def test_english_claim_without_evidence_is_withheld(self):
        generated = generated_claims(); generated['en']['claims'][0]['evidence'][0]['quote'] = 'Fabricated evidence that never appeared.'
        with self.assertRaises(ai.ArticleUnavailable): self.summarize(generated=generated)

    def test_missing_edition_is_withheld(self):
        generated = generated_claims(); del generated['en']
        with self.assertRaises(ai.ArticleUnavailable): self.summarize(generated=generated)

    def test_reviewer_requires_primary_source_in_both_editions(self):
        client = MagicMock();client.model='test'
        client.generate.side_effect = [generated_claims(),review()]
        doc=ai.Document('https://www.infoq.com/news/article',BODY,[])
        current=item(title='Java software maintenance',source='InfoQ')
        with patch.object(ai,'fetch_document',return_value=doc), self.assertRaises(ai.ArticleUnavailable):
            bilingual.summarize_item(current,client)

    def test_wrong_review_indices_block_publication(self):
        verdict=review();verdict['en']['claims'][1]['index']=0
        with self.assertRaises(ai.ArticleUnavailable): self.summarize(verdict=verdict)

    def test_title_and_semantic_checks_fail_closed(self):
        for key in ('title_supported','equivalent','conditions_complete'):
            for value in (False,None):
                with self.subTest(key=key,value=value):
                    verdict=review();verdict['ko'][key]=value
                    with self.assertRaises(ai.ArticleUnavailable):self.summarize(verdict=verdict)

    def test_title_comparison_absent_from_claims_is_withheld_before_second_call(self):
        generated=generated_claims();generated['en']['title']='Spring Security is 100x faster'
        with self.assertRaisesRegex(ai.ArticleUnavailable,'title numbers'):self.summarize(generated=generated)

    def test_component_omission_is_withheld(self):
        generated=generated_claims();generated['ko']['claims'][0]['text_ko']=generated['ko']['claims'][0]['text_ko'].replace('OAuth','인증')
        with self.assertRaisesRegex(ai.ArticleUnavailable,'protected terms'):self.summarize(generated=generated)

    def test_benchmark_secondary_source_without_primary_is_withheld_before_ai(self):
        for title in ('Serverless queries 100x more data','Backend costs fall 50%','Database latency benchmark'):
            client=MagicMock()
            current=item(title=title,source='InfoQ')
            with self.subTest(title=title),patch.object(ai,'fetch_document',return_value=ai.Document(current.link,BODY,[])):
                with self.assertRaisesRegex(ai.ArticleUnavailable,'primary reference'):bilingual.summarize_item(current,client)
                client.generate.assert_not_called()

    def test_release_reference_precedes_issue_and_primary_contract_is_explicit(self):
        current=item(title='Agent release with compatibility requirements',source='InfoQ')
        repo='https://github.com/vendor/agent'
        issue=repo+'/issues/197'
        release=repo+'/releases/tag/v0.0.13'
        original=ai.Document(current.link,BODY,[repo,issue,release])
        generated=generated_claims()
        for lang in ('en','ko'):
            for claim in generated[lang]['claims']:
                for evidence in claim['evidence']:evidence['document_id']=1
        client=MagicMock();client.model='test';client.generate.side_effect=[generated,review()]
        def fetch(url,hosts):return original if url==current.link else ai.Document(url,BODY,[])
        with patch.object(ai,'fetch_document',side_effect=fetch) as fetched:
            result=bilingual.summarize_item(current,client)
        self.assertEqual([current.link,release,repo],[call.args[0] for call in fetched.call_args_list])
        self.assertEqual(3,len(result['documents']))
        payload=client.generate.call_args_list[0].args[1]
        self.assertEqual([1,2],payload['primary_document_ids'])
        self.assertTrue(payload['require_primary_quotes'])
        self.assertIn('EVERY claim in BOTH editions',client.generate.call_args_list[0].args[0])


class PublicationTests(unittest.TestCase):
    def run_pipeline(self, root, extra=None, enrich=None, link_error=None):
        argv=['digest','--repo-root',str(root),'--github-output',str(root/'output'),*(extra or [])]
        with patch('sys.argv',argv), patch.object(legacy,'load_feed',side_effect=lambda *_: fixtures.PipelineTests().feed()), patch.object(generator,'enrich_items',side_effect=enrich or (lambda _: [article()])), patch.object(generator,'check_article_link',return_value=link_error), contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return generator.main()

    def test_json_generation_then_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(0,self.run_pipeline(root))
            files=list((root/'src/content/digests').glob('*.json'))
            self.assertEqual(1,len(files))
            self.assertEqual([],generator.validate_digest(json.loads(files[0].read_text())))
            self.assertEqual(0,self.run_pipeline(root))
            self.assertTrue((root/'output').read_text().endswith('generated=false\n'))

    def existing(self, root, count=1):
        now=datetime.now(legacy.KST)
        articles=[]
        for index in range(count):
            old=article();old['id']=f'old-{index}';old['url']=f'https://spring.io/old-{index}'
            articles.append(old)
        target=root/'src/content/digests'/f'{now.date().isoformat()}.json'
        target.parent.mkdir(parents=True)
        data={'date':now.date().isoformat(),'publishedAt':now.isoformat(),'articles':articles}
        target.write_text(json.dumps(data));return target,data

    def test_append_preserves_reviewed_content_and_publication_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,original=self.existing(root)
            self.assertEqual(0,self.run_pipeline(root,['--append']))
            updated=json.loads(target.read_text())
            self.assertEqual(original['articles'],updated['articles'][:1])
            self.assertEqual(original['publishedAt'],updated['publishedAt'])
            self.assertIn('updatedAt',updated)
            self.assertEqual(2,len(updated['articles']))
            self.assertEqual([],generator.validate_digest(updated))
            state=json.loads((root/'.pipeline/content_state.json').read_text())
            self.assertIn(original['articles'][0]['url'],state['seen_links'])
            self.assertIn('https://spring.io/article',state['seen_links'])

    def test_full_daily_digest_skips_ai_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,_=self.existing(root,6);before=target.read_bytes()
            def fail(_):raise AssertionError('AI must not run')
            self.assertEqual(0,self.run_pipeline(root,['--append'],enrich=fail))
            self.assertEqual(before,target.read_bytes())
            self.assertFalse((root/'.pipeline').exists())

    def test_failed_append_keeps_published_content_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,_=self.existing(root);before=target.read_bytes()
            self.assertEqual(1,self.run_pipeline(root,['--append','--check-links'],link_error='HTTP 404'))
            self.assertEqual(before,target.read_bytes());self.assertFalse((root/'.pipeline').exists())

    def test_append_respects_existing_source_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,_=self.existing(root,3);before=target.read_bytes()
            def fail(_):raise AssertionError('Source quota already full')
            self.assertEqual(0,self.run_pipeline(root,['--append'],enrich=fail))
            self.assertEqual(before,target.read_bytes())

    def test_append_fills_remaining_slot_from_another_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,data=self.existing(root,5)
            for index,old in enumerate(data['articles']):
                old['source']='InfoQ' if index<3 else 'Cloudflare Blog'
                host='www.infoq.com' if index<3 else 'blog.cloudflare.com'
                old['url']=f'https://{host}/old-{index}'
            target.write_text(json.dumps(data))
            candidates=[item(title='Java release update',source='InfoQ',link='https://www.infoq.com/news/new',score=12),item(title='Rust performance update',source='Cloudflare Blog',link='https://blog.cloudflare.com/new',score=8)]
            def enrich(selected):
                self.assertEqual(['Cloudflare Blog'],[i.source_name for i in selected])
                new=article();new['source']='Cloudflare Blog';new['url']='https://blog.cloudflare.com/new';return [new]
            with patch.object(legacy,'parse_feed',return_value=candidates):
                self.assertEqual(0,self.run_pipeline(root,['--append'],enrich=enrich))
            updated=json.loads(target.read_text())
            self.assertEqual(6,len(updated['articles']))
            self.assertEqual(data['articles'],updated['articles'][:5])

    def test_preview_validates_without_writing_content_or_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(0,self.run_pipeline(root,['--dry-run','--force']))
            self.assertFalse((root/'src').exists());self.assertFalse((root/'.pipeline').exists())
            self.assertEqual('generated=false\n',(root/'output').read_text())

    def test_ai_or_link_failures_do_not_write(self):
        for failure in ('ai','link'):
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                def enrich(_): raise ai.AIError('quota exhausted')
                code=self.run_pipeline(root,['--check-links'],enrich=enrich if failure=='ai' else None,link_error='HTTP 404' if failure=='link' else None)
                self.assertEqual(1,code);self.assertFalse((root/'src').exists());self.assertFalse((root/'.pipeline').exists())

    def test_new_json_history_blocks_republishing_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);history=root/'src/content/digests';history.mkdir(parents=True)
            (history/'2020-01-01.json').write_text(json.dumps({'articles':[{'url':'https://spring.io/article'}]}))
            self.assertEqual(0,self.run_pipeline(root))
            self.assertEqual(1,len(list(history.glob('*.json'))))
            self.assertFalse((root/'.pipeline').exists())

    def test_unchecked_summary_or_bad_evidence_reference_rejected(self):
        for failure in ('summary','evidence','duplicate'):
            with self.subTest(failure=failure):
                a=article()
                if failure=='summary': a['editions']['en']['summary'] += ' Unchecked facts.'
                if failure=='evidence': a['editions']['ko']['claims'][0]['evidence'][0]['document_id']=9
                now=datetime.now(legacy.KST)
                data={'date':now.date().isoformat(),'publishedAt':now.isoformat(),'articles':[a,a] if failure=='duplicate' else [a]}
                self.assertTrue(generator.validate_digest(data))


if __name__=='__main__': unittest.main()
