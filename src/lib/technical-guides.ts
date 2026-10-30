import type { Entry, Language } from './content';
import {nativeLanguages,translationLanguages} from './locales.ts';
import {guideLocales,hasLocalizedGuide,localizedGuidesUpdatedAt} from './guide-locales.ts';
import {toolGuideLocales,toolGuidesUpdatedAt} from './tool-guide-locales.ts';
import {remainingGuideLocales,remainingGuideLocalesUpdatedAt} from './remaining-guide-locales.ts';
import type { CategoryGuide } from './category-guide';
import { algorithmGuide } from './algorithm-guide.ts';
import { springGuide } from './spring-guide.ts';

export const guideTerms = ['coding-test', 'springboot', 'linux', 'jdk', 'util', 'automation', 'jenkins', 'jekyll', 'security'] as const;
const updatedAt = new Date('2026-10-30T10:10:46.396668+00:00');
const nativeGuideIndexCopy = {
  en: { label: 'Guides', title: 'Technical Learning Guides',
    description: 'Choose a reading path through Java exercises, Spring Boot, shell automation, JDK features, development tools, reviewed publishing, Jenkins recovery, legacy Ruby diagnostics and runtime security, with code and scoped checks.',
    intro: 'Choose the problem you want to solve. Each path connects available articles with code and recorded checks. Read each article’s environment and limits before reusing an example.',
    home: 'Home', open: 'Explore the guide' },
  ko: { label: '학습 안내', title: '기술 학습 안내',
    description: 'Java 문제 풀이·Spring Boot·셸 자동화·JDK·개발 도구·검토 후 게시·Jenkins 복구·과거 Ruby 환경 진단·런타임 보안을 읽는 순서로 연결합니다. 코드와 검증 범위를 확인하며 학습하세요.',
    intro: '해결하려는 문제에서 시작하세요. 각 안내는 코드와 확인 범위가 있는 실제 글을 연결합니다. 예제를 적용하기 전에 해당 글의 실행 환경과 한계를 확인하세요.',
    home: '홈', open: '안내 읽기' },
};
export const guideIndexCopy = {...nativeGuideIndexCopy,...Object.fromEntries(Object.entries(guideLocales).map(([lang,copy])=>[lang,copy.index]))} as Record<Language,typeof nativeGuideIndexCopy.en>;
const common = {
  en: { extra: 'More articles', home: 'Home', categories: 'Categories' },
  ko: { extra: '다른 글', home: '홈', categories: '카테고리' },
};
const crossCategoryKeys: Partial<Record<string, readonly string[]>> = {
  jekyll: ['2026-04-07-ruby-rbenv-jekyll-build-troubleshooting'],
};
const paths = {
  security: {
    en: {label:'Runtime security guides',title:'Runtime Security Guides: PHP, Node.js, GitLab and JVM Trust',eyebrow:'Runtime patching',
      description:'Check PHP, Node.js and GitLab upgrade evidence, distinguish supplier fixes from version labels, and inspect JVM certificate trust.',
      intro:'Follow each product’s advisory and the runtime actually serving the workload. Local examples compare declared versions and collect runtime evidence; they do not discover services, reproduce exploits or certify patch status.',
      groups:[
        {id:'php',title:'PHP engine and web workers',description:'Separate the PHP engine fixes, vendor backports, session follow-up and Windows package rebuild.',keys:['2026-10-30-php2shell-runtime-patching']},
        {id:'node',title:'Brotli paths and Node.js rollout',description:'Trace untrusted decompression and connect runtime fix evidence to every worker and replica.',keys:['2026-10-30-node2shell-brotli-runtime-patching']},
        {id:'gitlab',title:'GitLab server upgrade',description:'Compare the RCE release threshold and follow upgrade stops before verifying adoption.',keys:['2026-10-30-gitlab2shell-cve-2026-110264']},
        {id:'trust',title:'JVM certificate trust',description:'Distinguish supplier distrust guidance from the CA inventory of a newly started JVM.',keys:['2026-10-30-jdk-emudhra-truststore']},
      ]},
    ko: {label:'런타임 보안 학습 안내',title:'런타임 보안 학습 안내: PHP·Node.js·GitLab·JVM 신뢰',eyebrow:'런타임 패치',
      description:'PHP·Node.js·GitLab의 업그레이드 증거와 버전 이름표를 구분하고 JVM 인증서 신뢰 설정을 확인합니다.',
      intro:'제품별 공지와 실제 작업을 처리하는 런타임을 함께 확인합니다. 로컬 예제는 선언된 버전 비교와 런타임 증거 수집을 돕습니다. 서비스 탐색·악용 재현·패치 상태 인증은 하지 않습니다.',
      groups:[
        {id:'php',title:'PHP 엔진과 웹 워커',description:'PHP 엔진 수정·공급자 백포트·세션 후속 공지·Windows 패키지 재빌드를 구분합니다.',keys:['2026-10-30-php2shell-runtime-patching']},
        {id:'node',title:'Brotli 경로와 Node.js 반영',description:'신뢰할 수 없는 압축 해제 경로를 추적하고 모든 워커·복제본을 수정 런타임 증거와 연결합니다.',keys:['2026-10-30-node2shell-brotli-runtime-patching']},
        {id:'gitlab',title:'GitLab 서버 업그레이드',description:'RCE 수정 기준을 비교하고 필수 경유 지점을 거쳐 실행 반영을 확인합니다.',keys:['2026-10-30-gitlab2shell-cve-2026-110264']},
        {id:'trust',title:'JVM 인증서 신뢰',description:'공급자 신뢰 해제 안내와 새 JVM에서 수집한 CA 목록을 구분합니다.',keys:['2026-10-30-jdk-emudhra-truststore']},
      ]},
  },
  jekyll: {
    en: {label:'Ruby and Jekyll environment guides',title:'Ruby and Jekyll Guides: Bundle Context and Native Compiler Checks',eyebrow:'Legacy Ruby diagnostics',
      description:'Identify the selected Ruby and Bundler context, render an isolated legacy Jekyll fixture and separate native compiler checks from gem installation.',
      intro:'Start with the Ruby executable and declared bundle, then isolate compiler failures. These examples reproduce an unsupported Ruby 3.2.2 environment. A two-page render or standalone C++ probe does not verify a full site or a native gem rebuild.',
      groups:[
        {id:'bundle',title:'Check the runtime and bundle',description:'Identify the selected executable and render two pages with the declared legacy bundle.',keys:['2023-09-04-jekyll-install']},
        {id:'compiler',title:'Isolate compiler failures',description:'Separate Ruby build configuration from the compiler and SDK inputs used by a temporary C++ program.',keys:['2026-04-07-ruby-rbenv-jekyll-build-troubleshooting']},
      ]},
    ko: {label:'Ruby·Jekyll 환경 학습 안내',title:'Ruby·Jekyll 학습 안내: 번들 환경과 네이티브 컴파일러 확인',eyebrow:'과거 Ruby 환경 진단',
      description:'선택된 Ruby와 Bundler 환경을 확인하고 격리된 과거 Jekyll 예제를 렌더링합니다. 네이티브 컴파일러 검사와 gem 설치를 구분합니다.',
      intro:'Ruby 실행기와 선언한 번들부터 확인한 뒤 컴파일러 실패를 분리합니다. 지원이 종료된 Ruby 3.2.2 환경을 재현하는 예제입니다. 두 페이지 렌더링이나 독립 C++ 검사만으로 전체 사이트 빌드나 네이티브 gem 재빌드를 검증할 수는 없습니다.',
      groups:[
        {id:'bundle',title:'실행기와 번들 확인',description:'선택된 실행기를 확인하고 선언한 과거 번들로 두 페이지를 렌더링합니다.',keys:['2023-09-04-jekyll-install']},
        {id:'compiler',title:'컴파일러 실패 분리',description:'Ruby 빌드 설정과 임시 C++ 프로그램에 사용하는 컴파일러·SDK 입력을 구분합니다.',keys:['2026-04-07-ruby-rbenv-jekyll-build-troubleshooting']},
      ]},
  },
  automation: {
    en: {label:'Publishing workflow guides',title:'Publishing Workflow Guides: Draft Review, CI and Deployment',eyebrow:'Reviewed publishing',
      description:'Follow the move from automatic publication to draft PR review, then distinguish passing checks from an authorized production deployment.',
      intro:'Prepare a candidate as a draft, inspect the changes, and publish after approval. These articles trace this repository’s workflow and executable fixtures; a passing PR check alone does not prove a production deployment or content accuracy.',
      groups:[
        {id:'drafts',title:'Prepare a reviewable draft',description:'Follow candidate preparation and the review boundary before publication.',keys:['2026-04-07-jekyll-github-actions-content-pipeline']},
        {id:'deployment',title:'Separate checks from deployment',description:'Trace reusable checks, event conditions and production deployment evidence.',keys:['2026-04-07-jekyll-quality-gates-proof-html-bundler-audit']},
      ]},
    ko: {label:'게시 절차 학습 안내',title:'게시 절차 학습 안내: 초안 검토·CI·배포',eyebrow:'검토 후 게시',
      description:'자동 게시에서 Draft PR 검토로 전환한 흐름을 확인하고, 검사 통과와 승인된 운영 배포를 구분합니다.',
      intro:'후보를 초안으로 준비하고 변경 내용을 검토한 뒤 승인 후 게시합니다. 이 저장소의 워크플로와 실행 가능한 모의 예제를 따라갑니다. PR 검사 통과만으로 운영 배포나 본문 정확성이 입증되지는 않습니다.',
      groups:[
        {id:'drafts',title:'검토할 초안 준비',description:'후보 준비부터 게시 전 검토 경계까지 확인합니다.',keys:['2026-04-07-jekyll-github-actions-content-pipeline']},
        {id:'deployment',title:'검사와 배포 구분',description:'재사용 검사·이벤트 조건·운영 배포 근거를 이어 확인합니다.',keys:['2026-04-07-jekyll-quality-gates-proof-html-bundler-audit']},
      ]},
  },
  jenkins: {
    en: {label:'Jenkins recovery guides',title:'Jenkins Docker Guides: Startup, Persistence and Backup Restore',eyebrow:'Jenkins in Docker',
      description:'Start a disposable Jenkins controller, verify container recreation, then restore a stopped controller’s home into a new Docker volume.',
      intro:'Begin with startup and persistent storage before attempting a backup restore. The examples use disposable controllers and compare HTTP readiness, a marker and the initial password. They do not prove production workload recovery or credential decryption.',
      groups:[
        {id:'persistence',title:'Verify startup and persistence',description:'Check readiness and preserved state after recreating a container.',keys:['2023-09-28-jenkins-docker-install']},
        {id:'restore',title:'Restore into a new volume',description:'Stop the source controller, separate master.key from the archive and verify restored state.',keys:['2026-10-27-jenkins-home-backup-restore']},
      ]},
    ko: {label:'Jenkins 복구 학습 안내',title:'Jenkins Docker 학습 안내: 시작·영속성·백업 복구',eyebrow:'Docker의 Jenkins',
      description:'일회용 Jenkins 컨트롤러를 시작하고 컨테이너 재생성 후 상태를 확인합니다. 정지한 컨트롤러의 홈을 새 Docker 볼륨에 복구합니다.',
      intro:'시작과 영속 저장소부터 확인한 뒤 백업 복구로 넘어갑니다. 일회용 컨트롤러에서 HTTP 준비 상태·표식·초기 암호를 비교합니다. 운영 작업 복구나 자격 증명 복호화를 입증하는 예제는 아닙니다.',
      groups:[
        {id:'persistence',title:'시작과 영속성 확인',description:'준비 상태와 컨테이너 재생성 후 보존된 상태를 확인합니다.',keys:['2023-09-28-jenkins-docker-install']},
        {id:'restore',title:'새 볼륨에 복구',description:'원본 컨트롤러를 정지하고 master.key를 아카이브와 분리한 뒤 복구 상태를 확인합니다.',keys:['2026-10-27-jenkins-home-backup-restore']},
      ]},
  },
  linux: {
    en: {label:'Shell automation guides', title:'Shell Automation Guides: Interpreters, YAML and Release Assets', eyebrow:'Shell automation',
      description:'Choose sh or Bash, validate YAML and numeric versions, then select GitHub release assets with explicit input contracts and local tests.',
      intro:'Check the interpreter first, then validate inputs before selecting or executing a command. The numeric-version example does not implement all SemVer rules, and release metadata does not verify downloaded bytes.',
      groups:[
        {id:'interpreter',title:'Choose an interpreter',description:'Keep POSIX syntax and Bash invocation consistent.',keys:['2023-09-20-linux-shellscript-function-error']},
        {id:'inputs',title:'Validate structured input',description:'Parse YAML without eval and compare dotted numeric versions under explicit bounds.',keys:['2021-07-27-parse-yaml','2023-11-17-linux-shellscript-version-compare']},
        {id:'releases',title:'Select release assets',description:'Select the intended release asset, then compare the downloaded bytes with a trusted checksum.',keys:['2023-09-23-linux-shellscript-github-latest','2026-10-30-verify-sha256-download']},
      ]},
    ko: {label:'셸 자동화 학습 안내',title:'셸 자동화 학습 안내: 실행기·YAML·릴리스 자산',eyebrow:'셸 자동화',
      description:'sh·Bash 선택부터 YAML·숫자 버전 검증과 GitHub 릴리스 자산 선택까지 입력 조건과 로컬 예제로 이어 확인합니다.',
      intro:'실행기를 먼저 확인하고 명령을 선택하거나 실행하기 전에 입력을 검증합니다. 숫자 버전 예제는 전체 SemVer 규칙을 구현하지 않으며, 릴리스 메타데이터만으로 다운로드한 바이트를 검증할 수는 없습니다.',
      groups:[
        {id:'interpreter',title:'실행기 선택',description:'POSIX 문법과 Bash 실행 방식을 일치시킵니다.',keys:['2023-09-20-linux-shellscript-function-error']},
        {id:'inputs',title:'구조화된 입력 검증',description:'eval 없이 YAML을 읽고 명시한 범위에서 점으로 나눈 숫자 버전을 비교합니다.',keys:['2021-07-27-parse-yaml','2023-11-17-linux-shellscript-version-compare']},
        {id:'releases',title:'릴리스 자산 선택',description:'의도한 릴리스 자산을 고른 뒤 다운로드한 바이트를 신뢰하는 체크섬과 비교합니다.',keys:['2023-09-23-linux-shellscript-github-latest','2026-10-30-verify-sha256-download']},
      ]},
  },
  jdk: {
    en: {label:'JDK feature guides',title:'JDK Guides: Final APIs, Runtime Checks and Previews',eyebrow:'JDK',
      description:'Distinguish final APIs in JDK 21 and 25 from previews, inspect runtime binaries and certificate trust, and try Valhalla value-object semantics.',
      intro:'Separate language/API status from the runtime you actually install. These articles include historical release events and preview material; use each recorded version and do not infer current support from an old release note.',
      groups:[
        {id:'features',title:'Distinguish feature status',description:'Start with final APIs and the boundaries of preview features.',keys:['2023-09-20-jdk-21-release']},
        {id:'scoped',title:'Bound request context',description:'Use finalized JDK 25 ScopedValue and distinguish binding restoration from asynchronous inheritance.',keys:['2026-10-31-jdk25-scopedvalue']},
        {id:'preview',title:'Read preview history',description:'Understand String Templates and the standard formatting alternative shown in the article.',keys:['2023-09-23-jdk-21-string-templates']},
        {id:'binaries',title:'Inspect runtime binaries',description:'Keep the historical Temurin delay separate from platform and binary-metadata checks.',keys:['2023-10-10-temurin-jdk21-delay']},
        {id:'trust',title:'Check certificate trust',description:'Identify the JVM and supplier guidance before interpreting trust-store inventory.',keys:['2026-10-30-jdk-emudhra-truststore']},
        {id:'valhalla',title:'Try value-object semantics',description:'Compare records and value objects on JDK 28 EA without inferring a guaranteed memory layout.',keys:['2026-10-31-project-valhalla-value-objects']},
      ]},
    ko: {label:'JDK 기능 학습 안내',title:'JDK 학습 안내: 정식 API·실행기 확인·미리보기',eyebrow:'JDK',
      description:'JDK 21·25의 정식 API와 미리보기를 구분하고 실행기 바이너리·인증서 신뢰·Valhalla 값 객체의 의미를 살펴봅니다.',
      intro:'언어·API의 상태와 실제 설치할 실행기를 구분합니다. 과거 릴리스와 Preview 자료를 포함하므로 기록한 버전을 따르고 오래된 릴리스 글만으로 현재 지원 상태를 판단하지 않습니다.',
      groups:[
        {id:'features',title:'기능의 상태 구분',description:'정식 API와 Preview 기능의 적용 범위부터 확인합니다.',keys:['2023-09-20-jdk-21-release']},
        {id:'scoped',title:'요청 컨텍스트의 범위',description:'JDK 25 정식 ScopedValue를 실행하고 바인딩 복원과 비동기 상속의 경계를 구분합니다.',keys:['2026-10-31-jdk25-scopedvalue']},
        {id:'preview',title:'Preview 이력 확인',description:'String Templates 이력과 본문이 제공하는 표준 포맷팅 대안을 살펴봅니다.',keys:['2023-09-23-jdk-21-string-templates']},
        {id:'binaries',title:'실행기 바이너리 확인',description:'과거 Temurin 출시 지연과 플랫폼·바이너리 메타데이터 검사를 구분합니다.',keys:['2023-10-10-temurin-jdk21-delay']},
        {id:'trust',title:'인증서 신뢰 확인',description:'JVM과 공급자 공지를 식별한 뒤 신뢰 저장소 목록을 해석합니다.',keys:['2026-10-30-jdk-emudhra-truststore']},
        {id:'valhalla',title:'값 객체의 의미 실험',description:'JDK 28 EA에서 일반·값 레코드를 비교하고 특정 메모리 배치를 보장으로 해석하지 않습니다.',keys:['2026-10-31-project-valhalla-value-objects']},
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
  if(term==='security'&&lang!=='en'&&lang!=='ko')return undefined;
  if(term==='coding-test')return algorithmGuide(lang,all);
  if(term==='springboot')return springGuide(lang,all);
  if(!Object.hasOwn(paths,term))return undefined;
  const native=paths[term as keyof typeof paths];
  const localized=hasLocalizedGuide(lang)?guideLocales[lang]:undefined;
  const translated=hasLocalizedGuide(lang)?(term==='linux'?guideLocales[lang].linux:term==='util'?toolGuideLocales[lang]:remainingGuideLocales[lang][term as keyof typeof remainingGuideLocales[typeof lang]]):undefined;
  const groupCopy=translated?.groups as Record<string,{title:string;description:string}>|undefined;
  const definition=translated?{...translated,groups:native.en.groups.map(group=>({...group,...groupCopy![group.id]}))}:native[lang as 'en'|'ko'];
  const copyUpdatedAt=term==='util'?toolGuidesUpdatedAt:term==='linux'?localizedGuidesUpdatedAt:remainingGuideLocalesUpdatedAt;
  const items=all.filter(e=>e.language===lang&&e.kind==='post'&&(e.categories.includes(term)||crossCategoryKeys[term]?.includes(e.translationKey))&&e.reviewStatus!=='example'&&e.publishedAt.getTime()<=Date.now());
  if(!items.length)return undefined;
  const byKey=new Map(items.map(e=>[e.translationKey,e]));let position=1;
  const sections=definition.groups.map(group=>{
    const entries=group.keys.flatMap(key=>byKey.has(key)?[byKey.get(key)!]:[]);const start=position;position+=entries.length;
    return {id:group.id,title:group.title,description:group.description,entries,start};
  }).filter(group=>group.entries.length>0);
  const selected=new Set(sections.flatMap(s=>s.entries.map(e=>e.translationKey)));
  const extras=items.filter(e=>!selected.has(e.translationKey));const ordered=[...sections.flatMap(s=>s.entries),...extras];
  return {...definition,...(localized?.common||common[lang as 'en'|'ko']),lang,url:`/${lang}/categories/${term}/`,listAnchor:'articles',sections,extras,ordered,
    updatedAt:new Date(Math.max(localized?copyUpdatedAt.getTime():updatedAt.getTime(),...ordered.map(e=>(e.updatedAt||e.publishedAt).getTime())))};
}
export function categoryGuideAlternates(term:string,all:Entry[]) {
  return ([...nativeLanguages,...translationLanguages]).flatMap(language=>{const guide=categoryGuide(term,language,all);return guide?[{language,url:guide.url}]:[];});
}
export function technicalGuides(lang:Language,all:Entry[]) {
  return guideTerms.flatMap(term=>{const guide=categoryGuide(term,lang,all);return guide?[guide]:[];});
}
export function guideIndexAlternates(all:Entry[]) {
  return ([...nativeLanguages,...translationLanguages]).filter(language=>technicalGuides(language,all).length>0).map(language=>({language,url:`/${language}/guides/`}));
}
export function guideIndexStructuredData(lang:Language,guides:CategoryGuide[],site:URL) {
  const copy=guideIndexCopy[lang];const url=new URL(`/${lang}/guides/`,site).href;
  const lastmod=new Date(Math.max(hasLocalizedGuide(lang)?localizedGuidesUpdatedAt.getTime():updatedAt.getTime(),...guides.map(g=>g.updatedAt.getTime()))).toISOString();
  return [
    {'@context':'https://schema.org','@type':'CollectionPage','@id':url+'#collection',url,name:copy.title,description:copy.description,inLanguage:lang,dateModified:lastmod,mainEntity:{'@id':url+'#paths'}},
    {'@context':'https://schema.org','@type':'ItemList','@id':url+'#paths',numberOfItems:guides.length,itemListElement:guides.map((g,i)=>({'@type':'ListItem',position:i+1,name:g.title,url:new URL(g.url,site).href}))},
    {'@context':'https://schema.org','@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:copy.home,item:new URL(`/${lang}/`,site).href},{'@type':'ListItem',position:2,name:copy.label,item:url}]},
  ];
}

export function additionalArticleGuides(entry:Entry,all:Entry[]) {
  return technicalGuides(entry.language,all).filter(guide=>
    !entry.categories.some(term=>guide.url===`/${entry.language}/categories/${term}/`) &&
    guide.ordered.some(candidate=>candidate.url===entry.url));
}
