#!/usr/bin/env python3
"""Create a readable PR review body from a generated bilingual candidate."""
import argparse
import html
import json
from pathlib import Path
import re


def text(value):
    # External headlines/quotes must remain text, including mentions and HTML.
    value = html.escape(str(value), quote=False).replace('@', '&#64;')
    return re.sub(r'([\\`*_{}\[\]()#!|>~])', r'\\\1', value).replace('\n', ' ')


def link(url):
    from urllib.parse import urlsplit
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or any(c in url for c in '<>\r\n'):
        raise ValueError('Invalid review source URL')
    return '<' + url + '>'


def render(data):
    lines = [
        '이 PR은 자동 생성한 **미게시 초안**입니다. 자동 검사는 사람의 사실 확인을 대체하지 않습니다.', '',
        f'수집 기준일: {text(data["date"])} / 기사 {len(data["articles"])}개', '',
        '- [ ] 원문을 열어 사실·수치·날짜·출시 상태와 인용의 맥락을 확인했습니다.',
        '- [ ] 영문·한국어 제목과 요약이 같은 의미인지, 과장이나 누락이 없는지 확인했습니다.',
        '- [ ] 수정이 필요하면 Files changed의 JSON을 수정하고 두 언어의 summary와 claims를 함께 맞췄습니다.',
        '- [ ] 게시할 준비가 되면 **Ready for review → Merge pull request**를 누릅니다. 병합이 게시 승인입니다.', '',
        '게시하지 않을 경우 PR을 닫으세요. 검토 대기 PR이 열려 있는 동안 다음 자동 생성은 건너뜁니다.', '',
        '검토가 오래 걸렸다면 기사 최신성도 다시 확인하세요. PR 본문은 최초 생성본이며 수정 후에는 Files changed가 기준입니다.',
    ]
    for number, article in enumerate(data['articles'], 1):
        lines += ['', '---', '', f'### {number}. {text(article["editions"]["ko"]["title"])}', '',
                  f'출처: {text(article["source"])} · 기사 날짜: {text(article["publishedAt"])}', '', link(article['url'])]
        for lang, label in [('en', 'English'), ('ko', '한국어')]:
            edition = article['editions'][lang]
            lines += ['', f'**{label}: {text(edition["title"])}**', '', text(edition['summary']), '', '<details>', f'<summary>{label} 문장별 원문 근거</summary>', '']
            for claim in edition['claims']:
                lines += [f'- 주장: {text(claim["text"])}']
                for evidence in claim['evidence']:
                    document = article['documents'][evidence['document_id']]
                    lines += [f'  - 인용: “{text(evidence["quote"])}”', f'  - 근거 문서: {link(document["url"])}']
            lines += ['', '</details>']
    result = '\n'.join(lines) + '\n'
    if len(result) > 60000:
        raise ValueError('Review exceeds the PR body budget')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('digest', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(render(json.loads(args.digest.read_text())), encoding='utf-8')


if __name__ == '__main__':
    main()
