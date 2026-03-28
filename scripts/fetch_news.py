import hashlib
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Optional
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
POSTS_JSON = ROOT / 'posts.json'
POSTS_JS = ROOT / 'posts.js'
FEED_XML = ROOT / 'feed.xml'
SITEMAP_XML = ROOT / 'sitemap.xml'
ROBOTS_TXT = ROOT / 'robots.txt'

SITE_URL = os.getenv('COSMOS_SITE_URL', 'https://marambaiajunior.github.io/cosmos-week/').rstrip('/') + '/'
SITE_NAME = 'Cosmos Week'
SITE_DESCRIPTION_PT = 'Portal de jornalismo científico com foco em astronomia, astrofísica, cosmologia e ciência de fronteira.'
SITE_DESCRIPTION_EN = 'Science journalism portal focused on astronomy, astrophysics, cosmology and frontier research.'
MAX_POSTS = 28
MAX_POSTS_PER_SOURCE = 6
MAX_PREPRINTS = 10
MIN_POSTS_PER_CATEGORY = 1
USER_AGENT = 'CosmosWeekBot/4.0 (+https://github.com/marambaiajunior/cosmos-week)'
REQUEST_TIMEOUT = 30
PAGE_TIMEOUT = 20
TRANSLATE_TIMEOUT = 20
TRANSLATE_ENDPOINT = 'https://translate.googleapis.com/translate_a/single'
MAX_PAGE_FETCHES = 18

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'media': 'http://search.yahoo.com/mrss/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}

MESES_PT = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez',
}

IMG = {
    'pillars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg/1280px-Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg',
    'andromeda': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Andromeda_Galaxy_%28with_h-alpha%29.jpg/1280px-Andromeda_Galaxy_%28with_h-alpha%29.jpg',
    'hubbledeep': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Hubble_ultra_deep_field.jpg/1280px-Hubble_ultra_deep_field.jpg',
    'milkyway': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg/1280px-Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg',
    'orion': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg/1280px-Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg',
    'helix': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/NGC7293_%282004%29.jpg/1280px-NGC7293_%282004%29.jpg',
    'jezero': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Jezero_Crater_delta_colored_mosaic.jpg/1280px-Jezero_Crater_delta_colored_mosaic.jpg',
    'moon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/1280px-FullMoon2010.jpg',
    'lunarSouthPole': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg/1280px-PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg',
    'mars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/1280px-OSIRIS_Mars_true_color.jpg',
    'jupiter': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/1280px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
    'saturn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/1280px-Saturn_during_Equinox.jpg',
    'exoplanetTransit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Transiting_Exoplanet_Artist%27s_Impression.jpg/1280px-Transiting_Exoplanet_Artist%27s_Impression.jpg',
    'exoplanetOcean': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Artist%E2%80%99s_impression_of_an_exoplanet.jpg/1280px-Artist%E2%80%99s_impression_of_an_exoplanet.jpg',
    'blackhole': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Black_hole_-_Messier_87_crop_max_res.jpg/1280px-Black_hole_-_Messier_87_crop_max_res.jpg',
    'm87jet': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/M87_jet.jpg/1280px-M87_jet.jpg',
    'neutronStar': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Neutron_Star.jpg/1280px-Neutron_Star.jpg',
    'supernova': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Cassiopeia_A.jpg/1280px-Cassiopeia_A.jpg',
    'kilonova': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Neutron_star_collision.jpg/1280px-Neutron_star_collision.jpg',
    'comet': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Comet_67P_on_19_September_2014_NavCam_mosaic.jpg/1280px-Comet_67P_on_19_September_2014_NavCam_mosaic.jpg',
    'asteroid': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/243_Ida.jpg/1280px-243_Ida.jpg',
    'rubin': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/LSST_at_Sunset_%28Cropped%29.jpg/1280px-LSST_at_Sunset_%28Cropped%29.jpg',
    'particleTracks': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/LHCb_event_display.jpg/1280px-LHCb_event_display.jpg',
    'cern': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/CERN_Globe_and_Main_Building.jpg/1280px-CERN_Globe_and_Main_Building.jpg',
    'earth': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/1280px-The_Earth_seen_from_Apollo_17.jpg',
    'magneticField': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Earth%27s_magnetic_field_and_magnetosphere.jpg/1280px-Earth%27s_magnetic_field_and_magnetosphere.jpg',
    'climate': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Global_Surface_Temperature_Anomalies_1880-2013.jpg/1280px-Global_Surface_Temperature_Anomalies_1880-2013.jpg',
}

BAD_TITLE_PATTERNS = [
    r'^week in images', r'^watch live', r'^image:', r'^video:', r'^earth from space', r'^i am artemis',
    r'awards categories', r'crew.?s suits', r'view of', r'views mount', r'photo of', r'^listen to this audio excerpt',
    r'^how europe will', r'^nextstep', r'^where spiral arms', r'^earth from ', r'^getting to the core of a medicane',
]
BAD_URL_PARTS = [
    '/image-article/', '/images/', '/videos/', '/video/', '/week_in_images/', '/photojournal/', '/multimedia/', '/gallery/'
]
BAD_TEXT_HINTS = [
    'listen to this audio excerpt', 'discover our week through the lens', 'category i:', 'copyright',
    'image credit', 'video:', 'image:', 'week in images', 'earth from space:', 'artist impression'
]
PROMO_HINTS = [
    'award', 'awards', 'profile', 'audio excerpt', 'watch live', 'week in images', 'gallery',
    'contract opportunity', 'broad agency announcement', 'synopsis', 'procurement', 'solicitation', 'podcast',
    'career', 'jobs', 'livestream', 'event coverage', 'photo essay', 'webcast'
]
SCIENTIFIC_RESULT_HINTS = [
    'detect', 'detected', 'discovery', 'discover', 'measurement', 'measured', 'results', 'study', 'paper',
    'observations', 'first images', 'first light', 'finds', 'reveals', 'evidence', 'analysis', 'mission',
    'launches', 'data', 'maps', 'constraints', 'spectrum', 'spectra', 'atmosphere', 'galaxy', 'exoplanet',
    'black hole', 'dark matter', 'dark energy', 'star', 'nebula', 'gravitational wave', 'telescope', 'survey',
    'signal', 'candidate', 'sample return', 'biosignature', 'habitability', 'interstellar'
]
BROAD_INTEREST_PREPRINT_HINTS = [
    'dark matter', 'dark energy', 'exoplanet', 'black hole', 'james webb', 'jwst', 'galaxy', 'cosmology',
    'hubble tension', 'gravitational wave', 'supernova', 'mars', 'moon', 'solar', 'neutron star', 'euclid',
    'rubin', 'desi', 'cmb', 'planet', 'universe', 'biosignature', 'habitability'
]
TECHNICAL_JARGON_HINTS = [
    'hamiltonian', 'lagrangian', 'puiseux', 'hessenberg', 'all-solid-state', 'metamodel', 'waveguides',
    'crconi', 'adiabatic equations', 'teapot effect', 'photoluminescence', 'baryon acoustic oscillations',
    'scalar-tensor realization', 'steady-state wind flow transformer', 'introductory physics', 'emulator-based'
]
PUBLIC_INTEREST_HINTS = [
    'moon', 'mars', 'exoplanet', 'black hole', 'dark matter', 'dark energy', 'galaxy', 'universe', 'earth',
    'climate', 'magnetic field', 'gravitational wave', 'life', 'biosignature', 'ocean', 'sample return',
    'telescope', 'jwst', 'hubble', 'euclid', 'rubin', 'nasa', 'esa', 'jpl'
]
HARD_RESEARCH_HINTS = [
    'published', 'journal', 'analysis', 'dataset', 'observations', 'spectroscopy', 'transit', 'survey',
    'map', 'constraints', 'letters', 'astrophysical journal', 'nature', 'science'
]

