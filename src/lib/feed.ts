import type { Language } from './content';
import type { DigestData } from './digest-schema';
import type { RenewalData } from './renewal-schema';
const xml = (value: string) => value.replace(/[<>&"']/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[c]!);
interface FeedEntry { title: string; url: string; description: string; publishedAt: Date; updatedAt?: Date; digest?: {data: DigestData}; renewal?: {data:RenewalData}; }
export function renderFeed(posts: FeedEntry[], lang: Language, site: URL, name: string) {
  const escapeHtml = xml;
  const home = new URL(`/${lang}/`,site).href;
  const latest = posts.reduce((date,post)=>Math.max(date,(post.updatedAt || post.publishedAt).getTime()),0);
  const items = posts.map(post => {
    const renewed=post.renewal?.data;
    const archiveDescription=renewed ? `${lang==='en'?'Historical news':'과거 뉴스'} · ${renewed.archiveDate}\n`+[...renewed.editions[lang].claims,...renewed.editions[lang].followUp].map(c=>c.text).join('\n') : undefined;
    const description = archiveDescription || (post.digest ? post.digest.data.articles.map((article,index)=>`${index+1}. ${article.editions[lang].title}\n${article.editions[lang].summary}`).join('\n\n') : post.description);
    const content = renewed ? `<section><h2>${escapeHtml(renewed.editions[lang].title)}</h2><p>${escapeHtml(archiveDescription!)}</p><p>${escapeHtml(renewed.reviewFocus[lang])}</p><a href="${escapeHtml(renewed.url)}">${lang==='en'?'Read source':'원문 읽기'}</a></section>` : post.digest ? post.digest.data.articles.map((article,index)=>`<section><h2>${index+1}. ${escapeHtml(article.editions[lang].title)}</h2><p>${escapeHtml(article.editions[lang].summary)}</p><p><a href="${escapeHtml(article.url)}">${lang==='en'?'Read source':'원문 읽기'}</a></p></section>`).join('') : undefined;
    return `<item><title>${xml(post.title)}</title><link>${new URL(post.url,site)}</link><guid isPermaLink="true">${new URL(post.url,site)}</guid><description>${xml(description)}</description>${content ? `<content:encoded>${xml(content)}</content:encoded>` : ''}<pubDate>${post.publishedAt.toUTCString()}</pubDate><atom:updated>${(post.updatedAt || post.publishedAt).toISOString()}</atom:updated></item>`;
  }).join('');
  return `<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>${xml(name)} (${lang})</title><link>${home}</link><description>${xml(name)}</description><language>${lang}</language><atom:link href="${home}feed.xml" rel="self" type="application/rss+xml"/>${latest ? `<lastBuildDate>${new Date(latest).toUTCString()}</lastBuildDate>` : ''}${items}</channel></rss>`;
}
