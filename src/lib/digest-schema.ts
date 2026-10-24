import { z } from 'astro/zod';
const claim = z.object({ text: z.string(), evidence: z.array(z.object({ document_id: z.number().int().nonnegative(), quote: z.string() })).min(1) });
const edition = z.object({ title: z.string(), summary: z.string().min(80).max(800), claims: z.array(claim).min(2).max(3) });
export const digestSchema = z.object({
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), publishedAt: z.coerce.date(), updatedAt: z.coerce.date().optional(),
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
  });
export type DigestData = z.infer<typeof digestSchema>;
export type DigestArticle = DigestData["articles"][number];
