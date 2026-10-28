/** Runs only inside a privately generated, self-contained offline review file. */
export function mountReview(document){
  const data=JSON.parse(document.getElementById('packet-data').textContent);
  const get=id=>document.getElementById(id);
  const language=get('language'),search=get('query'),select=get('edition'),status=get('status'),view=get('comparison');
  let filtered=[],position=0;
  const node=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;};
  const date=value=>new Intl.DateTimeFormat('ko-KR',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Seoul'}).format(new Date(value));
  function link(text,url){const el=node('a',text);el.href=url;el.target='_blank';el.rel='noopener noreferrer';return el;}
  function column(title,lang,rows,side){
    const el=node('section',undefined,'column');el.lang=lang;el.append(node('h3',title));
    const list=node('ol');
    for(const row of rows){
      const item=node('li');item.append(node('p',row[side]));
      if(side==='english'&&row.evidence.length){
        const details=node('details');details.append(node('summary','저장된 원문 근거'));
        for(const quote of row.evidence){const block=node('blockquote');block.append(node('p',quote.quote),link('근거 자료 ↗',quote.url));details.append(block);}
        item.append(details);
      }
      list.append(item);
    }
    el.append(list);return el;
  }
  function render(){
    const item=filtered[position];
    get('previous').disabled=!item||position===0;get('next').disabled=!item||position===filtered.length-1;
    select.disabled=!item;view.replaceChildren();
    if(!item){status.textContent='조건에 맞는 대기 원고가 없습니다.';view.append(node('p','검색어를 지우거나 다른 언어를 선택하세요.'));return;}
    select.value=item.key;
    status.textContent=`${position+1} / ${filtered.length}편 · 전체 대기 ${data.entries.length}편 · 열람은 승인으로 기록되지 않습니다.`;
    const header=node('header',undefined,'article-header');
    header.append(node('h2',item.title),node('p',`${data.languages[item.language]} · 원고 키 ${item.key}`));
    const links=node('p',undefined,'links');
    links.append(link('기사 원문 ↗',item.sourceURL),link('고정 버전의 번역 원고 ↗',item.draftURL),link('게시 전 목록 ↗',item.releaseURL));
    header.append(links,node('p',`원래 소식 기준일 ${item.archiveDate} · 영어 기준본 수정 ${date(item.sourceUpdatedAt)} (한국 시각)`));
    view.append(header);
    const titles=node('div',undefined,'pair');titles.append(column(item.englishTitle,'en',item.claims,'english'),column(item.title,item.language,item.claims,'translated'));view.append(titles);
    if(item.followUp.length){const follow=node('section');follow.append(node('h3','추가 확인된 후속 사실'));const pair=node('div',undefined,'pair');pair.append(column('영어 기준문','en',item.followUp,'english'),column(data.languages[item.language],item.language,item.followUp,'translated'));follow.append(pair);view.append(follow);}
    const notes=node('details',undefined,'review-notes');notes.append(node('summary','내부 검토 의견과 기존 검토 시점'));
    const evidence={"stored-excerpts":"저장된 원문 인용","supplemental-primary":"별도 공식 보완 근거"};
    notes.append(node('p',`기존 AI 검토 ${date(item.reviewedAt)} (한국 시각) · ${evidence[item.evidenceMethod]??item.evidenceMethod}`),node('p','이번 파일 생성은 외부 사실 재검증이나 사람의 게시 승인이 아닙니다.'));
    const pair=node('div',undefined,'pair');const en=node('section');en.lang='en';en.append(node('h4','영어 검토 의견'),node('p',item.englishFocus));
    const target=node('section');target.lang=item.language;target.append(node('h4',data.languages[item.language]),node('p',item.translatedFocus));pair.append(en,target);notes.append(pair);view.append(notes);
  }
  function filter(){
    const term=search.value.normalize('NFKC').toLocaleLowerCase().trim();
    filtered=data.entries.filter(item=>(!language.value||item.language===language.value)&&`${item.key} ${item.title} ${item.englishTitle}`.normalize('NFKC').toLocaleLowerCase().includes(term));
    position=0;select.replaceChildren();
    for(const item of filtered){const option=node('option',`${item.englishTitle} · ${data.languages[item.language]}`);option.value=item.key;select.append(option);}
    render();
  }
  for(const [code,label] of Object.entries(data.languages)){
    const count=data.entries.filter(item=>item.language===code).length;
    if(count){const option=node('option',`${label} (${count}편)`);option.value=code;language.append(option);}
  }
  language.addEventListener('change',filter);search.addEventListener('input',filter);
  select.addEventListener('change',()=>{position=Math.max(0,filtered.findIndex(item=>item.key===select.value));render();});
  get('previous').addEventListener('click',()=>{if(position>0){position--;render();}});
  get('next').addEventListener('click',()=>{if(position<filtered.length-1){position++;render();}});
  filter();
}
