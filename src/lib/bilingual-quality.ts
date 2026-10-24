import policy from './bilingual-quality-policy.json' with {type:'json'};

type Edition = {title:string; claims:{text:string}[]; review?:{keyChange:number[];affectedAudience:number[];conditions:number[]}};
function numbers(text:string) {
  const words=policy.numberWords as Record<string,string>;
  const normalized=text.replace(new RegExp(`\\b(${Object.keys(words).join('|')})\\b`,'gi'),value=>words[value.toLowerCase()]);
  return new Set([...normalized.matchAll(new RegExp(policy.numberPattern,'g'))].map(match=>match[0].replaceAll(',','')));
}
function terms(text:string) {
  return new Set(Object.entries(policy.terms).filter(([,pattern])=>new RegExp(`(?<![A-Za-z0-9])(?:${pattern})(?![A-Za-z0-9])`,'i').test(text)).map(([name])=>name));
}
function equal(a:Set<string>,b:Set<string>) {return a.size===b.size && [...a].every(value=>b.has(value));}
export function validBilingualEditions(editions:{en:Edition;ko:Edition}) {
  const {en,ko}=editions;
  if(en.claims.length!==ko.claims.length)return false;
  for(let i=0;i<en.claims.length;i++) for(const extract of [numbers,terms]) if(!equal(extract(en.claims[i].text),extract(ko.claims[i].text)))return false;
  for(const edition of [en,ko])for(const extract of [numbers,terms]){
    const body=extract(edition.claims.map(claim=>claim.text).join(' '));
    if([...extract(edition.title)].some(value=>!body.has(value)))return false;
  }
  for(const key of ['keyChange','affectedAudience','conditions'] as const)if(JSON.stringify(en.review?.[key])!==JSON.stringify(ko.review?.[key]))return false;
  return true;
}
