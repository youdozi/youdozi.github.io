from pathlib import Path
import tempfile
import unittest
from content_maintenance import audit


class ContentMaintenanceTests(unittest.TestCase):
    def test_only_public_editions_count_and_gaps_do_not_invent_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sitemap.xml').write_text('<urlset/>')
            for language, key, extra in [('en', 'one', ''), ('ko', 'one', ''),
                                          ('en', 'example', '<meta name="robots" content="noindex">'),
                                          ('en', 'moved', '<meta http-equiv="refresh" content="0;url=/en/">')]:
                path = root / language / 'posts' / key / 'index.html'
                path.parent.mkdir(parents=True)
                path.write_text(f'<html lang="{language}"><head><link rel="canonical" href="https://youdozi.github.io/{language}/posts/{key}/">{extra}</head></html>')
            report = audit(root)
            self.assertEqual((report['topics'], report['publishedEditions'], report['missingEditions']), (1, 2, 6))
            self.assertEqual(report['translationGaps'][0]['missing'], ['zh-CN', 'ja', 'de', 'fr', 'ru', 'es'])

    def test_missing_or_empty_build_is_not_a_clean_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                audit(directory)
            (Path(directory) / 'sitemap.xml').write_text('<urlset/>')
            with self.assertRaises(ValueError):
                audit(directory)
