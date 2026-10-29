#!/usr/bin/env python3
"""Check reserved geometry and loading attributes of public article assets offline."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class ArticleImages(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'img' and any('prose' in classes for _, classes in self.stack):
            self.images.append(values)
        if tag not in VOID:
            self.stack.append((tag, values.get('class', '').split()))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def validate_image(image, root):
    src = image.get('src', '')
    if not src.startswith('/assets/'):
        return False
    root = Path(root).resolve()
    path = (root / unquote(urlsplit(src).path).lstrip('/')).resolve()
    if not path.is_relative_to(root / 'assets') or not path.is_file():
        raise ValueError('Local image is missing or leaves assets')
    for key in ('width', 'height'):
        if not re.fullmatch(r'[1-9][0-9]*', image.get(key, '')):
            raise ValueError(f'Local image needs a positive integer {key}')
    if image.get('loading') not in ('eager', 'lazy'):
        raise ValueError('Local image needs an explicit loading policy')
    if image.get('decoding') not in ('async', 'sync', 'auto'):
        raise ValueError('Local image needs an explicit decoding policy')
    if path.suffix.lower() == '.svg':
        svg = ET.parse(path).getroot()
        box = svg.get('viewBox', '').replace(',', ' ').split()
        if len(box) == 4:
            actual_width, actual_height = float(box[2]), float(box[3])
            width, height = int(image['width']), int(image['height'])
            # Allow one displayed pixel of rounding when an author scales an image.
            if actual_width <= 0 or actual_height <= 0 or abs(width * actual_height - height * actual_width) > max(actual_width, actual_height):
                raise ValueError('SVG display dimensions distort its viewBox ratio')
    return True


def check(root):
    root = Path(root)
    articles = images = 0
    for path in root.rglob('*.html'):
        parser = ArticleImages()
        parser.feed(path.read_text(encoding='utf-8'))
        count = 0
        for image in parser.images:
            try:
                count += validate_image(image, root)
            except (ValueError, ET.ParseError) as error:
                raise ValueError(f'{path.relative_to(root)}: {image.get("src")}: {error}') from error
        articles += count > 0
        images += count
    if not images:
        raise ValueError('No local article images found; check the build directory')
    return {'articlesWithImages': articles, 'localArticleImages': images}


if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--dist', type=Path, default=Path('dist'))
    args = arguments.parse_args()
    print('[ok] Reserved local image geometry and loading attributes: ' + json.dumps(check(args.dist)))
