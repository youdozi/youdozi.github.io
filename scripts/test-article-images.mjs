import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,symlink,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {satteri} from '@astrojs/markdown-satteri';
import {localImageSize,articleImagePlugin} from './article-images.mjs';

async function fixture(run){
 const root=await mkdtemp(join(tmpdir(),'article-images-'));await mkdir(join(root,'assets'));
 await writeFile(join(root,'assets','example.svg'),'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 240" width="120" height="240"></svg>');
 try{await run(root);}finally{await rm(root,{recursive:true,force:true});}
}
async function renderer(root){return satteri({hastPlugins:[articleImagePlugin(root)]}).createRenderer({syntaxHighlight:false});}

test('SVG and PNG dimensions come from file metadata, not filenames or alt text',()=>fixture(async root=>{
 assert.deepEqual(await localImageSize('/assets/example.svg?version=1#part',root),{width:120,height:240});
 const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==','base64');await writeFile(join(root,'assets','pixel.png'),png);
 assert.deepEqual(await localImageSize('/assets/pixel.png',root),{width:1,height:1});
}));
test('each document reserves real dimensions, preserves text and leaves its first image eager',()=>fixture(async root=>{
 const render=await renderer(root);const baseline=await satteri().createRenderer({syntaxHighlight:false});const md='![<kept> 한글 & 日本語](/assets/example.svg)\n\n![second](/assets/example.svg)';
 for(let i=0;i<2;i++){
  const result=await render.render(md);assert.equal((result.code.match(/width="120" height="240"/g)||[]).length,2);
  assert.equal((result.code.match(/loading="eager"/g)||[]).length,1);assert.equal((result.code.match(/loading="lazy"/g)||[]).length,1);
  assert.equal((result.code.match(/decoding="async"/g)||[]).length,2);assert.deepEqual(result.code.match(/alt="[^"]*"/g),(await baseline.render(md)).code.match(/alt="[^"]*"/g));
 }
}));
test('explicit HAST image policies and dimensions are preserved; one dimension derives its counterpart',()=>fixture(async root=>{
 const plugin=articleImagePlugin(root)();
 const rows=[{src:'/assets/example.svg',alt:'original',width:60,loading:'lazy',decoding:'sync'},{src:'/assets/example.svg',height:80},{src:'/assets/example.svg',width:12,height:24}];
 for(const properties of rows)await plugin.element.visit({properties},{setProperty(node,key,value){node.properties[key]=value;}});
 assert.deepEqual(rows[0],{src:'/assets/example.svg',alt:'original',width:60,height:120,loading:'lazy',decoding:'sync'});
 assert.equal(rows[1].width,40);assert.equal(rows[2].width,12);assert.equal(rows[2].height,24);
 const render=await renderer(root);const raw='<img src="/assets/example.svg" alt="original" width="60" height="120" loading="lazy" decoding="sync">';
 assert.equal((await render.render(raw)).code.trim(),raw);
}));
test('remote, protocol-relative and data URLs are never fetched or assigned invented dimensions',()=>fixture(async root=>{
 for(const src of ['https://example.invalid/private.png','//example.invalid/image.png','data:image/svg+xml,test','relative.png'])assert.equal(await localImageSize(src,root),undefined);
 const render=await renderer(root);const result=await render.render('![remote](https://example.invalid/private.png)');assert.ok(!result.code.includes('width='));assert.ok(!result.code.includes('loading='));
}));
test('missing, corrupt, traversal and outward symlink assets fail without reading arbitrary files',()=>fixture(async root=>{
 await assert.rejects(localImageSize('/assets/missing.svg',root));await writeFile(join(root,'assets','bad.svg'),'broken');await assert.rejects(localImageSize('/assets/bad.svg',root));
 for(const src of ['/assets/../../outside.svg','/assets/%2e%2e/outside.svg','/assets/..%2foutside.svg'])await assert.rejects(localImageSize(src,root));
 await writeFile(join(root,'outside.svg'),'<svg width="99" height="99"></svg>');await symlink(join(root,'outside.svg'),join(root,'assets','alias.svg'));await assert.rejects(localImageSize('/assets/alias.svg',root),/symlink/);
}));
