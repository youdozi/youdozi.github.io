import policy from './editorial-policy.json' with {type:'json'};
import type {DigestArticle} from './digest-schema';
type Language = 'en' | 'ko';
export interface ReviewRow {label:string;value:string;kind:'automatic'|'source'|'human'|'missing';}
export const experimentLabel = (article:DigestArticle,lang:Language) => !article.editorial ? (lang==='ko'?'직접 실험 기록 미입력':'No direct experiment record provided') : article.editorial.experiment.status==='tested' ? (lang==='ko'?'직접 실험 · 기록 첨부':'Tested directly · report linked') : (lang==='ko'?'직접 실험 미수행':'Not tested directly');
export function candidateReviewRows(article:DigestArticle,lang:Language):ReviewRow[]{
  const ko=lang==='ko';const selection=article.selection;const sections=article.editions[lang].review;
  const rows:ReviewRow[]=[];
  if(selection){
    rows.push({label:ko?'추천 독자 · 자동 분류':'Suggested audience · automatic',value:policy.audience[lang],kind:'automatic'});
    rows.push({label:ko?'선정 이유 · 키워드 기준':'Selection reason · keyword rules',value:(selection.relevance==='direct'?(ko?'직접 관련':'Directly related'):(ko?'간접 관련':'Adjacent topic'))+' · '+selection.reasons.map(reason=>(policy.reasons as Record<string,{en:string;ko:string}>)[reason][lang]).join(', '),kind:'automatic'});
    rows.push({label:ko?'검토 우선순위 · 자동 제안':'Review priority · automatic suggestion',value:policy.priorities[selection.priority][lang]+(ko?' — 도입 권고가 아닙니다.':' — not an adoption recommendation.'),kind:'automatic'});
  }
  for(const key of ['keyChange','affectedAudience','conditions'] as const){
    const indices=sections?.[key]||[];
    rows.push({label:policy.sections[key][lang],kind:indices.length?'source':'missing',value:indices.length?indices.map(index=>`${article.editions[lang].claims[index].text} (${ko?'근거 문장':'claim'} ${index+1})`).join('\n'):(ko?'요약 근거에 정리되지 않았습니다. 원문을 확인하고 검토해 주세요.':'Not identified in the summary evidence. Review the original source.')});
  }
  rows.push({label:ko?'편집 의견 · 사용자 작성':'Editorial opinion · written by reviewer',kind:'human',value:article.editorial?.opinion[lang] || (ko?'아직 작성하지 않았습니다. 게시 가치와 적용 판단을 검토해 주세요.':'Not written yet. Review the publication value and applicability.')});
  const experiment=article.editorial?.experiment;
  rows.push({label:ko?'직접 실험 여부':'Direct experimentation',kind:'human',value:experimentLabel(article,lang)+(experiment?.status==='tested'?`\n${experiment.environment[lang]}\n${experiment.result[lang]}\n${experiment.reportUrl}`:'')});
  return rows;
}
