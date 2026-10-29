#!/usr/bin/env node
/** Render both pending news and technical editions in a disposable committed snapshot. */
import {readFile,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {withSnapshot,root,releases,checks,fixturePlan,stageFixtures} from './translation-preview.mjs';
const exec=promisify(execFile);

export async function previewTechnicalTranslations(base=root){
  const result=await withSnapshot(base,async(sandbox)=>{
    const {inspectTechnicalBatch,technicalFixturePlan,stageTechnicalFixtures,checkTechnicalPublications}=await import(pathToFileURL(join(sandbox,'scripts/technical-publication.mjs')).href);
    const {inspectRelease}=await import(pathToFileURL(join(sandbox,'scripts/translation-release.mjs')).href);
    const {translationSchema}=await import(pathToFileURL(join(sandbox,'src/lib/translation-schema.ts')).href);
    const batch=await inspectTechnicalBatch(sandbox),existing=await checkTechnicalPublications(sandbox);
    const published=new Set(existing.records.map(r=>`${r.data.language}-${r.data.translationKey}`));
    const at=new Date().toISOString();
    const technical=technicalFixturePlan(batch,at).filter(r=>!published.has(r.key));
    const reports=[];for(const manifest of releases)reports.push(await inspectRelease(manifest,sandbox));
    // Separate synthetic timestamps exercise a feed containing both kinds of entry.
    const news=fixturePlan(reports,new Date(new Date(at).getTime()-1000).toISOString());
    const markerPath=join(sandbox,'.translation-preview-fixture.json');
    const marker=JSON.parse(await readFile(markerPath,'utf8'));
    await writeFile(markerPath,JSON.stringify({...marker,technicalFixtureKeys:technical.map(r=>r.key),fixtureKeys:news.records.map(r=>r.path.split('/').at(-1).replace(/\.json$/,''))}));
    await stageTechnicalFixtures(sandbox,base,technical);
    await stageFixtures(sandbox,base,news.records,data=>translationSchema.parse(data));
    const summaries=[];
    const commands=[...checks,...(technical.length?[['python3',['-B','scripts/check_technical_preview.py']]]:[])];
    for(const [tool,args] of commands){
      let stdout;
      try{({stdout}=await exec(tool==='node'?process.execPath:tool,args,{cwd:sandbox,timeout:300000,maxBuffer:16*1024*1024}));}
      catch(error){const safe=new Error(`Isolated technical step failed: ${args.at(-1)}`);safe.cause=error;throw safe;}
      for(const line of stdout.split('\n'))if(line.startsWith('[ok]'))summaries.push(line);
    }
    const indexes={};
    for(const lang of Object.keys(JSON.parse(await readFile(join(sandbox,'src/lib/locales.json'),'utf8')).locales))indexes[lang]=JSON.parse(await readFile(join(sandbox,`dist/${lang}/search-index.json`),'utf8')).length;
    const sitemap=await readFile(join(sandbox,'dist/sitemap.xml'),'utf8');
    return {technicalFixtureEditions:technical.length,existingTechnicalPublications:existing.approvedEditions,newsFixtureEditions:news.records.length,
      previewArticlesByLanguage:indexes,previewArticles:Object.values(indexes).reduce((a,b)=>a+b,0),previewSitemapURLs:(sitemap.match(/<loc>/g)??[]).length,
      checks:summaries,realUserApprovalRecorded:false,workingPublicationFilesChanged:false,workingDistChanged:false};
  });
  return {...result,temporarySnapshotRemoved:true};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)previewTechnicalTranslations().then(r=>console.log(JSON.stringify(r,null,2))).catch(error=>{console.error(error.message);if(error.cause)console.error(error.cause.stdout?.slice(-5000),error.cause.stderr?.slice(-5000));process.exitCode=1;});
