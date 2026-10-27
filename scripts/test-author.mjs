import test from 'node:test';
import assert from 'node:assert/strict';
import {authorId,authorPath,authorData,profileLanguages,profileAlternates,profileStructuredData} from '../src/lib/author.ts';
test('all author links resolve to an actual language edition and share one identity',()=>{
  assert.deepEqual(profileLanguages,['en','ko']);
  for(const lang of ['en','ko','ja','zh-CN','de','fr','ru','es']){
    assert.equal(authorPath(lang),lang==='ko'?'/ko/about/':'/en/about/');
    assert.equal(authorData(lang)['@id'],authorId);
    assert.deepEqual(authorData(lang).sameAs,['https://github.com/youdozi']);
    assert.equal('jobTitle' in authorData(lang),false);
  }
});
test('profile schema identifies the displayed author without article or invented biography fields',()=>{
  for(const lang of profileLanguages){
    const [profile,breadcrumb]=profileStructuredData(lang);
    assert.equal(profile['@type'],'ProfilePage');assert.equal(profile.mainEntity.name,'youdozi');
    assert.equal(profile.mainEntity['@id'],authorId);assert.equal(profile.mainEntity.url,profile.url);
    assert.equal(profile.inLanguage,lang);assert.equal(breadcrumb.itemListElement.at(-1).item,profile.url);
  }
  assert.deepEqual(profileAlternates.map(a=>a.url),['/en/about/','/ko/about/']);
});
