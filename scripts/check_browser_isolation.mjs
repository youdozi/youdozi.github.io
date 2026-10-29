/** Local real-browser proof: no Google connections are needed or allowed. */
import {createServer} from 'node:http';
import assert from 'node:assert/strict';
import {chromium} from 'playwright-core';
import {isolatedContext,telemetryDecision} from './browser/isolated-context.mjs';
import {chromePath} from './browser/chrome.mjs';

const received=[];
const server=createServer((request,response)=>{
  const url=new URL(request.url,'http://local.invalid');
  if(telemetryDecision(url.href)==='block'||url.pathname==='/proxy-metrics')received.push(url.pathname);
  if(url.pathname==='/worker.js'){response.setHeader('Content-Type','text/javascript');response.end("self.onmessage=()=>fetch('/g/collect?tid=G-XZVJ0K06M9&en=worker').catch(()=>{});");return;}
  if(url.pathname==='/popup'){response.end("<script>fetch('/collect?tid=G-XZVJ0K06M9&en=popup').catch(()=>{});</script>");return;}
  response.setHeader('Content-Type','text/html');response.end('<!doctype html><title>Local isolation fixture</title><h1>Fixture works</h1>');
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;const results=[];
try{
  browser=await chromium.launch({executablePath:await chromePath(),headless:true});
  for(const mode of ['verification','tag-verification']){
    const {context,summary}=await isolatedContext(browser,{},mode);
    try{
      const page=await context.newPage();await page.goto(origin);
      await page.evaluate(async()=>{
        await fetch('/normal-content');
        const attempts=[fetch('https://www.google-analytics.com/g/collect?tid=G-XZVJ0K06M9&en=external'),fetch('/g/collect?tid=G-XZVJ0K06M9&en=page_view'),fetch('/mp/collect',{method:'POST',body:'tid=G-XZVJ0K06M9&en=post'}),fetch('/proxy-metrics',{method:'POST',body:'tid=G-XZVJ0K06M9&en=proxy'})];
        navigator.sendBeacon('/collect?tid=G-XZVJ0K06M9&en=beacon','test');
        const image=new Image();image.src='/collect?tid=G-XZVJ0K06M9&en=image';
        const script=document.createElement('script');script.src='/collect?tid=G-XZVJ0K06M9&en=script';document.head.append(script);
        const worker=new Worker('/worker.js');worker.postMessage('run');
        window.open('/popup');
        await Promise.allSettled(attempts);
      });
      await page.waitForFunction(()=>window.document.readyState==='complete');
      for(let i=0;i<60&&summary().blocked<9;i++)await page.waitForTimeout(50);
      assert.equal(await page.locator('h1').textContent(),'Fixture works');
      assert.equal(summary().blocked,9);assert.equal(summary().blockedCollection,9);
      assert.equal(received.length,0,'No telemetry endpoint may reach the server');results.push(summary());
      // No external network needed to verify tag-mode's narrowly scoped exception.
      assert.equal(telemetryDecision('https://www.googletagmanager.com/gtag/js?id=G-XZVJ0K06M9','',mode),mode==='verification'?'block':'allow-tag');
    }finally{await context.close();}
  }
  console.log(JSON.stringify({cases:results,telemetryRequestsReceivedByFixture:received.length}));
  console.log('[ok] Real Chrome: GET/POST, proxy payload, beacon, image, script, worker and popup telemetry blocked; normal content remains available.');
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
