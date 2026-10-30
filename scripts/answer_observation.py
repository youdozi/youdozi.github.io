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

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'content/seo/answer-pilot.json'
AI_DOMAINS = frozenset(('chatgpt.com', 'chat.openai.com', 'perplexity.ai', 'claude.ai', 'copilot.microsoft.com', 'gemini.google.com'))


def targets(cohort):
    if cohort.get('schemaVersion') != 1 or cohort.get('languages') != ['en', 'ko'] or not re.fullmatch(r'[a-z0-9-]+', cohort.get('cohortId', '')):
        raise ValueError('Invalid pilot identity')
    articles = cohort.get('articles', [])
    if len(articles) != 5 or len({a['key'] for a in articles}) != 5:
        raise ValueError('Expected five unique pilot topics')
    output = []
    for a in articles:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9-]+', a['key']):
            raise ValueError('Invalid article key')
        for lang in cohort['languages']:
            if not isinstance(a['questions'].get(lang), str) or not a['questions'][lang].strip():
                raise ValueError('Missing localized question')
            output.append({'key': a['key'], 'language': lang, 'url': SITE + f'{lang}/posts/{a["key"]}/'})
    return output


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
    def inspection(row):
        return {'url': row['url'], 'response': safe(inspect, {'inspectionUrl': row['url'], 'siteUrl': SITE, 'languageCode': row['language']})}
    with ThreadPoolExecutor(max_workers=3) as pool:
        inspections = list(pool.map(inspection, selected))
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
    if before.get('schemaVersion') != 1 or after.get('schemaVersion') != 1 or before.get('cohortIdentity') != after.get('cohortIdentity') or before.get('cohortId') != after.get('cohortId'):
        raise ValueError('Comparison requires the same pilot URL set')
    a, b = before['dates'], after['dates']; period(**a); period(**b)
    if date.fromisoformat(b['start']) <= date.fromisoformat(a['end']):
        raise ValueError('Follow-up must not overlap baseline')
    boundary = None
    if changed_at:
        changed = datetime.fromisoformat(changed_at)
        if changed.tzinfo is None: raise ValueError('Deployment time requires an explicit timezone')
        boundary = str(changed.astimezone(ZoneInfo('America/Los_Angeles')).date())
        if a['end'] >= boundary or b['start'] <= boundary:
            raise ValueError('Exclude the deployment PT day from both windows')
    per_page = []
    for target in after.get('targets', []):
        url = target['url']; old, new = page_metrics(before, url), page_metrics(after, url)
        delta = {k: new[k] - old[k] for k in ('clicks', 'impressions') if k in old and k in new} if old is not None and new is not None else None
        per_page.append({'url': url, 'baselineGscWeb': old, 'followUpGscWeb': new, 'delta': delta,
                         'baselineGaAttribution': attribution_metrics(before, url), 'followUpGaAttribution': attribution_metrics(after, url)})
    return {'baselineDates': a, 'followUpDates': b, 'equalLengthDays': 28,
            'deploymentDayPT': boundary, 'publicationBoundaryVerified': boundary is not None,
            'pages': per_page, 'causalEffectEstablished': False, 'dedicatedAIVisibilityMeasured': False}


def summary(report):
    inspection_rows = report.get('inspections', [])
    passed = sum(r['response'].get('data', {}).get('inspectionResult', {}).get('indexStatusResult', {}).get('verdict') == 'PASS' for r in inspection_rows)
    result = {'dates': report['dates'], 'pilotURLs': len(report['targets']), 'googleIndexPass': passed,
            'googleIndexOtherOrUnknown': len(inspection_rows) - passed,
            'gscWebPages': report['gscWeb']['pages']['state'],
            'gscReturnedPageRows': len(report['gscWeb']['pages']['rows']),
            'ga4State': report['ga4Attribution']['state'],
            'ga4Timezone': report['ga4Attribution'].get('metadata', {}).get('timeZone', 'unknown'),
            'aiDomainMatchedAttributionRows': len(report['aiDomainMatchedAttributionRows']),
            'dedicatedAIReports': {k: v['state'] for k, v in report['dedicatedAIReports'].items()}}
    if 'comparison' in report:
        compared = report['comparison']
        result['comparison'] = {k: compared[k] for k in ('baselineDates','followUpDates','publicationBoundaryVerified','causalEffectEstablished')}
        result['comparison']['pages'] = [{k: row[k] for k in ('url','baselineGscWeb','followUpGscWeb','delta','baselineGaAttribution','followUpGaAttribution')} for row in compared['pages']]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Read GSC/GA APIs only; never submit URLs or modify settings')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--start'); parser.add_argument('--end')
    parser.add_argument('--compare', type=Path, help='Existing private baseline for a non-overlapping 28-day comparison')
    parser.add_argument('--changed-at', help='Actual deployment ISO timestamp with timezone; required with --compare')
    parser.add_argument('--report', type=Path, help='Summarize a saved snapshot without network or raw query disclosure')
    args = parser.parse_args()
    try:
        if args.report:
            if args.live or args.output or args.start or args.end or args.compare or args.changed_at:
                raise ValueError('--report cannot query APIs or write files')
            print(json.dumps(summary(json.loads(args.report.read_text())), ensure_ascii=False, indent=2)); return 0
        cohort = json.loads(COHORT.read_text()); targets(cohort)
        now = datetime.now(timezone.utc)
        if bool(args.start) != bool(args.end): raise ValueError('Specify both --start and --end')
        dates = period(args.start, args.end) if args.start else period(*windows(now)['current'])
        settled_end = windows(now)['current'][1]
        if dates['end'] > settled_end: raise ValueError('Use a window ending at least three PT calendar days ago')
        if bool(args.compare) != bool(args.changed_at): raise ValueError('Use --compare and --changed-at together')
        if not args.live:
            if args.output or args.compare: raise ValueError('Writing requires --live')
            print(json.dumps({'mode': 'plan-only', 'dates': dates, 'targets': targets(cohort), 'settingsModified': False}, indent=2)); return 0
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
        report['sourceHashes'] = {r['url']: hashlib.sha256((ROOT / f'src/content/posts/{r["language"]}/{r["key"]}.md').read_bytes()).hexdigest() for r in targets(cohort)}
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
