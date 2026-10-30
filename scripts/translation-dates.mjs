/** Canonicalize explicit calendar dates in prose; never infer numeric slash dates. */
const months=new Map();
for(const locale of ['en','de','fr','es','ru'])for(let month=1;month<=12;month++){
 const parts=new Intl.DateTimeFormat(locale,{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).formatToParts(new Date(Date.UTC(2020,month-1,15)));
 months.set(parts.find(p=>p.type==='month').value.toLocaleLowerCase('en'),month);
}
const escape=value=>value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const names=[...months.keys()].sort((a,b)=>b.length-a.length).map(escape).join('|');
const dayFirst=new RegExp(`(?<![\\p{L}\\d])(\\d{1,2})\\.?\\s+(?:de\\s+)?(${names})(?:\\s+(?:de\\s+)?(\\d{4})(?!\\d))?(?![\\p{L}\\d])`,'giu');
const englishNames=Array.from({length:12},(_,i)=>new Intl.DateTimeFormat('en',{month:'long',timeZone:'UTC'}).format(new Date(Date.UTC(2020,i,15)))).join('|');
const monthFirst=new RegExp(`(?<![\\p{L}\\d])(${englishNames})\\s+(\\d{1,2})(?:,?\\s+(\\d{4})(?!\\d))?(?![\\p{L}\\d])`,'gu');
function token(original,year,month,day){
 // Reject invalid dates without silently rolling them into the next month.
 const y=year?Number(year):2000,m=Number(month),d=Number(day),date=new Date(Date.UTC(y,m-1,d));
 if(date.getUTCFullYear()!==y||date.getUTCMonth()!==m-1||date.getUTCDate()!==d)return original;
 return ` calendar[${year?year+'-':''}${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}] `;
}
export function normalizeCalendarDates(text){
 return text
  .replace(/(?<!\d)(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日/gu,(s,y,m,d)=>token(s,y,m,d))
  .replace(/(?<![\d年])(\d{1,2})月\s*(\d{1,2})日/gu,(s,m,d)=>token(s,undefined,m,d))
  .replace(monthFirst,(s,m,d,y)=>token(s,y,months.get(m.toLocaleLowerCase('en')),d))
  .replace(dayFirst,(s,d,m,y)=>token(s,y,months.get(m.toLocaleLowerCase('en')),d));
}
