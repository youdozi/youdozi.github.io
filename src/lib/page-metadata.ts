import type {Entry,Language} from './content';
import {authorData} from './author.ts';
import {localeInfo} from './locales.ts';

export function serializeJsonLd(value: Record<string,unknown>[]): string {
  // Preserve the existing HTML-safe encoding and recover the original JSON values.
  return JSON.stringify(value).replace(/</g, '\\u003c');
}

export function articleMetadata(entry: Pick<Entry,'publishedAt'|'updatedAt'|'language'>) {
  return {
    publishedTime: entry.publishedAt.toISOString(),
    modifiedTime: (entry.updatedAt || entry.publishedAt).toISOString(),
    authorUrl: authorData(entry.language).url,
  };
}
export type ArticleMetadata = ReturnType<typeof articleMetadata>;

export function alternateLocales(language: Language, alternates: {language:Language}[]) {
  return [...new Set(alternates.filter(item=>item.language!==language).map(item=>localeInfo[item.language].ogLocale))];
}
