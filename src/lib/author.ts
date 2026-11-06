import type {Language} from './content';

export const authorId='https://youdozi.github.io/#author';
export const profileUpdatedAt='2026-11-06T04:20:30.442907+00:00';
export const profileLanguages=['en','ko'] as const;
export function authorPath(lang:Language){return `/${lang==='ko'?'ko':'en'}/about/`;}
export function authorData(lang:Language){return {'@type':'Person','@id':authorId,name:'youdozi',url:'https://youdozi.github.io'+authorPath(lang),sameAs:['https://github.com/youdozi']};}
export const profileAlternates=profileLanguages.map(language=>({language,url:authorPath(language)}));
export const profileCopy={
  en:{label:'About',title:'About youdozi',description:'Meet the maintainer of youdozi’s memory and explore Java, Spring and shell guides, development news and multilingual articles.',
    intro:'youdozi maintains this blog and its public GitHub repository. The site brings together Java, Spring and shell guides, development news and multilingual editions.',
    workTitle:'What you can read here',work:'Technical guides focus on a concrete problem, with code, flow diagrams and the environment used for a reproduction. News articles link to their sources and distinguish the original announcement from later developments. The learning guides connect related articles in a reading order.',
    github:'GitHub profile',repository:'Blog repository',guides:'Browse the learning guides',home:'Home'},
  ko:{label:'소개',title:'youdozi 소개',description:'youdozi’s memory 운영자와 Java·Spring·셸 기술 가이드, 개발 뉴스, 다국어 글을 소개합니다.',
    intro:'youdozi는 이 블로그와 공개 GitHub 저장소를 관리합니다. Java·Spring·셸 기술 가이드, 개발 뉴스와 다국어 글을 모아 제공합니다.',
    workTitle:'이곳에서 읽을 수 있는 글',work:'기술 가이드는 구체적인 문제를 중심으로 코드·흐름도·재현 환경을 설명합니다. 뉴스는 출처를 연결하고 최초 발표와 이후 상황을 구분합니다. 학습 안내에서는 관련 글을 읽는 순서로 연결합니다.',
    github:'GitHub 프로필',repository:'블로그 저장소',guides:'학습 안내 읽기',home:'홈'},
};
export function profileStructuredData(lang:'en'|'ko'){
  const url='https://youdozi.github.io'+authorPath(lang);const copy=profileCopy[lang];
  return [
    {'@context':'https://schema.org','@type':'ProfilePage','@id':url+'#profile',url,name:copy.title,description:copy.description,inLanguage:lang,dateModified:profileUpdatedAt,mainEntity:authorData(lang)},
    {'@context':'https://schema.org','@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:copy.home,item:`https://youdozi.github.io/${lang}/`},{'@type':'ListItem',position:2,name:copy.label,item:url}]},
  ];
}
