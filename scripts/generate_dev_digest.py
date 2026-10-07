#!/usr/bin/env python3
"""Generate a Jekyll markdown digest post from curated development RSS feeds."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


KST = timezone(timedelta(hours=9))
UTC = timezone.utc

TRACKING_QUERY_PREFIXES = (
    "utm_",
    "fbclid",
    "gclid",
    "ref",
    "source",
    "mkt_",
    "mc_",
)

@dataclass
class FeedItem:
    source_name: str
    source_weight: int
    title: str
    link: str
    published_at: datetime
    summary: str
    score: int
    topic_tags: List[str]


@dataclass(frozen=True)
class FeedSource:
    slug: str
    name: str
    url: str
    weight: int


TOPIC_KEYWORDS = {
    "ai": ["ai", "llm", "gpt", "agent", "rag", "inference", "copilot"],
    "java": ["java", "jdk", "jvm", "spring", "gradle"],
    "cloud": ["kubernetes", "docker", "cloud", "aws", "gcp", "azure", "cloudflare", "container", "istio"],
    "web": ["react", "next.js", "node", "typescript", "frontend", "backend"],
    "data": ["postgres", "mysql", "redis", "kafka", "data", "analytics"],
    "security": ["security", "cve", "auth", "oauth", "vulnerability", "exfiltration", "exposure", "tls", "certificate"],
}

QUALITY_SOURCES = [
    FeedSource(
        slug="github-changelog",
        name="GitHub Changelog",
        url="https://github.blog/changelog/feed/",
        weight=3,
    ),
    FeedSource(
        slug="infoq",
        name="InfoQ",
        url="https://feed.infoq.com/",
        weight=3,
    ),
    FeedSource(
        slug="jetbrains",
        name="JetBrains Blog",
        url="https://blog.jetbrains.com/feed/",
        weight=2,
    ),
    FeedSource(
        slug="spring",
        name="Spring Blog",
        url="https://spring.io/blog.atom",
        weight=3,
    ),
    FeedSource(
        slug="cloudflare",
        name="Cloudflare Blog",
        url="https://blog.cloudflare.com/rss/",
        weight=2,
    ),
]

SUMMARY_RULES = {
    "security": "적용 제품과 영향받는 버전, 수정 또는 완화 조치를 원문에서 확인하세요.",
    "cloud": "배포·운영 구성의 변경점과 호환성, 비용 조건을 원문에서 확인하세요.",
    "java": "지원하는 JDK/Spring 버전과 업그레이드 시 호환성·마이그레이션 사항을 확인하세요.",
    "ai": "모델·도구의 지원 범위와 평가 결과, 사용 제약을 원문에서 확인하세요.",
    "web": "사용 중인 프레임워크 버전과 API 변경, 마이그레이션 필요 여부를 확인하세요.",
    "data": "적용 데이터 시스템과 성능 측정 조건, 운영상 제한 사항을 확인하세요.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a dev digest markdown post.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument(
        "--max-items", type=int, default=6, help="Maximum selected items"
    )
    parser.add_argument(
        "--days-back", type=int, default=7, help="Only include items within N days"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite today's digest if exists"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print candidate result only"
    )
    parser.add_argument(
        "--state-file",
        default=".pipeline/content_state.json",
        help="State file for processed links",
    )
    parser.add_argument(
        "--fixtures-dir",
        default=None,
        help="Directory containing local RSS/Atom fixture files for offline validation",
    )
    parser.add_argument("--min-score", type=int, default=6)
    parser.add_argument("--max-per-source", type=int, default=3)
    parser.add_argument("--check-links", action="store_true", help="Require selected article URLs to respond with HTML over HTTPS")
    parser.add_argument("--github-output", help="Append generated/post_path outputs to this GitHub Actions output file")
    args = parser.parse_args()
    if min(args.max_items, args.days_back, args.max_per_source) < 1 or args.min_score < 0:
        parser.error("item/day/source limits must be positive; min-score must be non-negative")
    return args


def normalize_url(raw: str) -> str:
    parsed = urlparse(raw.strip())
    kept_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower.startswith(TRACKING_QUERY_PREFIXES):
            continue
        kept_query.append((key, value))
    query = urlencode(kept_query)
    clean = parsed._replace(fragment="", query=query)
    return urlunparse(clean)


def parse_datetime(text: str) -> Optional[datetime]:
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)
    except ValueError:
        pass
    candidates = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S%z",
    ]
    for fmt in candidates:
        try:
            dt = datetime.strptime(text.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC)
        except ValueError:
            continue
    try:
        dt = parsedate_to_datetime(text)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except (TypeError, ValueError):
        return None


def sanitize_text(value: str, max_length: int = 420) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*The post .*? appeared first on .*?$", "", text, flags=re.I).strip()
    text = re.sub(r"\s+By [A-Z][\w’'-]+(?:[ ,]+[A-Z][\w’'-]+)+\.?$", "", text).strip()
    if len(text) <= max_length:
        return text
    # Preserve complete sentences; reject an excerpt if its first sentence is too long.
    prefix = text[:max_length]
    endings = list(re.finditer(r"[.!?](?=\s|$)", prefix))
    return prefix[:endings[-1].end()] if endings else ""


def keyword_matches(text: str, keyword: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(keyword) + r"s?(?!\w)", text.lower()) is not None


def collect_topic_tags(title: str, summary: str) -> List[str]:
    corpus = f"{title} {summary}".lower()
    return [tag for tag, keywords in TOPIC_KEYWORDS.items()
            if any(keyword_matches(corpus, keyword) for keyword in keywords)]


def summary_is_complete(summary: str) -> bool:
    return (80 <= len(summary) <= 420
            and not summary.rstrip().endswith(("…", "..."))
            and re.search(r"[.!?。]$", summary) is not None)


PROMOTIONAL_TITLE = re.compile(r"\b(interns?|hiring|careers?|webinars?|sponsored|giveaway)\b", re.I)


def score_item(
    source_weight: int, published_at: datetime, title: str, summary: str
) -> int:
    now = datetime.now(UTC)
    age_hours = (now - published_at).total_seconds() / 3600
    score = source_weight

    if age_hours <= 24:
        score += 3
    elif age_hours <= 72:
        score += 2
    elif age_hours <= 24 * 7:
        score += 1

    text = f"{title} {summary}".lower()
    for keywords in TOPIC_KEYWORDS.values():
        if any(keyword_matches(text, token) for token in keywords):
            score += 1

    if len(summary) >= 120:
        score += 1

    if any(bad in text for bad in ["sponsored", "webinar", "promo", "advert"]):
        score -= 2

    return max(0, score)


def read_state(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {"seen_links": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid deduplication state: {path}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"invalid deduplication state: {path}")
    seen_links = raw.get("seen_links", [])
    if not isinstance(seen_links, list):
        raise ValueError(f"invalid seen_links list: {path}")
    return {"seen_links": [str(item) for item in seen_links]}


def write_state(path: Path, seen_links: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen_links": sorted(set(seen_links))}
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def parse_feed(xml_text: str, source_name: str, source_weight: int) -> List[FeedItem]:
    root = ET.fromstring(xml_text)
    items: List[FeedItem] = []

    for node in root.findall(".//item"):
        title = sanitize_text(node.findtext("title", ""), max_length=180)
        link = node.findtext("link", "")
        published = node.findtext("pubDate", "") or node.findtext("date", "")
        summary = sanitize_text(node.findtext("description", ""))
        dt = parse_datetime(published)
        if not title or not link or dt is None:
            continue
        clean_link = normalize_url(link)
        tags = collect_topic_tags(title, summary)
        score = score_item(source_weight, dt, title, summary)
        items.append(
            FeedItem(
                source_name=source_name,
                source_weight=source_weight,
                title=title,
                link=clean_link,
                published_at=dt,
                summary=summary,
                score=score,
                topic_tags=tags,
            )
        )

    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", atom_ns):
        title = sanitize_text(
            entry.findtext("atom:title", default="", namespaces=atom_ns), max_length=180
        )
        link_node = next((node for node in entry.findall("atom:link", atom_ns)
                          if node.attrib.get("rel", "alternate") == "alternate"), None)
        link = link_node.attrib.get("href", "") if link_node is not None else ""
        published = entry.findtext(
            "atom:published", "", namespaces=atom_ns
        ) or entry.findtext("atom:updated", "", namespaces=atom_ns)
        summary = sanitize_text(entry.findtext("atom:summary", "", namespaces=atom_ns))
        if not summary:
            summary = sanitize_text(
                entry.findtext("atom:content", "", namespaces=atom_ns)
            )
        dt = parse_datetime(published)
        if not title or not link or dt is None:
            continue
        clean_link = normalize_url(link)
        tags = collect_topic_tags(title, summary)
        score = score_item(source_weight, dt, title, summary)
        items.append(
            FeedItem(
                source_name=source_name,
                source_weight=source_weight,
                title=title,
                link=clean_link,
                published_at=dt,
                summary=summary,
                score=score,
                topic_tags=tags,
            )
        )

    return items


def fetch_feed(url: str) -> str:
    req = Request(url, headers={"User-Agent": "youdozi-dev-digest-bot/1.0"})
    insecure_ssl = os.getenv("PIPELINE_INSECURE_SSL", "false").lower() == "true"
    context = (
        ssl._create_unverified_context()
        if insecure_ssl
        else ssl.create_default_context()
    )
    with urlopen(req, timeout=20, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def load_feed(source: FeedSource, fixtures_dir: Optional[Path]) -> str:
    if fixtures_dir is not None:
        fixture_path = fixtures_dir / f"{source.slug}.xml"
        return fixture_path.read_text(encoding="utf-8")
    return fetch_feed(source.url)


def select_items(
    candidates: List[FeedItem], seen_links: set[str], days_back: int, max_items: int,
    min_score: int = 6, max_per_source: int = 3,
) -> List[FeedItem]:
    from validate_dev_digest import allowed_article_url

    now = datetime.now(UTC)
    cutoff = now - timedelta(days=days_back)
    dedup_title: set[str] = set()
    dedup_links = set(seen_links)
    source_counts: Dict[str, int] = {}
    selected: List[FeedItem] = []
    for item in sorted(candidates, key=lambda x: (x.score, x.published_at), reverse=True):
        if not cutoff <= item.published_at <= now:
            continue
        if (item.score < min_score or not item.topic_tags
                or not summary_is_complete(item.summary)
                or PROMOTIONAL_TITLE.search(item.title)
                or not allowed_article_url(item.source_name, item.link)):
            continue
        if item.link in dedup_links or source_counts.get(item.source_name, 0) >= max_per_source:
            continue
        title_key = re.sub(r"[^\w]+", "", item.title.casefold())
        if title_key in dedup_title:
            continue
        dedup_title.add(title_key)
        dedup_links.add(item.link)
        source_counts[item.source_name] = source_counts.get(item.source_name, 0) + 1
        selected.append(item)
        if len(selected) >= max_items:
            break
    return selected


def topic_message(item: FeedItem) -> str:
    # Prefer the headline topic, then security, before broad supporting keywords.
    tags = collect_topic_tags(item.title, "") or item.topic_tags
    for tag in ("security", "java", "cloud", "data", "web", "ai"):
        if tag in tags:
            return SUMMARY_RULES[tag]
    return "원문에서 적용 대상과 제한 사항을 확인하세요."


def seen_post_links(posts_dir: Path, excluding: Path) -> set[str]:
    links: set[str] = set()
    for post in posts_dir.glob("*-dev-digest.markdown"):
        if post == excluding:
            continue
        text = post.read_text(encoding="utf-8")
        links.update(normalize_url(link) for link in re.findall(r"^- 링크: \[([^\]]+)\]", text, re.M))
    return links


def emit_outputs(args: argparse.Namespace, generated: bool, path: Path) -> None:
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as output:
            output.write(f"generated={str(generated).lower()}\n")
            if generated:
                output.write(f"post_path={path.relative_to(Path(args.repo_root).resolve()).as_posix()}\n")


def build_markdown(today_kst: datetime, items: List[FeedItem], tags: List[str]) -> str:
    lines = [
        "---",
        "layout: posts",
        f'title: "[dev] {today_kst.strftime("%Y-%m-%d")} 개발 뉴스 다이제스트"',
        f"date: {today_kst.strftime('%Y-%m-%d %H:%M:%S')} +0900",
        "categories:",
        "  - dev",
        "  - digest",
        "tags:",
    ]
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.extend(
        [
            "generated_by: content-pipeline",
            'disclaimer: "원문을 재배포하지 않고 핵심 포인트와 링크만 제공합니다."',
            "---",
            "",
            "## 이번 다이제스트 기준",
            "",
            "- 공식 기술 블로그와 기술 매체 RSS에서 수집",
            "- 최신성, 기술 키워드, 최소 점수, 출처별 최대 개수와 중복 여부로 선별",
            "- RSS 제공 설명을 정리해 싣습니다. 번역 및 원문 사실 검증은 수행하지 않습니다.",
            "",
            "## 핵심 아티클",
            "",
        ]
    )

    for idx, item in enumerate(items, start=1):
        lines.extend(
            [
                f"### {idx}. {item.title}",
                "",
                f"- 출처: {item.source_name}",
                f"- 발행일: {item.published_at.astimezone(KST).strftime('%Y-%m-%d %H:%M')} (KST)",
                f"- 링크: [{item.link}]({item.link})",
                f"- 출처 제공 설명: {item.summary}",
                f"- 확인할 점: {topic_message(item)}",
                "",
            ]
        )

    lines.extend(
        [
            "## 활용 가이드",
            "",
            "1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.",
            "2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.",
            "",
            "---",
            "이 글은 자동 수집됩니다. 분류와 확인할 점은 규칙 기반 안내이며, 세부 사실과 적용 여부는 원문에서 확인하세요.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    posts_dir = repo_root / "_posts" / "dev" / "digest"
    state_path = repo_root / args.state_file
    fixtures_dir = Path(args.fixtures_dir).resolve() if args.fixtures_dir else None

    today_kst = datetime.now(KST)
    file_name = f"{today_kst.strftime('%Y-%m-%d')}-dev-digest.markdown"
    target_post = posts_dir / file_name

    if target_post.exists() and not args.force:
        print(f"[skip] Digest already exists: {target_post}")
        emit_outputs(args, False, target_post)
        return 0

    state = read_state(state_path)
    seen_links = {normalize_url(link) for link in state["seen_links"]}
    historical_links = seen_post_links(posts_dir, target_post)
    seen_links.update(historical_links)

    candidates: List[FeedItem] = []
    successful_sources = 0
    for source in QUALITY_SOURCES:
        try:
            xml_text = load_feed(source, fixtures_dir)
            feed_items = parse_feed(xml_text, source.name, int(source.weight))
            candidates.extend(feed_items)
            if feed_items:
                successful_sources += 1
            if fixtures_dir is not None:
                print(f"[ok] {source.name}: {len(feed_items)} items (fixture)")
            else:
                print(f"[ok] {source.name}: {len(feed_items)} items")
        except Exception as exc:
            print(f"[warn] failed to fetch {source.name} ({source.url}): {exc}")

    if successful_sources == 0:
        print("[error] No feed returned usable items.", file=sys.stderr)
        return 1
    selected = select_items(
        candidates, seen_links, days_back=args.days_back, max_items=args.max_items,
        min_score=args.min_score, max_per_source=args.max_per_source,
    )
    if not selected:
        print("[skip] No new items matched the quality thresholds.")
        emit_outputs(args, False, target_post)
        return 0

    selected_tags = sorted({tag for item in selected for tag in item.topic_tags})
    if not selected_tags:
        selected_tags = ["dev", "news"]

    markdown = build_markdown(today_kst, selected, selected_tags)
    from validate_dev_digest import validate_text
    errors = validate_text(markdown, target_post, min_items=1,
                           days_back=args.days_back, check_links=args.check_links,
                           seen_links=historical_links)
    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1
    print(f"[info] selected {len(selected)} items")

    if args.dry_run:
        print("[dry-run] Post preview")
        print("-" * 72)
        print(markdown[:2500])
        print("-" * 72)
    else:
        posts_dir.mkdir(parents=True, exist_ok=True)
        target_post.write_text(markdown, encoding="utf-8")
        seen_links.update(item.link for item in selected)
        write_state(state_path, seen_links)
        print(f"[done] wrote {target_post}")
        print(f"[done] updated {state_path}")
        emit_outputs(args, True, target_post)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
