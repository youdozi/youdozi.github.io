import { entries, languages, type Language } from '../../lib/content';
export function getStaticPaths() { return languages.map(lang => ({ params: { lang } })); }
export async function GET({ params }: { params: { lang: Language } }) {
  const data = (await entries()).filter(e => e.language === params.lang).map(e => ({ title: e.title, url: e.url, tags: e.tags, description: e.description, content: e.post?.body?.replace(/<[^>]*>/g, ' ') || e.digest?.data.articles.map(a => a.editions[params.lang].title + ' ' + a.editions[params.lang].summary).join(' ') || (e.renewal ? [...e.renewal.data.editions[params.lang].claims,...e.renewal.data.editions[params.lang].followUp].map(c=>c.text).join(' ')+' '+e.renewal.data.reviewFocus[params.lang] : '') }));
  return Response.json(data);
}
