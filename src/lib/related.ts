import type { Entry } from './content';

// Navigation and workflow labels do not establish a topical relationship.
const generic = new Set(['archive-renewal', 'dev', 'digest', 'blog', 'post', 'posts', 'news', 'development']);
function normalize(value: string): string {
  const key = value.normalize('NFKC').toLowerCase().trim();
  return ({ springboot: 'spring', 'spring-boot': 'spring', tests: 'testing', test: 'testing' } as Record<string, string>)[key] || key;
}
function terms(values: string[]): Set<string> {
  return new Set(values.map(normalize).filter(value => value && !generic.has(value)));
}

// Match named technologies, not arbitrary words such as "release" or "review".
// Approved English source titles give translated renewals the same topic signals.
const topics: [RegExp, number, 'vendor'?][] = [
  [/\b(?:spring(?:boot)?|webclient|webflux)\b/iu, 6],
  [/\b(?:java|jdk|jvm|kotlin|gradle)\b/iu, 4],
  [/\b(?:junit|mockwebserver|testing|tests?)\b/iu, 3],
  [/\b(?:security|vulnerabilit(?:y|ies)|cve|waf|codeql|dependabot|authorization|authentication|advisories)\b|보안/iu, 2],
  [/\bcloudflare\b/iu, 6, 'vendor'],
  [/\b(?:github|codeql|dependabot)\b/iu, 5, 'vendor'],
  [/\bcopilot\b/iu, 6],
  [/\b(?:kubernetes|k8s)\b/iu, 6],
  [/\b(?:aws|amazon web services)\b/iu, 6, 'vendor'],
  [/\b(?:postgresql|mysql|database|databases)\b|데이터베이스/iu, 4],
];
// A shared vendor alone is too broad (e.g. code scanning vs model retirement).
function signals(entry: Entry) {
  const sourceTitles = entry.renewal?.data.editions.en.title ||
    entry.digest?.data.articles.map(article => article.editions.en.title).join(' ') || '';
  const title = [entry.title, sourceTitles, ...entry.tags, ...entry.categories].join(' ');
  return { tags: terms(entry.tags), categories: terms(entry.categories), topics: topics.map(([pattern]) => pattern.test(title)) };
}

export function relatedEntries(entry: Entry, all: Entry[], limit = 3): Entry[] {
  if (limit <= 0) return [];
  const target = signals(entry);
  const seen = new Set<string>();
  return all.filter(candidate => {
    if (candidate.language !== entry.language || candidate.translationKey === entry.translationKey ||
        candidate.reviewStatus === 'example' || seen.has(candidate.translationKey)) return false;
    seen.add(candidate.translationKey);
    return true;
  }).map(candidate => {
    const other = signals(candidate);
    const sharedTags = [...target.tags].filter(tag => other.tags.has(tag)).length;
    const sharedCategories = [...target.categories].filter(category => other.categories.has(category)).length;
    const topicScore = topics.reduce((sum, [, weight], index) => sum + (target.topics[index] && other.topics[index] ? weight : 0), 0);
    const hasTopic = target.topics.some((matched, index) => matched && other.topics[index] && topics[index][2] !== 'vendor');
    return { candidate, score: sharedTags || sharedCategories || hasTopic ? sharedTags * 8 + sharedCategories * 2 + topicScore : 0 };
  }).filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || b.candidate.publishedAt.getTime() - a.candidate.publishedAt.getTime() || a.candidate.url.localeCompare(b.candidate.url, 'en'))
    .slice(0, Math.floor(limit)).map(({ candidate }) => candidate);
}
