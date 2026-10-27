import test from 'node:test';
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import YAML from 'yaml';
import { createHash } from 'node:crypto';
import { convertPost } from './migrate-jekyll.mjs';

test('each original post retains its provenance and a unique language route after review', async () => {
  const routes = new Set(); const sources = new Set(); const translations = new Set();
  const files = await readdir('src/content/posts/ko');
  for (const file of files) {
    const source = await readFile(`src/content/posts/ko/${file}`, 'utf8');
    const [, front, body] = source.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    const data = YAML.parse(front);
    if (data.legacySource) {
      const original = await readFile(data.legacySource,'utf8');
      const expected = convertPost(original, data.legacySource);
      if (data.reviewedAt) {
        assert.equal(data.archiveBodySha256, createHash('sha256').update(expected.body).digest('hex'), data.legacySource);
        assert.ok(data.reviewScope && data.reviewSources.length > 0, data.legacySource);
        assert.ok(body.trim().length > 0);
      } else assert.equal(body, expected.body, data.legacySource);
      assert.equal(data.routeSlug, expected.metadata.routeSlug);
      assert.ok(!sources.has(data.legacySource)); sources.add(data.legacySource);
    } else {
      assert.equal(data.legacyUrl, undefined, 'New posts do not invent legacy routes');
      assert.equal(data.archiveBodySha256, undefined, 'New posts do not invent archive hashes');
      assert.ok(body.trim().length > 0 && data.description && data.reviewScope && data.reviewSources.length > 0);
    }
    assert.equal(data.language, 'ko');
    assert.equal(typeof data.routeSlug, 'string');
    const route = `/ko/${data.kind === 'digest' ? 'digest' : 'posts'}/${data.routeSlug}/`;
    assert.ok(!routes.has(route), `duplicate ${route}`); routes.add(route);
    assert.ok(!translations.has(data.translationKey)); translations.add(data.translationKey);
  }
  async function originals(dir) {
    return (await Promise.all((await readdir(dir,{withFileTypes:true})).map(e => e.isDirectory() ? originals(`${dir}/${e.name}`) : Promise.resolve(e.name.endsWith('.markdown') ? [`${dir}/${e.name}`] : [])))).flat();
  }
  assert.deepEqual([...sources].sort(), (await originals('_posts')).sort(), 'Every original source retains exactly one reviewed Korean edition');
});

test('migration converts prose attributes and image spaces while preserving code', () => {
  const content = '---\ntitle: Example\ndate: 2026-01-01 00:00:00 +0900\ncategories: [java]\ntags: []\n---\n![image](/assets/my image.png){:width="40%"}\n```sh\necho "{:literal}"\n```\n';
  const post = convertPost(content,'_posts/2026-01-01-example.markdown');
  assert.match(post.body,/my%20image.png/);
  assert.ok(!post.body.includes('width="40%"'));
  assert.ok(post.body.includes('echo "{:literal}"'));
  assert.equal(post.metadata.legacyUrl,'/java/example/');
  assert.equal(post.metadata.publishedAt,'2025-12-31T15:00:00.000Z');
});

