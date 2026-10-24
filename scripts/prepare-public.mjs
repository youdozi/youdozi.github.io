import { cp, mkdir, readdir, writeFile } from 'node:fs/promises';
await mkdir('public/assets', { recursive: true });
await cp('assets/img', 'public/assets/img', { recursive: true });
for (const file of await readdir('.')) {
  if (/^(google|naver)[a-z0-9]+\.html$/.test(file)) await cp(file, `public/${file}`);
}
await writeFile('public/.nojekyll', '');
