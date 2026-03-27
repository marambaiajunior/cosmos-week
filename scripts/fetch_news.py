import json
import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

POSTS_JSON = Path('posts.json')
POSTS_JS = Path('posts.js')
MAX_POSTS = 36
USER_AGENT = 'CosmosWeekBot/1.0 (+https://github.com/marambaiajunior/cosmos-week)'

SOURCES = [
    {
        'name': 'NASA',
        'url': 'https://www.nasa.gov/feed/',
        'kind': 'rss',
    },
    {
        'name': 'NASA News Releases',
        'url': 'https://www.nasa.gov/news-release/feed/',
        'kind': 'rss',
    },
    {
        'name': 'ESA Space News',
        'url': 'https://www.esa.int/rssfeed/Our_Activities/Space_News',
        'kind': 'rss',
    },
    {
        'name': 'ESA Space Science',
        'url': 'https://www.esa.int/rssfeed/Our_Activities/Space_Science',
        'kind': 'rss',
    },
    {
        'name': 'arXiv Astrophysics',
        'url': 'https://export.arxiv.org/api/query?search_query=cat:astro-ph*&sortBy=submittedDate&sortOrder=descending&max_results=18',
        'kind': 'atom',
    },
    {
        'name': 'arXiv Physics',
        'url': 'https://export.arxiv.org/api/query?search_query=cat:physics*&sortBy=submittedDate&sortOrder=descending&max_results=12',
        'kind': 'atom',
    },
]

KEYWORD_CATEGORIES = [
    ('Exoplanetas', ['exoplanet', 'exoplaneta', 'habitável', 'habitavel', 'biosignature', 'bioassinatura', 'sub-neptune', 'super-earth', 'super-terra', 'trappist', 'k2-18']),
    ('Cosmologia', ['cosmology', 'cosmologia', 'dark matter', 'matéria escura', 'materia escura', 'dark energy', 'energia escura', 'big bang', 'hubble', 'cmb', 'euclid']),
    ('Astrofísica', ['black hole', 'buraco negro', 'neutron star', 'estrela de nêutrons', 'estrela de neutrons', 'supernova', 'magnetar', 'pulsar', 'gravitational wave', 'onda gravitacional', 'frb', 'fast radio burst', 'kilonova']),
    ('Astronomia', ['galaxy', 'galáxia', 'galaxia', 'nebula', 'nebulosa', 'milky way', 'via láctea', 'via lactea', 'moon', 'lua', 'mars', 'marte', 'jupiter', 'saturn', 'comet', 'cometa', 'asteroid', 'asteroide', 'rubin', 'telescope', 'telescópio', 'telescopio', 'artemis', 'jwst', 'webb', 'hubble', 'xrism']),
    ('Física', ['physics', 'física', 'fisica', 'quantum', 'quântico', 'quantico', 'cern', 'lhc', 'particle', 'partícula', 'particula', 'quark', 'muon', 'múon']),
    ('Biologia', ['biology', 'biologia', 'hiv', 'crispr', 'microbe', 'microbe', 'archaea', 'arqueia', 'parasite', 'parasita', 'malaria']),
    ('Química', ['chemistry', 'química', 'quimica', 'molecule', 'molecula', 'ribose', 'spectroscopy']),
    ('Ciências da Terra', ['earth', 'terra', 'climate', 'clima', 'magnetic field', 'campo magnético', 'campo magnetico', 'atmosphere', 'atmosfera', 'sea ice', 'ice', 'ocean']),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def strip_html(text: str) -> str:
    if not text:
        return ''
    text = html.unescape(text)
    text = re.sub(r'<script.*?</script>', ' ', text, flags=re.I | re.S)
    text = re.sub(r'<style.*?</style>', ' ', text, flags=re.I | re.S)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate(text: str, limit: int) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].strip()
    return cut + '…'


