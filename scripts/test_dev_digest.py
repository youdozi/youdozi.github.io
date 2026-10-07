"""Offline regression tests for collection, selection and publication gates."""
import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import generate_dev_digest as g
import validate_dev_digest as v

DESCRIPTION = "This release updates production defaults and documents migration steps for backend services."


def item(title="Spring Security updates OAuth defaults", source="Spring Blog", link=None, age=1, summary=DESCRIPTION, score=8):
    hosts = {"Spring Blog": "spring.io", "InfoQ": "www.infoq.com", "Cloudflare Blog": "blog.cloudflare.com"}
    return g.FeedItem(source, 3, title, link or f"https://{hosts[source]}/article",
                      datetime.now(g.UTC) - timedelta(hours=age), summary, score,
                      g.collect_topic_tags(title, summary))


class SelectionTests(unittest.TestCase):
    def test_no_substring_topic_matches(self):
        self.assertEqual([], g.collect_topic_tags("daily maintenance", ""))
        self.assertNotIn("ai", g.collect_topic_tags("Cloudflare Containers", ""))
        self.assertNotIn("ai", g.collect_topic_tags("Streamline video processing", ""))

    def test_real_topics_and_plurals(self):
        self.assertIn("ai", g.collect_topic_tags("AI agents and LLMs", ""))
        self.assertIn("java", g.collect_topic_tags("Spring Boot 4", ""))

    def test_security_reason_has_priority_over_data(self):
        article = item("GitLab Vulnerability Enables Data Exfiltration")
        self.assertEqual(g.SUMMARY_RULES["security"], g.topic_message(article))

    def test_java_title_has_priority_over_ai_summary(self):
        article = item("Java News Roundup", summary=DESCRIPTION + " AI agent improvements are included.")
        self.assertEqual(g.SUMMARY_RULES["java"], g.topic_message(article))

    def test_selection_rejects_future_old_short_and_low_score(self):
        candidates = [item(age=-2), item(age=200), item(summary="Tiny."), item(score=1)]
        self.assertEqual([], g.select_items(candidates, set(), 7, 6))

    def test_rejects_promotional_title(self):
        self.assertEqual([], g.select_items([item("AI interns and hiring")], set(), 7, 6))

    def test_dedup_links_in_current_batch_and_seen_state(self):
        a, b = item(), item("Spring JVM release")
        self.assertEqual(1, len(g.select_items([a, b], set(), 7, 6)))
        self.assertEqual([], g.select_items([a], {a.link}, 7, 6))

    def test_source_limit_does_not_backfill(self):
        articles = [item(f"Spring release {n}", link=f"https://spring.io/{n}") for n in range(6)]
        self.assertEqual(3, len(g.select_items(articles, set(), 7, 6)))

    def test_rejects_wrong_host(self):
        self.assertEqual([], g.select_items([item(link="https://example.invalid/news")], set(), 7, 6))

    def test_unicode_titles_are_not_all_collapsed(self):
        a, b = item("스프링 보안 업데이트", link="https://spring.io/a"), item("자바 실행 성능", link="https://spring.io/b")
        a.topic_tags = b.topic_tags = ["java"]
        self.assertEqual(2, len(g.select_items([a, b], set(), 7, 6)))


