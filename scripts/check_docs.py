"""Check static Pages references and displayed evidence using only the stdlib."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
        self.labels = []
        self.inputs = []
        self.image_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs['id'])
        for attr in ['href', 'src']:
            if attr in attrs:
                self.refs.append(attrs[attr])
        if tag == 'label':
            self.labels.append(attrs.get('for'))
        if tag == 'input':
            self.inputs.append(attrs['id'])
        if tag == 'img':
            assert attrs.get('alt'), 'Image missing descriptive alt text'
            self.image_count += 1


def main():
    source = (DOCS / 'index.html').read_text()
    page = Page()
    page.feed(source)
    local_count = 0
    for ref in page.refs:
        url = urlsplit(ref)
        if url.scheme:
            assert url.scheme == 'https', f'Unexpected remote protocol: {ref}'
            assert url.hostname not in ['localhost', '127.0.0.1'], ref
            continue
        assert not ref.startswith('/'), f'Domain-root link breaks project hosting: {ref}'
        if url.path:
            path = (DOCS / unquote(url.path)).resolve()
            assert path.is_relative_to(DOCS), f'Link escapes deployed directory: {ref}'
            assert path.is_file(), f'Missing local target: {ref}'
            local_count += 1
        if url.fragment and not url.path:
            assert url.fragment in page.ids, f'Missing section: {ref}'
    assert set(page.inputs) <= set(page.labels), 'Unlabeled preview controls'
    assert len(page.inputs) == 5
    assert page.image_count == 5
    assert (DOCS / '.nojekyll').is_file()
    assert 'Prediction interface preview' in source
    assert 'does not calculate predictions' in source
    assert not re.search(r'https?://(?:localhost|127\.0\.0\.1)|/Users/|/private/', source)
    metrics = json.loads((DOCS / 'assets/metrics.json').read_text())['metrics']
    for name, values in metrics.items():
        for key, value in values.items():
            digits = 4 if key == 'R2' else 3
            assert f'{value:.{digits}f}' in source, f'{name}/{key} differs from evidence'
    css = (DOCS / 'styles.css').read_text()
    for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)', css):
        assert (DOCS / ref).is_file(), f'Missing CSS asset: {ref}'
    assert '@media(max-width:760px)' in css.replace(' ', '')
    assert 'prefers-reduced-motion' in css
    print(f'PASS: {local_count} local references, {len(page.ids)} unique IDs, '
          f'{page.image_count} images, 5 labeled inputs, metric consistency and Pages paths.')


if __name__ == '__main__':
    main()
