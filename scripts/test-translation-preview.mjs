import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm,lstat,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fixturePlan,stageFixtures,withSnapshot,fingerprint,checks} from './translation-preview.mjs';

const id='a'.repeat(16),key=`es-${id}`;
const item=()=>({key,status:'awaiting-approval',publicationFile:`src/content/translations/${key}.json`,draft:{language:'es',renewalId:id,state:'draft',edition:{title:'Fixture',claims:['One','Two'],followUp:[]}}});
const report=edition=>({summary:{blocked:0},editions:[edition]});
async function project(work){
  const base=await mkdtemp(join(tmpdir(),'translation-preview-contract-'));
  try{
    await mkdir(join(base,'src/content/translations'),{recursive:true});
    await mkdir(join(base,'node_modules'));
    await mkdir(join(base,'.pipeline/translations/releases'),{recursive:true});
    await mkdir(join(base,'dist'));
    await writeFile(join(base,'.gitignore'),'node_modules/\ndist/\n');
    await writeFile(join(base,'src/content/translations/keep.json'),'committed publication');
    await writeFile(join(base,'.pipeline/translations/releases/keep.json'),'approval pending');
    await writeFile(join(base,'dist/index.html'),'real public output');
    execFileSync('git',['init','-q'],{cwd:base});execFileSync('git',['add','.'],{cwd:base});
    execFileSync('git',['-c','user.name=Preview contract','-c','user.email=preview@example.invalid','commit','-qm','fixture'],{cwd:base});
    await work(base);
  }finally{await rm(base,{recursive:true,force:true});}
}

test('preview fixture metadata explicitly denies real human approval and never changes the draft',()=>{
  const edition=item(),before=structuredClone(edition);
  const plan=fixturePlan([report(edition)],'2026-10-01T00:00:00Z');
  assert.deepEqual(edition,before);
  assert.equal(plan.records.length,1);
  assert.match(plan.records[0].data.approval.reviewedBy,/NOT_HUMAN_APPROVAL/);
  assert.match(plan.records[0].data.approval.basis,/NOT a user publication approval/);
  assert.equal(plan.records[0].data.approval.pullRequest,Number.MAX_SAFE_INTEGER);
  assert.equal(plan.records[0].data.publishedAt,'2026-10-01T00:00:00Z');
});

test('blocked, duplicate, changed identity or destination abort before any fixtures exist',()=>{
  assert.throws(()=>fixturePlan([{summary:{blocked:1},editions:[item()]}]),/blocked/);
  assert.throws(()=>fixturePlan([report(item()),report(item())]),/Duplicate/);
  for(const mutate of [e=>e.status='blocked',e=>e.publicationFile='../outside.json',e=>e.key='different',e=>delete e.draft]){
    const edition=item();mutate(edition);assert.throws(()=>fixturePlan([report(edition)]),/Invalid/);
  }
});

test('already published editions are skipped and are never overwritten',()=>{
  const edition=item();edition.status='already-published';
  assert.deepEqual(fixturePlan([report(edition)]),{records:[],alreadyPublished:1});
});

test('snapshot uses committed files, ignores untracked drafts and preserves normal output',async()=>{
  await project(async base=>{
    await writeFile(join(base,'user-untracked-draft.json'),'user draft');
    await writeFile(join(base,'src/content/translations/keep.json'),'uncommitted user edit');
    const before=await fingerprint(base,['src/content','.pipeline/translations','dist']);let captured;
    const result=await withSnapshot(base,async(sandbox,commit)=>{
      captured=sandbox;
      assert.match(commit,/^[a-f0-9]{40}$/);
      assert.equal(await readFile(join(sandbox,'src/content/translations/keep.json'),'utf8'),'committed publication');
      await assert.rejects(lstat(join(sandbox,'user-untracked-draft.json')),{code:'ENOENT'});
      assert.equal((await lstat(join(sandbox,'node_modules'))).isSymbolicLink(),true);
      await stageFixtures(sandbox,base,fixturePlan([report(item())]).records,data=>data);
      assert.equal(JSON.parse(await readFile(join(sandbox,`src/content/translations/${key}.json`),'utf8')).approval.reviewedBy,'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL');
      return {checked:true};
    });
    assert.equal(result.fixtureOnly,true);assert.equal(result.checked,true);
    await assert.rejects(lstat(captured),{code:'ENOENT'});
    assert.equal(await fingerprint(base,['src/content','.pipeline/translations','dist']),before);
    assert.equal(await readFile(join(base,'user-untracked-draft.json'),'utf8'),'user draft');
  });
});

