#!/usr/bin/env node
/** Create a private offline comparison of committed, approval-pending translations. */
import {readFile,realpath,mkdir,open,unlink,lstat} from 'node:fs/promises';
import {constants} from 'node:fs';
import {resolve,dirname,relative,join,sep,extname} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify,parseArgs} from 'node:util';
import {randomBytes,createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {root,releases,withSnapshot} from './translation-preview.mjs';
import {mountReview} from './translation-review-client.mjs';

const exec=promisify(execFile);
const github='https://github.com/youdozi/youdozi.github.io';
export function safeHTTPS(value){const url=new URL(value);if(url.protocol!=='https:'||url.username||url.password)throw new Error('Review links must use credential-free HTTPS');return url.href;}
export function reviewEntry(item,source,row,review,commit){
  if(!/^[a-f0-9]{40}$/.test(commit)||item.status!=='awaiting-approval'||!item.draft)throw new Error('Expected a pinned pending edition');
  const draft=item.draft;
  function pairs(section){
    if(source.editions.en[section].length!==draft.edition[section].length)throw new Error('Review comparison omits or adds a source claim');
    return source.editions.en[section].map((claim,i)=>({english:claim.text,translated:draft.edition[section][i],
      evidence:claim.evidence.map(e=>({quote:e.quote,url:safeHTTPS(source.documents[e.document_id].url)}))}));
  }
  return {key:item.key,language:draft.language,title:draft.edition.title,englishTitle:source.editions.en.title,
    sourceURL:safeHTTPS(source.url),archiveDate:source.archiveDate,sourceUpdatedAt:source.updatedAt,
    reviewedAt:review.reviewedAt,evidenceMethod:row.evidence.method,claims:pairs('claims'),followUp:pairs('followUp'),
    englishFocus:source.reviewFocus.en,translatedFocus:draft.reviewFocus,
    draftURL:`${github}/blob/${commit}/${row.batch.path}`,releaseURL:`${github}/blob/${commit}/${row.manifest}`};
}

export async function buildPacket(selected=releases,base=root){
  const result=await withSnapshot(base,async(sandbox,commit)=>{
    const {inspectRelease}=await import(pathToFileURL(join(sandbox,'scripts/translation-release.mjs')).href);
    const entries=[],seen=new Set();let alreadyPublished=0;
    for(const manifest of selected){
      const report=await inspectRelease(manifest,sandbox);
      if(report.summary.blocked)throw new Error('Blocked release; fix the pinned review before generating a packet');
      const ledger=JSON.parse(await readFile(join(sandbox,manifest),'utf8'));
      for(const item of report.editions){
        if(seen.has(item.key))throw new Error('Duplicate edition across review releases');seen.add(item.key);
        if(item.status==='already-published'){alreadyPublished++;continue;}
        const row={...ledger.editions.find(row=>row.key===item.key),manifest};
        const source=JSON.parse(await readFile(join(sandbox,row.source.path),'utf8'));
        const review=JSON.parse(await readFile(join(sandbox,row.review.path),'utf8'));
        entries.push(reviewEntry(item,source,row,review,commit));
      }
    }
    const locales=JSON.parse(await readFile(join(sandbox,'src/lib/locales.json'),'utf8'));
    return {entries,languages:Object.fromEntries(locales.translationLanguages.map(code=>[code,locales.locales[code].label])),alreadyPublished};
  });
  return {schemaVersion:1,draftOnly:true,generatedAt:new Date().toISOString(),sourceCommit:result.sourceCommit,
    languages:result.languages,entries:result.entries,alreadyPublished:result.alreadyPublished,
    realUserApprovalRecorded:false,temporarySnapshotRemoved:true};
}

export function renderPacket(packet){
  if(packet.draftOnly!==true||packet.realUserApprovalRecorded!==false||!Array.isArray(packet.entries))throw new Error('Expected an approval-pending review packet');
  const nonce=randomBytes(18).toString('base64');
  const data=JSON.stringify(packet).replace(/[<>&\u2028\u2029]/g,char=>'\\u'+char.charCodeAt(0).toString(16).padStart(4,'0'));
  if(!/^[a-f0-9]{40}$/.test(packet.sourceCommit))throw new Error('Invalid packet source commit');
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'"><title>번역 게시 전 검토</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f7f2;color:#222;font:16px/1.7 system-ui,sans-serif}main{max-width:1300px;margin:auto;padding:32px 24px}h1,h2,h3,h4{line-height:1.35}h1{font-size:30px}h2{font-size:24px;overflow-wrap:anywhere}h3{font-size:19px}a{color:#28584b;overflow-wrap:anywhere}.notice{background:#e9eee5;padding:16px 20px;border-left:4px solid #45634e}.version{font-size:13px;color:#555}.controls{display:grid;grid-template-columns:220px minmax(0,1fr);gap:16px;margin:28px 0}label{display:flex;flex-direction:column;gap:6px;font-weight:600;min-width:0}input,select,button{font:inherit;padding:10px;border:1px solid #aeb7aa;border-radius:4px;background:white;color:inherit;max-width:100%;min-width:0}input,select{width:100%}button{cursor:pointer}button:disabled{cursor:default;opacity:.45}.picker{grid-column:1/-1}.navigation{display:flex;gap:12px}#status{font-size:14px}.article-header{margin:28px 0 20px}.links{display:flex;gap:18px;flex-wrap:wrap}.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px}.pair>section{min-width:0;overflow-wrap:anywhere}.column{background:white;padding:20px;border:1px solid #d9ded4}.column ol{padding-left:22px}.column li{padding-left:5px;margin-bottom:20px}details{font-size:14px}summary{cursor:pointer}blockquote{margin:12px 0;padding-left:16px;border-left:3px solid #d9ded4}.review-notes{margin-top:28px;border-top:1px solid #d9ded4;padding-top:16px}.review-notes .pair{margin-top:16px}@media(max-width:800px){main{padding:20px 14px}.controls,.pair{grid-template-columns:minmax(0,1fr)}.picker{grid-column:auto}.column{padding:14px}h1{font-size:25px}}
</style></head><body><main><h1>번역 게시 전 검토</h1><p class="notice">이 파일은 게시 대기 원고를 비교하는 오프라인 자료입니다. 열람은 승인·게시로 기록되지 않습니다. 확인한 원고 키와 언어를 게시 요청에 명시하세요.</p><p class="version">고정 버전 <a href="${github}/tree/${packet.sourceCommit}" target="_blank" rel="noopener noreferrer">${packet.sourceCommit.slice(0,7)}</a> · 새 외부 사실 검증이나 사람의 검토를 완료했다는 뜻이 아닙니다.</p><div class="controls"><label for="language">대상 언어<select id="language"><option value="">전체 언어</option></select></label><label for="query">제목 또는 원고 키 검색<input id="query" type="search" autocomplete="off"></label><label class="picker" for="edition">검토할 원고<select id="edition"></select></label></div><div class="navigation"><button id="previous" type="button">이전 원고</button><button id="next" type="button">다음 원고</button></div><p id="status" role="status" aria-live="polite"></p><section id="comparison" aria-label="영어 기준문과 대상 언어 비교"></section><noscript><p>이 파일을 비교하려면 JavaScript를 허용하세요. 원본 원고는 저장소의 게시 전 목록에서 확인할 수 있습니다.</p></noscript></main><script id="packet-data" type="application/json" nonce="${nonce}">${data}</script><script nonce="${nonce}">(${mountReview.toString()})(document);</script></body></html>`;
}

async function canonicalTarget(path){
  let ancestor=resolve(path);const suffix=[];
  for(;;){
    try{return resolve(await realpath(ancestor),...suffix.reverse());}
    catch(error){if(error.code!=='ENOENT')throw error;const parent=dirname(ancestor);if(parent===ancestor)throw error;suffix.push(relative(parent,ancestor));ancestor=parent;}
  }
}
export async function privateDestination(output,worktrees){
  if(!worktrees.length)throw new Error('Cannot validate private output without repository worktrees');
  if(extname(output).toLowerCase()!=='.html')throw new Error('Review output must be a new HTML file');
  const target=await canonicalTarget(output);
  for(const tree of worktrees){const base=await canonicalTarget(tree);if(target===base||target.startsWith(base+sep))throw new Error('Review output must stay outside every repository worktree');}
  try{await lstat(target);throw new Error('Review output already exists');}catch(error){if(error.code!=='ENOENT')throw error;}
  return target;
}
export async function savePacket(output,html,worktrees){
  const target=await privateDestination(output,worktrees);
  await mkdir(dirname(target),{recursive:true,mode:0o700});
  await privateDestination(target,worktrees);
  const file=await open(target,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW,0o600);
  try{await file.writeFile(html);}catch(error){await file.close();await unlink(target);throw error;}
  await file.close();return target;
}
async function main(){
  const {values}=parseArgs({options:{release:{type:'string',multiple:true},output:{type:'string'}}});
  const {stdout}=await exec('git',['worktree','list','--porcelain','-z'],{cwd:root});
  const worktrees=stdout.split('\0').filter(line=>line.startsWith('worktree ')).map(line=>line.slice(9));
  if(values.output)await privateDestination(values.output,worktrees);
  const packet=await buildPacket(values.release??releases);
  const counts=Object.fromEntries(Object.keys(packet.languages).map(code=>[code,packet.entries.filter(item=>item.language===code).length]));
  const report={mode:values.output?'private-offline-file':'preview',sourceCommit:packet.sourceCommit,pendingEditions:packet.entries.length,byLanguage:counts,realUserApprovalRecorded:false,temporarySnapshotRemoved:true};
  if(values.output){const html=renderPacket(packet);report.output=await savePacket(values.output,html,worktrees);report.sha256=createHash('sha256').update(html).digest('hex');}
  console.log(JSON.stringify(report,null,2));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