def parse_date(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d'):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return datetime.now(timezone.utc)


def classify_category(text: str, source_name: str) -> str:
    low = f'{source_name} {text}'.lower()
    for cat, keywords in KEYWORD_CATEGORIES:
        if any(k in low for k in keywords):
            return cat
    if 'arxiv' in source_name.lower():
        return 'Física'
    return 'Astronomia'


def cat_cls(cat: str) -> str:
    low = cat.lower()
    repl = (
        low.replace('á', 'a').replace('à', 'a').replace('â', 'a')
        .replace('é', 'e').replace('ê', 'e')
        .replace('í', 'i').replace('ó', 'o').replace('ô', 'o')
        .replace('ú', 'u').replace('ç', 'c')
        .replace(' ', '-')
    )
    return 'terra' if repl == 'ciencias-da-terra' else repl


def reading_time(text: str) -> str:
    words = max(1, len(text.split()))
    mins = max(2, round(words / 180))
    return f'{mins} min'


def make_body(summary: str, source_name: str, link: str) -> str:
    summary = strip_html(summary)
    parts = []
    if summary:
        parts.append(f'<p>{html.escape(summary)}</p>')
    parts.append(
        f'<p>Este artigo foi incorporado automaticamente do feed de <strong>{html.escape(source_name)}</strong>. '
        f'Para detalhes completos, contexto adicional e eventuais imagens originais da publicação, abra a fonte original.</p>'
    )
    parts.append(
        f'<blockquote>Fonte original: <a href="{html.escape(link)}" target="_blank" rel="noopener">{html.escape(link)}</a></blockquote>'
    )
    return ''.join(parts)


def parse_rss(xml_bytes: bytes, source_name: str):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall('.//item'):
        title = strip_html(item.findtext('title', default=''))
        link = (item.findtext('link', default='') or '').strip()
        desc = strip_html(item.findtext('description', default=''))
        pub = item.findtext('pubDate', default='') or item.findtext('{http://purl.org/dc/elements/1.1/}date', default='')
        if not title or not link:
            continue
        dt = parse_date(pub)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(desc, 320),
            'published': dt,
            'source': source_name,
        })
    return items


def parse_atom(xml_bytes: bytes, source_name: str):
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_bytes)
    items = []
    for entry in root.findall('a:entry', ns):
        title = strip_html(entry.findtext('a:title', default='', namespaces=ns))
        summary = strip_html(entry.findtext('a:summary', default='', namespaces=ns))
        published = entry.findtext('a:published', default='', namespaces=ns) or entry.findtext('a:updated', default='', namespaces=ns)
        link = ''
        for link_el in entry.findall('a:link', ns):
            href = link_el.get('href', '').strip()
            rel = link_el.get('rel', 'alternate')
            if href and rel == 'alternate':
                link = href
                break
        if not title or not link:
            continue
        dt = parse_date(published)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(summary, 320),
            'published': dt,
            'source': source_name,
        })
    return items


def load_all_items():
    all_items = []
    for src in SOURCES:
        try:
            raw = fetch(src['url'])
            if src['kind'] == 'atom':
                all_items.extend(parse_atom(raw, src['name']))
            else:
                all_items.extend(parse_rss(raw, src['name']))
            print(f'OK  {src["name"]}')
        except Exception as exc:
            print(f'ERR {src["name"]}: {exc}')
    return all_items


def dedupe_and_rank(items):
    seen = set()
    cleaned = []
    for item in sorted(items, key=lambda x: x['published'], reverse=True):
        key = re.sub(r'\W+', '', item['title'].lower())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    return cleaned[:MAX_POSTS]


def to_post(item, idx: int, total: int):
    category = classify_category(item['title'] + ' ' + item['summary'], item['source'])
    dt = item['published']
    featured = idx < 3
    trending = idx < 8
    return {
        'id': idx + 1,
        'cat': category,
        'catCls': cat_cls(category),
        'img': None,
        'title': item['title'],
        'sub': truncate(item['summary'], 140),
        'excerpt': truncate(item['summary'], 220),
        'body': make_body(item['summary'], item['source'], item['link']),
        'date': dt.strftime('%d %b %Y'),
        'time': dt.strftime('%Hh%M'),
        'read': reading_time(item['summary']),
        'source': item['source'],
        'srcUrl': item['link'],
        'featured': featured,
        'trending': trending,
    }


def save_posts(posts):
    POSTS_JSON.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding='utf-8')
    POSTS_JS.write_text(
        '// Dados atualizados automaticamente para o Cosmos Week\n\nwindow.postsData = ' +
        json.dumps(posts, ensure_ascii=False, indent=2) +
        ';\n',
        encoding='utf-8'
    )


def main():
    items = load_all_items()
    ranked = dedupe_and_rank(items)
    posts = [to_post(item, idx, len(ranked)) for idx, item in enumerate(ranked)]
    save_posts(posts)
    print(f'{len(posts)} posts salvos em {datetime.now(timezone.utc).isoformat()}')


if __name__ == '__main__':
    main()
