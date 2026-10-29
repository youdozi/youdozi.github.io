import {z} from 'astro/zod';
const hash=z.string().regex(/^[a-f0-9]{64}$/);
const timestamp=z.iso.datetime({offset:true}).refine(t=>new Date(t)<=new Date(),'Future publication timestamp');
export const technicalPublicationSchema=z.object({
  schemaVersion:z.literal(1),state:z.literal('approved'),
  language:z.enum(['zh-CN','ja','de','fr','ru','es']),
  translationKey:z.string().regex(/^\d{4}-\d{2}-\d{2}-[a-z0-9.-]+$/),
  routeSlug:z.string().regex(/^[a-z0-9][a-z0-9._-]*$/),kind:z.literal('post'),
  title:z.string().trim().min(1).max(240),description:z.string().trim().min(1).max(600),
  categories:z.array(z.string()),tags:z.array(z.string()),
  sourcePath:z.string().regex(/^src\/content\/posts\/en\/\d{4}-\d{2}-\d{2}-[a-z0-9.-]+\.md$/),
  sourceSha256:hash,draftSha256:hash,
  manifestPath:z.string().regex(/^\.pipeline\/technical-translations\/batch-[0-9]+\/manifest\.json$/),manifestSha256:hash,
  publishedAt:timestamp,updatedAt:timestamp,
  approval:z.object({kind:z.enum(['human','render-fixture']),reviewedBy:z.string().trim().min(1),
    pullRequest:z.number().int().positive(),approvedAt:timestamp,basis:z.string().trim().min(1)}).strict(),
  // Keeps the shared Article renderer's optional hero-image contract explicit.
  image:z.undefined().optional(),
}).strict().superRefine((d,ctx)=>{
  if(new Date(d.approval.approvedAt)>new Date(d.publishedAt)||new Date(d.publishedAt)>new Date(d.updatedAt))ctx.addIssue({code:'custom',message:'Technical publication chronology is inconsistent'});
  const fixture=d.approval.reviewedBy==='AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL'&&d.approval.pullRequest===Number.MAX_SAFE_INTEGER;
  if((d.approval.kind==='render-fixture')!==fixture||d.approval.kind==='human'&&/AUTOMATED|FIXTURE|NOT_HUMAN/i.test(d.approval.reviewedBy))ctx.addIssue({code:'custom',message:'Synthetic review must not claim human approval'});
});
export type TechnicalPublicationData=z.infer<typeof technicalPublicationSchema>;
