"""Read the canonical JSON frontmatter emitted by the technical publication preparer."""
import json
from pathlib import Path


def technical_records(base):
    records = {}
    for path in sorted((Path(base) / 'src/content/technical-translations').glob('*/*.md')):
        parts = path.read_text().split('---\n', 2)
        if len(parts) != 3 or parts[0] or not parts[1].strip().startswith('{'):
            raise ValueError('Expected canonical technical publication JSON frontmatter')
        data = json.loads(parts[1])
        if data.get('state') != 'approved' or data.get('kind') != 'post':
            raise ValueError('Unapproved technical publication')
        url = f"/{data['language']}/posts/{data['routeSlug']}/"
        if url in records: raise ValueError('Duplicate technical publication URL')
        records[url] = {**data, 'body': parts[2]}
    return records
