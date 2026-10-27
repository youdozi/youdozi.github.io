#!/usr/bin/env python3
"""Build accessible static flow diagrams from reviewed bilingual source data."""
import argparse
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

SOURCE = Path('content/diagrams/algorithms.json')
WORKFLOW_SOURCE = Path('content/diagrams/workflows.json')
STRATEGY_SOURCE = Path('content/diagrams/query-strategies.json')
PUBLICATION_SOURCE = Path('content/diagrams/publication.json')
RUBY_SOURCE = Path('content/diagrams/ruby-environment.json')
JENKINS_SOURCE = Path('content/diagrams/jenkins.json')
OUTPUT = Path('public/assets/diagrams')
LANGUAGES = ('en', 'ko')


def validate(data):
    if data.get('version') != 1 or not isinstance(data.get('diagrams'), list) or not data['diagrams']:
        raise ValueError('Expected a nonempty version1 diagram collection')
    keys = set()
    for item in data['diagrams']:
        key = item.get('key', '')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:[-.][a-z0-9]+)*', key) or key in keys:
            raise ValueError('Expected unique, safe article keys')
        keys.add(key)
        for field in ('title', 'description'):
            if set(item.get(field, {})) != set(LANGUAGES) or not all(isinstance(v, str) and v.strip() for v in item[field].values()):
                raise ValueError('Every diagram needs localized titles and descriptions')
        steps = item.get('steps', [])
        if not 2 <= len(steps) <= 10:
            raise ValueError('Expected2..10 readable flow steps')
        for step in steps:
            if step.get('kind') not in ('process', 'condition', 'result'):
                raise ValueError('Unknown step kind')
            for lang in LANGUAGES:
                lines = step.get(lang)
                if not isinstance(lines, list) or not 1 <= len(lines) <= 3 or not all(isinstance(line, str) and line.strip() for line in lines):
                    raise ValueError('Each step needs1..3 nonempty localized lines')
        for step in steps:
            if 'branch' in step:
                branch = step['branch']
                if (step['kind'] != 'condition' or item.get('loop') is not None or not isinstance(branch, dict)
                        or not {'exit','continue'} <= set(branch) or set(branch) - {'exit','continue','outcome'}
                        or branch.get('outcome','error') not in ('error','complete')):
                    raise ValueError('Exit branches require a condition and no overlapping loop')
                for field in ('exit','continue'):
                    labels = branch[field]
                    if (not isinstance(labels, dict) or set(labels) != set(LANGUAGES)
                            or not all(isinstance(v,str) and v.strip() and len(v)<=12 for v in labels.values())):
                        raise ValueError('Expected short localized branch labels')
        if 'codeContract' in item:
            contracts = item['codeContract']
            if not isinstance(contracts, list) or not contracts:
                raise ValueError('Expected nonempty code requirements')
            for contract in contracts:
                if (not isinstance(contract, dict) or contract.get('language') not in ('java','sh','groovy','python','xml','javascript','ruby')
                        or not isinstance(contract.get('contains'), str) or not contract['contains'].strip()):
                    raise ValueError('Invalid code language or required snippet')
        loop = item.get('loop')
        if loop is not None:
            if (type(loop.get('from')) is not int or type(loop.get('to')) is not int
                    or not 0 <= loop['to'] < loop['from'] < len(steps)
                    or set(loop.get('label', {})) != set(LANGUAGES)
                    or not all(isinstance(s,str) and s.strip() for s in loop['label'].values())):
                raise ValueError('Invalid loop endpoints or localized labels')
    return data


