#!/usr/bin/env node
/** Render approval-pending translations in a disposable committed snapshot only. */
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {parseArgs} from 'node:util';
import {mkdtemp,mkdir,readFile,readdir,writeFile,rm,symlink,lstat,readlink,realpath} from 'node:fs/promises';
import {resolve,join,relative,sep} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

const exec=promisify(execFile);
export const root=resolve(import.meta.dirname,'..');
export const releases=['.pipeline/translations/releases/spanish-full-031.json','.pipeline/translations/releases/multilingual-full-032.json'];
// Deliberately omit IndexNow and all publication/deployment commands.
export const checks=[['node',['scripts/prepare-public.mjs']],['node',['node_modules/astro/bin/astro.mjs','build']],
  ...['check_site','check_seo','check_migration','check_metadata','check_listing_metadata','check_learning_paths','check_discovery','check_reader_content','check_article_images','check_translation_preview'].map(name=>['python3',['-B',`scripts/${name}.py`]]),
  ['python3',['-B','scripts/build_example_archives.py','--check-dist','dist']]];

export async function fingerprint(base,paths){
  const hash=createHash('sha256');
  async function visit(path){
    let stat;
    try{stat=await lstat(path);}catch(error){if(error.code==='ENOENT'){hash.update(relative(base,path)+'\0missing\0');return;}throw error;}
    hash.update(relative(base,path)+'\0');
    if(stat.isSymbolicLink())hash.update('symlink\0'+await readlink(path));
    else if(stat.isDirectory())for(const name of (await readdir(path)).sort())await visit(join(path,name));
    else hash.update(await readFile(path));
    hash.update('\0');
  }
  for(const path of paths)await visit(resolve(base,path));
  return hash.digest('hex');
}

export function fixturePlan(reports,at=new Date().toISOString()){
  const seen=new Set(),records=[];let existing=0;
  for(const report of reports){
    if(report.summary.blocked)throw new Error('A release has blocked editions; preview cancelled');
    for(const item of report.editions){
      if(seen.has(item.key))throw new Error('Duplicate edition across preview releases');
      seen.add(item.key);
      if(item.status==='already-published'){existing++;continue;}
      if(item.status!=='awaiting-approval'||!item.draft||item.publicationFile!==`src/content/translations/${item.key}.json`
          ||item.key!==`${item.draft.language}-${item.draft.renewalId}`)throw new Error('Invalid preview edition');
      records.push({path:item.publicationFile,data:{...item.draft,state:'approved',reviewedAt:at,publishedAt:at,updatedAt:at,
        approval:{reviewedBy:'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL',pullRequest:Number.MAX_SAFE_INTEGER,
          approvedAt:at,basis:'Disposable isolated test fixture only. NOT a user publication approval.'}}});
    }
  }
  return {records,alreadyPublished:existing};
}

export async function stageFixtures(sandbox,actualRoot,records,validate){
  const base=await realpath(sandbox),actual=await realpath(actualRoot);
  if(base===actual||base.startsWith(actual+sep)||actual.startsWith(base+sep))throw new Error('Preview must be outside the working repository');
  const marker=JSON.parse(await readFile(join(base,'.translation-preview-fixture.json'),'utf8'));
  if(marker.fixtureOnly!==true||marker.actualRoot!==actual)throw new Error('Missing isolated preview marker');
  const directory=await realpath(join(base,'src/content/translations'));
  if(directory!==join(base,'src/content/translations'))throw new Error('Preview translations directory must not be a symlink');
  const prepared=records.map(record=>{
    if(!/^src\/content\/translations\/(?:zh-CN|ja|de|fr|ru|es)-[a-f0-9]{16}\.json$/.test(record.path))throw new Error('Invalid preview destination');
    return {path:join(base,record.path),data:validate(record.data)};
  });
  for(const record of prepared)await writeFile(record.path,JSON.stringify(record.data,null,2)+'\n',{flag:'wx'});
}

async function command(command,args,cwd){
  try{return await exec(command==='node'?process.execPath:command,args,{cwd,timeout:300000,maxBuffer:16*1024*1024});}
  catch{throw new Error(`Isolated preview step failed: ${command==='node'?(args[0]??'node'):command==='python3'?args.at(-1):command}`);}
}

