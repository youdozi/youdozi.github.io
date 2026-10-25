import { z } from 'astro/zod';
import {validBilingualEditions} from './bilingual-quality.ts';
import archivePolicy from './archive-policy.json' with {type:'json'};
const nonempty=z.string().trim().min(1);
const timestamp=z.iso.datetime({offset:true}).refine(t=>new Date(t)<=new Date(),'Future timestamp');
const https=z.url().refine(value=>{try {const u=new URL(value);return u.protocol==='https:' && !u.username && !u.password && (!u.port || u.port==='443') && !/[\s<>\\]/.test(value);}catch{return false;}});
const claim=z.object({text:nonempty.max(600),evidence:z.array(z.object({document_id:z.number().int().nonnegative(),quote:z.string().min(20).max(240)})).min(1).max(3)});
const edition=z.object({title:nonempty.max(240),claims:z.array(claim).min(2).max(3),followUp:z.array(claim).max(3)});
export const renewalSchema=z.object({
  schemaVersion:z.literal(1),state:z.literal('approved'),outcome:z.literal('renewed_draft'),id:z.string().regex(/^[0-9a-f]{16}$/),
  slug:z.string().regex(/^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$/),batchId:nonempty,
  archiveDate:z.string().regex(/^\d{4}-\d{2}-\d{2}$/),originalPagePublishedAt:timestamp,
  source:nonempty,url:https,sourceFile:nonempty,articleNumber:z.number().int().positive(),sourcePublishedAt:timestamp.nullable(),
  editionPublishedAt:z.object({en:timestamp,ko:timestamp}),updatedAt:timestamp,reviewedAt:timestamp,
  reviewMethod:z.literal('editorial-source-context-review'),experimentStatus:z.literal('not_tested'),
  reviewFocus:z.object({en:nonempty.max(1200),ko:nonempty.max(1200)}),
  editions:z.object({en:edition,ko:edition}),tags:z.array(nonempty).min(1),
  documents:z.array(z.object({url:https,role:z.enum(['primary','reporting']),sha256:z.string().regex(/^[0-9a-f]{64}$/),fetchedAt:timestamp,extractorVersion:z.literal('article-parser-v1')})).min(1).max(4),
  approval:z.object({reviewedBy:nonempty,pullRequest:z.number().int().positive(),approvedAt:timestamp,basis:nonempty}),
}).superRefine((value,ctx)=>{
  const fail=(message:string)=>ctx.addIssue({code:'custom',message});
  if(!value.slug.startsWith(value.archiveDate+'-') || value.editionPublishedAt.ko!==value.originalPagePublishedAt)fail('Historical dates changed');
  if(new Date(value.reviewedAt)>new Date(value.approval.approvedAt) || new Date(value.approval.approvedAt)>new Date(value.editionPublishedAt.en) || new Date(value.editionPublishedAt.en)>new Date(value.updatedAt) || new Date(value.originalPagePublishedAt)>new Date(value.reviewedAt))fail('Publication and review chronology is inconsistent');
  if(!validBilingualEditions(value.editions) || !validBilingualEditions({en:{title:'',claims:value.editions.en.followUp},ko:{title:'',claims:value.editions.ko.followUp}}))fail('Bilingual facts differ');
  for(const lang of ['en','ko'] as const){
    const ed=value.editions[lang];
    if(lang==='ko' && !/[가-힣]/.test(ed.title))fail('Korean title required');
    for(const c of [...ed.claims,...ed.followUp]){
      if(lang==='ko' && !/[가-힣]/.test(c.text))fail('Korean claim required');
      if(c.evidence.some(e=>e.document_id>=value.documents.length))fail('Unknown source document');
      if(!c.evidence.some(e=>value.documents[e.document_id]?.role==='primary'))fail('Primary evidence required');
    }
  }
  if(value.documents.some(d=>new Date(d.fetchedAt)>new Date(value.reviewedAt)))fail('Source collection follows review');
  if(value.documents.some(d=>d.role==='primary' && !archivePolicy.primaryHosts.includes(new URL(d.url).hostname) && !archivePolicy.primaryUrls.includes(d.url)))fail('Unapproved primary publisher');
});
export type RenewalData=z.infer<typeof renewalSchema>;