CATEGORY_RULES = [
    ('Exoplanetas', ['exoplanet', 'exoplaneta', 'biosignature', 'hycean', 'trappist', 'k2-18', 'habitable']),
    ('Cosmologia', ['cosmology', 'cosmologia', 'dark energy', 'energia escura', 'dark matter', 'matter power', 'cmb', 'hubble tension', 'inflation']),
    ('Astrofísica', ['black hole', 'buraco negro', 'neutron star', 'nêutron', 'gravitational wave', 'kilonova', 'supernova', 'quasar', 'fast radio burst', 'frb', 'magnetar', 'pulsar']),
    ('Física', ['physics', 'física', 'quânt', 'quantum', 'cern', 'lhc', 'higgs', 'quark', 'muon', 'particle', 'plasma', 'photonic', 'perovskite', 'superconductor', 'materials']),
    ('Ciências da Terra', ['earth', 'climate', 'sea level', 'atmospheric', 'atmosphere', 'weather', 'geodynamo', 'magnetic field', 'magnetosphere', 'earth science', 'river', 'ocean', 'environment', 'geophysics']),
    ('Biologia', ['biology', 'biologia', 'biomedical', 'microbe', 'life', 'crispr', 'archaea', 'hiv', 'genetic', 'genome', 'protein', 'cell', 'disease']),
    ('Química', ['chemistry', 'química', 'molecule', 'molecular', 'spectroscopy', 'ribose', 'chemical', 'catalyst', 'reaction', 'polymer', 'ice chemistry']),
    ('Astronomia', ['galaxy', 'galax', 'nebula', 'milky way', 'moon', 'mars', 'jupiter', 'saturn', 'comet', 'asteroid', 'telescope', 'artemis', 'jwst', 'webb', 'hubble', 'rubin', 'observatory']),
]

TOPIC_IMAGE_RULES = [
    (r'(artemis|shackleton|lunar south pole|polo sul lunar|\bmoon\b|\blua\b)', ['lunarSouthPole', 'moon']),
    (r'(perseverance|jezero|\bmars\b|marte|ingenuity)', ['jezero', 'mars']),
    (r'(jupiter|jovian)', ['jupiter']),
    (r'(saturn|saturno|cassini)', ['saturn']),
    (r'(solar|sunspot|flare|cme|aurora|geomagnetic|sun)', ['solar', 'climate']),
    (r'(black hole|buraco negro|event horizon|m87|quasar)', ['blackhole', 'm87jet']),
    (r'(neutron star|estrela de neutrons|nêutrons|gravitational wave|onda gravitacional|kilonova|ligo|virgo)', ['kilonova', 'neutronStar']),
    (r'(supernova)', ['supernova']),
    (r'(comet|cometa)', ['comet']),
    (r'(asteroid|asteroide|kuiper|dwarf planet|planeta anão)', ['asteroid', 'rubin']),
    (r'(rubin|lsst)', ['rubin']),
    (r'(exoplanet|exoplaneta|hycean|biosignature|super-earth|super-terra|sub-neptune)', ['exoplanetTransit', 'exoplanetOcean']),
    (r'(ocean|oceano|water world)', ['exoplanetOcean', 'exoplanetTransit']),
    (r'(nebula|nebulosa|orion|helix)', ['orion', 'helix']),
    (r'(galaxy|galaxia|galáxia|andromeda|milky way|via láctea|spiral)', ['andromeda', 'milkyway']),
    (r'(cosmology|cosmologia|dark energy|dark matter|cmb|euclid|deep field|universo)', ['hubbledeep', 'andromeda']),
    (r'(lhc|cern|higgs|quark|muon|particle)', ['particleTracks', 'cern']),
    (r'(climate|earth|sea level|atmospheric|weather|magnetosphere|magnetic field)', ['magneticField', 'climate', 'earth']),
]

CATEGORY_IMAGE_FALLBACKS = {
    'Astronomia': ['milkyway', 'andromeda', 'orion', 'comet'],
    'Cosmologia': ['hubbledeep', 'andromeda'],
    'Astrofísica': ['blackhole', 'neutronStar', 'supernova'],
    'Exoplanetas': ['exoplanetTransit', 'exoplanetOcean'],
    'Física': ['particleTracks', 'cern', 'solar'],
    'Biologia': ['earth', 'exoplanetOcean'],
    'Química': ['orion', 'hubbledeep'],
    'Ciências da Terra': ['magneticField', 'climate', 'earth'],
}

SOURCE_TYPE_LABELS = {
    'agency': {'pt': 'Fonte institucional', 'en': 'Institutional source'},
    'preprint': {'pt': 'Preprint', 'en': 'Preprint'},
    'journal': {'pt': 'Artigo científico', 'en': 'Research paper'},
}

SOURCE_NOTES = {
    'agency': {
        'pt': 'Fonte primária institucional. Exige leitura com contexto e distinção entre anúncio e evidência.',
        'en': 'Primary institutional source. It should be read with context and a clear distinction between announcement and evidence.'
    },
    'preprint': {
        'pt': 'Preprint ainda sem revisão por pares. Trata-se de resultado provisório, não de conclusão consolidada.',
        'en': 'Preprint not yet peer reviewed. Treat it as provisional work, not as a settled conclusion.'
    },
    'journal': {
        'pt': 'Artigo científico revisado por pares ou material publicado com lastro acadêmico explícito.',
        'en': 'Peer-reviewed research paper or material published with explicit academic backing.'
    },
}

EDITORIAL_BANDS = {
    'flagship': {'pt': 'Prioridade máxima', 'en': 'Top priority'},
    'high': {'pt': 'Alta prioridade', 'en': 'High priority'},
    'standard': {'pt': 'Prioridade editorial', 'en': 'Editorial priority'},
    'watch': {'pt': 'Leitura monitorada', 'en': 'Watchlist'},
}

EVIDENCE_LABELS = {
    'peer_reviewed': {'pt': 'Evidência revisada', 'en': 'Peer-reviewed evidence'},
    'institutional_update': {'pt': 'Atualização institucional', 'en': 'Institutional update'},
    'preprint': {'pt': 'Resultado provisório', 'en': 'Preliminary result'},
}

@dataclass
class SourceConfig:
    name: str
    url: str
    kind: str
    source_type: str
    priority: int


SOURCES = [
    SourceConfig('NASA News Releases', 'https://www.nasa.gov/news-release/feed/', 'rss', 'agency', 94),
    SourceConfig('JPL News', 'https://www.jpl.nasa.gov/feeds/news/', 'rss', 'agency', 93),
    SourceConfig('ESA Space Science', 'https://www.esa.int/rssfeed/Our_Activities/Space_Science', 'rss', 'agency', 90),
    SourceConfig('ESA Space News', 'https://www.esa.int/rssfeed/Our_Activities/Space_News', 'rss', 'agency', 80),
    SourceConfig('NASA Earth Observatory - Image of the Day', 'https://science.nasa.gov/feed/earth-observatory/image-of-the-day', 'rss', 'agency', 77),
    SourceConfig('NASA Earth Observatory - Natural Events', 'https://science.nasa.gov/feed/earth-observatory/natural-events', 'rss', 'agency', 79),
    SourceConfig('NIH News Releases', 'https://www.nih.gov/news-releases/feed.xml', 'rss', 'agency', 78),
    SourceConfig('arXiv Astrophysics', 'https://export.arxiv.org/api/query?search_query=(cat:astro-ph.*+AND+(all:exoplanet+OR+all:galaxy+OR+all:%22dark+matter%22+OR+all:%22dark+energy%22+OR+all:%22black+hole%22+OR+all:cosmology+OR+all:%22gravitational+wave%22+OR+all:supernova+OR+all:jwst+OR+all:euclid+OR+all:mars+OR+all:moon))&sortBy=submittedDate&sortOrder=descending&max_results=18', 'atom', 'preprint', 54),
    SourceConfig('arXiv Physics Frontiers', 'https://export.arxiv.org/api/query?search_query=((cat:quant-ph+OR+cat:hep-ph+OR+cat:hep-ex+OR+cat:physics.plasm-ph+OR+cat:cond-mat.mtrl-sci)+AND+(all:physics+OR+all:quantum+OR+all:particle+OR+all:muon+OR+all:plasma+OR+all:higgs+OR+all:quark+OR+all:superconductor))&sortBy=submittedDate&sortOrder=descending&max_results=18', 'atom', 'preprint', 52),
    SourceConfig('arXiv Quantitative Biology', 'https://export.arxiv.org/api/query?search_query=(cat:q-bio.*+AND+(all:biology+OR+all:cell+OR+all:genome+OR+all:protein+OR+all:disease+OR+all:microbe+OR+all:evolution))&sortBy=submittedDate&sortOrder=descending&max_results=18', 'atom', 'preprint', 49),
    SourceConfig('arXiv Chemical Physics', 'https://export.arxiv.org/api/query?search_query=((cat:physics.chem-ph+OR+cat:cond-mat.soft)+AND+(all:chemistry+OR+all:chemical+OR+all:molecule+OR+all:catalyst+OR+all:spectroscopy+OR+all:reaction+OR+all:polymer))&sortBy=submittedDate&sortOrder=descending&max_results=18', 'atom', 'preprint', 48),
    SourceConfig('arXiv Geophysics', 'https://export.arxiv.org/api/query?search_query=((cat:physics.geo-ph+OR+cat:physics.ao-ph)+AND+(all:earth+OR+all:climate+OR+all:ocean+OR+all:atmosphere+OR+all:geophysics+OR+all:magnetic+OR+all:weather))&sortBy=submittedDate&sortOrder=descending&max_results=18', 'atom', 'preprint', 50),
]

