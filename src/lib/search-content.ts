import {readerMarkdown} from './reader-markdown.ts';

/** Remove HTML prose markup without treating comparison operators or code as tags. */
export function searchContent(markdown:string):string {
  const input=readerMarkdown(markdown),blocks:string[]=[];
  let marker='\u0000SEARCH_CODE\u0000';while(input.includes(marker))marker+='X';
  const keep=(value:string)=>{const index=blocks.push(value)-1;return `${marker}${index}${marker}`;};
  const lines:string[]=[];let fence:{char:string;length:number;lines:string[]}|undefined;
  for(const line of input.split('\n')){
    if(fence){
      fence.lines.push(line);
      if(new RegExp(`^ {0,3}${fence.char}{${fence.length},}\\s*$`).test(line)){lines.push(keep(fence.lines.join('\n')));fence=undefined;}
      continue;
    }
    const open=line.match(/^ {0,3}(`{3,}|~{3,})/);
    if(open){fence={char:open[1][0],length:open[1].length,lines:[line]};continue;}
    lines.push(line.replace(/(`+)([^`\n]+)\1/g,keep));
  }
  if(fence)lines.push(keep(fence.lines.join('\n')));
  let output=lines.join('\n').replace(/<!--[\s\S]*?-->/g,' ')
    .replace(/<(script|style|template)\b[^>]*>[\s\S]*?<\/\1\s*>/gi,' ')
    .replace(/<\/?[A-Za-z][^>]*>/g,' ');
  blocks.forEach((value,index)=>{output=output.replace(`${marker}${index}${marker}`,()=>value);});
  return output;
}
