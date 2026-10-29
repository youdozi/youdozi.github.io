#!/usr/bin/env python3
"""Group saved Google observations by core topic; no APIs, authentication or indexing requests."""
import argparse
from datetime import datetime
import json
from pathlib import Path

from search_growth import REGISTRY, SITE, targets, index_status, compare


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result if result.tzinfo is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


def page_performance(snapshot, url, period):
    response = snapshot.get('performance', {}).get(period, {}).get('pages', {})
    if response.get('httpStatus') != 200:
        return {'state': 'request-failed-or-unavailable', 'clicks': None, 'impressions': None, 'position': None}
    rows = [r for r in response.get('rows', []) if r.get('keys') == [url]]
    row = rows[0] if len(rows) == 1 else {}
    return {'state': 'row-returned' if len(rows) == 1 else 'row-not-returned',
            **{key: row.get(key) for key in ('clicks', 'impressions', 'position')}}


def build_report(snapshot, deployed_at=None, previous=None, registry=None):
    selected = targets(registry or json.loads(REGISTRY.read_text()))
    checked = timestamp(snapshot.get('checkedAt'))
    deployed = timestamp(deployed_at) if deployed_at is not None else None
    if snapshot.get('site') != SITE or checked is None or (deployed_at is not None and deployed is None):
        raise ValueError('Expected this property, a dated snapshot and timezone-aware deployment time')
    rows = {r['url']: r for r in snapshot['urls']}
    if len(rows) != len(snapshot['urls']):
        raise ValueError('Duplicate snapshot URLs')
    for expected in selected:
        row = rows.get(expected['url'])
        if row is None or any(row.get(key) != expected[key] for key in ('key', 'kind', 'language', 'expectedCanonical')):
            raise ValueError('Snapshot must include the registered core editions and legacy mappings')
    if previous is not None and (timestamp(previous.get('checkedAt')) is None or timestamp(previous['checkedAt']) > checked):
        raise ValueError('Previous snapshot must have an earlier timezone-aware observation time')
    report = {'schemaVersion': 1, 'site': SITE, 'checkedAt': snapshot['checkedAt'], 'deployedAt': deployed_at,
              'snapshotVsDeployment': 'not-compared' if deployed is None else 'before-deployment' if checked < deployed else 'on-or-after-deployment',
              'windows': snapshot['windows'], 'topics': [],
              'limits': ['Saved Google index observations, not a live indexability test or proof of migration completion.',
                         'Missing page rows and canonical/crawl fields remain unavailable, not zero or a change.',
                         'A crawl after deployment does not prove the new HTML was used or establish causality.',
                         'Canonical page metrics are kept per URL and are not added to property totals.']}
    for offset in range(0, len(selected), 3):
        group = selected[offset:offset + 3]
        old_url = group[2]['url']
        editions = {}
        for role, expected in zip(('en', 'ko', 'legacy'), group):
            row = rows[expected['url']]
            state = index_status(row['inspection'])
            canonical = state.get('googleCanonical') if state else None
            crawl = state.get('lastCrawlTime') if state else None
            crawled = timestamp(crawl)
            relation = ('unavailable' if not canonical else 'matches-destination' if canonical == expected['expectedCanonical']
                        else 'still-legacy' if canonical == old_url else 'other')
            editions[role] = {'url': expected['url'], 'verdict': state.get('verdict') if state else None,
                              'googleCanonical': canonical, 'canonicalRelation': relation, 'lastCrawlTime': crawl,
                              'crawlVsDeployment': 'not-compared' if deployed is None else 'unavailable' if crawled is None else 'before-deployment' if crawled < deployed else 'on-or-after-deployment',
                              'performance': {period: page_performance(snapshot, expected['url'], period) for period in ('current', 'previous')}}
        ko, legacy = editions['ko'], editions['legacy']
        new_selected = ko['verdict'] == 'PASS' and ko['canonicalRelation'] == 'matches-destination'
        observation = ('destination-selected-on-both' if new_selected and legacy['canonicalRelation'] == 'matches-destination'
                       else 'new-indexed-legacy-still-selected' if new_selected and legacy['canonicalRelation'] == 'still-legacy'
                       else 'legacy-still-selected' if legacy['canonicalRelation'] == 'still-legacy' else 'pending-or-unavailable')
        report['topics'].append({'key': group[0]['key'], 'observation': observation, 'editions': editions})
    report['summary'] = {language: {'checked': 10,
        'googlePass': sum(t['editions'][language]['verdict'] == 'PASS' for t in report['topics']),
        'unknownOrError': sum(t['editions'][language]['verdict'] is None for t in report['topics'])} for language in ('en', 'ko', 'legacy')}
    if previous is not None:
        report['comparison'] = compare(previous, snapshot)
    return report


def format_report(report):
    lines = ['핵심 글 주소 전환 관측', '조회: ' + report['checkedAt'],
             '배포: ' + (report['deployedAt'] or '미지정') + ' / 관측 시점: ' + report['snapshotVsDeployment'],
             '배포 후 크롤링 기록도 변경 반영·색인 완료·원인을 증명하지 않습니다.']
    for language, counts in report['summary'].items():
        lines.append(f"{language}: {counts['checked']}개 중 PASS {counts['googlePass']}개 · 판정 미제공/오류 {counts['unknownOrError']}개")
    for topic in report['topics']:
        lines.append('\n' + topic['key'] + ' / ' + topic['observation'])
        for language, edition in topic['editions'].items():
            current = edition['performance']['current']
            metrics = f"클릭 {current['clicks']} · 노출 {current['impressions']}" if current['state'] == 'row-returned' else '실적 미반환·비교 불가'
            lines.extend([f"  {language}: {edition['url']}",
                          f"    판정 {edition['verdict'] or '미제공'} · 대표 주소 {edition['canonicalRelation']} · {edition['googleCanonical'] or '미제공'}",
                          f"    마지막 크롤링 {edition['lastCrawlTime'] or '미제공'} · 배포 대비 {edition['crawlVsDeployment']} · {metrics}"])
    if 'comparison' in report:
        c = report['comparison']
        lines.append(f"\n이전 관측 대비: PASS 전환 {len(c['newPass'])} · PASS 해제 {len(c['noLongerPass'])} · 색인 비교 불가 {len(c['uncomparableUrls'])} · canonical 변경 {len(c['canonicalChanges'])} · canonical 미제공 {len(c['canonicalUncomparableUrls'])}")
    lines.append('\n누락 필드는 0이나 변화로 간주하지 않습니다. 실적 구간은 PT 기준이며 겹치는 구간의 차이는 인과효과가 아닙니다. 검색어는 출력하지 않습니다.')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--deployed-at')
    parser.add_argument('--output', type=Path, help='Optional new private JSON outside all repository worktrees')
    args = parser.parse_args()
    try:
        from search_engines import destination, save_new
        output = destination(args.output) if args.output else None
        report = build_report(json.loads(args.snapshot.expanduser().read_text()), args.deployed_at,
                              json.loads(args.previous.expanduser().read_text()) if args.previous else None)
        if output:
            save_new(output, report)
        print(format_report(report))
        return 0
    except Exception as error:
        print('Migration report failed (' + type(error).__name__ + '); input contents omitted.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
