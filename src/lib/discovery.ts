import type {Entry,Language} from './content';
import {supportedLanguages} from './locales.ts';
export type DiscoveryEntry = Pick<Entry,'language'|'kind'|'tags'|'categories'|'publishedAt'|'updatedAt'|'url'|'title'|'reviewStatus'>;
export type Section = 'posts'|'digest'|'categories'|'tags';
export const archiveStructureUpdatedAt='2026-10-28T02:00:43Z';
export const archivePath=(lang:Language)=>'/'+lang+'/archive/';
export function availableEntries(all:DiscoveryEntry[],lang:Language) {
  return all.filter(entry=>entry.language===lang&&entry.reviewStatus!=='example');
}
export function hasSection(all:DiscoveryEntry[],lang:Language,section:Section) {
  const entries=availableEntries(all,lang);
  if(section==='posts'||section==='digest')return entries.some(e=>e.kind===(section==='posts'?'post':'digest'));
  return entries.some(e=>e[section].some(value=>value!=='archive-renewal'));
}
export function sectionAlternates(all:DiscoveryEntry[],section:Section) {
  return supportedLanguages.filter(language=>hasSection(all,language,section)).map(language=>({language,url:'/'+language+'/'+section+'/'}));
}
export function archiveAlternates(all:DiscoveryEntry[]) {
  return supportedLanguages.filter(language=>availableEntries(all,language).length>0).map(language=>({language,url:archivePath(language)}));
}
export function archiveEntries(all:DiscoveryEntry[],lang:Language) {
  return availableEntries(all,lang).slice().sort((a,b)=>b.publishedAt.getTime()-a.publishedAt.getTime()||a.url.localeCompare(b.url));
}
export function archiveYears(all:DiscoveryEntry[],lang:Language) {
  const groups=new Map<string,DiscoveryEntry[]>();
  for(const entry of archiveEntries(all,lang)) {
    // Use the same publication-date zone as formatDate.
    const year=new Intl.DateTimeFormat('en',{year:'numeric',timeZone:'Asia/Seoul'}).format(entry.publishedAt);
    if(!groups.has(year))groups.set(year,[]);
    groups.get(year)!.push(entry);
  }
  return [...groups].map(([year,entries])=>({year,entries}));
}
export function archiveModified(all:DiscoveryEntry[],lang:Language) {
  const entries=availableEntries(all,lang);
  return entries.length?new Date(Math.max(Date.parse(archiveStructureUpdatedAt),...entries.map(e=>(e.updatedAt||e.publishedAt).getTime()))).toISOString():undefined;
}
export function archiveStructuredData(all:DiscoveryEntry[],lang:Language,title:string,description:string,site:URL) {
  const entries=archiveEntries(all,lang),url=new URL(archivePath(lang),site).href;
  return [
    {'@context':'https://schema.org','@type':'CollectionPage','@id':url+'#collection',url,name:title,description,inLanguage:lang,dateModified:archiveModified(all,lang),mainEntity:{'@id':url+'#articles'}},
    {'@context':'https://schema.org','@type':'ItemList','@id':url+'#articles',numberOfItems:entries.length,itemListElement:entries.map((e,i)=>({'@type':'ListItem',position:i+1,name:e.title,url:new URL(e.url,site).href}))},
  ];
}
export function recoveryPath(all:DiscoveryEntry[],lang:Language) {
  return availableEntries(all,lang).length?archivePath(lang):'/en/';
}
