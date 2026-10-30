#!/usr/bin/env node
/** Exercise the generated search UI in an isolated Chrome context. */
import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {createServer} from 'node:http';
import {resolve,join,sep} from 'node:path';
import {parseArgs} from 'node:util';
import {chromium} from 'playwright-core';
import {isolatedContext} from './browser/isolated-context.mjs';
import {chromePath} from './browser/chrome.mjs';

const {values}=parseArgs({options:{url:{type:'string'}}});
let server;
let base;
if(values.url){
  const url=new URL(values.url);
  assert.ok(['http:','https:'].includes(url.protocol)&&['youdozi.github.io','127.0.0.1','localhost'].includes(url.hostname)&&!url.username&&!url.password&&!url.search&&!url.hash&&url.pathname==='/','Use a clean site origin');
  base=url.origin;
}else{
  const dist=resolve('dist');
  const mime={html:'text/html',css:'text/css',js:'text/javascript',json:'application/json',svg:'image/svg+xml'};
  server=createServer(async(req,res)=>{
    try{
      let path=resolve(dist,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
      if(path!==dist&&!path.startsWith(dist+sep)){res.writeHead(403).end();return;}
      if((await stat(path)).isDirectory())path=join(path,'index.html');
      res.writeHead(200,{'Content-Type':mime[path.split('.').at(-1)]??'application/octet-stream'}).end(await readFile(path));
    }catch{res.writeHead(404).end();}
  });
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  base='http://127.0.0.1:'+server.address().port;
}

const browser=await chromium.launch({executablePath:await chromePath(),headless:true});
const checks=[];
try{
  for(const width of [320,1360]){
    const {context,summary}=await isolatedContext(browser,{viewport:{width,height:900}});
    try{
      const page=await context.newPage();
      for(const lang of ['en','ko','zh-CN','ja','de','fr','ru','es']){
        const index=await (await context.request.get(`${base}/${lang}/search-index.json`)).json();
        assert.ok(index.length>0);
        const query=index[0].title;
        const url=new URL(`/${lang}/search/`,base);url.searchParams.set('q',query);
        await page.goto(url.href);
        const input=page.locator('#search');
        await page.waitForFunction(()=>document.querySelector('#results a'));
        assert.equal(await input.inputValue(),query);
        const links=await page.locator('#results a').evaluateAll(links=>links.map(a=>a.getAttribute('href')));
        assert.ok(links.includes(index[0].url));
        assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),`https://youdozi.github.io/${lang}/search/`);
        assert.match(await page.locator('meta[name=robots]').getAttribute('content'),/noindex/);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
        await page.reload();await page.waitForFunction(()=>document.querySelector('#results a'));
        assert.deepEqual(await page.locator('#results a').evaluateAll(links=>links.map(a=>a.getAttribute('href'))),links);
        const searchURL=page.url();
        await page.locator('#results a').first().click();await page.waitForURL(url=>!url.pathname.endsWith('/search/'));
        await page.goBack();await page.waitForFunction(()=>document.querySelector('#results a'));
        assert.equal(page.url(),searchURL);assert.equal(await input.inputValue(),query);
        const historyLength=await page.evaluate(()=>history.length);
        await input.fill('a query that has no matching article 064');
        await page.waitForFunction(()=>new URL(location.href).searchParams.get('q')==='a query that has no matching article 064'&&document.querySelector('#results').getAttribute('aria-busy')==='false');
        assert.equal(await page.locator('#results a').count(),0);
        assert.ok((await page.locator('#status').textContent()).trim());
        assert.equal(await page.evaluate(()=>history.length),historyLength);
        await input.fill('');
        await page.waitForFunction(()=>!new URL(location.href).searchParams.has('q'));
        assert.equal(await page.locator('#results a').count(),0);
        assert.equal(await page.locator('#status').textContent(),'');
        checks.push({lang,width,restored:true,shared:true,back:true,clear:true});
      }

      // Real network failure, retry, and late-response cancellation in a separate page.
      let attempts=0;
      await page.route('**/en/search-index.json',async route=>{
        if(++attempts===1)await route.fulfill({status:503,body:'unavailable'});
        else await route.continue();
      });
      await page.goto(`${base}/en/search/?q=WebClient`);
      await page.locator('#search-retry').waitFor({state:'visible'});
      await page.locator('#search-retry').click();
      await page.waitForFunction(()=>document.querySelector('#results a'));
      assert.equal(attempts,2);
      await page.unroute('**/en/search-index.json');

      // Composition events are synthetic; this checks event handling, not an OS IME.
      const input=page.locator('#search');
      await input.evaluate(input=>{
        input.dispatchEvent(new CompositionEvent('compositionstart'));
        input.value='한';input.dispatchEvent(new InputEvent('input',{isComposing:true}));
      });
      assert.equal(new URL(page.url()).searchParams.get('q'),'WebClient');
      await input.evaluate(input=>{
        input.value='한글';input.dispatchEvent(new CompositionEvent('compositionend'));
      });
      await page.waitForFunction(()=>new URL(location.href).searchParams.get('q')==='한글');
      await page.evaluate(()=>{history.pushState(null,'','?q=WebClient');dispatchEvent(new PopStateEvent('popstate'));});
      await page.waitForFunction(()=>document.querySelector('#search').value==='WebClient'&&document.querySelector('#results a'));

      const payload='<img src=x onerror="window.searchInjected=true">';
      await input.fill(payload);
      await page.waitForFunction(query=>new URL(location.href).searchParams.get('q')===query,payload);
      assert.equal(await page.evaluate(()=>window.searchInjected),undefined);
      assert.equal(await page.locator('#results img').count(),0);

      await page.route('**/en/search-index.json',async route=>{
        await new Promise(done=>setTimeout(done,400));await route.continue();
      });
      await page.goto(`${base}/en/search/?q=WebClient`);
      await page.locator('#search').fill('');
      await page.waitForTimeout(650);
      assert.equal(await page.locator('#results a').count(),0);
      assert.equal(await page.locator('#status').textContent(),'');
      assert.equal(await page.locator('#results').getAttribute('aria-busy'),'false');
      console.log(JSON.stringify({width,editions:8,retry:true,compositionEvents:true,popstate:true,literalQuery:true,staleResponse:true,isolation:summary()}));
    }finally{await context.close();}
  }
}finally{
  await browser.close();if(server)await new Promise(done=>server.close(done));
}
console.log(JSON.stringify({passed:true,pages:checks.length,checks}));
