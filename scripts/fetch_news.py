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
    ('Ciências da Terra', ['earth climate', 'global warming', 'climate change', 'mudança climática', 'mudanca climatica', 'aquecimento global', 'geomagnetic', 'earth magnetic field', 'campo magnético terrestre', 'magnetosphere', 'magnetosfera', 'aurora borealis', 'aurora australis', 'sea level', 'nível do mar', 'nivel do mar', 'antarctica', 'antártica', 'antartica', 'arctic sea ice', 'gelo ártico', 'gelo artico', 'ocean acidification', 'acidificação', 'terremoto', 'earthquake', 'vulcão', 'vulcao', 'volcano']),
]


# Wikimedia Commons — mesmas URLs que o front-end usa em IMG{}
THEMATIC_IMAGES = {
    'pillars':          'https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg/800px-Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg',
    'andromeda':        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Andromeda_Galaxy_%28with_h-alpha%29.jpg/800px-Andromeda_Galaxy_%28with_h-alpha%29.jpg',
    'whirlpool':        'https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Messier51_sRGB.jpg/800px-Messier51_sRGB.jpg',
    'hubbledeep':       'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Hubble_ultra_deep_field.jpg/800px-Hubble_ultra_deep_field.jpg',
    'milkyway':         'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg/800px-Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg',
    'carina':           'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Carina_Nebula_by_Harel_Boren_%28151851961%2C_modified%29.jpg/800px-Carina_Nebula_by_Harel_Boren_%28151851961%2C_modified%29.jpg',
    'orion':            'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg/800px-Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg',
    'solar':            'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/800px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'aurora':           'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aurora_Borealis_over_Lake_Ladoga.jpg/800px-Aurora_Borealis_over_Lake_Ladoga.jpg',
    'moon':             'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/800px-FullMoon2010.jpg',
    'lunarSouthPole':   'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg/800px-PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg',
    'mars':             'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/800px-OSIRIS_Mars_true_color.jpg',
    'perseverance':     'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/PIA23764-Mars2020Rover-ArtistConcept-20190723.jpg/800px-PIA23764-Mars2020Rover-ArtistConcept-20190723.jpg',
    'jupiter':          'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/800px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
    'europa':           'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Europa-moon-625x443.jpg/800px-Europa-moon-625x443.jpg',
    'saturn':           'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/800px-Saturn_during_Equinox.jpg',
    'exoplanetTransit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Transiting_Exoplanet_Artist%27s_Impression.jpg/800px-Transiting_Exoplanet_Artist%27s_Impression.jpg',
    'exoplanetOcean':   'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Artist%E2%80%99s_impression_of_an_exoplanet.jpg/800px-Artist%E2%80%99s_impression_of_an_exoplanet.jpg',
    'blackhole':        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Black_hole_-_Messier_87_crop_max_res.jpg/800px-Black_hole_-_Messier_87_crop_max_res.jpg',
    'neutronStar':      'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Neutron_Star.jpg/800px-Neutron_Star.jpg',
    'supernova':        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/SN1994D.jpg/800px-SN1994D.jpg',
    'kilonova':         'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Neutron_Star_Merger_Illustration.jpg/800px-Neutron_Star_Merger_Illustration.jpg',
    'comet':            'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Comet_Hale-Bopp_1995O1.jpg/800px-Comet_Hale-Bopp_1995O1.jpg',
    'asteroid':         'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Ida_and_Dactyl.jpg/800px-Ida_and_Dactyl.jpg',
    'rubin':            'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/LSST_Rendering.jpg/800px-LSST_Rendering.jpg',
    'particleTracks':   'https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/CMS_Higgs-event.jpg/800px-CMS_Higgs-event.jpg',
    'earth':            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/The_Blue_Marble_%28remastered%29.jpg/800px-The_Blue_Marble_%28remastered%29.jpg',
    'magneticField':    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Magnetosphere_rendition.jpg/800px-Magnetosphere_rendition.jpg',
    'climate':          'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Global_Temperature_Anomaly.svg/800px-Global_Temperature_Anomaly.svg.png',
}

_NS_MEDIA = 'http://search.yahoo.com/mrss/'
_NS_MEDIA2 = 'http://search.yahoo.com/mrss'

def extract_feed_image(item_el, raw_desc: str) -> str | None:
    """Try to pull a real image URL from an RSS/Atom item element."""
    # 1. media:content (Yahoo Media RSS)
    for ns in (_NS_MEDIA, _NS_MEDIA2):
        mc = item_el.find(f'{{{ns}}}content')
        if mc is not None:
            url = mc.get('url', '')
            if url.startswith('http'):
                return url
        mt = item_el.find(f'{{{ns}}}thumbnail')
        if mt is not None:
            url = mt.get('url', '')
            if url.startswith('http'):
                return url
    # 2. <enclosure> (classic RSS podcasting standard, also used for images)
    enc = item_el.find('enclosure')
    if enc is not None:
        url = enc.get('url', '')
        typ = enc.get('type', '')
        if url.startswith('http') and 'image' in typ:
            return url
    # 3. <img src="..."> embedded in description HTML
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc or '', re.I)
    if m:
        url = m.group(1)
        if url.startswith('http'):
            return url
    return None


