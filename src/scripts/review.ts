import { digestSchema, type DigestData } from '../lib/digest-schema';
const repository = 'youdozi/youdozi.github.io';
const github = `https://api.github.com/repos/${repository}`;
const form = document.querySelector<HTMLFormElement>('#review-form')!;
const input = document.querySelector<HTMLInputElement>('#pr-number')!;
const status = document.querySelector<HTMLElement>('#review-status')!;
const result = document.querySelector<HTMLElement>('#review-result')!;
const button = form.querySelector<HTMLButtonElement>('button')!;
let generation = 0;
function element<T extends Element = HTMLElement>(root: ParentNode, selector: string) { return root.querySelector<T>(selector)!; }
async function request(path: string, raw = false): Promise<any> {
  const response = await fetch(`${github}/${path}`, {headers:{Accept:raw ? 'application/vnd.github.raw+json' : 'application/vnd.github+json'},cache:'no-store',credentials:'omit',signal:AbortSignal.timeout(20000)});
  if (!response.ok) {
    if (response.status === 403 || response.status === 429) throw new Error('GitHub 조회 한도 또는 접근 제한에 도달했습니다. 잠시 후 다시 시도하거나 GitHub PR에서 확인하세요.');
    if (response.status === 404) throw new Error('PR 또는 초안 파일을 찾을 수 없습니다. PR 번호를 확인하세요.');
    throw new Error('GitHub에서 초안을 불러오지 못했습니다. 잠시 후 다시 시도하세요.');
  }
  return response.json();
}
function render(data: DigestData) {
  for (const lang of ['en','ko'] as const) {
    const container = element(document, `#review-${lang}`);
    const template = element<HTMLTemplateElement>(document, `#review-template-${lang}`);
    const articles = data.articles.map((article, index) => {
      const section = template.content.firstElementChild!.cloneNode(true) as HTMLElement;
      element(section,'[data-source]').textContent=article.source;
      const date=element<HTMLTimeElement>(section,'[data-date]');date.dateTime=article.publishedAt.toISOString();
      date.textContent=new Intl.DateTimeFormat(lang==='en'?'en-US':'ko-KR',{dateStyle:'medium',timeZone:'Asia/Seoul'}).format(article.publishedAt);
      element(section,'[data-title]').textContent=`${index+1}. ${article.editions[lang].title}`;
      element(section,'[data-summary]').textContent=article.editions[lang].summary;
      element<HTMLAnchorElement>(section,'[data-source-link]').href=article.url;
      const claims=element(section,'[data-claims]');claims.replaceChildren();
      for (const claim of article.editions[lang].claims) {
        const group=document.createElement('div');const text=document.createElement('p');text.textContent=claim.text;group.append(text);
        for (const evidence of claim.evidence) {
          const quote=document.createElement('blockquote');const text=document.createElement('p');text.textContent=evidence.quote;
          const link=document.createElement('a');link.href=article.documents[evidence.document_id].url;link.textContent=lang==='en'?'Evidence source ↗':'인용 출처 ↗';link.rel='noopener noreferrer';
          quote.append(text,link);group.append(quote);
        }
        claims.append(group);
      }
      return section;
    });
    container.replaceChildren(...articles);
  }
  element<HTMLInputElement>(document,'#show-evidence').checked=false;
}
async function load(number: string) {
  const current=++generation;
  result.hidden=true;
  if (!/^[1-9]\d{0,8}$/.test(number)) {status.textContent='올바른 PR 번호를 입력하세요.';return;}
  button.disabled=true;status.textContent='GitHub에서 검토할 초안을 불러오고 있습니다…';
  try {
    const pr=await request(`pulls/${number}`);
    if (pr.head?.repo?.full_name!==repository || pr.base?.ref!=='main' || !pr.head?.ref?.startsWith('content/digest-review-') || !/^[a-f0-9]{40}$/.test(pr.head.sha)) throw new Error('이 저장소의 개발 뉴스 검토용 PR만 미리볼 수 있습니다.');
    if (pr.state!=='open') throw new Error(pr.merged ? '이미 병합된 PR입니다. 게시된 글을 사이트에서 확인하세요.' : '닫힌 PR입니다. 이 초안은 검토 대상이 아닙니다.');
    const files=await request(`pulls/${number}/files?per_page=100`);
    const digests=files.filter((file: {filename:string;status:string})=>/^(added|modified)$/.test(file.status) && /^src\/content\/digests\/\d{4}-\d{2}-\d{2}\.json$/.test(file.filename));
    if (digests.length!==1) throw new Error('PR에 검토할 다이제스트 파일이 하나 있어야 합니다. GitHub에서 변경 파일을 확인하세요.');
    const raw=await request(`contents/${digests[0].filename}?ref=${pr.head.sha}`,true);
    const parsed=digestSchema.safeParse(raw);
    if (!parsed.success) throw new Error('초안 형식이나 요약·근거가 올바르지 않습니다. GitHub에서 JSON 수정 및 검사 결과를 확인하세요.');
    // Verify the preview still represents the current head, not an edit made during loading.
    const latest=await request(`pulls/${number}`);
    if (latest.head.sha!==pr.head.sha || latest.state!=='open') throw new Error('불러오는 동안 PR이 변경되었습니다. 초안을 다시 불러오세요.');
    if (current!==generation) return;
    render(parsed.data);
    const prLink=element<HTMLAnchorElement>(document,'#review-pr');prLink.href=`https://github.com/${repository}/pull/${number}`;
    const version=element<HTMLAnchorElement>(document,'#review-version');version.href=`https://github.com/${repository}/blob/${pr.head.sha}/${digests[0].filename}`;version.textContent=`확인 중인 버전 ${pr.head.sha.slice(0,7)} ↗`;
    element(document,'#review-meta').textContent=`수집 기준일 ${parsed.data.date} · 기사 ${parsed.data.articles.length}개 · PR #${number} · GitHub에서 수정했다면 다시 불러오세요.`;
    result.hidden=false;status.textContent='초안을 불러왔습니다. 원문을 열어 확인한 뒤 GitHub PR에서 최종 검토·병합하세요.';
  } catch (error) {
    if (current===generation) status.textContent=error instanceof Error && error.name!=='TimeoutError' && error.name!=='TypeError' ? error.message : '네트워크 연결을 확인하고 다시 시도하세요. GitHub PR에서도 초안을 볼 수 있습니다.';
  } finally {if(current===generation) button.disabled=false;}
}
form.addEventListener('submit',event=>{event.preventDefault();const number=input.value.trim();const url=new URL(location.href);url.searchParams.set('pr',number);history.replaceState(null,'',url);void load(number);});
for (const control of document.querySelectorAll<HTMLButtonElement>('[data-view]')) control.addEventListener('click',()=>{
  element<HTMLElement>(document,'#review-columns').dataset.mode=control.dataset.view;
  for (const button of document.querySelectorAll('[data-view]')) button.setAttribute('aria-pressed',String(button===control));
});
element<HTMLInputElement>(document,'#show-evidence').addEventListener('change',event=>{const checked=(event.target as HTMLInputElement).checked;for(const details of result.querySelectorAll('details')) details.open=checked;});
if (matchMedia('(max-width:800px)').matches) element<HTMLButtonElement>(document,'[data-view="ko"]').click();
const number=new URL(location.href).searchParams.get('pr');if(number){input.value=number;void load(number);}
