import test from 'node:test';
import assert from 'node:assert/strict';
import {searchContent} from '../src/lib/search-content.ts';
test('version comparisons survive across paragraphs and table rows',()=>{
 const text='Results: `1.1000 < 2.0`.\n\n| `1.2.0.0.1 > 1.2` | success |';
 assert.equal(searchContent(text),text);
 assert.equal(searchContent('left < right\n\nnext > previous'),'left < right\n\nnext > previous');
});
test('inline and fenced code preserve generic types and literal HTML',()=>{
 const text='Use `Map<String, Long>` and `<script>literal</script>`.\n\n````java\nList<String> values;\n```\n````\n\n~~~html\n<script>sample</script>\n~~~';
 assert.equal(searchContent(text),text);
});
test('actual HTML prose tags and hidden script bodies are excluded',()=>{
 const output=searchContent('<p>Visible <strong>words</strong>.</p>\n<script>hidden script</script><!-- hidden comment -->');
 assert.ok(output.includes('Visible'));assert.ok(output.includes('words'));
 assert.ok(!output.includes('<p>'));assert.ok(!output.includes('hidden'));
});
test('editorial removal still applies and input marker collisions do not corrupt code',()=>{
 const output=searchContent('Visible `a < b`. \u0000SEARCH_CODE\u0000\n\n## 검토 기록\nInternal advice.');
 assert.ok(output.includes('`a < b`'));assert.ok(output.includes('\u0000SEARCH_CODE\u0000'));assert.ok(!output.includes('Internal advice'));
});
