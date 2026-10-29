import registry from '../../content/seo/core-articles.json' with {type:'json'};
import type {Entry,Language} from './content';

export function coreArticles(lang:Language,all:Entry[]) {
  if(lang!=='en'&&lang!=='ko')return [];
  const eligible=new Map(all.filter(e=>e.language===lang&&e.kind==='post'&&e.reviewStatus!=='example'&&e.publishedAt.getTime()<=Date.now()).map(e=>[e.translationKey,e]));
  return registry.articles.flatMap(({key})=>eligible.has(key)?[eligible.get(key)!]:[]);
}
