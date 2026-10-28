import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,writeFile,copyFile,readdir,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,join,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';
import {inspectRelease,publishRelease,fileSha256} from './translation-release.mjs';
import {root} from './translations.mjs';
const ledgerPath='.pipeline/translations/releases/spanish-full-031.json';
const ledger=JSON.parse(await readFile(ledgerPath,'utf8'));
const approval={reviewedBy:'Temporary release test only',pullRequest:1,basis:'Synthetic fixture outside the repository; not user publication approval'};
const load=async p=>JSON.parse(await readFile(p,'utf8'));
async function fixture(run){
 const base=await mkdtemp(join(tmpdir(),'youdozi-release-check-'));
 try{
  const files=new Set([ledgerPath,...ledger.editions.flatMap(r=>[r.batch.path,r.source.path,r.review.path,r.evidence.path])]);
  for(const p of files){await mkdir(dirname(join(base,p)),{recursive:true});await copyFile(resolve(root,p),join(base,p));}
  await mkdir(join(base,'src/content/translations'),{recursive:true});
  await run(base,structuredClone(ledger));
 }finally{await rm(base,{recursive:true,force:true});}
}
async function saveLedger(base,data){await writeFile(join(base,ledgerPath),JSON.stringify(data));}
async function repin(base,row,field,value){
 const path=join(base,row[field].path);await writeFile(path,JSON.stringify(value));row[field].sha256=fileSha256(await readFile(path));
}

test('pinned release covers 53 private editions without writing approval or publication files',async()=>{
 const report=await inspectRelease(ledgerPath);
 assert.deepEqual(report.summary,{total:53,awaitingApproval:53,alreadyPublished:0,blocked:0});
 assert.equal(report.approval,null);
 assert.equal(report.editions.filter(e=>e.evidenceMethod==='supplemental-primary').length,1);
 assert.equal(report.editions.find(e=>e.key==='es-50b97c32c1d2c027').status,'awaiting-approval');
 for(const e of report.editions)await assert.rejects(readFile(resolve(root,e.publicationFile)),{code:'ENOENT'});
});

