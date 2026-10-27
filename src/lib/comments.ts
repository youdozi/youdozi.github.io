export const commentRepository='youdozi/youdozi.github.io';
export const commentOrigin='https://utteranc.es';
export function isCommentCallback(url:string){return !!new URL(url).searchParams.get('utterances');}
export function commentTerm(entry:{legacyUrl?:string;translationKey:string}){
  return entry.legacyUrl||entry.translationKey;
}
export function commentFallback(term:string){
  return `https://github.com/${commentRepository}/issues?${new URLSearchParams({q:`is:issue "${term}"`})}`;
}
export function isCommentResize(event:{origin:string;source:unknown;data:unknown},frameWindow:unknown){
  if(event.origin!==commentOrigin||!frameWindow||event.source!==frameWindow||typeof event.data!=='object'||!event.data)return false;
  const data=event.data as {type?:unknown;height?:unknown};
  return data.type==='resize'&&typeof data.height==='number'&&Number.isFinite(data.height)&&data.height>0;
}
