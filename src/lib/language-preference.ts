import {supportedLanguages,type Language} from './locales.ts';

export const languagePreferenceKey = 'youdozi.language';
export function isSupportedLanguage(value: string | null): value is Language {
  return supportedLanguages.some(language => language === value);
}

/** Match browser BCP 47 preferences only to editions the build actually publishes. */
export function preferredLanguage(preferences: readonly string[], saved: string | null, available: readonly Language[]): Language {
  if (isSupportedLanguage(saved) && available.includes(saved)) return saved;
  for (const preference of preferences) {
    try {
      const locale = new Intl.Locale(preference);
      let language: string = locale.language;
      if (language === 'zh') {
        // A generic zh preference uses our simplified edition. Never substitute it for Hant.
        if (locale.script && locale.script !== 'Hans') continue;
        if (!locale.script && ['TW','HK','MO'].includes(locale.region ?? '')) continue;
        language = 'zh-CN';
      }
      if (isSupportedLanguage(language) && available.includes(language)) return language;
    } catch { /* Ignore invalid or unsupported locale tags and try the next preference. */ }
  }
  return 'en';
}
