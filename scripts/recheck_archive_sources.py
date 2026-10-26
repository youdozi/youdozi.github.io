#!/usr/bin/env python3
"""Recheck held evidence without changing batches, approvals or publication state."""
from __future__ import annotations
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from archive_renewal import read, write
from archive_sources import DEFAULT_EXTRACTOR, fetch_document
from ai_dev_digest import compact


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def recheck(root, *, rounds=2):
    if rounds not in (2,3):
        raise ValueError('Use 2 or 3 independent source collections')
    directory=Path(root)/'.pipeline/archive-renewal'
    manifest=read(directory/'manifest.json')
    held={r['id'] for r in manifest['items'] if r['status']=='blocked'}
    entries=[]
    for path in sorted((directory/'batches').glob('*.json')):
        batch=read(path)
        entries.extend((batch,e) for e in batch['entries'] if e['id'] in held)
    urls={}
    for _,e in entries:
        previous=e.get('research',{}).get('previousDraft')
        selected=[d['url'] for d in previous['documents']] if previous else e.get('attemptedSourceUrls',[])
        urls[e['id']]=list(dict.fromkeys(selected))

    def collect(url):
        observations=[];body=None
        for _ in range(rounds):
            try:
                body=fetch_document(url,DEFAULT_EXTRACTOR)
                observations.append({'fetchedAt':now(),'sha256':hashlib.sha256(body.encode()).hexdigest(),'characters':len(body)})
            except (ValueError,OSError) as exc:
                observations.append({'fetchedAt':now(),'error':str(exc)})
                break  # Do not repeat an HTTP challenge or failed bounded transport cycle.
        stable=(len(observations)==rounds and all('sha256' in r for r in observations)
                and len({r['sha256'] for r in observations})==1)
        return {'url':url,'extractorVersion':DEFAULT_EXTRACTOR,'stable':stable,'observations':observations},body

    unique=list(dict.fromkeys(u for group in urls.values() for u in group))
    with ThreadPoolExecutor(max_workers=4) as pool:
        fetched=dict(zip(unique,pool.map(collect,unique)))
    results=[]
    for batch,e in entries:
        previous=e.get('research',{}).get('previousDraft')
        complete=bool(urls[e['id']]) and all(fetched[u][0]['stable'] for u in urls[e['id']])
        missing=[]
        if previous and complete:
            for lang in ('en','ko'):
                ed=previous['editions'][lang]
                for claim in ed['claims']+ed['followUp']:
                    for evidence in claim['evidence']:
                        u=previous['documents'][evidence['document_id']]['url']
                        if compact(evidence['quote']) not in compact(fetched[u][1]):
                            missing.append({'language':lang,'url':u,'quote':evidence['quote']})
        candidate=bool(previous and complete and not missing)
        item={'id':e['id'],'batchId':batch['batchId'],'title':e['editions']['ko']['title'],
              'status':'source_recheck_passed' if candidate else 'editorial_evidence_still_required' if complete else 'source_recheck_incomplete',
              'sources':urls[e['id']],'missingQuotes':missing,'publicationStateChanged':False}
        if candidate:
            draft=copy.deepcopy(previous)
            for d in draft['documents']:
                obs=fetched[d['url']][0]['observations'][-1]
                d.update(sha256=obs['sha256'],fetchedAt=obs['fetchedAt'],extractorVersion=DEFAULT_EXTRACTOR)
            item.update(proposedReviewedAt=now(),draftCandidate=draft,
                        remainingReview='Confirm primary-source policy, semantic support and human approval before promotion. This report is not an active batch or publication approval.')
        results.append(item)
    return {'schemaVersion':1,'checkedAt':now(),'extractorVersion':DEFAULT_EXTRACTOR,'rounds':rounds,
            'scope':'All blocked manifest items; selected previous-draft documents or recorded attempted URLs.',
            'publicationStateChanged':False,'sources':[fetched[u][0] for u in unique],'items':results}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path('.'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--rounds',type=int,choices=[2,3],default=2)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite an evidence report; choose a new --output path')
    report=recheck(args.repo_root,rounds=args.rounds)
    write(args.output,report)
    print(f"[ok] Rechecked {len(report['items'])} held entries; {sum(i['status']=='source_recheck_passed' for i in report['items'])} source-backed draft candidates; no publication state changed")


if __name__=='__main__':main()
