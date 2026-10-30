#!/usr/bin/env node
/** Verify root-only negotiation and explicit language choices with telemetry blocked. */
import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {createServer} from 'node:http';
import {resolve,join,sep} from 'node:path';
import {parseArgs} from 'node:util';
import {chromium} from 'playwright-core';
import {isolatedContext} from './browser/isolated-context.mjs';
import {chromePath} from './browser/chrome.mjs';

const {values}=parseArgs({options:{url:{type:'string'}}});
const languages=['en','ko','zh-CN','ja','de','fr','ru','es'];
const key='youdozi.language';
let server,base;
if(values.url){
  const url=new URL(values.url);
  assert.ok(['http:','https:'].includes(url.protocol)&&['youdozi.github.io','127.0.0.1','localhost'].includes(url.hostname)&&!url.username&&!url.password&&!url.search&&!url.hash&&url.pathname==='/','Use a clean site origin');
  base=url.origin;
}else{
  const dist=resolve('dist'),mime={html:'text/html',css:'text/css',js:'text/javascript',json:'application/json',svg:'image/svg+xml'};
  server=createServer(async(req,res)=>{
    try{
      let path=resolve(dist,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
      if(path!==dist&&!path.startsWith(dist+sep)){res.writeHead(403).end();return;}
      if((await stat(path)).isDirectory())path=join(path,'index.html');
      res.writeHead(200,{'Content-Type':mime[path.split('.').at(-1)]??'application/octet-stream'}).end(await readFile(path));
    }catch{res.writeHead(404).end();}
  });
  await new Promise(done=>server.listen(0,'127.0.0.1',done));base='http://127.0.0.1:'+server.address().port;
}
let browser;
const checks=[];
async function run(name,options,body,init){
  const {context,summary}=await isolatedContext(browser,options);
  try{
    if(init)await context.addInitScript(init);
    const page=await context.newPage(),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await body(page,context);
    assert.deepEqual(errors,[],name+' must not throw');
    checks.push({name,passed:true,isolation:summary()});
  }finally{await context.close();}
}
async function root(page,language,suffix=''){
  await page.goto(base+'/'+suffix);
  await page.waitForURL(url=>url.pathname===`/${language}/`);
  assert.equal(await page.locator('html').getAttribute('lang'),language);
  assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),`https://youdozi.github.io/${language}/`);
}
async function choose(page,language,keyboard=false){
  await page.locator('.language-menu summary').click();
  const link=page.locator(`.language-menu a[data-language-choice="${language}"]`);
  if(keyboard)await link.press('Enter');else await link.click();
}
try{
  browser=await chromium.launch({executablePath:await chromePath(),headless:true});
  for(const width of [320,1360]){
    for(const [locale,expected] of [['en-GB','en'],['ko-KR','ko'],['zh-CN','zh-CN'],['ja-JP','ja'],['de-AT','de'],['fr-CA','fr'],['ru-RU','ru'],['es-419','es'],['pt-BR','en'],['zh-TW','en']]){
      await run(`browser-${locale}-${width}`,{locale,viewport:{width,height:950}},async page=>{
        await root(page,expected,'?from=language-test#main');
        assert.equal(new URL(page.url()).searchParams.get('from'),'language-test');assert.equal(new URL(page.url()).hash,'#main');
        assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),null,'detection must not overwrite manual preferences');
        await page.locator('.language-menu summary').click();
        assert.equal(await page.locator('.language-menu a[data-language-choice]').count(),8);
        assert.equal(await page.locator('.language-menu a[aria-current=page]').getAttribute('data-language-choice'),expected);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
      });
    }
    await run(`manual-choices-${width}`,{locale:'ja-JP',viewport:{width,height:950}},async page=>{
      for(const language of languages){
        // Explicit URLs must win even after a different manual choice was saved.
        await page.goto(base+'/en/');
        assert.equal(new URL(page.url()).pathname,'/en/');
        await choose(page,language,language==='ko');
        await page.waitForURL(url=>url.pathname===`/${language}/`);
        assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),language);
        await root(page,language);
      }
      const article='/en/posts/2023-09-19-springboot-test-webclient/';
      await page.goto(base+article);
      assert.equal(new URL(page.url()).pathname,article);
      await choose(page,'ko',true);
      await page.waitForURL(url=>url.pathname===article.replace('/en/','/ko/'));
      await root(page,'ko');
      await page.goto(base+article);
      assert.equal(new URL(page.url()).pathname,article);
      await root(page,'ko');
      await page.goBack();
      assert.equal(new URL(page.url()).pathname,article,'root replace must not create a redirect loop on Back');
      await page.goto(base+'/ko/search/?q=WebClient');
      await page.locator('#results a').first().waitFor();
      await choose(page,'ko');
      assert.equal(new URL(page.url()).searchParams.get('q'),'WebClient','selecting the current language preserves search state');
    });
  }
  await run('priority-and-saved-validation',{locale:'en-US'},async page=>{
    await root(page,'fr');
    await page.evaluate(key=>localStorage.setItem(key,'../../review'),key);
    await root(page,'fr');
    await page.evaluate(key=>localStorage.setItem(key,'de'),key);
    await root(page,'de');
  },()=>Object.defineProperty(navigator,'languages',{get:()=>['pt-BR','fr-CA','ko-KR']}));
  await run('storage-blocked',{locale:'ko-KR'},async page=>{
    await root(page,'ko');await choose(page,'ja');await page.waitForURL(url=>url.pathname==='/ja/');
    await root(page,'ko');
  },()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError');}}));
  await run('javascript-disabled',{locale:'ko-KR',javaScriptEnabled:false},async page=>{
    await page.goto(base+'/');await page.waitForURL(url=>url.pathname==='/en/');
    await choose(page,'ko');await page.waitForURL(url=>url.pathname==='/ko/');
  });
  await run('entry-script-blocked',{locale:'ko-KR'},async page=>{
    await page.route('**/*',async route=>route.request().resourceType()==='script'?route.abort():route.continue());
    await page.goto(base+'/');assert.equal(new URL(page.url()).pathname,'/');
    assert.equal(await page.locator('a[data-language-choice]').count(),8);
    assert.equal(await page.locator('meta[name=robots]').getAttribute('content'),'noindex,follow');
    assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),'https://youdozi.github.io/en/');
    await page.locator('a[data-language-choice=ko]').click();await page.waitForURL(url=>url.pathname==='/ko/');
  });
}finally{
  if(browser)await browser.close();if(server)await new Promise(done=>server.close(done));
}
console.log(JSON.stringify({passed:true,cases:checks.length,checks}));
