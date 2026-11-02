#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {createServer} from 'node:http';
import {resolve,join,sep} from 'node:path';
import {chromium} from 'playwright-core';
import {chromePath} from './browser/chrome.mjs';
import {isolatedContext} from './browser/isolated-context.mjs';

const dist=resolve('dist'),mime={html:'text/html',css:'text/css',js:'text/javascript',json:'application/json',svg:'image/svg+xml'};
const server=createServer(async(req,res)=>{
  try{
    let path=resolve(dist,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
    if(path!==dist&&!path.startsWith(dist+sep)){res.writeHead(403).end();return;}
    if((await stat(path)).isDirectory())path=join(path,'index.html');
    res.writeHead(200,{'Content-Type':mime[path.split('.').at(-1)]??'application/octet-stream'}).end(await readFile(path));
  }catch{res.writeHead(404).end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const base='http://127.0.0.1:'+server.address().port;
const samples=['/en/posts/2026-11-02-ai-assisted-attack-defense/','/ko/posts/2026-11-02-ai-assisted-tdd/','/de/posts/2023-09-19-springboot-test-webclient/','/ja/'];
let browser;
const checks=[];
try{
  browser=await chromium.launch({executablePath:await chromePath(),headless:true});
  for(const width of [320,360])for(const path of samples){
    const {context,summary}=await isolatedContext(browser,{viewport:{width,height:800}});
    try{
      const page=await context.newPage(),errors=[];
      page.on('pageerror',error=>errors.push(error.message));
      const response=await page.goto(base+path,{waitUntil:'networkidle'});
      assert.equal(response.status(),200);
      assert.deepEqual(errors,[],path+' script errors');
      const result=await page.evaluate(()=>{
        const h=e=>e.getBoundingClientRect().height;
        const targets=[...document.querySelectorAll('.site-header nav>a,.language-menu summary,.code-tools button,.footer-links>a')];
        return {overflow:document.documentElement.scrollWidth>innerWidth,
          smallTargets:targets.filter(e=>h(e)<43.5).map(e=>e.textContent),
          code:[...document.querySelectorAll('.prose pre')].map(e=>({focusable:e.tabIndex===0,name:!!(e.getAttribute('aria-label')||e.getAttribute('aria-labelledby'))})),
          unnamedLinks:[...document.querySelectorAll('a')].filter(e=>!e.textContent.trim()&&!e.getAttribute('aria-label')&&!e.querySelector('img[alt]')).length,
          navigationMs:Math.round(performance.getEntriesByType('navigation')[0].duration),
          inlineScriptBytes:[...document.scripts].filter(e=>!e.src&&(!e.type||['module','text/javascript'].includes(e.type))).reduce((n,e)=>n+new TextEncoder().encode(e.textContent).length,0),
          scriptBytes:performance.getEntriesByType('resource').filter(e=>/\.m?js$/.test(new URL(e.name).pathname)).reduce((n,e)=>n+e.decodedBodySize,0)};
      });
      assert.equal(result.overflow,false,path+' horizontal overflow');
      assert.deepEqual(result.smallTargets,[],path+' touch targets');
      assert.equal(result.unnamedLinks,0,path+' unnamed links');
      assert.ok(result.code.every(e=>e.focusable&&e.name),path+' keyboard-accessible code');
      // A project budget for reader scripts; this is not a Core Web Vitals threshold.
      assert.ok(result.scriptBytes+result.inlineScriptBytes<64*1024,path+' reader script budget');
      await page.locator('.skip-link').focus();await page.keyboard.press('Enter');
      assert.equal(await page.evaluate(()=>document.activeElement.id),'main',path+' skip link focus');
      const menu=page.locator('.language-menu');
      await menu.locator('summary').focus();await page.keyboard.press('Space');
      assert.equal(await menu.getAttribute('open'),'');
      assert.equal(await menu.locator('a[data-language-choice]').count(),8);
      const menuFits=await menu.locator('ul').evaluate(e=>{const b=e.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth;});
      assert.ok(menuFits,path+' language menu fits viewport');
      checks.push({path,width,...result,isolation:summary()});
    }finally{await context.close();}
  }
  console.log(JSON.stringify({scope:'Local mobile reading regression and synthetic resource budget; no field Core Web Vitals or complete WCAG conformance claim',checks},null,2));
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
