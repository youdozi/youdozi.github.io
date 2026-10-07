"""Offline AI tests: evidence and publication decisions must fail closed."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import ai_dev_digest as ai
import generate_dev_digest as g
import validate_dev_digest as v
from test_dev_digest import item, DESCRIPTION
import test_dev_digest as base

BODY = "Spring Security now requires explicit OAuth scopes for service accounts. This update is in public preview, not generally available. " * 6
CLAIMS = [
    {"text_ko": "Spring Security는 서비스 계정에 명시적인 OAuth 범위를 요구한다고 발표했습니다.", "evidence": [{"document_id": 0, "quote": "requires explicit OAuth scopes for service accounts"}]},
    {"text_ko": "이번 업데이트는 공개 프리뷰 단계이며 정식 출시된 상태는 아니라고 설명합니다.", "evidence": [{"document_id": 0, "quote": "in public preview, not generally available"}]},
]


class ExtractionTests(unittest.TestCase):
    def test_extracts_article_omits_navigation_and_script(self):
        parser = ai.ArticleParser()
        parser.feed(f"<nav>ignore</nav><main><article><p>{BODY}</p><script>ignore</script><a href='/release'>release</a></article></main><footer>ignore</footer>")
        self.assertNotIn("ignore", parser.extract())
        self.assertIn("OAuth scopes", parser.extract())
        self.assertEqual(["/release"], parser.links)

    def test_no_full_page_fallback(self):
        parser = ai.ArticleParser();parser.feed(f"<div>{BODY}</div>")
        self.assertEqual("", parser.extract())

    def test_fetch_rejects_unapproved_url_without_request(self):
        with patch.object(ai, "urlopen") as request:
            with self.assertRaises(ai.ArticleUnavailable):
                ai.fetch_document("https://example.invalid/article", ai.PRIMARY_HOSTS)
            request.assert_not_called()


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.docs = [ai.Document("https://spring.io/blog/release", BODY, [])]
        self.claims = json.loads(json.dumps(CLAIMS))

    def test_valid_korean_summary(self):
        self.assertIn("공개 프리뷰", ai.verify_claims(self.claims, self.docs, True))

    def test_invented_quote_rejected(self):
        self.claims[0]["evidence"][0]["quote"] = "This fabricated quote is not in the article"
        with self.assertRaises(ai.ArticleUnavailable):
            ai.verify_claims(self.claims, self.docs, False)

    def test_unknown_document_id_rejected(self):
        self.claims[0]["evidence"][0]["document_id"] = 7
        with self.assertRaises(ai.ArticleUnavailable):
            ai.verify_claims(self.claims, self.docs, False)

    def test_sensitive_claim_requires_primary_source(self):
        self.docs[0].url = "https://www.infoq.com/news/example"
        with self.assertRaises(ai.ArticleUnavailable):
            ai.verify_claims(self.claims, self.docs, True)

    def test_liquid_or_markdown_injection_rejected(self):
        self.claims[0]["text_ko"] += " {{ site.secret }}."
        with self.assertRaises(ai.ArticleUnavailable):
            ai.verify_claims(self.claims, self.docs, False)

    def test_non_korean_summary_rejected(self):
        self.claims[0]["text_ko"] = DESCRIPTION
        with self.assertRaises(ai.ArticleUnavailable):
            ai.verify_claims(self.claims, self.docs, False)

    def test_reviewer_can_reject_matching_but_misleading_quote(self):
        client = MagicMock()
        client.generate.side_effect = [{"claims": self.claims}, {"supported": False, "requires_official": True, "claims": [{"index": 0, "supported": True}, {"index": 1, "supported": False}]}]
        with patch.object(ai, "fetch_document", return_value=self.docs[0]):
            with self.assertRaises(ai.ArticleUnavailable):
                ai.summarize_item(item(), client)
        self.assertEqual(2, client.generate.call_count)

    def test_accepted_summary_has_hashes_and_checked_scope(self):
        client = MagicMock()
        client.generate.side_effect = [{"claims": self.claims}, {"supported": True, "requires_official": True, "claims": [{"index": 0, "supported": True}, {"index": 1, "supported": True}]}]
        with patch.object(ai, "fetch_document", return_value=self.docs[0]):
            result = ai.summarize_item(item(), client)
        self.assertEqual("source_consistency_checked", result["verification"])
        self.assertEqual(64, len(result["documents"][0]["sha256"]))
        self.assertNotIn("body", result["documents"][0])
        article = item()
        post = g.build_markdown(datetime.now(g.KST), [article], ["java"], {article.link: result})
        path = Path(datetime.now(g.KST).strftime("%Y-%m-%d-dev-digest.markdown"))
        self.assertEqual([], v.validate_text(post, path))
        self.assertIn("한국어 AI 요약", post)

    def test_secondary_sensitive_article_without_official_reference_is_withheld(self):
        self.docs[0].url = "https://www.infoq.com/news/example"
        client = MagicMock()
        with patch.object(ai, "fetch_document", return_value=self.docs[0]):
            with self.assertRaises(ai.ArticleUnavailable):
                ai.summarize_item(item(source="InfoQ"), client)
        client.generate.assert_not_called()


class APITests(unittest.TestCase):
    def test_missing_key_fails_without_network(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaises(ai.AIError):
                ai.Gemini()

    def test_quota_error_does_not_leak_key_or_retry(self):
        secret = "test-secret-not-real"
        with patch.dict(os.environ, {"GEMINI_API_KEY": secret}), patch.object(ai, "urlopen", side_effect=HTTPError("https://api.test", 429, secret, None, None)) as request:
            client = ai.Gemini()
            with self.assertRaises(ai.AIError) as error:
                client.generate("summarize", {}, ai.CLAIM_SCHEMA)
            self.assertNotIn(secret, str(error.exception))
            self.assertIn("429", str(error.exception))
            self.assertEqual(1, request.call_count)
            sent = request.call_args[0][0]
            self.assertNotIn(secret, sent.full_url)
            self.assertEqual(secret, sent.get_header("X-goog-api-key"))

    def test_api_call_budget(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}), patch.object(ai, "urlopen") as request:
            client = ai.Gemini();client.calls = 12
            with self.assertRaises(ai.AIError):
                client.generate("summarize", {}, ai.CLAIM_SCHEMA)
            request.assert_not_called()

    def test_incomplete_json_output_rejected(self):
        response = MagicMock()
        response.read.return_value = json.dumps({"candidates": [{"finishReason": "MAX_TOKENS"}]}).encode()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}), patch.object(ai, "urlopen") as request:
            request.return_value.__enter__.return_value = response
            with self.assertRaises(ai.AIError):
                ai.Gemini().generate("summarize", {}, ai.CLAIM_SCHEMA)

    def test_ai_failure_does_not_write_post_or_state(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(ai, "enrich_items", side_effect=ai.AIError("quota exhausted")):
            root = Path(tmp)
            runner = base.PipelineTests()
            self.assertEqual(1, runner.run_generator(root, load=lambda *_: runner.feed(), extra=["--ai"]))
            self.assertFalse((root/"_posts").exists())
            self.assertFalse((root/".pipeline").exists())


if __name__ == "__main__":
    unittest.main()
