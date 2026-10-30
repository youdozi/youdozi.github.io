import { prepareSearch, searchItems, type SearchItem } from '../lib/search';
import { searchQuery, searchLocation } from '../lib/search-location';

const input = document.querySelector<HTMLInputElement>('#search')!;
const results = document.querySelector<HTMLDivElement>('#results')!;
const status = document.querySelector<HTMLParagraphElement>('#status')!;
const retry = document.querySelector<HTMLButtonElement>('#search-retry')!;
let index: Promise<ReturnType<typeof prepareSearch>> | undefined;
let version = 0;
let composing = false;
let timer: ReturnType<typeof setTimeout> | undefined;

async function search(syncLocation = true) {
  clearTimeout(timer);
  const current = ++version;
  if (syncLocation) {
    const next = searchLocation(new URL(location.href), input.value);
    if (next.href !== location.href) {
      // History can be unavailable in restricted browsing environments. Search still works.
      try { history.replaceState(history.state, '', next); } catch { /* optional URL persistence */ }
    }
  }
  retry.hidden = true;
  results.replaceChildren();
  status.textContent = '';
  results.setAttribute('aria-busy', 'false');
  if (!input.value.trim()) return;
  const query = input.value;
  status.textContent = status.dataset.loading!;
  results.setAttribute('aria-busy', 'true');
  try {
    index ??= fetch(`/${input.dataset.lang}/search-index.json`)
      .then(response => { if (!response.ok) throw new Error('index'); return response.json() as Promise<SearchItem[]>; })
      .then(prepareSearch)
      .catch(error => { index = undefined; throw error; });
    const items = await index;
    if (current !== version) return;
    const matches = searchItems(items, query);
    const number = new Intl.NumberFormat(input.dataset.lang);
    status.textContent = matches.total
      ? status.dataset.count!.replace('{shown}', number.format(matches.items.length)).replace('{total}', number.format(matches.total))
      : status.dataset.empty!;
    for (const item of matches.items) {
      const article = document.createElement('article'); article.className = 'search-result';
      const heading = document.createElement('h2'); const link = document.createElement('a');
      link.href = item.url; link.textContent = item.title;
      const description = document.createElement('p'); description.textContent = item.description;
      heading.append(link); article.append(heading, description); results.append(article);
    }
  } catch {
    if (current === version) {
      status.textContent = status.dataset.error!;
      retry.hidden = false;
    }
  } finally {
    if (current === version) results.setAttribute('aria-busy', 'false');
  }
}

function restore() {
  composing = false;
  input.value = searchQuery(new URL(location.href));
  void search(false);
}

input.addEventListener('compositionstart', () => { composing = true; ++version; clearTimeout(timer); });
input.addEventListener('compositionend', () => { composing = false; void search(); });
input.addEventListener('input', event => {
  if (composing || (event instanceof InputEvent && event.isComposing)) return;
  ++version;
  clearTimeout(timer);
  results.replaceChildren();
  // Coalesce typing rather than creating history entries or replacing on every keystroke.
  if (!input.value.trim()) void search();
  else timer = setTimeout(() => { void search(); }, 200);
});
retry.addEventListener('click', () => { input.focus(); void search(); });
window.addEventListener('popstate', restore);
window.addEventListener('pageshow', event => { if (event.persisted) restore(); });
restore();
