import copy
import hashlib
import json
import subprocess
import unittest
from unittest.mock import patch
from pathlib import Path
import archive_sources as sources
import archive_renewal as archive
from ai_dev_digest import ArticleParser

URL='https://www.infoq.com/articles/example/'
ARTICLE='<h2>Limits and mitigation</h2><p>'+('Evidence must remain complete. '*6)+'</p><table><tr><th>Affected</th><td>1.0 to 1.4</td></tr></table><pre>allowScripts = false</pre>'


def response(markup,status=200,final=URL,mime='text/html'):
    return subprocess.CompletedProcess([],0,markup+'\n'+json.dumps({'http_code':status,'url_effective':final,'content_type':mime}),'')


class ExtractionTests(unittest.TestCase):
    def test_v1_remains_identical_and_v2_excludes_reordered_footer(self):
        a='<main><article><div class="article__data">'+ARTICLE+'</div><ul class="related__topics"><li>Cloud</li><li>Security</li></ul></article></main>'
        b=a.replace('<li>Cloud</li><li>Security</li>','<li>Security</li><li>Cloud</li>')
        old=ArticleParser();old.feed(a)
        self.assertEqual(old.extract(),sources.extract_body(a,'article-parser-v1'))
        self.assertNotEqual(sources.extract_body(a,'article-parser-v1'),sources.extract_body(b,'article-parser-v1'))
        self.assertEqual(sources.extract_body(a,'article-parser-v2'),sources.extract_body(b,'article-parser-v2'))
        stable=sources.extract_body(a,'article-parser-v2')
        for value in ['Limits and mitigation','Affected','1.0 to 1.4','allowScripts = false']:
            self.assertIn(value,stable)
        self.assertNotIn('Cloud',stable)
        self.assertNotEqual(stable,sources.extract_body(a.replace('1.4','1.5'),'article-parser-v2'))

    def test_filters_structural_chrome_without_cutting_article_prose(self):
        html='<main><nav>Navigation</nav><article><div itemprop="articleBody">'+ARTICLE+'<p>Related Topics: this phrase belongs to the article.</p><aside>Promotion</aside><div class="related__group">Offer</div><section><p>Final caveat survives.</p></section></div><div class="author-section-full">Bio</div></article><footer>Privacy</footer></main>'
        body=sources.extract_body(html,'article-parser-v2')
        for phrase in ['Final caveat survives.','Related Topics: this phrase belongs to the article.']:
            self.assertIn(phrase,body)
        for phrase in ['Navigation','Promotion','Offer','Bio','Privacy']:
            self.assertNotIn(phrase,body)

    def test_markdown_body_excludes_repository_counters(self):
        template='<main><article><span>{counter} commits since release</span><div class="markdown-body">'+ARTICLE+'</div><div>Reactions {counter}</div></article></main>'
        self.assertEqual(sources.extract_body(template.format(counter=10),'article-parser-v2'),
                         sources.extract_body(template.format(counter=11),'article-parser-v2'))
        self.assertNotIn('commits since release',sources.extract_body(template.format(counter=10),'article-parser-v2'))

    def test_nested_void_and_hidden_elements_do_not_lose_body(self):
        body=sources.extract_body('<main><article><div class="entry-content"><p>Visible before<br/> and after<img src="x"/>.</p><div hidden>Secret</div><div aria-hidden="true">Hidden</div><p>Last paragraph.</p></div></article></main>','article-parser-v2')
        self.assertIn('Visible before and after .',body);self.assertIn('Last paragraph.',body)
        self.assertNotIn('Secret',body);self.assertNotIn('Hidden',body)
        with self.assertRaises(ValueError):sources.extract_body('<main>x</main>','future-parser')

    def test_document_versions_have_separate_hash_and_quote_evidence(self):
        root=Path(__file__).resolve().parents[1]
        batch=copy.deepcopy(archive.read(root/'.pipeline/archive-renewal/batches/pilot-001.json'))
        batch['entries']=batch['entries'][:1];entry=batch['entries'][0]
        bodies={}
        shared_url=entry['documents'][1]['url']
        for i,d in enumerate(entry['documents']):
            d['url']=shared_url
            d['extractorVersion']='article-parser-v2' if i else 'article-parser-v1'
            quotes=[q['quote'] for ed in entry['editions'].values() for c in ed['claims']+ed['followUp'] for q in c['evidence'] if q['document_id']==i]
            body=' '.join(quotes)+' unique '+str(i)
            bodies[(d['url'],d['extractorVersion'])]=body;d['sha256']=hashlib.sha256(body.encode()).hexdigest()
        manifest=archive.read(root/'.pipeline/archive-renewal/manifest.json')
        self.assertEqual([],archive.validate_batch(batch,manifest,documents=bodies))
        d=entry['documents'][0];bodies[(d['url'],d['extractorVersion'])]+=' changed'
        self.assertTrue(any('source content changed' in e for e in archive.validate_batch(batch,manifest,documents=bodies)))


class TransportTests(unittest.TestCase):
    def test_timeout_uses_ipv4_and_retains_https_and_bounds(self):
        fail=subprocess.CompletedProcess([],28,'','timeout')
        with patch.object(sources.subprocess,'run',side_effect=[fail,response('<article>'+ARTICLE+'</article>')]) as run:
            self.assertIn('Affected',sources.fetch_document(URL))
        self.assertEqual(2,run.call_count)
        self.assertNotIn('--ipv4',run.call_args_list[0].args[0]);self.assertIn('--ipv4',run.call_args_list[1].args[0])
        for call in run.call_args_list:
            for value in ['--disable','--proto','=https','--proto-redir','--max-redirs','--max-time','--max-filesize']:
                self.assertIn(value,call.args[0])

    def test_retries_are_bounded_and_python_timeouts_are_sanitized(self):
        with patch.object(sources.subprocess,'run',return_value=subprocess.CompletedProcess([],28,'','')) as run:
            with self.assertRaisesRegex(ValueError,'attempt 3'):sources.fetch_document(URL)
            self.assertEqual(3,run.call_count)
        with patch.object(sources.subprocess,'run',side_effect=subprocess.TimeoutExpired('curl',17)) as run:
            with self.assertRaisesRegex(ValueError,'3 bounded attempts'):sources.fetch_document(URL)
            self.assertEqual(3,run.call_count)

    def test_does_not_retry_challenges_bad_html_redirects_or_certificate_errors(self):
        for result in [response('<article>'+ARTICLE+'</article>',202),response('{}',mime='application/json'),response('<article>'+ARTICLE+'</article>',final='https://other.example/a'),response('<article>Short</article>'),subprocess.CompletedProcess([],60,'','certificate error'),subprocess.CompletedProcess([],22,'','HTTP failure')]:
            with self.subTest(result=result),patch.object(sources.subprocess,'run',return_value=result) as run:
                with self.assertRaises(ValueError):sources.fetch_document(URL)
                self.assertEqual(1,run.call_count)
        with patch.object(sources.subprocess,'run') as run:
            with self.assertRaises(ValueError):sources.fetch_document('http://unsafe.example/')
            with self.assertRaises(ValueError):sources.fetch_document(URL,'unsupported')
            run.assert_not_called()

    def test_ipv4_success_still_rejects_a_202_response(self):
        with patch.object(sources.subprocess,'run',side_effect=[subprocess.CompletedProcess([],28,'',''),response('<article>'+ARTICLE+'</article>',202)]) as run:
            with self.assertRaisesRegex(ValueError,'HTTP 202'):sources.fetch_document(URL)
            self.assertEqual(2,run.call_count)


if __name__=='__main__':unittest.main()
