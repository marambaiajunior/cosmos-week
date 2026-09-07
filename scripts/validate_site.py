#!/usr/bin/env python3
"""Offline validation of public routes, generated feeds and all HTML assets."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.github', 'node_modules', '__pycache__', 'dist', 'work'}
REQUIRED = [
    'index.html', 'en/index.html', 'arquivo/index.html', 'en/archive/index.html',
    'livro/vortice-maligno/index.html', 'livro/vortice-maligno/checklist/index.html',
    'posts.json', 'posts.js', 'all_posts.json', 'assets/data/posts-index.json',
    'assets/data/archive-index.json', 'feed.xml', 'sitemap.xml', 'robots.txt',
    'assets/img/livro/vortice-maligno-capa.webp',
]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.json_ld = [], [], []
        self.script = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if attrs.get('srcset'):
            self.refs.extend(part.strip().split()[0] for part in attrs['srcset'].split(',') if part.strip())
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.script = ''

    def handle_data(self, data):
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.json_ld.append(self.script)
            self.script = None


def main():
    errors = []
    for item in REQUIRED:
        if not (ROOT / item).is_file():
            errors.append(f'Arquivo ausente: {item}')
    if (ROOT / 'Livro').exists():
        errors.append('Pasta Livro com maiúscula: use somente livro (rota canônica).')
    files = [p for p in ROOT.rglob('*') if p.is_file() and not IGNORED.intersection(p.relative_to(ROOT).parts)]
    folded = {}
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        for candidate in [relative, *[p.as_posix() for p in Path(relative).parents if str(p) != '.']]:
            key = candidate.casefold()
            if key in folded and folded[key] != candidate:
                errors.append(f'Conflito de maiúsculas: {folded[key]} / {candidate}')
            folded[key] = candidate
    data = {}
    for name in ['posts.json', 'all_posts.json', 'assets/data/posts-index.json', 'assets/data/archive-index.json']:
        try:
            posts = json.loads((ROOT / name).read_text(encoding='utf-8'))
            if not isinstance(posts, list) or not posts:
                raise ValueError('lista vazia ou inválida')
            slugs = [p['slug'] for p in posts]
            if len(slugs) != len(set(slugs)):
                raise ValueError('slugs duplicados')
            data[name] = set(slugs)
            for slug in slugs:
                for prefix in ['noticia', 'en/news']:
                    if not (ROOT / prefix / slug / 'index.html').is_file():
                        errors.append(f'{name}: matéria ausente em {prefix}/{slug}/')
            if name.startswith('assets/') and any(any(k.startswith('body') or k == 'inline_images' for k in p) for p in posts):
                errors.append(f'{name}: conteúdo completo indevido no índice público')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'{name}: {exc}')
    for source, output in [('posts.json', 'assets/data/posts-index.json'), ('all_posts.json', 'assets/data/archive-index.json')]:
        if data.get(source) != data.get(output):
            errors.append(f'{output}: índice não corresponde à base {source}')

    pages = 0
    missing = Counter()
    for path in files:
        if path.suffix.lower() != '.html':
            continue
        pages += 1
        relative = path.relative_to(ROOT).as_posix()
        parser = PageParser()
        parser.feed(path.read_text(encoding='utf-8'))
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f'{relative}: IDs HTML duplicados')
        for payload in parser.json_ld:
            try:
                json.loads(payload)
            except ValueError:
                errors.append(f'{relative}: JSON-LD inválido')
        for ref in parser.refs:
            url = urlsplit(urljoin('https://www.cosmosweek.com/' + relative, ref))
            if url.hostname not in {'www.cosmosweek.com', 'cosmosweek.com'}:
                continue
            local = ROOT / unquote(url.path).lstrip('/')
            if local.is_dir():
                local /= 'index.html'
            if not local.is_file():
                missing[url.path] += 1
    errors.extend(f'Link/recurso ausente: {url} ({count} referências)' for url, count in missing.items())
    for name in ['feed.xml', 'sitemap.xml']:
        try:
            tree = ElementTree.parse(ROOT / name)
            if name == 'sitemap.xml':
                urls = [n.text for n in tree.findall('.//{*}loc')]
                if len(urls) < 100 or len(urls) != len(set(urls)):
                    errors.append('Sitemap incompleto ou com URLs duplicadas')
                for url in urls:
                    local = ROOT / unquote(urlsplit(url).path).lstrip('/')
                    if local.is_dir():
                        local /= 'index.html'
                    if not local.is_file():
                        errors.append(f'Sitemap aponta para página ausente: {url}')
        except (OSError, ElementTree.ParseError) as exc:
            errors.append(f'{name}: {exc}')
    errors = list(dict.fromkeys(errors))
    print(f'{pages} páginas HTML verificadas; {len(errors)} erro(s).')
    for error in errors[:50]:
        print(f'ERRO: {error}')
    if not errors:
        print('PASS: rotas, recursos locais, JSON-LD, índices bilíngues, RSS e sitemap.')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
