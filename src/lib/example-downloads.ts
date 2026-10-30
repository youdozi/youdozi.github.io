import catalog from '../../content/examples/downloads.json' with {type:'json'};
import type {Entry} from './content';

/** Downloads belong only to the native canonical article editions they contain. */
export function exampleDownload(entry:Entry):string|undefined {
  const {language,translationKey:key}=entry;
  if(!['en','ko'].includes(language)||entry.kind!=='post'||entry.reviewStatus!=='revised'||
     entry.publishedAt.getTime()>Date.now()||entry.url!==`/${language}/posts/${key}/`||
     !catalog.examples.some(example=>example.key===key))return;
  return `/assets/examples/${key}-${language}.zip`;
}
