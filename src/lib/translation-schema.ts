import {z} from 'astro/zod';
import {createHash} from 'node:crypto';
import type {RenewalData} from './renewal-schema';
import {numbers,terms} from './bilingual-quality.ts';
const text=z.string().trim().min(1).max(1800).refine(t=>!/<\/?[A-Za-z]/.test(t),'HTML is not translation text');
const timestamp=z.iso.datetime({offset:true}).refine(t=>new Date(t)<=new Date(),'Future timestamp');
const shared={
  schemaVersion:z.literal(1),renewalId:z.string().regex(/^[0-9a-f]{16}$/),
  language:z.enum(['zh-CN','ja','de','fr','ru','es']),sourceSha256:z.string().regex(/^[0-9a-f]{64}$/),
  edition:z.object({title:text.max(240),claims:z.array(text.max(1200)).min(2).max(3),followUp:z.array(text.max(1200)).max(3)}),
  reviewFocus:text,
};
export const translationDraftSchema=z.object({...shared,state:z.literal('draft')}).strict();
export const translationSchema=z.object({...shared,state:z.literal('approved'),reviewedAt:timestamp,publishedAt:timestamp,updatedAt:timestamp,
  approval:z.object({reviewedBy:z.string().trim().min(1),pullRequest:z.number().int().positive(),approvedAt:timestamp,basis:z.string().trim().min(1)}),
}).strict().superRefine((d,ctx)=>{
  if(new Date(d.reviewedAt)>new Date(d.approval.approvedAt)||new Date(d.approval.approvedAt)>new Date(d.publishedAt)||new Date(d.publishedAt)>new Date(d.updatedAt))ctx.addIssue({code:'custom',message:'Translation review and publication chronology is inconsistent'});
});
export type TranslationData=z.infer<typeof translationSchema>;
const equal=(a:Set<string>,b:Set<string>)=>a.size===b.size&&[...a].every(v=>b.has(v));
export function validateTranslationSource(data:z.infer<typeof translationDraftSchema>|TranslationData,source:RenewalData,sourceBytes:string){
  if(data.renewalId!==source.id||data.sourceSha256!==createHash('sha256').update(sourceBytes).digest('hex'))throw new Error('Translation source changed; re-review the English edition: '+data.renewalId);
  if('reviewedAt' in data && new Date(data.reviewedAt)<new Date(source.updatedAt))throw new Error('Translation review precedes the source revision');
  for(const section of ['claims','followUp'] as const){
    const original=source.editions.en[section],translated=data.edition[section];
    if(original.length!==translated.length)throw new Error('Translation omitted or added a source claim');
    original.forEach((c,i)=>{for(const extract of [numbers,terms])if(!equal(extract(c.text),extract(translated[i])))throw new Error('Translation numbers or protected terms differ from source');});
  }
  for(const extract of [numbers,terms]){
    if(!equal(extract(source.reviewFocus.en),extract(data.reviewFocus)))throw new Error('Translation review focus changes numbers or protected terms');
    const body=extract(data.edition.claims.join(' '));
    if([...extract(data.edition.title)].some(value=>!body.has(value)))throw new Error('Translation title adds ungrounded numbers or protected terms');
  }
  const script={"zh-CN":/\p{Script=Han}/u,ja:/[\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}]/u,de:/\p{Script=Latin}/u,fr:/\p{Script=Latin}/u,ru:/\p{Script=Cyrillic}/u,es:/\p{Script=Latin}/u}[data.language];
  for(const value of [data.edition.title,...data.edition.claims,...data.edition.followUp,data.reviewFocus])if(!script.test(value))throw new Error('Translation lacks expected language script');

}
export function translatedEdition(data:TranslationData,source:RenewalData){
  return {title:data.edition.title,claims:source.editions.en.claims.map((c,i)=>({...c,text:data.edition.claims[i]})),followUp:source.editions.en.followUp.map((c,i)=>({...c,text:data.edition.followUp[i]}))};
}
