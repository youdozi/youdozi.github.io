import type {Entry,Language} from './content';

export const listingPageSize=12;
export function listingPage<T>(items:T[],page:number) {
  const totalPages=Math.max(1,Math.ceil(items.length/listingPageSize));
  if (!Number.isInteger(page) || page<1 || page>totalPages) throw new Error('Invalid listing page');
  return {totalPages,visible:items.slice((page-1)*listingPageSize,page*listingPageSize)};
}

/** Describe this page's visible cards, rather than other pages or featured links. */
export function listingStructuredData(items:Pick<Entry,'title'|'url'|'language'>[],context:{title:string;description:string;lang:Language;url:string},site:URL):Record<string,unknown>[] {
  if (!items.length) return [];
  if (items.some(item=>item.language!==context.lang) || new Set(items.map(item=>item.url)).size!==items.length) throw new Error('Listing items must be unique and use the page language');
  const url=new URL(context.url,site).href;
  return [
    {'@context':'https://schema.org','@type':'CollectionPage','@id':url+'#collection',url,
      name:context.title,description:context.description,inLanguage:context.lang,mainEntity:{'@id':url+'#entries'}},
    {'@context':'https://schema.org','@type':'ItemList','@id':url+'#entries',name:context.title,
      numberOfItems:items.length,itemListElement:items.map((item,index)=>({
        '@type':'ListItem',position:index+1,name:item.title,url:new URL(item.url,site).href,
      }))},
  ];
}
