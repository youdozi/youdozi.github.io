#!/usr/bin/env python3
"""Generate a Jekyll markdown digest post from curated development RSS feeds."""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
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

ALLOWED_QUERY_PREFIXES = ("id", "p", "q", "v")
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
    "ai": ["ai", "llm", "gpt", "agent", "rag", "inference"],
    "java": ["java", "jdk", "jvm", "spring", "gradle"],
    "cloud": ["kubernetes", "docker", "cloud", "aws", "gcp", "azure"],
    "web": ["react", "next.js", "node", "typescript", "frontend", "backend"],
    "data": ["postgres", "mysql", "redis", "kafka", "data", "analytics"],
    "security": ["security", "cve", "auth", "oauth", "vulnerability"],
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
    "security": "보안 영향이 있을 수 있어 팀 기준 점검 항목으로 정리할 가치가 있습니다.",
    "cloud": "인프라 운영비나 배포 안정성에 바로 영향을 줄 수 있는 주제입니다.",
    "java": "JVM/Spring 기반 프로젝트의 코드/런타임 의사결정에 연결되는 내용입니다.",
    "ai": "개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.",
    "web": "프론트엔드/백엔드 생산성 및 사용자 경험에 직접적인 개선 여지가 있습니다.",
    "data": "데이터 처리량, 조회 성능, 운영 관측성 개선에 참고할 만한 주제입니다.",
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
    return parser.parse_args()


def normalize_url(raw: str) -> str:
    parsed = urlparse(raw.strip())
    kept_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower.startswith(TRACKING_QUERY_PREFIXES):
            continue
        if key_lower.startswith(ALLOWED_QUERY_PREFIXES):
            kept_query.append((key, value))
    query = urlencode(kept_query)
    clean = parsed._replace(fragment="", query=query)
    return urlunparse(clean)


def parse_datetime(text: str) -> Optional[datetime]:
    if not text:
        return None
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
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def collect_topic_tags(title: str, summary: str) -> List[str]:
    corpus = f"{title} {summary}".lower()
    tags: List[str] = []
    for tag, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in corpus for keyword in keywords):
            tags.append(tag)
    return tags


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
        if any(token in text for token in keywords):
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
    except json.JSONDecodeError:
        return {"seen_links": []}
    seen_links = raw.get("seen_links", [])
    if not isinstance(seen_links, list):
        seen_links = []
    return {"seen_links": [str(item) for item in seen_links]}


def write_state(path: Path, seen_links: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen_links": sorted(set(seen_links))[-2000:]}
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
        link_node = entry.find("atom:link", atom_ns)
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
    candidates: List[FeedItem], seen_links: set[str], days_back: int, max_items: int
) -> List[FeedItem]:
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=days_back)

    dedup_title = set()
    selected: List[FeedItem] = []
    for item in sorted(
        candidates, key=lambda x: (x.score, x.published_at), reverse=True
    ):
        if item.published_at < cutoff:
            continue
        if item.link in seen_links:
            continue
        title_key = re.sub(r"[^a-z0-9]+", "", item.title.lower())[:80]
        if title_key in dedup_title:
            continue
        dedup_title.add(title_key)
        selected.append(item)
        if len(selected) >= max_items:
            break
    return selected


def topic_message(item: FeedItem) -> str:
    for tag in item.topic_tags:
        if tag in SUMMARY_RULES:
            return SUMMARY_RULES[tag]
    return "팀 기술 스택 관점에서 변화 포인트를 빠르게 파악하기 좋은 업데이트입니다."


def build_markdown(today_kst: datetime, items: List[FeedItem], tags: List[str]) -> str:
    lines = [
        "---",
        "layout: posts",
        'title: "[dev] 주간 기술 아티클 다이제스트"',
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
            "- 공식 기술 블로그/검증된 매체 RSS 중심으로 수집",
            "- 최신성(최근 7일), 기술 밀도, 중복 여부 기준으로 선별",
            "- 원문 전체 복제 없이 핵심 포인트 + 출처 링크만 정리",
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
                f"- 한줄 요약: {item.summary or '원문 요약이 짧아 제목/메타데이터 중심으로 선별했습니다.'}",
                f"- 왜 중요한가: {topic_message(item)}",
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
            "이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.",
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
        return 0

    state = read_state(state_path)
    seen_links = set(state["seen_links"])

    candidates: List[FeedItem] = []
    for source in QUALITY_SOURCES:
        try:
            xml_text = load_feed(source, fixtures_dir)
            feed_items = parse_feed(xml_text, source.name, int(source.weight))
            candidates.extend(feed_items)
            if fixtures_dir is not None:
                print(f"[ok] {source.name}: {len(feed_items)} items (fixture)")
            else:
                print(f"[ok] {source.name}: {len(feed_items)} items")
        except Exception as exc:
            print(f"[warn] failed to fetch {source.name} ({source.url}): {exc}")

    selected = select_items(
        candidates, seen_links, days_back=args.days_back, max_items=args.max_items
    )
    if not selected:
        print("[skip] No new high-quality items matched the thresholds.")
        return 0

    selected_tags = sorted({tag for item in selected for tag in item.topic_tags})
    if not selected_tags:
        selected_tags = ["dev", "news"]

    markdown = build_markdown(today_kst, selected, selected_tags)
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
