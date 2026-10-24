import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';
const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(), language: z.enum(['en', 'ko']), translationKey: z.string(),
    routeSlug: z.string().regex(/^[a-z0-9][a-z0-9._-]*$/), kind: z.enum(['post', 'digest']),
    publishedAt: z.coerce.date(), categories: z.array(z.string()).default([]), tags: z.array(z.string()).default([]),
    updatedAt: z.coerce.date().optional(), reviewedAt: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
    reviewScope: z.string().optional(), archiveBodySha256: z.string().length(64).optional(),
    reviewSources: z.array(z.url()).default([]), reviewStatus: z.enum(['revised', 'source-audited', 'example']).optional(),
    description: z.string().optional(), image: z.string().optional(), legacyUrl: z.string().optional(), legacySource: z.string().optional(),
  }),
});
const claim = z.object({ text: z.string(), evidence: z.array(z.object({ document_id: z.number().int().nonnegative(), quote: z.string() })).min(1) });
const edition = z.object({ title: z.string(), summary: z.string().min(80).max(800), claims: z.array(claim).min(2).max(3) });
const digests = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/digests' }),
  schema: z.object({
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), publishedAt: z.coerce.date(),
    articles: z.array(z.object({
      id: z.string(), source: z.string(), url: z.url().startsWith('https://'), publishedAt: z.coerce.date(), tags: z.array(z.string()),
      editions: z.object({ en: edition, ko: edition }),
      model: z.string(), verification: z.literal('source_consistency_checked'),
      documents: z.array(z.object({ url: z.url().startsWith('https://'), sha256: z.string().regex(/^[0-9a-f]{64}$/) })).min(1),
    }).superRefine((article, ctx) => {
      for (const language of ['en', 'ko'] as const) {
        const edition = article.editions[language];
        if (edition.summary !== edition.claims.map(c => c.text).join(' ')) ctx.addIssue({ code: 'custom', message: 'Summary must contain only verified claims' });
        for (const claim of edition.claims) for (const evidence of claim.evidence) {
          if (evidence.document_id >= article.documents.length) ctx.addIssue({ code: 'custom', message: 'Unknown evidence document' });
        }
      }
    })).min(1).max(6),
  }),
});
export const collections = { posts, digests };
