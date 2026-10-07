#!/usr/bin/env python3
"""Validate each digest article before it can be committed."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

KST = timezone(timedelta(hours=9))
SOURCE_HOSTS = {
    "GitHub Changelog": {"github.blog"},
    "InfoQ": {"www.infoq.com", "infoq.com"},
    "JetBrains Blog": {"blog.jetbrains.com"},
    "Spring Blog": {"spring.io"},
    "Cloudflare Blog": {"blog.cloudflare.com"},
}
REQUIRED_SECTIONS = ["## 이번 다이제스트 기준", "## 핵심 아티클", "## 활용 가이드"]


def allowed_article_url(source: str, url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (parsed.scheme == "https" and parsed.hostname in SOURCE_HOSTS.get(source, set())
                and parsed.port in (None, 443) and not parsed.username and not parsed.password
                and not re.search(r"[\s<>\\]", url))
    except ValueError:
        return False


def check_article_link(source: str, url: str) -> str | None:
    if not allowed_article_url(source, url):
        return "URL must use HTTPS on the declared source's approved host"
    try:
        request = Request(url, headers={"User-Agent": "youdozi-dev-digest-bot/1.0"})
        with urlopen(request, timeout=20) as response:
            if not allowed_article_url(source, response.geturl()):
                return "article redirected outside its approved source"
            if response.status != 200:
                return f"article returned HTTP {response.status}"
            if response.headers.get_content_type() not in ("text/html", "application/xhtml+xml"):
                return "article did not return an HTML document"
    except Exception as exc:
        return f"article link could not be verified: {exc}"
    return None


def split_front_matter(text: str) -> Tuple[Dict[str, List[str] | str], str]:
    if not text.startswith("---\n"):
        raise ValueError("front matter opening delimiter is missing")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError("front matter closing delimiter is missing")
    _, raw, body = parts
    data: Dict[str, List[str] | str] = {}
    list_key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if list_key is None or not isinstance(data.get(list_key), list):
                raise ValueError(f"list item without list key: {line}")
            data[list_key].append(line[4:].strip())
            continue
        if ":" not in line:
            raise ValueError(f"invalid front matter line: {line}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in data:
            raise ValueError(f"duplicate front matter key: {key}")
        data[key] = value.strip('"') if value else []
        list_key = key
    return data, body


def validate_text(text: str, path: Path, min_items: int = 1, *, days_back: int = 7,
                  check_links: bool = False, seen_links: set[str] | None = None) -> List[str]:
    from generate_dev_digest import normalize_url, summary_is_complete

    errors: List[str] = []
    try:
        metadata, body = split_front_matter(text)
    except ValueError as exc:
        return [str(exc)]
    if metadata.get("layout") != "posts":
        errors.append("layout must be 'posts'")
    categories = metadata.get("categories", [])
    if not isinstance(categories, list) or not {"dev", "digest"}.issubset(categories):
        errors.append("categories must include 'dev' and 'digest'")
    if not isinstance(metadata.get("tags"), list) or not metadata["tags"]:
        errors.append("tags must be a non-empty list")
    if metadata.get("generated_by") != "content-pipeline":
        errors.append("generated_by must be 'content-pipeline'")
    if not metadata.get("title"):
        errors.append("title is required")
    post_date = None
    try:
        post_date = datetime.strptime(str(metadata.get("date", "")), "%Y-%m-%d %H:%M:%S %z")
        if post_date > datetime.now(KST):
            errors.append("post date cannot be in the future")
        if path.name != post_date.strftime("%Y-%m-%d-dev-digest.markdown"):
            errors.append("filename must match the post date")
    except ValueError:
        errors.append("post date must include a valid date, time and timezone")
    for section in REQUIRED_SECTIONS:
        if body.count(section) != 1:
            errors.append(f"section must occur exactly once: {section}")
    matches = list(re.finditer(r"^### (\d+)\. (.+)$", body, re.M))
    if len(matches) < min_items:
        errors.append(f"expected at least {min_items} articles, found {len(matches)}")
    if [int(m[1]) for m in matches] != list(range(1, len(matches) + 1)):
        errors.append("article numbers must be consecutive from 1")
    local_links: set[str] = set()
    titles: set[str] = set()
    for index, match in enumerate(matches):
        label = f"article {index + 1}"
        title_key = re.sub(r"[^\w]+", "", match[2].casefold())
        if title_key in titles:
            errors.append(f"{label}: duplicate title")
        titles.add(title_key)
        end = matches[index + 1].start() if index + 1 < len(matches) else body.find("## 활용 가이드", match.end())
        block = body[match.end():end if end != -1 else len(body)]
        fields: dict[str, str] = {}
        for key, value in re.findall(r"^- ([^:]+):\s*(.*)$", block, re.M):
            if key in fields:
                errors.append(f"{label}: duplicate field {key}")
            fields[key] = value.strip()
        # Read older posts too, but enforce the same per-article checks.
        summary = fields.get("출처 제공 설명", fields.get("한줄 요약", ""))
        reason = fields.get("확인할 점", fields.get("왜 중요한가", ""))
        if not summary_is_complete(summary):
            errors.append(f"{label}: description must be 80–420 characters and end as a complete sentence")
        if re.search(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);", summary):
            errors.append(f"{label}: description contains unresolved HTML entities")
        if "appeared first on" in summary.lower():
            errors.append(f"{label}: description contains RSS boilerplate")
        if not reason:
            errors.append(f"{label}: explanation is required")
        source = fields.get("출처", "")
        if source not in SOURCE_HOSTS:
            errors.append(f"{label}: unknown source")
        try:
            published = datetime.strptime(fields.get("발행일", ""), "%Y-%m-%d %H:%M (KST)").replace(tzinfo=KST)
            if post_date and not post_date - timedelta(days=days_back, minutes=1) <= published <= post_date:
                errors.append(f"{label}: publication date is future or outside the freshness window")
        except ValueError:
            errors.append(f"{label}: valid publication date is required")
        link_match = re.fullmatch(r"\[(https://[^\]]+)\]\((https://[^)]+)\)", fields.get("링크", ""))
        if not link_match or link_match[1] != link_match[2]:
            errors.append(f"{label}: matching HTTPS link text and target are required")
            continue
        link = link_match[2]
        if not allowed_article_url(source, link):
            errors.append(f"{label}: URL must match its approved source host")
            continue
        normalized = normalize_url(link)
        if normalized in local_links or normalized in (seen_links or set()):
            errors.append(f"{label}: duplicate article URL")
        local_links.add(normalized)
        if check_links:
            error = check_article_link(source, link)
            if error:
                errors.append(f"{label}: {error}")
    return errors


def validate_post(path: Path, min_items: int, **kwargs) -> List[str]:
    if not path.exists():
        return [f"post does not exist: {path}"]
    return validate_text(path.read_text(encoding="utf-8"), path, min_items, **kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("post_path")
    parser.add_argument("--min-items", type=int, default=1)
    parser.add_argument("--days-back", type=int, default=7)
    parser.add_argument("--check-links", action="store_true")
    args = parser.parse_args()
    if min(args.min_items, args.days_back) < 1:
        parser.error("min-items and days-back must be positive")
    errors = validate_post(Path(args.post_path).resolve(), args.min_items,
                           days_back=args.days_back, check_links=args.check_links)
    for error in errors:
        print(f"[error] {error}")
    if not errors:
        print(f"[ok] validated {args.post_path}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
