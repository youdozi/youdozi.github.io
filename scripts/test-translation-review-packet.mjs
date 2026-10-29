import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,writeFile,rm,lstat,stat,symlink,realpath} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {mountReview} from './translation-review-client.mjs';
import {reviewEntry,renderPacket,safeHTTPS,privateDestination,savePacket} from './translation-review-packet.mjs';

const commit='b'.repeat(40);
function fixture(){
  const source={url:'https://example.com/source',archiveDate:'2025-01-01',updatedAt:'2026-10-01T00:00:00Z',reviewFocus:{en:'English internal advice'},documents:[{url:'https://example.com/evidence'}],
    editions:{en:{title:'English title',claims:[{text:'Claim one 42.',evidence:[{document_id:0,quote:'The original says 42.'}]},{text:'Claim two.',evidence:[]}],followUp:[{text:'Later restriction.',evidence:[]}]}}};
  const item={status:'awaiting-approval',key:'es-'+'a'.repeat(16),draft:{language:'es',reviewFocus:'Translated internal advice',edition:{title:'Target title',claims:['Target one 42.','Target two.'],followUp:['Later target.']}}};
  const row={batch:{path:'.pipeline/translations/batches/example.json'},manifest:'.pipeline/translations/releases/example.json',evidence:{method:'stored-excerpts'}};
  const entry=reviewEntry(item,source,row,{reviewedAt:'2026-10-02T00:00:00Z'},commit);
  return {item,source,row,entry,packet:{schemaVersion:1,draftOnly:true,realUserApprovalRecorded:false,sourceCommit:commit,generatedAt:'2026-10-29T00:00:00Z',languages:{es:'Español'},entries:[entry]}};
}

test('review pairs preserve source/target claims, conditions, evidence and immutable links',()=>{
  const {entry}=fixture();
  assert.deepEqual(entry.claims[0],{english:'Claim one 42.',translated:'Target one 42.',evidence:[{quote:'The original says 42.',url:'https://example.com/evidence'}]});
  assert.equal(entry.followUp[0].english,'Later restriction.');
  assert.equal(entry.followUp[0].translated,'Later target.');
  assert.ok(entry.draftURL.includes(`/blob/${commit}/.pipeline/`));
  assert.ok(entry.releaseURL.includes(`/blob/${commit}/.pipeline/`));
  assert.ok(!Object.hasOwn(entry,'approval'));
});

test('unready editions, changed claim structure and unsafe links cannot enter a packet',()=>{
  for(const mutation of [f=>f.item.status='blocked',f=>f.item.draft.edition.followUp=[],f=>f.source.url='javascript:alert(1)',f=>f.source.documents[0].url='https://user:secret@example.com']){
    const f=fixture();mutation(f);assert.throws(()=>reviewEntry(f.item,f.source,f.row,{reviewedAt:'2026-10-02T00:00:00Z'},commit));
  }
  for(const value of ['http://example.com','javascript:alert(1)','data:text/html,anything','https://user:password@example.com'])assert.throws(()=>safeHTTPS(value));
  assert.equal(safeHTTPS('https://example.com/path'),'https://example.com/path');
});

