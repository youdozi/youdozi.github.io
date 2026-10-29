import test from 'node:test';import assert from 'node:assert/strict';
import {telemetryDecision,isolatedContext} from './browser/isolated-context.mjs';
test('default verification blocks tag libraries and Google telemetry on all subdomains',()=>{
 for(const url of ['https://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9','https://region1.google-analytics.com/g/collect','https://analytics.google.com/g/collect','https://stats.g.doubleclick.net/g/collect'])assert.equal(telemetryDecision(url),'block');
 assert.equal(telemetryDecision('https://google-analytics.com.evil.invalid/article'),'allow');
});
test('collection paths and first-party GA proxy payloads are blocked without saving payloads',()=>{
 for(const path of ['/collect','/g/collect','/mp/collect','/debug/mp/collect','/batch'])assert.equal(telemetryDecision('https://youdozi.github.io'+path),'block');
 assert.equal(telemetryDecision('https://local.invalid/custom','tid=G-XZVJ0K06M9&en=page_view'),'block');
 assert.equal(telemetryDecision('https://local.invalid/page'),'allow');
});
test('tag verification permits only the exact HTTPS Google tag for this site; measurement stays blocked',()=>{
 const mode='tag-verification';assert.equal(telemetryDecision('https://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9','',mode),'allow-tag');
 for(const url of ['http://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9','https://www.googletagmanager.com/gtag/js?id=G-OTHER','https://google-analytics.com/g/collect'])assert.equal(telemetryDecision(url,'',mode),'block');
 assert.equal(telemetryDecision('https://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9','',mode,'POST'),'block');
 assert.equal(telemetryDecision('https://www.googletagmanager.com:444/gtag/js?id=G-XZVJ0K06M9','',mode),'block');
 assert.equal(telemetryDecision('https://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9&tid=G-XZVJ0K06M9','',mode),'block');
 assert.throws(()=>telemetryDecision('https://example.com','','off'),/Unknown/);
});
test('context policy blocks service workers before pages and records counts without raw URLs',async()=>{
 let options,handler;const context={async route(pattern,fn){assert.equal(pattern,'**/*');handler=fn;},async close(){}};
 const browser={async newContext(value){options=value;return context;}};const isolated=await isolatedContext(browser,{serviceWorkers:'allow'});assert.equal(options.serviceWorkers,'block');
 let aborted=false;await handler({request:()=>({url:()=> 'https://google-analytics.com/g/collect?secret=private',postData:()=>null,method:()=> 'GET'}),abort:async()=>{aborted=true;}});
 assert.equal(aborted,true);assert.deepEqual(isolated.summary(),{mode:'verification',serviceWorkers:'block',blocked:1,blockedCollection:1,allowedTag:0});assert.ok(!JSON.stringify(isolated.summary()).includes('private'));
});

test('default regression command and CI execute the shared browser isolation checks',async()=>{
 const {readFile}=await import('node:fs/promises');
 const pkg=JSON.parse(await readFile(new URL('../package.json',import.meta.url),'utf8'));
 assert.ok(pkg.scripts.test.includes('scripts/test-browser-isolation.mjs'));
 assert.equal(pkg.scripts['check:browser-isolation'],'node scripts/check_browser_isolation.mjs');
 const workflow=await readFile(new URL('../.github/workflows/site-checks.yml',import.meta.url),'utf8');
 assert.ok(workflow.includes('run: npm run check:browser-isolation'));
});
