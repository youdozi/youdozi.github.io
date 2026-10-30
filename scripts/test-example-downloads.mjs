import test from 'node:test';
import assert from 'node:assert/strict';
import catalog from '../content/examples/downloads.json' with {type:'json'};
import {exampleDownload} from '../src/lib/example-downloads.ts';

test('downloads identify only the paired native canonical articles',()=>{
  for(const {key} of catalog.examples)for(const language of ['en','ko']){
    const entry={language,translationKey:key,kind:'post',reviewStatus:'revised',publishedAt:new Date('2020-01-01Z'),url:`/${language}/posts/${key}/`};
    assert.equal(exampleDownload(entry),`/assets/examples/${key}-${language}.zip`);
    for(const patch of [{language:'ja'},{language:'es'},{kind:'digest'},{reviewStatus:'example'},{reviewStatus:'pending'},{publishedAt:new Date('2999-01-01Z')},{url:'/legacy/'},{translationKey:'unregistered'}])assert.equal(exampleDownload({...entry,...patch}),undefined);
  }
});
