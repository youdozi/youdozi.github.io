from copy import deepcopy
import json
import unittest

from check_learning_paths import LearningPage, SITE, validate


def page(path, body='', graph=None):
    result = LearningPage()
    result.feed('<html lang="en"><head><link rel="canonical" href="' + SITE + path + '">' +
                ('<script type="application/ld+json">' + json.dumps(graph) + '</script>' if graph else '') + '</head><body>' + body + '</body></html>')
    return result


def fixture():
    guide = '/en/categories/linux/'
    steps = ['/en/posts/first/', '/en/posts/middle/', '/en/posts/last/']
    pages = {SITE + '/en/guides/': page('/en/guides/', graph=[{'@type': 'ItemList', 'itemListElement': [{'url': SITE + guide}]}]),
             SITE + guide: page(guide, '<section class="algorithm-group"><ol>' + ''.join('<li><a href="' + p + '">' + p.split('/')[-2] + '</a></li>' for p in steps) + '</ol></section><section class="algorithm-extras"><a href="/en/posts/extra/">Extra</a></section>')}
    for index, path in enumerate(steps):
        links = '<a data-learning-guide href="' + guide + '">Shell guide</a>'
        for role, offset in [('previous', -1), ('next', 1)]:
            if 0 <= index + offset < len(steps):
                target = steps[index + offset]
                links += '<a data-learning-direction="' + role + '" href="' + target + '"><span>' + role + '</span><strong>' + target.split('/')[-2] + '</strong></a>'
        pages[SITE + path] = page(path, '<nav data-article-learning-path data-guide-url="' + guide + '" data-position="' + str(index + 1) + '" data-total="3" aria-label="Learning path">' + links + '</nav>')
    pages[SITE + '/en/posts/extra/'] = page('/en/posts/extra/')
    return pages, set(pages)


class LearningPathTests(unittest.TestCase):
    def test_all_visible_curated_steps_have_neighbors_and_extras_are_excluded(self):
        pages, sitemap = fixture()
        errors, counts = validate(pages, sitemap, ('en',))
        self.assertEqual(errors, [])
        self.assertEqual(counts, {'articles': 3, 'language:en': 3, 'neighborLinks': 4})
        pages[SITE + '/en/posts/first/'].paths.clear()
        self.assertIn('expected exactly one', '\n'.join(validate(pages, sitemap, ('en',))[0]))

    def test_translated_paths_reject_cross_language_neighbors_and_missing_index(self):
        pages, sitemap = fixture()
        # Exercise the same rendered contract with a Japanese edition, including URLs and attributes.
        pages = {url.replace('/en/', '/ja/'): deepcopy(value) for url, value in pages.items()}
        sitemap = {url.replace('/en/', '/ja/') for url in sitemap}
        for value in pages.values():
            value.language = 'ja'
            value.canonicals = [url.replace('/en/', '/ja/') for url in value.canonicals]
            value.jsonld = [raw.replace('/en/', '/ja/') for raw in value.jsonld]
            for step in value.guide_steps:
                step['url'] = step['url'].replace('/en/', '/ja/')
            for path in value.paths:
                path['attrs']['data-guide-url'] = path['attrs']['data-guide-url'].replace('/en/', '/ja/')
                for link in path['links']:
                    link['url'] = link['url'].replace('/en/', '/ja/')
        self.assertEqual(validate(pages, sitemap, ('ja',))[0], [])
        pages[SITE + '/ja/posts/middle/'].paths[0]['links'][1]['url'] = SITE + '/en/posts/first/'
        self.assertIn('without wrapping', '\n'.join(validate(pages, sitemap, ('ja',))[0]))
        del pages[SITE + '/ja/guides/']
        self.assertIn('missing or invalid guide index', '\n'.join(validate(pages, sitemap, ('ja',))[0]))

    def test_wrong_neighbors_wraps_and_wrong_titles_fail(self):
        pages, sitemap = fixture()
        middle = pages[SITE + '/en/posts/middle/'].paths[0]
        middle['links'][1]['url'] = SITE + '/en/posts/last/'
        self.assertIn('without wrapping', '\n'.join(validate(pages, sitemap, ('en',))[0]))
        pages, sitemap = fixture()
        pages[SITE + '/en/posts/first/'].paths[0]['links'][1]['text'] = 'Wrong title'
        self.assertIn('destination article titles', '\n'.join(validate(pages, sitemap, ('en',))[0]))

    def test_wrong_positions_unlisted_targets_and_stray_paths_fail(self):
        pages, sitemap = fixture()
        pages[SITE + '/en/posts/middle/'].paths[0]['attrs']['data-position'] = '1'
        pages[SITE + '/en/posts/extra/'].paths = deepcopy(pages[SITE + '/en/posts/first/'].paths)
        sitemap.remove(SITE + '/en/posts/last/')
        errors = '\n'.join(validate(pages, sitemap, ('en',))[0])
        self.assertIn('position, total', errors)
        self.assertIn('same-language public article', errors)
        self.assertIn('multi-article curated section', errors)


if __name__ == '__main__':
    unittest.main()
