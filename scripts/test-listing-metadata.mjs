import test from 'node:test';
import assert from 'node:assert/strict';
import {listingPage,listingStructuredData} from '../src/lib/listing-metadata.ts';
import {serializeJsonLd} from '../src/lib/page-metadata.ts';
const site=new URL('https://youdozi.github.io');
const items=Array.from({length:25},(_,i)=>({title:`Title ${i}`,url:`/en/posts/item-${i}/`,language:'en'}));
const context={title:'Posts',description:'Visible posts',lang:'en',url:'/en/posts/'};
test('every page uses its actual cards once, including the final partial page',()=>{
 const pages=[1,2,3].map(page=>listingPage(items,page));
 assert.deepEqual(pages.map(p=>p.visible.length),[12,12,1]);assert.deepEqual(pages.flatMap(p=>p.visible),items);
 assert.ok(pages.every(p=>p.totalPages===3));
 for(const page of [0,-1,1.5,NaN,4])assert.throws(()=>listingPage(items,page),/Invalid/);
 assert.deepEqual(listingPage([],1),{totalPages:1,visible:[]});
});
test('collection and list IDs use the current canonical page and actual visible order',()=>{
 const visible=listingPage(items,2).visible;const [collection,list]=listingStructuredData(visible,{...context,url:'/en/posts/page/2/',title:'Posts · Page 2'},site);
 assert.equal(collection.url,'https://youdozi.github.io/en/posts/page/2/');assert.equal(collection['@id'],collection.url+'#collection');assert.equal(collection.mainEntity['@id'],list['@id']);
 assert.equal(list.numberOfItems,12);assert.equal(list.name,collection.name);assert.equal(collection.inLanguage,'en');
 assert.deepEqual(list.itemListElement.map(i=>[i.position,i.name,i.url]),visible.map((item,i)=>[i+1,item.title,new URL(item.url,site).href]));
 assert.equal(list.itemListElement[0].name,'Title 12');assert.ok(!JSON.stringify(list).includes('Title 0'));
});
test('all eight languages keep localized card text and real language URLs',()=>{
 for(const lang of ['en','ko','zh-CN','ja','de','fr','ru','es']){
  const localized={language:lang,url:`/${lang}/digest/example/`,title:'한글 日本語 简体 français русский español'};
  const [collection,list]=listingStructuredData([localized],{...context,lang,url:`/${lang}/digest/`},site);
  assert.equal(collection.inLanguage,lang);assert.equal(list.itemListElement[0].name,localized.title);assert.equal(list.itemListElement[0].url,new URL(localized.url,site).href);
 }
});
test('empty listings emit no invented collection and mixed or duplicate cards fail',()=>{
 assert.deepEqual(listingStructuredData([],context,site),[]);
 assert.throws(()=>listingStructuredData([items[0],items[0]],context,site),/unique/);
 assert.throws(()=>listingStructuredData([{...items[0],language:'ko'}],context,site),/language/);
});
test('listing JSON-LD uses the shared serializer without interpreting special card titles',()=>{
 const title='Literal </script><script>alert(1)</script> & "quote"';const graph=listingStructuredData([{...items[0],title}],context,site);
 const encoded=serializeJsonLd(graph);assert.ok(!encoded.includes('<'));assert.deepEqual(JSON.parse(encoded),graph);assert.equal(JSON.parse(encoded)[1].itemListElement[0].name,title);
});
