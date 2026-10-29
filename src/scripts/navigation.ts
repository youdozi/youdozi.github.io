const menu=document.querySelector<HTMLDetailsElement>('.language-menu');
if(menu){
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape'||!menu.open)return;
    const focused=menu.contains(document.activeElement);
    menu.open=false;
    if(focused){event.preventDefault();menu.querySelector('summary')?.focus();}
  });
  document.addEventListener('click',event=>{
    if(menu.open&&!event.composedPath().includes(menu))menu.open=false;
  });
  menu.addEventListener('focusout',event=>{
    if(event.relatedTarget instanceof Node&&!menu.contains(event.relatedTarget))menu.open=false;
  });
}
