import {prepareTechnicalAssets} from './technical-publication.mjs';
import { execFileSync } from 'node:child_process';
import { cp, mkdir, readdir, writeFile } from 'node:fs/promises';
await mkdir('public/assets', { recursive: true });
await cp('assets/img', 'public/assets/img', { recursive: true });
for (const file of await readdir('.')) {
  if (/^(google|naver)[a-z0-9]+\.html$/.test(file)) await cp(file, `public/${file}`);
}
await writeFile('public/.nojekyll', '');

// Both normal builds and integration fixtures prepare the same generated assets.
execFileSync('python3', ['-B', 'scripts/build_example_archives.py'], { stdio: 'inherit' });
execFileSync('python3', ['-B', 'scripts/build_algorithm_diagrams.py'], { stdio: 'inherit' });

console.log(`[ok] ${await prepareTechnicalAssets()} approved technical diagram assets prepared`);
