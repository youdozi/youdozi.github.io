import {isSupportedLanguage,languagePreferenceKey} from '../lib/language-preference';

function rememberLanguage(event: MouseEvent) {
  if (event.defaultPrevented || (event.type === 'auxclick' && event.button !== 1)) return;
  const link = event.target instanceof Element ? event.target.closest<HTMLAnchorElement>('a[data-language-choice]') : null;
  const language = link?.dataset.languageChoice ?? null;
  if (!link || !isSupportedLanguage(language)) return;
  const available = link.closest<HTMLElement>('[data-language-options]')?.dataset.languageOptions?.split(',') ?? [];
  const target = new URL(link.href);
  if (!available.includes(language) || target.origin !== location.origin || target.pathname.split('/')[1] !== language) return;
  // Static HTML cannot contain a runtime search query or fragment for a self-link.
  if (language === document.documentElement.lang && target.pathname === location.pathname) link.href = location.href;
  try { localStorage.setItem(languagePreferenceKey, language); } catch { /* A blocked preference must not prevent navigation. */ }
}
document.addEventListener('click', rememberLanguage);
document.addEventListener('auxclick', rememberLanguage);

const menu=document.querySelector<HTMLDetailsElement>('.language-menu');
if(menu){
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape'||!menu.open)return;
    const focused=menu.contains(document.activeElement);
    menu.open=false;
    if(focused){event.preventDefault();menu.querySelector('summary')?.focus();}
  });
  document.addEventListener('click',event=>{
    if(menu.open&&!event.composedPath().includes(menu))menu.open=false;
  });
  menu.addEventListener('focusout',event=>{
    if(event.relatedTarget instanceof Node&&!menu.contains(event.relatedTarget))menu.open=false;
  });
}
