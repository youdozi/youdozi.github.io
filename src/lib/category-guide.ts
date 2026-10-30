import type { Entry, Language } from './content';

export interface CategoryGuide {
  label: string; title: string; description: string; intro: string;
  extra: string; home: string; categories: string;
  lang: Language; url: string; updatedAt: Date;
  eyebrow?: string; listAnchor?: string;
  sections: { id: string; title: string; description: string; entries: Entry[]; start: number }[];
  extras: Entry[]; ordered: Entry[];
}

export function categoryStructuredData(guide: CategoryGuide, site: URL): Record<string, unknown>[] {
  const url = new URL(guide.url, site).href;
  const listId = `${url}#${guide.listAnchor || "exercises"}`;
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
