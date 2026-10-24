#!/usr/bin/env python3
"""Reproducible archive inventory and bounded HTTPS source checks; not a fact checker."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile
from threading import Semaphore
from urllib.parse import urlsplit

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.title=''; self.in_title=False; self.meta={}
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta':self.meta[attrs.get('property',attrs.get('name',''))]=attrs.get('content','')
    def handle_endtag(self, tag):
        if tag=='title':self.in_title=False
    def handle_data(self, text):
        if self.in_title:self.title+=text


def inventory(root):
    result=[]
    for file in sorted((root/'src/content/posts/ko').glob('*.md')):
        source=file.read_text();body=source.split('---\n',2)[2]
        articles=[]
        for match in re.finditer(r'^### (\d+)\. (.+)\n([\s\S]*?)(?=^### \d+\. |^## 활용 가이드|\Z)',body,re.M):
            block=match[3];link=re.search(r'^- 링크: \[(https?://[^\]]+)\]',block,re.M)
            description=re.search(r'^- (한국어 AI 요약|출처 제공 설명|정정 요약|한줄 요약): (.*)$',block,re.M)
            articles.append({'number':int(match[1]),'title':match[2],'url':link[1] if link else None,
                'summary':description[2] if description else '', 'summary_kind':description[1] if description else None})
        result.append({'file':str(file.relative_to(root)),'kind':'digest' if file.name.startswith('digest-') else 'post','articles':articles})
    return result


def inspect_url(url, directory, locks, require_html=True):
    key=hashlib.sha256(url.encode()).hexdigest()
    destination=directory/f'{key}.html'
    host=urlsplit(url).hostname
    if urlsplit(url).scheme!='https':return {'url':url,'status':'invalid_scheme'}
    with locks[host]:
        try:
            proc=subprocess.run(['curl','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--max-redirs','5','--max-time','15','--connect-timeout','5','--max-filesize','2500000','--user-agent','youdozi-archive-review/1.0','--output',str(destination),'--write-out','%{json}',url],capture_output=True,text=True,timeout=18)
            info=json.loads(proc.stdout or '{}');code=info.get('http_code',0)
            result={'url':url,'http_status':code,'final_url':info.get('url_effective',url), 'content_type':info.get('content_type','')}
            if proc.returncode:result['status']='network_error';result['curl_exit']=proc.returncode;return result
            result['status']='reachable' if code==200 else 'not_found' if code in (404,410) else 'restricted' if code in (401,403,429) else 'unverified_response' if code==202 else 'http_error'
            if code==200 and destination.exists():
                data=destination.read_bytes();parser=Metadata();parser.feed(data.decode('utf-8',errors='replace'))
                result['title']=re.sub(r'\s+',' ',parser.meta.get('og:title') or parser.title).strip()[:300]
                result['sha256']=hashlib.sha256(data).hexdigest()
                if require_html and 'html' not in info.get('content_type',''):result['status']='unexpected_content_type'
            return result
        except (subprocess.TimeoutExpired,ValueError,OSError):return {'url':url,'status':'network_error'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='.pipeline/archive-source-review.json');parser.add_argument('--workers',type=int,default=8)
    parser.add_argument('--cache-dir',default='/tmp/youdozi-review-pages');parser.add_argument('--news-only', action='store_true');args=parser.parse_args()
    if not 1 <= args.workers <= 16:parser.error('workers must be between 1 and 16')
    posts=inventory(Path('.'));urls=sorted({a['url'] for p in posts for a in p['articles'] if a['url']})
    technical=set()
    if not args.news_only:
        for file in Path('src/content/posts/ko').glob('*.md'):
            if file.name.startswith('digest-'):continue
            technical.update(re.findall(r'^  - "(https://[^\"]+)"$',file.read_text().split('---\n',2)[1],re.M))
    all_urls=sorted(set(urls)|technical)
    cache=Path(args.cache_dir);cache.mkdir(parents=True,exist_ok=True)
    locks={urlsplit(u).hostname:Semaphore(2) for u in all_urls}
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'scope':'URL availability and page-title metadata only; this does not verify article claims','post_count':len(posts),'digest_article_count':len(urls),'sources':[], 'technical_reference_sources':[]}
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures={executor.submit(inspect_url,u,cache,locks,u in urls):u for u in all_urls}
        for future in as_completed(futures):
            result=future.result()
            if result['url'] in urls:report['sources'].append(result)
            if result['url'] in technical:report['technical_reference_sources'].append(result)
            if (len(report['sources']) + len(report['technical_reference_sources']))%50==0:
                print(f"[progress] {len(report['sources'])}/{len(all_urls)} {dict(Counter(s['status'] for s in report['sources']))}",flush=True)
                output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    report['technical_reference_sources'].sort(key=lambda s:s['url'])
    report['sources'].sort(key=lambda s:s['url']);report['counts']=dict(Counter(s['status'] for s in report['sources']))
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
