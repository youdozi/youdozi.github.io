import test from 'node:test';
import assert from 'node:assert/strict';
import {commentTerm,commentFallback,isCommentResize,isCommentCallback} from '../src/lib/comments.ts';
import copy from '../src/lib/comments-ui.json' with {type:'json'};
test('discussion identity and GitHub fallback preserve the existing term',()=>{
  for(const entry of [{legacyUrl:'/springboot/example/',translationKey:'new-key'},{translationKey:'2026-example'}]){
    const term=commentTerm(entry);assert.equal(term,entry.legacyUrl||entry.translationKey);
    const url=new URL(commentFallback(term));assert.equal(url.origin,'https://github.com');
    assert.equal(url.pathname,'/youdozi/youdozi.github.io/issues');assert.equal(url.searchParams.get('q'),`is:issue "${term}"`);
  }
  assert.equal(isCommentCallback('https://youdozi.github.io/en/?utterances=example-return'),true);
  assert.equal(isCommentCallback('https://youdozi.github.io/en/?utterances='),false);
  assert.equal(isCommentCallback('https://youdozi.github.io/en/'),false);
});
test('only the expected frame and origin can acknowledge a valid widget resize',()=>{
  const frame={};const event={origin:'https://utteranc.es',source:frame,data:{type:'resize',height:320}};
  assert.equal(isCommentResize(event,frame),true);
  for(const change of [{origin:'https://other.example'},{source:{}},{data:null},{data:'resize'},{data:{type:'resize',height:'320'}},{data:{type:'resize',height:NaN}},{data:{type:'resize',height:0}},{data:{type:'resize',height:Infinity}}])assert.equal(isCommentResize({...event,...change},frame),false);
  assert.equal(isCommentResize(event,null),false);
});
test('comment action and status copy covers all eight supported editions',()=>{
  assert.deepEqual(Object.keys(copy).sort(),['en','ko','zh-CN','ja','de','fr','ru','es'].sort());
  for(const edition of Object.values(copy))for(const key of ['show','loading','opened','error','github'])assert.ok(edition[key].trim());
});