def get_thematic_image(title: str, summary: str, source_name: str, category: str) -> str:
    """Return a contextually appropriate Wikimedia image URL based on article content."""
    text = f'{title} {summary} {source_name}'.lower()

    # — Específicos primeiro (contexto fino) —
    if re.search(r'k2-18|hycean|dms|dimetilssulfeto|biosignature|bioassinatura|ocean glint', text):
        return THEMATIC_IMAGES['exoplanetOcean']
    if re.search(r'exoplanet|exoplaneta|trappist|speculoos|sub.neptune|super.terra|super.earth|zona habit', text):
        return THEMATIC_IMAGES['exoplanetTransit']
    if re.search(r'shackleton|polo sul lunar', text):
        return THEMATIC_IMAGES['lunarSouthPole']
    if re.search(r'artemis|lunar|lua\b|moon\b', text):
        return THEMATIC_IMAGES['moon']
    if re.search(r'perseverance|jezero|curiosity', text):
        return THEMATIC_IMAGES['perseverance']
    if re.search(r'\bmarte\b|mars\b|mars sample', text):
        return THEMATIC_IMAGES['mars']
    if re.search(r'europa\b', text):
        return THEMATIC_IMAGES['europa']
    if re.search(r'j[uú]piter|jupiter', text):
        return THEMATIC_IMAGES['jupiter']
    if re.search(r'saturn|saturno|cassini', text):
        return THEMATIC_IMAGES['saturn']
    if re.search(r'solar flare|coronal|tempestade solar|sunspot|mancha solar', text):
        return THEMATIC_IMAGES['solar']
    if re.search(r'\bsol\b|\bsun\b', text) and re.search(r'flare|erup|eject', text):
        return THEMATIC_IMAGES['solar']
    if re.search(r'aurora borealis|aurora austral|aurora\b', text):
        return THEMATIC_IMAGES['aurora']
    if re.search(r'black hole|buraco negro|m87|sgr a\*|event horizon', text):
        return THEMATIC_IMAGES['blackhole']
    if re.search(r'kilonova|ligo|virgo|gw\d|onda gravitacional|gravitational wave', text):
        return THEMATIC_IMAGES['kilonova']
    if re.search(r'neutron star|estrela de n[eê]utrons|magnetar|pulsar', text):
        return THEMATIC_IMAGES['neutronStar']
    if re.search(r'\bsupernova\b', text):
        return THEMATIC_IMAGES['supernova']
    if re.search(r'comet|cometa', text):
        return THEMATIC_IMAGES['comet']
    if re.search(r'asteroid|asteroide', text):
        return THEMATIC_IMAGES['asteroid']
    if re.search(r'vera rubin|rubin observatory|lsst', text):
        return THEMATIC_IMAGES['rubin']
    if re.search(r'jwst|james webb|webb telescope', text):
        return THEMATIC_IMAGES['hubbledeep']
    if re.search(r'carina', text):
        return THEMATIC_IMAGES['carina']
    if re.search(r'orion nebula|nebulosa de orion', text):
        return THEMATIC_IMAGES['orion']
    if re.search(r'nebula|nebulosa', text):
        return THEMATIC_IMAGES['pillars']
    if re.search(r'andromeda|andrômeda', text):
        return THEMATIC_IMAGES['andromeda']
    if re.search(r'milky way|via l[aá]ctea|gaia satellite|gaia mission', text):
        return THEMATIC_IMAGES['milkyway']
    if re.search(r'gal[aá]xia|galaxy|galactic', text):
        return THEMATIC_IMAGES['whirlpool']
    if re.search(r'lhc|cern|higgs|quark|m[uú]on|particle|partícula|detector', text):
        return THEMATIC_IMAGES['particleTracks']
    if re.search(r'aquecimento global|global warming|climate change|mudança climática', text):
        return THEMATIC_IMAGES['climate']
    if re.search(r'campo magn[eé]tico|magnetosphere|magnetosfera|geomagnetic', text):
        return THEMATIC_IMAGES['magneticField']
    if re.search(r'earth\b|planeta terra\b', text):
        return THEMATIC_IMAGES['earth']

    # — Fallback por categoria —
    cat_fallback = {
        'Exoplanetas':       THEMATIC_IMAGES['exoplanetTransit'],
        'Cosmologia':        THEMATIC_IMAGES['hubbledeep'],
        'Astrofísica':       THEMATIC_IMAGES['blackhole'],
        'Astronomia':        THEMATIC_IMAGES['milkyway'],
        'Física':            THEMATIC_IMAGES['particleTracks'],
        'Biologia':          THEMATIC_IMAGES['europa'],
        'Química':           THEMATIC_IMAGES['pillars'],
        'Ciências da Terra': THEMATIC_IMAGES['earth'],
    }
    return cat_fallback.get(category, THEMATIC_IMAGES['pillars'])


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
        raw_desc = item.findtext('description', default='') or ''
        desc = strip_html(raw_desc)
        pub = item.findtext('pubDate', default='') or item.findtext('{http://purl.org/dc/elements/1.1/}date', default='')
        if not title or not link:
            continue
        dt = parse_date(pub)
        img = extract_feed_image(item, raw_desc)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(desc, 320),
            'published': dt,
            'source': source_name,
            'img': img,
        })
    return items


def parse_atom(xml_bytes: bytes, source_name: str):
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_bytes)
    items = []
    for entry in root.findall('a:entry', ns):
        title = strip_html(entry.findtext('a:title', default='', namespaces=ns))
        raw_summary = entry.findtext('a:summary', default='', namespaces=ns) or ''
        summary = strip_html(raw_summary)
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
        img = extract_feed_image(entry, raw_summary)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(summary, 320),
            'published': dt,
            'source': source_name,
            'img': img,
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
    # Use real image from feed; fall back to thematic Wikimedia image
    img = item.get('img') or get_thematic_image(item['title'], item['summary'], item['source'], category)
    return {
        'id': idx + 1,
        'cat': category,
        'catCls': cat_cls(category),
        'img': img,
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