TRANSLATION_CACHE: dict[tuple[str, str], str] = {}
PAGE_CACHE: dict[str, str] = {}
IMAGE_CACHE: dict[str, Optional[str]] = {}
PAGE_FETCHES = 0


def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def collapse_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def normalize_text(text: str) -> str:
    text = collapse_ws(text or '').lower()
    return (text.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a').replace('ä', 'a')
                .replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('ë', 'e')
                .replace('í', 'i').replace('ì', 'i').replace('ï', 'i')
                .replace('ó', 'o').replace('ô', 'o').replace('õ', 'o').replace('ò', 'o').replace('ö', 'o')
                .replace('ú', 'u').replace('ù', 'u').replace('ü', 'u').replace('û', 'u')
                .replace('ç', 'c').replace('ñ', 'n'))


def strip_html(text: str) -> str:
    if not text:
        return ''
    text = html.unescape(text)
    text = re.sub(r'<script.*?</script>', ' ', text, flags=re.I | re.S)
    text = re.sub(r'<style.*?</style>', ' ', text, flags=re.I | re.S)
    text = re.sub(r'<[^>]+>', ' ', text)
    return collapse_ws(text)


def truncate(text: str, limit: int) -> str:
    text = collapse_ws(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].strip()
    return f'{cut}…'


def unique_keep_order(items: Iterable) -> list:
    seen = set()
    out = []
    for item in items:
        key = item if isinstance(item, str) else repr(item)
        if not item or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


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


def format_date_pt(dt: datetime) -> str:
    return f'{dt.day:02d} {MESES_PT[dt.month]} {dt.year}'


def format_date_en(dt: datetime) -> str:
    return dt.strftime('%d %b %Y')


def slugify(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text[:96] or 'artigo'


def stable_index(seed: str, size: int) -> int:
    if size <= 1:
        return 0
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return int(digest[:12], 16) % size


def stable_pick(options: list[str], seed: str) -> str:
    return options[stable_index(seed, len(options))]


def clean_image_url(url: str) -> Optional[str]:
    if not url:
        return None
    url = html.unescape(url).strip()
    if url.startswith('//'):
        url = 'https:' + url
    if not re.match(r'^https?://', url, flags=re.I):
        return None
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return None
    return url if parsed.netloc else None


def image_url_looks_good(url: str) -> bool:
    low = normalize_text(url)
    if any(bad in low for bad in ('logo', 'favicon', 'avatar', 'placeholder', 'sprite', 'icon')):
        return False
    if not re.search(r'\.(jpg|jpeg|png|webp)(?:$|[?#])', low) and not any(term in low for term in ('image', 'photo', 'media')):
        return False
    return True


def find_first_image_in_html(fragment: str, base_url: str = '') -> Optional[str]:
    if not fragment:
        return None
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', fragment, flags=re.I)
    if not match:
        return None
    src = match.group(1).strip()
    if base_url:
        src = urllib.parse.urljoin(base_url, src)
    src = clean_image_url(src)
    return src if src and image_url_looks_good(src) else None


def source_domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ''


def fetch_page_html(url: str) -> str:
    global PAGE_FETCHES
    if not url:
        return ''
    if url in PAGE_CACHE:
        return PAGE_CACHE[url]
    if PAGE_FETCHES >= MAX_PAGE_FETCHES:
        PAGE_CACHE[url] = ''
        return ''
    PAGE_FETCHES += 1
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=PAGE_TIMEOUT) as response:
            raw = response.read(1_200_000)
        page = raw.decode('utf-8', errors='ignore')
    except Exception:
        page = ''
    PAGE_CACHE[url] = page
    return page


def extract_page_text(url: str) -> str:
    page = fetch_page_html(url)
    if not page:
        return ''
    paragraphs = []
    for block in re.findall(r'<p[^>]*>(.*?)</p>', page, flags=re.I | re.S):
        text = strip_html(block)
        low = normalize_text(text)
        if len(text) < 60:
            continue
        if any(pattern in low for pattern in BAD_TEXT_HINTS):
            continue
        if low.startswith('image credit') or low.startswith('credit:'):
            continue
        paragraphs.append(text)
        if len(paragraphs) >= 12:
            break
    return ' '.join(paragraphs)


def fetch_page_image(url: str) -> Optional[str]:
    if not url:
        return None
    if url in IMAGE_CACHE:
        return IMAGE_CACHE[url]
    page = fetch_page_html(url)
    if not page:
        IMAGE_CACHE[url] = None
        return None
    patterns = [
        r'<meta[^>]+property=["\']og:image(?:url)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.I)
        if match:
            candidate = urllib.parse.urljoin(url, match.group(1).strip())
            candidate = clean_image_url(candidate)
            if candidate and image_url_looks_good(candidate):
                IMAGE_CACHE[url] = candidate
                return candidate
    inline = find_first_image_in_html(page, url)
    IMAGE_CACHE[url] = inline
    return inline


def extract_rss_image(item: ET.Element, link: str, description_html: str) -> Optional[str]:
    candidates = []
    for tag in ('enclosure', '{http://search.yahoo.com/mrss/}content', '{http://search.yahoo.com/mrss/}thumbnail'):
        for element in item.findall(tag):
            url = clean_image_url(element.get('url', ''))
            if url:
                candidates.append(url)
    for tag_name in ('description', '{http://purl.org/rss/1.0/modules/content/}encoded'):
        raw_html = item.findtext(tag_name, default='') or ''
        image = find_first_image_in_html(raw_html, link)
        if image:
            candidates.append(image)
    desc_image = find_first_image_in_html(description_html, link)
    if desc_image:
        candidates.append(desc_image)
    for candidate in unique_keep_order(candidates):
        if image_url_looks_good(candidate):
            return candidate
    return None


def extract_atom_image(entry: ET.Element, link: str, summary_html: str) -> Optional[str]:
    candidates = []
    for link_el in entry.findall('atom:link', NS):
        rel = (link_el.get('rel') or 'alternate').lower()
        href = clean_image_url(link_el.get('href', ''))
        media_type = (link_el.get('type') or '').lower()
        if href and (rel == 'enclosure' or media_type.startswith('image/')):
            candidates.append(href)
    for media_tag in ('media:content', 'media:thumbnail'):
        for element in entry.findall(media_tag, NS):
            url = clean_image_url(element.get('url', ''))
            if url:
                candidates.append(url)
    for field in ('atom:summary', 'atom:content'):
        html_field = entry.findtext(field, default='', namespaces=NS) or ''
        image = find_first_image_in_html(html_field, link)
        if image:
            candidates.append(image)
    summary_image = find_first_image_in_html(summary_html, link)
    if summary_image:
        candidates.append(summary_image)
    for candidate in unique_keep_order(candidates):
        if image_url_looks_good(candidate):
            return candidate
    return None


def parse_rss(xml_bytes: bytes, source: SourceConfig) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall('.//item'):
        title = strip_html(item.findtext('title', default=''))
        link = collapse_ws(item.findtext('link', default=''))
        description_html = item.findtext('description', default='') or ''
        content_html = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', default='') or description_html
        summary = strip_html(description_html or content_html)
        full_text = truncate(strip_html(content_html or description_html), 2800)
        pub = item.findtext('pubDate', default='') or item.findtext('{http://purl.org/dc/elements/1.1/}date', default='')
        if not title or not link:
            continue
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(summary, 460),
            'full_text': full_text or summary,
            'published': parse_date(pub),
            'source': source.name,
            'source_type': source.source_type,
            'source_priority': source.priority,
            'feed_img': extract_rss_image(item, link, description_html),
        })
    return items


