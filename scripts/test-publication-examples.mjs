import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, mkdtemp, writeFile, symlink, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const examples = [
  ['2026-04-07-jekyll-github-actions-content-pipeline', 'review-contract.mjs', '5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.'],
  ['2026-04-07-jekyll-quality-gates-proof-html-bundler-audit', 'deploy-contract.mjs', '24 policy-model combinations and 6 rejected workflow mutations passed.'],
];
for (const [key, file, output] of examples) {
  test(`documented ${file} agrees across editions and executes its workflow contracts`, async () => {
    const paired = [];
    for (const lang of ['en', 'ko']) {
      const source = await readFile(`src/content/posts/${lang}/${key}.md`, 'utf8');
      const blocks = [...source.matchAll(/^### `([^`]+)`\n\n```javascript\n([\s\S]*?)\n```/gm)];
      assert.equal(blocks.length, 1, `${lang}: one complete named JavaScript file`);
      assert.equal(blocks[0][1], file);
      paired.push(blocks[0][2]);
    }
    assert.equal(paired[0], paired[1], 'Both editions must execute the same example');
    const directory = await mkdtemp(join(tmpdir(), 'youdozi-publication-example-'));
    try {
      await symlink(resolve('node_modules'), join(directory, 'node_modules'), 'dir');
      const path = join(directory, file);
      await writeFile(path, paired[0]);
      const result = spawnSync(process.execPath, [path], {encoding:'utf8',timeout:20000});
      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.equal(result.stdout.trim(), output);
    } finally { await rm(directory, {recursive:true,force:true}); }
  });
}
