import type {Entry,Language} from './content';
export const articleUi:Record<Language,{toc:string;updated:string}>={
  en:{toc:'On this page',updated:'Updated'},ko:{toc:'이 글의 목차',updated:'수정일'},
  'zh-CN':{toc:'本文目录',updated:'更新日期'},ja:{toc:'この記事の目次',updated:'更新日'},
  de:{toc:'Auf dieser Seite',updated:'Aktualisiert'},fr:{toc:'Sur cette page',updated:'Mis à jour'},
  ru:{toc:'На этой странице',updated:'Обновлено'},es:{toc:'En esta página',updated:'Actualizado'},
};
export type ArticleHeading={depth:number;slug:string;text:string};
export function articleSections(kind:Entry['kind'],headings:ArticleHeading[]=[]){
  if(kind!=='post')return [];
  const seen=new Set<string>();
  const sections=headings.filter(h=>{
    if(h.depth!==2||!h.slug||!h.text.trim()||seen.has(h.slug))return false;
    seen.add(h.slug);return true;
  });
  return sections.length>=4?sections:[];
}
export function visibleModified(entry:Pick<Entry,'publishedAt'|'updatedAt'>){
  return entry.updatedAt&&entry.updatedAt.getTime()>entry.publishedAt.getTime()?entry.updatedAt:undefined;
}
