import type {Entry} from './content';
import {guideLocales} from './guide-locales.ts';
import {technicalGuides} from './technical-guides.ts';

const nativeLearningPathCopy = {
  en: {label:'Learning path',heading:'Continue reading',previous:'Previous article',next:'Next article'},
  ko: {label:'학습 경로',heading:'이어서 읽기',previous:'이전 글',next:'다음 글'},
};
export const learningPathCopy = {...nativeLearningPathCopy,...Object.fromEntries(Object.entries(guideLocales).map(([lang,copy])=>[lang,copy.learning]))} as Record<Entry['language'],typeof nativeLearningPathCopy.en>;
export type LearningStep = Pick<Entry,'url'|'title'>;
export type ArticleLearningPath = {
  guide: {url:string;label:string}; position:number; total:number;
  previous?:LearningStep; next?:LearningStep;
};

export function articleLearningPath(entry:Entry,all:Entry[]):ArticleLearningPath|undefined {
  if(entry.kind!=='post'||entry.reviewStatus==='example')return;
  // Only the explicitly curated sections establish a reading sequence. Extras
  // and related-entry scores must not become implied prerequisites or lessons.
  for(const guide of technicalGuides(entry.language,all)){
    const steps=guide.sections.flatMap(section=>section.entries);
    const index=steps.findIndex(step=>step.url===entry.url);
    if(index<0||steps.length<2)continue;
    const step=(item:Entry|undefined):LearningStep|undefined=>item?{url:item.url,title:item.title}:undefined;
    return {guide:{url:guide.url,label:guide.label},position:index+1,total:steps.length,
      previous:step(steps[index-1]),next:step(steps[index+1])};
  }
}