test('automation creates a draft review PR and reusable validation cannot deploy', async () => {
  const pipeline = YAML.parse(await readFile('.github/workflows/dev-content-pipeline.yml','utf8'));
  assert.equal(pipeline.on.workflow_dispatch.inputs.preview.default,false);
  assert.equal(pipeline.jobs.publish, undefined);
  assert.equal(pipeline.jobs.generate.if, "github.ref == 'refs/heads/main'");
  assert.equal(pipeline.jobs.validate.uses,'./.github/workflows/site-checks.yml');
  assert.equal(pipeline.jobs.validate.with.ref,'${{ needs.generate.outputs.commit_sha }}');
  assert.deepEqual(pipeline.jobs.review.needs,['generate','validate']);
  assert.equal(pipeline.jobs.generate.permissions['pages'], undefined);
  assert.equal(pipeline.jobs.review.permissions['pages'], undefined);
  const commit = pipeline.jobs.generate.steps.find(step=>step.id==='commit').run;
  assert.match(commit,/git push origin "HEAD:refs\/heads\/\$branch"/);
  assert.ok(!/git push[^\n]*main/.test(commit));
  const review = pipeline.jobs.review.steps.at(-1).with.script;
  assert.match(review,/draft: true/);
  assert.match(review,/createWorkflowDispatch/);
  assert.match(review,/workflow_id: 'site-quality-gates.yml', ref: process.env.REVIEW_BRANCH/);
  assert.equal(pipeline.jobs.review.permissions.actions,'write');
  assert.ok(!/pulls\.merge|enableAutoMerge|auto_merge/.test(review));
  const pending = pipeline.jobs.generate.steps.find(step=>step.id==='pending').with.script;
  const output = {};
  const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
  const runPending = new AsyncFunction('github','context','core',pending);
  const context = {repo:{owner:'youdozi',repo:'youdozi.github.io'}};
  const github = {rest:{pulls:{list(){}}},paginate:async()=>[{html_url:'review-url',head:{repo:{full_name:'youdozi/youdozi.github.io'},ref:'content/digest-review-1'}}]};
  const core = {setOutput:(key,value)=>output[key]=value,summary:{addRaw(){return this;},async write(){}}};
  await runPending(github,context,core);
  assert.equal(output.exists,true);
  github.paginate=async()=>[];
  await runPending(github,context,core);
  assert.equal(output.exists,false);
  assert.equal(pipeline.jobs.generate.steps.find(step=>step.id==='digest').if, "steps.pending.outputs.exists != 'true'");
  const site = YAML.parse(await readFile('.github/workflows/site-quality-gates.yml','utf8'));
  assert.equal(site.on.workflow_call,undefined);
  assert.equal(site.jobs.build.uses,'./.github/workflows/site-checks.yml');
  assert.match(site.jobs.deploy.if,/github.ref == 'refs\/heads\/main'/);
  assert.match(site.jobs.deploy.if,/github.event_name == 'push'/);
  assert.ok(site.jobs.deploy.steps.some(s=>s.uses==='actions/deploy-pages@v4'));
  const checks = YAML.parse(await readFile('.github/workflows/site-checks.yml','utf8'));
  assert.deepEqual(Object.keys(checks.jobs),['build']);
  assert.deepEqual(checks.permissions,{contents:'read'});
  assert.equal(checks.jobs.build.steps[0].with.ref,'${{ inputs.ref }}');
  assert.equal(checks.on.workflow_call.inputs.pages_artifact.default,false);

});

