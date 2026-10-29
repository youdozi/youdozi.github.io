import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,writeFile,copyFile,mkdir,mkdtemp,rm,symlink,readdir} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {technicalPublicationSchema} from '../src/lib/technical-publication-schema.ts';
import {inspectTechnicalBatch,publicationPlan,technicalFixturePlan,prepareApprovedTechnicalBatch,validatePublishedEdition,checkTechnicalPublications,serializeArticle,stageTechnicalFixtures,prepareTechnicalAssets,manifestPath} from './technical-publication.mjs';
const root=resolve(import.meta.dirname,'..');
const approval={kind:'human',reviewedBy:'Test reviewer',pullRequest:123,basis:'Simulated unit-test authorization in a temporary directory only.'};
async function project(work){
  const folder=await mkdtemp(join(tmpdir(),'youdozi-translation-preview-')),base=join(folder,'site');
  try{
    const manifest=JSON.parse(await readFile(join(root,manifestPath),'utf8'));
    const paths=new Set([manifestPath,...manifest.editions.flatMap(r=>[r.source.path,r.draft.path,r.diagramSource.path,r.diagram.path,r.sourceDiagram.path])]);
    for(const path of paths){await mkdir(dirname(join(base,path)),{recursive:true});await copyFile(join(root,path),join(base,path));}
    await mkdir(join(base,'src/content/technical-translations'),{recursive:true});
    await work(base,folder);
  }finally{await rm(folder,{recursive:true,force:true});}
}
async function marker(base,batch){await writeFile(join(base,'.translation-preview-fixture.json'),JSON.stringify({fixtureOnly:true,actualRoot:root,technicalFixtureKeys:batch.editions.map(e=>e.key)}));}

test('approved plan preserves complete code and changes only the diagram destination in prose',async()=>{
  const batch=await inspectTechnicalBatch(),records=publicationPlan(batch,approval);
  assert.equal(records.length,12);
  for(const record of records){await validatePublishedEdition(record.data,record.body,batch);assert.equal(record.data.approval.kind,'human');assert.match(record.body,/\/assets\/diagrams\/technical\//);}
});
test('missing approval, synthetic reviewer, wrong manifest and future chronology are rejected',async()=>{
  const batch=await inspectTechnicalBatch();
  for(const value of [undefined,{}, {...approval,basis:''},{...approval,reviewedBy:'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL'}])assert.throws(()=>publicationPlan(batch,value));
  const record=publicationPlan(batch,approval)[0];
  assert.equal(technicalPublicationSchema.safeParse({...record.data,approval:{...record.data.approval,approvedAt:'2999-01-01T00:00:00Z'}}).success,false);
  await project(async base=>{await assert.rejects(prepareApprovedTechnicalBatch(base,approval,'0'.repeat(64)),/exact reviewed manifest/);assert.deepEqual(await readdir(join(base,'src/content/technical-translations')),[]);});
});
test('human preparation creates twelve approved Markdown files without altering the draft ledger',async()=>{
  await project(async base=>{
    const batch=await inspectTechnicalBatch(base),before=await readFile(join(base,manifestPath),'utf8');
    assert.equal(await prepareApprovedTechnicalBatch(base,approval,batch.manifestSha256),12);
    const checked=await checkTechnicalPublications(base);assert.equal(checked.approvedEditions,12);assert.equal(checked.pendingEditions,0);
    assert.equal(await readFile(join(base,manifestPath),'utf8'),before);
    assert.equal(await prepareTechnicalAssets(base),12);
  });
});
test('published prose, title, identity and source hash cannot diverge from the reviewed batch',async()=>{
  const batch=await inspectTechnicalBatch(),record=publicationPlan(batch,approval)[0];
  await assert.rejects(validatePublishedEdition(record.data,record.body+'Unreviewed addition.',batch),/body differs/);
  for(const [field,value] of [['title','Different'],['routeSlug','different'],['sourceSha256','0'.repeat(64)]])await assert.rejects(validatePublishedEdition({...record.data,[field]:value},record.body,batch),/differs from reviewed/);
});
test('changed English source invalidates an existing approved publication',async()=>{
  await project(async base=>{
    const batch=await inspectTechnicalBatch(base);await prepareApprovedTechnicalBatch(base,approval,batch.manifestSha256);
    const source=join(base,batch.editions[0].data.sourcePath);await writeFile(source,(await readFile(source,'utf8'))+'Changed source.');
    await assert.rejects(checkTechnicalPublications(base),/Pinned file changed/);
  });
});
test('synthetic publication requires both an external disposable directory and the exact fixture marker',async()=>{
  await project(async base=>{
    const batch=await inspectTechnicalBatch(base),records=technicalFixturePlan(batch);
    await assert.rejects(stageTechnicalFixtures(base,base,records),/isolated snapshot/);
    await assert.rejects(stageTechnicalFixtures(base,root,records));
    await marker(base,batch);await stageTechnicalFixtures(base,root,records);
    assert.equal((await checkTechnicalPublications(base)).approvedEditions,12);
    await rm(join(base,'.translation-preview-fixture.json'));
    await assert.rejects(checkTechnicalPublications(base));
  });
});
test('existing target is never overwritten and a partially written batch is rolled back',async()=>{
  await project(async base=>{
    const batch=await inspectTechnicalBatch(base),target=join(base,batch.editions[3].path);await mkdir(dirname(target),{recursive:true});await writeFile(target,'Existing user file');
    await assert.rejects(prepareApprovedTechnicalBatch(base,approval,batch.manifestSha256),{code:'EEXIST'});
    assert.equal(await readFile(target,'utf8'),'Existing user file');
    for(const edition of batch.editions.slice(0,3))await assert.rejects(readFile(join(base,edition.path)),{code:'ENOENT'});
  });
});
test('language symlink cannot send approved manuscripts outside their collection',async()=>{
  await project(async(base,folder)=>{
    const batch=await inspectTechnicalBatch(base),outside=join(folder,'outside');await mkdir(outside);
    await symlink(outside,join(base,'src/content/technical-translations/zh-CN'));
    await assert.rejects(prepareApprovedTechnicalBatch(base,approval,batch.manifestSha256),/symlink/);assert.deepEqual(await readdir(outside),[]);
  });
});
test('asset preparation removes withdrawn generated diagrams without copying pending diagrams',async()=>{
  await project(async base=>{
    const generated=join(base,'public/assets/diagrams/technical');await mkdir(generated,{recursive:true});await writeFile(join(generated,'withdrawn.svg'),'stale');
    assert.equal(await prepareTechnicalAssets(base),0);await assert.rejects(readFile(join(generated,'withdrawn.svg')),{code:'ENOENT'});
  });
});
