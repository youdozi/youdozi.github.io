import copy
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

import build_algorithm_diagrams as diagrams


class AlgorithmDiagramsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(diagrams.SOURCE.read_text())

    def test_registered_articles_have_localized_diagrams_and_complete_code(self):
        diagrams.validate(self.data)
        diagrams.validate_articles(self.data)
        with tempfile.TemporaryDirectory() as directory:
            posts = Path(directory)
            for lang in diagrams.LANGUAGES:
                folder = posts / lang
                folder.mkdir()
                for item in self.data['diagrams']:
                    (folder / (item['key'] + '.md')).write_text((Path('src/content/posts') / lang / (item['key'] + '.md')).read_text())
            target = posts / 'ko' / (self.data['diagrams'][0]['key'] + '.md')
            for text in [target.read_text().replace('![', '![' + '](' + '/missing' + ')', 1), target.read_text().replace('public class Solution', 'class Partial')]:
                target.write_text(text)
                with self.assertRaises(ValueError):
                    diagrams.validate_articles(self.data, posts)

    def test_unsafe_duplicate_and_incomplete_sources_fail_before_asset_generation(self):
        for mutation in ['path', 'duplicate', 'missing-translation', 'bad-loop']:
            data = copy.deepcopy(self.data)
            first = data['diagrams'][0]
            if mutation == 'path': first['key'] = '../../outside'
            elif mutation == 'duplicate': data['diagrams'].append(copy.deepcopy(first))
            elif mutation == 'missing-translation': del first['steps'][0]['ko']
            else: first['loop'] = {'from':1,'to':99,'label':{'en':'Yes','ko':'예'}}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                diagrams.validate(data)

    def test_svg_escapes_text_preserves_languages_and_has_no_external_execution(self):
        item = copy.deepcopy(self.data['diagrams'][0])
        item['title']['en'] = 'A < B & "C"'
        item['steps'][0]['en'] = ['<script>alert(1)</script>']
        ns = {'s':'http://www.w3.org/2000/svg'}
        for lang in diagrams.LANGUAGES:
            svg = diagrams.render(item, lang)
            tree = ET.fromstring(svg)
            self.assertEqual(tree.attrib['role'], 'img')
            self.assertEqual(tree.attrib['{http://www.w3.org/XML/1998/namespace}lang'], lang)
            self.assertEqual(tree.find('s:title',ns).text, item['title'][lang])
            self.assertEqual(tree.find('s:desc',ns).text, item['description'][lang])
            self.assertEqual(tree.findall('.//s:script',ns), [])
            self.assertNotIn('href=',svg)
            self.assertEqual(diagrams.render(item, lang),svg)

    def test_loop_targets_and_localized_step_counts_share_one_structure(self):
        for item in self.data['diagrams']:
            for lang in diagrams.LANGUAGES:
                tree = ET.fromstring(diagrams.render(item,lang))
                labels=[e.text for e in tree.findall('.//{*}text')]
                for step in item['steps']:
                    for line in step[lang]: self.assertIn(line,labels)
                if 'loop' in item:
                    self.assertIn(item['loop']['label'][lang],labels)
                    self.assertEqual(len(tree.findall('.//{*}path[@stroke-dasharray]')),1)


    def test_workflow_contract_requires_code_in_the_declared_fence_language(self):
        data = {'version':1,'diagrams':[copy.deepcopy(json.loads(diagrams.WORKFLOW_SOURCE.read_text())['diagrams'][0])]}
        diagrams.validate(data)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            item=data['diagrams'][0]
            for lang in diagrams.LANGUAGES:
                folder=root/lang;folder.mkdir()
                source=(Path('src/content/posts')/lang/(item['key']+'.md')).read_text()
                (folder/(item['key']+'.md')).write_text(source)
            diagrams.validate_articles(data, root)
            target=root/'en'/(item['key']+'.md')
            # Marker in prose or a different code language cannot satisfy sh code.
            source=target.read_text().replace('```sh', '```text')
            target.write_text(source+'\n./gradlew test\n')
            with self.assertRaises(ValueError):diagrams.validate_articles(data,root)
        for contract in [[],[{'language':'html','contains':'anything'}],[{'language':'sh','contains':''}]]:
            broken=copy.deepcopy(data);broken['diagrams'][0]['codeContract']=contract
            with self.assertRaises(ValueError):diagrams.validate(broken)

    def test_source_loading_detects_collisions_between_collections(self):
        with tempfile.TemporaryDirectory() as directory:
            first=Path(directory)/'first.json';second=Path(directory)/'second.json'
            first.write_text(json.dumps(self.data));second.write_text(json.dumps(self.data))
            with self.assertRaises(ValueError):diagrams.load_sources([first,second])

    def test_all_registered_workflows_render_localized_assets_and_keep_algorithm_contracts(self):
        data=diagrams.load_sources()
        diagrams.validate_articles(data)
        self.assertEqual(len(data['diagrams']),sum(len(json.loads(path.read_text())['diagrams']) for path in [diagrams.SOURCE,diagrams.WORKFLOW_SOURCE,diagrams.STRATEGY_SOURCE,diagrams.PUBLICATION_SOURCE,diagrams.RUBY_SOURCE]))
        for item in data['diagrams']:
            for lang in diagrams.LANGUAGES:
                tree=ET.fromstring(diagrams.render(item,lang))
                self.assertEqual(tree.find('{*}title').text,item['title'][lang])
                self.assertEqual(tree.find('{*}desc').text,item['description'][lang])
                self.assertFalse(tree.findall('.//{*}script'))


    def test_exit_branches_preserve_both_locales_and_reject_overlapping_loops(self):
        source=json.loads(diagrams.WORKFLOW_SOURCE.read_text())
        item=copy.deepcopy(next(i for i in source['diagrams'] if any('branch' in s for s in i['steps'])))
        for lang in diagrams.LANGUAGES:
            tree=ET.fromstring(diagrams.render(item,lang))
            branches=[s['branch'] for s in item['steps'] if 'branch' in s]
            self.assertEqual(len(tree.findall('.//{*}circle')),len(branches))
            labels=[e.text for e in tree.findall('.//{*}text')]
            for branch in branches:
                self.assertIn(branch['exit'][lang],labels)
                self.assertIn(branch['continue'][lang],labels)
        broken=copy.deepcopy(item);broken['loop']={'from':2,'to':0,'label':{'en':'Yes','ko':'예'}}
        with self.assertRaises(ValueError):diagrams.validate({'version':1,'diagrams':[broken]})
        broken=copy.deepcopy(item)
        branch=next(s['branch'] for s in broken['steps'] if 'branch' in s)
        del branch['exit']['ko']
        with self.assertRaises(ValueError):diagrams.validate({'version':1,'diagrams':[broken]})


    def test_existing_dotted_article_slug_is_safe_but_path_controls_are_rejected(self):
        item=copy.deepcopy(next(i for i in json.loads(diagrams.WORKFLOW_SOURCE.read_text())['diagrams'] if i['key']=='2021-07-23-app-diagrams.net'))
        diagrams.validate({'version':1,'diagrams':[item]})
        for key in ['2021-07-23-app..diagrams','2021-07-23-app/../diagrams','2021-07-23-app%2ediagrams','2021-07-23-app.']:
            item['key']=key
            with self.subTest(key=key),self.assertRaises(ValueError):
                diagrams.validate({'version':1,'diagrams':[item]})


    def test_successful_early_return_is_distinct_from_an_error_terminal(self):
        source=json.loads(diagrams.WORKFLOW_SOURCE.read_text())
        item=copy.deepcopy(next(i for i in source['diagrams'] if i['key']=='2021-07-20-http-status-test'))
        diagrams.validate({'version':1,'diagrams':[item]})
        for lang in diagrams.LANGUAGES:
            tree=ET.fromstring(diagrams.render(item,lang))
            labels=[e.text for e in tree.findall('.//{*}text')]
            self.assertIn('✓',labels);self.assertNotIn('×',labels)
            self.assertEqual(tree.find('.//{*}circle').get('fill'),'#2b6044')
        branch=next(s['branch'] for s in item['steps'] if 'branch' in s)
        branch['outcome']='unknown'
        with self.assertRaises(ValueError):diagrams.validate({'version':1,'diagrams':[item]})


if __name__ == '__main__':
    unittest.main()
