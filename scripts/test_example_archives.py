from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import build_example_archives as examples


class ExampleArchiveTests(unittest.TestCase):
    def test_all_paired_projects_have_identical_code_and_localized_provenance(self):
        recipes = examples.catalog()
        self.assertEqual(len(recipes), 14)
        for recipe in recipes:
            _, code = examples.project_files(recipe, 'en')
            self.assertEqual(code, examples.project_files(recipe, 'ko')[1])
            for language in examples.LANGUAGES:
                blob = examples.archive_bytes(recipe, language)
                self.assertEqual(blob, examples.archive_bytes(recipe, language))
                members = examples.verified_members(blob, recipe, language)
                provenance = json.loads(members['PROVENANCE.json'])
                self.assertIn(f'/{language}/posts/{recipe["key"]}/', provenance['article'])
                self.assertEqual(provenance['sourceSha256'], examples.digest(examples.article(examples.ROOT, recipe, language)[0]))
                self.assertIn(recipe['commands'], members['README.txt'].decode())
                for name, content in members.items():
                    if name != 'PROVENANCE.json':
                        self.assertEqual(provenance['files'][name], examples.digest(content))
                self.assertTrue(all(members[name] == content for name, content in code.items()))

    def test_archive_tampering_missing_files_duplicate_members_and_symlinks_fail(self):
        recipe = next(r for r in examples.catalog() if r['key'].endswith('version-compare'))
        members = examples.archive_files(recipe, 'en')
        for scenario in ('changed', 'missing', 'extra', 'duplicate', 'symlink'):
            stream = BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                for name, content in members.items():
                    if scenario == 'missing' and name.endswith('.sh'):
                        continue
                    info = zipfile.ZipInfo(name); info.create_system = 3
                    info.external_attr = (0o120777 if scenario == 'symlink' else 0o100644) << 16
                    archive.writestr(info, content + b'\nchanged' if scenario == 'changed' else content)
                if scenario == 'extra': archive.writestr('../escape', b'bad')
                if scenario == 'duplicate':
                    with self.assertWarns(UserWarning): archive.writestr(next(iter(members)), b'bad')
            with self.assertRaises(ValueError): examples.verified_members(stream.getvalue(), recipe, 'en')

    def test_ambiguous_sources_future_articles_and_ineligible_review_states_fail(self):
        recipe = next(r for r in examples.catalog() if r['key'].endswith('jdk-21-release'))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / f'src/content/posts/en/{recipe["key"]}.md'
            target.parent.mkdir(parents=True)
            source = (examples.ROOT / target.relative_to(root)).read_text()
            for text in (source + '\n### `Jdk21Example.java`\n\n```java\nbad\n```\n',
                         source.replace('reviewStatus: revised', 'reviewStatus: example'),
                         source.replace('reviewStatus: revised', 'reviewStatus: "revised'),
                         source.replace('2026-10-27T03:19:18+00:00', '2999-01-01T00:00:00+00:00')):
                self.assertNotEqual(text, source)
                target.write_text(text)
                with self.assertRaises(ValueError): examples.archive_bytes(recipe, 'en', root)

    def test_path_escape_duplicate_paths_and_changed_inline_setup_fail(self):
        for path in ('../escape', '/escape', 'a/../b', 'a\\b', 'a//b', './file', 'C:/file'):
            with self.assertRaises(ValueError): examples.safe_path(path)
        recipe = deepcopy(examples.catalog()[0]); recipe['files'].append(recipe['files'][0])
        with self.assertRaises(ValueError): examples.archive_bytes(recipe, 'en')
        recipe = deepcopy(next(r for r in examples.catalog() if r['key'].endswith('test-webclient')))
        recipe['inlineFiles'][0]['value'] = "rootProject.name = 'unrecorded'"
        with self.assertRaises(ValueError): examples.archive_bytes(recipe, 'en')

    def test_generation_retains_unrelated_files_and_published_checks_detect_stale_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            assets = root / 'assets/examples'; assets.mkdir(parents=True)
            stale = assets / '2000-01-01-retired-en.zip'; stale.write_bytes(b'retired')
            marker = assets / 'unrelated.txt'; marker.write_text('keep')
            first = examples.generate(assets)
            self.assertFalse(stale.exists()); self.assertEqual(marker.read_text(), 'keep')
            self.assertEqual(first, examples.generate(assets))
            marker.unlink()
            for recipe in examples.catalog():
                for language in examples.LANGUAGES:
                    target = root / language / 'posts' / recipe['key'] / 'index.html'
                    target.parent.mkdir(parents=True)
                    target.write_text(f'<a class="example-download" download href="/assets/examples/{recipe["key"]}-{language}.zip">Files</a>')
            self.assertEqual(examples.check_dist(root)['articleDownloadLinks'], 2 * len(examples.catalog()))
            next(assets.glob('*.zip')).write_bytes(b'broken')
            with self.assertRaises((ValueError, zipfile.BadZipFile)): examples.check_dist(root)

    def test_execution_extraction_rejects_a_disagreement_with_independent_code(self):
        recipe = next(r for r in examples.catalog() if r['key'].endswith('version-compare'))
        _, code = examples.project_files(recipe, 'en')
        with tempfile.TemporaryDirectory() as directory:
            examples.extract_example(recipe['key'], directory, {name: body.decode().removesuffix('\n') for name, body in code.items()})
            self.assertEqual((Path(directory) / 'version-compare.sh').read_bytes(), code['version-compare.sh'])
            with self.assertRaises(ValueError):
                examples.extract_example(recipe['key'], directory, {'version-compare.sh': 'changed'})


if __name__ == '__main__':
    unittest.main()
