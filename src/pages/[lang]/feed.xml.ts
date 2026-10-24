import { entries, languages, type Language, SITE } from '../../lib/content';
export function getStaticPaths() { return languages.map(lang => ({ params: { lang } })); }
const xml = (value: string) => value.replace(/[<>&"']/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[c]!);
export async function GET({ params, site }: { params: { lang: Language }; site: URL }) {
  const posts = (await entries()).filter(e => e.language === params.lang).slice(0,30);
  const url = new URL(`/${params.lang}/`, site).href;
  return new Response(`<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>${xml(SITE)} (${params.lang})</title><link>${url}</link><description>${xml(SITE)}</description><language>${params.lang}</language><atom:link href="${url}feed.xml" rel="self" type="application/rss+xml"/>${posts.map(p => `<item><title>${xml(p.title)}</title><link>${new URL(p.url,site)}</link><guid isPermaLink="true">${new URL(p.url,site)}</guid><description>${xml(p.description)}</description><pubDate>${p.publishedAt.toUTCString()}</pubDate></item>`).join('')}</channel></rss>`, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
