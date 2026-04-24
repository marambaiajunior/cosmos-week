"""Cosmos Week editorial refinement pass.

This script runs *after* the main feed ingestion pipeline and applies a second,
portal-specific editorial curation layer. Its purpose is to keep the site from
feeling like a raw automated aggregator by enforcing source diversity, removing
administrative and off-mission items, standardising excerpts and rebuilding the
published set from the best available candidates in the current and archive
snapshots.

Design goals:
  - reduce bureaucratic / service / profile-like entries;
  - preserve scientific seriousness and avoid clickbait;
  - improve headline/deck consistency without rewriting facts;
  - strengthen source taxonomy and editorial notes;
  - keep the output compatible with the existing Phase 1 front end.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import fetch_news as cw

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = Path(__file__).with_name('editorial_rules.json')

CATEGORY_ORDER = [
    'Astronomia', 'Cosmologia', 'Astrofísica', 'Exoplanetas',
    'Física', 'Biologia', 'Química', 'Ciências da Terra'
]

COVERAGE_LABELS = {
    'agency': {'pt': 'Fonte institucional', 'en': 'Institutional source'},
    'journal': {'pt': 'Artigo científico', 'en': 'Research paper'},
    'preprint': {'pt': 'Preprint', 'en': 'Preprint'},
    'news': {'pt': 'Jornalismo científico', 'en': 'Science journalism'},
}

COVERAGE_NOTES = {
    'agency': {
        'pt': 'Fonte primária institucional. Boa para anúncio inicial e contexto operacional, mas não substitui validação independente.',
        'en': 'Primary institutional source. Useful for first disclosure and operational context, but not a substitute for independent validation.',
    },
    'journal': {
        'pt': 'Artigo científico publicado, com lastro editorial e revisão por pares.',
        'en': 'Published scientific paper with editorial screening and peer review.',
    },
    'preprint': {
        'pt': 'Preprint em circulação técnica. Resultado provisório, ainda sem revisão por pares formal.',
        'en': 'Preprint in technical circulation. Preliminary result, not yet peer reviewed.',
    },
    'news': {
        'pt': 'Cobertura jornalística de ciência. Sempre que possível, vale conferir o paper, o release técnico ou a fonte primária citada.',
        'en': 'Science journalism coverage. When possible, verify the cited paper, technical release or primary source.',
    },
}

EVIDENCE_LABELS = {
    'institutional_update': {'pt': 'Atualização institucional', 'en': 'Institutional update'},
    'peer_reviewed': {'pt': 'Evidência revisada', 'en': 'Peer-reviewed evidence'},
    'preprint': {'pt': 'Resultado provisório', 'en': 'Preliminary result'},
    'journalistic': {'pt': 'Cobertura jornalística', 'en': 'Journalistic coverage'},
}


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding='utf-8'))


RULES = load_rules()
EXCLUDE_TITLE_PATTERNS = [re.compile(p, re.I) for p in RULES['exclude_title_patterns']]
DOWNGRADE_TEXT_PATTERNS = [re.compile(p, re.I) for p in RULES['downgrade_text_patterns']]
OBS_GUIDE_PATTERNS = [re.compile(p, re.I) for p in RULES['observation_guide_patterns']]
SCIENCE_SIGNAL_TERMS = tuple(RULES['science_signal_terms'])
PUBLIC_INTEREST_TERMS = tuple(RULES['public_interest_terms'])
GENERIC_PERSON_TERMS = tuple(RULES['generic_person_title_terms'])
TARGET_POST_COUNT = int(RULES.get('target_post_count', 40))
CATEGORY_FLOOR = int(RULES.get('category_floor', 2))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_source_name(name: str) -> str:
    clean = cw.collapse_ws(name or '')
    return RULES['source_aliases'].get(clean, clean)


def coverage_kind_for(post: dict) -> str:
    source = normalize_source_name(post.get('source') or '')
    if post.get('isPreprint') or post.get('sourceType') == 'preprint':
        return 'preprint'
    return RULES['source_coverage_kind'].get(source, 'agency')


def evidence_key_for_kind(kind: str) -> str:
    if kind == 'preprint':
        return 'preprint'
    if kind == 'journal':
        return 'peer_reviewed'
    if kind == 'news':
        return 'journalistic'
    return 'institutional_update'


def normalized_haystack(post: dict) -> str:
    bits = [
        post.get('title_en') or post.get('title') or '',
        post.get('sub_en') or post.get('sub') or '',
        post.get('excerpt_en') or post.get('excerpt') or '',
        post.get('source') or '',
        post.get('srcUrl') or '',
    ]
    return cw.normalize_text(' '.join(bits))


def title_en(post: dict) -> str:
    return cw.collapse_ws(post.get('title_en') or post.get('title') or '')


def title_pt(post: dict) -> str:
    return cw.collapse_ws(post.get('title_pt') or post.get('title') or '')


def likely_person_only_title(title: str) -> bool:
    words = [w for w in re.split(r'\s+', title.strip()) if w]
    if not (1 < len(words) <= 5):
        return False
    if not all(w[:1].isupper() for w in words if w[:1].isalpha()):
        return False
    low = cw.normalize_text(title)
    return not any(term in low for term in GENERIC_PERSON_TERMS)


def story_kind(post: dict) -> str:
    title = title_en(post).strip(' .')
    low_title = cw.normalize_text(title)
    hay = normalized_haystack(post)

    if any(p.search(low_title) for p in EXCLUDE_TITLE_PATTERNS):
        return 'drop'
    if likely_person_only_title(title):
        return 'drop'
    if len(title.split()) <= 4 and not any(term in low_title for term in SCIENCE_SIGNAL_TERMS + PUBLIC_INTEREST_TERMS):
        return 'drop'
    if any(p.search(low_title) for p in OBS_GUIDE_PATTERNS):
        return 'guide'
    if any(p.search(hay) for p in DOWNGRADE_TEXT_PATTERNS):
        return 'ops'
    return 'science'


def age_hours(post: dict) -> float:
    try:
        published = datetime.fromisoformat(str(post.get('publishedIso') or ''))
    except Exception:
        return 99999.0
    return max(0.0, (datetime.now(timezone.utc) - published).total_seconds() / 3600)


def refined_score(post: dict) -> int:
    score = int(post.get('score') or 0)
    hay = normalized_haystack(post)
    kind = coverage_kind_for(post)
    kind_story = story_kind(post)

    if kind == 'news':
        score -= 5
    elif kind == 'preprint':
        score -= 12

    if kind_story == 'guide':
        score -= 10
    elif kind_story == 'ops':
        score -= 24

    if any(term in hay for term in PUBLIC_INTEREST_TERMS):
        score += 6
    if any(term in hay for term in SCIENCE_SIGNAL_TERMS):
        score += 8

    hours = age_hours(post)
    if hours <= 48:
        score += 6
    elif hours <= 120:
        score += 3
    elif hours >= 240:
        score -= 4

    return max(0, min(100, score))


def smooth_title(text: str) -> str:
    text = cw.collapse_ws(text or '')
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = text.replace(' .', '.').replace(' ,', ',')
    return text


def sentence_safe_excerpt(text: str, limit: int, fallback: str = '') -> str:
    clean = cw.smooth_prose(cw.strip_html(text or ''))
    clean = re.sub(r'\s+', ' ', clean).strip()
    if not clean:
        clean = cw.smooth_prose(cw.strip_html(fallback or ''))
    if not clean:
        return ''

    sentences = [
        cw.collapse_ws(part) for part in re.split(r'(?<=[.!?])\s+', clean)
        if cw.collapse_ws(part)
    ]
    built: list[str] = []
    total = 0
    for sentence in sentences:
        sentence = sentence.rstrip(' .;,:') + '.'
        needed = len(sentence) + (1 if built else 0)
        if built and total + needed > limit:
            break
        if not built and len(sentence) > limit:
            clipped = sentence[:limit].rsplit(' ', 1)[0].rstrip(' .;,:')
            return clipped + '.' if clipped else cw.truncate(clean, limit)
        built.append(sentence)
        total += needed
        if total >= max(90, limit // 2):
            break
    return ' '.join(built) if built else cw.truncate(clean, limit)


def bulletize(text: str, limit: int = 145) -> str:
    cleaned = sentence_safe_excerpt(text, limit)
    cleaned = cleaned.rstrip('.')
    return cleaned if cleaned else cw.truncate(cw.smooth_prose(text or ''), limit)


def strip_highlight_prefix(text: str) -> str:
    return re.sub(r'^(Em foco|Detalhe|Leitura editorial|Focus|Detail|Editorial reading):\s+', '', cw.collapse_ws(text or ''), flags=re.I)


def significantly_different(a: str, b: str) -> bool:
    a_words = {w for w in re.findall(r'[\wÀ-ÿ]+', cw.normalize_text(a)) if len(w) > 3}
    b_words = {w for w in re.findall(r'[\wÀ-ÿ]+', cw.normalize_text(b)) if len(w) > 3}
    if not a_words or not b_words:
        return cw.normalize_text(a) != cw.normalize_text(b)
    overlap = len(a_words & b_words) / max(1, min(len(a_words), len(b_words)))
    return overlap < 0.72


def highlight_note(kind: str, lang: str) -> str:
    notes = {
        'pt': {
            'agency': 'Leitura editorial: release institucional, útil como fonte primária, mas não como validação independente.',
            'journal': 'Leitura editorial: estudo publicado, com base mais robusta que release ou preprint.',
            'preprint': 'Leitura editorial: resultado provisório, ainda sem revisão por pares formal.',
            'news': 'Leitura editorial: reportagem científica; quando possível, confira a fonte primária citada.',
        },
        'en': {
            'agency': 'Editorial reading: institutional release, useful as a primary source but not independent validation.',
            'journal': 'Editorial reading: published study, on firmer ground than a release or preprint.',
            'preprint': 'Editorial reading: provisional result, not yet formally peer reviewed.',
            'news': 'Editorial reading: science reporting; whenever possible, verify the cited primary source.',
        },
    }
    return notes['en' if lang == 'en' else 'pt'][kind]


def build_highlights(summary: str, facts: Iterable[str], kind: str, lang: str) -> list[str]:
    facts_clean = [strip_highlight_prefix(str(f)) for f in facts if cw.collapse_ws(str(f))]
    summary_line = bulletize(summary, 150)
    second_source = ''
    for fact in facts_clean:
        candidate = bulletize(fact, 145)
        low_candidate = cw.normalize_text(candidate)
        if any(marker in low_candidate for marker in ('leitura editorial', 'editorial reading', 'release institucional', 'journalistic coverage', 'resultado provisório', 'peer reviewed')):
            continue
        if candidate and significantly_different(candidate, summary_line):
            second_source = candidate
            break

    if lang == 'en':
        bullets = [f'Focus: {summary_line}']
        if second_source:
            bullets.append(f'Detail: {second_source}')
        bullets.append(highlight_note(kind, 'en'))
    else:
        bullets = [f'Em foco: {summary_line}']
        if second_source:
            bullets.append(f'Detalhe: {second_source}')
        bullets.append(highlight_note(kind, 'pt'))

    return cw.distinct_facts([cw.collapse_ws(b) for b in bullets], 3)


def build_highlights_wrapper(title: str, summary: str, facts: list[str], source_type: str, lang: str) -> list[str]:
    del title
    return build_highlights(summary or '', facts or [], source_type or 'news', lang)


def recalc_score_breakdown(post: dict, score: int, kind: str, kind_story: str) -> dict:
    base = dict(post.get('scoreBreakdown') or {})
    evidence = int(base.get('evidence', 0) or 0)
    relevance = int(base.get('relevance', 0) or 0)
    accessibility = int(base.get('accessibility', 0) or 0)
    novelty = int(base.get('novelty', 0) or 0)

    if kind == 'news':
        evidence = max(42, evidence - 18)
    elif kind == 'preprint':
        evidence = max(35, evidence - 25)
    elif kind == 'journal':
        evidence = max(evidence, 84)

    if kind_story == 'guide':
        relevance = max(30, relevance - 12)
    elif kind_story == 'ops':
        relevance = max(22, relevance - 24)

    if score >= 88:
        relevance = max(relevance, 84)
    elif score >= 78:
        relevance = max(relevance, 74)

    return {
        'source': max(0, min(100, int(base.get('source', 0) or 0))),
        'evidence': max(0, min(100, evidence)),
        'relevance': max(0, min(100, relevance)),
        'accessibility': max(0, min(100, accessibility)),
        'novelty': max(0, min(100, novelty)),
    }


def editorial_band(score: int) -> str:
    if score >= 92:
        return 'flagship'
    if score >= 80:
        return 'high'
    if score >= 68:
        return 'standard'
    return 'watch'


def refresh_post_fields(post: dict) -> dict:
    post = dict(post)
    post['source'] = normalize_source_name(post.get('source') or '')
    kind = coverage_kind_for(post)
    kind_story = story_kind(post)
    score = refined_score(post)
    band = editorial_band(score)
    evidence_key = evidence_key_for_kind(kind)

    title_pt_clean = smooth_title(post.get('title_pt') or post.get('title') or '')
    title_en_clean = smooth_title(post.get('title_en') or post.get('title') or '')
    post['title'] = title_pt_clean
    post['title_pt'] = title_pt_clean
    post['title_en'] = title_en_clean

    sub_pt = sentence_safe_excerpt(post.get('sub_pt') or post.get('excerpt_pt') or post.get('body_pt') or '', 180, fallback=title_pt_clean)
    sub_en = sentence_safe_excerpt(post.get('sub_en') or post.get('excerpt_en') or post.get('body_en') or '', 180, fallback=title_en_clean)
    excerpt_pt = sentence_safe_excerpt(post.get('excerpt_pt') or post.get('sub_pt') or post.get('body_pt') or '', 260, fallback=sub_pt or title_pt_clean)
    excerpt_en = sentence_safe_excerpt(post.get('excerpt_en') or post.get('sub_en') or post.get('body_en') or '', 260, fallback=sub_en or title_en_clean)

    post['sub'] = sub_pt
    post['sub_pt'] = sub_pt
    post['sub_en'] = sub_en
    post['excerpt'] = excerpt_pt
    post['excerpt_pt'] = excerpt_pt
    post['excerpt_en'] = excerpt_en

    facts_pt = post.get('highlights_pt') or post.get('highlights') or []
    facts_en = post.get('highlights_en') or []
    post['highlights'] = build_highlights(sub_pt or excerpt_pt or title_pt_clean, facts_pt, kind, 'pt')
    post['highlights_pt'] = post['highlights']
    post['highlights_en'] = build_highlights(sub_en or excerpt_en or title_en_clean, facts_en or facts_pt, kind, 'en')

    post['coverageKind'] = kind
    post['coverageKindLabel'] = COVERAGE_LABELS[kind]['pt']
    post['coverageKindLabel_pt'] = COVERAGE_LABELS[kind]['pt']
    post['coverageKindLabel_en'] = COVERAGE_LABELS[kind]['en']
    post['sourceType'] = kind
    post['sourceTypeLabel'] = COVERAGE_LABELS[kind]['pt']
    post['sourceTypeLabel_pt'] = COVERAGE_LABELS[kind]['pt']
    post['sourceTypeLabel_en'] = COVERAGE_LABELS[kind]['en']
    post['sourceNote'] = COVERAGE_NOTES[kind]['pt']
    post['sourceNote_pt'] = COVERAGE_NOTES[kind]['pt']
    post['sourceNote_en'] = COVERAGE_NOTES[kind]['en']
    post['evidenceKey'] = evidence_key
    post['evidenceLabel'] = EVIDENCE_LABELS[evidence_key]['pt']
    post['evidenceLabel_pt'] = EVIDENCE_LABELS[evidence_key]['pt']
    post['evidenceLabel_en'] = EVIDENCE_LABELS[evidence_key]['en']
    post['editorialBand'] = band
    post['editorialBandLabel'] = cw.EDITORIAL_BANDS[band]['pt']
    post['editorialBandLabel_pt'] = cw.EDITORIAL_BANDS[band]['pt']
    post['editorialBandLabel_en'] = cw.EDITORIAL_BANDS[band]['en']
    post['score'] = score
    post['scoreBreakdown'] = recalc_score_breakdown(post, score, kind, kind_story)
    post['storyKind'] = kind_story
    post['lastModifiedIso'] = now_iso()
    return post


def load_run_new_slugs() -> set[str]:
    slugs = cw.load_run_new_slugs_marker()
    return set() if slugs is None else slugs


def load_candidate_pool() -> list[dict]:
    current = []
    archive = []
    new_slugs = load_run_new_slugs()
    if cw.POSTS_JSON.exists():
        current = json.loads(cw.POSTS_JSON.read_text(encoding='utf-8'))
    if cw.ARCHIVE_POSTS_JSON.exists():
        archive = json.loads(cw.ARCHIVE_POSTS_JSON.read_text(encoding='utf-8'))

    merged: dict[str, dict] = {}
    for item in archive + current:
        if not isinstance(item, dict):
            continue
        slug = cw.collapse_ws(str(item.get('slug') or ''))
        if not slug:
            continue
        merged[slug] = item

    pool: list[dict] = []
    for item in merged.values():
        slug = cw.collapse_ws(str(item.get('slug') or ''))
        if slug in new_slugs:
            pool.append(refresh_post_fields(item))
        else:
            # Existing articles are treated as immutable editorial artifacts.
            # They may be selected, sorted and republished in indexes, but their
            # text fields are not regenerated just because another workflow ran.
            pool.append(cw.mark_preserve_content(dict(item)))
    return pool


def choose_posts(pool: list[dict]) -> list[dict]:
    base_caps = defaultdict(lambda: 3, {k: int(v) for k, v in RULES['base_source_caps'].items()})
    max_caps = defaultdict(lambda: 5, {k: int(v) for k, v in RULES['max_source_caps'].items()})

    science = [p for p in pool if p.get('storyKind') == 'science']
    guides = [p for p in pool if p.get('storyKind') == 'guide']
    ops = [p for p in pool if p.get('storyKind') == 'ops']

    for collection in (science, guides, ops):
        collection.sort(key=lambda post: (int(post.get('score') or 0), post.get('publishedIso') or ''), reverse=True)

    selected: list[dict] = []
    seen: set[str] = set()
    per_source: Counter = Counter()
    per_category: Counter = Counter()

    def can_take(post: dict, caps: dict[str, int]) -> bool:
        slug = cw.collapse_ws(str(post.get('slug') or ''))
        source = normalize_source_name(post.get('source') or '')
        return bool(slug) and slug not in seen and per_source[source] < caps[source]

    def take(post: dict) -> None:
        slug = cw.collapse_ws(str(post.get('slug') or ''))
        source = normalize_source_name(post.get('source') or '')
        seen.add(slug)
        per_source[source] += 1
        per_category[post.get('cat') or 'Astronomia'] += 1
        selected.append(post)

    for category in CATEGORY_ORDER:
        while per_category[category] < CATEGORY_FLOOR and len(selected) < TARGET_POST_COUNT:
            picked = False
            for post in science:
                if post.get('cat') != category:
                    continue
                if can_take(post, base_caps):
                    take(post)
                    picked = True
                    break
            if not picked:
                break

    for post in science:
        if len(selected) >= TARGET_POST_COUNT:
            break
        if can_take(post, base_caps):
            take(post)

    for post in science:
        if len(selected) >= TARGET_POST_COUNT:
            break
        if can_take(post, max_caps):
            take(post)

    for pool_name in (guides, ops):
        for post in pool_name:
            if len(selected) >= TARGET_POST_COUNT:
                break
            if can_take(post, max_caps):
                take(post)

    selected.sort(key=lambda post: post.get('publishedIso') or '', reverse=True)
    for idx, post in enumerate(selected, start=1):
        post['id'] = idx
    return selected


def print_report(selected: list[dict], pool: list[dict]) -> None:
    counts_source = Counter(post.get('source') for post in selected)
    counts_cat = Counter(post.get('cat') for post in selected)
    counts_kind = Counter(post.get('coverageKind') for post in selected)
    dropped = Counter(post.get('storyKind') for post in pool)

    print(f'[editorial-refine] pool: {len(pool)} candidatos')
    print(f'[editorial-refine] saída: {len(selected)} posts')
    print(f'[editorial-refine] story kinds no pool: {dict(dropped)}')
    print(f'[editorial-refine] cobertura final: {dict(counts_kind)}')
    print('[editorial-refine] por categoria:')
    for category, count in sorted(counts_cat.items(), key=lambda item: (-item[1], item[0])):
        print(f'  - {category}: {count}')
    print('[editorial-refine] por fonte:')
    for source, count in sorted(counts_source.items(), key=lambda item: (-item[1], item[0])):
        print(f'  - {source}: {count}')


def main() -> None:
    if not cw.POSTS_JSON.exists():
        raise SystemExit('posts.json não encontrado. Execute primeiro scripts/fetch_news.py ou forneça o snapshot existente.')
    pool = load_candidate_pool()
    selected = choose_posts(pool)
    if not selected:
        raise SystemExit('Nenhum post elegível após a curadoria editorial.')
    print_report(selected, pool)
    cw.build_highlights = build_highlights_wrapper
    cw.save_posts(selected)
    cw.remove_run_new_slugs_marker()
    print('[editorial-refine] artefatos reconstruídos com sucesso')


if __name__ == '__main__':
    main()
