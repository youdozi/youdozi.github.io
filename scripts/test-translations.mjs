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

test('translation queue covers all sources and reports their actual prepared status',async()=>{
  const queue=await prepareQueue();
  const sources=(await readdir('src/content/renewals')).filter(f=>f.endsWith('.json'));
  assert.equal(queue.sources.length,sources.length);
  assert.equal(queue.tasks.length,sources.length*queue.languages.length);
  assert.deepEqual(queue.languages,['zh-CN','ja','de','fr','ru','es']);
  const batches=(await readdir('.pipeline/translations/batches')).filter(f=>f.endsWith('.json'));
  const drafts=(await Promise.all(batches.map(async f=>JSON.parse(await readFile(`.pipeline/translations/batches/${f}`,'utf8')).translations))).flat();
  assert.equal(queue.tasks.filter(t=>t.status==='draft').length,drafts.length);
  for(const task of queue.tasks)assert.equal(task.status,drafts.some(d=>d.renewalId===task.renewalId&&d.language===task.language)?'draft':'pending');
  assert.ok(queue.tasks.some(t=>t.language==='es'&&t.status==='draft'));
  for(const s of queue.sources){
    const bytes=await readFile(`src/content/renewals/${s.renewalId}.json`,'utf8');
    assert.equal(s.sourceSha256,createHash('sha256').update(bytes).digest('hex'));
    assert.equal(queue.tasks.filter(t=>t.renewalId===s.renewalId).length,queue.languages.length);
  }
});

test('translation queue handles both partial and complete preparation of a source',async()=>{
  const base=await mkdtemp(join(tmpdir(),'youdozi-partial-translation-queue-'));
  try{
    await mkdir(join(base,'src/content/renewals'),{recursive:true});
    await mkdir(join(base,'.pipeline/translations/batches'),{recursive:true});
    await writeFile(join(base,`src/content/renewals/${source.id}.json`),sourceBytes);
    const draft=batch.translations[0];
    await writeFile(join(base,'.pipeline/translations/batches/partial.json'),JSON.stringify({...batch,translations:[draft]}));
    const queue=await prepareQueue(base);
    assert.equal(queue.sources.length,1);
    assert.equal(queue.tasks.length,queue.languages.length);
    assert.equal(queue.tasks.filter(t=>t.status==='draft').length,1);
    assert.equal(queue.tasks.filter(t=>t.status==='pending').length,queue.languages.length-1);
    for(const task of queue.tasks){
      assert.equal(task.status,task.language===draft.language?'draft':'pending');
      assert.equal(task.sourceSha256,draft.sourceSha256);
      assert.equal(task.batch,task.language===draft.language?'batches/partial.json':undefined);
    }
    const spanishBatch=JSON.parse(await readFile('.pipeline/translations/batches/spanish-001.json','utf8'));
    const spanish=spanishBatch.translations.find(t=>t.renewalId===source.id);
    assert.ok(spanish);
    await writeFile(join(base,'.pipeline/translations/batches/partial.json'),JSON.stringify({...batch,translations:[...batch.translations,spanish]}));
    const complete=await prepareQueue(base);
    assert.equal(complete.tasks.length,complete.languages.length);
    assert.ok(complete.tasks.every(t=>t.status==='draft'));
    assert.equal(complete.tasks.filter(t=>t.status==='pending').length,0);
  }finally{await rm(base,{recursive:true,force:true});}
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

test('number-word checks respect Unicode words and agree with Python without losing real numbers',async()=>{
  const {numbers}=await import('../src/lib/bilingual-quality.ts');
  const {spawnSync}=await import('node:child_process');
  const cases=[
    ['Aktivitäten, Identitäten und Universitäten',[]],
    ['ten activities, one region',['1','10']],
    ['Prioritäten plus 16',['16']],
    ['one개 und ten한',[]],
    ['someone, stone, TEN and one',['1','10']],
    ['one_two ten_X',[]],
    ['１２one',[]],
    ['120,000 / 2.43 / CodeQL 2.25.2',['120000','2.25.2','2.43']],
  ];
  const python=spawnSync('python3',['-B','-c',"import json,sys;sys.path.insert(0,'scripts');from bilingual_quality import numbers;print(json.dumps([sorted(numbers(t)) for t in json.load(sys.stdin)]))"],{input:JSON.stringify(cases.map(([value])=>value)),encoding:'utf8'});
  assert.equal(python.status,0,python.stderr);
  const expected=JSON.parse(python.stdout);
  for(const [i,[value,wanted]] of cases.entries()){
    assert.deepEqual(expected[i],wanted,value);
    assert.deepEqual([...numbers(value)].sort(),wanted,value);
  }
});
