#!/usr/bin/env node
/** Prepare approved technical editions. All commands default to read-only checks. */
import {readFile,readdir,realpath,mkdir,writeFile,unlink,rm,lstat} from 'node:fs/promises';
import {resolve,relative,dirname,basename,sep} from 'node:path';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import {pathToFileURL} from 'node:url';
import {parse} from 'yaml';
import {inspectTechnicalTranslations} from './check-technical-translations.mjs';
import {technicalPublicationSchema} from '../src/lib/technical-publication-schema.ts';
export const root=resolve(import.meta.dirname,'..');
export const manifestPath='.pipeline/technical-translations/batch-050/manifest.json';
export const sha=raw=>createHash('sha256').update(raw).digest('hex');
export function readArticle(raw){
  const match=/^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(raw);
  if(!match)throw new Error('Missing technical frontmatter');
  return {data:parse(match[1]),body:match[2]};
}
export const serializeArticle=(data,body)=>`---\n${JSON.stringify(data,null,2)}\n---\n${body}`;
export const assetURL=(language,key)=>`/assets/diagrams/technical/${language}-${key}.svg`;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);

export async function inspectTechnicalBatch(base=root){
  const summary=await inspectTechnicalTranslations(base,manifestPath);
  const bytes=await readFile(resolve(base,manifestPath),'utf8'),manifest=JSON.parse(bytes);
  const editions=[];
  for(const row of manifest.editions){
    const draft=readArticle(await readFile(resolve(base,row.draft.path),'utf8'));
    const source=readArticle(await readFile(resolve(base,row.source.path),'utf8'));
    const {language,translationKey:key}=row;
    const body=draft.body.replace(`](${key}.svg)`,`](${assetURL(language,key)})`);
    editions.push({key:row.key,path:`src/content/technical-translations/${language}/${key}.md`,body,
      diagramPath:row.diagram.path,diagramSha256:row.diagram.sha256,
      data:{schemaVersion:1,state:'approved',language,translationKey:key,routeSlug:source.data.routeSlug,kind:'post',
        title:draft.data.title,description:draft.data.description,categories:source.data.categories??[],tags:source.data.tags??[],
        sourcePath:row.source.path,sourceSha256:row.source.sha256,draftSha256:row.draft.sha256,
        manifestPath,manifestSha256:sha(bytes)}});
  }
  return {summary,manifestSha256:sha(bytes),editions};
}
export function publicationPlan(batch,approval,at=new Date().toISOString()){
  if(approval?.kind!=='human'||!approval.reviewedBy?.trim()||!approval.basis?.trim()||!Number.isSafeInteger(approval.pullRequest)||approval.pullRequest<=0||approval.pullRequest===Number.MAX_SAFE_INTEGER)throw new Error('Explicit human approval details required');
  return batch.editions.map(edition=>({...edition,data:technicalPublicationSchema.parse({...edition.data,publishedAt:at,updatedAt:at,approval:{...approval,approvedAt:at}})}));
}
export function technicalFixturePlan(batch,at=new Date().toISOString()){
  return batch.editions.map(edition=>({...edition,data:technicalPublicationSchema.parse({...edition.data,publishedAt:at,updatedAt:at,
    approval:{kind:'render-fixture',reviewedBy:'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL',pullRequest:Number.MAX_SAFE_INTEGER,approvedAt:at,basis:'Disposable isolated rendering fixture only; NOT a user publication approval.'}})}));
}
export async function validatePublishedEdition(data,body,batch,base=root){
  const record=technicalPublicationSchema.parse(data);
  const edition=batch.editions.find(e=>e.key===`${record.language}-${record.translationKey}`);
  if(!edition)throw new Error('Publication not present in pinned technical batch');
  for(const [field,value] of Object.entries(edition.data))if(!same(record[field],value))throw new Error(`Technical publication differs from reviewed ${field}`);
  if(body!==edition.body)throw new Error('Published technical body differs from reviewed draft');
  const source=readArticle(await readFile(resolve(base,record.sourcePath),'utf8')).data;
  if(new Date(record.approval.approvedAt)<new Date(source.updatedAt??source.publishedAt))throw new Error('Approval precedes source revision');
  if(record.approval.kind==='render-fixture'){
    const actual=await realpath(base);
    const marker=JSON.parse(await readFile(resolve(actual,'.translation-preview-fixture.json'),'utf8'));
    const original=await realpath(marker.actualRoot);
    if(basename(actual)!=='site'||!/^youdozi-translation-preview-[A-Za-z0-9_-]+$/.test(basename(dirname(actual))))throw new Error('Synthetic approval requires a disposable preview directory');
    try{await lstat(resolve(actual,'.git'));throw new Error('Synthetic approval is forbidden in a Git checkout');}catch(error){if(error.code!=='ENOENT')throw error;}
    if(marker.fixtureOnly!==true||original===actual||actual.startsWith(original+sep)||original.startsWith(actual+sep)||!marker.technicalFixtureKeys?.includes(edition.key))throw new Error('Synthetic approval requires an isolated technical preview marker');
  }
  return record;
}
export async function publishedTechnicalFiles(base=root){
  base=await realpath(base);
  const directory=resolve(base,'src/content/technical-translations'),files=[];
  if(await realpath(directory)!==directory)throw new Error('Technical publications directory must not be a symlink');
  for(const item of await readdir(directory,{withFileTypes:true})){
    if(item.name==='.gitkeep'&&item.isFile())continue;
    if(!item.isDirectory()||!['zh-CN','ja','de','fr','ru','es'].includes(item.name))throw new Error('Unknown technical publication directory or file');
    for(const file of await readdir(resolve(directory,item.name))){
      const path=`src/content/technical-translations/${item.name}/${file}`;
      if(!/^\d{4}-\d{2}-\d{2}-[a-z0-9.-]+\.md$/.test(file)||await realpath(resolve(base,path))!==resolve(base,path))throw new Error('Invalid technical publication filename or symlink');
      files.push(path);
    }
  }
  return files;
}
export async function checkTechnicalPublications(base=root){
  base=await realpath(base);
  const paths=await publishedTechnicalFiles(base);
  const batch=await inspectTechnicalBatch(base),records=[];
  for(const path of paths){
    const {data,body}=readArticle(await readFile(resolve(base,path),'utf8'));
    const record=await validatePublishedEdition(data,body,batch,base);
    if(path!==`src/content/technical-translations/${record.language}/${record.translationKey}.md`)throw new Error('Publication path and identity differ');
    records.push({path,data:record,body});
  }
  return {approvedEditions:records.length,records,pendingEditions:batch.editions.length-records.length};
}
async function writeRecords(base,records){
  base=await realpath(base);
  const directory=resolve(base,'src/content/technical-translations');
  if(await realpath(directory)!==directory)throw new Error('Technical output directory must not be a symlink');
  const created=[];
  try{
    for(const record of records){
      const target=resolve(base,record.path);
      if(record.path!==`src/content/technical-translations/${record.data.language}/${record.data.translationKey}.md`)throw new Error('Invalid publication destination');
      await mkdir(dirname(target),{recursive:true});
      if(await realpath(dirname(target))!==dirname(target))throw new Error('Technical output language must not be a symlink');
      await writeFile(target,serializeArticle(record.data,record.body),{flag:'wx'});created.push(target);
    }
  }catch(error){await Promise.all(created.map(path=>unlink(path)));throw error;}
  return created.length;
}
export async function prepareApprovedTechnicalBatch(base,approval,expectedManifestSha256){
  const batch=await inspectTechnicalBatch(base);
  if(expectedManifestSha256!==batch.manifestSha256)throw new Error('Approval must name the exact reviewed manifest hash');
  const records=publicationPlan(batch,approval);
  // Validate the entire fixed set before the first write; wx prevents overwriting existing editions.
  for(const record of records)await validatePublishedEdition(record.data,record.body,batch,base);
  return writeRecords(base,records);
}
export async function stageTechnicalFixtures(sandbox,actualRoot,records){
  const actual=await realpath(actualRoot),base=await realpath(sandbox);
  if(actual===base||base.startsWith(actual+sep)||actual.startsWith(base+sep))throw new Error('Technical fixtures require an isolated snapshot');
  const marker=JSON.parse(await readFile(resolve(base,'.translation-preview-fixture.json'),'utf8'));
  if(marker.actualRoot!==actual||marker.fixtureOnly!==true)throw new Error('Missing technical isolation marker');
  const batch=await inspectTechnicalBatch(base);
  for(const record of records){
    if(record.data.approval.kind!=='render-fixture')throw new Error('Expected synthetic technical record');
    await validatePublishedEdition(record.data,record.body,batch,base);
  }
  return writeRecords(base,records);
}
export async function prepareTechnicalAssets(base=root){
  base=await realpath(base);
  const result=await checkTechnicalPublications(base);
  const destination=resolve(base,'public/assets/diagrams/technical');
  await mkdir(dirname(destination),{recursive:true});
  if(await realpath(dirname(destination))!==dirname(destination))throw new Error('Technical asset parent must not be a symlink');
  // This generated namespace is owned solely by this preparer; remove withdrawn editions too.
  await rm(destination,{recursive:true,force:true});
  if(!result.records.length)return 0;
  const batch=await inspectTechnicalBatch(base);await mkdir(destination);
  for(const record of result.records){
    const edition=batch.editions.find(e=>e.key===`${record.data.language}-${record.data.translationKey}`);
    const svg=await readFile(resolve(base,edition.diagramPath));
    if(sha(svg)!==edition.diagramSha256)throw new Error('Reviewed technical SVG changed');
    await writeFile(resolve(base,'public'+assetURL(record.data.language,record.data.translationKey)),svg,{flag:'wx'});
  }
  return result.records.length;
}
async function main(){
  const {positionals,values}=parseArgs({allowPositionals:true,options:{'reviewed-by':{type:'string'},'approval-pr':{type:'string'},'approval-basis':{type:'string'},'manifest-sha256':{type:'string'}}});
  const command=positionals[0]??'check';
  if(command==='check'){
    const {records,...summary}=await checkTechnicalPublications();console.log(JSON.stringify(summary,null,2));
  }else if(command==='publish'){
    if(!/^[1-9]\d*$/.test(values['approval-pr']??'')||!values['manifest-sha256'])throw new Error('publish requires exact manifest hash, reviewer, approval PR and explicit approval basis');
    const count=await prepareApprovedTechnicalBatch(root,{kind:'human',reviewedBy:values['reviewed-by'],pullRequest:Number(values['approval-pr']),basis:values['approval-basis']},values['manifest-sha256']);
    console.log(JSON.stringify({preparedEditions:count,deployed:false}));
  }else throw new Error('Usage: technical-publication.mjs check|publish [explicit approval details]');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
