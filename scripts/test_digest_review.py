import copy
import unittest
from render_digest_review import render
from test_bilingual_digest import article


class DigestReviewTests(unittest.TestCase):
    def test_reviewer_sees_both_editions_sources_and_every_evidence_quote(self):
        entry = article()
        body = render({'date': '2026-10-24', 'articles': [entry]})
        for lang in ('en', 'ko'):
            self.assertIn(entry['editions'][lang]['summary'], body)
            for claim in entry['editions'][lang]['claims']:
                for evidence in claim['evidence']:
                    self.assertIn(evidence['quote'], body)
        self.assertIn(entry['url'], body)
        self.assertIn('미게시 초안', body)
        self.assertIn('Merge pull request', body)
        self.assertIn('Files changed', body)

    def test_external_text_cannot_create_mentions_html_or_checkboxes(self):
        entry = copy.deepcopy(article())
        entry['editions']['ko']['title'] = '@youdozi <script>bad</script>\n- [x] approved'
        body = render({'date': '2026-10-24', 'articles': [entry]})
        self.assertNotIn('@youdozi', body)
        self.assertNotIn('<script>', body)
        self.assertNotIn('\n- [x]', body)

    def test_invalid_source_url_stops_pr_creation(self):
        entry = article()
        entry['url'] = 'https://spring.io/\n> forged'
        with self.assertRaises(ValueError):
            render({'date': '2026-10-24', 'articles': [entry]})


if __name__ == '__main__':
    unittest.main()