def render(item, language):
    if language not in LANGUAGES:
        raise ValueError('Unsupported diagram language')
    height = 105 + 126 * len(item['steps'])
    title, description = escape(item['title'][language]), escape(item['description'][language])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 {height}" width="420" height="{height}" role="img" aria-labelledby="title description" xml:lang="{language}">',
        f'<title id="title">{title}</title><desc id="description">{description}</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2b6044"/></marker></defs>',
        '<rect width="100%" height="100%" rx="12" fill="#f6f6f0"/>',
        '<g font-family="system-ui,sans-serif" fill="#202923">',
        f'<text x="210" y="39" text-anchor="middle" font-size="20" font-weight="650">{title}</text>']
    for i, step in enumerate(item['steps']):
        y = 76 + i * 126
        color = {'process':'#ffffff', 'condition':'#fff5da', 'result':'#e3efdf'}[step['kind']]
        radius = 22 if step['kind'] == 'result' else 7
        parts.append(f'<rect x="20" y="{y}" width="320" height="86" rx="{radius}" fill="{color}" stroke="#7b8d79" stroke-width="1.5"/>')
        for n, line in enumerate(step[language]):
            text_y = y + 43 + (n - (len(step[language]) - 1) / 2) * 24 + 6
            parts.append(f'<text x="180" y="{text_y:g}" text-anchor="middle" font-size="16">{escape(line)}</text>')
        if (branch := step.get('branch')) is not None:
            parts.append(f'<path d="M 342 {y+43} H 369" fill="none" stroke="#2b6044" stroke-width="2" marker-end="url(#arrow)"/>')
            terminal_color = '#2b6044' if branch.get('outcome') == 'complete' else '#8c3a32'
            terminal_symbol = '✓' if branch.get('outcome') == 'complete' else '×'
            parts.append(f'<circle cx="384" cy="{y+43}" r="12" fill="{terminal_color}"/>')
            parts.append(f'<text x="384" y="{y+49}" text-anchor="middle" font-size="19" fill="white">{terminal_symbol}</text>')
            parts.append(f'<text x="384" y="{y+76}" text-anchor="middle" font-size="10">{escape(branch["exit"][language])}</text>')
            if i < len(item['steps'])-1:
                parts.append(f'<text x="193" y="{y+111}" font-size="12">{escape(branch["continue"][language])}</text>')
        if i < len(item['steps']) - 1:
            parts.append(f'<path d="M 180 {y + 87} V {y + 120}" fill="none" stroke="#2b6044" stroke-width="2" marker-end="url(#arrow)"/>')
    if (loop := item.get('loop')) is not None:
        start = 119 + loop['from'] * 126
        end = 119 + loop['to'] * 126
        parts.append(f'<path d="M 342 {start} H 386 V {end} H 342" fill="none" stroke="#2b6044" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrow)"/>')
        parts.append(f'<text x="389" y="{(start+end)/2:g}" font-size="13">{escape(loop["label"][language])}</text>')
    parts.append('</g></svg>\n')
    return ''.join(parts)


def validate_articles(data, posts=Path('src/content/posts')):
    for item in data['diagrams']:
        for lang in LANGUAGES:
            article = (posts / lang / (item['key'] + '.md')).read_text()
            image = f'/assets/diagrams/{item["key"]}-{lang}.svg'
            if not re.search(r'!\[[^\]\n]+\]\(' + re.escape(image) + r'\)', article):
                raise ValueError(f'Missing localized diagram alt/link: {lang}/{item["key"]}')
            contracts = item.get('codeContract', [{'language':'java','contains':'public class Solution'}])
            blocks = re.findall(r'^```([a-z]+)\n([\s\S]*?)^```[ \t]*$', article, re.M)
            for contract in contracts:
                if not any(language == contract['language'] and contract['contains'] in code for language,code in blocks):
                    raise ValueError(f'Missing required {contract["language"]} code: {lang}/{item["key"]}')


def load_sources(paths=(SOURCE, WORKFLOW_SOURCE, STRATEGY_SOURCE, PUBLICATION_SOURCE, RUBY_SOURCE, JENKINS_SOURCE)):
    combined = {'version':1, 'diagrams':[]}
    for path in paths:
        combined['diagrams'].extend(validate(json.loads(Path(path).read_text()))['diagrams'])
    # Detect duplicate article keys across independently maintained source files.
    return validate(combined)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate diagram sources and paired articles without writing assets')
    args = parser.parse_args()
    data = load_sources()
    validate_articles(data)
    if not args.check:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        for item in data['diagrams']:
            for lang in LANGUAGES:
                (OUTPUT / f'{item["key"]}-{lang}.svg').write_text(render(item, lang))
    print(f'[ok] {len(data["diagrams"])} paired flow sources and code requirements checked; ' + ('no files written.' if args.check else f'{len(data["diagrams"])*2} static SVG diagrams generated.'))


if __name__ == '__main__':
    main()
