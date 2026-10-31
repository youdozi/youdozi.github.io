import json
from pathlib import Path
import tempfile
import unittest
from xml.sax.saxutils import escape

from check_technical_preview import check, expected_paragraphs

KEY = 'es-2021-07-22-dot-product'
SLUG = '2021-07-22-dot-product'
URL = '/es/posts/' + SLUG + '/'
ASSET = '/assets/diagrams/technical/' + KEY + '.svg'
CODE = 'public class Solution {}'
BODY = '## Flujo\n\nMultiplica `a[i]` antes de sumar.\n\n![Flujo]('+ASSET+')\n\n```java\n'+CODE+'\n```\n'


class TechnicalPreviewTests(unittest.TestCase):
    def test_empty_legacy_anchor_is_layout_not_a_missing_paragraph(self):
        self.assertEqual(list(expected_paragraphs('<span id="legacy"></span>\n\nKept **contract**.\n')), ['kept contract.'])

    def test_literal_anchor_in_inline_code_is_still_visible_content(self):
        self.assertEqual(list(expected_paragraphs('Literal `<span id="literal"></span>` remains.\n')), ['literal <span id="literal"></span> remains.'])

    def fixture(self, base):
        path = base/f'src/content/technical-translations/es/{SLUG}.md'; path.parent.mkdir(parents=True)
        data = {'state':'approved','kind':'post','language':'es','translationKey':SLUG,'routeSlug':SLUG,'title':'Producto escalar','description':'Calcula productos.',
                'updatedAt':'2026-10-29T00:00:00+00:00','approval':{'kind':'render-fixture','reviewedBy':'AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL'}}
        path.write_text('---\n'+json.dumps(data)+'\n---\n'+BODY)
        (base/'.translation-preview-fixture.json').write_text(json.dumps({'fixtureOnly':True,'technicalFixtureKeys':[KEY]}))
        sitemap = []
        for lang in ('en','ko','es'):
            url = f'/{lang}/posts/{SLUG}/'; sitemap.append('<url><loc>https://youdozi.github.io'+url+'</loc></url>')
            path = base/('dist'+url+'index.html'); path.parent.mkdir(parents=True)
            alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="https://youdozi.github.io/{l}/posts/{SLUG}/">' for l in ('en','ko','es'))
            alts += f'<link rel="alternate" hreflang="x-default" href="https://youdozi.github.io/en/posts/{SLUG}/">'
            path.write_text(f'<html lang="{lang}"><head><link rel="canonical" href="https://youdozi.github.io{url}"><meta property="og:title" content="Producto escalar"><meta name="description" content="Calcula productos.">{alts}</head><body><article><h1>Producto escalar</h1><div class="prose"><h2>Flujo</h2><p>Multiplica <code>a[i]</code> antes de sumar.</p><p><img src="{ASSET}" alt="Flujo"></p><pre><code>{CODE}</code></pre></div></article></body></html>')
        asset = base/('dist'+ASSET); asset.parent.mkdir(parents=True); asset.write_text('<svg/>')
        (base/'dist/es/search-index.json').write_text(json.dumps([{'url':URL,'title':'Producto escalar','description':'Calcula productos.','content':BODY}]))
        (base/'dist/es/feed.xml').write_text(f'<rss xmlns:atom="http://www.w3.org/2005/Atom"><channel><item><link>https://youdozi.github.io{URL}</link><title>Producto escalar</title><description>Calcula productos.</description><atom:updated>2026-10-29T00:00:00Z</atom:updated></item></channel></rss>')
        (base/'dist/sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(sitemap)+'</urlset>')

    def test_full_paragraph_code_diagram_feed_and_counterparts(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            self.assertEqual(check(base)['fixtureEditions'],1)
            self.assertEqual(check(base)['completeParagraphsAndTableRows'],2)

    def test_hidden_paragraph_cannot_replace_visible_prose(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base);p=base/('dist'+URL+'index.html')
            p.write_text(p.read_text().replace('<p>Multiplica <code>a[i]</code> antes de sumar.</p>','<script>Multiplica a[i] antes de sumar.</script>'))
            with self.assertRaisesRegex(ValueError,'omits'):check(base)

    def test_inline_code_does_not_invent_a_space_before_punctuation(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            paths=[base/f'src/content/technical-translations/es/{SLUG}.md',base/('dist'+URL+'index.html'),base/'dist/es/search-index.json']
            for p in paths:p.write_text(p.read_text().replace(' antes de sumar.', '.'))
            self.assertEqual(check(base)['fixtureEditions'],1)

    def test_search_paragraph_and_java_code_changes_are_rejected(self):
        for surface in ('search','java'):
            with self.subTest(surface=surface),tempfile.TemporaryDirectory() as folder:
                base=Path(folder);self.fixture(base)
                p=base/('dist/es/search-index.json' if surface=='search' else 'dist'+URL+'index.html')
                p.write_text(p.read_text().replace('antes de sumar.','' ) if surface=='search' else p.read_text().replace(CODE,'public class Wrong {}'))
                with self.assertRaises(ValueError):check(base)

    def test_localized_table_rows_preserve_inline_commands_without_markdown_delimiters(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            table='\n\n| Invocación | Intérprete |\n| --- | --- |\n| `sh greet.sh NAME` | Lee el archivo. |\n'
            p=base/f'src/content/technical-translations/es/{SLUG}.md';p.write_text(p.read_text()+table)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('</div></article>','<table><tr><th>Invocación</th><th>Intérprete</th></tr><tr><td><code>sh greet.sh NAME</code></td><td>Lee el archivo.</td></tr></table></div></article>'))
            p=base/'dist/es/search-index.json';rows=json.loads(p.read_text());rows[0]['content']+=table;p.write_text(json.dumps(rows))
            self.assertEqual(check(base)['completeParagraphsAndTableRows'],4)

    def test_shell_and_json_fences_are_checked_instead_of_assuming_java(self):
        for language,code in [('sh',"printf 'ok'"),('json','{"ok":true}')]:
            with self.subTest(language=language),tempfile.TemporaryDirectory() as folder:
                base=Path(folder);self.fixture(base)
                paths=[base/f'src/content/technical-translations/es/{SLUG}.md',base/('dist'+URL+'index.html')]
                for p in paths:p.write_text(p.read_text().replace('```java','```'+language).replace(CODE,code))
                result=check(base)
                self.assertEqual(result['codeLanguages'],{language:1})
                self.assertEqual(result['localizedJavaExamples'],0)
                p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace(code,'changed code'))
                with self.assertRaisesRegex(ValueError,'code example'):check(base)

    def test_older_fixture_may_be_absent_from_the_latest_thirty_feed(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            original=json.loads((base/f'src/content/technical-translations/es/{SLUG}.md').read_text().split('---\n',2)[1])
            index=base/'dist/es/search-index.json';rows=json.loads(index.read_text());items=[]
            for i in range(31):
                slug=f'2026-10-29-newer-{i}'
                data={**original,'translationKey':slug,'routeSlug':slug,'updatedAt':'2026-10-29T01:00:00+00:00'}
                (base/f'src/content/technical-translations/es/{slug}.md').write_text('---\n'+json.dumps(data)+'\n---\nAnother article.')
                url=f'/es/posts/{slug}/';rows.append({'url':url,'title':'Another','content':'Another article.'})
                if i<30:items.append('<item><link>https://youdozi.github.io'+url+'</link></item>')
            index.write_text(json.dumps(rows))
            (base/'dist/es/feed.xml').write_text('<rss><channel>'+''.join(items)+'</channel></rss>')
            self.assertEqual(check(base)['rssEditions'],0)

    def test_missing_assets_feed_counterparts_and_forged_titles_are_rejected(self):
        for surface in ('asset','feed','alternate','title'):
            with self.subTest(surface=surface),tempfile.TemporaryDirectory() as folder:
                base=Path(folder);self.fixture(base)
                if surface=='asset':(base/('dist'+ASSET)).unlink()
                else:
                    p=base/('dist/es/feed.xml' if surface=='feed' else 'dist/ko/posts/'+SLUG+'/index.html' if surface=='alternate' else 'dist'+URL+'index.html')
                    p.write_text(p.read_text().replace('Calcula productos.','Wrong') if surface=='feed' else p.read_text().replace('hreflang="es"','hreflang="fr"') if surface=='alternate' else p.read_text().replace('<h1>Producto escalar</h1>','<h1>Wrong</h1>'))
                with self.assertRaises(ValueError):check(base)

    def test_supplementary_architecture_image_must_render_in_order_with_local_asset(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            extra='/assets/diagrams/technical/'+KEY+'-architecture.svg'
            p=base/f'src/content/technical-translations/es/{SLUG}.md'
            p.write_text(p.read_text()+'\n\n![Arquitectura]('+extra+')\n')
            p=base/('dist'+URL+'index.html')
            p.write_text(p.read_text().replace('</div></article>','<p><img src="'+extra+'" alt="Arquitectura"></p></div></article>'))
            asset=base/('dist'+extra);asset.write_text('<svg/>')
            self.assertEqual(check(base)['fixtureEditions'],1)
            asset.unlink()
            with self.assertRaisesRegex(ValueError,'diagram'):check(base)

    def test_numbered_list_items_are_visible_without_html_list_markers(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            listing='\n\n1. 入力を1回確認する。\n2. 完了後に出力する。\n'
            p=base/f'src/content/technical-translations/es/{SLUG}.md';p.write_text(p.read_text()+listing)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('</div></article>','<ol><li>入力を1回確認する。</li><li>完了後に出力する。</li></ol></div></article>'))
            p=base/'dist/es/search-index.json';rows=json.loads(p.read_text());rows[0]['content']+=listing;p.write_text(json.dumps(rows))
            self.assertEqual(check(base)['completeParagraphsAndTableRows'],4)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('<li>完了後に出力する。</li>',''))
            with self.assertRaisesRegex(ValueError,'omits a paragraph'):check(base)

    def test_api_fragment_parentheses_and_typographic_apostrophes_keep_complete_prose(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            paragraph="\n\nL'appel à [tryAcquire()](https://example.org/api#tryAcquire()) refuse le travail.\n"
            p=base/f'src/content/technical-translations/es/{SLUG}.md';p.write_text(p.read_text()+paragraph)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('</div></article>',"<p>L’appel à <a href='https://example.org/api#tryAcquire()'>tryAcquire()</a> refuse le travail.</p></div></article>"))
            p=base/'dist/es/search-index.json';rows=json.loads(p.read_text());rows[0]['content']+=paragraph;p.write_text(json.dumps(rows))
            self.assertEqual(check(base)['completeParagraphsAndTableRows'],3)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('refuse le travail.',''))
            with self.assertRaisesRegex(ValueError,'omits a paragraph'):check(base)

    def test_generic_type_in_inline_code_must_remain_visible(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            heading='\n\n## Permite `List<int>`?\n'
            p=base/f'src/content/technical-translations/es/{SLUG}.md';p.write_text(p.read_text()+heading)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('</div></article>','<h2>Permite <code>List&lt;int&gt;</code>?</h2></div></article>'))
            p=base/'dist/es/search-index.json';rows=json.loads(p.read_text());rows[0]['content']+=heading;p.write_text(json.dumps(rows))
            self.assertEqual(check(base)['completeParagraphsAndTableRows'],3)
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('List&lt;int&gt;','List'))
            with self.assertRaisesRegex(ValueError,'omits a paragraph'):check(base)

    def test_publication_mode_requires_real_approval_and_no_fixture_marker(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);self.fixture(base)
            with self.assertRaisesRegex(ValueError,'actual publication approval'):check(base,published=True)
            p=base/f'src/content/technical-translations/es/{SLUG}.md'
            p.write_text(p.read_text().replace('render-fixture','human').replace('AUTOMATED_RENDER_FIXTURE_NOT_HUMAN_APPROVAL','Publication authorizer'))
            (base/'.translation-preview-fixture.json').unlink()
            result=check(base,published=True)
            self.assertEqual(result['publishedEditions'],1)
            self.assertFalse(result['fixtureOnly'])
            p=base/('dist'+URL+'index.html');p.write_text(p.read_text().replace('antes de sumar.',''))
            with self.assertRaisesRegex(ValueError,'omits a paragraph'):check(base,published=True)
