import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import YAML from 'yaml';

export function convertPost(source, filename) {
  const match = source.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
  if (!match) throw new Error(`Missing front matter: ${filename}`);
  const data = YAML.parse(match[1]);
  const day = path.basename(filename).slice(0, 10);
  const slug = path.basename(filename).replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.(markdown|md)$/, '');
  const categories = (Array.isArray(data.categories) ? data.categories : [data.categories]).filter(Boolean).map(String);
  const rawDate = String(data.date || `${day} 00:00:00 +0900`).trim();
  const publishedAt = new Date(rawDate.replace(/^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{2})(\d{2})$/, '$1T$2$3:$4')).toISOString();
  const digest = slug === 'dev-digest';
  const metadata = {
    title: data.title, language: 'ko', translationKey: digest ? `digest-${day}` : `${day}-${slug}`,
    routeSlug: digest ? day : `${day}-${slug}`, kind: digest ? 'digest' : 'post', publishedAt,
    categories, tags: (Array.isArray(data.tags) ? data.tags : [data.tags]).filter(Boolean).map(String),
    legacyUrl: `/${[...categories, slug].join('/')}/`,
    ...(data.excerpt ? { description: data.excerpt } : {}),
    ...(data.header?.teaser ? { image: data.header.teaser } : {}),
    legacySource: filename,
  };
  // Only convert prose; shell/code examples must survive byte-for-byte.
  let fenced = false;
  const body = match[2].split('\n').map(line => {
    if (/^\s*(```|~~~)/.test(line)) { fenced = !fenced; return line; }
    if (fenced) return line;
    if (/multiple-gradle-build|parse-yaml/.test(filename)) {
      line = line.replace(/\[([^\]]+)\]\(\.[^)]*\)/g, '`$1`');
    }
    line = line.replace('](springboot/springboot-intellij-import/)', '](/ko/posts/2023-09-10-springboot-intellij-import/)');
    return line.replace(/\{:[^}\n]*\}/g, '')
      .replace(/(!\[[^\]]*\]\()([^\n]*?)(\))/g, (_, start, url, end) => start + url.replace(/ /g, '%20') + end);
  }).join('\n');
  return { metadata, body, text: `---\n${YAML.stringify(metadata, { defaultStringType: 'QUOTE_DOUBLE', defaultKeyType: 'PLAIN' })}---\n${body}` };
}

async function walk(dir) {
  const result = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...await walk(file));
    else if (/\.(md|markdown)$/.test(file)) result.push(file);
  }
  return result;
}
if (process.argv[1]?.endsWith('migrate-jekyll.mjs')) {
  await mkdir('src/content/posts/ko', { recursive: true });
  for (const file of await walk('_posts')) {
    const post = convertPost(await readFile(file, 'utf8'), file);
    const target = `src/content/posts/ko/${post.metadata.translationKey}.md`;
    // Rerunning migration must not overwrite later editorial changes.
    try { await readFile(target); throw new Error(`Already migrated: ${target}`); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    await writeFile(target, post.text);
  }
  console.log('Migrated the Jekyll archive to Korean content.');
}
