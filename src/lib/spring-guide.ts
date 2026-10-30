import type { Entry, Language } from './content';
import type { CategoryGuide } from './category-guide';
import {nativeLanguages,translationLanguages} from './locales.ts';
import {guideLocales,hasLocalizedGuide} from './guide-locales.ts';
import {springGuideLocales,springGuideLocalesUpdatedAt} from './spring-guide-locales.ts';

const groups = [
  {id:'start',keys:['2023-09-07-springboot-initializer','2023-09-13-springboot-history','2023-09-10-springboot-intellij-import','2023-09-15-springboot-intellij-lombok']},
  {id:'data',keys:['2023-09-08-springboot3-migration','2023-09-05-querydsl-no-release','2023-09-09-springboot3-querydsl']},
  {id:'deliver',keys:['2023-09-19-springboot-test-webclient','2021-07-23-multiple-gradle-build']},
] as const;
const copy = {
  en:{label:'Spring Boot guides',title:'Spring Boot Guides: Setup, Persistence, Testing and Packaging',
    description:'Follow working Spring Boot examples from project setup and IDE checks to Jakarta persistence, query comparisons, HTTP tests and frontend packaging.',
    intro:'Start with a reproducible project, then inspect how the build, persistence and HTTP contracts fit together. Use each article’s documented Boot, JDK and Gradle combination; these examples span different release lines.',
    extra:'More Spring Boot articles',home:'Home',categories:'Categories',
    groups:{
      start:{title:'Create and run',description:'Generate the project, distinguish component versions, then verify command-line execution and Lombok before diagnosing IDE recognition.'},
      data:{title:'Persistence and migration',description:'Review Java and Jakarta compatibility, compare representative query predicates, then generate and execute Querydsl Q types.'},
      deliver:{title:'Test and package',description:'Check HTTP response contracts with a local mock server and package separate Vue outputs into an executable JAR.'},
    }},
  ko:{label:'Spring Boot 학습 안내',title:'Spring Boot 학습 안내: 생성·영속성·테스트·패키징',
    description:'프로젝트 생성과 IDE 확인부터 Jakarta 영속성, 쿼리 비교, HTTP 테스트, 프런트엔드 패키징까지 재현 가능한 Spring Boot 예제를 연결합니다.',
    intro:'재현 가능한 프로젝트에서 시작해 빌드·영속성·HTTP 계약을 이어 확인합니다. 예제마다 Boot·JDK·Gradle의 재현 조합을 따르세요. 서로 다른 릴리스 계열의 예제를 함께 다룹니다.',
    extra:'다른 Spring Boot 글',home:'홈',categories:'카테고리',
    groups:{
      start:{title:'프로젝트 생성과 실행',description:'프로젝트를 생성하고 구성요소의 버전을 구분합니다. 명령행 실행과 Lombok 컴파일을 확인한 뒤 IDE 인식 문제를 살펴봅니다.'},
      data:{title:'영속성과 이관',description:'Java·Jakarta 호환성을 확인하고 대표 쿼리 조건을 비교합니다. 이후 Q 타입을 생성해 실제 조회를 실행합니다.'},
      deliver:{title:'테스트와 패키징',description:'로컬 모의 서버로 HTTP 응답 계약을 확인하고, 별도로 빌드한 Vue 앱의 결과를 실행 JAR에 패키징합니다.'},
    }},
};
function eligible(lang:Language, all:Entry[]) {
  return all.filter(e=>e.language===lang && e.kind==='post' && e.categories.includes('springboot') && e.reviewStatus!=='example' && e.publishedAt.getTime()<=Date.now());
}
export function springCategoryLabel(lang:Language) {return hasLocalizedGuide(lang)?springGuideLocales[lang].label:copy[lang].label;}
export function springCategoryAlternates(all:Entry[]) {
  return ([...nativeLanguages,...translationLanguages]).filter(lang=>eligible(lang,all).length>0).map(language=>({language,url:`/${language}/categories/springboot/`}));
}
export function springGuide(lang:Language,all:Entry[]):CategoryGuide|undefined {
  const localized=hasLocalizedGuide(lang);
  const definition=localized?{...springGuideLocales[lang],...guideLocales[lang].common,extra:springGuideLocales[lang].extra}:copy[lang];
  const items=eligible(lang,all);if(!items.length)return undefined;
  const byKey=new Map(items.map(e=>[e.translationKey,e]));let position=1;
  const sections=groups.map(group=>{
    const entries=group.keys.flatMap(key=>byKey.has(key)?[byKey.get(key)!]:[]);
    const start=position;position+=entries.length;
    return {id:group.id,...definition.groups[group.id],entries,start};
  }).filter(group=>group.entries.length>0);
  const selected=new Set(sections.flatMap(g=>g.entries.map(e=>e.translationKey)));
  const extras=items.filter(e=>!selected.has(e.translationKey));const ordered=[...sections.flatMap(g=>g.entries),...extras];
  return {...definition,lang,url:`/${lang}/categories/springboot/`,eyebrow:'Spring Boot',listAnchor:'articles',sections,extras,ordered,
    updatedAt:new Date(Math.max(localized?springGuideLocalesUpdatedAt.getTime():Date.parse('2026-10-27T00:00:00Z'),...ordered.map(e=>(e.updatedAt||e.publishedAt).getTime())))};
}
