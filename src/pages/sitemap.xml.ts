import { entries, alternateLinks, publishedLanguages } from '../lib/content';
import {hasSection,archiveAlternates,archiveModified} from '../lib/discovery';
import {profileAlternates,profileUpdatedAt} from '../lib/author';
import {guideTerms,categoryGuideAlternates,categoryGuide,guideIndexAlternates,technicalGuides,guideIndexStructuredData} from '../lib/technical-guides';
const escape = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
export async function GET({ site }: { site: URL }) {
  const all = await entries();
  const guideLinks=(url:string,lastmod:string,alternates:{language:string;url:string}[])=>{
    const english=alternates.find(a=>a.language==='en');
    return `<url><loc>${escape(new URL(url,site).href)}</loc><lastmod>${lastmod}</lastmod>${alternates.map(a=>`<xhtml:link rel="alternate" hreflang="${a.language}" href="${escape(new URL(a.url,site).href)}"/>`).join('')}${english?`<xhtml:link rel="alternate" hreflang="x-default" href="${escape(new URL(english.url,site).href)}"/>`:''}</url>`;
  };
  const guides=guideTerms.map(term=>{
    const alternates=categoryGuideAlternates(term,all);
    return alternates.map(a=>guideLinks(a.url,categoryGuide(term,a.language,all)!.updatedAt.toISOString(),alternates)).join('');
  }).join('');
  const indexAlternates=guideIndexAlternates(all);
  const guideIndexes=indexAlternates.map(a=>{
    const data=guideIndexStructuredData(a.language,technicalGuides(a.language,all),site);
    return guideLinks(a.url,data[0].dateModified!,indexAlternates);
  }).join('');
  const staticUrls = (await publishedLanguages()).flatMap(lang => ['', 'posts/', 'digest/', 'categories/', 'tags/']
    .filter(section => !section || hasSection(all,lang,section.slice(0,-1) as 'posts'|'digest'|'categories'|'tags'))
    .map(section => `/${lang}/${section}`));
  const archiveLinks=archiveAlternates(all);
  const archives=archiveLinks.map(a=>guideLinks(a.url,archiveModified(all,a.language)!,archiveLinks)).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${staticUrls.map(url => `<url><loc>${new URL(url,site)}</loc></url>`).join('')}${archives}${guides}${guideIndexes}${profileAlternates.map(a=>guideLinks(a.url,profileUpdatedAt,profileAlternates)).join('')}${all.map(e => `<url><loc>${escape(new URL(e.url,site).href)}</loc><lastmod>${(e.updatedAt || e.publishedAt).toISOString()}</lastmod>${alternateLinks(e,all).map(a => `<xhtml:link rel="alternate" hreflang="${a.language}" href="${escape(new URL(a.url,site).href)}"/>`).join('')}${all.some(other => other.translationKey === e.translationKey && other.language === 'en') ? `<xhtml:link rel="alternate" hreflang="x-default" href="${escape(new URL(all.find(other => other.translationKey === e.translationKey && other.language === 'en')!.url,site).href)}"/>` : ''}</url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
