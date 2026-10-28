import test from 'node:test';
import assert from 'node:assert/strict';
import {mountCodeTools} from '../src/scripts/code-tools.ts';
import copy from '../src/lib/code-copy-ui.json' with {type:'json'};

// Minimal DOM for event/state tests; real generated pages are also checked in Chrome.
class Element {
  constructor(tag,document){this.tagName=tag;this.ownerDocument=document;this.children=[];this.dataset={};this.attributes=new Map();this.events={};this.textContent='';}
  append(...nodes){for(const node of nodes){if(node.parentElement){const old=node.parentElement.children;old.splice(old.indexOf(node),1);}this.children.push(node);node.parentElement=this;}}
  before(node){const list=this.parentElement.children;list.splice(list.indexOf(this),0,node);node.parentElement=this.parentElement;}
  setAttribute(key,value){this.attributes.set(key,value);}
  hasAttribute(key){return this.attributes.has(key);}
  removeAttribute(key){this.attributes.delete(key);}
  addEventListener(event,fn){this.events[event]=fn;}
  click(){return this.events.click();}
}
function fixture(text){
  const document={createElement:tag=>new Element(tag,document)};
  const root=document.createElement('div'),pre=document.createElement('pre'),code=document.createElement('code');
  code.textContent=text;pre.append(code);root.append(pre);root.querySelectorAll=()=>[code];
  return {root,pre,code,button:()=>root.children[0].children[0].children[0],status:()=>root.children[0].children[2]};
}
const sample='\tconst text = "<script> & 한글 日本語 é ё";\n\n  $ echo "$HOME"\n';
test('clipboard receives only exact code text after an explicit click',async()=>{
  const f=fixture(sample),writes=[];mountCodeTools(f.root,copy.en,{async writeText(text){writes.push(text);}});
  assert.deepEqual(writes,[]);assert.equal(f.pre.tabIndex,0);assert.equal(f.pre.attributes.get('role'),'region');
  assert.equal(f.code.textContent,sample);assert.equal(f.code.parentElement,f.pre);
  await f.button().click();assert.deepEqual(writes,[sample]);assert.equal(f.status().textContent,copy.en.copied);
  assert.equal(f.button().textContent,copy.en.copy);assert.equal(f.status().attributes.get('role'),'status');
  assert.equal(f.code.textContent,sample);
});
test('permission rejection reports failure and the same button can retry',async()=>{
  const f=fixture(sample);let attempts=0;mountCodeTools(f.root,copy.ko,{async writeText(){if(++attempts===1)throw Error('denied');}});
  await f.button().click();assert.equal(f.status().textContent,copy.ko.error);assert.equal(f.button().hasAttribute('aria-disabled'),false);
  await f.button().click();assert.equal(attempts,2);assert.equal(f.status().textContent,copy.ko.copied);
});
test('a synchronous clipboard failure is caught without trapping the button',async()=>{
  const f=fixture(sample);mountCodeTools(f.root,copy.en,{writeText(){throw Error('blocked');}});
  await f.button().click();assert.equal(f.status().textContent,copy.en.error);assert.equal(f.button().hasAttribute('aria-disabled'),false);
});
test('repeated activation during one pending write does not race its result',async()=>{
  const f=fixture(sample);let finish,calls=0;mountCodeTools(f.root,copy.en,{writeText(){calls++;return new Promise(resolve=>{finish=resolve;});}});
  const pending=f.button().click();await f.button().click();assert.equal(calls,1);assert.equal(f.button().attributes.get('aria-disabled'),'true');
  finish();await pending;assert.equal(f.status().textContent,copy.en.copied);assert.equal(f.button().hasAttribute('aria-disabled'),false);
});
test('unsupported clipboard keeps code available and keyboard focusable without an unusable button',()=>{
  const f=fixture(sample);mountCodeTools(f.root,copy.en);assert.equal(f.root.children[0],f.pre);assert.equal(f.pre.tabIndex,0);assert.equal(f.code.textContent,sample);
});
test('mounting twice does not duplicate tools or change existing accessible names',()=>{
  const f=fixture(sample);f.pre.setAttribute('tabindex','0');f.pre.setAttribute('aria-label','Existing name');f.pre.setAttribute('role','group');
  const writer={async writeText(){}};mountCodeTools(f.root,copy.en,writer);const wrapper=f.root.children[0];mountCodeTools(f.root,copy.en,writer);
  assert.equal(f.root.children.length,1);assert.equal(f.root.children[0],wrapper);assert.equal(f.pre.attributes.get('aria-label'),'Existing name');assert.equal(f.pre.attributes.get('role'),'group');
  const blank=fixture('\n\t ');mountCodeTools(blank.root,copy.en,writer);assert.equal(blank.root.children[0],blank.pre);assert.equal(blank.pre.dataset.codeTools,undefined);
});
test('action, completion, failure and code region labels cover all eight languages',()=>{
  assert.deepEqual(Object.keys(copy).sort(),['en','ko','zh-CN','ja','de','fr','ru','es'].sort());
  for(const labels of Object.values(copy))assert.deepEqual(Object.keys(labels).sort(),['copy','copied','error','block'].sort());
  for(const labels of Object.values(copy))for(const value of Object.values(labels))assert.ok(value.trim());
});
