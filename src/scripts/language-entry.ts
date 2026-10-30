import {isSupportedLanguage,languagePreferenceKey,preferredLanguage} from '../lib/language-preference';
import './navigation';

// Language-specific and legacy URLs must always keep their explicit destinations.
if (location.pathname === '/') {
  const available = (document.documentElement.dataset.publishedLanguages ?? '').split(',').filter(isSupportedLanguage);
  let saved: string | null = null;
  try { saved = localStorage.getItem(languagePreferenceKey); } catch { /* Browsing can disable storage. */ }
  const preferences = navigator.languages?.length ? navigator.languages : [navigator.language];
  const language = preferredLanguage(preferences, saved, available);
  location.replace(`/${language}/${location.search}${location.hash}`);
}