test('source or batch drift blocks the whole publication before any writes',async()=>{
 for(const field of ['source','batch'])await fixture(async(base,data)=>{
  const p=join(base,data.editions[0][field].path);await writeFile(p,(await readFile(p,'utf8'))+'\n');
  const report=await inspectRelease(ledgerPath,base);assert.ok(report.summary.blocked>0);
  await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('repinning a review with an unresolved finding cannot silently make the edition ready',async()=>{
 await fixture(async(base,data)=>{
  const row=data.editions[0],review=await load(join(base,row.review.path));
  review.findings.push({renewalId:row.key.slice(3),field:'edition.claims[0]',status:'open',finding:'Unresolved meaning error fixture'});
  await repin(base,row,'review',review);await saveLedger(base,data);
  const report=await inspectRelease(ledgerPath,base);
  assert.ok(report.editions[0].reasons.some(r=>r.includes('Unresolved translation review')));
  await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('alternate evidence requires every unchanged claim, primary sources and accurate recovery scope',async()=>{
 for(const change of [d=>d.coverage.pop(),d=>d.sourceSha256='0'.repeat(64),d=>d.originalSourceRecovered=true,d=>d.documents[0].url='https://example.com/unverified',d=>d.documents[0].quotes[0]='Changed quote without updating its digest'])await fixture(async(base,data)=>{
  const row=data.editions.find(e=>e.key==='es-50b97c32c1d2c027'),proof=await load(join(base,row.evidence.path));change(proof);
  await repin(base,row,'evidence',proof);await saveLedger(base,data);
  const report=await inspectRelease(ledgerPath,base);assert.equal(report.summary.blocked,1);
  await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('stored evidence failure remains blocking even if a changed report is repinned',async()=>{
 await fixture(async(base,data)=>{
  const row=data.editions[0],evidence=await load(join(base,row.evidence.path));
  evidence.items.find(i=>i.renewalId===row.key.slice(3)).checks[0].present=false;
  await repin(base,row,'evidence',evidence);await saveLedger(base,data);
  const report=await inspectRelease(ledgerPath,base);assert.equal(report.editions[0].status,'blocked');
  await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('release paths cannot escape the review directory through traversal or symlinks',async()=>{
 await fixture(async(base,data)=>{
  const row=data.editions[0];const original=await readFile(join(base,row.review.path));
  await writeFile(join(base,'outside.json'),original);
  const link='.pipeline/translations/ai-reviews/escape.json';await symlink(join(base,'outside.json'),join(base,link));row.review.path=link;
  await saveLedger(base,data);const report=await inspectRelease(ledgerPath,base);
  assert.ok(report.editions[0].reasons.some(r=>r.includes('escapes')));
  await assert.rejects(inspectRelease('../../outside.json',base));
 });
});

test('duplicate editions fail and valid fixtures still need complete approval metadata',async()=>{
 await fixture(async(base,data)=>{
  data.editions.push(data.editions[0]);await saveLedger(base,data);
  await assert.rejects(inspectRelease(ledgerPath,base),/Duplicate/);
 });
 await fixture(async(base)=>{
  await assert.rejects(publishRelease(ledgerPath,{},base));
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('explicit test approval creates exactly the pinned editions and refuses duplicate publication',async()=>{
 await fixture(async(base)=>{
  const created=await publishRelease(ledgerPath,approval,base);assert.equal(created.length,53);
  assert.equal((await readdir(join(base,'src/content/translations'))).length,53);
  const report=await inspectRelease(ledgerPath,base);
  assert.deepEqual(report.summary,{total:53,awaitingApproval:0,alreadyPublished:53,blocked:0});
  await assert.rejects(publishRelease(ledgerPath,approval,base),/already-published/);
  assert.equal((await readdir(join(base,'src/content/translations'))).length,53);
 });
});

test('the publication CLI rejects the old raw-batch route before accessing a manuscript',()=>{
 const result=spawnSync(process.execPath,['scripts/translations.mjs','publish','--batch','not-a-real-batch.json','--reviewed-by','TEST ONLY','--approval-pr','1','--approval-basis','TEST ONLY'],{cwd:root,encoding:'utf8'});
 assert.notEqual(result.status,0);assert.match(result.stderr,/pinned --release \(not --batch\)/);
});

test('the remaining five languages pin exactly the private counterparts of the Spanish release',async()=>{
 const report=await inspectRelease('.pipeline/translations/releases/multilingual-full-032.json');
 assert.deepEqual(report.summary,{total:265,awaitingApproval:265,alreadyPublished:0,blocked:0});
 assert.equal(report.approval,null);
 const sourceIds=new Set(ledger.editions.map(e=>e.key.slice(3)));
 for(const lang of ['zh-CN','ja','de','fr','ru']){
  const editions=report.editions.filter(e=>e.draft.language===lang);
  assert.equal(editions.length,53);
  assert.deepEqual(new Set(editions.map(e=>e.draft.renewalId)),sourceIds);
  for(const e of editions)await assert.rejects(readFile(resolve(root,e.publicationFile)),{code:'ENOENT'});
 }
 assert.equal(report.editions.filter(e=>e.evidenceMethod==='supplemental-primary').length,5);
});

test('legacy resolved rechecks are accepted but open, unknown and contradictory findings block publication',async()=>{
 for(const [finding,blocked] of [[{recheck:'resolved'},false],[{recheck:'open'},true],[{},true],[{status:'open',recheck:'resolved'},true],[{status:'resolved',recheck:'open'},true]])await fixture(async(base,data)=>{
  const row=data.editions[0];data.editions=[row];
  const review=await load(join(base,row.review.path));
  review.findings=[{renewalId:row.key.slice(3),field:'edition.claims[0]',...finding}];
  await repin(base,row,'review',review);await saveLedger(base,data);
  const report=await inspectRelease(ledgerPath,base);assert.equal(report.summary.blocked,Number(blocked));
  if(blocked)await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});

test('an exact batch hash cannot turn a different language or partial review into full coverage',async()=>{
 for(const change of [r=>r.scope.language='ja',r=>r.scope.languages='es',r=>r.scope.fields=['edition.title'],r=>r.carryForwardScope={'spanish-002':'Only one changed field was rechecked'},r=>r.carryForwardScope={'spanish-002':''}])await fixture(async(base,data)=>{
  const row=data.editions[0];data.editions=[row];
  const review=await load(join(base,row.review.path));change(review);
  await repin(base,row,'review',review);await saveLedger(base,data);
  const report=await inspectRelease(ledgerPath,base);assert.equal(report.summary.blocked,1);
  assert.match(report.editions[0].reasons.join(' '),/full edition and language/);
  await assert.rejects(publishRelease(ledgerPath,approval,base),/blocked editions/);
  assert.deepEqual(await readdir(join(base,'src/content/translations')),[]);
 });
});
