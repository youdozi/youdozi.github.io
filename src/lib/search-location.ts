/** Keep the reader's exact Unicode query; URLSearchParams handles escaping. */
export function searchQuery(url: URL): string {
  return url.searchParams.get('q') ?? '';
}

/** Preserve unrelated parameters, fragment and origin; never interpret a query as a URL. */
export function searchLocation(url: URL, query: string): URL {
  const next = new URL(url);
  if (query.trim()) next.searchParams.set('q', query);
  else next.searchParams.delete('q');
  return next;
}
