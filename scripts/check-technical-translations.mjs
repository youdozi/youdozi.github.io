#!/usr/bin/env node
/** Validate private technical translation manuscripts; never publish or create routes. */
import {readFile,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,relative,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {parse} from 'yaml';
import policy from '../src/lib/locales.json' with {type:'json'};

const root=resolve(import.meta.dirname,'..');
const defaultManifest='.pipeline/technical-translations/batch-050/manifest.json';
const sha=value=>createHash('sha256').update(value).digest('hex');
const fail=message=>{throw new Error(message);};
const same=(a,b,message)=>{if(JSON.stringify(a)!==JSON.stringify(b))fail(message);};
function article(raw){
  const match=/^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(raw);
  if(!match)fail('Missing Markdown frontmatter');
  return {meta:parse(match[1]),body:match[2]};
}
function code(body){return [...body.matchAll(/^```([^\n]*)\n([\s\S]*?)^```[ \t]*$/gm)].map(m=>[m[1],m[2]]);}
function prose(body){return body.replace(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm,'');}
function inline(body){return [...prose(body).matchAll(/`([^`\n]+)`/g)].map(m=>m[1]).sort();}
function links(body){return [...prose(body).matchAll(/(?<!!)\[[^\]\n]*\]\(([^)]+)\)/g)].map(m=>m[1]);}
function numbers(body){
  // Ignore link paths, image alt (a duplicate caption), code and localized digit grouping.
  const visible=prose(body).replace(/!\[[^\]\n]*\]\([^)]+\)/g,'').replace(/\]\([^)]+\)/g,']')
    .replace(/`[^`\n]+`/g,'').replace(/(\d)[,.\u00a0\u202f](?=\d{3}(?:\D|$))/g,'$1');
  return visible.match(/\d+/g)??[];
}
function shape(body){return prose(body).trim().split(/\n\n+/).map(block=>block.startsWith('## ')?'heading':block.startsWith('![')?'image':block.startsWith('| ')?'table':'paragraph');}
const escape=value=>value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');

export function compareManuscript(sourceRaw,draftRaw,diagram,key,language){
  const source=article(sourceRaw),draft=article(draftRaw),m=draft.meta;
  if(m.state!=='draft'||m.language!==language||m.translationKey!==key||!m.title?.trim()||!m.description?.trim())fail('Invalid draft identity or localized metadata');
  if(['publishedAt','updatedAt','approval','reviewedAt','reviewStatus'].some(k=>k in m))fail('Private draft must not claim publication or inherited review');
  if(source.meta.translationKey!==key||source.meta.language!=='en'||source.meta.kind!=='post'||source.meta.reviewStatus==='example')fail('Expected eligible English technical source');
  same(code(source.body),code(draft.body),'Executable code changed during translation');
  same(inline(source.body),inline(draft.body),'Inline code changed or omitted');
  same(links(source.body),links(draft.body),'Source links changed, reordered or omitted');
  same(numbers(source.body),numbers(draft.body),'Numeric values changed or omitted');
  same(shape(source.body),shape(draft.body),'Source paragraph, heading or table structure changed');
  const rows=body=>body.split('\n').filter(line=>line.startsWith('|')).map(line=>line.replace(/`[^`]+`/g,m=>m.replaceAll('|','\u0000')).split('|').slice(1,-1).map(cell=>cell.trim().replaceAll('\u0000','|')));
  const sourceRows=rows(source.body),draftRows=rows(draft.body);
  same(sourceRows.map(row=>row.length),draftRows.map(row=>row.length),'Table structure changed or omitted');
  sourceRows.forEach((row,i)=>row.forEach((cell,j)=>{
    const translated=draftRows[i][j];
    same(inline(cell),inline(translated),'Table code changed or omitted');
    same(numbers(cell),numbers(translated),'Table numbers changed or omitted');
    if(/^(?:true|false|[-+]?\d[\d, .]*|`[^`]+`)$/.test(cell)&&cell!==translated)fail('Table values changed or omitted');
  }));
  const images=[...draft.body.matchAll(/!\[([^\]\n]+)\]\(([^)]+)\)/g)];
  if(images.length!==1||images[0][1]!==diagram.description||images[0][2]!==`${key}.svg`||!draft.body.includes(`\n\n${diagram.description}\n\n`))fail('Localized diagram, alt or adjacent caption missing');
  return {source,draft};
}

