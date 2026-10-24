import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://youdozi.github.io',
  output: 'static',
  trailingSlash: 'always',
  i18n: { defaultLocale: 'en', locales: ['en', 'ko'], routing: { prefixDefaultLocale: true } },
  markdown: { shikiConfig: { theme: 'github-dark' } },
});
