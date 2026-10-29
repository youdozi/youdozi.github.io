import policy from './locales.json' with {type:'json'};
export const nativeLanguages = ['en','ko'] as const;
export const translationLanguages = ['zh-CN','ja','de','fr','ru','es'] as const;
export type NativeLanguage = typeof nativeLanguages[number];
export type TranslationLanguage = typeof translationLanguages[number];
export type Language = NativeLanguage | TranslationLanguage;
export const supportedLanguages: readonly Language[] = [...nativeLanguages,...translationLanguages];
export const localeInfo = policy.locales;
