import {readFile,mkdir} from 'node:fs/promises';
import {chromium} from 'playwright-core';
import {chromePath} from './browser/chrome.mjs';
import {isolatedContext} from './browser/isolated-context.mjs';

// Editable SVG sources and checked-in PNGs; no remote assets or page requests.
const directory=new URL('../assets/img/social/',import.meta.url);
await mkdir(directory,{recursive:true});
const browser=await chromium.launch({executablePath:await chromePath(),headless:true});
try {
  const {context}=await isolatedContext(browser,{viewport:{width:1200,height:630},deviceScaleFactor:1});
  try {
    const page=await context.newPage();
    for(const language of ['en','ko']) {
      const name=`webclient-restclient-${language}`;
      const svg=await readFile(new URL(name+'.svg',directory),'utf8');
      await page.setContent(`<style>html,body{margin:0;width:1200px;height:630px}svg{display:block}</style>${svg}`);
      await page.evaluate(()=>document.fonts.ready);
      const overflow=await page.locator('svg text').evaluateAll(texts=>texts.some(text=>{const box=text.getBBox();return box.x<0||box.x+box.width>1200||box.y<0||box.y+box.height>630;}));
      if(overflow)throw Error('Social image text outside canvas: '+language);
      await page.locator('svg').screenshot({path:new URL(name+'.png',directory).pathname});
      console.log('Rendered '+name+'.png (1200×630)');
    }
  } finally {await context.close();}
} finally {await browser.close();}