test('embedded draft strings cannot terminate scripts or create executable markup',()=>{
  const {packet}=fixture();
  const value='</script><img src=x onerror=alert(1)>&\u2028\u2029';
  packet.entries[0].title=value;packet.entries[0].claims[0].translated=value;
  const html=renderPacket(packet);
  assert.equal((html.match(/<\/script>/g)||[]).length,2);
  assert.ok(!html.includes('<img'));
  const data=JSON.parse(html.match(/id="packet-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
  assert.equal(data.entries[0].title,value);
  assert.equal(data.entries[0].claims[0].translated,value);
  assert.match(html,/connect-src 'none'/);
  const nonce=html.match(/script-src 'nonce-([^']+)'/)[1];
  assert.equal((html.match(new RegExp(`nonce="${nonce.replace(/[+]/g,'\\+')}"`,'g'))||[]).length,2);
});

test('published or malformed packet metadata cannot masquerade as pending review',()=>{
  const {packet}=fixture();
  for(const change of [{draftOnly:false},{realUserApprovalRecorded:true},{sourceCommit:'<script>'}])assert.throws(()=>renderPacket({...packet,...change}));
  assert.ok(renderPacket({...packet,entries:[]}).includes('id="comparison"'));
});

async function folders(work){
  const base=await mkdtemp(join(tmpdir(),'review-packet-contract-'));
  try{const roots=[join(base,'repo-one'),join(base,'repo-two')];for(const root of roots)await mkdir(root);await work(base,roots);}
  finally{await rm(base,{recursive:true,force:true});}
}

test('outputs reject all checkouts, nested destinations and symlink aliases to another checkout',async()=>{
  await folders(async(base,roots)=>{
    for(const root of roots)await assert.rejects(privateDestination(join(root,'nested/review.html'),roots),/outside/);
    const alias=join(base,'outside-alias');await symlink(roots[1],alias,'dir');
    await assert.rejects(privateDestination(join(alias,'review.html'),roots),/outside/);
    await assert.rejects(privateDestination(join(base,'review.json'),roots),/HTML/);
    await assert.rejects(privateDestination(join(base,'review.html'),[]),/worktrees/);
  });
});

test('private file creation is exclusive and keeps existing files unchanged',async()=>{
  await folders(async(base,roots)=>{
    const target=join(base,'private/review.html');
    const saved=await savePacket(target,'first packet',roots);assert.equal(saved,await realpath(target));
    assert.equal((await stat(target)).mode&0o777,0o600);
    assert.equal((await stat(join(base,'private'))).mode&0o777,0o700);
    await assert.rejects(savePacket(target,'replacement',roots),/exists/);
    assert.equal(await readFile(target,'utf8'),'first packet');
  });
});

test('dangling symlink outputs and failed writes leave existing paths safe',async()=>{
  await folders(async(base,roots)=>{
    const alias=join(base,'alias.html');await symlink(join(base,'missing.html'),alias);
    await assert.rejects(savePacket(alias,'packet',roots),/exists/);
    assert.equal((await lstat(alias)).isSymbolicLink(),true);
    const broken=join(base,'broken.html');
    await assert.rejects(savePacket(broken,{},roots));
    await assert.rejects(lstat(broken),{code:'ENOENT'});
  });
});

test('CI checks packets without a persistent artifact and keeps normal build unchanged',async()=>{
  const {scripts}=JSON.parse(await readFile(new URL('../package.json',import.meta.url),'utf8'));
  assert.equal(scripts['check:translation-review'],'node scripts/translation-review-packet.mjs');
  assert.ok(!scripts.build.includes('translation-review-packet'));
  assert.ok(scripts.test.includes('test-translation-review-packet.mjs'));
  const workflow=await readFile(new URL('../.github/workflows/site-checks.yml',import.meta.url),'utf8');
  const command=workflow.indexOf('run: npm run check:translation-review');
  assert.ok(command>workflow.indexOf('run: npm run check:translation-preview'));
  assert.ok(command<workflow.indexOf('uses: actions/upload-artifact'));
  assert.ok(!workflow.slice(command,workflow.indexOf('\n',command)).includes('--output'));
});

class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.value='';this.listeners={};this.text='';}
  set textContent(value){this.text=String(value);this.children=[];}
  get textContent(){return this.text+this.children.map(child=>child.textContent).join(' ');}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.text='';this.children=children;}
  addEventListener(type,callback){this.listeners[type]=callback;}
  emit(type){this.listeners[type]?.();}
}
function dom(){
  const {packet,entry}=fixture();
  packet.languages={es:'Español',ja:'日本語'};
  packet.entries=[entry,{...structuredClone(entry),key:'es-'+'c'.repeat(16),title:'Second target',englishTitle:'Second source'},
    {...structuredClone(entry),language:'ja',key:'ja-'+'a'.repeat(16),title:'Japanese target',englishTitle:'Japanese source'}];
  const elements=Object.fromEntries(['packet-data','language','query','edition','status','comparison','previous','next'].map(id=>[id,new Element('div')]));
  elements['packet-data'].textContent=JSON.stringify(packet);
  const created=[];
  const document={getElementById:id=>elements[id],createElement:tag=>{const el=new Element(tag);created.push(el);return el;}};
  mountReview(document);
  return {elements,created,packet};
}

test('comparison navigation and language selection display the paired edition without changing draft data',()=>{
  const {elements,packet}=dom();const frozen=JSON.stringify(packet);
  assert.equal(elements.edition.children.length,3);
  assert.match(elements.comparison.textContent,/Claim one 42/);
  assert.match(elements.comparison.textContent,/Target one 42/);
  assert.equal(elements.previous.disabled,true);
  elements.language.value='es';elements.language.emit('change');
  assert.equal(elements.edition.children.length,2);
  elements.next.emit('click');assert.match(elements.status.textContent,/2 \/ 2/);
  assert.match(elements.comparison.textContent,/Second target/);
  assert.equal(elements.next.disabled,true);
  elements.previous.emit('click');assert.match(elements.status.textContent,/1 \/ 2/);
  elements.language.value='ja';elements.language.emit('change');
  assert.match(elements.comparison.textContent,/Japanese target/);
  assert.equal(elements.edition.children.length,1);
  assert.equal(JSON.stringify(packet),frozen);
});

test('search clears stale comparisons on no match and restores them without persistence or requests',()=>{
  const {elements}=dom();
  elements.query.value='missing review key';elements.query.emit('input');
  assert.equal(elements.edition.children.length,0);
  assert.equal(elements.next.disabled,true);assert.equal(elements.previous.disabled,true);
  assert.ok(!elements.comparison.textContent.includes('Target one 42'));
  elements.query.value='Japanese';elements.query.emit('input');
  assert.equal(elements.edition.children.length,1);assert.match(elements.comparison.textContent,/Japanese target/);
  elements.query.value='';elements.query.emit('input');assert.equal(elements.edition.children.length,3);
});

test('DOM comparison renders hostile draft titles as text and uses safe new-tab evidence links',()=>{
  const {elements,created,packet}=dom();
  assert.ok(created.filter(el=>el.tagName==='a').every(el=>el.href.startsWith('https://')&&el.target==='_blank'&&el.rel==='noopener noreferrer'));
  const malicious='</script><img onerror=alert(1)>';
  packet.entries[0].title=malicious;elements['packet-data'].textContent=JSON.stringify(packet);
  const document={getElementById:id=>elements[id],createElement:tag=>{const el=new Element(tag);created.push(el);return el;}};
  mountReview(document);
  assert.ok(elements.comparison.textContent.includes(malicious));
  assert.equal(created.filter(el=>['img','script','iframe'].includes(el.tagName)).length,0);
});
