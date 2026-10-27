import {commentOrigin,commentRepository,isCommentResize,isCommentCallback} from '../lib/comments';

class OnDemandComments extends HTMLElement {
  private state:'idle'|'loading'|'opened'|'error'='idle';
  private timer:number|undefined;
  private message:((event:MessageEvent)=>void)|undefined;
  connectedCallback(){
    if(this.dataset.bound)return;
    this.dataset.bound='true';this.dataset.state=this.state;
    const button=this.querySelector('button')!;
    button.hidden=false;
    button.addEventListener('click',()=>this.open());
    // Complete a reader-initiated Utterances login return without a second click.
    if(isCommentCallback(location.href))this.open();
  }
  disconnectedCallback(){this.cleanup();}
  private cleanup(){
    window.clearTimeout(this.timer);
    if(this.message)window.removeEventListener('message',this.message);
    this.message=undefined;
  }
  private open(){
    if(this.state!=='idle')return;
    this.state='loading';this.dataset.state=this.state;
    const button=this.querySelector('button')!;
    const status=this.querySelector<HTMLElement>('[role="status"]')!;
    const mount=this.querySelector<HTMLElement>('#comment-widget')!;
    button.setAttribute('aria-disabled','true');button.textContent=this.dataset.loading!;
    status.textContent=this.dataset.loading!;
    mount.hidden=false;mount.setAttribute('aria-busy','true');mount.style.minHeight='280px';
    const fail=()=>{
      if(this.state==='opened')return;
      this.state='error';this.dataset.state=this.state;
      const focused=document.activeElement===button;
      window.clearTimeout(this.timer);button.hidden=true;
      status.textContent=this.dataset.error!;mount.setAttribute('aria-busy','false');
      if(!mount.querySelector('iframe'))mount.hidden=true;
      if(focused)this.querySelector<HTMLAnchorElement>('.comment-actions a')!.focus({preventScroll:true});
    };
    this.message=event=>{
      const frame=mount.querySelector<HTMLIFrameElement>('iframe.utterances-frame');
      if(!frame||!isCommentResize(event,frame.contentWindow))return;
      this.state='opened';this.dataset.state=this.state;
      button.setAttribute('aria-expanded','true');
      const focused=document.activeElement===button;
      button.hidden=true;status.textContent=this.dataset.opened!;
      mount.hidden=false;mount.setAttribute('aria-busy','false');mount.style.removeProperty('min-height');
      this.cleanup();
      if(focused)frame.focus({preventScroll:true});
    };
    window.addEventListener('message',this.message);
    this.timer=window.setTimeout(fail,20000);
    const script=document.createElement('script');
    script.src=commentOrigin+'/client.js';script.async=true;script.crossOrigin='anonymous';
    script.setAttribute('repo',commentRepository);
    script.setAttribute('issue-term',this.dataset.term!);
    script.setAttribute('theme','github-light');script.onerror=fail;
    mount.append(script);
  }
}
if(!customElements.get('on-demand-comments'))customElements.define('on-demand-comments',OnDemandComments);
