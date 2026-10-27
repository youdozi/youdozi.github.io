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


if __name__ == '__main__':
    unittest.main()
