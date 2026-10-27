import type { Entry, Language } from './content';
import type { CategoryGuide } from './category-guide';
import { algorithmGuide } from './algorithm-guide.ts';
import { springGuide } from './spring-guide.ts';

export const guideTerms = ['coding-test', 'springboot', 'linux', 'jdk', 'util'] as const;
const updatedAt = new Date('2026-10-27T08:19:59.645138+00:00');
export const guideIndexCopy = {
  en: { label: 'Guides', title: 'Technical Learning Guides',
    description: 'Choose a reading path through Java exercises, Spring Boot, shell automation, JDK features and development tools, with code and clearly scoped checks.',
    intro: 'Choose the problem you want to solve. Each path connects available articles with code and recorded checks. Read each article’s environment and limits before reusing an example.',
    home: 'Home', open: 'Explore the guide' },
  ko: { label: '학습 안내', title: '기술 학습 안내',
    description: 'Java 문제 풀이·Spring Boot·셸 자동화·JDK 기능·개발 도구를 읽는 순서로 연결합니다. 코드와 검증 범위를 확인하며 학습하세요.',
    intro: '해결하려는 문제에서 시작하세요. 각 안내는 코드와 확인 범위가 있는 실제 글을 연결합니다. 예제를 적용하기 전에 해당 글의 실행 환경과 한계를 확인하세요.',
    home: '홈', open: '안내 읽기' },
};
const common = {
  en: { extra: 'More articles', home: 'Home', categories: 'Categories' },
  ko: { extra: '다른 글', home: '홈', categories: '카테고리' },
};
const paths = {
  linux: {
    en: {label:'Shell automation guides', title:'Shell Automation Guides: Interpreters, YAML and Release Assets', eyebrow:'Shell automation',
      description:'Choose sh or Bash, validate YAML and numeric versions, then select GitHub release assets with explicit input contracts and local tests.',
      intro:'Check the interpreter first, then validate inputs before selecting or executing a command. The numeric-version example does not implement all SemVer rules, and release metadata does not verify downloaded bytes.',
      groups:[
        {id:'interpreter',title:'Choose an interpreter',description:'Keep POSIX syntax and Bash invocation consistent.',keys:['2023-09-20-linux-shellscript-function-error']},
        {id:'inputs',title:'Validate structured input',description:'Parse YAML without eval and compare dotted numeric versions under explicit bounds.',keys:['2021-07-27-parse-yaml','2023-11-17-linux-shellscript-version-compare']},
        {id:'releases',title:'Select release assets',description:'Check the response and asset selection before treating metadata as a download instruction.',keys:['2023-09-23-linux-shellscript-github-latest']},
      ]},
    ko: {label:'셸 자동화 학습 안내',title:'셸 자동화 학습 안내: 실행기·YAML·릴리스 자산',eyebrow:'셸 자동화',
      description:'sh·Bash 선택부터 YAML·숫자 버전 검증과 GitHub 릴리스 자산 선택까지 입력 조건과 로컬 예제로 이어 확인합니다.',
      intro:'실행기를 먼저 확인하고 명령을 선택하거나 실행하기 전에 입력을 검증합니다. 숫자 버전 예제는 전체 SemVer 규칙을 구현하지 않으며, 릴리스 메타데이터만으로 다운로드한 바이트를 검증할 수는 없습니다.',
      groups:[
        {id:'interpreter',title:'실행기 선택',description:'POSIX 문법과 Bash 실행 방식을 일치시킵니다.',keys:['2023-09-20-linux-shellscript-function-error']},
        {id:'inputs',title:'구조화된 입력 검증',description:'eval 없이 YAML을 읽고 명시한 범위에서 점으로 나눈 숫자 버전을 비교합니다.',keys:['2021-07-27-parse-yaml','2023-11-17-linux-shellscript-version-compare']},
        {id:'releases',title:'릴리스 자산 선택',description:'응답과 자산 선택을 확인한 뒤 다운로드에 사용할 정보를 결정합니다.',keys:['2023-09-23-linux-shellscript-github-latest']},
      ]},
  },
  jdk: {
    en: {label:'JDK feature guides',title:'JDK Guides: Final APIs, Preview History and Binary Checks',eyebrow:'JDK',
      description:'Distinguish final and preview JDK 21 features, understand the String Templates history and inspect JDK binary metadata under each article’s recorded scope.',
      intro:'Separate language/API status from the runtime you actually install. These articles include historical release events and preview material; use each recorded version and do not infer current support from an old release note.',
      groups:[
        {id:'features',title:'Distinguish feature status',description:'Start with final APIs and the boundaries of preview features.',keys:['2023-09-20-jdk-21-release']},
        {id:'preview',title:'Read preview history',description:'Understand String Templates and the standard formatting alternative shown in the article.',keys:['2023-09-23-jdk-21-string-templates']},
        {id:'binaries',title:'Inspect runtime binaries',description:'Keep the historical Temurin delay separate from platform and binary-metadata checks.',keys:['2023-10-10-temurin-jdk21-delay']},
      ]},
    ko: {label:'JDK 기능 학습 안내',title:'JDK 학습 안내: 정식 API·Preview 이력·바이너리 확인',eyebrow:'JDK',
      description:'JDK 21의 정식·Preview 기능을 구분하고 String Templates 이력과 JDK 바이너리 메타데이터를 각 글의 확인 범위에 따라 살펴봅니다.',
      intro:'언어·API의 상태와 실제 설치할 실행기를 구분합니다. 과거 릴리스와 Preview 자료를 포함하므로 기록한 버전을 따르고 오래된 릴리스 글만으로 현재 지원 상태를 판단하지 않습니다.',
      groups:[
        {id:'features',title:'기능의 상태 구분',description:'정식 API와 Preview 기능의 적용 범위부터 확인합니다.',keys:['2023-09-20-jdk-21-release']},
        {id:'preview',title:'Preview 이력 확인',description:'String Templates 이력과 본문이 제공하는 표준 포맷팅 대안을 살펴봅니다.',keys:['2023-09-23-jdk-21-string-templates']},
        {id:'binaries',title:'실행기 바이너리 확인',description:'과거 Temurin 출시 지연과 플랫폼·바이너리 메타데이터 검사를 구분합니다.',keys:['2023-10-10-temurin-jdk21-delay']},
      ]},
  },
  util: {
    en: {label:'Development tool guides',title:'Development Tool Guides: HTTP Checks, Code Search and Diagrams',eyebrow:'Development tools',
      description:'Probe local HTTP responses, narrow a code search and keep editable draw.io sources with shared diagrams through small practical examples.',
      intro:'Use a small example to check a response, locate an implementation or preserve an editable diagram. Local fixtures and file-structure checks have narrower scope than a live service or a full editor round trip.',
      groups:[
        {id:'responses',title:'Check a response',description:'Use a local Python server to distinguish HTTP response cases.',keys:['2021-07-20-http-status-test']},
        {id:'search',title:'Find the implementation',description:'Narrow repository/path searches and verify a known checkout with Git.',keys:['2021-08-06-search-github']},
        {id:'diagrams',title:'Keep diagrams editable',description:'Store draw.io source and inspect the XML relationships separately from a shared image.',keys:['2021-07-23-app-diagrams.net']},
      ]},
    ko: {label:'개발 도구 학습 안내',title:'개발 도구 학습 안내: HTTP 검사·코드 검색·다이어그램',eyebrow:'개발 도구',
      description:'작은 예제로 로컬 HTTP 응답을 확인하고 코드 검색 범위를 좁힙니다. 공유 이미지와 함께 편집 가능한 draw.io 원본을 관리합니다.',
      intro:'응답을 확인하고 구현을 찾거나 편집 가능한 다이어그램을 남기는 작은 예제에서 시작합니다. 로컬 모의 응답과 파일 구조 검사는 실제 서비스나 편집기 왕복 검사보다 범위가 좁습니다.',
      groups:[
        {id:'responses',title:'응답 확인',description:'로컬 Python 서버에서 HTTP 응답 사례를 구분합니다.',keys:['2021-07-20-http-status-test']},
        {id:'search',title:'구현 찾기',description:'저장소·경로로 검색을 좁히고 알고 있는 체크아웃을 Git으로 확인합니다.',keys:['2021-08-06-search-github']},
        {id:'diagrams',title:'편집 가능한 그림 보관',description:'draw.io 원본을 보관하고 공유 이미지와 별도로 XML 관계를 확인합니다.',keys:['2021-07-23-app-diagrams.net']},
      ]},
  },
};
export function categoryGuide(term:string,lang:Language,all:Entry[]):CategoryGuide|undefined {
  if(term==='coding-test')return algorithmGuide(lang,all);
  if(term==='springboot')return springGuide(lang,all);
  if((lang!=='en'&&lang!=='ko')||!Object.hasOwn(paths,term))return undefined;
  const definition=paths[term as keyof typeof paths][lang];
  const items=all.filter(e=>e.language===lang&&e.kind==='post'&&e.categories.includes(term)&&e.reviewStatus!=='example'&&e.publishedAt.getTime()<=Date.now());
  if(!items.length)return undefined;
  const byKey=new Map(items.map(e=>[e.translationKey,e]));let position=1;
  const sections=definition.groups.map(group=>{
    const entries=group.keys.flatMap(key=>byKey.has(key)?[byKey.get(key)!]:[]);const start=position;position+=entries.length;
    return {id:group.id,title:group.title,description:group.description,entries,start};
  }).filter(group=>group.entries.length>0);
  const selected=new Set(sections.flatMap(s=>s.entries.map(e=>e.translationKey)));
  const extras=items.filter(e=>!selected.has(e.translationKey));const ordered=[...sections.flatMap(s=>s.entries),...extras];
  return {...definition,...common[lang],lang,url:`/${lang}/categories/${term}/`,listAnchor:'articles',sections,extras,ordered,
    updatedAt:new Date(Math.max(updatedAt.getTime(),...ordered.map(e=>(e.updatedAt||e.publishedAt).getTime())))};
}
export function categoryGuideAlternates(term:string,all:Entry[]) {
  return (['en','ko'] as const).flatMap(language=>{const guide=categoryGuide(term,language,all);return guide?[{language,url:guide.url}]:[];});
}
export function technicalGuides(lang:Language,all:Entry[]) {
  return guideTerms.flatMap(term=>{const guide=categoryGuide(term,lang,all);return guide?[guide]:[];});
}
export function guideIndexAlternates(all:Entry[]) {
  return (['en','ko'] as const).filter(language=>technicalGuides(language,all).length>0).map(language=>({language,url:`/${language}/guides/`}));
}
export function guideIndexStructuredData(lang:'en'|'ko',guides:CategoryGuide[],site:URL) {
  const copy=guideIndexCopy[lang];const url=new URL(`/${lang}/guides/`,site).href;
  const lastmod=new Date(Math.max(updatedAt.getTime(),...guides.map(g=>g.updatedAt.getTime()))).toISOString();
  return [
    {'@context':'https://schema.org','@type':'CollectionPage','@id':url+'#collection',url,name:copy.title,description:copy.description,inLanguage:lang,dateModified:lastmod,mainEntity:{'@id':url+'#paths'}},
    {'@context':'https://schema.org','@type':'ItemList','@id':url+'#paths',numberOfItems:guides.length,itemListElement:guides.map((g,i)=>({'@type':'ListItem',position:i+1,name:g.title,url:new URL(g.url,site).href}))},
    {'@context':'https://schema.org','@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:copy.home,item:new URL(`/${lang}/`,site).href},{'@type':'ListItem',position:2,name:copy.label,item:url}]},
  ];
}
