#!/usr/bin/env python3
"""Read-only AEO pilot snapshots. Raw queries and analytics stay outside Git."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo

from search_console import CONFIG, SITE, access_token
from search_growth import google_post, windows
from search_engines import destination, save_new
from measurement_audit import PROPERTY, ga_session, ga_call
from build_example_archives import article, scalar

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'content/seo/answer-pilot.json'
REGISTRY = ROOT / 'content/seo/answer-cohorts.json'
AI_DOMAINS = frozenset(('chatgpt.com', 'chat.openai.com', 'perplexity.ai', 'claude.ai', 'copilot.microsoft.com', 'gemini.google.com'))


def targets(cohort):
    if cohort.get('schemaVersion') != 1 or cohort.get('languages') != ['en', 'ko'] or not re.fullmatch(r'[a-z0-9-]+', cohort.get('cohortId', '')):
        raise ValueError('Invalid pilot identity')
    articles = cohort.get('articles', [])
    if not isinstance(articles, list) or not 1 <= len(articles) <= 20 or any(not isinstance(a, dict) or not isinstance(a.get('key'), str) for a in articles) or len({a['key'] for a in articles}) != len(articles):
        raise ValueError('Expected one to twenty unique cohort topics')
    output = []
    for a in articles:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9-]+', a['key']):
            raise ValueError('Invalid article key')
        for lang in cohort['languages']:
            if not isinstance(a['questions'].get(lang), str) or not a['questions'][lang].strip():
                raise ValueError('Missing localized question')
            output.append({'key': a['key'], 'language': lang, 'url': SITE + f'{lang}/posts/{a["key"]}/'})
    return output


def load_cohort(cohort_id=None, root=ROOT):
    root = Path(root).resolve()
    registry_path = root / REGISTRY.relative_to(ROOT)
    if registry_path.resolve() != registry_path:
        raise ValueError('Registry must not be a symlink')
    registry = json.loads(registry_path.read_text())
    rows = registry.get('cohorts', [])
    if registry.get('schemaVersion') != 1 or not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Invalid cohort registry')
    for row in rows:
        if not re.fullmatch(r'[a-z0-9-]+', row['id']) or not re.fullmatch(r'content/seo/[a-z0-9-]+\.json', row['path']) or type(row.get('topics')) is not int or not 1 <= row['topics'] <= 20:
            raise ValueError('Invalid registered cohort')
    if registry.get('default') not in {r['id'] for r in rows}:
        raise ValueError('Missing default cohort')
    row = next((r for r in rows if r['id'] == (cohort_id or registry['default'])), None)
    if row is None: raise ValueError('Unknown cohort ID')
    path = root / row['path']
    if path.resolve() != path: raise ValueError('Cohort must not be a symlink')
    cohort = json.loads(path.read_text()); targets(cohort)
    if cohort['cohortId'] != row['id'] or len(cohort['articles']) != row['topics']:
        raise ValueError('Cohort identity or size disagrees with registry')
    return cohort


def source_records(cohort, root=ROOT):
    records = {}
    for row in targets(cohort):
        raw, _ = article(root, {'key': row['key']}, row['language'])
        head = raw.decode().split('---\n', 2)[1]
        records[row['url']] = {'sha256': hashlib.sha256(raw).hexdigest(),
                               'publishedAt': scalar(head, 'publishedAt')}
    return records


def inspect_targets(cohort, inspect):
    def inspection(row):
        return {'url': row['url'], 'response': safe(inspect, {'inspectionUrl': row['url'], 'siteUrl': SITE, 'languageCode': row['language']})}
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(inspection, targets(cohort)))


def collect_index(cohort, inspect, now):
    return {'schemaVersion': 1, 'mode': 'index-only', 'cohortId': cohort['cohortId'],
            'cohortIdentity': cohort_identity(cohort), 'observedAt': now.isoformat(),
            'targets': targets(cohort), 'inspections': inspect_targets(cohort, inspect),
            'limitations': ['Saved Google index status only; no live crawl test, index request, GSC performance or GA4 collection.']}


def publication_coverage(report, url, zone):
    """Declared publication is a necessary date bound, not proof of route availability."""
    declared = report.get('sourcePublications', {}).get(url)
    if not isinstance(declared, str) or not declared or not zone: return 'not-recorded'
    try:
        published = datetime.fromisoformat(declared.replace('Z', '+00:00'))
        if published.tzinfo is None: return 'not-recorded'
        start = datetime.fromisoformat(report['dates']['start']).replace(tzinfo=ZoneInfo(zone))
        end = datetime.fromisoformat(report['dates']['end']).replace(tzinfo=ZoneInfo(zone)) + timedelta(days=1)
        return 'declared-before-window' if published <= start else 'not-yet-published' if published >= end else 'partial-window'
    except (ValueError, KeyError): return 'not-recorded'


def cohort_identity(cohort):
    return hashlib.sha256(json.dumps(targets(cohort), sort_keys=True).encode()).hexdigest()


def ai_source(source):
    """Attribution-label match only: not proof of a referral, human visit or citation."""
    if not isinstance(source, str):
        return False
    try:
        parsed = urlsplit(source if '://' in source else 'https://' + source)
        if parsed.username or parsed.password: return False
        host = parsed.hostname
    except ValueError:
        return False
    return bool(host and any(host.lower() == d or host.lower().endswith('.' + d) for d in AI_DOMAINS))


def period(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if (last - first).days != 27:
        raise ValueError('Use an inclusive 28-day observation window')
    return {'start': str(first), 'end': str(last)}


def safe(call, *args):
    try:
        response = call(*args)
        if not isinstance(response, dict):
            return {'error': 'Invalid API response'}
        # Never retain request objects or exception text (may contain credentials).
        return {k: response[k] for k in ('httpStatus', 'data', 'error') if k in response}
    except Exception:
        return {'error': 'API transport or authentication failure'}


def paged(call, payload, offset_key, rows_key, size=25000, max_pages=2):
    rows, pages, headers = [], [], {}
    for offset in range(0, size * max_pages, size):
        result = safe(call, {**payload, offset_key: offset})
        pages.append({k: v for k, v in result.items() if k != 'data'})
        if result.get('httpStatus') != 200 or result.get('error') or not isinstance(result.get('data'), dict):
            return {'state': 'error', 'rows': rows, 'pages': pages, 'completePagination': False}
        data = result['data']
        for key in ('metadata', 'dimensionHeaders', 'metricHeaders'):
            if key in data: headers[key] = data[key]
        if 'metadata' in data: pages[-1]['metadata'] = data['metadata']
        batch = data.get(rows_key, [])
        if not isinstance(batch, list):
            return {'state': 'error', 'rows': rows, 'pages': pages, 'completePagination': False}
        rows.extend(batch)
        if len(batch) < size:
            return {'state': 'returned-data' if rows else 'no-returned-rows', 'rows': rows,
                    'pages': pages, 'completePagination': True, **headers}
    return {'state': 'row-cap-reached', 'rows': rows, 'pages': pages, 'completePagination': False, **headers}


def collect(cohort, dates, gsc, inspect, ga, now):
    selected = targets(cohort)
    regex = '^(?:' + '|'.join(re.escape(r['url']) for r in selected) + ')$'
    base = {'startDate': dates['start'], 'endDate': dates['end'], 'type': 'web', 'dataState': 'final',
            'rowLimit': 25000, 'dimensionFilterGroups': [{'groupType': 'and', 'filters': [
                {'dimension': 'page', 'operator': 'includingRegex', 'expression': regex}]}]}
    search = {name: paged(gsc, {**base, 'dimensions': dimensions}, 'startRow', 'rows')
              for name, dimensions in [('pages', ['page']), ('daily', ['page', 'date']), ('queries', ['page', 'query'])]}
    inspections = inspect_targets(cohort, inspect)
    ga_report = paged(ga, {'dateRanges': [{'startDate': dates['start'], 'endDate': dates['end']}],
        'dimensions': [{'name': x} for x in ('landingPage', 'sessionSource', 'sessionMedium')],
        'metrics': [{'name': x} for x in ('sessions', 'engagedSessions')], 'limit': 25000,
        'dimensionFilter': {'filter': {'fieldName': 'landingPage', 'inListFilter': {
            'values': [urlsplit(r['url']).path for r in selected], 'caseSensitive': True}}}}, 'offset', 'rows')
    ai_rows = []
    if ga_report.get('dimensionHeaders') and ga_report.get('metricHeaders'):
        dims = [v['name'] for v in ga_report['dimensionHeaders']]; metrics = [v['name'] for v in ga_report['metricHeaders']]
        for row in ga_report['rows']:
            flat = {**dict(zip(dims, [v['value'] for v in row['dimensionValues']])),
                    **dict(zip(metrics, [v['value'] for v in row['metricValues']]))}
            if ai_source(flat.get('sessionSource')):
                ai_rows.append(flat)
    return {'schemaVersion': 1, 'cohortId': cohort['cohortId'], 'cohortIdentity': cohort_identity(cohort),
        'observedAt': now.isoformat(), 'dates': dates, 'targets': selected, 'gscWeb': search,
        'inspections': inspections, 'ga4Attribution': ga_report, 'aiDomainMatchedAttributionRows': ai_rows,
        'aiDomainPolicy': sorted(AI_DOMAINS),
        'dedicatedAIReports': {'google': {'state': 'not-collected', 'requires': 'Check Search generative AI inclusion and dedicated report in Search Console.'},
                               'bing': {'state': 'not-collected', 'requires': 'Check AI Performance in Bing Webmaster Tools; no undocumented endpoint is called.'}},
        'limitations': ['GSC API Web is not a dedicated AI citation metric. Query rows are not exhaustive and omitted rows are not zero.',
          'URL Inspection is current status at observedAt, not historical status for the requested performance window or a new crawl request.',
          'GA dates use property timezone; GSC uses PT. Equal date labels do not align their UTC boundaries.',
          'GA source labels are attribution, not verified AI referrals, citations, human visitors or incremental impact.',
          'Thresholding, sampling and other response metadata are preserved. Empty or failed responses are not zero.',
          'Pre/post differences are observational; URLs may not have existed for the whole baseline. Publication, indexing, demand and other edits can change results.']}


def page_metrics(report, url):
    search = report.get('gscWeb', {}).get('pages', {})
    if search.get('state') not in ('returned-data', 'no-returned-rows') or not search.get('completePagination'):
        return None
    row = next((r for r in search.get('rows', []) if r.get('keys') == [url]), None)
    if row is None: return None
    return {k: row[k] for k in ('clicks', 'impressions', 'ctr', 'position') if k in row}


def attribution_metrics(report, url):
    data = report.get('ga4Attribution', {})
    if data.get('state') != 'returned-data' or not data.get('completePagination'): return None
    dims = [x['name'] for x in data.get('dimensionHeaders', [])]
    metrics = [x['name'] for x in data.get('metricHeaders', [])]
    rows = []
    for raw in data.get('rows', []):
        row = {**dict(zip(dims, [v['value'] for v in raw['dimensionValues']])),
               **dict(zip(metrics, [v['value'] for v in raw['metricValues']]))}
        if row.get('landingPage') == urlsplit(url).path: rows.append(row)
    if not rows: return None
    return {'reportedSessions': sum(int(r['sessions']) for r in rows),
            'reportedEngagedSessions': sum(int(r['engagedSessions']) for r in rows),
            'aiDomainMatchedSessionsInReturnedRows': sum(int(r['sessions']) for r in rows if ai_source(r.get('sessionSource'))),
            'timeZone': data.get('metadata', {}).get('timeZone', 'unknown'),
            'pageMetadata': [p.get('metadata', {}) for p in data.get('pages', [])]}


def comparison(before, after, changed_at=None):
    if before.get('mode') == 'index-only' or after.get('mode') == 'index-only':
        raise ValueError('Index-only observations are not performance baselines')
    if before.get('schemaVersion') != 1 or after.get('schemaVersion') != 1 or before.get('cohortIdentity') != after.get('cohortIdentity') or before.get('cohortId') != after.get('cohortId'):
        raise ValueError('Comparison requires the same pilot URL set')
    a, b = before['dates'], after['dates']; period(**a); period(**b)
    if date.fromisoformat(b['start']) <= date.fromisoformat(a['end']):
        raise ValueError('Follow-up must not overlap baseline')
    boundary = None
    ga_boundary = None
    ga_zone_verified = False
    if changed_at:
        changed = datetime.fromisoformat(changed_at)
        if changed.tzinfo is None: raise ValueError('Deployment time requires an explicit timezone')
        boundary = str(changed.astimezone(ZoneInfo('America/Los_Angeles')).date())
        if a['end'] >= boundary or b['start'] <= boundary:
            raise ValueError('Exclude the deployment PT day from both windows')
        before_zone = before.get('ga4Attribution', {}).get('metadata', {}).get('timeZone')
        after_zone = after.get('ga4Attribution', {}).get('metadata', {}).get('timeZone')
        if before_zone and after_zone and before_zone != after_zone:
            raise ValueError('GA property timezone changed; periods are not comparable')
        ga_zone_verified = bool(before_zone and after_zone)
        ga_zone = after_zone or before_zone
        if ga_zone:
            ga_boundary = str(changed.astimezone(ZoneInfo(ga_zone)).date())
            if a['end'] >= ga_boundary or b['start'] <= ga_boundary:
                raise ValueError('Exclude the deployment GA property day from both windows')
    per_page = []
    for target in after.get('targets', []):
        url = target['url']; old, new = page_metrics(before, url), page_metrics(after, url)
        coverage = {'baseline': publication_coverage(before, url, 'America/Los_Angeles'),
                    'followUp': publication_coverage(after, url, 'America/Los_Angeles')}
        comparable = all(v == 'declared-before-window' for v in coverage.values())
        delta = {k: new[k] - old[k] for k in ('clicks', 'impressions') if k in old and k in new} if comparable and old is not None and new is not None else None
        per_page.append({'url': url, 'baselineGscWeb': old, 'followUpGscWeb': new, 'delta': delta,
                         'declaredPublicationCoveragePT': coverage, 'routeAvailabilityVerified': False,
                         'declaredPublicationCoverageGA': {
                             'baseline': publication_coverage(before, url, before.get('ga4Attribution', {}).get('metadata', {}).get('timeZone')),
                             'followUp': publication_coverage(after, url, after.get('ga4Attribution', {}).get('metadata', {}).get('timeZone'))},
                         'baselineGaAttribution': attribution_metrics(before, url), 'followUpGaAttribution': attribution_metrics(after, url)})
    return {'baselineDates': a, 'followUpDates': b, 'equalLengthDays': 28,
            'deploymentDayPT': boundary, 'deploymentDayGA': ga_boundary,
            'publicationBoundaryVerified': boundary is not None and ga_zone_verified,
            'pages': per_page, 'causalEffectEstablished': False, 'dedicatedAIVisibilityMeasured': False}


def summary(report):
    inspection_rows = report.get('inspections', [])
    counts = {'pass': 0, 'nonPassVerdict': 0, 'missingVerdict': 0, 'apiError': 0, 'notObserved': 0}
    for row in inspection_rows:
        response = row.get('response', {})
        verdict = response.get('data', {}).get('inspectionResult', {}).get('indexStatusResult', {}).get('verdict')
        category = 'apiError' if response.get('httpStatus') != 200 or response.get('error') else 'pass' if verdict == 'PASS' else 'nonPassVerdict' if verdict in ('FAIL','PARTIAL','NEUTRAL') else 'missingVerdict'
        counts[category] += 1
    counts['notObserved'] = max(0, len(report['targets']) - len(inspection_rows))
    passed = counts['pass']
    if report.get('mode') == 'index-only':
        return {'mode': 'index-only', 'cohortId': report['cohortId'], 'observedAt': report['observedAt'],
                'dataOrigin': report.get('dataOrigin', 'not-recorded'),
                'pilotURLs': len(report['targets']), 'googleIndex': counts,
                'gscWeb': 'not-collected', 'ga4': 'not-collected',
                'dedicatedAIReports': 'not-collected',
                'urls': [{'url': row['url'], 'httpStatus': row['response'].get('httpStatus'),
                    **{key: row['response'].get('data', {}).get('inspectionResult', {}).get('indexStatusResult', {}).get(key)
                       for key in ('verdict','coverageState','googleCanonical','lastCrawlTime')}} for row in inspection_rows]}
    result = {'dates': report['dates'], 'pilotURLs': len(report['targets']), 'googleIndexPass': passed,
            'observedAt': report.get('observedAt'), 'dataOrigin': report.get('dataOrigin', 'not-recorded'),
            'cohortId': report.get('cohortId'), 'googleIndex': counts,
            'gscWebPages': report['gscWeb']['pages']['state'],
            'gscReturnedPageRows': len(report['gscWeb']['pages']['rows']),
            'ga4State': report['ga4Attribution']['state'],
            'ga4Timezone': report['ga4Attribution'].get('metadata', {}).get('timeZone', 'unknown'),
            'aiDomainMatchedAttributionRows': len(report['aiDomainMatchedAttributionRows']),
            'dedicatedAIReports': {k: v['state'] for k, v in report['dedicatedAIReports'].items()}}
    if 'comparison' in report:
        compared = report['comparison']
        result['comparison'] = {k: compared[k] for k in ('baselineDates','followUpDates','publicationBoundaryVerified','causalEffectEstablished')}
        result['comparison']['pages'] = [{k: row[k] for k in ('url','baselineGscWeb','followUpGscWeb','delta','baselineGaAttribution','followUpGaAttribution','declaredPublicationCoveragePT','declaredPublicationCoverageGA','routeAvailabilityVerified') if k in row} for row in compared['pages']]
    result['declaredPublicationCoverage'] = [{'url': r['url'],
        'gscPT': publication_coverage(report, r['url'], 'America/Los_Angeles'),
        'ga4': publication_coverage(report, r['url'], report.get('ga4Attribution', {}).get('metadata', {}).get('timeZone')),
        'routeAvailabilityVerified': False} for r in report['targets']]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Read GSC/GA APIs only; never submit URLs or modify settings')
    parser.add_argument('--cohort', help='Registered cohort ID; default retains the original ten URLs')
    parser.add_argument('--index-only', action='store_true', help='Inspect current saved Google status without performance or GA4 access')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--start'); parser.add_argument('--end')
    parser.add_argument('--compare', type=Path, help='Existing private baseline for a non-overlapping 28-day comparison')
    parser.add_argument('--changed-at', help='Actual deployment ISO timestamp with timezone; required with --compare')
    parser.add_argument('--report', type=Path, help='Summarize a saved snapshot without network or raw query disclosure')
    args = parser.parse_args()
    try:
        if args.report:
            if args.live or args.output or args.start or args.end or args.compare or args.changed_at or args.cohort or args.index_only:
                raise ValueError('--report cannot query APIs or write files')
            print(json.dumps(summary(json.loads(args.report.read_text())), ensure_ascii=False, indent=2)); return 0
        cohort = load_cohort(args.cohort)
        sources = source_records(cohort)
        now = datetime.now(timezone.utc)
        if args.index_only:
            if args.start or args.end or args.compare or args.changed_at:
                raise ValueError('Index-only observations have no historical performance window')
            if not args.live:
                if args.output: raise ValueError('Writing requires --live')
                print(json.dumps({'mode': 'plan-only', 'observationMode': 'index-only', 'cohortId': cohort['cohortId'], 'targets': targets(cohort), 'settingsModified': False}, indent=2)); return 0
            if not args.output: raise ValueError('--live requires a new private --output')
            output = destination(args.output)
            token = access_token(SimpleNamespace(token_file=CONFIG / 'token.json', client=None))
            report = collect_index(cohort, lambda body: google_post(token, 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect', body), now)
            report['dataOrigin'] = 'live-api'
            report['sourceCommit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            report['sourceHashes'] = {url: value['sha256'] for url, value in sources.items()}
            report['sourcePublications'] = {url: value['publishedAt'] for url, value in sources.items()}
            save_new(output, report)
            print(json.dumps(summary(report), ensure_ascii=False, indent=2))
            return 1 if summary(report)['googleIndex']['apiError'] else 0
        if bool(args.start) != bool(args.end): raise ValueError('Specify both --start and --end')
        dates = period(args.start, args.end) if args.start else period(*windows(now)['current'])
        settled_end = windows(now)['current'][1]
        if dates['end'] > settled_end: raise ValueError('Use a window ending at least three PT calendar days ago')
        if bool(args.compare) != bool(args.changed_at): raise ValueError('Use --compare and --changed-at together')
        if not args.live:
            if args.output or args.compare: raise ValueError('Writing requires --live')
            print(json.dumps({'mode': 'plan-only', 'cohortId': cohort['cohortId'], 'dates': dates, 'targets': targets(cohort), 'settingsModified': False}, indent=2)); return 0
        if not args.output: raise ValueError('--live requires a new private --output outside all worktrees')
        output = destination(args.output)
        before = json.loads(args.compare.read_text()) if args.compare else None
        if before:
            comparison(before, {'schemaVersion': 1, 'cohortId': cohort['cohortId'], 'cohortIdentity': cohort_identity(cohort), 'dates': dates}, args.changed_at)
        token = access_token(SimpleNamespace(token_file=CONFIG / 'token.json', client=None))
        endpoint = 'https://www.googleapis.com/webmasters/v3/sites/' + quote(SITE, safe='') + '/searchAnalytics/query'
        session = ga_session()
        try:
            report = collect(cohort, dates, lambda body: google_post(token, endpoint, body),
                lambda body: google_post(token, 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect', body),
                lambda body: ga_call(session, 'POST', PROPERTY + ':runReport', body), now)
        finally: session.close()
        report['sourceCommit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['dataOrigin'] = 'live-api'
        report['sourceHashes'] = {url: value['sha256'] for url, value in sources.items()}
        report['sourcePublications'] = {url: value['publishedAt'] for url, value in sources.items()}
        if before: report['comparison'] = comparison(before, report, args.changed_at)
        save_new(output, report)
        print(json.dumps(summary(report), ensure_ascii=False, indent=2))
        failed = any(r['state'] == 'error' for r in report['gscWeb'].values()) or report['ga4Attribution']['state'] == 'error' or any(r['response'].get('httpStatus') != 200 or r['response'].get('error') for r in report['inspections'])
        return 1 if failed else 0
    except Exception:
        print('AEO snapshot failed: check dates, cohort, authentication and private output path. Credentials and API exception text are not printed.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
