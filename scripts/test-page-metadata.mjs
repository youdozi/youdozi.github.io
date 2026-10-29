import test from 'node:test';
import assert from 'node:assert/strict';
import {serializeJsonLd,articleMetadata,alternateLocales} from '../src/lib/page-metadata.ts';

test('JSON-LD round-trips special text without raw HTML opening delimiters or double escaping',()=>{
  const graph=[{headline:'Literal <tag> & "quote" </script><script>alert(1)</script>',description:'한글 日本語 简体 français русский \\u003c \u2028 \u2029'}];
  const serialized=serializeJsonLd(graph);
  assert.ok(!serialized.includes('<'));
  assert.deepEqual(JSON.parse(serialized),graph);
  assert.ok(serialized.includes('\\u003c/script>'));
});
test('article social dates reuse recorded dates and the actual author language fallback',()=>{
  const publishedAt=new Date('2023-09-18T15:00:00Z'),updatedAt=new Date('2026-10-27T05:23:47.316Z');
  for(const language of ['en','ko','zh-CN','ja','de','fr','ru','es']){
    const original=articleMetadata({language,publishedAt});
    assert.equal(original.publishedTime,publishedAt.toISOString());assert.equal(original.modifiedTime,publishedAt.toISOString());
    assert.equal(articleMetadata({language,publishedAt,updatedAt}).modifiedTime,updatedAt.toISOString());
    assert.equal(original.authorUrl,'https://youdozi.github.io'+(language==='ko'?'/ko/about/':'/en/about/'));
  }
});
test('social alternate locales use actual counterparts and exclude self and duplicates',()=>{
  assert.deepEqual(alternateLocales('en',[{language:'en'},{language:'ko'},{language:'ko'}]),['ko_KR']);
  assert.deepEqual(alternateLocales('ko',[{language:'ko'}]),[]);
  assert.deepEqual(alternateLocales('fr',[{language:'en'},{language:'fr'},{language:'zh-CN'}]),['en_US','zh_CN']);
});
