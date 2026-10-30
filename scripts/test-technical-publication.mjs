import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,writeFile,copyFile,mkdir,mkdtemp,rm,symlink,readdir} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {technicalPublicationSchema} from '../src/lib/technical-publication-schema.ts';
import {inspectTechnicalBatch,inspectTechnicalBatches,publicationPlan,technicalFixturePlan,prepareApprovedTechnicalBatch,validatePublishedEdition,checkTechnicalPublications,serializeArticle,sha,stageTechnicalFixtures,prepareTechnicalAssets,manifestPath} from './technical-publication.mjs';
const {inspectTechnicalTranslations}=await import('./check-technical-translations.mjs');
const root=resolve(import.meta.dirname,'..');
const approval={kind:'human',reviewedBy:'Test reviewer',pullRequest:123,basis:'Simulated unit-test authorization in a temporary directory only.'};
async function project(work){
  const folder=await mkdtemp(join(tmpdir(),'youdozi-translation-preview-')),base=join(folder,'site');
  try{
    const registryPath='.pipeline/technical-translations/batches.json';
    const registry=JSON.parse(await readFile(join(root,registryPath),'utf8'));
    const manifests=await Promise.all(registry.manifests.map(async path=>JSON.parse(await readFile(join(root,path),'utf8'))));
    const paths=new Set([registryPath,...registry.manifests,...manifests.flatMap(m=>m.editions.flatMap(r=>[r.source.path,r.draft.path,r.diagramSource.path,r.diagram.path,r.sourceDiagram.path]))]);
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
    const checked=await checkTechnicalPublications(base);assert.equal(checked.approvedEditions,12);assert.equal(checked.pendingEditions,84);
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

test('approval hash for the first batch cannot publish the separate shell batch',async()=>{
  await project(async base=>{
    const first=await inspectTechnicalBatch(base),secondPath='.pipeline/technical-translations/batch-052/manifest.json';
    await assert.rejects(prepareApprovedTechnicalBatch(base,approval,first.manifestSha256,secondPath),/exact reviewed manifest/);
    const second=await inspectTechnicalBatch(base,secondPath);
    assert.equal(await prepareApprovedTechnicalBatch(base,approval,second.manifestSha256,secondPath),18);
    assert.equal((await checkTechnicalPublications(base)).approvedEditions,18);
    assert.equal((await checkTechnicalPublications(base)).pendingEditions,78);
    assert.equal((await inspectTechnicalBatches(base)).editions.length,96);
  });
});
test('unknown or duplicated manifest registrations are rejected before publication',async()=>{
  await project(async base=>{
    await assert.rejects(inspectTechnicalBatch(base,'.pipeline/technical-translations/batch-999/manifest.json'),/Unregistered/);
    const path=join(base,'.pipeline/technical-translations/batches.json'),registry=JSON.parse(await readFile(path,'utf8'));
    registry.manifests.push(registry.manifests[0]);await writeFile(path,JSON.stringify(registry));
    await assert.rejects(inspectTechnicalBatches(base),/Invalid technical batch registry/);
  });
});

test('failure branches cannot be dropped or converted into successful exits',async()=>{
  for(const mutate of [diagram=>diagram.steps[3].branch.outcome='complete',diagram=>delete diagram.steps[3].branch]){
    await project(async base=>{
      const path='.pipeline/technical-translations/batch-052/manifest.json',manifest=JSON.parse(await readFile(join(base,path),'utf8'));
      const row=manifest.editions.find(r=>r.language==='zh-CN'&&r.translationKey.includes('function-error'));
      const diagram=JSON.parse(await readFile(join(base,row.diagramSource.path),'utf8'));mutate(diagram);
      const bytes=JSON.stringify(diagram);await writeFile(join(base,row.diagramSource.path),bytes);row.diagramSource.sha256=sha(bytes);
      await writeFile(join(base,path),JSON.stringify(manifest));
      await assert.rejects(inspectTechnicalTranslations(base,path),/Flow (exit outcome|branch)/);
    });
  }
});
test('release sample JSON remains protected executable-fence content',async()=>{
  const batch=await inspectTechnicalBatch(root,'.pipeline/technical-translations/batch-052/manifest.json');
  const record=publicationPlan(batch,approval).find(r=>r.data.translationKey.includes('github-latest'));
  await assert.rejects(validatePublishedEdition(record.data,record.body.replace('jdk-17.0.8.1+1','jdk-99'),batch),/body differs/);
});
test('distinct registry paths cannot disguise a duplicated batch identity',async()=>{
  await project(async base=>{
    const path=join(base,'.pipeline/technical-translations/batch-052/manifest.json'),manifest=JSON.parse(await readFile(path,'utf8'));
    manifest.batchId='technical-050';await writeFile(path,JSON.stringify(manifest));
    await assert.rejects(inspectTechnicalBatches(base),/Duplicate technical batch ID/);
  });
});
