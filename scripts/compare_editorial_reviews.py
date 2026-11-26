"""Compare providers on published articles without writing site content."""

import argparse
import json
from pathlib import Path

import fetch_news as news


def main() -> None:
    parser = argparse.ArgumentParser(description='Compara a revisão de português de duas APIs.')
    parser.add_argument('--output', type=Path, default=Path('comparacao-revisao.json'))
    args = parser.parse_args()
    if not news.OPENAI_API_KEY or not news.GEMINI_API_KEY:
        raise SystemExit('A comparação requer os secrets OPENAI_API_KEY e GEMINI_API_KEY.')

    posts = json.loads(news.POSTS_JSON.read_text(encoding='utf-8'))
    if not posts:
        raise SystemExit('A edição atual não tem matérias para comparar.')
    comparisons = []
    for post in posts[:5]:
        title = post['title_pt']
        summary = post['sub_pt']
        facts = post.get('highlights_pt', [])[:3]
        body = post['body_pt']
        comparisons.append({
            'slug': post['slug'],
            'original': {'title': title, 'summary': summary, 'facts': facts, 'body': body},
            'gemini': news.review_portuguese_content(title, summary, facts, body, provider='gemini'),
            'openai': news.review_portuguese_content(title, summary, facts, body, provider='openai'),
        })

    args.output.write_text(json.dumps({
        'modelos': {'gemini': news.GEMINI_MODEL, 'openai': news.OPENAI_MODEL},
        'materias': comparisons,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    paired = sum(all(post[provider]['status'] == 'success' for provider in ('gemini', 'openai'))
                 for post in comparisons)
    print(f'{paired}/{len(comparisons)} matérias revisadas pelos dois modelos. Relatório: {args.output}')
    if not paired:
        raise SystemExit('Nenhuma matéria teve duas revisões válidas para comparar.')


if __name__ == '__main__':
    main()
