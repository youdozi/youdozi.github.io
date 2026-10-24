import { createHash } from 'node:crypto';
import { getCollection, type CollectionEntry } from 'astro:content';
export const languages = ['en', 'ko'] as const;
export type Language = typeof languages[number];
export const SITE = "youdozi's memory";
export type Entry = {
  title: string; language: Language; translationKey: string; slug: string; kind: 'post' | 'digest';
  publishedAt: Date; updatedAt?: Date; categories: string[]; tags: string[]; description: string; url: string;
  reviewStatus?: 'revised' | 'source-audited' | 'example';
  legacyUrl?: string; legacySource?: string; post?: CollectionEntry<'posts'>; digest?: CollectionEntry<'digests'>;
};
export const text = {
  en: { home: 'Home', posts: 'Writing', digest: 'Dev digest', categories: 'Categories', tags: 'Topics', search: 'Search', all: 'All writing', read: 'Read article', recent: 'Latest entries', empty: 'No entries in English yet.', archive: 'Explore the Korean archive', language: 'Language', about: 'Practical notes on Java, Spring, testing, and software engineering, with working examples and source references.', scope: 'AI summaries checked against source quotations and context. This is not a guarantee of factual accuracy.', source: 'Read source', published: 'Published', related: 'More to read', results: 'Search articles', searchHint: 'Search titles, topics, and article text', noResults: 'No matching articles.', footer: 'A developer’s working memory.', digestDescription: 'Development news and source links.', overview: 'Writing & development news', old: 'This entry is part of the original archive. The source descriptions may be in English.', notTranslated: 'English translation is not available for this entry.' },
  ko: { home: '홈', posts: '개발 기록', digest: '개발 다이제스트', categories: '카테고리', tags: '주제', search: '검색', all: '전체 글', read: '글 읽기', recent: '최근 기록', empty: '아직 게시글이 없습니다.', archive: '한국어 아카이브 보기', language: '언어', about: 'Java와 소프트웨어, 개발하며 배운 것들을 기록합니다.', scope: 'AI 요약의 원문 인용과 문맥 일치를 확인했습니다. 사실의 진위를 보장하지 않습니다.', source: '원문 읽기', published: '발행일', related: '함께 읽을 글', results: '게시글 검색', searchHint: '제목, 주제, 본문으로 검색', noResults: '검색 결과가 없습니다.', footer: '개발하며 쌓아가는 기억.', digestDescription: '출처 링크와 함께 모아둔 개발 뉴스입니다.', overview: '개발 기록과 기술 뉴스', old: '기존 아카이브 글입니다. 수집 당시의 영문 설명이 포함될 수 있습니다.', notTranslated: '이 글의 영문 번역은 아직 없습니다.' },
};
let cache: Promise<Entry[]> | undefined;
export async function entries(includeExamples = false): Promise<Entry[]> {
  const all = await (cache ??= (async () => {
    const result: Entry[] = [];
    const digests = await getCollection('digests');
    const digestKeys = new Set(digests.map(d => `digest-${d.data.date}`));
    for (const post of await getCollection('posts')) {
      const d = post.data;
      if (d.publishedAt > new Date() || digestKeys.has(d.translationKey)) continue;
      const url = d.kind === 'digest' ? `/${d.language}/digest/${d.routeSlug}/` : `/${d.language}/posts/${d.routeSlug}/`;
      result.push({ ...d, slug: d.routeSlug, description: d.description || (d.kind === 'digest' ? ((post.body || '').match(/^- (?:한국어 AI 요약|출처 제공 설명|한줄 요약): (.+)$/m)?.[1]?.slice(0, 180) || text[d.language].digestDescription) : (post.body || '').replace(/```[\s\S]*?```/g, '').replace(/<[^>]*>|[#*`\[\]]/g, '').replace(/\s+/g, ' ').trim().slice(0, 180)), url, post });
    }
    for (const digest of digests) {
      const d = digest.data;
      if (d.publishedAt > new Date()) continue;
      for (const language of languages) {
        result.push({ title: language === 'en' ? `Dev digest · ${d.date}` : `개발 다이제스트 · ${d.date}`, language, translationKey: `digest-${d.date}`, slug: d.date, kind: 'digest', publishedAt: d.publishedAt, categories: ['dev', 'digest'], tags: [...new Set(d.articles.flatMap(a => a.tags))], description: d.articles[0].editions[language].summary, url: `/${language}/digest/${d.date}/`, digest });
      }
    }
    const urls = new Set<string>();
    const translations = new Set<string>();
    for (const entry of result) {
      const key = `${entry.language}:${entry.translationKey}`;
      if (urls.has(entry.url) || translations.has(key)) throw new Error(`Duplicate content route or translation: ${entry.url}`);
      urls.add(entry.url); translations.add(key);
    }
    return result.sort((a,b) => b.publishedAt.getTime() - a.publishedAt.getTime());
  })());
  return includeExamples ? all : all.filter(entry => entry.reviewStatus !== 'example');
}
export function formatDate(date: Date, lang: Language) {
  return new Intl.DateTimeFormat(lang === 'en' ? 'en-US' : 'ko-KR', { dateStyle: 'medium', timeZone: 'Asia/Seoul' }).format(date);
}
export function taxonomySlug(value: string) {
  const readable = value.normalize('NFKC').toLocaleLowerCase('en-US').replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'topic';
  // Retain distinct tags such as SpringBoot/springboot and C++/C#.
  return readable === value ? readable : `${readable}-${createHash('sha256').update(value).digest('hex').slice(0, 10)}`;
}
export function taxonomyUrl(lang: Language, kind: 'tags' | 'categories', value: string) {
  return `/${lang}/${kind}/${encodeURIComponent(taxonomySlug(value))}/`;
}
export function alternateLinks(entry: Entry, all: Entry[]) {
  return all.filter(e => e.translationKey === entry.translationKey).map(e => ({ language: e.language, url: e.url }));
}
