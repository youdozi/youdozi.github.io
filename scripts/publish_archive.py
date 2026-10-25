#!/usr/bin/env python3
"""Publish an explicitly approved historical batch; never publishes blocked entries."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone

from archive_renewal import (DIRECTORY, read, write, timestamp, validate_batch,
    validate_manifest, fetch_document, sync_manifest)
from render_digest_review import text as safe_text

PUBLIC = Path('src/content/renewals')


def publication(batch, entry, record, *, slug, approval, published_at):
    if entry['outcome'] != 'renewed_draft':
        raise ValueError('Blocked/unverifiable entries cannot be published')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*',slug):
        raise ValueError('Use a dated descriptive route slug')
    return {**copy.deepcopy(entry), 'schemaVersion':1, 'state':'approved', 'slug':slug,
        'source':record['source'], 'url':record['url'], 'articleNumber':record['articleNumber'],
        'sourcePublishedAt':record['sourcePublishedAt'], 'sourceFile':record['sourceFile'],
        'batchId':batch['batchId'], 'reviewMethod':batch['reviewMethod'], 'reviewedAt':batch['reviewedAt'],
        'editionPublishedAt':{'ko':record['originalPagePublishedAt'],'en':published_at},
        'updatedAt':published_at, 'approval':approval,
        'tags':['archive-renewal']}


def validate_publication(data, manifest, *, now=None):
    """Reuse the historical claim contract while enforcing publication provenance."""
    errors=[];now=now or datetime.now(timezone.utc)
    try:
        if data['schemaVersion']!=1 or data['state']!='approved' or data['outcome']!='renewed_draft':
            return ['Only explicitly approved renewed drafts may be public']
        original=next(r for r in manifest['items'] if r['id']==data['id'])
        for key in ('source','url','sourcePublishedAt','sourceFile','articleNumber'):
            if data[key]!=original[key]:errors.append('Public original provenance changed: '+key)
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*',data['slug']) or not data['slug'].startswith(data['archiveDate']+'-'):
            errors.append('Publication slug must preserve its archive date')
        approval=data['approval'];approved=timestamp(approval['approvedAt']);published=timestamp(data['editionPublishedAt']['en'])
        if not isinstance(approval['reviewedBy'],str) or not approval['reviewedBy'].strip() or not isinstance(approval['basis'],str) or not approval['basis'].strip() or type(approval['pullRequest']) is not int or approval['pullRequest']<1:
            errors.append('Publication requires explicit human approval')
        if timestamp(data['reviewedAt'])>approved or approved>published or published>now or timestamp(data['updatedAt'])<published or timestamp(data['updatedAt'])>now:
            errors.append('Publication, review and approval timestamps are inconsistent')
        draft=copy.deepcopy(data);draft['editionPublishedAt']['en']=None
        batch={'schemaVersion':1,'state':'draft','mode':'historical','batchId':data['batchId'],
            'reviewMethod':data['reviewMethod'],'reviewedAt':data['reviewedAt'],'entries':[draft]}
        errors.extend(validate_batch(batch,manifest,now=now))
        if not isinstance(data['tags'],list) or not data['tags'] or any(not isinstance(t,str) or not t.strip() for t in data['tags']):errors.append('Invalid archive topics')
    except (KeyError,TypeError,ValueError,StopIteration,AttributeError):
        errors.append('Invalid historical publication structure')
    return errors


def patch_legacy(source, publications):
    """Keep original headings/links/dates and unrelated article blocks byte-for-byte."""
    front,header,body=source.split('---\n',2)
    latest=max(p['updatedAt'] for p in publications)
    for p in publications:
        number=p['articleNumber'];edition=p['editions']['ko']
        pattern=rf'(^### {number}\. [^\n]+\n)([\s\S]*?)(?=^### \d+\. |^## 활용 가이드|\Z)'
        match=re.search(pattern,body,re.M)
        if not match or p['url'] not in match[2]:raise ValueError('Original article block not found')
        preserved=[line for line in match[2].splitlines() if line.startswith(('- 출처:','- 발행일:','- 링크:'))]
        if len(preserved)!=3:raise ValueError('Missing historical source metadata')
        lines=['',*preserved,'- 정정 요약: '+' '.join(safe_text(c['text']) for c in edition['claims']),
            '- 리뉴얼 검토일: '+p['reviewedAt'][:10],
            f'- 보강 원고: [한국어](/ko/digest/{p["slug"]}/) · [English](/en/digest/{p["slug"]}/)','']
        if edition['followUp']:
            lines+=['**검토 시점 후속 확인**','']+['- '+safe_text(c['text']) for c in edition['followUp']]+['']
        lines+=['**검토 초점 · 직접 적용 결과가 아닌 편집 제안**','',safe_text(p['reviewFocus']['ko']),'']
        for c in edition['claims']+edition['followUp']:
            for e in c['evidence']:lines+=['> '+safe_text(e['quote']),'>',f'> [인용 출처]({p["documents"][e["document_id"]]["url"]})','']
        replacement=match[1]+'\n'.join(lines)+'\n'
        body=body[:match.start()]+replacement+body[match.end():]
    updates={'updatedAt':latest,'reviewedAt':latest[:10],
        'reviewScope':'일부 기사에 승인된 한영 보강 원고와 공식 출처 근거를 반영했습니다. 표시된 기사 이외의 내용은 기존 검토 범위를 유지합니다.'}
    for key,value in updates.items():
        line=key+': '+json.dumps(value,ensure_ascii=False)
        pattern=r'^'+key+r':.*$'
        header=re.sub(pattern,lambda _:line,header,flags=re.M) if re.search(pattern,header,re.M) else header+line+'\n'
    return front+'---\n'+header+'---\n'+body


def publish(root,batch,slugs,approval,*,published_at,check_sources=True):
    root=Path(root);manifest=read(root/DIRECTORY/'manifest.json')
    errors=validate_manifest(manifest,root)+validate_batch(batch,manifest)
    if errors:raise ValueError('; '.join(errors))
    renewed=[e for e in batch['entries'] if e['outcome']=='renewed_draft']
    if set(slugs)!={e['id'] for e in renewed}:raise ValueError('Explicit slug map must cover exactly the approved drafts')
    if len(set(slugs.values()))!=len(slugs):raise ValueError('Duplicate publication slugs')
    if check_sources:
        bodies={d['url']:fetch_document(d['url']) for e in renewed for d in e['documents']}
        errors=validate_batch(batch,manifest,documents=bodies)
        if errors:raise ValueError('; '.join(errors))
    originals={r['id']:r for r in manifest['items']};publications=[]
    existing_slugs={read(path)['slug'] for path in (root/PUBLIC).glob('*.json')}
    if existing_slugs.intersection(slugs.values()):raise ValueError('Refusing to reuse an existing archive route')
    for e in renewed:
        record=originals[e['id']];destination=root/PUBLIC/(e['id']+'.json')
        if destination.exists() or record['status'] not in {'awaiting_review','approved','draft_ready'}:raise ValueError('Refusing to overwrite previously published or unreviewed work')
        p=publication(batch,e,record,slug=slugs[e['id']],approval=approval,published_at=published_at)
        errors=validate_publication(p,manifest)
        if errors:raise ValueError('; '.join(errors))
        publications.append(p)
    # Compute and validate every output before writing any file.
    patches={}
    for name in {p['sourceFile'] for p in publications}:
        patches[name]=patch_legacy((root/name).read_text(),[p for p in publications if p['sourceFile']==name])
    for p in publications:
        r=originals[p['id']];r['status']='published';r['approval']=approval
        r['publication']={'file':str(PUBLIC/(p['id']+'.json')),'slug':p['slug'],'englishPublishedAt':published_at}
    errors=validate_manifest(manifest)
    if errors:raise ValueError('; '.join(errors))
    # Roll back local outputs if a write or final provenance check fails.
    originals_text={name:(root/name).read_text() for name in patches}
    old_manifest=(root/DIRECTORY/'manifest.json').read_text()
    try:
        for p in publications:write(root/PUBLIC/(p['id']+'.json'),p)
        for name,value in patches.items():(root/name).write_text(value)
        manifest=sync_manifest(root,manifest)
        write(root/DIRECTORY/'manifest.json',manifest)
        errors=validate_manifest(manifest,root)
        if errors:raise ValueError('; '.join(errors))
    except Exception:
        for name,value in originals_text.items():(root/name).write_text(value)
        for p in publications:(root/PUBLIC/(p['id']+'.json')).unlink(missing_ok=True)
        (root/DIRECTORY/'manifest.json').write_text(old_manifest)
        raise
    return publications


def check_publications(root,manifest):
    errors=[];root=Path(root);seen=set();ids=set()
    for path in sorted((root/PUBLIC).glob('*.json')):
        data=read(path);errors.extend(f'{path.name}: {e}' for e in validate_publication(data,manifest))
        if path.stem!=data.get('id'):errors.append('Public archive filename does not match ID')
        if data.get('slug') in seen:errors.append('Duplicate public archive route')
        seen.add(data.get('slug'));ids.add(data.get('id'))
        r=next((r for r in manifest['items'] if r['id']==data.get('id')),None)
        if not r or r['status']!='published' or r.get('approval')!=data.get('approval') or r.get('publication')!={'file':str(PUBLIC/path.name),'slug':data.get('slug'),'englishPublishedAt':data.get('editionPublishedAt',{}).get('en')}:
            errors.append('Public archive is not linked to an approved manifest record')
        batch_path=root/DIRECTORY/'batches'/f'{data.get("batchId")}.json'
        batch=read(batch_path) if batch_path.is_file() else {}
        entry=next((e for e in batch.get('entries',[]) if e['id']==data.get('id')),None)
        if not entry or any(data.get(k)!=entry.get(k) for k in ('editions','documents','reviewFocus','outcome','experimentStatus')) or data.get('reviewedAt')!=batch.get('reviewedAt'):
            errors.append('Public archive differs from its reviewed batch')
    for r in manifest['items']:
        if r['status']=='published' and r['id'] not in ids:errors.append('Published archive record has no public content')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',required=True,type=Path)
    parser.add_argument('--slugs',required=True,type=Path)
    parser.add_argument('--reviewed-by',required=True)
    parser.add_argument('--approval-pr',required=True,type=int)
    parser.add_argument('--approval-basis',required=True,help='Where the explicit publication instruction was received')
    parser.add_argument('--repo-root',type=Path,default=Path('.'))
    args=parser.parse_args();now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    approval={'reviewedBy':args.reviewed_by,'pullRequest':args.approval_pr,'approvedAt':now,
        'basis':args.approval_basis}
    try:
        result=publish(args.repo_root,read(args.batch),read(args.slugs),approval,published_at=now)
        print(f'[ok] Prepared {len(result)} approved archive articles for publication; blocked entries preserved')
    except (ValueError,KeyError,OSError,TypeError) as e:
        print('[error]',e);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
