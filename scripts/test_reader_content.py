from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from xml.sax.saxutils import escape

import check_reader_content as gate

FOCUS = 'PRIVATE editorial recommendation that readers should never receive.'


class ReaderContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels, _, _ = gate.policy()

    def test_internal_headings_records_and_hidden_cards_are_rejected(self):
        for content in ('<h2>검토 기록 — 2026-10-28</h2>', '<strong>검토 초점 · 직접 적용 결과가 아닌 편집 제안</strong>', '<li>리뉴얼 검토일: 2026-10-28</li>', '<aside data-candidate-review hidden>Anything</aside>', '<div class="candidate-review">Anything</div>', '<dl data-review-fields>Anything</dl>', '<div><span>활용 가이드</span></div>', '<h2>검토/보강</h2>'):
            with self.subTest(content=content):
                self.assertTrue(gate.html_errors('<article class="article">'+content+'</article>', self.labels))
        self.assertIn('internal-review-markup', gate.html_errors('<aside data-candidate-review hidden></aside><article class="article"><p>News</p></article>', self.labels))

    def test_every_localized_internal_label_is_rejected(self):
        ui = json.loads((gate.BASE/'src/lib/archive-ui.json').read_text())
        for language, edition in ui.items():
            for key in gate.INTERNAL_KEYS:
                with self.subTest(language=language, key=key):
                    self.assertIn('internal-editorial-label', gate.html_errors('<article class="article"><h2>'+edition[key]+'</h2></article>', self.labels))

    def test_known_advice_without_a_label_is_rejected_but_never_returned(self):
        errors = gate.html_errors('<article class="article"><p>'+FOCUS+'</p></article>', self.labels, FOCUS)
        self.assertEqual(errors, {'internal-review-advice'})
        self.assertNotIn(FOCUS, str(errors))
        self.assertEqual(gate.text_errors(FOCUS, self.labels, FOCUS), {'internal-review-advice'})

    def test_code_quotations_facts_and_source_links_are_preserved(self):
        html = '<article class="article"><h2>Code review</h2><p>코드 검토와 보안 검토를 수행합니다. 버전 14의 제약은 유지됩니다.</p><p>검토 초점은 API의 입력 계약입니다.</p><pre><code>검토 기록\n'+FOCUS+'</code></pre><blockquote><p>편집 제안</p></blockquote><p><a href="https://example.com">출처</a></p></article>'
        self.assertEqual(gate.html_errors(html, self.labels, FOCUS), set())
        text = '## Code review\n\n코드 검토와 보안 검토\n\n```md\n## 검토 기록\n'+FOCUS+'\n```\n> 편집 제안\n후속 제한 조건은 유지됩니다.'
        self.assertEqual(gate.text_errors(text, self.labels, FOCUS), set())

    def test_review_shell_is_outside_public_inventory_but_missing_article_fails(self):
        self.assertEqual(gate.html_errors('<h1>초안 검토</h1>', self.labels), {'missing-public-article'})
        self.assertEqual(gate.html_errors('<h1>초안 검토</h1>', self.labels, fragment=True), set())

    def test_fragment_entities_inline_markup_and_unclosed_tags_do_not_bypass_labels(self):
        for html in ('<h2>검토 <em>기록</em></h2>', '<p>검토&nbsp;기록</p>', '<span>검토 기록', '검토 기록'):
            self.assertIn('internal-editorial-label', gate.html_errors(html, self.labels, fragment=True))

    def fixture(self, root, html=None, row=None, description='Qualified news.', encoded='<p>Qualified news.</p>'):
        url = '/en/digest/example/'
        row = row or {'url': url, 'title': 'A public article', 'description': 'Qualified news.', 'content': 'Qualified news.'}
        index = root/'en/search-index.json'; index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps([row]))
        article = root/'en/digest/example/index.html'; article.parent.mkdir(parents=True, exist_ok=True)
        article.write_text(html or '<article class="article"><h1>A public article</h1><p>Qualified news.</p></article>')
        feed = '<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><item><title>A public article</title><link>https://youdozi.github.io'+url+'</link><description>'+escape(description)+'</description><content:encoded>'+escape(encoded)+'</content:encoded></item></channel></rss>'
        (root/'feed.xml').write_text(feed); (root/'en/feed.xml').write_text(feed)
        (root/'review').mkdir(exist_ok=True)
        (root/'review/index.html').write_text('<h1>검토 기록</h1><aside data-candidate-review></aside>')
        return row

    def test_whole_output_checks_inventory_and_both_feed_paths_without_review_shell(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root)
            errors, counts = gate.check(root, self.labels, {}, {'en'})
            self.assertEqual(errors, [])
            self.assertEqual(counts, {'articles': 1, 'searchIndexes': 1, 'feeds': 2})

    def test_html_search_metadata_search_body_and_feed_leaks_fail_the_gate(self):
        for surface in ('html', 'search-body', 'search-metadata', 'feed-description', 'feed-content', 'feed-metadata', 'advice'):
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); row = self.fixture(root)
                if surface == 'html': self.fixture(root, html='<article class="article"><h2>검토 기록</h2></article>')
                if surface == 'search-body':
                    row['content'] = '## 검토 기록 — 2026-10-28\nInternal content'
                    self.fixture(root, row=row)
                if surface == 'search-metadata':
                    row['reviewFocus'] = FOCUS; self.fixture(root, row=row)
                if surface == 'feed-description': self.fixture(root, description='<strong>검토 기록</strong>')
                if surface == 'feed-content': self.fixture(root, encoded='<h2>검토 기록</h2>')
                if surface == 'feed-metadata':
                    path = root/'en/feed.xml'; path.write_text(path.read_text().replace('</item>', '<reviewFocus>'+FOCUS+'</reviewFocus></item>'))
                if surface == 'advice': self.fixture(root, encoded='<p>'+FOCUS+'</p>')
                errors, _ = gate.check(root, self.labels, {'/en/digest/example/': FOCUS}, {'en'})
                self.assertTrue(errors)
                self.assertNotIn(FOCUS, str(errors))

    def test_missing_malformed_empty_and_duplicate_inventory_cannot_pass(self):
        for mutation in ('missing-index', 'malformed-index', 'empty-index', 'duplicate', 'missing-article', 'missing-feed', 'malformed-feed', 'empty-feed'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); row = self.fixture(root)
                index = root/'en/search-index.json'
                if mutation == 'missing-index': index.unlink()
                if mutation == 'malformed-index': index.write_text('{broken')
                if mutation == 'empty-index': index.write_text('[]')
                if mutation == 'duplicate': index.write_text(json.dumps([row, deepcopy(row)]))
                if mutation == 'missing-article': (root/'en/digest/example/index.html').unlink()
                if mutation == 'missing-feed': (root/'en/feed.xml').unlink()
                if mutation == 'malformed-feed': (root/'en/feed.xml').write_text('<broken')
                if mutation == 'empty-feed': (root/'en/feed.xml').write_text('<rss><channel/></rss>')
                self.assertTrue(gate.check(root, self.labels, {}, {'en'})[0])

    def test_unlisted_feed_entry_and_urls_outside_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.fixture(root)
            path = root/'en/feed.xml'; path.write_text(path.read_text().replace('/en/digest/example/', '/en/digest/unlisted/'))
            self.assertTrue(gate.check(root, self.labels, {}, {'en'})[0])
            for url in ('https://outside.example/a/', '//outside.example/a/', '/../outside/', '/%2e%2e/outside/', '/en/a/?x=1'):
                with self.subTest(url=url), self.assertRaises(ValueError): gate.article_file(root, url)

    def test_build_runs_gate_before_any_indexnow_submission_step(self):
        scripts = json.loads((gate.BASE/'package.json').read_text())['scripts']
        self.assertIn('python3 -B scripts/check_reader_content.py', scripts['build'])
        self.assertLess(scripts['build'].index('check_reader_content.py'), scripts['build'].index('indexnow.py'))


if __name__ == '__main__': unittest.main()
