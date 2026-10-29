#!/usr/bin/env python3
"""Read-only search/GA comparison and explicitly labeled traffic sensitivity reports."""
import argparse
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote
from zoneinfo import ZoneInfo

from search_console import CONFIG, SITE, access_token, private_json
from search_engines import bing_get, destination, save_new
from search_growth import google_post

PROPERTY = 'properties/280207087'
MEASUREMENT = 'G-XZVJ0K06M9'
GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'


def span(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if not 0 <= (last - first).days <= 6:
        raise ValueError('Choose an inclusive window of one to seven days')
    return first, last


def aligned_window(start, end, local_zone):
    first, last = span(start, end)
    low = datetime.combine(first, time(), ZoneInfo('America/Los_Angeles'))
    high = datetime.combine(last + timedelta(days=1), time(), ZoneInfo('America/Los_Angeles'))
    local = ZoneInfo(local_zone)
    # Walk UTC so DST boundaries do not invent or omit an actual hour.
    cursor, stop = low.astimezone(timezone.utc), high.astimezone(timezone.utc)
    hours = []
    while cursor < stop:
        stamp = cursor.astimezone(local)
        if stamp.minute or stamp.second:
            raise ValueError('GA property timezone needs whole-hour alignment')
        hours.append(stamp.strftime('%Y%m%d%H'))
        cursor += timedelta(hours=1)
    return {'gscStart': low.isoformat(), 'gscEndExclusive': high.isoformat(),
            'gaStart': low.astimezone(local).isoformat(), 'gaEndExclusive': high.astimezone(local).isoformat(),
            'gaDates': {'startDate': str(low.astimezone(local).date()),
                        'endDate': str((high - timedelta(seconds=1)).astimezone(local).date())},
            'gaHours': sorted(set(hours))}


def exact(field, value):
    return {'filter': {'fieldName': field, 'stringFilter': {'matchType': 'EXACT', 'value': value}}}


def together(*expressions):
    return {'andGroup': {'expressions': list(expressions)}}


def validate_rules(rules, zone):
    if rules.get('schemaVersion') != 1 or rules.get('property') != PROPERTY or rules.get('timeZone') != zone:
        raise ValueError('Traffic rules must identify this property, schema and timezone')
    rows = rules.get('rules')
    if not isinstance(rows, list) or len(rows) > 20:
        raise ValueError('Expected at most twenty explicit suspected-traffic rules')
    seen = set()
    for row in rows:
        if row.get('classification') != 'suspected' or not row.get('reason') or not row.get('id') or row['id'] in seen:
            raise ValueError('Every unique rule needs a reason and suspected classification')
        seen.add(row['id'])
        if row.get('sourceMedium') not in ('(direct) / (none)', 'bing / organic', 'google / organic'):
            raise ValueError('Rule source must be explicit')
        if not isinstance(row.get('minutes'), list) or not 1 <= len(row['minutes']) <= 20:
            raise ValueError('Rule needs explicit minute timestamps')
        for minute in row['minutes']:
            if not isinstance(minute, str) or len(minute) != 12 or datetime.strptime(minute, '%Y%m%d%H%M').strftime('%Y%m%d%H%M') != minute:
                raise ValueError('Invalid rule minute')
        paths = row.get('paths')
        if not isinstance(paths, list) or not 1 <= len(paths) <= 50 or any(not isinstance(p, str) or not p.startswith(('/en/', '/ko/')) or '?' in p or '#' in p or '..' in p for p in paths):
            raise ValueError('Rule needs explicit public content paths without queries')
    return rules


def rule_expression(rules):
    rows = rules['rules']
    if not rows:
        return None
    return {'orGroup': {'expressions': [together(
        exact('sessionSourceMedium', row['sourceMedium']),
        {'filter': {'fieldName': 'dateHourMinute', 'inListFilter': {'values': row['minutes']}}},
        {'filter': {'fieldName': 'pagePath', 'inListFilter': {'values': row['paths']}}},
    ) for row in rows]}}


def plan(start, end, segment_start, segment_end, zone, rules):
    span(segment_start, segment_end)
    validate_rules(rules, zone)
    aligned = aligned_window(start, end, zone)
    host = exact('hostName', 'youdozi.github.io')
    hours = {'filter': {'fieldName': 'dateHour', 'inListFilter': {'values': aligned['gaHours']}}}
    ga = {}
    metrics = ['totalUsers', 'sessions', 'screenPageViews', 'engagedSessions']
    for name, source in [('all', None), ('google', 'google / organic'), ('bing', 'bing / organic')]:
        expression = together(host, hours, *([exact('sessionSourceMedium', source)] if source else []))
        ga['aligned:' + name] = {'dateRanges': [aligned['gaDates']], 'metrics': [{'name': x} for x in metrics], 'dimensionFilter': expression}
    for source in ('google', 'bing'):
        ga['alignedLandings:' + source] = {**ga['aligned:' + source], 'dimensions': [{'name': 'landingPage'}], 'limit': 1000}
    # Segment event counts, not user/session counts that overlap across pages.
    base = together(host, exact('eventName', 'page_view'))
    review = {'filter': {'fieldName': 'pagePath', 'stringFilter': {'matchType': 'FULL_REGEXP', 'value': '^/review/?$'}}}
    match = rule_expression(rules)
    filters = {'rawPageViews': base, 'reviewPageViews': together(base, review),
               'nonReviewPageViews': together(base, {'notExpression': review})}
    if match:
        filters['suspectedRulePageViews'] = together(base, {'notExpression': review}, match)
        filters['remainderSensitivityPageViews'] = together(base, {'notExpression': review}, {'notExpression': match})
    else:
        filters['remainderSensitivityPageViews'] = filters['nonReviewPageViews']
    for name, expression in filters.items():
        ga['segment:' + name] = {'dateRanges': [{'startDate': segment_start, 'endDate': segment_end}],
                                'metrics': [{'name': 'eventCount'}], 'dimensionFilter': expression}
    gsc = {name: {'startDate': start, 'endDate': end, 'dataState': 'final', 'type': 'web', 'dimensions': dimensions, 'rowLimit': 25000}
           for name, dimensions in [('totals', []), ('daily', ['date']), ('pages', ['page'])]}
    return {'searchDatesPT': {'start': start, 'end': end}, 'alignment': aligned,
            'segmentDates': {'start': segment_start, 'end': segment_end, 'timeZone': zone}, 'ga': ga, 'gsc': gsc}


def flat(response):
    if response.get('httpStatus') != 200 or not isinstance(response.get('data'), dict):
        return None
    data = response['data']
    dimensions = [x['name'] for x in data.get('dimensionHeaders', [])]
    metrics = [x['name'] for x in data.get('metricHeaders', [])]
    return [{**dict(zip(dimensions, [v['value'] for v in row.get('dimensionValues', [])])),
             **dict(zip(metrics, [v['value'] for v in row.get('metricValues', [])]))} for row in data.get('rows', [])]


def summarize(report):
    values = {}
    for name in ('rawPageViews', 'reviewPageViews', 'nonReviewPageViews', 'suspectedRulePageViews', 'remainderSensitivityPageViews'):
        rows = flat(report['ga'].get('segment:' + name, {}))
        value = rows[0].get('eventCount') if rows and len(rows) == 1 else None
        values[name] = int(value) if isinstance(value, str) and value.isdigit() else None
    if not report['rules']['rules']:
        values['suspectedRulePageViews'] = 0  # No match rule exists; not an API zero assumption.
    raw, review, public, suspect, rest = (values[k] for k in values)
    checks = {'rawEqualsReviewPlusNonReview': None if None in (raw, review, public) else raw == review + public,
              'nonReviewEqualsSuspectedPlusRemainder': None if None in (public, suspect, rest) else public == suspect + rest}
    gsc = report['gsc'].get('totals', {})
    rows = gsc.get('data', {}).get('rows') if gsc.get('httpStatus') == 200 else None
    google = flat(report['ga'].get('aligned:google', {}))
    return {'pageViewScenarios': values, 'partitionChecks': checks,
            'googleClicksAndImpressions': rows[0] if rows and len(rows) == 1 else None,
            'alignedGoogleAnalytics': google[0] if google and len(google) == 1 else None,
            'bingPerformanceState': 'rows-returned' if report['bingStats'].get('data') else 'unknown-or-unavailable',
            'warning': 'Rule matches are suspected, not confirmed automation. The remainder is not a verified human audience. Users/sessions are not subtracted; no GA settings or original data changed.'}


def collect(requests, rules, ga_post, gsc_post, bing):
    def read(callback, *args):
        try:
            return callback(*args)
        except Exception as error:
            return {'error': type(error).__name__}
    ga = {name: read(ga_post, body) for name, body in requests['ga'].items()}
    gsc = {name: read(gsc_post, body) for name, body in requests['gsc'].items()}
    sites = read(bing, 'GetUserSites', {})
    raw_sites = sites.get('data')
    matches = [x['Url'] for x in raw_sites if isinstance(x, dict) and isinstance(x.get('Url'), str) and x['Url'].rstrip('/') == SITE.rstrip('/')] if isinstance(raw_sites, list) else []
    stats = read(bing, 'GetRankAndTrafficStats', {'siteUrl': matches[0]}) if len(matches) == 1 else {'error': 'Expected exactly one registered Bing site match', 'notRequested': True}
    report = {'schemaVersion': 1, 'checkedAt': datetime.now(timezone.utc).isoformat(), 'site': SITE, 'property': PROPERTY,
              'measurementId': MEASUREMENT, 'requests': requests, 'rules': rules, 'ga': ga, 'gsc': gsc,
              'bingRegisteredSiteMatches': matches, 'bingStats': stats,
              'limits': ['GSC final web dates use PT; GA aligned queries use the exact corresponding property-timezone hours.',
                         'GA sessions and search clicks are different metrics. Canonical GSC page rows may omit data and are not total clicks.',
                         'An empty Bing array is unknown performance, not zero clicks. Bing API includes all supported verticals; its date basis is not silently equated with GA.',
                         'Sensitivity segmentation counts page_view events. Matches do not identify the operator or prove automation.',
                         'No settings, publishing, sitemap submission or indexing requests were changed.']}
    report['apiErrors'] = [kind + ':' + name for kind, rows in [('ga', ga), ('gsc', gsc)] for name, response in rows.items() if response.get('httpStatus') != 200]
    if stats.get('httpStatus') != 200:
        report['apiErrors'].append('bing:stats')
    report['summary'] = summarize(report)
    return report


def ga_session():
    from google.auth.transport.requests import AuthorizedSession, Request
    from google.oauth2.credentials import Credentials
    credentials = Credentials.from_authorized_user_file(str(CONFIG / 'analytics-token.json'), scopes=[GA_SCOPE])
    if not credentials.valid:
        credentials.refresh(Request())
        private_json(CONFIG / 'analytics-token.json', json.loads(credentials.to_json()))
    return AuthorizedSession(credentials)


def ga_call(session, method, endpoint, body=None):
    try:
        response = session.request(method, 'https://analyticsdata.googleapis.com/v1beta/' + endpoint, json=body, timeout=45, allow_redirects=False)
        if response.status_code != 200:
            return {'httpStatus': response.status_code, 'error': 'GA API request failed'}
        return {'httpStatus': 200, 'data': response.json()}
    except Exception:
        return {'error': 'GA transport or response failure'}


def format_report(report):
    if report.get('schemaVersion') != 1 or report.get('property') != PROPERTY or report.get('site') != SITE:
        raise ValueError('Expected this site measurement snapshot')
    summary = summarize(report)
    return '\n'.join(['조회: ' + report['checkedAt'], '검색 비교: ' + json.dumps(report['requests']['searchDatesPT']) + ' PT',
                      'GA 대응 시간: ' + report['requests']['alignment']['gaStart'] + ' ~ ' + report['requests']['alignment']['gaEndExclusive'] + ' (끝 시각 제외)',
                      '조회 분리 구간: ' + json.dumps(report['requests']['segmentDates'], ensure_ascii=False),
                      '같은 시간 구간의 GA Google: ' + json.dumps(summary['alignedGoogleAnalytics'], ensure_ascii=False),
                      'GSC 클릭·노출: ' + json.dumps(summary['googleClicksAndImpressions'], ensure_ascii=False),
                      '페이지 조회 분리: ' + json.dumps(summary['pageViewScenarios'], ensure_ascii=False),
                      '분할 검산: ' + json.dumps(summary['partitionChecks']), 'Bing 실적: ' + summary['bingPerformanceState'], 'API 조회 실패: ' + json.dumps(report.get('apiErrors', [])), '의심 규칙 일치는 자동화 확정이 아니며, 나머지 구간도 실제 독자로 검증된 값이 아닙니다. 원본과 GA 설정은 유지했습니다.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start'); parser.add_argument('--end')
    parser.add_argument('--segment-start'); parser.add_argument('--segment-end')
    parser.add_argument('--rules', type=Path); parser.add_argument('--output', type=Path)
    parser.add_argument('--live', action='store_true'); parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report:
        if args.live or args.output:
            parser.error('--report cannot write or query APIs')
        print(format_report(json.loads(args.report.expanduser().read_text())))
        return
    if not args.start or not args.end:
        parser.error('--start and --end are required PT calendar dates')
    # This site's recorded GA property timezone; verified again in live mode.
    zone = 'Asia/Seoul'
    rules = json.loads(args.rules.expanduser().read_text()) if args.rules else {'schemaVersion': 1, 'property': PROPERTY, 'timeZone': zone, 'rules': []}
    requests = plan(args.start, args.end, args.segment_start or args.start, args.segment_end or args.end, zone, rules)
    if not args.live:
        print(json.dumps({'mode': 'preview', 'searchWindow': requests['alignment'], 'segmentWindow': requests['segmentDates'], 'suspectedRules': len(rules['rules']), 'requests': len(requests['ga']) + len(requests['gsc']) + 2}, ensure_ascii=False, indent=2))
        return
    if not args.output:
        parser.error('--live requires a new private --output')
    output = destination(args.output)  # Fail before credentials or APIs if output is unsafe.
    session = ga_session()
    try:
        response = session.get('https://analyticsadmin.googleapis.com/v1beta/' + PROPERTY, timeout=30)
        if response.status_code != 200 or response.json().get('timeZone') != zone:
            raise ValueError('GA property timezone could not be verified')
        response = session.get('https://analyticsadmin.googleapis.com/v1beta/' + PROPERTY + '/dataStreams', timeout=30)
        if response.status_code != 200 or sum(x.get('webStreamData', {}).get('measurementId') == MEASUREMENT for x in response.json().get('dataStreams', [])) != 1:
            raise ValueError('GA site measurement ID could not be verified')
        token = access_token(SimpleNamespace(token_file=CONFIG / 'token.json', client=None))
        endpoint = 'https://www.googleapis.com/webmasters/v3/sites/' + quote(SITE, safe='') + '/searchAnalytics/query'
        key = (CONFIG / 'bing-api-key.txt').read_text().strip()
        report = collect(requests, rules, lambda body: ga_call(session, 'POST', PROPERTY + ':runReport', body),
                         lambda body: google_post(token, endpoint, body), lambda method, params: bing_get(key, method, params))
        save_new(output, report)
        print(format_report(report));print('비공개 결과: ' + str(output))
        if report['apiErrors'] or any(value is not True for value in report['summary']['partitionChecks'].values()):
            raise SystemExit(2)
    finally:
        session.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # No raw HTTP exceptions: URLs/headers can contain API credentials.
        print('Measurement audit failed: ' + (str(error) if isinstance(error, ValueError) else type(error).__name__), file=__import__('sys').stderr)
        raise SystemExit(1)