def parse_atom(xml_bytes: bytes, source: SourceConfig) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    items = []
    for entry in root.findall('atom:entry', NS):
        title = strip_html(entry.findtext('atom:title', default='', namespaces=NS))
        summary_html = entry.findtext('atom:summary', default='', namespaces=NS) or ''
        content_html = entry.findtext('atom:content', default='', namespaces=NS) or summary_html
        summary = strip_html(summary_html or content_html)
        full_text = truncate(strip_html(content_html or summary_html), 2800)
        published = entry.findtext('atom:published', default='', namespaces=NS) or entry.findtext('atom:updated', default='', namespaces=NS)
        link = ''
        for link_el in entry.findall('atom:link', NS):
            href = collapse_ws(link_el.get('href', ''))
            rel = link_el.get('rel', 'alternate')
            if href and rel == 'alternate':
                link = href
                break
        if not title or not link:
            continue
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(summary, 460),
            'full_text': full_text or summary,
            'published': parse_date(published),
            'source': source.name,
            'source_type': source.source_type,
            'source_priority': source.priority,
            'feed_img': extract_atom_image(entry, link, summary_html or content_html),
        })
    return items


def classify_category(text: str, source_name: str) -> str:
    low = normalize_text(f'{source_name} {text}')
    for category, keywords in CATEGORY_RULES:
        if any(keyword in low for keyword in keywords):
            return category
    return 'Astronomia'


def cat_cls(category: str) -> str:
    low = normalize_text(category).replace(' ', '-')
    return 'terra' if low == 'ciencias-da-terra' else low


def infer_thematic_image(title: str, summary: str, source_name: str, category: str) -> str:
    text = normalize_text(' '.join([title, summary, source_name, category]))
    candidates = []
    for pattern, keys in TOPIC_IMAGE_RULES:
        if re.search(pattern, text, flags=re.I):
            candidates.extend(IMG[key] for key in keys if key in IMG)
    if not candidates:
        candidates.extend(IMG[key] for key in CATEGORY_IMAGE_FALLBACKS.get(category, ['pillars', 'andromeda']) if key in IMG)
    unique = unique_keep_order(candidates)
    if not unique:
        unique = [IMG['pillars'], IMG['andromeda']]
    seed = f'{title}|{summary}|{source_name}|{category}'
    return unique[stable_index(seed, len(unique))]


def freshness_points(dt: datetime) -> int:
    hours = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if hours <= 18:
        return 10
    if hours <= 48:
        return 7
    if hours <= 96:
        return 4
    return 1


def editorial_band_from_score(score: int) -> str:
    if score >= 92:
        return 'flagship'
    if score >= 80:
        return 'high'
    if score >= 68:
        return 'standard'
    return 'watch'


def evidence_key_for(item: dict) -> str:
    if item.get('source_type') == 'preprint':
        return 'preprint'
    if item.get('source_type') == 'journal':
        return 'peer_reviewed'
    return 'institutional_update'


def compute_editorial_profile(item: dict) -> dict:
    low = normalize_text(' '.join([item['title'], item['summary'], item['link'], item['source']]))
    category = classify_category(item['title'] + ' ' + item['summary'], item['source'])

    source_score = int(item.get('source_priority', 50))
    evidence_score = 58 if item.get('source_type') == 'preprint' else 82
    relevance_score = 48
    accessibility_score = 52
    novelty_score = 45 + freshness_points(item['published'])
    risk_score = 0

    if any(re.search(pattern, low) for pattern in BAD_TITLE_PATTERNS):
        risk_score += 45
    if any(part in low for part in BAD_URL_PARTS):
        risk_score += 50
    if any(pattern in low for pattern in BAD_TEXT_HINTS):
        risk_score += 35
    if any(hint in low for hint in PROMO_HINTS):
        risk_score += 25
    if re.search(r'\b(video|image|gallery|photos?|audio)\b', low):
        risk_score += 22
    if re.search(r'\b(profile|interview|award|awards|podcast|career|livestream)\b', low):
        risk_score += 24
    if any(hint in low for hint in TECHNICAL_JARGON_HINTS):
        accessibility_score -= 16
        relevance_score -= 10
    if len(item['title']) > 140:
        accessibility_score -= 8
    if re.search(r'[\$\\]|\bep\$_|\bdr\d\b', item['title'].lower()):
        accessibility_score -= 10

    if any(hint in low for hint in SCIENTIFIC_RESULT_HINTS):
        relevance_score += 18
    if any(hint in low for hint in PUBLIC_INTEREST_HINTS):
        relevance_score += 14
        accessibility_score += 8
    if any(hint in low for hint in HARD_RESEARCH_HINTS):
        evidence_score += 6
    if category in ('Astronomia', 'Cosmologia', 'Astrofísica', 'Exoplanetas'):
        relevance_score += 8
    elif category in ('Física', 'Química'):
        relevance_score += 2
    if item.get('source_type') == 'preprint' and not any(keyword in low for keyword in BROAD_INTEREST_PREPRINT_HINTS):
        risk_score += 24
        relevance_score -= 12
    if item.get('source_type') == 'preprint' and any(keyword in low for keyword in BROAD_INTEREST_PREPRINT_HINTS):
        relevance_score += 6

    overall = round(
        0.24 * source_score +
        0.24 * evidence_score +
        0.26 * relevance_score +
        0.14 * accessibility_score +
        0.12 * novelty_score -
        risk_score
    )
    overall = max(0, min(100, overall))
    return {
        'overall': overall,
        'source_score': max(0, min(100, source_score)),
        'evidence_score': max(0, min(100, evidence_score)),
        'relevance_score': max(0, min(100, relevance_score)),
        'accessibility_score': max(0, min(100, accessibility_score)),
        'novelty_score': max(0, min(100, novelty_score)),
        'band': editorial_band_from_score(overall),
        'evidence_key': evidence_key_for(item),
        'category': category,
    }


def score_item(item: dict) -> int:
    return compute_editorial_profile(item)['overall']


def is_noise(item: dict) -> bool:
    low = normalize_text(' '.join([item['title'], item['summary'], item['link']]))
    profile = compute_editorial_profile(item)
    if profile['overall'] < 62:
        return True
    if len(item['summary']) < 55:
        return True
    if low.startswith('image:') or low.startswith('video:'):
        return True
    if source_domain(item.get('link', '')).endswith('youtube.com'):
        return True
    return False


def dedupe_and_rank(items: list[dict]) -> list[dict]:
    seen = set()
    per_source = Counter()
    preprints = 0
    per_category = Counter()
    ranked = []
    decorated = []
    category_order = [
        'Astronomia', 'Cosmologia', 'Astrofísica', 'Exoplanetas',
        'Física', 'Biologia', 'Química', 'Ciências da Terra'
    ]

    for item in items:
        profile = compute_editorial_profile(item)
        item['editorial_profile'] = profile
        decorated.append(item)

    decorated.sort(key=lambda x: (x['editorial_profile']['overall'], x['editorial_profile']['relevance_score'], x['published']), reverse=True)

    def can_take(item: dict) -> bool:
        key = re.sub(r'\W+', '', normalize_text(item['title']))
        if key in seen:
            return False
        if is_noise(item):
            return False
        if per_source[item['source']] >= MAX_POSTS_PER_SOURCE:
            return False
        if item['source_type'] == 'preprint' and preprints >= MAX_PREPRINTS:
            return False
        if len(ranked) >= MAX_POSTS:
            return False
        return True

    def take(item: dict) -> None:
        nonlocal preprints
        key = re.sub(r'\W+', '', normalize_text(item['title']))
        seen.add(key)
        item['score'] = item['editorial_profile']['overall']
        ranked.append(item)
        per_source[item['source']] += 1
        per_category[item['editorial_profile']['category']] += 1
        if item['source_type'] == 'preprint':
            preprints += 1

    for category in category_order:
        if MIN_POSTS_PER_CATEGORY <= 0:
            break
        if per_category[category] >= MIN_POSTS_PER_CATEGORY:
            continue
        for item in decorated:
            if item['editorial_profile']['category'] != category:
                continue
            if can_take(item):
                take(item)
                break

    for item in decorated:
        if can_take(item):
            take(item)
        if len(ranked) >= MAX_POSTS:
            break

    return ranked

def split_sentences(text: str) -> list[str]:
    text = collapse_ws(strip_html(text))
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for part in parts:
        part = collapse_ws(part).strip(' "“”‘’')
        if len(part) < 35:
            continue
        out.append(part)
    return out


