#!/usr/bin/env python3
"""Inventory and review historical news without publishing or changing live gates."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

from ai_dev_digest import ArticleParser, compact
from audit_archive import inventory
from bilingual_quality import validate_editions
from generate_dev_digest import KST, normalize_url
from render_digest_review import text as safe_text

DIRECTORY = Path('.pipeline/archive-renewal')
STATUSES = {'pending', 'researching', 'draft_ready', 'awaiting_review', 'blocked',
            'approved', 'published', 'merged_duplicate', 'unverifiable_archived', 'excluded_example'}
TERMINAL = {'published', 'merged_duplicate', 'unverifiable_archived', 'excluded_example'}
ARCHIVE_POLICY = json.loads((Path(__file__).resolve().parents[1]/'src/lib/archive-policy.json').read_text())
PRIMARY_HOSTS = set(ARCHIVE_POLICY['primaryHosts'])
PRIMARY_URLS = set(ARCHIVE_POLICY.get('primaryUrls',[]))
RISK = re.compile(r'\b(cve|vulnerabil\w*|security|compromis\w*|exposure|deprecat\w*|end.of.life|cost|pricing|benchmark|\d+%)\b', re.I)
BACKEND = re.compile(r'\b(java|jdk|jvm|spring|database|postgres\w*|kafka|redis|backend|observability|attestation|ci)\b', re.I)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a timezone-aware string')
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('timestamp needs a timezone')
    return date


def https(value):
    try:
        u = urlsplit(value)
        return u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password and u.port in (None, 443) and not re.search(r'[\s<>\\]', value)
    except (TypeError, ValueError):
        return False


def source_records(root):
    root = Path(root); records = []
    superseded = {f'digest-{p.stem}' for p in (root/'src/content/digests').glob('*.json')}
    for post in inventory(root):
        if post['kind'] != 'digest':
            continue
        path = root/post['file']; source = path.read_text(encoding='utf-8')
        header, body = source.split('---\n', 2)[1:]
        published = re.search(r'^publishedAt: "([^"\n]+)"$', header, re.M)
        if not published:
            raise ValueError(f'{path}: missing original publication timestamp')
        timestamp(published[1])
        day = path.stem.removeprefix('digest-')
        example = bool(re.search(r'^reviewStatus: "example"$', header, re.M))
        blocks = {int(m[1]): m[2] for m in re.finditer(r'^### (\d+)\. [^\n]+\n([\s\S]*?)(?=^### \d+\. |^## 활용 가이드|\Z)', body, re.M)}
        for article in post['articles']:
            if not article['url'] or not https(article['url']):
                raise ValueError(f'{path}: article {article["number"]} lacks an HTTPS source')
            block = blocks[article['number']]
            publisher = re.search(r'^- 출처: (.+)$', block, re.M)
            date = re.search(r'^- 발행일: (\d{4}-\d\d-\d\d \d\d:\d\d) \(KST\)$', block, re.M)
            source_published = datetime.strptime(date[1], '%Y-%m-%d %H:%M').replace(tzinfo=KST).isoformat() if date else None
            identity = normalize_url(article['url'])
            records.append({'id':hashlib.sha256(identity.encode()).hexdigest()[:16],
                'sourceFile':post['file'], 'articleNumber':article['number'], 'archiveDate':day,
                'originalPagePublishedAt':published[1], 'sourcePublishedAt':source_published,
                'source':publisher[1] if publisher else 'unknown', 'url':article['url'], 'originalTitle':article['title'],
                'visibility':'example' if example else 'superseded' if path.stem in superseded else 'listed',
                'priority':'risk' if RISK.search(article['title']) else 'backend' if BACKEND.search(article['title']) else 'general'})
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('duplicate source identity; resolve explicitly before creating the manifest')
    return records


def sync_manifest(root, existing=None):
    records = source_records(root)
    previous = {r['id']:r for r in (existing or {}).get('items', [])}
    missing = set(previous) - {r['id'] for r in records}
    if missing:
        raise ValueError('archive records disappeared; do not silently drop tracked work')
    items = []
    for record in records:
        old = previous.get(record['id'])
        immutable = ('sourceFile','articleNumber','archiveDate','originalPagePublishedAt','sourcePublishedAt','url')
        if old and any(old.get(k) != record[k] for k in immutable):
            raise ValueError(f'{record["id"]}: original provenance changed')
        state = {k:old[k] for k in ('status','batchId','reviewPullRequest','approval','publication') if old and k in old}
        record.update(state or {'status':'excluded_example' if record['visibility']=='example' else 'pending','batchId':None,'reviewPullRequest':None})
        items.append(record)
    return {'schemaVersion':1, 'scope':'Every preserved historical news item, including examples and superseded articles', 'items':items}


def validate_manifest(data, root=None):
    errors = []
    try:
        if data['schemaVersion'] != 1 or not isinstance(data['items'],list):
            return ['unsupported archive manifest']
        ids = set()
        for r in data['items']:
            if r['id'] in ids or r['id'] != hashlib.sha256(normalize_url(r['url']).encode()).hexdigest()[:16]:
                errors.append('duplicate or unstable archive ID')
            ids.add(r['id'])
            if r['status'] not in STATUSES:errors.append('unknown archive status')
            if r.get('batchId') is not None and not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',r['batchId']):errors.append('invalid manifest batch ID')
            if r.get('reviewPullRequest') is not None and (type(r['reviewPullRequest']) is not int or r['reviewPullRequest']<1):errors.append('invalid review PR number')
            if r['status'] in {'draft_ready','awaiting_review','blocked'} and not r.get('batchId'):errors.append('review work needs a batch')
            if r['status']=='awaiting_review' and not r.get('reviewPullRequest'):errors.append('awaiting review needs a PR')
            if (r['visibility']=='example') != (r['status']=='excluded_example'):errors.append('example data cannot become news')
            if r['status'] in {'approved','published','merged_duplicate','unverifiable_archived'}:
                approval=r.get('approval',{})
                if not approval.get('reviewedBy') or type(approval.get('pullRequest')) is not int or approval['pullRequest']<1:
                    errors.append('final dispositions require explicit recorded human review')
                if timestamp(approval.get('approvedAt'))>datetime.now(timezone.utc):errors.append('future human approval')
            timestamp(r['originalPagePublishedAt'])
            if r['sourcePublishedAt'] is not None:timestamp(r['sourcePublishedAt'])
        if root is not None:
            rebuilt = sync_manifest(root,data)
            if rebuilt != data:errors.append('manifest does not match preserved archive; run sync')
    except (KeyError, TypeError, ValueError, AttributeError):
        errors.append('invalid archive manifest structure or provenance')
    return errors


def fetch_document(url):
    if not https(url):raise ValueError('unsafe source URL')
    result=subprocess.run(['curl','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https',
        '--max-redirs','5','--max-time','25','--max-filesize','2500000','--write-out','\n%{url_effective}',url],text=True,capture_output=True,timeout=30)
    if result.returncode:raise ValueError(f'source unavailable (curl {result.returncode})')
    markup,final_url=result.stdout.rsplit('\n',1)
    if not https(final_url) or urlsplit(final_url).hostname!=urlsplit(url).hostname:raise ValueError('source redirected to a different publisher')
    parser=ArticleParser();parser.feed(markup);body=parser.extract()
    if len(body)<100:raise ValueError('article body unavailable')
    return body


def validate_batch(batch, manifest, *, now=None, documents=None):
    """documents optionally maps URLs to freshly extracted bodies for exact checks.

    Historical source dates are not subject to the live generator's seven-day gate.
    Draft dates never stand in for actual English publication or human approval.
    """
    errors=[];now=now or datetime.now(timezone.utc)
    try:
        if batch['schemaVersion']!=1 or batch['mode']!='historical' or batch['state']!='draft':return ['unsupported historical draft batch']
        if batch.get('reviewMethod')!='editorial-source-context-review':errors.append('historical drafts must declare their actual review method')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',batch['batchId']):errors.append('invalid batch ID')
        reviewed=timestamp(batch['reviewedAt'])
        if reviewed>now:errors.append('future review timestamp')
        if not isinstance(batch['entries'],list) or not 1<=len(batch['entries'])<=15:return errors+['review batch must contain 1–15 entries']
        originals={r['id']:r for r in manifest['items']};seen=set()
        for entry in batch['entries']:
            r=originals[entry['id']]
            if entry['id'] in seen:errors.append('duplicate batch entry')
            seen.add(entry['id'])
            if r['visibility']=='example':errors.append('fixture cannot be renewed as news')
            if entry['archiveDate']!=r['archiveDate'] or entry['originalPagePublishedAt']!=r['originalPagePublishedAt']:
                errors.append('historical date or original publication changed')
            if timestamp(r['originalPagePublishedAt'])>reviewed:errors.append('review precedes original publication')
            if r['sourcePublishedAt'] and timestamp(r['sourcePublishedAt'])>reviewed:errors.append('review precedes source publication')
            if entry['editionPublishedAt']!={'ko':r['originalPagePublishedAt'],'en':None}:
                errors.append('draft English edition must not be backdated or marked published')
            if entry['experimentStatus']!='not_tested':errors.append('draft cannot invent experiment evidence')
            if set(entry['reviewFocus'])!={'en','ko'} or any(not isinstance(t,str) or not t.strip() or len(t)>1200 for t in entry['reviewFocus'].values()):
                errors.append('bilingual review focus is missing')
            editions=entry['editions'];docs=entry['documents']
            if set(editions)!={'en','ko'}:errors.append('missing archive language edition')
            for edition in editions.values():
                if not isinstance(edition['title'],str) or not edition['title'].strip() or len(edition['title'])>240:errors.append('invalid archive title')
            if not re.search(r'[가-힣]',editions['ko']['title']):errors.append('Korean archive title is required')
            if entry['outcome']=='unverifiable_proposal':
                reason=entry.get('reason',{})
                if set(reason)!={'en','ko'} or any(not isinstance(t,str) or not t.strip() or len(t)>1200 for t in reason.values()) or docs or any(editions[l]['claims'] or editions[l]['followUp'] for l in ('en','ko')):
                    errors.append('unverifiable sources cannot claim verified facts')
                continue
            if entry['outcome']!='renewed_draft':errors.append('unknown draft outcome')
            if not 1<=len(docs)<=4:errors.append('renewed article requires 1–4 source documents')
            for d in docs:
                if not https(d['url']) or not re.fullmatch('[0-9a-f]{64}',d['sha256']):errors.append('invalid document URL or hash')
                if timestamp(d['fetchedAt'])>reviewed or d['extractorVersion']!='article-parser-v1':errors.append('invalid source collection provenance')
                if d['role'] not in {'primary','reporting'}:errors.append('unknown document role')
                if d['role']=='primary' and urlsplit(d['url']).hostname not in PRIMARY_HOSTS and d['url'] not in PRIMARY_URLS:errors.append('unapproved primary publisher')
                if documents is not None and hashlib.sha256(documents[d['url']].encode()).hexdigest()!=d['sha256']:
                    errors.append('source content changed; review quotes and refresh provenance explicitly')
            errors.extend(validate_editions(editions))
            follow={l:{'title':'','claims':editions[l]['followUp']} for l in ('en','ko')}
            errors.extend(validate_editions(follow))
            for language in ('en','ko'):
                edition=editions[language]
                if not isinstance(edition['title'],str) or not 1<=len(edition['title'])<=240:errors.append('invalid archive title')
                if not 2<=len(edition['claims'])<=3 or not 0<=len(edition['followUp'])<=3:errors.append('invalid historical/follow-up claim count')
                for claim in edition['claims']+edition['followUp']:
                    if not isinstance(claim['text'],str) or not claim['text'].strip() or len(claim['text'])>600:errors.append('invalid archive claim')
                    if language=='ko' and not re.search(r'[가-힣]',claim['text']):errors.append('Korean archive claim is required')
                    if not isinstance(claim['evidence'],list) or not 1<=len(claim['evidence'])<=3:errors.append('missing archive claim evidence')
                    primary=False
                    for e in claim['evidence']:
                        if type(e['document_id']) is not int or not 0<=e['document_id']<len(docs):
                            errors.append('unknown archive evidence document');continue
                        document=docs[e['document_id']]
                        primary |= document['role']=='primary'
                        if not isinstance(e['quote'],str) or not 20<=len(e['quote'])<=240:errors.append('invalid archive quote')
                        elif documents is not None and compact(e['quote']) not in compact(documents[document['url']]):errors.append('archive quote absent from source')
                    if not primary:errors.append('archive claim needs primary-source evidence')
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        errors.append('invalid historical batch structure or provenance')
    return errors


def check(root, *, check_sources=False):
    root=Path(root);directory=root/DIRECTORY
    if not directory.exists():return []
    manifest=read(directory/'manifest.json');errors=validate_manifest(manifest,root)
    ownership={}
    for path in sorted((directory/'batches').glob('*.json')):
        batch=read(path);documents=None
        if check_sources:
            documents={d['url']:fetch_document(d['url']) for e in batch['entries'] for d in e['documents']}
        errors.extend(f'{path.name}: {error}' for error in validate_batch(batch,manifest,documents=documents))
        for entry in batch['entries']:
            if entry['id'] in ownership:errors.append('an article is assigned to multiple active batches')
            ownership[entry['id']]=batch['batchId']
    for record in manifest['items']:
        if record.get('batchId') and ownership.get(record['id'])!=record['batchId']:errors.append('manifest batch assignment is missing or mismatched')
        if record['id'] in ownership and record.get('batchId')!=ownership[record['id']]:errors.append('batch entry has no matching manifest assignment')
    from publish_archive import check_publications
    errors.extend(check_publications(root,manifest))
    return errors


def render(batch,manifest):
    def safe(value):return safe_text(value).replace('&\\#64;','&#64;')
    original={r['id']:r for r in manifest['items']}
    lines=['# Historical news renewal '+batch['batchId'],'',
        '미게시 검토 초안입니다. 이 PR의 데이터는 공개 페이지·RSS·사이트맵에서 읽지 않습니다. 승인 후 게시 변환은 별도 단계입니다.','',
        '원래 뉴스 기준일과 한국어 최초 발행일을 유지하며, 영문 최초 공개일은 아직 지정하지 않았습니다.','',
        f'검토 시각: {batch["reviewedAt"]}','',
        '검증 방식: 원문 맥락을 대조한 편집 초안입니다. Gemini 검증 호출·직접 실험·사람의 승인을 수행했다는 뜻이 아닙니다.','',
        '- [ ] 당시 사실과 현재 후속 확인이 구분되어 있습니다.',
        '- [ ] 버전·수치·보안 조건과 한영 의미를 원문과 대조했습니다.',
        '- [ ] 원문 확인 불가 항목은 완료로 승인하지 않고 처리 방침을 결정했습니다.',
        '- [ ] 직접 실험했다고 표시한 항목이 없습니다.','']
    for i,e in enumerate(batch['entries'],1):
        r=original[e['id']]
        lines += [f'## {i}. {safe(r["originalTitle"])}','',f'ID: `{e["id"]}` · 원래 기준일: {r["archiveDate"]} · 상태: {e["outcome"]}','',f'원문: <{r["url"]}>','']
        for lang,label in [('en','English'),('ko','한국어')]:
            ed=e['editions'][lang];lines += [f'### {label}: {safe(ed["title"])}','']
            if e['outcome']=='unverifiable_proposal':lines += [safe(e['reason'][lang]),'']
            for name,key in [('당시 소식','claims'),('검토 시점 후속 확인','followUp')]:
                lines += ['**'+name+'**','']
                lines += ['- '+safe(c['text']) for c in ed[key]] or ['추가 검증된 사실 없음. 상태가 변하지 않았다는 뜻은 아닙니다.']
                lines += ['']
            lines += ['**검토 초점 · 편집 제안이며 직접 적용 결과가 아님**',safe(e['reviewFocus'][lang]),'']
            if ed['claims'] or ed['followUp']:
                lines += ['<details><summary>문장별 원문 근거</summary>','']
                for c in ed['claims']+ed['followUp']:
                    lines += ['- '+safe(c['text'])]
                    for q in c['evidence']:lines += ['  - “'+safe(q['quote'])+'”',f'  - <{e["documents"][q["document_id"]]["url"]}>']
                lines += ['','</details>','']
    result='\n'.join(lines)+'\n'
    if len(result)>60000:raise ValueError('split the review batch; PR body exceeds 60,000 characters')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['sync','status','check','render','next'])
    parser.add_argument('--repo-root',type=Path,default=Path('.'))
    parser.add_argument('--batch',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--check-sources',action='store_true')
    parser.add_argument('--max-items',type=int,choices=range(1,16),default=10)
    args=parser.parse_args();path=args.repo_root/DIRECTORY/'manifest.json'
    try:
        if args.command=='sync':
            result=sync_manifest(args.repo_root,read(path) if path.exists() else None);write(path,result)
            print(f'[ok] Tracked {len(result["items"])} historical items without publishing')
        elif args.command=='status':
            data=read(path);counts=Counter(r['status'] for r in data['items'])
            print(json.dumps({'total':len(data['items']),'states':dict(counts),
                'verifiedPublished':counts['published'],'unverifiableArchived':counts['unverifiable_archived'],
                'excludedExamples':counts['excluded_example'],'openRealItems':sum(r['visibility']!='example' and r['status'] not in TERMINAL for r in data['items'])},ensure_ascii=False,indent=2))
        elif args.command=='next':
            data=read(path);errors=validate_manifest(data,args.repo_root)
            if errors:raise ValueError('; '.join(errors))
            priority={'risk':0,'backend':1,'general':2}
            waiting=sorted((r for r in data['items'] if r['status']=='pending' and not r.get('batchId')),
                key=lambda r:(priority[r['priority']],r['archiveDate'],r['id']))
            print(json.dumps(waiting[:args.max_items],ensure_ascii=False,indent=2))
        elif args.command=='check':
            errors=check(args.repo_root,check_sources=args.check_sources)
            for error in errors:print('[error]',error)
            if errors:return 1
            print('[ok] Archive provenance, draft dates, bilingual claims and assignments checked')
        elif args.command=='render':
            if not args.batch or not args.output:parser.error('render requires --batch and --output')
            manifest=read(path);batch=read(args.batch);errors=validate_batch(batch,manifest)
            if errors:raise ValueError('; '.join(errors))
            args.output.write_text(render(batch,manifest),encoding='utf-8')
        return 0
    except (ValueError,KeyError,OSError,TypeError,subprocess.TimeoutExpired) as exc:
        print(f'[error] {exc}');return 1


if __name__=='__main__':raise SystemExit(main())
