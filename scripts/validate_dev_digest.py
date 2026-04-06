#!/usr/bin/env python3
"""Validate generated Jekyll markdown digest posts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_SECTIONS = [
    "## 이번 다이제스트 기준",
    "## 핵심 아티클",
    "## 활용 가이드",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated dev digest post.")
    parser.add_argument("post_path", help="Path to the generated markdown post")
    parser.add_argument(
        "--min-items", type=int, default=1, help="Minimum number of article sections"
    )
    return parser.parse_args()


def split_front_matter(text: str) -> Tuple[Dict[str, List[str] | str], str]:
    if not text.startswith("---\n"):
        raise ValueError("front matter opening delimiter is missing")

    try:
        _, raw_front_matter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("front matter closing delimiter is missing") from exc

    data: Dict[str, List[str] | str] = {}
    current_list_key: str | None = None

    for line in raw_front_matter.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"list item without key: {line}")
            value = line[4:].strip()
            data.setdefault(current_list_key, [])
            assert isinstance(data[current_list_key], list)
            data[current_list_key].append(value)
            continue
        if ":" not in line:
            raise ValueError(f"invalid front matter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        current_list_key = key
        if value:
            data[key] = value
        else:
            data[key] = []

    return data, body


def validate_post(path: Path, min_items: int) -> List[str]:
    errors: List[str] = []
    if not path.exists():
        return [f"post does not exist: {path}"]

    text = path.read_text(encoding="utf-8")

    try:
        front_matter, body = split_front_matter(text)
    except ValueError as exc:
        return [str(exc)]

    if front_matter.get("layout") != "posts":
        errors.append("layout must be 'posts'")

    categories = front_matter.get("categories", [])
    if not isinstance(categories, list) or "dev" not in categories or "digest" not in categories:
        errors.append("categories must include 'dev' and 'digest'")

    tags = front_matter.get("tags", [])
    if not isinstance(tags, list) or not tags:
        errors.append("tags must be a non-empty list")

    if front_matter.get("generated_by") != "content-pipeline":
        errors.append("generated_by must be 'content-pipeline'")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"required section missing: {section}")

    item_count = len(re.findall(r"^### \d+\. ", body, flags=re.MULTILINE))
    if item_count < min_items:
        errors.append(f"expected at least {min_items} article sections, found {item_count}")

    source_count = len(re.findall(r"^- 출처: .+", body, flags=re.MULTILINE))
    link_count = len(
        re.findall(r"^- 링크: \[https://[^\]]+\]\(https://[^)]+\)", body, flags=re.MULTILINE)
    )
    why_count = len(re.findall(r"^- 왜 중요한가: .+", body, flags=re.MULTILINE))

    if source_count != item_count:
        errors.append(f"article/source count mismatch: {item_count} vs {source_count}")
    if link_count != item_count:
        errors.append(f"article/link count mismatch: {item_count} vs {link_count}")
    if why_count != item_count:
        errors.append(f"article/reason count mismatch: {item_count} vs {why_count}")

    return errors


def main() -> int:
    args = parse_args()
    path = Path(args.post_path).resolve()
    errors = validate_post(path, args.min_items)
    if errors:
        for error in errors:
            print(f"[error] {error}")
        return 1

    print(f"[ok] validated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
