import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import YAML from 'yaml';
import registry from '../content/seo/core-articles.json' with {type:'json'};
import {coreArticles} from '../src/lib/core-articles.ts';

test('core article registry preserves existing route identities and paired editions',()=>{
  assert.equal(new Set(registry.articles.map(a=>a.key)).size,10);
  assert.equal(registry.articles.filter(a=>a.focus).length,4);
  for(const {key,legacyPath} of registry.articles)for(const language of ['en','ko']){
    const source=fs.readFileSync(`src/content/posts/${language}/${key}.md`,'utf8');
    const data=YAML.parse(source.split('---')[1]);
    assert.equal(data.translationKey,key);assert.equal(data.routeSlug,key);
    assert.equal(data.kind,'post');assert.notEqual(data.reviewStatus,'example');
    if(language==='ko')assert.equal(data.legacyUrl,legacyPath);
  }
});
test('featured selection keeps editorial order and excludes unavailable editions',()=>{
  const make=(key,more={})=>({translationKey:key,language:'en',kind:'post',publishedAt:new Date('2020-01-01Z'),...more});
  const keys=registry.articles.map(a=>a.key);
  const entries=[make(keys[3]),make(keys[2],{publishedAt:new Date('2999-01-01Z')}),make(keys[1],{reviewStatus:'example'}),make(keys[0]),make(keys[4],{kind:'digest'}),make('unregistered')];
  assert.deepEqual(coreArticles('en',entries).map(e=>e.translationKey),[keys[0],keys[3]]);
  assert.deepEqual(coreArticles('ja',entries),[]);assert.deepEqual(coreArticles('ko',entries),[]);
});

import {answerCitations} from '../src/lib/answer-pilot.ts';
import pilot from '../content/seo/answer-pilot.json' with {type:'json'};
test('answer evidence is exposed only when actually linked in a pilot introduction',()=>{
 for(const article of pilot.articles)for(const language of ['en','ko']){
  const entry={language,kind:'post',translationKey:article.key,post:{body:`A supported claim. [Official source](${article.evidence[0]})\n\nDetails.`}};
  assert.deepEqual(answerCitations(entry),article.evidence);
  for(const body of ['No supporting link.',`Intro without citation.\n\n[Later](${article.evidence[0]})`,`\`\`\`text\n[Not visible evidence](${article.evidence[0]})\n\`\`\``])assert.deepEqual(answerCitations({...entry,post:{body}}),[]);
  for(const patch of [{language:'ja'},{kind:'digest'},{translationKey:'unrelated'},{reviewStatus:'example'}])assert.deepEqual(answerCitations({...entry,...patch}),[]);
 }
});
