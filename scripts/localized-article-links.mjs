import {readFile,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {parse} from 'yaml';

async function articleIndex(base,now) {
  const routes=new Map(),editions=new Map();
  for(const directory of ['posts','technical-translations']){
    const root=resolve(base,'src/content',directory);
    for(const file of await readdir(root,{recursive:true})){
      if(!file.endsWith('.md'))continue;
      const raw=await readFile(resolve(root,file),'utf8');
      const front=/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(raw);
      if(!front)throw new Error('Article link index requires frontmatter');
      const data=parse(front[1]);
      if(data.kind!=='post'||data.reviewStatus==='example'||new Date(data.publishedAt)>now)continue;
      if(directory==='technical-translations'&&data.state!=='approved')continue;
      const url=`/${data.language}/posts/${data.routeSlug}/`;
      routes.set(url,data.translationKey);
      editions.set(`${data.language}:${data.translationKey}`,url);
    }
  }
  return {routes,editions};
}

/** Resolve body links against published editions without changing pinned translation sources. */
export function localizedArticleLinks(base=process.cwd(),now=new Date()) {
  let index;
  return ({fileURL})=>{
    const language=fileURL?.pathname.match(/\/src\/content\/(?:posts|technical-translations)\/([^/]+)\//)?.[1];
    if(!language)return;
    return {name:'localized-article-links',element:{filter:['a'],async visit(node,ctx){
      const href=node.properties?.href;
      if(typeof href!=='string'||(!href.startsWith('/')&&!href.startsWith('https://youdozi.github.io/'))||href.startsWith('//'))return;
      const target=new URL(href,'https://youdozi.github.io');
      // A translated heading may have a different ID; keep explicit section links intact.
      if(target.hash||target.origin!=='https://youdozi.github.io')return;
      const {routes,editions}=await (index??=articleIndex(base,now));
      const key=routes.get(target.pathname),local=key&&editions.get(`${language}:${key}`);
      if(local&&local!==target.pathname)ctx.setProperty(node,'href',`${href.startsWith('https:')?target.origin:''}${local}${target.search}`);
    }}};
  };
}
