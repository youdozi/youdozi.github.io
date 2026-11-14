import test from 'node:test';
import assert from 'node:assert/strict';
import {readerMarkdown} from '../src/lib/reader-markdown.ts';
import {renderFeed} from '../src/lib/feed.ts';

test('reader Markdown removes editorial sections without swallowing later technical content',()=>{
  const content='## 이번 다이제스트 기준\n\n수집 절차\n\n### 내부 세부사항\n내부 값\n\n## 핵심 아티클\n\n기술 내용 2.25.2\n\n## 활용 가이드\n\n팀 위키 편집 안내\n\n## 검토 기록 — 2026-10-24\n\nHTTP 200 수집 감사\n\n## 별도 기술 설명\n\n버전 제약을 유지합니다.\n';
  const cleaned=readerMarkdown(content);
  for(const text of ['수집 절차','내부 값','팀 위키 편집 안내','HTTP 200 수집 감사'])assert.ok(!cleaned.includes(text));
  for(const text of ['기술 내용 2.25.2','버전 제약을 유지합니다.'])assert.ok(cleaned.includes(text));
});

test('reader Markdown preserves code, technical corrections, follow-up conditions and source links',()=>{
  const content='```md\n## 검토 기록 — 2026-10-24\n코드 예시\n```\n\n## 검증 및 보강 — 2026-10-24\n\n버전 14는 현재 권장 조합이 아닙니다.\n\n**검토 시점 후속 확인**\n\n- 공개 전 30일 동안 회원에게만 제공됩니다.\n\n**검토 초점 · 직접 적용 결과가 아닌 편집 제안**\n\n내부 편집 제안입니다.\n\n> 출처의 인용문\n> [인용 출처](https://example.com/source)\n\n- 리뉴얼 검토일: 2026-10-24\n- 확인할 점(자동 분류): 일반 안내\n- 보강 원고: [한국어](/ko/digest/example/)\n';
  const cleaned=readerMarkdown(content);
  assert.ok(cleaned.includes('```md\n## 검토 기록 — 2026-10-24\n코드 예시\n```'));
  for(const text of ['## 추가 설명','버전 14는 현재 권장 조합이 아닙니다.','공개 전 30일 동안 회원에게만 제공됩니다.','https://example.com/source','- 관련 글: [한국어](/ko/digest/example/)'])assert.ok(cleaned.includes(text));
  for(const text of ['내부 편집 제안입니다.','**검토 시점 후속 확인**','리뉴얼 검토일:','확인할 점(자동 분류):'])assert.ok(!cleaned.includes(text));
});

test('public RSS retains news and follow-up facts while excluding editorial review advice',()=>{
  const edition={title:'Article',claims:[{text:'A qualified statement.'}],followUp:[{text:'A later restriction applies.'}]};
  const entry={title:edition.title,url:'/en/digest/example/',description:'Description',publishedAt:new Date('2026-01-01T00:00:00Z'),renewal:{data:{archiveDate:'2025-12-01',url:'https://example.com/source',reviewFocus:{en:'PRIVATE_REVIEW_ADVICE'},editions:{en:edition}}},renewalEdition:edition,renewalFocus:'PRIVATE_REVIEW_ADVICE'};
  const feed=renderFeed([entry],'en',new URL('https://youdozi.github.io/'),'Blog');
  for(const value of ['A qualified statement.','A later restriction applies.','2025-12-01','https://example.com/source'])assert.ok(feed.includes(value));
  assert.ok(!feed.includes('PRIVATE_REVIEW_ADVICE'));
});

test('body links select published local editions and preserve unavailable, section and external links',async()=>{
  const {mkdtemp,mkdir,writeFile,rm}=await import('node:fs/promises');
  const {tmpdir}=await import('node:os');
  const {join}=await import('node:path');
  const {pathToFileURL}=await import('node:url');
  const {satteri}=await import('@astrojs/markdown-satteri');
  const {localizedArticleLinks}=await import('./localized-article-links.mjs');
  const base=await mkdtemp(join(tmpdir(),'localized-article-links-'));
  async function article(lang,key,slug,extra={}){
    const directory=lang==='en'?'posts':'technical-translations';
    const path=join(base,'src/content',directory,lang,`${key}.md`);
    await mkdir(join(base,'src/content',directory,lang),{recursive:true});
    await writeFile(path,`---\n${JSON.stringify({kind:'post',language:lang,translationKey:key,routeSlug:slug,publishedAt:'2026-01-01',state:'approved',...extra})}\n---\nBody`);
    return pathToFileURL(path);
  }
  try{
    const fileURL=await article('ja','source','source');
    await article('en','topic','original');await article('ja','topic','localized');
    await article('en','missing','missing');
    await article('en','future','future');await article('ja','future','future',{publishedAt:'2999-01-01'});
    await article('en','example','example');await article('ja','example','example',{reviewStatus:'example'});
    await article('en','unapproved','unapproved');await article('ja','unapproved','unapproved',{state:'draft'});
    const renderer=await satteri({hastPlugins:[localizedArticleLinks(base,new Date('2026-11-14'))]}).createRenderer({syntaxHighlight:false});
    const input='[local](/en/posts/original/?from=guide)\n\n[absolute](https://youdozi.github.io/en/posts/original/)\n\n[section](/en/posts/original/#setup)\n\n[missing](/en/posts/missing/)\n\n[future](/en/posts/future/)\n\n[example](/en/posts/example/)\n\n[draft](/en/posts/unapproved/)\n\n[external](https://example.com/en/posts/original/)\n\n[relative](//example.com/en/posts/original/)\n\n`[literal](/en/posts/original/)`\n\n```html\n<a href="/en/posts/original/">literal</a>\n```';
    const html=(await renderer.render(input,{fileURL})).code;
    assert.ok(html.includes('href="/ja/posts/localized/?from=guide"'));
    assert.ok(html.includes('href="https://youdozi.github.io/ja/posts/localized/"'));
    for(const href of ['/en/posts/original/#setup','/en/posts/missing/','/en/posts/future/','/en/posts/example/','/en/posts/unapproved/','https://example.com/en/posts/original/','//example.com/en/posts/original/'])assert.ok(html.includes(`href="${href}"`),href);
    assert.ok(html.includes('[literal](/en/posts/original/)'));
    assert.ok(html.includes('href="/en/posts/original/"'));
    assert.ok((await renderer.render('[kept](/en/posts/original/)')).code.includes('href="/en/posts/original/"'));
  }finally{await rm(base,{recursive:true,force:true});}
});
