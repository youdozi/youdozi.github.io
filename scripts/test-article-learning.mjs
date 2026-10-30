import test from 'node:test';
import assert from 'node:assert/strict';
import {articleLearningPath,learningPathCopy} from '../src/lib/article-learning.ts';
const make=(key,language='en',more={})=>({translationKey:key,title:key,url:`/${language}/posts/${key}/`,language,kind:'post',categories:['linux'],tags:[],publishedAt:new Date('2020-01-01Z'),...more});
const keys=['2023-09-20-linux-shellscript-function-error','2021-07-27-parse-yaml','2023-11-17-linux-shellscript-version-compare','2023-09-23-linux-shellscript-github-latest'];

test('reading neighbors follow curated sections instead of dates, input order or extras',()=>{
 const entries=[make(keys[3]),make('extra'),make(keys[1]),make(keys[0]),make(keys[2])];
 const before=structuredClone(entries);
 const path=articleLearningPath(entries[2],entries);
 assert.equal(path.position,2);assert.equal(path.total,4);
 assert.equal(path.previous.url,`/en/posts/${keys[0]}/`);assert.equal(path.next.url,`/en/posts/${keys[2]}/`);
 assert.equal(path.guide.url,'/en/categories/linux/');assert.equal(articleLearningPath(entries[1],entries),undefined);
 assert.deepEqual(entries,before);
});
test('boundaries do not wrap; unavailable editions are omitted without cross-language fallback',()=>{
 for(const language of ['en','ko']){
  const entries=[make(keys[0],language),make(keys[1],language,{reviewStatus:'example'}),make(keys[2],language,{publishedAt:new Date('2999-01-01Z')}),make(keys[3],language),make(keys[1],language==='en'?'ko':'en')];
  const first=articleLearningPath(entries[0],entries),last=articleLearningPath(entries[3],entries);
  assert.equal(first.previous,undefined);assert.equal(first.next.url,entries[3].url);assert.equal(first.total,2);
  assert.equal(last.next,undefined);assert.equal(last.previous.url,entries[0].url);
  assert.equal(articleLearningPath(entries[1],entries),undefined);assert.equal(articleLearningPath(entries[2],entries),undefined);
 }
 for(const more of [{kind:'digest'},{language:'ja'},{reviewStatus:'example'}])assert.equal(articleLearningPath(make(keys[0],'en',more),[]),undefined);
 assert.equal(articleLearningPath(make(keys[0]),[make(keys[0])]),undefined);
});
test('named cross-category steps join their guide, with matching Korean and English directions',()=>{
 const key='2026-04-07-ruby-rbenv-jekyll-build-troubleshooting';
 for(const language of ['en','ko']){
  const entries=[make('2023-09-04-jekyll-install',language,{categories:['jekyll']}),make(key,language,{categories:['blog']})];
  const path=articleLearningPath(entries[1],entries);
  assert.equal(path.guide.url,`/${language}/categories/jekyll/`);assert.equal(path.previous.url,entries[0].url);assert.equal(path.next,undefined);
  assert.ok(learningPathCopy[language].previous&&learningPathCopy[language].next);
 }
});

test('all six translated editions use curated same-language neighbors without unpublished prerequisites',()=>{
 for(const language of ['zh-CN','ja','de','fr','ru','es']){
  const entries=[make(keys[3],language),make(keys[2],language),make(keys[0],language),make(keys[1],'en'),make(keys[1],language,{publishedAt:new Date('2999-01-01Z')})];
  const middle=articleLearningPath(entries[1],entries);
  assert.equal(middle.guide.url,`/${language}/categories/linux/`);
  assert.equal(middle.position,2);assert.equal(middle.total,3);
  assert.equal(middle.previous.url,entries[2].url);assert.equal(middle.next.url,entries[0].url);
  assert.equal(articleLearningPath(entries[2],entries).previous,undefined);
  assert.equal(articleLearningPath(entries[0],entries).next,undefined);
  assert.ok(learningPathCopy[language].previous&&learningPathCopy[language].next);
  assert.equal(articleLearningPath(entries[4],entries),undefined);
 }
});

test('localized tool articles follow HTTP, code search and diagram order',()=>{
 for(const language of ['zh-CN','ja','de','fr','ru','es']){
  const entries=['2021-07-23-app-diagrams.net','2021-08-06-search-github','2021-07-20-http-status-test'].map(key=>make(key,language,{categories:['util']}));
  const path=articleLearningPath(entries[1],entries);
  assert.equal(path.position,2);assert.equal(path.total,3);
  assert.equal(path.guide.url,`/${language}/categories/util/`);
  assert.equal(path.previous.url,entries[2].url);assert.equal(path.next.url,entries[0].url);
  assert.equal(articleLearningPath(entries[2],entries).previous,undefined);
  assert.equal(articleLearningPath(entries[0],entries).next,undefined);
 }
});
