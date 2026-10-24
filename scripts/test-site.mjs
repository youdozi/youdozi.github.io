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
    const original = await readFile(data.legacySource,'utf8');
    const expected = convertPost(original, data.legacySource);
    if (data.reviewedAt) {
      assert.equal(data.archiveBodySha256, createHash('sha256').update(expected.body).digest('hex'), data.legacySource);
      assert.ok(data.reviewScope && data.reviewSources.length > 0, data.legacySource);
      assert.ok(body.trim().length > 0);
    } else assert.equal(body, expected.body, data.legacySource);
    assert.equal(data.routeSlug, expected.metadata.routeSlug);
    assert.equal(data.language, 'ko');
    assert.equal(typeof data.routeSlug, 'string');
    const route = `/ko/${data.kind === 'digest' ? 'digest' : 'posts'}/${data.routeSlug}/`;
    assert.ok(!routes.has(route), `duplicate ${route}`); routes.add(route);
    assert.ok(!sources.has(data.legacySource)); sources.add(data.legacySource);
    assert.ok(!translations.has(data.translationKey)); translations.add(data.translationKey);
  }
  async function originals(dir) { return (await Promise.all((await readdir(dir,{withFileTypes:true})).map(e => e.isDirectory() ? originals(`${dir}/${e.name}`) : Promise.resolve(e.name.endsWith('.markdown') ? 1 : 0)))).reduce((a,b)=>a+b,0); }
  assert.equal(files.length, await originals('_posts'));
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

test('workflow YAML parses and automated publication builds the exact generated commit', async () => {
  const pipeline = YAML.parse(await readFile('.github/workflows/dev-content-pipeline.yml','utf8'));
  assert.equal(pipeline.jobs.publish.uses,'./.github/workflows/site-quality-gates.yml');
  assert.equal(pipeline.jobs.publish.with.ref,'${{ needs.generate.outputs.commit_sha }}');
  const site = YAML.parse(await readFile('.github/workflows/site-quality-gates.yml','utf8'));
  assert.ok(site.on.workflow_call);
  assert.equal(site.jobs.build.steps[0].with.ref,'${{ inputs.ref || github.sha }}');
  assert.ok(site.jobs.deploy.steps.some(s=>s.uses==='actions/deploy-pages@v4'));
});

test('Astro renders paired editions, reciprocal language links, and escapes source titles', async () => {
  const { writeFile, unlink } = await import('node:fs/promises');
  const { spawnSync } = await import('node:child_process');
  const result = spawnSync('python3', ['-B', '-c', "import sys,json;sys.path.insert(0,'scripts');from test_bilingual_digest import article;a=article();a['publishedAt']='2000-01-01T00:00:00+09:00';a['editions']['en']['title']='Literal {{ 7 | times: 7 }} <script>alert(1)</script>';print(json.dumps({'date':'2000-01-01','publishedAt':'2000-01-01T01:00:00+09:00','articles':[a]}))"], {encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);
  const fixture='src/content/digests/2000-01-01.json';
  try {
    await writeFile(fixture,result.stdout,{flag:'wx'});
    const build=spawnSync(process.execPath,['node_modules/astro/bin/astro.mjs','build'],{encoding:'utf8',maxBuffer:8*1024*1024});
    assert.equal(build.status,0,build.stderr);
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
    assert.match(en,/Source evidence/);assert.match(ko,/원문 인용 근거/);
    const englishIndex=JSON.parse(await readFile('dist/en/search-index.json','utf8'));
    assert.ok(englishIndex.some(entry => entry.url === '/en/digest/2000-01-01/'));
    assert.ok(englishIndex.some(entry => entry.url === '/en/posts/2023-09-19-springboot-test-webclient/'));
    const koreanIndex=JSON.parse(await readFile('dist/ko/search-index.json','utf8'));
    assert.ok(!koreanIndex.some(entry=>entry.url==='/ko/digest/2026-03-16/'));
    const sample=await readFile('dist/ko/digest/2026-03-16/index.html','utf8');
    assert.match(sample,/noindex,follow/);assert.match(sample,/예제 데이터/);
    const sitemap=await readFile('dist/sitemap.xml','utf8');
    assert.ok(!sitemap.includes('/ko/digest/2026-03-16/'));
    const englishArticle=await readFile('dist/en/posts/2023-09-19-springboot-test-webclient/index.html','utf8');
    assert.match(englishArticle,/<html lang="en">/);
    assert.match(englishArticle,/rel="canonical" href="https:\/\/youdozi.github.io\/en\/posts\/2023-09-19-springboot-test-webclient\/"/);
    assert.match(englishArticle,/hreflang="ko" href="https:\/\/youdozi.github.io\/ko\/posts\/2023-09-19-springboot-test-webclient\/"/);
    const graph=JSON.parse(englishArticle.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
    const posting=graph.find(item=>item['@type']==='BlogPosting');
    assert.equal(posting.inLanguage,'en');assert.equal(posting.author.name,'youdozi');
    assert.ok(posting.datePublished && posting.dateModified);
    assert.ok(graph.some(item=>item['@type']==='BreadcrumbList'));


    const tags=await readFile('dist/ko/tags/index.html','utf8');
    const upper=tags.match(/href="([^"]+)"[^>]*>SpringBoot /)?.[1];
    const lower=tags.match(/href="([^"]+)"[^>]*>springboot /)?.[1];
    assert.ok(upper && lower);assert.notEqual(upper,lower);
    assert.ok((await readFile(`dist${decodeURIComponent(upper)}index.html`,'utf8')).includes('Gradle'));

  } finally {
    await unlink(fixture);
  }
});
