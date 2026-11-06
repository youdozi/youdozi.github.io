#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {createServer} from 'node:http';
import {resolve,join,sep} from 'node:path';
import {runInNewContext} from 'node:vm';
import {chromium} from 'playwright-core';
import {isolatedContext} from './browser/isolated-context.mjs';
import {chromePath} from './browser/chrome.mjs';

const key='youdozi-analytics-disabled',flag='ga-disable-G-XZVJ0K06M9';
const html=await readFile('dist/en/about/index.html','utf8');
const bootstrap=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes(key)&&s.includes('gtag'));
assert.ok(bootstrap,'Built production page must include the measurement gate');
assert.ok(!(await readFile('dist/review/index.html','utf8')).includes('googletagmanager.com/gtag/js'), 'Internal review visits must not load Analytics');
for(const preference of [null,'true','false','unexpected','storage-error']){
 const appended=[],listeners={},window={addEventListener:(name,fn)=>{listeners[name]=fn;}};
 let stored=preference;
 runInNewContext(bootstrap,{window,location:{hostname:'youdozi.github.io'},localStorage:{getItem(){if(stored==='storage-error')throw Error('denied');return stored;}},document:{createElement:()=>({}),head:{append:tag=>appended.push(tag)}},Date});
 assert.equal(appended.length,preference==='true'?0:1,'Opt-out must prevent loading the tag, not only hide the control');
 assert.equal(window[flag],preference==='true');
 stored='true';listeners.storage({key});assert.equal(window[flag],true,'Opt-out must disable an already open tab');
 stored=null;listeners.storage({key:null});assert.equal(window[flag],false);
}
const root=resolve('dist'),mime={html:'text/html',js:'text/javascript',css:'text/css',svg:'image/svg+xml',json:'application/json'};
const server=createServer(async(req,res)=>{
 try{
  let path=resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!path.startsWith(root+sep)){res.writeHead(403).end();return;}
  if((await stat(path)).isDirectory())path=join(path,'index.html');
  res.writeHead(200,{'Content-Type':mime[path.split('.').at(-1)]??'application/octet-stream'}).end(await readFile(path));
 }catch{res.writeHead(404).end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const base=`http://127.0.0.1:${server.address().port}`,checks=[];let browser;
try{
 browser=await chromium.launch({executablePath:await chromePath(),headless:true});
 for(const lang of ['en','ko'])for(const width of [320,1280]){
  const {context}=await isolatedContext(browser,{viewport:{width,height:950}});
  try{
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(`${base}/${lang}/about/`);
   assert.equal(await page.locator('[data-analytics-preference], [data-analytics-toggle]').count(),0,'About must not display measurement controls');
   assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),null);
   const other=await context.newPage();await other.goto(`${base}/${lang}/about/`);
   await page.evaluate(key=>localStorage.setItem(key,'true'),key);
   await other.waitForFunction(()=>window['ga-disable-G-XZVJ0K06M9']===true);
   await page.reload();assert.equal(await page.evaluate(flag=>window[flag],flag),true);
   await page.goto(`${base}/${lang}/categories/jdk/`);assert.equal(await page.evaluate(flag=>window[flag],flag),true);
   await page.evaluate(key=>localStorage.setItem(key,'false'),key);
   await other.waitForFunction(()=>window['ga-disable-G-XZVJ0K06M9']===false);
   await page.goto(`${base}/${lang}/about/`);
   assert.equal(await page.evaluate(flag=>window[flag],flag),false);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
   assert.deepEqual(errors,[]);checks.push({lang,width,noAboutControls:true,storedPreferenceAndOtherTab:true});
  }finally{await context.close();}
 }
 const {context}=await isolatedContext(browser);
 try{
  await context.addInitScript(()=>{Object.defineProperty(Storage.prototype,'getItem',{value(){throw Error('storage denied');}});});
  const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(base+'/en/about/');
  assert.equal(await page.locator('[data-analytics-preference], [data-analytics-toggle]').count(),0);
  assert.equal(await page.locator('h1').count(),1);assert.deepEqual(errors,[]);
  checks.push({storageDenied:'about-remains-readable'});
 }finally{await context.close();}
 console.log(JSON.stringify({bootstrapCases:5,browserChecks:checks}));
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