test('snapshot and staged files are removed when validation or rendering fails',async()=>{
  await project(async base=>{
    let captured;
    await assert.rejects(withSnapshot(base,async sandbox=>{
      captured=sandbox;
      await stageFixtures(sandbox,base,fixturePlan([report(item())]).records,data=>data);
      throw new Error('Render contract failure');
    }),/Render contract failure/);
    await assert.rejects(lstat(captured),{code:'ENOENT'});
    await assert.rejects(lstat(join(base,`src/content/translations/${key}.json`)),{code:'ENOENT'});
  });
});

test('root preservation detects concurrent changes without discarding user edits',async()=>{
  await project(async base=>{
    await assert.rejects(withSnapshot(base,async()=>{
      await writeFile(join(base,'src/content/translations/keep.json'),'concurrent user edit');
      return {};
    }),/Protected working inputs\/output changed/);
    assert.equal(await readFile(join(base,'src/content/translations/keep.json'),'utf8'),'concurrent user edit');
  });
});

test('staging refuses the working checkout, missing marker, invalid paths and symlinked content',async()=>{
  await project(async base=>{
    await assert.rejects(stageFixtures(base,base,[],data=>data),/outside/);
    await withSnapshot(base,async sandbox=>{
      const marker=join(sandbox,'.translation-preview-fixture.json');
      const saved=await readFile(marker);
      await writeFile(marker,'{}');
      await assert.rejects(stageFixtures(sandbox,base,[],data=>data),/marker/);
      await writeFile(marker,saved);
      await assert.rejects(stageFixtures(sandbox,base,[{path:'../escape.json',data:{}}],data=>data),/destination/);
      await rm(join(sandbox,'src/content/translations'),{recursive:true});
      await symlink(join(base,'src/content/translations'),join(sandbox,'src/content/translations'),'dir');
      await assert.rejects(stageFixtures(sandbox,base,[],data=>data),/symlink/);
      return {};
    });
  });
});

test('fixture validation rejects all records before writing and refuses existing files',async()=>{
  await project(async base=>{
    await withSnapshot(base,async sandbox=>{
      const plan=fixturePlan([report(item())]);
      await assert.rejects(stageFixtures(sandbox,base,plan.records,()=>{throw new Error('Schema failed');}),/Schema failed/);
      await assert.rejects(lstat(join(sandbox,plan.records[0].path)),{code:'ENOENT'});
      await stageFixtures(sandbox,base,plan.records,data=>data);
      const before=await readFile(join(sandbox,plan.records[0].path));
      await assert.rejects(stageFixtures(sandbox,base,plan.records,data=>data),{code:'EEXIST'});
      assert.deepEqual(await readFile(join(sandbox,plan.records[0].path)),before);
      return {};
    });
  });
});

test('preview commands cannot submit IndexNow or publish and include reader/SEO/discovery gates',()=>{
  const commands=JSON.stringify(checks);
  assert.ok(!/indexnow|--submit|publish|deploy|npm/.test(commands));
  for(const name of ['check_site.py','check_seo.py','check_migration.py','check_metadata.py','check_listing_metadata.py','check_learning_paths.py','check_discovery.py','check_reader_content.py','check_article_images.py'])assert.ok(commands.includes(name));
});

test('CI previews before uploading normal dist and package separates preview from normal build',async()=>{
  const config=await readFile(new URL('../.github/workflows/site-checks.yml',import.meta.url),'utf8');
  const preview=config.indexOf('npm run check:translation-preview');
  assert.ok(preview>config.indexOf('run: npm run build'));
  assert.ok(preview<config.indexOf('uses: actions/upload-artifact'));
  const {scripts}=JSON.parse(await readFile(new URL('../package.json',import.meta.url),'utf8'));
  assert.equal(scripts['check:translation-preview'],'node scripts/translation-preview.mjs');
  assert.ok(!scripts.build.includes('translation-preview'));
  assert.ok(scripts.build.includes('scripts/check_migration.py'));
  assert.ok(scripts.build.includes('scripts/check_learning_paths.py'));
  assert.ok(scripts.test.includes('scripts/test-translation-preview.mjs'));
});
