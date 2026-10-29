import { entries, publishedLanguages, type NativeLanguage, type Language } from '../../lib/content';
import {searchContent} from '../../lib/search-content';
export async function getStaticPaths() { return (await publishedLanguages()).map(lang => ({ params: { lang } })); }
export async function GET({ params }: { params: { lang: Language } }) {
  const data = (await entries()).filter(e => e.language === params.lang).map(e => ({
    title: e.title, url: e.url, tags: e.tags, description: e.description,
    content: e.post?.body ? searchContent(e.post.body)
      : e.digest?.data.articles.map(a => a.editions[params.lang as NativeLanguage].title + ' ' + a.editions[params.lang as NativeLanguage].claims.map(c=>c.text).join(' ')).join(' ')
      || (e.renewalEdition ? [...e.renewalEdition.claims,...e.renewalEdition.followUp].map(c=>c.text).join(' ') : ''),
  }));
  return Response.json(data);
}