def sentence_score(sentence: str) -> tuple[int, int]:
    low = normalize_text(sentence)
    score = 0
    if re.search(r'\d', sentence):
        score += 4
    if re.search(r'\b(jwst|nasa|esa|jpl|cern|euclid|desi|hubble|rubin|mars|moon|earth|arxiv)\b', low):
        score += 4
    if re.search(r'\b(first|new|detected|measured|observed|analysis|results|reveals|maps|launch|mission|constraints)\b', low):
        score += 3
    if len(sentence) > 210:
        score -= 1
    return score, len(sentence)


def gather_fact_sentences(item: dict) -> list[str]:
    pool = []
    pool.extend(split_sentences(item.get('summary', '')))
    pool.extend(split_sentences(item.get('full_text', '')))
    page_text = extract_page_text(item.get('link', ''))
    if page_text:
        pool.extend(split_sentences(page_text))
    scored = []
    seen = set()
    for sentence in pool:
        normalized = normalize_text(sentence)
        if normalized in seen:
            continue
        seen.add(normalized)
        if any(bad in normalized for bad in BAD_TEXT_HINTS):
            continue
        scored.append((sentence_score(sentence), sentence))
    scored.sort(reverse=True)
    return [sentence for _, sentence in scored[:6]]


def reading_time(text: str, lang: str = 'pt') -> str:
    words = max(1, len(strip_html(text).split()))
    minutes = max(4, round(words / 170))
    return f'{minutes} min de leitura' if lang == 'pt' else f'{minutes} min read'


def translate_text(text: str, target_lang: str) -> str:
    text = collapse_ws(text)
    if not text:
        return ''
    cache_key = (target_lang, text)
    cached = TRANSLATION_CACHE.get(cache_key)
    if cached is not None:
        return cached
    params = urllib.parse.urlencode({
        'client': 'gtx', 'sl': 'auto', 'tl': target_lang, 'dt': 't', 'q': text,
    })
    url = f'{TRANSLATE_ENDPOINT}?{params}'
    try:
        raw = fetch(url, timeout=TRANSLATE_TIMEOUT)
        data = json.loads(raw.decode('utf-8', errors='ignore'))
        translated = ''.join(part[0] for part in (data[0] or []) if part and part[0]).strip()
        if translated:
            TRANSLATION_CACHE[cache_key] = translated
            return translated
    except Exception:
        pass
    TRANSLATION_CACHE[cache_key] = text
    return text


def distinct_facts(facts: list[str], limit: int = 4) -> list[str]:
    out = []
    seen = set()
    for fact in facts:
        clean = collapse_ws(fact)
        if not clean:
            continue
        key = normalize_text(clean)
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def trimmed_fact(text: str, limit: int = 240) -> str:
    text = collapse_ws(text)
    text = re.sub(r'^[A-Z][^:]{0,28}:\s+', '', text)
    return truncate(text, limit)


def compose_lede(title: str, summary: str, facts: list[str], source_type: str, lang: str, seed: str) -> str:
    summary = collapse_ws(summary)
    fact = trimmed_fact(facts[0], 200) if facts else summary
    if lang == 'pt':
        if source_type == 'preprint':
            options = [
                f'{summary} Por enquanto, este é o núcleo do resultado em circulação técnica.',
                f'{summary} É isso que o novo preprint realmente coloca em discussão.',
                f'{summary} Antes de qualquer entusiasmo extra, é esse o ponto factual do novo trabalho.',
            ]
        elif source_type == 'agency':
            options = [
                f'{summary} É a partir desse eixo que a atualização mais recente merece ser lida.',
                f'{summary} Por trás do anúncio institucional, este é o dado que realmente sustenta a história.',
                f'{summary} Em linguagem de redação, é esse o ponto que transforma a atualização em notícia e não apenas em comunicado.',
            ]
        else:
            options = [
                f'{summary} Esse é o núcleo do material mais recente.',
                f'{summary} É a partir desse resultado que a discussão científica realmente avança agora.',
                f'{summary} No centro desta história está exatamente esse resultado: {fact}',
            ]
    else:
        if source_type == 'preprint':
            options = [
                f'{summary} For now, that is the core of the result circulating as a technical preprint.',
                f'{summary} That is what the new preprint is actually putting on the table.',
                f'{summary} Before extra excitement is added, that is the factual center of the new work.',
            ]
        elif source_type == 'agency':
            options = [
                f'{summary} That is the axis around which the latest update deserves to be read.',
                f'{summary} Beneath the institutional announcement, that is the point that genuinely supports the story.',
                f'{summary} In newsroom terms, that is what turns the update into a story rather than just a release.',
            ]
        else:
            options = [
                f'{summary} That is the core of the latest material.',
                f'{summary} This is the result from which the scientific discussion genuinely moves forward.',
                f'{summary} At the center of this story is a straightforward point: {fact}',
            ]
    return stable_pick(options, seed + source_type)


def build_fact_paragraph(summary: str, facts: list[str], category: str, source_type: str, lang: str, seed: str) -> str:
    useful = distinct_facts(facts, 3)
    first = trimmed_fact(useful[0], 230) if useful else trimmed_fact(summary, 230)
    second = trimmed_fact(useful[1], 220) if len(useful) > 1 else ''
    if lang == 'pt':
        openers = [
            'Quando o material é lido sem pressa, a estrutura factual fica bem menos nebulosa.',
            'A leitura cuidadosa da base revela rapidamente onde a história realmente se apoia.',
            'Separada a manchete do restante, a evidência disponível fica mais fácil de enxergar.',
        ]
        closing = {
            'preprint': ' Isso ajuda a manter a discussão dentro do que o texto técnico de fato entrega, sem transformá-lo prematuramente em consenso.',
            'agency': ' Isso delimita o que é evidência, o que é cronograma e o que ainda pertence mais ao campo do anúncio do que ao da confirmação.',
            'journal': ' É esse conjunto que define o alcance real do resultado e impede uma leitura maior do que a evidência suporta.',
        }[source_type]
    else:
        openers = [
            'Once the material is read carefully, its factual structure becomes much less hazy.',
            'A close reading of the source quickly shows where the story actually rests.',
            'Once the headline is separated from everything around it, the available evidence is easier to see.',
        ]
        closing = {
            'preprint': ' That helps keep the discussion inside what the technical text actually delivers, rather than promoting it too early into consensus.',
            'agency': ' That separates evidence from schedule and from the portion of the story that still belongs more to announcement than to confirmation.',
            'journal': ' That is what defines the real scope of the result and keeps the reading from outrunning the evidence.',
        }[source_type]
    pieces = [stable_pick(openers, seed + category), first]
    if second and normalize_text(second) != normalize_text(first):
        pieces.append(second)
    return ' '.join(piece for piece in pieces if piece) + closing


def build_context_bridge(category: str, lang: str, seed: str) -> str:
    pt = {
        'Astronomia': [
            'É aí que a notícia deixa de ser apenas observacional e passa a ter peso interpretativo.',
            'Esse é o ponto em que a história entra no terreno mais sério da inferência astronômica.',
        ],
        'Cosmologia': [
            'É aí que a discussão encosta nas perguntas mais amplas do modelo cosmológico.',
            'É nesse ponto que a notícia toca as engrenagens conceituais da cosmologia atual.',
        ],
        'Astrofísica': [
            'É nesse trecho que a matéria ganha densidade física de verdade.',
            'É aqui que a leitura precisa migrar da descrição para o mecanismo.',
        ],
        'Exoplanetas': [
            'É aqui que o fascínio popular precisa dar lugar à caracterização cuidadosa.',
            'É nesse ponto que a conversa precisa sair do imaginário e voltar aos parâmetros observáveis.',
        ],
        'Física': [
            'É aqui que o rigor metodológico pesa mais do que o impacto da manchete.',
            'É nesse momento que a leitura jornalística precisa acompanhar o método e não o brilho do anúncio.',
        ],
        'Biologia': [
            'É nesse trecho que a diferença entre pista experimental e conclusão ampla precisa ficar nítida.',
            'É aqui que a leitura cuidadosa impede que um resultado localizado vire promessa universal.',
        ],
        'Química': [
            'É aqui que a robustez da caracterização passa a valer mais do que a novidade do enunciado.',
            'É nesse ponto que a solidez analítica separa avanço real de formulação chamativa.',
        ],
        'Ciências da Terra': [
            'É aqui que a notícia precisa ser conectada a séries históricas e não a um instante isolado.',
            'É nesse ponto que a leitura ganha valor ao ser encaixada em processos mais amplos do sistema terrestre.',
        ],
    }
    en = {
        'Astronomia': [
            'That is where the story stops being merely observational and starts to gain interpretive weight.',
            'This is the point at which the story enters the more serious terrain of astronomical inference.',
        ],
        'Cosmologia': [
            'That is where the discussion touches the largest questions inside the cosmological model.',
            'This is the point at which the story reaches the conceptual machinery of contemporary cosmology.',
        ],
        'Astrofísica': [
            'This is where the story gains real physical density.',
            'This is the point where the reading has to move from description to mechanism.',
        ],
        'Exoplanetas': [
            'This is where popular fascination has to give way to careful characterization.',
            'At this point, the conversation needs to leave imagination behind and return to observable parameters.',
        ],
        'Física': [
            'This is where methodological rigor matters more than headline impact.',
            'At this stage, journalistic reading has to follow the method rather than the glow of the announcement.',
        ],
        'Biologia': [
            'This is where the line between experimental hint and broad conclusion has to become explicit.',
            'At this stage, careful reading prevents a local result from turning into a universal promise.',
        ],
        'Química': [
            'This is where the strength of the characterization matters more than the novelty of the claim.',
            'At this point, analytical solidity separates a real advance from a catchy formulation.',
        ],
        'Ciências da Terra': [
            'This is where the story has to be connected to historical series rather than to a single moment.',
            'At this point, the reading becomes more useful when it is fitted into broader Earth-system processes.',
        ],
    }
    mapping = en if lang == 'en' else pt
    return stable_pick(mapping.get(category, mapping['Astronomia']), seed + category + lang)


