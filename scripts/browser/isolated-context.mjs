/** Browser verification must not contribute Google Analytics traffic. */
export const measurementId='G-XZVJ0K06M9';
const googleHost=host=>['google-analytics.com','googletagmanager.com','analytics.google.com','doubleclick.net'].some(base=>host===base||host.endsWith('.'+base));
const collectPath=path=>/^\/(?:g\/|mp\/|debug\/mp\/)?(?:collect|batch)\/?$/.test(path);
export function collectionRequest(url,body=''){
  const u=new URL(url),payload=[u.search.slice(1),body??''].join('&');
  return collectPath(u.pathname)||/(?:^|[&\s])(?:tid|measurement_id)=(?:G-|UA-)/i.test(payload);
}
export function telemetryDecision(url,body='',mode='verification',method='GET'){
  if(!['verification','tag-verification'].includes(mode))throw new Error('Unknown browser isolation mode');
  const u=new URL(url),tag=u.origin==='https://www.googletagmanager.com'&&!u.username&&!u.password&&u.pathname==='/gtag/js'&&u.searchParams.getAll('id').length===1&&u.searchParams.get('id')===measurementId&&method==='GET'&&!body;
  if(mode==='tag-verification'&&tag&&!collectionRequest(url,body))return 'allow-tag';
  if(googleHost(u.hostname)||collectionRequest(url,body))return 'block';
  return 'allow';
}

/** Install routes before creating pages. New pages/popups share this policy. */
export async function isolatedContext(browser,options={},mode='verification'){
  if(!['verification','tag-verification'].includes(mode))throw new Error('Unknown browser isolation mode');
  const context=await browser.newContext({...options,serviceWorkers:'block'});
  const counts={blocked:0,blockedCollection:0,allowedTag:0};
  try{
    await context.route('**/*',async route=>{
      const request=route.request(),decision=telemetryDecision(request.url(),request.postData(),mode,request.method());
      if(decision==='block'){counts.blocked++;if(collectionRequest(request.url(),request.postData()))counts.blockedCollection++;await route.abort('blockedbyclient');}
      else {if(decision==='allow-tag')counts.allowedTag++;await route.continue();}
    });
    return {context,summary:()=>({mode,serviceWorkers:'block',...counts})};
  }catch(error){await context.close();throw error;}
}
