export type SearchItem = { title: string; url: string; description: string; content: string; tags: string[] };
type IndexedItem = { item: SearchItem; title: string; tags: string; description: string; content: string; position: number };

// Preserve Hangul, Cyrillic and kana marks; fold accents only on Latin letters.
export function normalizeSearch(value: string): string {
  return value.normalize('NFKC').toLowerCase()
    .replace(/\p{Script=Latin}\p{M}*/gu, letter => letter.normalize('NFD').replace(/\p{M}/gu, ''));
}

export function prepareSearch(items: SearchItem[]): IndexedItem[] {
  return items.map((item, position) => ({ item, position,
    title: normalizeSearch(item.title), tags: normalizeSearch(item.tags.join(' ')),
    description: normalizeSearch(item.description), content: normalizeSearch(item.content),
  }));
}

export function searchItems(index: IndexedItem[], query: string, limit = 50): { items: SearchItem[]; total: number } {
  const terms = [...new Set(normalizeSearch(query).trim().split(/\s+/).filter(Boolean))];
  const phrase = terms.join(' ');
  if (!terms.length) return { items: [], total: 0 };
  const matches: { entry: IndexedItem; score: number }[] = [];
  for (const entry of index) {
    let score = entry.title === phrase ? 200 : entry.title.includes(phrase) ? 80 : 0;
    let matched = true;
    for (const term of terms) {
      const weight = entry.title.includes(term) ? 12 : entry.tags.includes(term) ? 8
        : entry.description.includes(term) ? 4 : entry.content.includes(term) ? 1 : 0;
      if (!weight) { matched = false; break; }
      score += weight;
    }
    if (matched) matches.push({ entry, score });
  }
  matches.sort((a, b) => b.score - a.score || a.entry.position - b.entry.position);
  return { items: matches.slice(0, limit).map(match => match.entry.item), total: matches.length };
}
