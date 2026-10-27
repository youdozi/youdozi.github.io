import type {Language} from './content';

export const authorId='https://youdozi.github.io/#author';
export const profileUpdatedAt='2026-10-27T11:17:02.644Z';
export const profileLanguages=['en','ko'] as const;
export function authorPath(lang:Language){return `/${lang==='ko'?'ko':'en'}/about/`;}
export function authorData(lang:Language){return {'@type':'Person','@id':authorId,name:'youdozi',url:'https://youdozi.github.io'+authorPath(lang),sameAs:['https://github.com/youdozi']};}
export const profileAlternates=profileLanguages.map(language=>({language,url:authorPath(language)}));
export const profileCopy={
  en:{label:'About',title:'About youdozi',description:'Meet the maintainer of youdozi’s memory and learn how its technical guides, development news and translations are prepared.',
    intro:'youdozi maintains this blog and its public GitHub repository. The site brings together Java, Spring and shell guides, development news and multilingual editions.',
    workTitle:'What you can read here',work:'Technical guides focus on a concrete problem, with code, flow diagrams and the environment used for a reproduction. News articles link to their sources and distinguish the original announcement from later developments. The learning guides connect related articles in a reading order.',
    processTitle:'How articles are prepared',process:'AI tools assist with drafting, revision and translation. New article candidates are prepared as draft pull requests and published after approval. Sources and example checks support the text; they do not establish that every statement or production environment has been verified.',
    limitsTitle:'Versions and corrections',limits:'Read each article’s version, date and stated limits before reusing an example. A recorded old runtime is not a recommendation for a new deployment. When an article is revised, its original publication date remains separate from its modification date.',
    corrections:'To report an error, use the GitHub discussion below the article and include its URL, the relevant passage and a source or reproduction when available.',
    github:'GitHub profile',repository:'Blog repository',guides:'Browse the learning guides',home:'Home'},
  ko:{label:'소개',title:'youdozi 소개',description:'youdozi’s memory 운영자와 기술 가이드·개발 뉴스·다국어 글의 작성 및 수정 원칙을 소개합니다.',
    intro:'youdozi는 이 블로그와 공개 GitHub 저장소를 관리합니다. Java·Spring·셸 기술 가이드, 개발 뉴스와 다국어 글을 모아 제공합니다.',
    workTitle:'이곳에서 읽을 수 있는 글',work:'기술 가이드는 구체적인 문제를 중심으로 코드·흐름도·재현 환경을 설명합니다. 뉴스는 출처를 연결하고 최초 발표와 이후 상황을 구분합니다. 학습 안내에서는 관련 글을 읽는 순서로 연결합니다.',
    processTitle:'글을 준비하는 방법',process:'초안 작성·퇴고·번역에 AI 도구를 활용합니다. 새 글 후보는 검토용 Draft PR로 준비하고 승인 후 게시합니다. 출처 대조와 예제 검사는 본문을 뒷받침하지만 모든 문장이나 운영 환경이 검증됐다는 뜻은 아닙니다.',
    limitsTitle:'버전과 내용 수정',limits:'예제를 적용하기 전에 글의 버전·날짜·확인 범위를 읽어주세요. 과거 재현 환경은 신규 운영 환경의 권장 버전을 뜻하지 않습니다. 글을 수정할 때는 최초 게시일과 수정일을 구분합니다.',
    corrections:'오류를 발견했다면 글 아래 GitHub 댓글에 해당 URL·문장과 가능한 경우 출처나 재현 방법을 남겨주세요.',
    github:'GitHub 프로필',repository:'블로그 저장소',guides:'학습 안내 읽기',home:'홈'},
};
export function profileStructuredData(lang:'en'|'ko'){
  const url='https://youdozi.github.io'+authorPath(lang);const copy=profileCopy[lang];
  return [
    {'@context':'https://schema.org','@type':'ProfilePage','@id':url+'#profile',url,name:copy.title,description:copy.description,inLanguage:lang,dateModified:profileUpdatedAt,mainEntity:authorData(lang)},
    {'@context':'https://schema.org','@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:copy.home,item:`https://youdozi.github.io/${lang}/`},{'@type':'ListItem',position:2,name:copy.label,item:url}]},
  ];
}
