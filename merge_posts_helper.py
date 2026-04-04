#!/usr/bin/env python3
"""Mescla um lote novo de artigos com o arquivo atual do Cosmos Week.

Uso:
  python merge_posts_helper.py posts.json novo_lote.json

Saídas geradas no mesmo diretório:
  - merged_posts.json
  - merged_posts.js
"""
from __future__ import annotations
import json, sys
from pathlib import Path

def richness(post):
    return len(' '.join(str(post.get(k,'')) for k in [
        'title','title_pt','title_en','excerpt','excerpt_pt','excerpt_en','body','body_pt','body_en'
    ]))

def stamp(post):
    return str(post.get('lastModifiedIso') or post.get('publishedIso') or '')

def pick_best(a, b):
    if not a: return b
    if stamp(b) > stamp(a): return b
    if stamp(b) < stamp(a): return a
    return b if richness(b) >= richness(a) else a

def merge(existing, incoming):
    merged = {}
    for post in existing + incoming:
        slug = post.get('slug')
        if not slug:
            continue
        merged[slug] = pick_best(merged.get(slug), post)
    return sorted(merged.values(), key=lambda p: str(p.get('publishedIso','')), reverse=True)

def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    current_path = Path(sys.argv[1])
    incoming_path = Path(sys.argv[2])
    current = json.loads(current_path.read_text(encoding='utf-8'))
    incoming = json.loads(incoming_path.read_text(encoding='utf-8'))
    merged = merge(current, incoming)
    out_json = current_path.with_name('merged_posts.json')
    out_js = current_path.with_name('merged_posts.js')
    out_json.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
    out_js.write_text('window.postsData = ' + json.dumps(merged, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    print(f'Mesclado com sucesso: {len(merged)} artigos.')
    print(f'Arquivos gerados: {out_json.name}, {out_js.name}')

if __name__ == '__main__':
    main()
