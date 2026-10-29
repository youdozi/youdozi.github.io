import tempfile
from pathlib import Path
import unittest
from check_article_images import ArticleImages, validate_image, check


class ArticleImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'assets').mkdir()
        (self.root / 'assets/example.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 240"/>')
        self.image = {'src': '/assets/example.svg', 'width': '120', 'height': '240', 'loading': 'eager', 'decoding': 'async'}

    def test_geometry_policy_and_scaled_aspect_ratio(self):
        self.assertTrue(validate_image(self.image, self.root))
        self.assertTrue(validate_image(dict(self.image, width='60', height='120'), self.root))
        for update in ({'width': '0'}, {'height': ''}, {'width': '50%'}, {'height': '120'}, {'loading': ''}, {'decoding': ''}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                validate_image(dict(self.image, **update), self.root)

    def test_scope_and_path_safety(self):
        self.assertFalse(validate_image({'src': 'https://example.invalid/image.svg'}, self.root))
        for src in ('/assets/missing.svg', '/assets/../../outside.svg', '/assets/..%2foutside.svg'):
            with self.subTest(src=src), self.assertRaises(ValueError):
                validate_image(dict(self.image, src=src), self.root)
        outside = self.root / 'outside.svg'
        outside.write_text('<svg/>')
        (self.root / 'assets/alias.svg').symlink_to(outside)
        with self.assertRaises(ValueError):
            validate_image(dict(self.image, src='/assets/alias.svg'), self.root)

    def test_only_rendered_prose_images_are_counted(self):
        parser = ArticleImages()
        parser.feed('<img src="/outside.svg"><article><div class="prose"><p><img src="/assets/example.svg"></p><pre>&lt;img src="code.svg"&gt;</pre></div></article>')
        self.assertEqual(parser.images, [{'src': '/assets/example.svg'}])

    def test_build_gate_rejects_missing_dimensions_and_empty_builds(self):
        with self.assertRaisesRegex(ValueError, 'No local'):
            check(self.root)
        attributes = ' '.join(f'{key}="{value}"' for key, value in self.image.items())
        page = self.root / 'index.html'
        page.write_text('<div class="prose"><img ' + attributes + '></div>')
        self.assertEqual(check(self.root), {'articlesWithImages': 1, 'localArticleImages': 1})
        page.write_text('<div class="prose"><img src="/assets/example.svg"></div>')
        with self.assertRaisesRegex(ValueError, 'width'):
            check(self.root)