class ParsingTests(unittest.TestCase):
    def test_entities_and_rss_footer_removed(self):
        text = g.sanitize_text("<p>Release &amp; migration.</p> The post Example appeared first on The GitHub Blog .")
        self.assertEqual("Release & migration.", text)

    def test_infoq_author_credit_does_not_reject_complete_description(self):
        self.assertEqual(DESCRIPTION, g.sanitize_text(DESCRIPTION + " By Susan Chang"))
        self.assertTrue(g.summary_is_complete(g.sanitize_text(DESCRIPTION + " By Siddharth Kodwani, Swaroop Chitlur")))

    def test_truncated_description_is_not_accepted(self):
        self.assertFalse(g.summary_is_complete(DESCRIPTION + "&#8230;"))
        self.assertFalse(g.summary_is_complete(DESCRIPTION + "…"))

    def test_long_description_uses_complete_sentence(self):
        text = g.sanitize_text(DESCRIPTION + " " + "x" * 500)
        self.assertEqual(DESCRIPTION, text)
        self.assertEqual("", g.sanitize_text("x" * 500))

    def test_url_preserves_article_query_and_drops_tracking(self):
        self.assertEqual("https://spring.io/article?article=42&page=2", g.normalize_url("https://spring.io/article?article=42&page=2&utm_source=rss#part"))

    def test_atom_uses_alternate_not_self_link(self):
        xml = f'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Spring Boot release</title><link rel="self" href="https://spring.io/feed"/><link rel="alternate" href="https://spring.io/article"/><updated>2026-10-07T01:00:00.123Z</updated><summary>{DESCRIPTION}</summary></entry></feed>'''
        parsed = g.parse_feed(xml, "Spring Blog", 3)
        self.assertEqual("https://spring.io/article", parsed[0].link)

    def test_state_corruption_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"state.json"
            for text in ("broken", "[]", '{"seen_links": 3}'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    g.read_state(path)

    def test_state_does_not_drop_links_lexicographically(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"state.json"
            links = {f"https://spring.io/{n}" for n in range(2001)}
            g.write_state(path, links)
            self.assertEqual(links, set(g.read_state(path)["seen_links"]))


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(g.KST)
        self.path = Path(self.now.strftime("%Y-%m-%d-dev-digest.markdown"))
        self.post = g.build_markdown(self.now, [item()], ["java", "security"])

    def validate(self, text, **kwargs):
        return v.validate_text(text, self.path, **kwargs)

    def test_valid_post(self):
        self.assertEqual([], self.validate(self.post))

    def test_missing_description_and_date_fail(self):
        import re
        broken = re.sub(r"^- (출처 제공 설명|발행일):.*\n", "", self.post, flags=re.M)
        errors = self.validate(broken)
        self.assertTrue(any("description" in error for error in errors))
        self.assertTrue(any("publication date" in error for error in errors))

    def test_fields_must_belong_to_each_article(self):
        broken = g.build_markdown(self.now, [item(), item("Spring JVM release", link="https://spring.io/b")], ["java"])
        broken = broken.replace("- 출처: Spring Blog", "", 1).replace("- 출처: Spring Blog", "- 출처: Spring Blog\n- 출처: Spring Blog", 1)
        self.assertTrue(self.validate(broken))

    def test_non_whitelisted_domain_fails(self):
        self.assertTrue(self.validate(self.post.replace("spring.io", "example.invalid")))

    def test_duplicate_url_fails(self):
        post = g.build_markdown(self.now, [item(), item("Spring JVM release")], ["java"])
        self.assertTrue(any("duplicate article URL" in e for e in self.validate(post)))

    def test_historical_duplicate_fails(self):
        self.assertTrue(self.validate(self.post, seen_links={"https://spring.io/article"}))

    def test_future_and_stale_article_dates_fail(self):
        for age in (-24, 200):
            post = g.build_markdown(self.now, [item(age=age)], ["java"])
            self.assertTrue(any("freshness" in e for e in self.validate(post)))

    def test_entities_and_boilerplate_fail(self):
        for suffix in ("&amp;", " The post Example appeared first on Blog."):
            self.assertTrue(self.validate(self.post.replace(DESCRIPTION, DESCRIPTION + suffix)))

    def test_link_label_must_match_target(self):
        self.assertTrue(self.validate(self.post.replace("](" + "https://spring.io/article", "](https://spring.io/other")))

    def test_link_network_failure_blocks_publication(self):
        with patch.object(v, "urlopen", side_effect=TimeoutError("network down")):
            self.assertTrue(self.validate(self.post, check_links=True))

    def test_successful_html_link(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.status = 200
        response.geturl.return_value = "https://spring.io/article"
        response.headers.get_content_type.return_value = "text/html"
        with patch.object(v, "urlopen") as request:
            request.return_value.__enter__.return_value = response
            self.assertIsNone(v.check_article_link("Spring Blog", "https://spring.io/article"))
            response.geturl.return_value = "https://example.invalid/article"
            self.assertIsNotNone(v.check_article_link("Spring Blog", "https://spring.io/article"))
            response.geturl.return_value = "https://spring.io/article"
            response.headers.get_content_type.return_value = "application/json"
            self.assertIsNotNone(v.check_article_link("Spring Blog", "https://spring.io/article"))


class PipelineTests(unittest.TestCase):
    def run_generator(self, root, *, load=None, extra=None):
        argv = ["digest", "--repo-root", str(root), "--github-output", str(root/"output")] + (extra or [])
        with patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            if load is None:
                return g.main()
            with patch.object(g, "load_feed", side_effect=load):
                return g.main()

    def feed(self, age=1):
        date = (datetime.now(g.UTC) - timedelta(hours=age)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        return f"<rss><channel><item><title>Spring Boot release</title><link>https://spring.io/article</link><pubDate>{date}</pubDate><description>{DESCRIPTION}</description></item></channel></rss>"

    def test_all_feeds_fail_returns_error_and_no_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(1, self.run_generator(root, load=OSError("offline")))
            self.assertFalse((root/"_posts").exists())
            self.assertFalse((root/".pipeline/content_state.json").exists())

    def test_no_candidates_skips_without_validating_old_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, self.run_generator(root, load=lambda *_: self.feed(age=200)))
            self.assertEqual("generated=false\n", (root/"output").read_text())
            self.assertFalse((root/".pipeline").exists())

    def test_generate_then_rerun_emits_exact_path_and_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, self.run_generator(root, load=lambda *_: self.feed()))
            posts = list((root/"_posts/dev/digest").glob("*.markdown"))
            self.assertEqual(1, len(posts))
            self.assertEqual([], v.validate_post(posts[0], 1))
            self.assertIn(f"post_path={posts[0].relative_to(root).as_posix()}", (root/"output").read_text())
            self.assertEqual(0, self.run_generator(root))
            self.assertTrue((root/"output").read_text().endswith("generated=false\n"))

    def test_failed_link_check_does_not_write_post_or_state(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(v, "check_article_link", return_value="HTTP 404"):
            root = Path(tmp)
            self.assertEqual(1, self.run_generator(root, load=lambda *_: self.feed(), extra=["--check-links"]))
            self.assertFalse((root/"_posts").exists())
            self.assertFalse((root/".pipeline").exists())

    def test_history_prevents_republish_when_state_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            posts = root/"_posts/dev/digest"
            posts.mkdir(parents=True)
            (posts/"2020-01-01-dev-digest.markdown").write_text("- 링크: [https://spring.io/article](https://spring.io/article)\n")
            self.assertEqual(0, self.run_generator(root, load=lambda *_: self.feed()))
            self.assertEqual(1, len(list(posts.glob("*.markdown"))))


if __name__ == "__main__":
    unittest.main()