export async function withSnapshot(base,work){
  const actual=await realpath(base);
  const protectedPaths=['src/content','.pipeline/translations','.pipeline/technical-translations','dist'];
  const before=await fingerprint(actual,protectedPaths);
  const directory=await mkdtemp(join(tmpdir(),'youdozi-translation-preview-'));
  const sandbox=join(directory,'site');
  try{
    await mkdir(sandbox);
    const {stdout}=await exec('git',['rev-parse','HEAD'],{cwd:actual});const commit=stdout.trim();
    await exec('git',['archive','--format=tar','--output',join(directory,'snapshot.tar'),commit],{cwd:actual});
    await exec('tar',['-xf',join(directory,'snapshot.tar'),'-C',sandbox]);
    await writeFile(join(sandbox,'.translation-preview-fixture.json'),JSON.stringify({fixtureOnly:true,actualRoot:actual}),{flag:'wx'});
    await symlink(await realpath(join(actual,'node_modules')),join(sandbox,'node_modules'),'dir');
    return {...await work(sandbox,commit),sourceCommit:commit,fixtureOnly:true};
  }finally{
    await rm(directory,{recursive:true,force:true});
    if(await fingerprint(actual,protectedPaths)!==before)throw new Error('Protected working inputs/output changed during preview; no restoration attempted');
  }
}

export async function preview(selected=releases,base=root){
  const result=await withSnapshot(base,async(sandbox,commit)=>{
    const {inspectRelease}=await import(pathToFileURL(join(sandbox,'scripts/translation-release.mjs')).href);
    const {translationSchema}=await import(pathToFileURL(join(sandbox,'src/lib/translation-schema.ts')).href);
    const reports=[];
    for(const manifest of selected)reports.push(await inspectRelease(manifest,sandbox));
    const plan=fixturePlan(reports);
    await stageFixtures(sandbox,base,plan.records,record=>translationSchema.parse(record));
    const marker=join(sandbox,'.translation-preview-fixture.json');
    await writeFile(marker,JSON.stringify({...JSON.parse(await readFile(marker,'utf8')),fixtureKeys:plan.records.map(record=>record.path.split('/').at(-1).replace(/\.json$/,''))}));
    // All these scripts read/build locally. Neither the publisher nor npm build is called.
    const summaries=[];
    for(const [tool,args] of checks){
      const {stdout}=await command(tool,args,sandbox);
      for(const line of stdout.split('\n'))if(line.startsWith('[ok]'))summaries.push(line);
    }
    const indexes={};
    for(const lang of Object.keys(JSON.parse(await readFile(join(sandbox,'src/lib/locales.json'),'utf8')).locales)){
      indexes[lang]=JSON.parse(await readFile(join(sandbox,`dist/${lang}/search-index.json`),'utf8')).length;
    }
    const sitemap=await readFile(join(sandbox,'dist/sitemap.xml'),'utf8');
    for(const record of plan.records){
      const draft=record.data,source=JSON.parse(await readFile(join(sandbox,`src/content/renewals/${draft.renewalId}.json`),'utf8'));
      const path=`/${draft.language}/digest/${source.slug}/`;
      if(!sitemap.includes(`https://youdozi.github.io${path}`))throw new Error('Preview edition missing from sitemap');
      const rows=JSON.parse(await readFile(join(sandbox,`dist/${draft.language}/search-index.json`),'utf8'));
      const row=rows.find(row=>row.url===path);
      if(!row||row.title!==draft.edition.title||[...draft.edition.claims,...draft.edition.followUp].some(text=>!row.content.includes(text)))throw new Error('Preview title or claims missing from search data');
    }
    return {pendingEditions:plan.records.length,alreadyPublishedInSelectedReleases:plan.alreadyPublished,
      publicTranslationsInPreview:(await readdir(join(sandbox,'src/content/translations'))).filter(name=>name.endsWith('.json')).length,
      previewArticlesByLanguage:indexes,previewArticleCount:Object.values(indexes).reduce((a,b)=>a+b,0),
      previewSitemapURLs:(sitemap.match(/<loc>/g)||[]).length,checks:summaries,
      realUserApprovalRecorded:false,workingPublicationFilesChanged:false,workingDistChanged:false,
      sourceNote:'Committed snapshot only; fixture timestamps are not real publication dates.'};
  });
  return {...result,temporarySnapshotRemoved:true};
}

async function main(){
  const {values}=parseArgs({options:{release:{type:'string',multiple:true}}});
  console.log(JSON.stringify(await preview(values.release??releases),null,2));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
