#!/usr/bin/env node
/** Small read-only public-page smoke check with mandatory telemetry isolation. */
import {parseArgs} from 'node:util';
import {chromium} from 'playwright-core';
import {isolatedContext} from './browser/isolated-context.mjs';
import {chromePath} from './browser/chrome.mjs';
const {values}=parseArgs({options:{url:{type:'string',multiple:true}}});
const urls=values.url??[];
if(!urls.length||urls.length>20)throw new Error('Provide one to twenty --url values');
for(const value of urls){const url=new URL(value);if(!['http:','https:'].includes(url.protocol)||!['youdozi.github.io','127.0.0.1','localhost'].includes(url.hostname)||url.username||url.password||url.search||url.hash)throw new Error('Use clean public site or loopback URLs without credentials or queries');}
const browser=await chromium.launch({executablePath:await chromePath(),headless:true});const pages=[];
try{
  for(const url of urls){
    const {context,summary}=await isolatedContext(browser);
    try{const page=await context.newPage();const response=await page.goto(url,{waitUntil:'networkidle',timeout:30000});const title=await page.title();const h1=await page.locator('h1').count();const ok=response?.status()===200&&title.trim().length>0&&h1===1;
      pages.push({requestedURL:url,resolvedURL:page.url(),httpStatus:response?.status(),title,h1,ok,isolation:summary()});
    }finally{await context.close();}
  }
}finally{await browser.close();}
console.log(JSON.stringify({mode:'read-only-telemetry-isolated',pages},null,2));if(pages.some(p=>!p.ok))process.exitCode=1;
