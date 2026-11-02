from pathlib import Path
from html import escape
p=Path(__file__).resolve().parent
texts={
'ko':['로그와 트레이스를 같은 ID로 연결','Python 예제','checkout → inventory.lookup','활성 span 안에서 로그 기록','OTel Collector','OTLP HTTP :4318','로그와 트레이스 분리 전송','Loki','로그 + trace_id','Tempo','부모·자식 span','Grafana Explore','로그 → 트레이스: derivedFields','span → 로그: tracesToLogsV2','service_name으로 범위 제한','trace_id로 같은 실행의 로그 선택'],
'en':['Connect logs and traces by ID','Python example','checkout → inventory.lookup','Log inside the active span','OTel Collector','OTLP HTTP :4318','Route logs and traces separately','Loki','Logs + trace_id','Tempo','Parent / child spans','Grafana Explore','Log → trace: derivedFields','Span → logs: tracesToLogsV2','Narrow by service_name','Filter one run with trace_id']}
for lang,t in texts.items():
 s=['<svg xmlns="http://www.w3.org/2000/svg" width="360" height="680" viewBox="0 0 360 680" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(t[0])}</title>',f'<desc id="desc">{escape("; ".join(t[1:]))}</desc>','<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#64748b"/></marker></defs>','<rect width="360" height="680" rx="16" fill="#f8fafc"/>','<g font-family="system-ui,sans-serif" fill="#0f172a" text-anchor="middle">']
 def text(y,v,bold=False,x=180): s.append(f'<text x="{x}" y="{y}" font-size="14"'+(' font-weight="700"' if bold else '')+f'>{escape(v)}</text>')
 def box(x,y,w,h):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#e0f2fe" stroke="#0284c7"/>')
 def arrow(d):s.append(f'<path d="{d}" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#a)"/>')
 text(31,t[0],True);box(20,55,320,105);text(82,t[1],True);text(111,t[2]);text(139,t[3]);arrow('M180 160V200');box(20,200,320,105);text(227,t[4],True);text(256,t[5]);text(284,t[6]);arrow('M180 305V330H95V355');arrow('M180 330H265V355');box(20,355,150,85);box(190,355,150,85);text(385,t[7],True,95);text(413,t[8],False,95);text(385,t[9],True,265);text(413,t[10],False,265);arrow('M95 440V470H155V490');arrow('M265 440V470H205V490');box(20,490,320,125);text(518,t[11],True);text(553,t[12]);text(587,t[13]);text(642,t[14]);text(665,t[15]);s.append('</g></svg>');(p/f'lgtm-log-trace-{lang}.svg').write_text('\n'.join(s))
