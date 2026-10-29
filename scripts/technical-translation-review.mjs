#!/usr/bin/env node
/** Private offline rendering for the technical pilot. No approval or publishing actions. */
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {parseArgs} from 'node:util';
import {createHash} from 'node:crypto';
import {parse} from 'yaml';
import {createSatteriMarkdownProcessor} from '@astrojs/markdown-satteri';
import {inspectTechnicalTranslations} from './check-technical-translations.mjs';
import {savePacket,privateDestination} from './translation-review-packet.mjs';

const root=resolve(import.meta.dirname,'..');
const {values}=parseArgs({options:{output:{type:'string'}}});
const trees=execFileSync('git',['worktree','list','--porcelain','-z'],{cwd:root,encoding:'utf8'}).split('\0').filter(s=>s.startsWith('worktree ')).map(s=>s.slice(9));
if(values.output)await privateDestination(values.output,trees);
const result=await inspectTechnicalTranslations();
if(!values.output){console.log(JSON.stringify(result,null,2));process.exit(0);}
const manifestPath='.pipeline/technical-translations/batch-050/manifest.json';
const rawManifest=await readFile(resolve(root,manifestPath),'utf8');
const manifest=JSON.parse(rawManifest);
const processor=await createSatteriMarkdownProcessor({syntaxHighlight:false});
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
async function render(path,source=false){
  const raw=await readFile(resolve(root,path),'utf8');
  const [,meta,body]=raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  const data=parse(meta);
  const image=[...body.matchAll(/!\[[^\]\n]*\]\(([^)]+)\)/g)][0]?.[1];
  const asset=source?resolve(root,'public',image.slice(1)):resolve(root,dirname(path),image);
  const svg=await readFile(asset);
  const markdown=body.replace(`](${image})`,'](data:image/svg+xml;base64,'+svg.toString('base64')+')').replaceAll('](/en/','](https://youdozi.github.io/en/');
  const html=(await processor.render(markdown)).code;
  return `<section lang="${escape(data.language)}"><h3>${escape(data.title)}</h3><p class="description">${escape(data.description)}</p>${html}</section>`;
}
const sections=[];
for(const row of manifest.editions){sections.push(`<details open><summary>${escape(row.key)}</summary><div class="pair">${await render(row.source.path,true)}${await render(row.draft.path)}</div></details>`);}
const sha=createHash('sha256').update(rawManifest).digest('hex');
const html=`<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>기술 글 12편 번역 대조</title><style>*{box-sizing:border-box}body{font:16px/1.7 system-ui,sans-serif;margin:24px;color:#202923;background:#f6f6f0}main{max-width:1400px;margin:auto}.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px}section{min-width:0;padding:20px;background:white;overflow-wrap:anywhere}img{max-width:100%;height:auto;display:block}pre{overflow-x:auto;background:#f6f6f0;padding:12px}table{width:100%;border-collapse:collapse}th,td{border:1px solid #bbb;padding:5px}details{margin:24px 0}summary{cursor:pointer;font-weight:bold}code{font-size:.9em}.version{font-size:12px;overflow-wrap:anywhere}@media(max-width:800px){body{margin:12px}.pair{grid-template-columns:minmax(0,1fr)}section{padding:12px}}</style><main><h1>기술 글 번역 12편 대조</h1><p>왼쪽은 영어 기준문, 오른쪽은 대상 언어 초안입니다. 이 파일의 열람은 게시 승인이 아닙니다. 원문의 실행 확인 문장은 원문 기록을 번역한 것이며 이번에 다시 실행했다는 뜻이 아닙니다.</p><p class="version">고정 원고 목록 SHA-256: ${sha} · source/draft/SVG hashes validated · AI 자체 대조, 독립 검토 없음</p>${sections.join('')}</main></html>`;
const output=await savePacket(values.output,html,trees);
console.log(JSON.stringify({...result,output,manifestSha256:sha},null,2));