def category_context(category: str, lang: str) -> str:
    pt = {
        'Astronomia': 'Em astronomia, um resultado ganha peso não pelo brilho do título, mas pela capacidade de melhorar a reconstrução física do sistema observado, refinar parâmetros e abrir espaço para medições independentes posteriores.',
        'Cosmologia': 'Em cosmologia, cada resultado relevante pressiona o modelo padrão em escalas máximas. O que importa aqui é saber se a evidência altera a leitura de expansão cósmica, estrutura em grande escala ou conteúdo energético do universo.',
        'Astrofísica': 'Na astrofísica, a pergunta central é sempre a mesma: que mecanismo físico está realmente sendo isolado? Boas matérias nessa área precisam distinguir entre comportamento observado, inferência teórica e cenário ainda especulativo.',
        'Exoplanetas': 'Em exoplanetas, a disciplina exige moderação. Massa, raio, temperatura, composição atmosférica e geometria orbital raramente são resolvidos de uma só vez, então qualquer afirmação sobre habitabilidade pede contexto duro e cautela.',
        'Física': 'Em física, relevância jornalística sem rigor metodológico é ornamento. O resultado só merece espaço nobre quando estatística, desenho experimental e consistência teórica sustentam a narrativa com alguma solidez.',
        'Biologia': 'Em biologia, a diferença entre indício e demonstração é decisiva. O leitor precisa saber que tipo de sistema foi estudado, o que de fato foi medido e até onde a extrapolação pode ser levada sem tropeçar em exagero.',
        'Química': 'Em química, o valor da notícia depende da robustez da evidência estrutural, espectroscópica ou cinética. É a qualidade da caracterização que separa anúncio interessante de avanço convincente.',
        'Ciências da Terra': 'Nas ciências da Terra, a utilidade do resultado aparece quando ele se conecta a séries históricas, medições independentes e implicações observacionais amplas, não apenas a uma imagem impactante ou a um evento isolado.',
    }
    en = {
        'Astronomia': 'In astronomy, a result matters not because of a flashy title, but because it improves the physical reconstruction of the observed system, refines parameters and creates room for later independent measurements.',
        'Cosmologia': 'In cosmology, every relevant result presses on the standard model at the largest scales. What matters is whether the evidence changes how we read cosmic expansion, large-scale structure or the energy content of the universe.',
        'Astrofísica': 'In astrophysics, the key question is always the same: what physical mechanism is actually being isolated? Strong reporting in this area has to distinguish between observed behavior, theoretical inference and still-speculative scenarios.',
        'Exoplanetas': 'In exoplanet science, moderation is mandatory. Mass, radius, temperature, atmospheric composition and orbital geometry are rarely resolved all at once, so every habitability claim requires hard context and caution.',
        'Física': 'In physics, news value without methodological rigor is decoration. A result only deserves prime placement when statistics, experimental design and theoretical consistency genuinely support the story.',
        'Biologia': 'In biology, the gap between a hint and a demonstration is decisive. Readers need to know what system was studied, what was actually measured and how far the extrapolation can go before it becomes exaggeration.',
        'Química': 'In chemistry, the news value depends on the robustness of the structural, spectroscopic or kinetic evidence. The quality of the characterization is what separates an interesting announcement from a convincing advance.',
        'Ciências da Terra': 'In Earth science, usefulness emerges when a result connects to historical series, independent measurements and broader observational implications, rather than simply to a striking image or a single event.',
    }
    return (en if lang == 'en' else pt).get(category, (en if lang == 'en' else pt)['Astronomia'])


def caution_text(source_type: str, lang: str) -> str:
    if source_type == 'preprint':
        return SOURCE_NOTES['preprint'][lang]
    if source_type == 'agency':
        return SOURCE_NOTES['agency'][lang]
    return SOURCE_NOTES['journal'][lang]


def next_steps_text(category: str, source_type: str, lang: str) -> str:
    pt = {
        'Astronomia': 'O próximo teste relevante será verificar se observações adicionais, idealmente em outros comprimentos de onda ou com outro instrumento, confirmam a mesma leitura.',
        'Cosmologia': 'Agora o ponto decisivo é saber se o efeito se mantém quando entra em confronto com outros levantamentos, outras calibrações e controles mais duros de sistemáticos.',
        'Astrofísica': 'Daqui para frente, o valor real da notícia dependerá da convergência entre dados independentes, modelagem física e comparação com cenários alternativos.',
        'Exoplanetas': 'A etapa seguinte é obter restrições independentes de atmosfera, massa, raio ou dinâmica orbital, porque é aí que a caracterização deixa de ser promissora e passa a ser robusta.',
        'Física': 'Em física, o filtro final continua sendo o mesmo de sempre: mais dados, mais escrutínio e menos tolerância a interpretações que sobrevivem apenas em condições muito específicas.',
        'Biologia': 'O passo seguinte é testar reprodutibilidade, mecanismo e generalização em outros modelos, sem confundir resultado promissor com conclusão definitiva.',
        'Química': 'O avanço se consolida quando outras técnicas e outros grupos reproduzem a mesma interpretação com leituras compatíveis.',
        'Ciências da Terra': 'O teste mais forte será encaixar esse resultado em séries temporais mais longas e em instrumentos independentes, reduzindo o risco de leitura episódica.',
    }
    en = {
        'Astronomia': 'The next relevant test is whether additional observations, ideally at other wavelengths or with another instrument, support the same reading.',
        'Cosmologia': 'The decisive point now is whether the effect survives confrontation with other surveys, other calibrations and tighter systematic controls.',
        'Astrofísica': 'From here on, the real value of the story depends on convergence between independent data, physical modeling and comparison with alternative scenarios.',
        'Exoplanetas': 'The next step is to obtain independent constraints on atmosphere, mass, radius or orbital dynamics, because that is where a promising target becomes a robustly characterized one.',
        'Física': 'In physics, the final filter remains the same as ever: more data, more scrutiny and less tolerance for interpretations that survive only under narrow assumptions.',
        'Biologia': 'The next step is to test reproducibility, mechanism and generalization in other models, without confusing a promising result with a final answer.',
        'Química': 'An advance becomes durable when other techniques and other groups reproduce the same interpretation with compatible measurements.',
        'Ciências da Terra': 'The strongest test will be to fit the result into longer time series and independent instruments, reducing the risk of episodic over-reading.',
    }
    text = (en if lang == 'en' else pt).get(category, (en if lang == 'en' else pt)['Astronomia'])
    if source_type == 'preprint':
        addon = ' Antes disso, o resultado ainda precisa sobreviver ao processo formal de revisão por pares.' if lang == 'pt' else ' Before that, the result still has to survive formal peer review.'
        return text + addon
    return text


