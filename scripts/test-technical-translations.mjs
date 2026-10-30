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


// Localized dates retain calendar identity without relaxing ordered numeric checks.
import {normalizeCalendarDates} from './translation-dates.mjs';
test('explicit localized calendar dates share identity, including yearless updates',()=>{
 const dates=['September 19, 2023','19. September 2023','19 septembre 2023','19 de septiembre de 2023','19 сентября 2023','2023年9月19日'];
 for(const date of dates)assert.equal(normalizeCalendarDates(date),normalizeCalendarDates(dates[0]));
 for(const date of ['9. Oktober','9 octobre','9 de octubre','9 октября','10月9日'])assert.equal(normalizeCalendarDates(date),normalizeCalendarDates('October 9'));
 assert.notEqual(normalizeCalendarDates('October 9'),normalizeCalendarDates('October 10'));
 assert.notEqual(normalizeCalendarDates('September 19, 2023'),normalizeCalendarDates('September 19, 2024'));
});
test('calendar normalization leaves versions, ambiguous dates and invalid dates literal',()=>{
 for(const value of ['JDK 21.0.1 and 17.0.8.1','1..65535','10/11/2023','may 21 threads','31 février 2023','2023年2月29日'])assert.equal(normalizeCalendarDates(value),value);
});

test('full translated manuscripts accept localized dates and reject changed dates or versions',async()=>{
 const m=JSON.parse(await readFile(join(root,'.pipeline/technical-translations/batch-058/manifest.json'),'utf8'));
 for(const language of m.languages){
  const row=m.editions.find(r=>r.language===language&&r.translationKey==='2023-10-10-temurin-jdk21-delay');
  const f={row,source:await readFile(join(root,row.source.path),'utf8'),draft:await readFile(join(root,row.draft.path),'utf8'),diagram:JSON.parse(await readFile(join(root,row.diagramSource.path),'utf8'))};
  assert.doesNotThrow(()=>check(f,f.draft));
  const changed=f.draft.replace(language==='zh-CN'||language==='ja'?'10月9日':language==='de'?'9. Oktober':language==='fr'?'9 octobre':language==='ru'?'9 октября':'9 de octubre',language==='zh-CN'||language==='ja'?'10月8日':language==='de'?'8. Oktober':language==='fr'?'8 octobre':language==='ru'?'8 октября':'8 de octubre');
  assert.notEqual(changed,f.draft);assert.throws(()=>check(f,changed),/Numeric values/);
  assert.throws(()=>check(f,f.draft.replace('Java 21','Java 22')),/Numeric values/);
 }
});
