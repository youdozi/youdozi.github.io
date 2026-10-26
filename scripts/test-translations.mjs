import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,writeFile,readdir,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {translationSchema,translationDraftSchema,validateTranslationSource,translatedEdition} from '../src/lib/translation-schema.ts';
import {prepareQueue,validateBatch,publishBatch,checkPublished,renderReview} from './translations.mjs';
const batch=JSON.parse(await readFile('.pipeline/translations/batches/pilot-001.json','utf8'));
const sourceBytes=await readFile(`src/content/renewals/${batch.translations[0].renewalId}.json`,'utf8');
const source=JSON.parse(sourceBytes);
const approval={reviewedBy:'test reviewer',pullRequest:1,basis:'Explicit human approval fixture only'};
const approved=d=>{const now=new Date().toISOString();return {...d,state:'approved',reviewedAt:now,publishedAt:now,updatedAt:now,approval:{...approval,approvedAt:now}};};

test('translation queue includes every approved source in all five languages with private pilot status',async()=>{
  const queue=await prepareQueue();
  const sources=(await readdir('src/content/renewals')).filter(f=>f.endsWith('.json'));
  assert.equal(queue.sources.length,sources.length);
  assert.equal(queue.tasks.length,sources.length*5);
  assert.deepEqual(queue.languages,['zh-CN','ja','de','fr','ru']);
  assert.equal(queue.tasks.filter(t=>t.status==='draft').length,batch.translations.length);
  for(const s of queue.sources){
    const bytes=await readFile(`src/content/renewals/${s.renewalId}.json`,'utf8');
    assert.equal(s.sourceSha256,createHash('sha256').update(bytes).digest('hex'));
    assert.equal(queue.tasks.filter(t=>t.renewalId===s.renewalId).length,5);
  }
});

test('public translation schema rejects drafts, missing approval and invalid chronology',()=>{
  const draft=batch.translations[0];
  assert.ok(translationDraftSchema.safeParse(draft).success);
  assert.ok(!translationSchema.safeParse(draft).success);
  const value=approved(draft);assert.ok(translationSchema.safeParse(value).success);
  const noApproval=structuredClone(value);delete noApproval.approval;
  assert.ok(!translationSchema.safeParse(noApproval).success);
  for(const mutate of [d=>d.publishedAt='2099-01-01T00:00:00Z',d=>d.updatedAt='2000-01-01T00:00:00Z',d=>d.approval.approvedAt='2000-01-01T00:00:00Z',d=>d.approval.reviewedBy=' ',d=>d.language='zh-TW',d=>d.edition.title='<script>bad</script>']){
    const bad=structuredClone(value);mutate(bad);assert.ok(!translationSchema.safeParse(bad).success);
  }
});

test('translation review preserves source revision, evidence, claim structure, numbers and terms',async()=>{
  assert.equal((await validateBatch(batch)).length,5);
  const draft=batch.translations[0];
  for(const mutate of [d=>d.sourceSha256='0'.repeat(64),d=>d.renewalId='0'.repeat(16),d=>d.edition.claims.pop(),d=>d.edition.claims[0]+=' 99%',d=>d.edition.claims[0]+=' Kubernetes',d=>d.edition.title+=' 99%',d=>d.reviewFocus+=' 99%',d=>d.edition.claims[0]='Untranslated English content.']){
    const bad=structuredClone(draft);mutate(bad);assert.throws(()=>validateTranslationSource(bad,source,sourceBytes));
  }
  assert.throws(()=>validateTranslationSource(draft,source,sourceBytes+'\n'),/source changed/);
  const old=approved(draft);old.reviewedAt='2000-01-01T00:00:00Z';assert.throws(()=>validateTranslationSource(old,source,sourceBytes),/precedes/);
  const edition=translatedEdition(approved(draft),source);
  assert.deepEqual(edition.claims[0].evidence,source.editions.en.claims[0].evidence);
  assert.equal(edition.claims[0].text,draft.edition.claims[0]);
  const duplicate=structuredClone(batch);duplicate.translations.push(duplicate.translations[0]);
  await assert.rejects(validateBatch(duplicate),/Duplicate/);
});

test('translation publication requires approval, refuses overwrite and rolls back partial writes',async()=>{
  const base=await mkdtemp(join(tmpdir(),'youdozi-translations-'));
  const directory=join(base,'src/content/translations');
  try{
    await mkdir(directory,{recursive:true});await mkdir(join(base,'src/content/renewals'),{recursive:true});
    await writeFile(join(base,`src/content/renewals/${source.id}.json`),sourceBytes);
    await assert.rejects(publishBatch(batch,{},base));
    assert.deepEqual(await readdir(directory),[]);
    const blocked=join(directory,`${batch.translations[1].language}-${source.id}.json`);
    await writeFile(blocked,'existing');
    await assert.rejects(publishBatch(batch,approval,base),/EEXIST/);
    assert.deepEqual(await readdir(directory),[`${batch.translations[1].language}-${source.id}.json`]);
    assert.equal(await readFile(blocked,'utf8'),'existing');await rm(blocked);
    const records=await publishBatch(batch,approval,base);assert.equal(records.length,5);
    assert.equal(await checkPublished(base),5);
    await assert.rejects(publishBatch(batch,approval,base),/EEXIST/);
    const bytes=await readFile(join(directory,`${records[0].language}-${source.id}.json`),'utf8');
    assert.equal(JSON.parse(bytes).approval.reviewedBy,approval.reviewedBy);
    assert.ok(new Date(records[0].publishedAt)>=new Date(source.updatedAt));
  }finally{await rm(base,{recursive:true,force:true});}
});

test('locale metadata and UI cover all supported languages, and review includes the exact draft',async()=>{
  const policy=JSON.parse(await readFile('src/lib/locales.json','utf8'));
  const extra=JSON.parse(await readFile('src/lib/localized-ui.json','utf8'));
  const ui=JSON.parse(await readFile('src/lib/archive-ui.json','utf8'));
  const {supportedLanguages,nativeLanguages,translationLanguages}=await import('../src/lib/locales.ts');
  assert.deepEqual([...nativeLanguages],policy.baseLanguages);assert.deepEqual([...translationLanguages],policy.translationLanguages);
  assert.deepEqual(Object.keys(policy.locales),supportedLanguages);
  const keys=Object.keys(extra.ja).sort(),archiveKeys=Object.keys(ui.en).sort();
  for(const lang of policy.translationLanguages){
    assert.deepEqual(Object.keys(extra[lang]).sort(),keys);
    assert.deepEqual(Object.keys(ui[lang]).sort(),archiveKeys);
    assert.ok(Object.values(extra[lang]).every(v=>v.trim()));
  }
  const review=await renderReview(batch);
  for(const draft of batch.translations){assert.ok(review.includes(draft.edition.title));assert.ok(review.includes(draft.edition.claims[0]));}
  assert.ok(review.includes(source.url));
});
