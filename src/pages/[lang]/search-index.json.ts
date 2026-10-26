import { entries, publishedLanguages, type NativeLanguage, type Language } from '../../lib/content';
export async function getStaticPaths() { return (await publishedLanguages()).map(lang => ({ params: { lang } })); }
export async function GET({ params }: { params: { lang: Language } }) {
  const data = (await entries()).filter(e => e.language === params.lang).map(e => ({
    title: e.title, url: e.url, tags: e.tags, description: e.description,
    content: e.post?.body?.replace(/<[^>]*>/g, ' ')
      || e.digest?.data.articles.map(a => a.editions[params.lang as NativeLanguage].title + ' ' + a.editions[params.lang as NativeLanguage].summary).join(' ')
      || (e.renewalEdition ? [...e.renewalEdition.claims,...e.renewalEdition.followUp].map(c=>c.text).join(' ')+' '+e.renewalFocus : ''),
  }));
  return Response.json(data);
}
