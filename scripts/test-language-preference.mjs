import test from 'node:test';
import assert from 'node:assert/strict';
import {preferredLanguage,isSupportedLanguage} from '../src/lib/language-preference.ts';
import {supportedLanguages} from '../src/lib/locales.ts';

test('browser regional language tags select each published edition',()=>{
  for(const [tag,expected] of [['en-GB','en'],['ko-KR','ko'],['zh-CN','zh-CN'],['ja-JP','ja'],['de-AT','de'],['fr-CA','fr'],['ru-RU','ru'],['es-419','es']]){
    assert.equal(preferredLanguage([tag],null,supportedLanguages),expected,tag);
  }
});

test('explicit choices win; unavailable or forged saved values cannot become routes',()=>{
  for(const language of supportedLanguages)assert.equal(preferredLanguage(['ja-JP'],language,supportedLanguages),language);
  for(const value of ['../../review','https://example.com','ZH-cn','{"language":"ko"}','',null]){
    assert.equal(preferredLanguage(['ko-KR'],value,supportedLanguages),'ko');
  }
  assert.equal(preferredLanguage(['de-DE','ko-KR'],'fr',['en','ko']),'ko');
  assert.equal(isSupportedLanguage('zh-CN'),true);assert.equal(isSupportedLanguage('zh-TW'),false);
});

test('browser preference order is respected while invalid and unpublished editions are skipped',()=>{
  assert.equal(preferredLanguage(['pt-BR','fr-FR','ko-KR'],null,supportedLanguages),'fr');
  assert.equal(preferredLanguage(['ko-KR','en-US'],null,supportedLanguages),'ko');
  assert.equal(preferredLanguage(['bad_locale','../../ko','','ja-JP'],null,supportedLanguages),'ja');
  assert.equal(preferredLanguage(['ja-JP','de-DE','ko-KR'],null,['en','ko']),'ko');
  assert.equal(preferredLanguage([],null,supportedLanguages),'en');
  assert.equal(preferredLanguage(['pt-BR','ar'],null,supportedLanguages),'en');
});

test('simplified Chinese mapping respects explicit script before region and avoids Traditional substitution',()=>{
  for(const tag of ['zh','zh-CN','zh-SG','zh-Hans','zh-Hans-TW','ZH-hans-cn'])assert.equal(preferredLanguage([tag],null,supportedLanguages),'zh-CN',tag);
  for(const tag of ['zh-TW','zh-HK','zh-MO','zh-Hant','zh-Hant-CN','zh-Latn']){
    assert.equal(preferredLanguage([tag,'ja-JP'],null,supportedLanguages),'ja',tag);
    assert.equal(preferredLanguage([tag],null,supportedLanguages),'en',tag);
  }
  assert.equal(preferredLanguage(['zh-Hant','zh-Hans'],null,supportedLanguages),'zh-CN');
});
