import type {Entry} from './content';
import pilot from '../../content/seo/answer-pilot.json' with {type:'json'};

/** Cite only pilot evidence actually linked in the reader-visible introduction. */
export function answerCitations(entry:Entry):string[] {
  if(entry.kind!=='post'||(entry.language!=='en'&&entry.language!=='ko')||entry.reviewStatus==='example')return [];
  const article=pilot.articles.find(article=>article.key===entry.translationKey);
  if(!article||!entry.post?.body)return [];
  const introduction=entry.post.body.trim().split(/\n\s*\n/,1)[0];
  if(introduction.startsWith('```'))return [];
  const prose=introduction.replace(/`[^`\n]*`/g,'').replace(/<!--[\s\S]*?-->/g,'');
  return [...new Set(article.evidence.filter(url=>prose.includes(`](${url})`)))];
}