def build_limits_paragraph(source_type: str, caution: str, lang: str, seed: str) -> str:
    if lang == 'pt':
        intros = {
            'preprint': [
                'A reserva metodológica aqui não é detalhe lateral.',
                'Há uma cautela elementar que precisa acompanhar a leitura.',
            ],
            'agency': [
                'Também convém ajustar o foco sobre a origem do material.',
                'A natureza da fonte muda a forma correta de ler a notícia.',
            ],
            'journal': [
                'Mesmo em material mais sólido, prudência continua sendo parte do método.',
                'Nem mesmo uma base mais robusta elimina a necessidade de cautela interpretativa.',
            ],
        }
    else:
        intros = {
            'preprint': [
                'The methodological reservation here is not a side note.',
                'There is a basic caution that has to accompany the reading.',
            ],
            'agency': [
                'It is also worth refocusing on the origin of the material.',
                'The nature of the source changes the correct way to read the story.',
            ],
            'journal': [
                'Even with a stronger base, prudence remains part of the method.',
                'A more solid footing still does not remove the need for interpretive caution.',
            ],
        }
    return f"{stable_pick(intros[source_type], seed + source_type + lang)} {caution}"


def build_pull_quote(summary: str, facts: list[str], source_type: str, lang: str, seed: str) -> str:
    candidate = trimmed_fact(facts[0], 180) if facts else trimmed_fact(summary, 180)
    if candidate and len(candidate) >= 60:
        return candidate
    if lang == 'pt':
        options = [
            'A parte útil de uma boa matéria científica começa quando o texto deixa de repetir a manchete e passa a medir o alcance real da evidência.',
            'Em ciência, o valor jornalístico não está no espanto isolado, mas no que resiste quando o entusiasmo é submetido ao método.',
        ]
    else:
        options = [
            'The useful part of a science story begins when the text stops repeating the headline and starts measuring the actual reach of the evidence.',
            'In science, journalistic value does not lie in isolated surprise, but in what remains after excitement is pushed through method.',
        ]
    return stable_pick(options, seed + 'quote')


def section_heading(kind: str, lang: str, category: str, seed: str) -> str:
    pt = {
        'evidence': ['Onde a evidência está', 'O que o material entrega de fato', 'O que, de fato, saiu do papel'],
        'relevance': ['Por que isso entra no radar', 'Onde está a relevância', 'Por que vale atenção agora'],
        'limits': ['O que ainda não está resolvido', 'As reservas necessárias', 'O que continua em aberto'],
    }
    en = {
        'evidence': ['Where the evidence sits', 'What the material actually delivers', 'What has genuinely been established'],
        'relevance': ['Why this enters the radar', 'Where the relevance lies', 'Why this deserves attention now'],
        'limits': ['What remains unresolved', 'The necessary reservations', 'What is still open'],
    }
    mapping = en if lang == 'en' else pt
    return stable_pick(mapping[kind], seed + kind + category + lang)


def build_highlights(title: str, summary: str, facts: list[str], source_type: str, lang: str) -> list[str]:
    useful = distinct_facts(facts, 2)
    if lang == 'pt':
        bullets = [f'Ponto central: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Dado-chave: {trimmed_fact(useful[0], 145)}')
        caution = {
            'preprint': 'Cautela: resultado ainda sem revisão por pares.',
            'agency': 'Leitura crítica: origem institucional exige separar anúncio de evidência.',
            'journal': 'Base de leitura: material com lastro científico explícito.',
        }[source_type]
        bullets.append(caution)
    else:
        bullets = [f'Core point: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Key detail: {trimmed_fact(useful[0], 145)}')
        caution = {
            'preprint': 'Caution: result not yet peer reviewed.',
            'agency': 'Critical reading: institutional origin requires separating announcement from evidence.',
            'journal': 'Reading base: material with explicit scientific backing.',
        }[source_type]
        bullets.append(caution)
    return bullets[:3]


def build_body(title: str, summary: str, facts: list[str], category: str, source: str, source_type: str, lang: str) -> str:
    seed = title + lang
    useful = distinct_facts(facts, 4)
    lede = compose_lede(title, summary, useful, source_type, lang, seed)
    evidence_paragraph = build_fact_paragraph(summary, useful, category, source_type, lang, seed)
    bridge = build_context_bridge(category, lang, seed)
    why = category_context(category, lang)
    caution = build_limits_paragraph(source_type, caution_text(source_type, lang), lang, seed)
    next_steps = next_steps_text(category, source_type, lang)
    quote = build_pull_quote(summary, useful, source_type, lang, seed)
    secondary = useful[1] if len(useful) > 1 else ''
    tertiary = useful[2] if len(useful) > 2 else ''

    evidence_heading = section_heading('evidence', lang, category, seed)
    relevance_heading = section_heading('relevance', lang, category, seed)
    limits_heading = section_heading('limits', lang, category, seed)

    if lang == 'pt':
        body = [
            f'<p>{html.escape(lede)}</p>',
            f'<p>{html.escape(evidence_paragraph)}</p>',
            f'<h2>{html.escape(evidence_heading)}</h2>',
        ]
        if secondary:
            body.append(f'<p>{html.escape(trimmed_fact(secondary, 260))}</p>')
        else:
            body.append(f'<p>{html.escape(trimmed_fact(summary, 250))}</p>')
        if tertiary and normalize_text(tertiary) not in {normalize_text(secondary), normalize_text(summary)}:
            body.append(f'<p>{html.escape(trimmed_fact(tertiary, 260))}</p>')
        body.extend([
            f'<h2>{html.escape(relevance_heading)}</h2>',
            f'<p>{html.escape(bridge)} {html.escape(why)}</p>',
            f'<blockquote>{html.escape(quote)}</blockquote>',
            f'<h2>{html.escape(limits_heading)}</h2>',
            f'<p>{html.escape(caution)}</p>',
            f'<p>{html.escape(next_steps)}</p>',
        ])
    else:
        body = [
            f'<p>{html.escape(lede)}</p>',
            f'<p>{html.escape(evidence_paragraph)}</p>',
            f'<h2>{html.escape(evidence_heading)}</h2>',
        ]
        if secondary:
            body.append(f'<p>{html.escape(trimmed_fact(secondary, 260))}</p>')
        else:
            body.append(f'<p>{html.escape(trimmed_fact(summary, 250))}</p>')
        if tertiary and normalize_text(tertiary) not in {normalize_text(secondary), normalize_text(summary)}:
            body.append(f'<p>{html.escape(trimmed_fact(tertiary, 260))}</p>')
        body.extend([
            f'<h2>{html.escape(relevance_heading)}</h2>',
            f'<p>{html.escape(bridge)} {html.escape(why)}</p>',
            f'<blockquote>{html.escape(quote)}</blockquote>',
            f'<h2>{html.escape(limits_heading)}</h2>',
            f'<p>{html.escape(caution)}</p>',
            f'<p>{html.escape(next_steps)}</p>',
        ])
    return ''.join(body)


def clean_sentence_for_deck(text: str) -> str:
    text = collapse_ws(text)
    text = re.sub(r'^[A-Z][^:]{0,24}:\s+', '', text)
    text = re.sub(r'\s*\(.*?\)', '', text)
    return truncate(text, 240)


def build_deck(summary: str, facts: list[str]) -> str:
    base = clean_sentence_for_deck(summary) if summary else ''
    if len(base) >= 90:
        return base
    useful = distinct_facts(facts, 2)
    for fact in useful:
        candidate = clean_sentence_for_deck(fact)
        if len(candidate) >= 90:
            return candidate
    return base or clean_sentence_for_deck(useful[0] if useful else '')

def choose_post_image(item: dict, category: str) -> str:
    feed_img = clean_image_url(item.get('feed_img') or '')
    if feed_img and image_url_looks_good(feed_img):
        return feed_img
    if item.get('source_type') != 'preprint':
        page_img = fetch_page_image(item.get('link', ''))
        if page_img and image_url_looks_good(page_img):
            return page_img
    return infer_thematic_image(item.get('title', ''), item.get('summary', ''), item.get('source', ''), category)


