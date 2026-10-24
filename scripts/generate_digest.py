#!/usr/bin/env python3
"""Generate bilingual JSON consumed by Astro. Never render external text as templates."""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import generate_dev_digest as legacy
from ai_dev_digest import AIError
from bilingual_digest import enrich_items
from validate_dev_digest import allowed_article_url, check_article_link


def validate_digest(data, *, now=None, days_back=7, check_links=False, seen_links=None):
    errors = []
    now = now or datetime.now(legacy.KST)
    try:
        published = datetime.fromisoformat(data["publishedAt"])
        if published.tzinfo is None or published > now or data["date"] != published.astimezone(legacy.KST).date().isoformat():
            errors.append("invalid digest publication date")
        collected = datetime.fromisoformat(data.get("updatedAt", data["publishedAt"]))
        if collected.tzinfo is None or collected < published or collected > now or collected.astimezone(legacy.KST).date().isoformat() != data["date"]:
            errors.append("invalid digest update date")
        articles = data["articles"]
        if not isinstance(articles, list) or not 1 <= len(articles) <= 6:
            return errors + ["digest must contain 1–6 articles"]
        seen = set(seen_links or set())
        ids = set()
        for article in articles:
            url = article["url"]
            normalized = legacy.normalize_url(url)
            if normalized in seen or article["id"] in ids:
                errors.append("duplicate article URL or ID")
            seen.add(normalized); ids.add(article["id"])
            if not allowed_article_url(article["source"], url):
                errors.append("article source URL is not approved")
            date = datetime.fromisoformat(article["publishedAt"])
            if date.tzinfo is None or not collected - timedelta(days=days_back) <= date <= collected:
                errors.append("article is future or outside the freshness window")
            if article["verification"] != "source_consistency_checked" or not article["model"]:
                errors.append("article verification is missing")
            documents = article["documents"]
            if not documents:
                errors.append("source documents are missing")
            for language in ("en", "ko"):
                edition = article["editions"][language]
                claims = edition["claims"]
                if not edition["title"] or not isinstance(claims, list) or not 2 <= len(claims) <= 3:
                    errors.append("language title or claims missing")
                if edition["summary"] != " ".join(c["text"] for c in claims):
                    errors.append("summary contains unchecked text")
                if not 80 <= len(edition["summary"]) <= (420 if language == "ko" else 800):
                    errors.append("summary length is outside the language budget")
                for claim in claims:
                    if not claim["evidence"]:
                        errors.append("claim evidence missing")
                    for evidence in claim["evidence"]:
                        i = evidence["document_id"]
                        if type(i) is not int or not 0 <= i < len(documents) or not 20 <= len(evidence["quote"]) <= 240:
                            errors.append("invalid evidence reference")
            if check_links:
                error = check_article_link(article["source"], url)
                if error:
                    errors.append(error)
    except (KeyError, TypeError, ValueError, AttributeError):
        errors.append("invalid bilingual digest structure")
    return errors


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--force", action="store_true")
    mode.add_argument("--append", action="store_true", help="Preserve today's reviewed articles and propose additional items up to six total")
    parser.add_argument("--check-links", action="store_true")
    parser.add_argument("--max-items", type=int, default=6)
    parser.add_argument("--days-back", type=int, default=7)
    parser.add_argument("--min-score", type=int, default=6)
    parser.add_argument("--max-per-source", type=int, default=3)
    parser.add_argument("--github-output")
    parser.add_argument("--fixtures-dir")
    args = parser.parse_args()
    if not 1 <= args.max_items <= 6 or min(args.days_back, args.max_per_source) < 1 or args.min_score < 0:
        parser.error("max-items must be 1–6; day/source limits positive; score nonnegative")
    root = Path(args.repo_root).resolve()
    now = datetime.now(legacy.KST)
    day = now.date().isoformat()
    target = root / "src/content/digests" / f"{day}.json"
    def output(generated):
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as stream:
                stream.write(f"generated={str(generated).lower()}\n")
                if generated:
                    stream.write(f"digest_path={target.relative_to(root).as_posix()}\n")
    if target.exists() and not (args.force or args.append):
        print(f"[skip] Digest already exists: {day}"); output(False); return 0
    try:
        existing = json.loads(target.read_text()) if args.append and target.exists() else None
        retained = existing["articles"] if existing else []
        if existing:
            errors = validate_digest(existing, now=now, days_back=args.days_back)
            if errors:
                raise ValueError("Existing digest is invalid: " + "; ".join(errors))
        capacity = min(args.max_items, 6 - len(retained))
        if capacity <= 0:
            print("[skip] Today's digest already contains six articles"); output(False); return 0
        retained_urls = {legacy.normalize_url(a["url"]) for a in retained}
        state_path = root / ".pipeline/content_state.json"
        seen = {legacy.normalize_url(url) for url in legacy.read_state(state_path)["seen_links"]}
        seen.update(legacy.seen_post_links(root / "_posts/dev/digest", Path("__none__")))
        for file in target.parent.glob("*.json"):
            if file != target:
                seen.update(legacy.normalize_url(a["url"]) for a in json.loads(file.read_text())["articles"])
        seen.update(retained_urls)
        candidates = []
        success = 0
        for source in legacy.QUALITY_SOURCES:
            try:
                feed = legacy.load_feed(source, Path(args.fixtures_dir) if args.fixtures_dir else None)
                items = legacy.parse_feed(feed, source.name, source.weight)
                candidates.extend(items)
                success += bool(items)
                print(f"[ok] {source.name}: {len(items)} items")
            except Exception:
                print(f"[warn] {source.name}: feed unavailable")
        if not success:
            raise ValueError("No feed returned usable items")
        selected = legacy.select_items(candidates, seen, args.days_back, capacity, args.min_score, args.max_per_source)
        counts = {}
        for article in retained:
            counts[article["source"]] = counts.get(article["source"], 0) + 1
        eligible = []
        for candidate in selected:
            if counts.get(candidate.source_name, 0) < args.max_per_source:
                eligible.append(candidate)
                counts[candidate.source_name] = counts.get(candidate.source_name, 0) + 1
        selected = eligible
        if not selected:
            print("[skip] No new eligible articles"); output(False); return 0
        articles = enrich_items(selected)
        if not articles:
            raise ValueError("All bilingual articles were withheld")
        data = {"date": day, "publishedAt": existing["publishedAt"] if existing else now.isoformat(), "articles": retained + articles}
        if existing:
            data["updatedAt"] = now.isoformat()
        errors = validate_digest(data, now=datetime.now(legacy.KST), days_back=args.days_back, check_links=args.check_links, seen_links=seen - retained_urls)
        if errors:
            raise ValueError("; ".join(errors))
        if args.dry_run:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            output(False); return 0
        atomic_json(target, data)
        atomic_json(state_path, {"seen_links": sorted(seen | {legacy.normalize_url(a["url"]) for a in articles})})
        print(f"[done] Wrote {target.relative_to(root)}")
        output(True); return 0
    except (AIError, ValueError, OSError, KeyError, TypeError) as exc:
        print(f"[error] {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
