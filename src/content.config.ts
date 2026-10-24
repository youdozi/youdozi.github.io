import { digestSchema } from './lib/digest-schema';
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
const digests = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/digests' }),
  schema: digestSchema,
});
export const collections = { posts, digests };