def to_post(item: dict, idx: int, regular_rank: int) -> dict:
    profile = item.get('editorial_profile') or compute_editorial_profile(item)
    category = profile['category']
    facts_en = gather_fact_sentences(item)
    title_en = collapse_ws(item['title'])
    summary_en = build_deck(item['summary'], facts_en)
    highlights_en = build_highlights(title_en, summary_en, facts_en, item['source_type'], 'en')
    body_en = build_body(title_en, summary_en, facts_en, category, item['source'], item['source_type'], 'en')

    title_pt = translate_text(title_en, 'pt')
    summary_pt = translate_text(summary_en, 'pt')
    facts_pt = [translate_text(fact, 'pt') for fact in facts_en[:6]]
    highlights_pt = build_highlights(title_pt, summary_pt, facts_pt, item['source_type'], 'pt')
    body_pt = build_body(title_pt, summary_pt, facts_pt, category, item['source'], item['source_type'], 'pt')

    dt = item['published']
    slug = slugify(title_en)
    canonical = f'{SITE_URL}?article={slug}'
    image = choose_post_image(item, category)
    is_featured = item['source_type'] != 'preprint' and regular_rank < 3 and profile['band'] in ('flagship', 'high')
    is_trending = item['source_type'] != 'preprint' and regular_rank < 6
    evidence_key = profile['evidence_key']
    evidence_label_pt = EVIDENCE_LABELS[evidence_key]['pt']
    evidence_label_en = EVIDENCE_LABELS[evidence_key]['en']
    editorial_band = profile['band']
    editorial_band_pt = EDITORIAL_BANDS[editorial_band]['pt']
    editorial_band_en = EDITORIAL_BANDS[editorial_band]['en']
    keywords_pt = unique_keep_order([category, item['source'], 'Cosmos Week'] + [frag.strip() for frag in re.split(r'[,;:\-]', title_pt) if len(frag.strip()) > 3])[:8]
    keywords_en = [translate_text(keyword, 'en') if keyword not in (item['source'], 'Cosmos Week') else keyword for keyword in keywords_pt]
    domain = source_domain(item['link'])

    return {
        'id': idx + 1,
        'slug': slug,
        'cat': category,
        'catCls': cat_cls(category),
        'img': image,
        'title': title_pt,
        'title_pt': title_pt,
        'title_en': title_en,
        'sub': truncate(summary_pt, 180),
        'sub_pt': truncate(summary_pt, 180),
        'sub_en': truncate(summary_en, 180),
        'excerpt': truncate(summary_pt, 260),
        'excerpt_pt': truncate(summary_pt, 260),
        'excerpt_en': truncate(summary_en, 260),
        'body': body_pt,
        'body_pt': body_pt,
        'body_en': body_en,
        'highlights': highlights_pt,
        'highlights_pt': highlights_pt,
        'highlights_en': highlights_en,
        'date': format_date_pt(dt),
        'date_pt': format_date_pt(dt),
        'date_en': format_date_en(dt),
        'time': dt.strftime('%Hh%M'),
        'time_pt': dt.strftime('%Hh%M'),
        'time_en': dt.strftime('%H:%M UTC'),
        'read': reading_time(body_pt, 'pt'),
        'read_pt': reading_time(body_pt, 'pt'),
        'read_en': reading_time(body_en, 'en'),
        'publishedIso': dt.isoformat(),
        'lastModifiedIso': dt.isoformat(),
        'source': item['source'],
        'sourceDomain': domain,
        'sourceType': item['source_type'],
        'sourceTypeLabel': SOURCE_TYPE_LABELS[item['source_type']]['pt'],
        'sourceTypeLabel_pt': SOURCE_TYPE_LABELS[item['source_type']]['pt'],
        'sourceTypeLabel_en': SOURCE_TYPE_LABELS[item['source_type']]['en'],
        'sourceNote': SOURCE_NOTES[item['source_type']]['pt'],
        'sourceNote_pt': SOURCE_NOTES[item['source_type']]['pt'],
        'sourceNote_en': SOURCE_NOTES[item['source_type']]['en'],
        'evidenceKey': evidence_key,
        'evidenceLabel': evidence_label_pt,
        'evidenceLabel_pt': evidence_label_pt,
        'evidenceLabel_en': evidence_label_en,
        'editorialBand': editorial_band,
        'editorialBandLabel': editorial_band_pt,
        'editorialBandLabel_pt': editorial_band_pt,
        'editorialBandLabel_en': editorial_band_en,
        'keywords': keywords_pt,
        'keywords_pt': keywords_pt,
        'keywords_en': keywords_en,
        'srcUrl': item['link'],
        'canonicalUrl': canonical,
        'featured': is_featured,
        'trending': is_trending,
        'isPreprint': item['source_type'] == 'preprint',
        'score': profile['overall'],
        'scoreBreakdown': {
            'source': profile['source_score'],
            'evidence': profile['evidence_score'],
            'relevance': profile['relevance_score'],
            'accessibility': profile['accessibility_score'],
            'novelty': profile['novelty_score'],
        },
    }


def build_feed(posts: list[dict]) -> None:
    items = []
    for post in posts[:18]:
        pub_str = datetime.fromisoformat(post['publishedIso']).strftime('%a, %d %b %Y %H:%M:%S +0000')
        categories = ''.join(f'<category>{xml_escape(cat)}</category>' for cat in unique_keep_order(post.get('keywords_pt', [])[:4]))
        body_preview = xml_escape(strip_html(post.get('body_pt', ''))[:900])
        items.append(
            f'''<item>
              <title>{xml_escape(post['title_pt'])}</title>
              <link>{xml_escape(post['canonicalUrl'])}</link>
              <guid>{xml_escape(post['canonicalUrl'])}</guid>
              <pubDate>{pub_str}</pubDate>
              <author>redacao@cosmosweek.com.br (Cosmos Week)</author>
              <description>{xml_escape(post['excerpt_pt'])}</description>
              {categories}
              <source url="{xml_escape(post['srcUrl'])}">{xml_escape(post['source'])}</source>
              <content:encoded>{body_preview}</content:encoded>
            </item>'''
        )
    last_build = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_DESCRIPTION_PT}</description>
    <language>pt-BR</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <generator>CosmosWeekBot 4.0</generator>
    {''.join(items)}
  </channel>
</rss>
'''
    FEED_XML.write_text(xml, encoding='utf-8')


def build_sitemap(posts: list[dict]) -> None:
    static_urls = [
        (SITE_URL, datetime.now(timezone.utc).date().isoformat()),
        (f'{SITE_URL}?page=arquivo', datetime.now(timezone.utc).date().isoformat()),
        (f'{SITE_URL}?page=sobre', datetime.now(timezone.utc).date().isoformat()),
        (f'{SITE_URL}?page=padroes', datetime.now(timezone.utc).date().isoformat()),
    ]
    dynamic_urls = [(post['canonicalUrl'], post['publishedIso'][:10]) for post in posts]
    all_urls = unique_keep_order(static_urls + dynamic_urls)
    body = '\n'.join(
        f'  <url><loc>{xml_escape(url)}</loc><lastmod>{lastmod}</lastmod></url>'
        for url, lastmod in all_urls
    )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
'''
    SITEMAP_XML.write_text(xml, encoding='utf-8')


def build_robots() -> None:
    ROBOTS_TXT.write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n', encoding='utf-8')


def save_posts(posts: list[dict]) -> None:
    POSTS_JSON.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding='utf-8')
    POSTS_JS.write_text('// Dados atualizados automaticamente para o Cosmos Week\n\nwindow.postsData = ' + json.dumps(posts, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    build_feed(posts)
    build_sitemap(posts)
    build_robots()


def load_all_items() -> list[dict]:
    all_items = []
    for source in SOURCES:
        try:
            raw = fetch(source.url)
            if source.kind == 'atom':
                items = parse_atom(raw, source)
            else:
                items = parse_rss(raw, source)
            all_items.extend(items)
            print(f'OK  {source.name}: {len(items)} itens')
        except Exception as exc:
            print(f'ERR {source.name}: {exc}')
    return all_items


def main() -> None:
    items = load_all_items()
    ranked = dedupe_and_rank(items)
    posts = []
    regular_rank = 0
    for idx, item in enumerate(ranked):
        current_rank = regular_rank if item['source_type'] != 'preprint' else 99
        if item['source_type'] != 'preprint':
            regular_rank += 1
        posts.append(to_post(item, idx, current_rank))
    save_posts(posts)
    counts = Counter(post['sourceType'] for post in posts)
    print(f'{len(posts)} posts salvos em {datetime.now(timezone.utc).isoformat()}')
    print(f'Distribuição por tipo: {dict(counts)}')
    print(f'Base do site: {SITE_URL}')


if __name__ == '__main__':
    main()