export async function inspectTechnicalTranslations(base=root,manifestPath=defaultManifest){
  const canonicalBase=await realpath(base);
  async function pinned(record,prefix){
    if(!record||!record.path?.startsWith(prefix)||!(/^[a-f0-9]{64}$/).test(record.sha256))fail('Invalid pinned file');
    const file=await realpath(resolve(canonicalBase,record.path));
    if(relative(canonicalBase,file)!==record.path)fail('Pinned file escapes its declared path');
    const raw=await readFile(file,'utf8');if(sha(raw)!==record.sha256)fail(`Pinned file changed: ${record.path}`);return raw;
  }
  if(!manifestPath.startsWith('.pipeline/technical-translations/'))fail('Expected private technical manifest');
  const manifestFile=await realpath(resolve(canonicalBase,manifestPath));
  if(relative(canonicalBase,manifestFile)!==manifestPath)fail('Manifest escapes private path');
  const manifest=JSON.parse(await readFile(manifestFile,'utf8'));
  if(manifest.schemaVersion!==1||manifest.state!=='awaiting-publication-approval'||manifest.approval!==null||!manifest.editions?.length)fail('Expected unapproved translation manifest');
  same(manifest.languages,policy.translationLanguages,'Expected all six target languages');
  const seen=new Set(),byTopic=new Map();
  const prefix=relative(canonicalBase,dirname(manifestFile))+'/';
  for(const row of manifest.editions){
    const {language,translationKey:key}=row;
    if(!manifest.languages.includes(language)||!/^\d{4}-\d{2}-\d{2}-[a-z0-9.-]+$/.test(key)||row.key!==`${language}-${key}`||seen.has(row.key))fail('Duplicate or invalid translation key');
    seen.add(row.key);byTopic.set(key,[...(byTopic.get(key)??[]),language]);
    const sourceRaw=await pinned(row.source,'src/content/posts/en/');
    if(row.source.path!==`src/content/posts/en/${key}.md`)fail('Wrong English source');
    const draftRaw=await pinned(row.draft,prefix),svg=await pinned(row.diagram,prefix);
    const diagram=JSON.parse(await pinned(row.diagramSource,prefix));
    for(const [record,ext] of [[row.draft,'md'],[row.diagram,'svg'],[row.diagramSource,'diagram.json']]){
      if(record.path!==`${prefix}${language}/${key}.${ext}`)fail('Noncanonical draft asset path');
    }
    const original=JSON.parse(await pinned(row.sourceDiagram,'content/diagrams/')).diagrams.find(d=>d.key===key);
    if(!original||diagram.key!==key||diagram.language!==language||!diagram.title?.trim()||!diagram.description?.trim())fail('Invalid localized flow source');
    same(diagram.steps.map(s=>s.kind),original.steps.map(s=>s.kind),'Flow structure changed');
    original.steps.forEach((step,i)=>{
      const localized=diagram.steps[i];
      if(Boolean(step.branch)!==Boolean(localized.branch))fail('Flow branch was added or omitted');
      if(step.branch){
        if((step.branch.outcome??'error')!==localized.branch.outcome)fail('Flow exit outcome changed');
        for(const label of ['exit','continue'])if(typeof localized.branch[label]!=='string'||!localized.branch[label].trim()||localized.branch[label].length>12)fail('Missing or oversized branch label');
      }
    });
    if(Boolean(original.loop)!==Boolean(diagram.loop))fail('Flow loop was added or omitted');
    if(original.loop&&(original.loop.from!==diagram.loop.from||original.loop.to!==diagram.loop.to||typeof diagram.loop.label!=='string'||!diagram.loop.label.trim()))fail('Flow loop endpoints or label changed');
    if(diagram.steps.some(s=>!Array.isArray(s.lines)||s.lines.length<1||s.lines.length>3||s.lines.some(line=>typeof line!=='string'||!line.trim())))fail('Empty or invalid translated flow step');
    const {draft}=compareManuscript(sourceRaw,draftRaw,diagram,key,language);
    if(draft.meta.sourcePath!==row.source.path||draft.meta.sourceSha256!==row.source.sha256)fail('Draft source pin mismatch');
    const labels=[diagram.title];
    diagram.steps.forEach((step,i)=>{
      labels.push(...step.lines);
      if(step.branch){labels.push(step.branch.outcome==='complete'?'✓':'×',step.branch.exit);if(i<diagram.steps.length-1)labels.push(step.branch.continue);}
    });
    if(diagram.loop)labels.push(diagram.loop.label);
    const texts=labels.map(escape);
    const svgTexts=[...svg.matchAll(/<text\b[^>]*>([^<]*)<\/text>/g)].map(m=>m[1]);
    same(svgTexts,texts,'SVG labels do not match localized diagram source');
    if(!svg.includes(`xml:lang="${language}"`)||!svg.includes(`<desc id="description">${escape(diagram.description)}</desc>`)||!svg.includes(`<title id="title">${escape(diagram.title)}</title>`)||/<(?:script|image|foreignObject)\b|\b(?:href|onload)=/i.test(svg))fail('Invalid or externally dependent diagram SVG');
    if((svg.match(/marker-end="url\(#arrow\)"/g)??[]).length!==diagram.steps.length-1+diagram.steps.filter(s=>s.branch).length+(diagram.loop?1:0))fail('SVG arrows do not match reviewed flow');
  }
  for(const languages of byTopic.values())same([...languages].sort(),[...manifest.languages].sort(),'Incomplete language group');
  return {batchId:manifest.batchId,topics:byTopic.size,preparedEditions:seen.size,byLanguage:Object.fromEntries(manifest.languages.map(l=>[l,manifest.editions.filter(r=>r.language===l).length])),manifestApprovalRecorded:false,publicFilesWritten:0};
}
export async function registeredManifests(base=root){
  const canonical=await realpath(base),path=resolve(canonical,'.pipeline/technical-translations/batches.json');
  if(await realpath(path)!==path)fail('Technical registry must not be a symlink');
  const registry=JSON.parse(await readFile(path,'utf8'));
  if(registry.schemaVersion!==1||!Array.isArray(registry.manifests)||!registry.manifests.length||new Set(registry.manifests).size!==registry.manifests.length||registry.manifests.some(p=>typeof p!=='string'||!/^\.pipeline\/technical-translations\/batch-[0-9]+\/manifest\.json$/.test(p)))fail('Invalid technical batch registry');
  return registry.manifests;
}
export async function inspectAllTechnicalTranslations(base=root){
  const manifests=await registeredManifests(base),batches=[],seen=new Set(),topics=new Set(),ids=new Set();
  for(const path of manifests){
    const summary=await inspectTechnicalTranslations(base,path),manifest=JSON.parse(await readFile(resolve(base,path),'utf8'));
    if(ids.has(manifest.batchId))fail('Duplicate technical batch ID');ids.add(manifest.batchId);
    for(const row of manifest.editions){if(seen.has(row.key))fail('Duplicate edition across technical batches');seen.add(row.key);topics.add(row.translationKey);}
    batches.push({...summary,manifest:path});
  }
  return {batches,topics:topics.size,preparedEditions:seen.size,manifestApprovalRecorded:false,publicFilesWritten:0};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  inspectAllTechnicalTranslations().then(r=>console.log(JSON.stringify(r,null,2))).catch(error=>{console.error(error.message);process.exitCode=1;});
}
