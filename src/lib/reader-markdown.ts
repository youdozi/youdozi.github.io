/** Remove repository editorial bookkeeping from published Markdown, preserving source files. */
export function readerMarkdown(content: string): string {
  const output: string[] = [];
  let skippedDepth: number | undefined;
  let editorialParagraph: 'pending' | 'body' | undefined;
  let fence: {char: string; length: number} | undefined;
  for (let line of content.split(/\r?\n/)) {
    if (fence) {
      if (skippedDepth === undefined) output.push(line);
      if (new RegExp(`^ {0,3}${fence.char}{${fence.length},}\\s*$`).test(line)) fence = undefined;
      continue;
    }
    const opening = line.match(/^ {0,3}(`{3,}|~{3,})/);
    if (opening) {
      fence = {char: opening[1][0], length: opening[1].length};
      editorialParagraph = undefined;
      if (skippedDepth === undefined) output.push(line);
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.+?)\s*#*$/);
    if (heading) {
      const depth = heading[1].length;
      if (skippedDepth !== undefined && depth > skippedDepth) continue;
      skippedDepth = undefined;
      editorialParagraph = undefined;
      if (/^(?:이번 다이제스트 기준|활용 가이드|검토 기록(?:\s*[—–-].*)?)$/.test(heading[2])) {
        skippedDepth = depth;
        continue;
      }
      if (/^검증 및 보강\s*[—–-]/.test(heading[2])) line = `${heading[1]} 추가 설명`;
      if (heading[2] === '확인한 자료') line = `${heading[1]} 참고 자료`;
    }
    if (skippedDepth !== undefined) continue;
    if (line.trim() === '**검토 초점 · 직접 적용 결과가 아닌 편집 제안**') {
      editorialParagraph = 'pending';
      continue;
    }
    if (editorialParagraph) {
      if (!line.trim()) {
        if (editorialParagraph === 'body') editorialParagraph = undefined;
        continue;
      }
      if (/^(?:>|[-*+]\s|\d+\.\s)/.test(line)) editorialParagraph = undefined;
      else { editorialParagraph = 'body'; continue; }
    }
    if (line.trim() === '**검토 시점 후속 확인**') continue;
    if (/^- (?:리뉴얼 검토일|확인할 점\(자동 분류\)):/.test(line)) continue;
    line = line.replace(/^- 보강 원고:/, '- 관련 글:');
    output.push(line);
  }
  return output.join('\n');
}
