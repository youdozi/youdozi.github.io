import { defineConfig } from 'astro/config';
import {readerMarkdownProcessor} from './scripts/reader-markdown-processor.mjs';
export default defineConfig({
  site: 'https://youdozi.github.io',
  output: 'static',
  trailingSlash: 'always',
  i18n: { defaultLocale: 'en', locales: ['en', 'ko'], routing: { prefixDefaultLocale: true } },
  markdown: { processor: readerMarkdownProcessor(), shikiConfig: { theme: 'github-dark' } },
});
