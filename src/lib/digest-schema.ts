import { z } from 'astro/zod';
import policy from './digest-policy.json' with { type: 'json' };
const nonempty = z.string().refine(value => value.trim().length > 0, 'Text cannot be empty');
const timestamp = z.union([
  z.date(),
  z.string().regex(/^\d{4}-\d{2}-\d{2}T.+(?:Z|[+-]\d{2}:\d{2})$/).transform(value => new Date(value)),
]).refine(date => Number.isFinite(date.getTime()), 'Invalid timestamp');
const httpsUrl = z.url().refine(value => {
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password && (!url.port || url.port === '443') && !/[\s<>\\]/.test(value); } catch { return false; }
}, 'URL must use HTTPS without credentials or unsafe characters');
const claim = z.object({ text: nonempty, evidence: z.array(z.object({ document_id: z.number().int().nonnegative(), quote: z.string().min(policy.minQuote).max(policy.maxQuote) })).min(1) });
const edition = (language: 'en' | 'ko') => z.object({title: nonempty.max(policy.maxTitle), summary: z.string().min(policy.minSummary).max(policy.maxSummary[language]), claims: z.array(claim).min(policy.minClaims).max(policy.maxClaims)});
function normalizedUrl(value: string) {
  let url: URL; try {url = new URL(value);} catch {return value;} url.hash = '';
  for (const key of [...url.searchParams.keys()]) if (policy.trackingQueryPrefixes.some(prefix => key.toLowerCase().startsWith(prefix))) url.searchParams.delete(key);
  return url.href;
}
const koreanDate = (date: Date) => new Date(date.getTime() + 9*3600*1000).toISOString().slice(0,10);
export const digestSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), publishedAt: timestamp, updatedAt: timestamp.optional(),
  articles: z.array(z.object({
    id: nonempty, source: nonempty, url: httpsUrl, publishedAt: timestamp, tags: z.array(z.string()),
    editions: z.object({ en: edition('en'), ko: edition('ko') }),
    model: nonempty, verification: z.literal('source_consistency_checked'),
    documents: z.array(z.object({ url: httpsUrl, sha256: z.string().regex(/^[0-9a-f]{64}$/) })).min(1),
  }).superRefine((article, ctx) => {
    const hosts = (policy.sourceHosts as Record<string, string[]>)[article.source] || [];
    let hostname = ''; try {hostname = new URL(article.url).hostname;} catch {}
    if (!hosts.includes(hostname)) ctx.addIssue({code:'custom',message:'Article source URL is not approved'});
    for (const language of ['en', 'ko'] as const) {
      const edition = article.editions[language];
      if (edition.summary !== edition.claims.map(c => c.text).join(' ')) ctx.addIssue({ code: 'custom', message: 'Summary must contain only verified claims' });
      for (const claim of edition.claims) for (const evidence of claim.evidence) {
        if (evidence.document_id >= article.documents.length) ctx.addIssue({ code: 'custom', message: 'Unknown evidence document' });
      }
    }
  })).min(policy.minArticles).max(policy.maxArticles),
}).superRefine((digest, ctx) => {
  const collected = digest.updatedAt || digest.publishedAt;
  if (!Number.isFinite(collected.getTime()) || !Number.isFinite(digest.publishedAt.getTime())) return;
  if (collected > new Date() || collected < digest.publishedAt || koreanDate(digest.publishedAt) !== digest.date || koreanDate(collected) !== digest.date) ctx.addIssue({code:'custom',message:'Invalid digest publication/update date'});
  const urls = new Set<string>(); const ids = new Set<string>();
  for (const article of digest.articles) {
    const url = normalizedUrl(article.url);
    if (urls.has(url) || ids.has(article.id)) ctx.addIssue({code:'custom',message:'Duplicate article URL or ID'});
    urls.add(url); ids.add(article.id);
    if (article.publishedAt > collected || article.publishedAt.getTime() < collected.getTime() - policy.daysBack*86400*1000) ctx.addIssue({code:'custom',message:'Article is future or outside the freshness window'});
  }
});
export type DigestData = z.infer<typeof digestSchema>;
export type DigestArticle = DigestData['articles'][number];
