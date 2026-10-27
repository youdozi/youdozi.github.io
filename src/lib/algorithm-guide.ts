import type { Entry, Language } from './content';

const groups = [
  { id: 'arrays', keys: ['2021-07-22-plus-minus', '2021-07-22-dot-product', '2021-07-29-interval-num'] },
  { id: 'strings', keys: ['2021-07-23-number-word', '2021-07-19-new-id', '2021-07-20-pair-delete'] },
  { id: 'collections', keys: ['2021-07-23-unsuccessful-runner', '2021-07-29-ponkemon', '2021-08-17-cache', '2021-07-24-fail-percentage'] },
] as const;

const copy = {
  en: {
    label: 'Java coding exercises', title: 'Java Coding Exercises: Arrays, Strings and Collections',
    description: 'Learn Java problem-solving through exercises on arrays, strings, stacks, maps, sets, caching, and sorting, with complete code and input bounds.',
    intro: 'Start with a calculation, then follow how the problem changes the state you need to retain. Each core exercise includes a complete Java solution, its input contract, and the reasoning behind the algorithm.',
    extra: 'More exercises', home: 'Home', categories: 'Categories',
    groups: {
      arrays: { title: 'Arrays and numeric bounds', description: 'Apply signs and match indices before choosing int or long. Continue with a sequence whose products exceed int.' },
      strings: { title: 'Strings and ordered transformations', description: 'Choose literal replacement for digit words, preserve normalization order, then use a stack for adjacent-pair removal.' },
      collections: { title: 'Counts, state and ordering', description: 'Distinguish name frequencies from distinct types. Then track cache recency and rank ratios with an explicit tie-break.' },
    },
  },
  ko: {
    label: 'Java 코딩 문제 풀이', title: 'Java 코딩테스트 풀이: 배열·문자열·컬렉션',
    description: '배열 계산부터 문자열·스택·맵·집합·LRU·정렬까지 Java 문제 풀이를 이어 읽습니다. 전체 코드와 입력 범위, 알고리즘의 판단 근거를 함께 확인하세요.',
    intro: '계산부터 시작해 문제에 따라 어떤 상태를 남겨야 하는지 살펴봅니다. 핵심 풀이마다 전체 Java 코드, 입력 조건과 알고리즘의 판단 근거를 제공합니다.',
    extra: '다른 문제 풀이', home: '홈', categories: '카테고리',
    groups: {
      arrays: { title: '배열 계산과 수치 범위', description: '부호와 인덱스의 대응을 확인하고 int·long을 선택합니다. 곱셈 결과가 int를 넘는 수열로 이어집니다.' },
      strings: { title: '문자열과 변환 순서', description: '영단어에는 리터럴 치환을, 아이디에는 순서가 있는 정규화를 적용합니다. 인접 쌍 제거에서는 스택에 남길 상태를 생각합니다.' },
      collections: { title: '빈도·상태·정렬', description: '이름별 인원수와 종류 수를 구분한 뒤 캐시의 최근 접근 순서를 추적합니다. 비율 정렬에서는 분모와 동률 기준을 함께 확인합니다.' },
    },
  },
};

function eligible(all: Entry[], lang: Language): Entry[] {
  const now = Date.now();
  return all.filter(entry => entry.language === lang && entry.kind === 'post' &&
    entry.categories.includes('coding-test') && entry.reviewStatus !== 'example' && entry.publishedAt.getTime() <= now);
}

export function algorithmCategoryLabel(lang: Language): string | undefined {
  return lang === 'en' || lang === 'ko' ? copy[lang].label : undefined;
}

export function algorithmCategoryAlternates(all: Entry[]) {
  return (['en', 'ko'] as const).filter(lang => eligible(all, lang).length > 0)
    .map(language => ({ language, url: `/${language}/categories/coding-test/` }));
}

export function algorithmGuide(lang: Language, all: Entry[]) {
  if (lang !== 'en' && lang !== 'ko') return undefined;
  const items = eligible(all, lang);
  if (!items.length) return undefined;
  const byKey = new Map(items.map(entry => [entry.translationKey, entry]));
  let position = 1;
  const sections = groups.map(group => {
    const entries = group.keys.flatMap(key => byKey.has(key) ? [byKey.get(key)!] : []);
    const start = position;
    position += entries.length;
    return { id: group.id, ...copy[lang].groups[group.id], entries, start };
  }).filter(group => group.entries.length > 0);
  const curated = new Set(sections.flatMap(group => group.entries.map(entry => entry.translationKey)));
  const extras = items.filter(entry => !curated.has(entry.translationKey));
  const ordered = [...sections.flatMap(group => group.entries), ...extras];
  const updatedAt = new Date(Math.max(Date.parse('2026-10-27T00:00:00Z'),
    ...ordered.map(entry => (entry.updatedAt || entry.publishedAt).getTime())));
  return { ...copy[lang], lang, url: `/${lang}/categories/coding-test/`, sections, extras, ordered, updatedAt };
}

export type AlgorithmGuide = NonNullable<ReturnType<typeof algorithmGuide>>;

export function algorithmStructuredData(guide: AlgorithmGuide, site: URL): Record<string, unknown>[] {
  const url = new URL(guide.url, site).href;
  const listId = `${url}#exercises`;
  return [
    { '@context': 'https://schema.org', '@type': 'CollectionPage', '@id': `${url}#collection`,
      url, name: guide.title, description: guide.description, inLanguage: guide.lang,
      dateModified: guide.updatedAt.toISOString(), mainEntity: { '@id': listId } },
    { '@context': 'https://schema.org', '@type': 'ItemList', '@id': listId,
      numberOfItems: guide.ordered.length, itemListElement: guide.ordered.map((entry, index) => ({
        '@type': 'ListItem', position: index + 1, name: entry.title, url: new URL(entry.url, site).href,
      })) },
    { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [
      { '@type': 'ListItem', position: 1, name: guide.home, item: new URL(`/${guide.lang}/`, site).href },
      { '@type': 'ListItem', position: 2, name: guide.categories, item: new URL(`/${guide.lang}/categories/`, site).href },
      { '@type': 'ListItem', position: 3, name: guide.label, item: url },
    ] },
  ];
}
