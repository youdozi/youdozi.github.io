import { entries, languages, type Language, SITE } from '../../lib/content';
import { renderFeed } from '../../lib/feed';
export function getStaticPaths() { return languages.map(lang => ({ params: { lang } })); }
export async function GET({ params, site }: { params: { lang: Language }; site: URL }) {
  const posts = (await entries()).filter(e => e.language === params.lang)
    .sort((a,b)=>(b.updatedAt || b.publishedAt).getTime()-(a.updatedAt || a.publishedAt).getTime()).slice(0,30);
  return new Response(renderFeed(posts,params.lang,site,SITE),{ headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
