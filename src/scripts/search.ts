import { prepareSearch, searchItems, type SearchItem } from '../lib/search';

const input = document.querySelector<HTMLInputElement>('#search')!;
const results = document.querySelector<HTMLDivElement>('#results')!;
const status = document.querySelector<HTMLParagraphElement>('#status')!;
const retry = document.querySelector<HTMLButtonElement>('#search-retry')!;
let index: Promise<ReturnType<typeof prepareSearch>> | undefined;
let version = 0;
let composing = false;

async function search() {
  const current = ++version;
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

input.addEventListener('compositionstart', () => { composing = true; ++version; });
input.addEventListener('compositionend', () => { composing = false; void search(); });
input.addEventListener('input', event => { if (!composing && !(event instanceof InputEvent && event.isComposing)) void search(); });
retry.addEventListener('click', () => { input.focus(); void search(); });
