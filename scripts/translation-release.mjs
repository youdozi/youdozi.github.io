#!/usr/bin/env node
/** Inspect a pinned translation release without publishing or calling external services. */
import {readFile,realpath,writeFile} from 'node:fs/promises';
import {resolve,dirname,sep} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import {validateBatch,publishBatch,root} from './translations.mjs';
import {translationSchema} from '../src/lib/translation-schema.ts';
import archivePolicy from '../src/lib/archive-policy.json' with {type:'json'};

export const fileSha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;
export const valueSha256=value=>fileSha256(JSON.stringify(canonical(value)));
const fail=message=>{throw new Error(message);};
const time=value=>typeof value==='string'&&Number.isFinite(Date.parse(value))&&Date.parse(value)<=Date.now();
const hex=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
const https=url=>{try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password&&(!u.port||u.port==='443');}catch{return false;}};
const same=(a,b)=>valueSha256(a)===valueSha256(b);

async function privateFile(base,path,prefix){
  if(typeof path!=='string'||path.startsWith('/')||path.includes('\\'))fail('Expected a relative repository JSON path');
  const directory=await realpath(resolve(base,prefix));
  const target=await realpath(resolve(base,path));
  if(!target.startsWith(directory+sep)||!target.endsWith('.json'))fail('Release file escapes its allowed directory');
  return target;
}
function checkStoredEvidence(report,source){
  if(!time(report.checkedAt))fail('Invalid source observation timestamp');
  const item=report.items?.find(i=>i.renewalId===source.id);
  const expected=[...source.editions.en.claims,...source.editions.en.followUp].flatMap(c=>c.evidence.map(e=>({document:source.documents[e.document_id].url,quote:e.quote})));
  if(item?.allEvidencePresent!==true||item.checks?.length!==expected.length)fail('Source evidence remains incomplete');
  for(const [i,e] of expected.entries()){
    const c=item.checks[i],doc=report.documents?.find(d=>d.url===e.document);
    if(c.present!==true||c.document!==e.document||c.quote!==e.quote||doc?.status!=='fetched'||!hex(doc.sha256))fail('Source evidence does not match the frozen source');
  }
}
function checkSupplement(report,source,sourceSha256){
  if(report.schemaVersion!==1||report.state!=='verified-with-alternate-primary-sources'||report.renewalId!==source.id||report.sourceSha256!==sourceSha256||!time(report.reviewedAt))fail('Supplement does not match the source revision');
  if(report.originalSourceRecovered!==false||!Array.isArray(report.documents)||!report.documents.length)fail('Supplement must distinguish alternate evidence from original URL recovery');
  for(const d of report.documents){
    if(!https(d.url)||!archivePolicy.primaryHosts.includes(new URL(d.url).hostname)||!time(d.observedAt)||d.transport!=='web.run'||d.hashScope!=='quoted-excerpts-only'||!Array.isArray(d.quotes)||!d.quotes.length||d.quotes.some(q=>typeof q!=='string'||!q.trim())||d.excerptsSha256!==valueSha256(d.quotes))fail('Invalid supplemental primary evidence');
  }
  const expected=['claims','followUp'].flatMap(section=>source.editions.en[section].map((c,index)=>({section,index,textSha256:valueSha256(c.text)})));
  if(report.coverage?.length!==expected.length)fail('Supplement omits a source claim');
  for(const [i,e] of expected.entries()){
    const c=report.coverage[i];
    if(c.section!==e.section||c.index!==e.index||c.textSha256!==e.textSha256||!Number.isInteger(c.document)||!report.documents[c.document])fail('Supplement claim coverage differs from the source');
  }
}
export async function inspectRelease(manifestPath,base=root){
  const path=await privateFile(base,manifestPath,'.pipeline/translations/releases');
  const manifest=JSON.parse(await readFile(path,'utf8'));
  if(manifest.schemaVersion!==1||manifest.state!=='awaiting-publication-approval'||manifest.approval!==null||!time(manifest.createdAt)||typeof manifest.releaseId!=='string'||!Array.isArray(manifest.editions)||!manifest.editions.length)fail('Expected a nonempty approval-pending release ledger');
  const cache=new Map(),batches=new Map(),seen=new Set();
  async function pinned(ref,prefix){
    if(!ref||!hex(ref.sha256))fail('Missing file hash');
    const key=ref.path+'\0'+ref.sha256;
    if(cache.has(key))return cache.get(key);
    const bytes=await readFile(await privateFile(base,ref.path,prefix));
    if(fileSha256(bytes)!==ref.sha256)fail('Pinned file changed: '+ref.path);
    const value=JSON.parse(bytes.toString('utf8'));cache.set(key,value);return value;
  }
  const editions=[];
  for(const row of manifest.editions){
    if(typeof row.key!=='string'||seen.has(row.key))fail('Duplicate or invalid release edition key');
    seen.add(row.key);
    const item={key:row.key,title:row.title,url:row.url,status:'blocked',reasons:[]};
    try{
      const batch=await pinned(row.batch,'.pipeline/translations/batches');
      let drafts=batches.get(row.batch.path);
      if(!drafts){drafts=await validateBatch(batch,base);batches.set(row.batch.path,drafts);}
      const draft=drafts.find(d=>`${d.language}-${d.renewalId}`===row.key);
      if(!draft||!hex(row.draftSha256)||valueSha256(draft)!==row.draftSha256)fail('Release draft changed or is absent from its batch');
      if(row.source?.path!==`src/content/renewals/${draft.renewalId}.json`||row.source.sha256!==draft.sourceSha256)fail('Release source identity differs');
      const source=await pinned(row.source,'src/content/renewals');
      const expectedURL=`https://youdozi.github.io/${draft.language}/digest/${source.slug}/`;
      if(row.title!==draft.edition.title||row.url!==expectedURL)fail('Release title or URL differs from the draft');
      const review=await pinned(row.review,'.pipeline/translations/ai-reviews');
      if(review.reviewedBatchSha256?.[row.batch.path]!==row.batch.sha256||review.sourceSha256?.[row.source.path]!==row.source.sha256||!time(review.reviewedAt)||Date.parse(review.reviewedAt)<Date.parse(source.updatedAt))fail('Review does not cover the pinned draft and source');
      const evidence=await pinned(row.evidence,'.pipeline/translations/ai-reviews');
      if(row.evidence.method==='stored-excerpts')checkStoredEvidence(evidence,source);
      else if(row.evidence.method==='supplemental-primary')checkSupplement(evidence,source,row.source.sha256);
      else fail('Unknown evidence method');
      for(const finding of review.findings??[]){
        if(finding.renewalId&&finding.renewalId!==draft.renewalId)continue;
        if(finding.status==='resolved')continue;
        const evidenceTime=row.evidence.method==='supplemental-primary'?evidence.reviewedAt:evidence.checkedAt;
        if(finding.renewalId===draft.renewalId&&finding.status==='pending-external-source-recheck'&&finding.field==='external source retrieval'&&Date.parse(evidenceTime)>=Date.parse(review.reviewedAt))continue;
        fail('Unresolved translation review finding');
      }
      const publicationFile=`src/content/translations/${row.key}.json`;
      let publicBytes;
      try{publicBytes=await readFile(resolve(base,publicationFile),'utf8');}catch(e){if(e.code!=='ENOENT')throw e;}
      if(publicBytes!==undefined){
        const published=translationSchema.parse(JSON.parse(publicBytes));
        if(published.sourceSha256!==draft.sourceSha256||!same(published.edition,draft.edition)||published.reviewFocus!==draft.reviewFocus||published.language!==draft.language||published.renewalId!==draft.renewalId||Date.parse(published.reviewedAt)<Date.parse(source.updatedAt))fail('Existing publication differs from the reviewed edition');
        item.status='already-published';
      }else item.status='awaiting-approval';
      Object.assign(item,{draft,publicationFile,evidenceMethod:row.evidence.method});
    }catch(error){item.reasons.push(error.message);}
    editions.push(item);
  }
  return {releaseId:manifest.releaseId,createdAt:manifest.createdAt,approval:manifest.approval,editions,summary:{total:editions.length,awaitingApproval:editions.filter(e=>e.status==='awaiting-approval').length,alreadyPublished:editions.filter(e=>e.status==='already-published').length,blocked:editions.filter(e=>e.status==='blocked').length}};
}
export async function publishRelease(manifestPath,approval,base=root){
  // Calling this function or supplying arguments is not evidence of user authorization.
  // The operator must first obtain explicit approval for these exact editions.
  const report=await inspectRelease(manifestPath,base);
  if(report.summary.blocked)fail('Release contains blocked editions; no publication files created');
  if(report.summary.alreadyPublished)fail('Release contains already-published editions; no publication files created');
  return publishBatch({schemaVersion:1,state:'draft',batchId:report.releaseId,translations:report.editions.map(e=>e.draft)},approval,base);
}
export function renderReleaseReview(report){
  const escape=value=>String(value).replaceAll('|','\\|').replaceAll('\n',' ');
  const lines=['# 스페인어 통합 게시 전 검토 목록','','이 목록은 원고·검토·근거 파일의 고정된 해시를 검사합니다. 내용의 진실성이나 사람의 게시 승인을 자동 판정하지 않습니다. 현재 원고는 비공개이며 아래 주소는 게시 예정 URL입니다.','','원고 대조: [12편](spanish-002.md), [15편](spanish-003.md), [26편](spanish-004.md).','','Buildkite의 기존 주소 접근 실패는 보존합니다. 추가 공식 근거는 [별도 기록](../ai-reviews/2026-10-28-buildkite-supplement.json)에 남깁니다. 공개 원문·발행일·번역 본문을 변경하지 않습니다.','',`검토 대상 ${report.summary.total}편 · 검사 통과/승인 대기 ${report.summary.awaitingApproval}편 · 이미 게시 ${report.summary.alreadyPublished}편 · 차단 ${report.summary.blocked}편`,'','| 원고 | 상태 | 예정 URL |','| --- | --- | --- |'];
  for(const item of report.editions)lines.push(`| ${escape(item.title)} | ${item.status==='awaiting-approval'?'검사 통과·승인 대기':escape(item.status+' '+item.reasons.join('; '))} | ${escape(item.url)} |`);
  return lines.join('\n')+'\n';
}
async function main(){
  const {positionals,values}=parseArgs({allowPositionals:true,options:{release:{type:'string'},output:{type:'string'}}});
  if(!values.release||!['check','review'].includes(positionals[0]))fail('Usage: translation-release.mjs check|review --release PATH [--output PATH]');
  const report=await inspectRelease(values.release);
  if(positionals[0]==='review'){
    if(!values.output)fail('review requires --output');
    const directory=await realpath(resolve(root,'.pipeline/translations/reviews'));
    const parent=await realpath(dirname(resolve(values.output)));
    if((parent!==directory&&!parent.startsWith(directory+sep))||!values.output.endsWith('.md'))fail('Review output must stay in the private reviews directory');
    await writeFile(values.output,renderReleaseReview(report),{flag:'wx'});
  }
  console.log(JSON.stringify({releaseId:report.releaseId,...report.summary},null,2));
  if(report.summary.blocked)process.exitCode=1;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(e=>{console.error(e.message);process.exitCode=1;});