test('Astro renders paired editions, reciprocal language links, and escapes source titles', async () => {
  const { writeFile, unlink } = await import('node:fs/promises');
  const { spawnSync } = await import('node:child_process');
  const result = spawnSync('python3', ['-B', '-c', "import sys,json;sys.path.insert(0,'scripts');from test_bilingual_digest import article;a=article();a['publishedAt']='2000-01-01T00:00:00+09:00';a['editions']['en']['title']='Literal {{ 7 | times: 7 }} <script>alert(1)</script>';print(json.dumps({'date':'2000-01-01','publishedAt':'2000-01-01T01:00:00+09:00','articles':[a]}))"], {encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);
  const fixture='src/content/digests/2000-01-01.json';
  const {publishBatch,checkPublished}=await import('./translations.mjs');
  const batch=JSON.parse(await readFile('.pipeline/translations/batches/pilot-001.json','utf8'));
  const spanishBatch=JSON.parse(await readFile('.pipeline/translations/batches/spanish-001.json','utf8'));
  const source=JSON.parse(await readFile(`src/content/renewals/${batch.translations[0].renewalId}.json`,'utf8'));
  const translationFiles=[];
  const existingTranslations=new Map();

  try {
    await writeFile(fixture,result.stdout,{flag:'wx'});
    const records=[],missing=[];
    for(const draft of [...batch.translations,...spanishBatch.translations]){
      const path=`src/content/translations/${draft.language}-${draft.renewalId}.json`;
      let bytes;
      try{bytes=await readFile(path,'utf8');}catch(error){if(error.code!=='ENOENT')throw error;}
      if(bytes===undefined){missing.push(draft);continue;}
      existingTranslations.set(path,bytes);
      const record=JSON.parse(bytes);
      assert.deepEqual(record.edition,draft.edition,'Published pilot must match its reviewed draft');
      assert.equal(record.reviewFocus,draft.reviewFocus);
      records.push(record);
    }
    if(missing.length){
      const created=await publishBatch({...batch,translations:missing},{reviewedBy:'Build test fixture',pullRequest:1,basis:'Temporary integration fixture, removed after test'});
      translationFiles.push(...created.map(t=>`src/content/translations/${t.language}-${t.renewalId}.json`));
      records.push(...created);
    }
    const published=records.filter(record=>record.renewalId===source.id);
    await checkPublished();
    const approvedTranslations=await Promise.all((await readdir('src/content/translations')).filter(file=>file.endsWith('.json')).map(async file=>JSON.parse(await readFile(`src/content/translations/${file}`,'utf8'))));

    const assets=spawnSync(process.execPath,['scripts/prepare-public.mjs'],{encoding:'utf8'});assert.equal(assets.status,0,assets.stderr);
    const build=spawnSync(process.execPath,['node_modules/astro/bin/astro.mjs','build'],{encoding:'utf8',maxBuffer:8*1024*1024});
    assert.equal(build.status,0,build.stderr);
    const checked=spawnSync('python3',['-B','scripts/check_site.py'],{encoding:'utf8'});assert.equal(checked.status,0,checked.stdout+checked.stderr);
    const en=await readFile('dist/en/digest/2000-01-01/index.html','utf8');
    const ko=await readFile('dist/ko/digest/2000-01-01/index.html','utf8');
    assert.match(en,/<html lang="en">/);assert.match(ko,/<html lang="ko">/);
    assert.match(en,/hreflang="ko" href="https:\/\/youdozi.github.io\/ko\/digest\/2000-01-01\/"/);
    assert.match(ko,/hreflang="en" href="https:\/\/youdozi.github.io\/en\/digest\/2000-01-01\/"/);
    assert.match(en,/Literal \{\{ 7 \| times: 7 \}\}/);
    assert.ok(!en.includes('<script>alert(1)</script>'));
    assert.match(en,/&lt;script&gt;/);
    const fixtureGraph=JSON.parse(en.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
    assert.ok(!JSON.stringify(fixtureGraph).includes('\\u003c'));
    assert.ok(!en.includes('Source evidence'));assert.ok(!ko.includes('원문 인용 근거'));
    for(const [lang,html] of [['en',en],['ko',ko]]){
      const article=JSON.parse(result.stdout).articles[0];
      assert.ok(html.includes(article.url));
      for(const claim of article.editions[lang].claims)assert.ok(html.includes(claim.text));
    }
    const englishIndex=JSON.parse(await readFile('dist/en/search-index.json','utf8'));
    assert.ok(englishIndex.some(entry => entry.url === '/en/digest/2000-01-01/'));
    assert.ok(englishIndex.some(entry => entry.url === '/en/posts/2023-09-19-springboot-test-webclient/'));
    const koreanIndex=JSON.parse(await readFile('dist/ko/search-index.json','utf8'));
    assert.ok(!koreanIndex.some(entry=>entry.url==='/ko/digest/2026-03-16/'));
    const sample=await readFile('dist/ko/digest/2026-03-16/index.html','utf8');
    assert.match(sample,/noindex,follow/);assert.match(sample,/예제 데이터/);
    const sitemap=await readFile('dist/sitemap.xml','utf8');
    assert.ok(!sitemap.includes('/ko/digest/2026-03-16/'));
    const reviewShell=await readFile('dist/review/index.html','utf8');
    assert.match(reviewShell,/noindex,follow/);
    assert.match(reviewShell,/id="generate-draft"[^>]*href="https:\/\/github.com\/youdozi\/youdozi.github.io\/actions\/workflows\/dev-content-pipeline.yml"/);

    assert.ok(!sitemap.includes('/review/'));
    assert.ok(!reviewShell.includes('Spring Security OAuth scope update'));
    assert.ok(!reviewShell.includes('Literal {{ 7 | times: 7 }}'));
    assert.ok(!reviewShell.includes('utteranc.es'));

    const englishArticle=await readFile('dist/en/posts/2023-09-19-springboot-test-webclient/index.html','utf8');
    assert.match(englishArticle,/<html lang="en">/);
    assert.match(englishArticle,/rel="canonical" href="https:\/\/youdozi.github.io\/en\/posts\/2023-09-19-springboot-test-webclient\/"/);
    assert.match(englishArticle,/hreflang="ko" href="https:\/\/youdozi.github.io\/ko\/posts\/2023-09-19-springboot-test-webclient\/"/);
    assert.ok(!englishArticle.includes('hreflang="ja"'));assert.ok(englishArticle.includes('href="/ja/"'));
    const graph=JSON.parse(englishArticle.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
    const posting=graph.find(item=>item['@type']==='BlogPosting');
    assert.equal(posting.inLanguage,'en');assert.equal(posting.author.name,'youdozi');
    assert.ok(posting.datePublished && posting.dateModified);
    assert.ok(graph.some(item=>item['@type']==='BreadcrumbList'));


    // Check emitted paths rather than assuming the registry is rendered correctly.
    const guideCounts=[['coding-test',10],['springboot',9],['linux',4],['jdk',3],['util',3],['automation',2],['jenkins',2],['jekyll',2]];
    for(const lang of ['en','ko']){
      const hubPath=`/${lang}/guides/`;
      const hub=await readFile(`dist${hubPath}index.html`,'utf8');
      const hubData=JSON.parse(hub.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
      const hubList=hubData.find(x=>x['@type']==='ItemList');
      assert.deepEqual(hubList.itemListElement.map(x=>x.url),guideCounts.map(([term])=>`https://youdozi.github.io/${lang}/categories/${term}/`));
      assert.equal(hubList.numberOfItems,8);
      assert.ok(!hubData.some(x=>x['@type']==='BlogPosting'));
      for(const [term,count] of guideCounts){
        const path=`/${lang}/categories/${term}/`;
        const html=await readFile(`dist${path}index.html`,'utf8');
        const data=JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
        const collection=data.find(x=>x['@type']==='CollectionPage');
        const list=data.find(x=>x['@type']==='ItemList');
        assert.equal(list.numberOfItems,count);assert.equal(collection.inLanguage,lang);
        const groups=html.match(/<div class="algorithm-groups"[^>]*>([\s\S]*?)<\/div>/)[1];
        const visible=[...groups.matchAll(/href="([^"]+)"/g)].map(m=>'https://youdozi.github.io'+m[1]);
        assert.deepEqual(visible,list.itemListElement.map(x=>x.url),'Visible order must match schema');
        assert.ok(html.includes(`href="${hubPath}"`));
        assert.ok(sitemap.includes(`<loc>https://youdozi.github.io${path}</loc><lastmod>${collection.dateModified}</lastmod>`));
        for(const item of list.itemListElement){
          const article=await readFile(`dist${item.url.replace('https://youdozi.github.io','')}index.html`,'utf8');
          assert.ok(article.includes(`href="${path}"`),'Each linked article returns to its category guide');
        }
      }
      assert.ok(hub.includes(`hreflang="x-default" href="https://youdozi.github.io/en/guides/"`));
      assert.ok(sitemap.includes(`<loc>https://youdozi.github.io${hubPath}</loc>`));
    }
    const coreRegistry=JSON.parse(await readFile('content/seo/core-articles.json','utf8'));
    for(const lang of ['en','ko']) {
      const home=await readFile(`dist/${lang}/index.html`,'utf8');
      const featured=home.match(/<section class="core-articles"[\s\S]*?<\/section>/)?.[0];
      assert.ok(featured,'Native home exposes the selected practical guides');
      assert.deepEqual([...featured.matchAll(/href="([^"]+)"/g)].map(m=>m[1]),coreRegistry.articles.map(a=>`/${lang}/posts/${a.key}/`));
    }
    const japaneseHome=await readFile('dist/ja/index.html','utf8');
    assert.ok(!japaneseHome.includes('core-articles-heading'));
    assert.ok(!japaneseHome.includes('href="/ja/guides/"'),'Do not link to an unavailable guide index');


    const renewals=await readdir('src/content/renewals');
    const manifest=JSON.parse(await readFile('.pipeline/archive-renewal/manifest.json','utf8'));
    assert.deepEqual(renewals.map(f=>f.replace(/\.json$/,'')).sort(),manifest.items.filter(r=>r.status==='published').map(r=>r.id).sort());
    for(const file of renewals){
      const article=JSON.parse(await readFile(`src/content/renewals/${file}`,'utf8'));
      for(const lang of ['en','ko']){
        const url=`https://youdozi.github.io/${lang}/digest/${article.slug}/`;
        const html=await readFile(`dist/${lang}/digest/${article.slug}/index.html`,'utf8');
        assert.ok(html.includes(`rel="canonical" href="${url}"`));
        for(const language of ['en','ko'])assert.ok(html.includes(`hreflang="${language}" href="https://youdozi.github.io/${language}/digest/${article.slug}/"`));
        assert.ok(html.includes(`hreflang="x-default" href="https://youdozi.github.io/en/digest/${article.slug}/"`));
        assert.ok(html.includes(`data-archive-date="${article.archiveDate}"`));
        assert.ok(!html.includes('noindex,follow'));
        for(const document of article.documents)assert.ok(html.includes(document.url.replaceAll('&','&amp;')),'Reader source links must remain available');
        const data=JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]).find(item=>item['@type']==='BlogPosting');
        assert.equal(data.datePublished,new Date(article.editionPublishedAt[lang]).toISOString());
        assert.equal(data.dateModified,new Date(article.updatedAt).toISOString());
        assert.equal(data.inLanguage,lang);assert.equal(data.temporalCoverage,article.archiveDate);
        assert.ok(sitemap.includes(`<loc>${url}</loc>`));
        const feed=await readFile(`dist/${lang}/feed.xml`,'utf8');
        const feedItems=feed.match(/<item>[\s\S]*?<\/item>/g)||[];
        assert.ok(feedItems.length<=30);
        const cutoff=Math.min(...feedItems.map(item=>Date.parse(item.match(/<atom:updated>(.*?)<\/atom:updated>/)[1])));
        const feedItem=feedItems.find(item=>item.includes(`<guid isPermaLink="true">${url}</guid>`));
        if(feedItems.length<30 || Date.parse(article.updatedAt)>cutoff)assert.ok(feedItem,`latest renewal omitted from RSS: ${url}`);
        if(feedItem){
          assert.ok(feedItem.includes(`<pubDate>${new Date(article.editionPublishedAt[lang]).toUTCString()}</pubDate>`));
          assert.ok(feedItem.includes(`<atom:updated>${new Date(article.updatedAt).toISOString()}</atom:updated>`));
        }
        const index=lang==='en'?englishIndex:koreanIndex;
        assert.ok(index.some(e=>e.url===`/${lang}/digest/${article.slug}/` && e.content.includes(article.editions[lang].claims[0].text)));
      }
    }
    const revisedLegacy=await readFile('dist/ko/digest/2026-10-20/index.html','utf8');
    assert.ok(revisedLegacy.includes('정정 요약'));
    assert.ok(!revisedLegacy.includes('32사'));
    for(const internal of ['기존 아카이브 글입니다.','검토·보강:','활용 가이드','검토 기록 —','검토 초점 · 직접 적용 결과가 아닌 편집 제안','검토 시점 후속 확인'])assert.ok(!revisedLegacy.includes(internal));
    const legacyIndex=koreanIndex.find(entry=>entry.url==='/ko/digest/2026-10-20/');
    assert.ok(legacyIndex);
    for(const internal of ['활용 가이드','검토 기록 —','직접 적용 결과가 아닌 편집 제안'])assert.ok(!legacyIndex.content.includes(internal));
    assert.ok(!sitemap.includes('pilot-001'));

    for(const record of published){
      const lang=record.language,url=`https://youdozi.github.io/${lang}/digest/${source.slug}/`;
      const html=await readFile(`dist/${lang}/digest/${source.slug}/index.html`,'utf8');
      assert.ok(html.includes(`<html lang="${lang}">`));
      const policy=JSON.parse(await readFile('src/lib/locales.json','utf8'));
      assert.ok(html.includes(`property="og:locale" content="${policy.locales[lang].ogLocale}"`));
      assert.ok(html.includes(`rel="canonical" href="${url}"`));
      assert.ok(!html.includes('noindex,follow'));
      for(const other of ['en','ko',...published.map(t=>t.language)]){
        const counterpart=await readFile(`dist/${other}/digest/${source.slug}/index.html`,'utf8');
        assert.ok(html.includes(`hreflang="${other}" href="https://youdozi.github.io/${other}/digest/${source.slug}/"`));
        assert.ok(counterpart.includes(`hreflang="${lang}" href="${url}"`));
      }
      assert.ok(html.includes(`hreflang="x-default" href="https://youdozi.github.io/en/digest/${source.slug}/"`));
      const graph=JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
      const posting=graph.find(item=>item['@type']==='BlogPosting');
      assert.equal(posting.inLanguage,lang);assert.equal(posting.datePublished,record.publishedAt);
      assert.equal(posting.dateModified,record.updatedAt);
      assert.ok(!html.includes(source.editions.en.claims[0].evidence[0].quote));
      assert.ok(!html.includes(record.reviewFocus));
      assert.ok(html.includes(source.url));
      const index=JSON.parse(await readFile(`dist/${lang}/search-index.json`,'utf8'));
      assert.equal(index.length,approvedTranslations.filter(t=>t.language===lang).length);
      assert.ok(index.find(entry=>entry.url===`/${lang}/digest/${source.slug}/`)?.content.includes(record.edition.claims[0]));
      const feed=await readFile(`dist/${lang}/feed.xml`,'utf8');
      assert.ok(feed.includes(`<language>${lang}</language>`));
      assert.ok(feed.includes(record.edition.claims[0].replaceAll('&','&amp;').replaceAll("'",'&apos;')));
      assert.ok(sitemap.includes(`<loc>${url}</loc>`));
      assert.ok(!sitemap.includes(`/${lang}/posts/`));
      assert.ok(!(await readFile(`dist/${lang}/index.html`,'utf8')).includes('noindex,follow'));
      const tagsPage=await readFile(`dist/${lang}/tags/index.html`,'utf8');
      assert.ok(!tagsPage.includes('archive-renewal'));
      assert.match(tagsPage,/noindex,follow/);
      assert.ok(!tagsPage.includes('hreflang='));
      assert.ok(!sitemap.includes(`<loc>https://youdozi.github.io/${lang}/tags/</loc>`));
      assert.ok((await readFile(`dist/${lang}/posts/index.html`,'utf8')).includes('noindex,follow'));
    }
    const esIndex=JSON.parse(await readFile('dist/es/search-index.json','utf8'));
    const esFeed=await readFile('dist/es/feed.xml','utf8');
    for(const draft of spanishBatch.translations){
      const original=JSON.parse(await readFile(`src/content/renewals/${draft.renewalId}.json`,'utf8'));
      const route=`/es/digest/${original.slug}/`,url=`https://youdozi.github.io${route}`;
      const html=await readFile(`dist${route}index.html`,'utf8');
      assert.ok(html.includes('<html lang="es">'));
      assert.ok(html.includes(`rel="canonical" href="${url}"`));
      assert.ok(html.includes('property="og:locale" content="es_ES"'));
      assert.ok(esIndex.some(entry=>entry.url===route&&entry.content.includes(draft.edition.claims[0])));
      assert.ok(esFeed.includes(url));assert.ok(sitemap.includes(`<loc>${url}</loc>`));
      for(const lang of ['en','ko','zh-CN','ja','de','fr','ru']){
        const counterpart=await readFile(`dist/${lang}/digest/${original.slug}/index.html`,'utf8');
        assert.ok(html.includes(`hreflang="${lang}" href="https://youdozi.github.io/${lang}/digest/${original.slug}/"`));
        assert.ok(counterpart.includes(`hreflang="es" href="${url}"`));
      }
    }

    const tags=await readFile('dist/ko/tags/index.html','utf8');
    const upper=tags.match(/href="([^"]+)"[^>]*>SpringBoot /)?.[1];
    const lower=tags.match(/href="([^"]+)"[^>]*>springboot /)?.[1];
    assert.ok(upper && lower);assert.notEqual(upper,lower);
    assert.ok((await readFile(`dist${decodeURIComponent(upper)}index.html`,'utf8')).includes('Gradle'));

  } finally {
    await unlink(fixture);
    await Promise.all(translationFiles.map(file=>unlink(file)));
    for(const [file,bytes] of existingTranslations)assert.equal(await readFile(file,'utf8'),bytes,'Build tests must preserve real publication records');
  }
});

test('draft notification mentions the owner once and rejects non-review PRs', async () => {
  const notification=YAML.parse(await readFile('.github/workflows/digest-review-notification.yml','utf8'));
  const pipeline=YAML.parse(await readFile('.github/workflows/dev-content-pipeline.yml','utf8'));
  assert.equal(pipeline.jobs.notify.needs,'review');
  assert.equal(pipeline.jobs.notify.uses,'./.github/workflows/digest-review-notification.yml');
  assert.equal(notification.permissions.pages,undefined);
  assert.equal(notification.jobs.notify.if,"github.ref == 'refs/heads/main'");
  const run = new (Object.getPrototypeOf(async function(){}).constructor)('github','context','core','process',notification.jobs.notify.steps[0].with.script);
  const pr={state:'open',draft:true,base:{ref:'main'},head:{repo:{full_name:'youdozi/youdozi.github.io'},ref:'content/digest-review-123'},html_url:'https://github.com/youdozi/youdozi.github.io/pull/20'};
  let comments=[];const sent=[];
  const github={rest:{pulls:{get:async()=>({data:pr})},issues:{listComments(){},createComment:async(data)=>sent.push(data)}},paginate:async()=>comments};
  const context={repo:{owner:'youdozi',repo:'youdozi.github.io'}};
  const core={info(){},summary:{addRaw(){return this},async write(){}}};
  const process={env:{PR_NUMBER:'20'}};
  await run(github,context,core,process);
  assert.equal(sent.length,1);assert.equal(sent[0].issue_number,20);
  assert.match(sent[0].body,/https:\/\/youdozi.github.io\/review\/\?pr=20/);
  assert.match(sent[0].body,/@youdozi/);assert.match(sent[0].body,/아직 사이트에는 게시되지/);
  comments=[{user:{login:'github-actions[bot]'},body:sent[0].body}];
  await run(github,context,core,process);assert.equal(sent.length,1);
  comments=[];pr.draft=false;
  await assert.rejects(run(github,context,core,process),/Only an open digest review draft/);
  assert.equal(sent.length,1);
});

test('generation and browser schemas agree on malformed saved content', async () => {
  const { spawnSync } = await import('node:child_process');
  const { digestSchema } = await import('../src/lib/digest-schema.ts');
  const original=JSON.parse(await readFile('src/content/digests/2026-10-24.json','utf8'));
  const cases={valid:original};
  function change(name,mutate){const data=structuredClone(original);mutate(data);cases[name]=data;}
  function withEditorial(data){
    const a=data.articles[0];
    a.selection={audience:'java-spring-backend',method:'keyword-rules-v1',relevance:'direct',priority:'normal',reasons:['jvm-spring']};
    a.editorial={opinion:{en:'',ko:''},experiment:{status:'not_tested',reportUrl:null,environment:{en:'',ko:''},result:{en:'',ko:''}}};
    for(const lang of ['en','ko'])a.editions[lang].review={keyChange:[0],affectedAudience:[],conditions:[1]};
  }
  change('valid_editorial',withEditorial);
  change('invalid_title_comparison',d=>{withEditorial(d);d.articles[0].editions.en.title+=' 100x faster';});
  change('invalid_bilingual_component',d=>{withEditorial(d);const e=d.articles[0].editions.ko;e.claims[0].text=e.claims[0].text.replaceAll('Node.js','런타임');e.summary=e.claims.map(c=>c.text).join(' ');});
  change('invalid_bilingual_number',d=>{withEditorial(d);const e=d.articles[0].editions.ko;e.claims[1].text=e.claims[1].text.replace('5개','9개');e.summary=e.claims.map(c=>c.text).join(' ');});
  change('invalid_bilingual_sections',d=>{withEditorial(d);d.articles[0].editions.ko.review.conditions=[];});
  change('invalid_review_reference',d=>{withEditorial(d);d.articles[0].editions.en.review.conditions=[99];});
  change('unproven_experiment',d=>{withEditorial(d);d.articles[0].editorial.experiment.status='tested';});
  change('invalid_selection_reason',d=>{withEditorial(d);d.articles[0].selection.reasons.push('constructor');});
  change('source',d=>d.articles[0].url='https://unapproved.example/news');
  change('future',d=>d.articles[0].publishedAt='2099-01-01T00:00:00+00:00');
  change('ko_length',d=>{const e=d.articles[0].editions.ko;e.claims[0].text='가'.repeat(300);e.claims[1].text='나'.repeat(200);e.summary=e.claims.map(c=>c.text).join(' ');});
  change('evidence',d=>d.articles[0].editions.en.claims[0].evidence[0].quote='short');
  change('duplicate',d=>d.articles[1].url=d.articles[0].url);
  change('tracking_duplicate',d=>{d.articles[1].source=d.articles[0].source;d.articles[1].url=d.articles[0].url+'?utm_source=test#fragment';});
  change('update_date',d=>d.updatedAt='2000-01-01T00:00:00+09:00');
  const response=spawnSync('python3',['-B','-c',"import json,sys;sys.path.insert(0,'scripts');from generate_digest import validate_digest;print(json.dumps({k:not bool(validate_digest(v)) for k,v in json.load(sys.stdin).items()}))"],{input:JSON.stringify(cases),encoding:'utf8'});
  assert.equal(response.status,0,response.stderr);
  const expected=JSON.parse(response.stdout);
  for(const [name,data] of Object.entries(cases)){
    assert.equal(expected[name],name.startsWith('valid'),name);
    assert.equal(digestSchema.safeParse(data).success,expected[name],name);
  }
  const pkg=JSON.parse(await readFile('package.json','utf8'));
  assert.ok(pkg.scripts.check.startsWith('npm run check:digests &&'));
  assert.ok(pkg.scripts.build.startsWith('npm run check:digests &&'));
});

test('RSS exposes every added article and update time without changing publication identity', async () => {
  const { digestSchema } = await import('../src/lib/digest-schema.ts');
  const { renderFeed } = await import('../src/lib/feed.ts');
  const data=digestSchema.parse(JSON.parse(await readFile('src/content/digests/2026-10-24.json','utf8')));
  const prior={...data,updatedAt:undefined,articles:data.articles.slice(0,3)};
  const post=d=>({title:`Dev digest · ${d.date}`,url:`/en/digest/${d.date}/`,description:d.articles[0].editions.en.summary,publishedAt:d.publishedAt,updatedAt:d.updatedAt,digest:{data:d}});
  for(const lang of ['en','ko']){
    const before=renderFeed([post(prior)],lang,new URL('https://youdozi.github.io/'),'Blog');
    const after=renderFeed([post(data)],lang,new URL('https://youdozi.github.io/'),'Blog');
    assert.notEqual(before,after);
    assert.equal(before.match(/<guid[^>]*>.*?<\/guid>/)[0],after.match(/<guid[^>]*>.*?<\/guid>/)[0]);
    assert.equal(before.match(/<pubDate>.*?<\/pubDate>/)[0],after.match(/<pubDate>.*?<\/pubDate>/)[0]);
    assert.ok(after.includes(data.updatedAt.toISOString()));
    assert.match(after,/<lastBuildDate>/);assert.match(after,/<content:encoded>/);
    for(const article of data.articles)assert.ok(after.includes(article.editions[lang].title.replaceAll('&','&amp;').replaceAll("'",'&apos;')));
  }
  const unsafe=structuredClone(data);unsafe.articles[0].editions.en.title='<img src=x onerror=alert(1)> &';
  const feed=renderFeed([post(unsafe)],'en',new URL('https://youdozi.github.io/'),'Blog');
  assert.ok(!feed.includes('<img'));assert.ok(feed.includes('&amp;lt;img'));
});

test('main protection requires Actions checks and PRs without granting bots a bypass', async () => {
  const protection=JSON.parse(await readFile('.github/main-protection.json','utf8'));
  const reviews=JSON.parse(await readFile('.github/main-review-ruleset.json','utf8'));
  assert.equal(protection.enforce_admins,true);
  assert.equal(protection.required_status_checks.strict,true);
  assert.deepEqual(protection.required_status_checks.checks,[{context:'build / build',app_id:15368}]);
  assert.ok(protection.required_pull_request_reviews);
  assert.equal(protection.allow_force_pushes,false);assert.equal(protection.allow_deletions,false);
  assert.equal(reviews.rules[0].parameters.required_approving_review_count,1);
  assert.equal(reviews.rules[0].parameters.dismiss_stale_reviews_on_push,true);
  assert.deepEqual(reviews.bypass_actors,[{actor_type:'RepositoryRole',actor_id:5,bypass_mode:'pull_request'}]);
});


test('archive schema accepts explicit legacy and stable extractor versions only', async () => {
  const {renewalSchema} = await import('../src/lib/renewal-schema.ts');
  const files = await readdir('src/content/renewals');
  const original = JSON.parse(await readFile(`src/content/renewals/${files[0]}`, 'utf8'));
  for (const version of ['article-parser-v1', 'article-parser-v2']) {
    const value = structuredClone(original);
    value.documents[0].extractorVersion = version;
    assert.equal(renewalSchema.safeParse(value).success, true);
  }
  original.documents[0].extractorVersion = 'unknown-extractor';
  assert.equal(renewalSchema.safeParse(original).success, false);
});
