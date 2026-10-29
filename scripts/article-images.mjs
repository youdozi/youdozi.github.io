import {readFile,realpath} from 'node:fs/promises';
import {resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {imageMetadata} from 'astro/assets/utils';

const publicRoot=fileURLToPath(new URL('../public/',import.meta.url));
const positive=value=>Number.isFinite(Number(value)) && Number(value)>0;

/** Only public assets are read; never probe remote URLs or paths outside public. */
export async function localImageSize(src,base=publicRoot) {
  if (typeof src!=='string' || !src.startsWith('/assets/') || src.includes('\\')) return undefined;
  const pathname=decodeURIComponent(new URL(src,'https://local.invalid').pathname);
  const root=await realpath(base),assetRoot=resolve(root,'assets');
  const candidate=resolve(root,'.'+pathname);
  if (!candidate.startsWith(assetRoot+sep)) throw new Error('Image path leaves public assets');
  const path=await realpath(candidate);
  if (!path.startsWith(assetRoot+sep)) throw new Error('Image symlink leaves public assets');
  const size=await imageMetadata(await readFile(path),src);
  if (!positive(size.width) || !positive(size.height)) throw new Error('Invalid local image dimensions');
  return {width:size.width,height:size.height};
}

/** A factory gives every Markdown document its own first-image policy. */
export function articleImagePlugin(base=publicRoot) {
  return ()=>{
    let imageIndex=0;
    return {name:'public-article-image-layout',element:{filter:['img'],async visit(node,ctx){
      const first=imageIndex++===0,props=node.properties??{};
      const size=await localImageSize(props.src,base);
      if (!size) return;
      const width=props.width,height=props.height;
      if (width==null && height==null) {
        ctx.setProperty(node,'width',size.width);ctx.setProperty(node,'height',size.height);
      } else if (positive(width) && height==null) {
        ctx.setProperty(node,'height',Math.max(1,Math.round(Number(width)*size.height/size.width)));
      } else if (positive(height) && width==null) {
        ctx.setProperty(node,'width',Math.max(1,Math.round(Number(height)*size.width/size.height)));
      }
      if (props.loading==null) ctx.setProperty(node,'loading',first?'eager':'lazy');
      if (props.decoding==null) ctx.setProperty(node,'decoding','async');
    }}};
  };
}
