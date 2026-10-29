import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,copyFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,dirname,join} from 'node:path';
import {inspectTechnicalTranslations,compareManuscript} from './check-technical-translations.mjs';
const root=resolve(import.meta.dirname,'..');
const manifestPath='.pipeline/technical-translations/batch-050/manifest.json';
const manifest=JSON.parse(await readFile(join(root,manifestPath),'utf8'));
async function fixture(key='2021-07-22-dot-product'){
  const row=manifest.editions.find(r=>r.language==='es'&&r.translationKey===key);
  return {row,source:await readFile(join(root,row.source.path),'utf8'),draft:await readFile(join(root,row.draft.path),'utf8'),diagram:JSON.parse(await readFile(join(root,row.diagramSource.path),'utf8'))};
}
function check(f,draft){return compareManuscript(f.source,draft,f.diagram,f.row.translationKey,f.row.language);}
test('all twelve complete private editions retain source code, structure and links',async()=>{
  const result=await inspectTechnicalTranslations();
  assert.equal(result.topics,2);assert.equal(result.preparedEditions,12);assert.equal(result.manifestApprovalRecorded,false);
});
test('overflow-changing cast in executable code is rejected',async()=>{
  const f=await fixture();assert.throws(()=>check(f,f.draft.replace('.map(i -> a[i] * b[i])','.map(i -> (long) (a[i] * b[i]))')),/Executable code/);
});
test('dropping the int overflow warning paragraph is rejected',async()=>{
  const f=await fixture();assert.throws(()=>check(f,f.draft.replace(/Para entradas mayores,[\s\S]*?\n\n/,'')),/Inline code/);
});
test('changing an example result is rejected',async()=>{
  const f=await fixture();assert.throws(()=>check(f,f.draft.replace('el resultado es 3','el resultado es 4')),/Numeric values/);
});
test('false sign mapped to a positive table value is rejected',async()=>{
  const f=await fixture('2021-07-22-plus-minus');assert.throws(()=>check(f,f.draft.replace('| 7 | false | -7 |','| 7 | false | 7 |')),/Table values/);
});
test('nonexistent localized link replacing a real English destination is rejected',async()=>{
  const f=await fixture();assert.throws(()=>check(f,f.draft.replace('/en/posts/','/es/posts/')),/Source links/);
});
test('inheriting an English publication date in a private translation is rejected',async()=>{
  const f=await fixture();assert.throws(()=>check(f,f.draft.replace('state: "draft"','state: "draft"\npublishedAt: "2026-10-29"')),/must not claim publication/);
});
test('edits to a pinned source invalidate the entire batch',async()=>{
  const folder=await mkdtemp(join(tmpdir(),'technical-translations-'));
  try{
    const paths=new Set([manifestPath,...manifest.editions.flatMap(r=>[r.source.path,r.draft.path,r.diagramSource.path,r.diagram.path,r.sourceDiagram.path])]);
    for(const path of paths){await mkdir(dirname(join(folder,path)),{recursive:true});await copyFile(join(root,path),join(folder,path));}
    await writeFile(join(folder,manifest.editions[0].source.path),'changed source');
    await assert.rejects(inspectTechnicalTranslations(folder),/Pinned file changed/);
  }finally{await rm(folder,{recursive:true,force:true});}
});
