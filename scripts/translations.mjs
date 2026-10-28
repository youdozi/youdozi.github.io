#!/usr/bin/env node
/** Translation preparation is private; publication requires recorded human approval. */
import {readFile,readdir,mkdir,writeFile,unlink} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import policy from '../src/lib/locales.json' with {type:'json'};
import {translationDraftSchema,translationSchema,validateTranslationSource} from '../src/lib/translation-schema.ts';
import {renewalSchema} from '../src/lib/renewal-schema.ts';

export const root=resolve(import.meta.dirname,'..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const load=async file=>JSON.parse(await readFile(file,'utf8'));
export async function sourceFor(id,base=root){
  if(!/^[0-9a-f]{16}$/.test(id))throw new Error('Invalid renewal ID');
  const bytes=await readFile(resolve(base,`src/content/renewals/${id}.json`),'utf8');
  const source=renewalSchema.parse(JSON.parse(bytes));
  if(source.id!==id)throw new Error('Source filename and renewal ID differ');
  return {source,bytes};
}
export async function prepareQueue(base=root){
  const sources=[];
  for(const file of (await readdir(resolve(base,'src/content/renewals'))).filter(f=>f.endsWith('.json')).sort()){
    const {source,bytes}=await sourceFor(file.replace(/\.json$/,''),base);
    sources.push({renewalId:source.id,sourceSha256:hash(bytes),slug:source.slug,sourceUrl:source.url,sourceUpdatedAt:source.updatedAt,edition:source.editions.en,reviewFocus:source.reviewFocus.en});
  }
  const prepared=new Map();
  try{
    for(const file of (await readdir(resolve(base,'.pipeline/translations/batches'))).filter(f=>f.endsWith('.json'))){
      const batch=await load(resolve(base,'.pipeline/translations/batches',file));
      for(const draft of await validateBatch(batch,base)){
        const key=`${draft.language}-${draft.renewalId}`;
        if(prepared.has(key))throw new Error('Duplicate translation across draft batches');
        prepared.set(key,file);
      }
    }
  }catch(error){if(error.code!=='ENOENT')throw error;}
  return {schemaVersion:1,scope:'approved-renewals',generatedAt:new Date().toISOString(),sourceCount:sources.length,languages:policy.translationLanguages,sources,tasks:sources.flatMap(s=>policy.translationLanguages.map(language=>({renewalId:s.renewalId,sourceSha256:s.sourceSha256,language,status:prepared.has(`${language}-${s.renewalId}`)?'draft':'pending',...(prepared.has(`${language}-${s.renewalId}`)?{batch:`batches/${prepared.get(`${language}-${s.renewalId}`)}`}:{})})))};
}
export async function validateBatch(batch,base=root){
  if(batch.schemaVersion!==1 || batch.state!=='draft' || !Array.isArray(batch.translations) || !batch.translations.length)throw new Error('Expected a nonempty draft translation batch');
  const seen=new Set();
  const translations=[];
  for(const raw of batch.translations){
    const draft=translationDraftSchema.parse(raw),key=`${draft.language}-${draft.renewalId}`;
    if(seen.has(key))throw new Error('Duplicate translation in batch');
    seen.add(key);
    const {source,bytes}=await sourceFor(draft.renewalId,base);
    validateTranslationSource(draft,source,bytes);
    translations.push(draft);
  }
  return translations;
}
export async function checkPublished(base=root){
  const directory=resolve(base,'src/content/translations');
  const seen=new Set();let count=0;
  for(const file of (await readdir(directory)).filter(f=>f.endsWith('.json'))){
    const data=translationSchema.parse(await load(resolve(directory,file)));
    const key=`${data.language}-${data.renewalId}`;
    if(file!==`${key}.json` || seen.has(key))throw new Error('Duplicate translation or noncanonical filename');
    seen.add(key);
    const {source,bytes}=await sourceFor(data.renewalId,base);
    validateTranslationSource(data,source,bytes);count++;
  }
  return count;
}
export async function renderReview(batch,base=root){
  const drafts=await validateBatch(batch,base);
  const lines=['# 다국어 번역 검토 초안','','의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.',''];
  for(const id of [...new Set(drafts.map(d=>d.renewalId))]){
    const {source}=await sourceFor(id,base);
    lines.push(`## ${source.editions.en.title}`,'',`원문: ${source.url}`,'',`검토 기준: 영어 보강본 ${id}, ${source.updatedAt}`,'','### 영어 기준본','');
    for(const [i,claim] of source.editions.en.claims.entries()){
      lines.push(`${i+1}. ${claim.text}`,'');
      for(const evidence of claim.evidence)lines.push(`> ${evidence.quote}`,'',`근거: ${source.documents[evidence.document_id].url}`,'');
    }
    if(source.editions.en.followUp.length){lines.push('후속 확인:','');for(const claim of source.editions.en.followUp)lines.push(`- ${claim.text}`);lines.push('');}
    lines.push(`검토 초점: ${source.reviewFocus.en}`,'');
    for(const draft of drafts.filter(d=>d.renewalId===id)){
      lines.push(`### ${policy.locales[draft.language].label} (${draft.language})`,'',draft.edition.title,'');
      for(const [i,claim] of draft.edition.claims.entries())lines.push(`${i+1}. ${claim}`,'');
      if(draft.edition.followUp.length){lines.push('후속 확인:','');for(const claim of draft.edition.followUp)lines.push(`- ${claim}`);lines.push('');}
      lines.push(`검토 초점: ${draft.reviewFocus}`,'');
    }
  }
  return lines.join('\n')+'\n';
}
export async function publishBatch(batch,approval,base=root){
  // The caller must already have explicit human authorization for this exact batch.
  const drafts=await validateBatch(batch,base);
  const now=new Date().toISOString();
  const records=drafts.map(d=>translationSchema.parse({...d,state:'approved',reviewedAt:now,publishedAt:now,updatedAt:now,approval:{...approval,approvedAt:now}}));
  const created=[];
  try{
    for(const record of records){
      const path=resolve(base,`src/content/translations/${record.language}-${record.renewalId}.json`);
      await writeFile(path,JSON.stringify(record,null,2)+'\n',{flag:'wx'});created.push(path);
    }
  }catch(error){await Promise.all(created.map(path=>unlink(path)));throw error;}
  return records;
}
async function main(){
  const {positionals,values}=parseArgs({allowPositionals:true,options:{output:{type:'string'},batch:{type:'string'},release:{type:'string'},'reviewed-by':{type:'string'},'approval-pr':{type:'string'},'approval-basis':{type:'string'}}});
  const [command]=positionals;
  if(command==='prepare'){
    if(!values.output)throw new Error('prepare requires --output');
    const output=resolve(values.output);
    if(!output.startsWith(resolve(root,'.pipeline/translations')+'/'))throw new Error('Queue output must stay in .pipeline/translations');
    const queue=await prepareQueue();await mkdir(dirname(output),{recursive:true});
    await writeFile(output,JSON.stringify(queue,null,2)+'\n',{flag:'wx'});
    console.log(`[ok] Prepared ${queue.sourceCount} sources / ${queue.tasks.length} translation tasks (${queue.tasks.filter(t=>t.status==='draft').length} drafts)`);
  }else if(command==='check'){
    const count=await checkPublished();
    let drafts=0;const seen=new Set();
    for(const file of (await readdir(resolve(root,'.pipeline/translations/batches'))).filter(f=>f.endsWith('.json'))){
      for(const draft of await validateBatch(await load(resolve(root,'.pipeline/translations/batches',file)))){
        const key=`${draft.language}-${draft.renewalId}`;if(seen.has(key))throw new Error('Duplicate translation across draft batches');seen.add(key);drafts++;
      }
    }
    console.log(`[ok] ${count} approved translations / ${drafts} private drafts validated`);
  }else if(command==='validate'){
    if(!values.batch)throw new Error('validate requires --batch');
    console.log(`[ok] ${(await validateBatch(await load(values.batch))).length} private drafts validated`);
  }else if(command==='review'){
    if(!values.batch || !values.output)throw new Error('review requires --batch and --output');
    const output=resolve(values.output);
    if(!output.startsWith(resolve(root,'.pipeline/translations')+'/'))throw new Error('Review output must stay in .pipeline/translations');
    const report=await renderReview(await load(values.batch));await mkdir(dirname(output),{recursive:true});
    await writeFile(output,report,{flag:'wx'});console.log('[ok] Private translation review written');
  }else if(command==='publish'){
    if(values.batch || !values.release || !values['reviewed-by'] || !values['approval-basis'] || !/^[1-9]\d*$/.test(values['approval-pr']||''))throw new Error('Publication requires a pinned --release (not --batch), --reviewed-by, --approval-pr and --approval-basis recording explicit user approval');
    const {publishRelease}=await import('./translation-release.mjs');
    const records=await publishRelease(values.release,{reviewedBy:values['reviewed-by'],pullRequest:Number(values['approval-pr']),basis:values['approval-basis']});
    console.log(`[ok] ${records.length} approved translation files prepared for a publication PR; no deployment triggered`);
  }else throw new Error('Usage: node scripts/translations.mjs prepare|check|validate|review|publish [options]');
}
if(process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
