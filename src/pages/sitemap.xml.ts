import { entries, alternateLinks, publishedLanguages } from '../lib/content';
import { algorithmCategoryAlternates, algorithmGuide } from '../lib/algorithm-guide';
const escape = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
export async function GET({ site }: { site: URL }) {
  const all = await entries();
  const guideAlternates = algorithmCategoryAlternates(all);
  const guides = guideAlternates.map(a => {
    const guide = algorithmGuide(a.language, all)!;
    return `<url><loc>${new URL(a.url, site)}</loc><lastmod>${guide.updatedAt.toISOString()}</lastmod>${guideAlternates.map(other => `<xhtml:link rel="alternate" hreflang="${other.language}" href="${new URL(other.url,site)}"/>`).join('')}${guideAlternates.some(other => other.language === 'en') ? `<xhtml:link rel="alternate" hreflang="x-default" href="${new URL('/en/categories/coding-test/', site)}"/>` : ''}</url>`;
  }).join('');
  const staticUrls = (await publishedLanguages()).flatMap(lang => ['', 'posts/', 'digest/', 'categories/', 'tags/']
    .filter(section => !section || all.some(e => e.language === lang && (section === 'digest/' ? e.kind === 'digest' : section === 'posts/' ? e.kind === 'post' : section === 'tags/' ? e.tags.some(tag => tag !== 'archive-renewal') : true)))
    .map(section => `/${lang}/${section}`));
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${staticUrls.map(url => `<url><loc>${new URL(url,site)}</loc></url>`).join('')}${guides}${all.map(e => `<url><loc>${escape(new URL(e.url,site).href)}</loc><lastmod>${(e.updatedAt || e.publishedAt).toISOString()}</lastmod>${alternateLinks(e,all).map(a => `<xhtml:link rel="alternate" hreflang="${a.language}" href="${escape(new URL(a.url,site).href)}"/>`).join('')}${all.some(other => other.translationKey === e.translationKey && other.language === 'en') ? `<xhtml:link rel="alternate" hreflang="x-default" href="${escape(new URL(all.find(other => other.translationKey === e.translationKey && other.language === 'en')!.url,site).href)}"/>` : ''}</url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
