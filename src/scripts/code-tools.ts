export type CodeCopyLabels = {copy:string;copied:string;error:string;block:string};
type ClipboardWriter = Pick<Clipboard,'writeText'>;

/** Enhance rendered code without changing the code nodes or their text. */
export function mountCodeTools(root: ParentNode, labels: CodeCopyLabels, clipboard?: ClipboardWriter) {
  for (const code of root.querySelectorAll<HTMLElement>('pre > code')) {
    const pre=code.parentElement!;
    if (pre.dataset.codeTools || !code.textContent?.trim()) continue;
    pre.dataset.codeTools='ready';
    if (!pre.hasAttribute('tabindex')) pre.tabIndex=0;
    if (!pre.hasAttribute('role')) pre.setAttribute('role','region');
    if (!pre.hasAttribute('aria-label') && !pre.hasAttribute('aria-labelledby')) pre.setAttribute('aria-label',labels.block);
    if (typeof clipboard?.writeText !== 'function') continue;

    const document=pre.ownerDocument;
    const wrapper=document.createElement('div');wrapper.className='code-example';
    const toolbar=document.createElement('div');toolbar.className='code-tools';
    const button=document.createElement('button');button.type='button';button.textContent=labels.copy;
    const status=document.createElement('p');status.className='code-copy-status';
    status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.setAttribute('aria-atomic','true');
    pre.before(wrapper);toolbar.append(button);wrapper.append(toolbar,pre,status);

    let busy=false;
    button.addEventListener('click',async()=>{
      if (busy) return;
      busy=true;button.setAttribute('aria-disabled','true');status.textContent='';
      try {
        // Preserve indentation, blank lines, prompts, Unicode and trailing newlines.
        await clipboard.writeText(code.textContent ?? '');
        status.textContent=labels.copied;
      } catch {
        status.textContent=labels.error;
      } finally {
        busy=false;button.removeAttribute('aria-disabled');
      }
    });
  }
}
