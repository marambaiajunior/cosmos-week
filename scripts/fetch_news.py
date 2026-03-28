import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Optional

POSTS_JSON = Path('posts.json')
POSTS_JS = Path('posts.js')
MAX_POSTS = 36
USER_AGENT = 'CosmosWeekBot/2.0 (+https://github.com/marambaiajunior/cosmos-week)'
REQUEST_TIMEOUT = 30
PAGE_IMAGE_TIMEOUT = 20
MAX_PAGE_IMAGE_FETCHES = 16
TRANSLATE_TIMEOUT = 20
TRANSLATE_ENDPOINT = 'https://translate.googleapis.com/translate_a/single'


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
    'triangulum': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/M33_-_Triangulum_Galaxy.jpg/1280px-M33_-_Triangulum_Galaxy.jpg',
    'whirlpool': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Messier51_sRGB.jpg/1280px-Messier51_sRGB.jpg',
    'sombrero': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/M104_ngc4594_sombrero_galaxy_hi-res.jpg/1280px-M104_ngc4594_sombrero_galaxy_hi-res.jpg',
    'ngc1300': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NGC_1300_Hubble_2005.jpg/1280px-NGC_1300_Hubble_2005.jpg',
    'hubbledeep': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Hubble_ultra_deep_field.jpg/1280px-Hubble_ultra_deep_field.jpg',
    'milkyway': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg/1280px-Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg',
    'carina': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Carina_Nebula_by_Harel_Boren_%28151851961%2C_modified%29.jpg/1280px-Carina_Nebula_by_Harel_Boren_%28151851961%2C_modified%29.jpg',
    'orion': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg/1280px-Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg',
    'crab': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Crab_Nebula.jpg/1280px-Crab_Nebula.jpg',
    'helix': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/NGC7293_%282004%29.jpg/1280px-NGC7293_%282004%29.jpg',
    'veil': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Veil_Nebula_-_NGC_6960_-_Caldwell_34_HST.jpg/1280px-Veil_Nebula_-_NGC_6960_-_Caldwell_34_HST.jpg',
    'lagoon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Hubble_Sees_the_Magic_of_Starlight_in_Lagoon_Nebula.jpg/1280px-Hubble_Sees_the_Magic_of_Starlight_in_Lagoon_Nebula.jpg',
    'triffid': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/VST_images_the_Trifid_Nebula.jpg/1280px-VST_images_the_Trifid_Nebula.jpg',
    'omega': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/A_Hubble_Image_of_the_Omega_Nebula.jpg/1280px-A_Hubble_Image_of_the_Omega_Nebula.jpg',
    'butterfly': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/NGC_6302_%28captured_by_the_Hubble_Space_Telescope%29.jpg/1280px-NGC_6302_%28captured_by_the_Hubble_Space_Telescope%29.jpg',
    'solar': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/1280px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'sunspot': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Sunspots_2400.jpg/1280px-Sunspots_2400.jpg',
    'aurora': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aurora_Borealis_over_Lake_Ladoga.jpg/1280px-Aurora_Borealis_over_Lake_Ladoga.jpg',
    'moon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/1280px-FullMoon2010.jpg',
    'lunarSouthPole': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg/1280px-PIA12233-LROC-ShackletonCrater-SouthPoleMoon.jpg',
    'mars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/1280px-OSIRIS_Mars_true_color.jpg',
    'perseverance': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/PIA23764-Mars2020Rover-ArtistConcept-20190723.jpg/1280px-PIA23764-Mars2020Rover-ArtistConcept-20190723.jpg',
    'jezero': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Jezero_Crater_delta_colored_mosaic.jpg/1280px-Jezero_Crater_delta_colored_mosaic.jpg',
    'jupiter': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/1280px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
    'europa': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Europa-moon-625x443.jpg/1280px-Europa-moon-625x443.jpg',
    'saturn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/1280px-Saturn_during_Equinox.jpg',
    'cassini': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Cassini_Spacecraft_Model.png/1280px-Cassini_Spacecraft_Model.png',
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

SOURCES = [
    {'name': 'NASA', 'url': 'https://www.nasa.gov/feed/', 'kind': 'rss'},
    {'name': 'NASA News Releases', 'url': 'https://www.nasa.gov/news-release/feed/', 'kind': 'rss'},
    {'name': 'ESA Space News', 'url': 'https://www.esa.int/rssfeed/Our_Activities/Space_News', 'kind': 'rss'},
    {'name': 'ESA Space Science', 'url': 'https://www.esa.int/rssfeed/Our_Activities/Space_Science', 'kind': 'rss'},
    {'name': 'arXiv Astrophysics', 'url': 'https://export.arxiv.org/api/query?search_query=cat:astro-ph*&sortBy=submittedDate&sortOrder=descending&max_results=18', 'kind': 'atom'},
    {'name': 'arXiv Physics', 'url': 'https://export.arxiv.org/api/query?search_query=cat:physics*&sortBy=submittedDate&sortOrder=descending&max_results=12', 'kind': 'atom'},
]

CATEGORY_RULES = [
    ('Exoplanetas', [
        'exoplanet', 'exoplaneta', 'biosignature', 'bioassinatura', 'hycean', 'trappist',
        'k2-18', 'super-earth', 'super-terra', 'sub-neptune', 'sub-netuno', 'habitable zone',
        'zona habitavel', 'zona habitável', 'proxima centauri b'
    ]),
    ('Cosmologia', [
        'cosmology', 'cosmologia', 'dark energy', 'energia escura', 'dark matter', 'materia escura',
        'matéria escura', 'cmb', 'big bang', 'hubble tension', 'energia do vacuo', 'euclid'
    ]),
    ('Astrofísica', [
        'black hole', 'buraco negro', 'neutron star', 'estrela de neutrons', 'estrela de nêutrons',
        'magnetar', 'pulsar', 'gravitational wave', 'onda gravitacional', 'kilonova',
        'supernova', 'quasar', 'fast radio burst', 'frb'
    ]),
    ('Física', [
        'physics', 'física', 'fisica', 'quantum', 'quântico', 'quantico', 'lhc', 'cern',
        'higgs', 'quark', 'muon', 'múon', 'partícula', 'particula', 'particle physics'
    ]),
    ('Ciências da Terra', [
        'climate change', 'mudanca climatica', 'mudança climática', 'global warming',
        'earth science', 'sea level', 'nivel do mar', 'nível do mar', 'antarctica', 'antarctic',
        'arctic sea ice', 'magnetosphere', 'geomagnetic', 'geodynamo', 'campo magnetico terrestre',
        'campo magnético terrestre', 'aurora boreal', 'aurora austral'
    ]),
    ('Biologia', [
        'biology', 'biologia', 'microbe', 'microbial', 'crispr', 'archaea', 'arqueia', 'parasite',
        'parasita', 'malaria', 'life sciences'
    ]),
    ('Química', [
        'chemistry', 'química', 'quimica', 'molecule', 'molecular', 'molecula', 'molécula',
        'spectroscopy', 'espectroscopia'
    ]),
    ('Astronomia', [
        'galaxy', 'galaxia', 'galáxia', 'nebula', 'nebulosa', 'milky way', 'via lactea',
        'via láctea', 'moon', 'lua', 'mars', 'marte', 'jupiter', 'saturn', 'comet', 'cometa',
        'asteroid', 'asteroide', 'rubin', 'telescope', 'telescopio', 'telescópio', 'artemis',
        'jwst', 'webb', 'hubble', 'xrism', 'observatory', 'observatorio', 'observatório'
    ]),
]

TOPIC_IMAGE_RULES = [
    (r'(artemis|shackleton|polo sul lunar|lunar|\blua\b|\bmoon\b|eclipse lunar)', ['lunarSouthPole', 'moon']),
    (r'(perseverance|jezero|marte|\bmars\b|ingenuity|mars sample return)', ['jezero', 'perseverance', 'mars']),
    (r'(jupiter|jovian|grande mancha vermelha)', ['jupiter']),
    (r'\beuropa\b', ['europa', 'jupiter']),
    (r'(saturno|\bsaturn\b|cassini|aneis de saturno|anéis de saturno)', ['saturn', 'cassini']),
    (r'(\bsol\b|solar|sunspot|mancha solar|flare|erupcao solar|erupção solar|coronal|cme|tempestade geomagnetica|tempestade geomagnética)', ['solar', 'sunspot', 'aurora']),
    (r'(buraco negro|black hole|event horizon|sgr a\*|sgr a|m87|quasar|horizonte de eventos)', ['blackhole', 'm87jet']),
    (r'(estrela[s]? de neutrons|estrela[s]? de nêutrons|neutron star|kilonova|ligo|virgo|onda gravitacional|gravitational wave|\bgw\d+)', ['kilonova', 'neutronStar']),
    (r'(pulsar|magnetar)', ['neutronStar']),
    (r'(supernova)', ['supernova', 'crab']),
    (r'(cometa|\bcomet\b)', ['comet']),
    (r'(asteroide|asteroid|cinturao de kuiper|cinturão de kuiper|kuiper|planeta anao|planeta anão|minor planet|objeto transnetuniano)', ['asteroid', 'rubin']),
    (r'(vera rubin|\brubin\b|lsst)', ['rubin']),
    (r'(exoplaneta|exoplanet|trappist|k2-18|proxima centauri b|super-terra|super earth|sub-netuno|sub-neptune|zona habitavel|zona habitável|biossinal|biosignature|hycean)', ['exoplanetTransit', 'exoplanetOcean']),
    (r'(oceano|ocean|agua liquida|água líquida|mundo oceanico|mundo oceânico)', ['exoplanetOcean', 'exoplanetTransit']),
    (r'(nebulosa|nebula|carina|orion|helix|veil|omega|lagoon|trifid|eagle|crab nebula|butterfly nebula)', ['carina', 'orion', 'helix', 'veil', 'lagoon', 'triffid', 'omega', 'butterfly', 'crab']),
    (r'(galaxia|galáxia|galaxy|andromeda|via lactea|via láctea|milky way|halo galactico|halo galáctico|aglomerado de galaxias|aglomerado de galáxias|spiral galaxy|galaxias anas|galáxias anãs)', ['andromeda', 'triangulum', 'whirlpool', 'sombrero', 'ngc1300', 'milkyway']),
    (r'(cosmologia|universo primitivo|universo jovem|energia escura|materia escura|matéria escura|cmb|fundo cosmico|fundo cósmico|hubble tension|euclid|jwst|webb|deep field|campo profundo)', ['hubbledeep', 'andromeda', 'ngc1300', 'milkyway']),
    (r'(lhc|cern|higgs|quark|muon|múon|muonico|muônico|particula|partícula|detector|cms|atlas|fisica de particulas|física de partículas)', ['particleTracks', 'cern']),
    (r'(clima|climate|aquecimento global|mudanca climatica|mudança climática|earth science|artico|ártico|antartica|antártica|greenland|sea level|nivel do mar|nível do mar|geodynamo|geomagnet|magnetosfera da terra|campo magnetico terrestre|campo magnético terrestre|aurora boreal|aurora austral|planeta terra)', ['magneticField', 'climate', 'earth', 'aurora']),
]

CATEGORY_IMAGE_FALLBACKS = {
    'Astronomia': ['milkyway', 'andromeda', 'comet', 'orion'],
    'Cosmologia': ['hubbledeep', 'andromeda', 'ngc1300'],
    'Astrofísica': ['blackhole', 'neutronStar', 'supernova', 'm87jet'],
    'Exoplanetas': ['exoplanetTransit', 'exoplanetOcean'],
    'Física': ['particleTracks', 'cern', 'solar'],
    'Biologia': ['europa', 'exoplanetOcean', 'carina'],
    'Química': ['omega', 'orion', 'hubbledeep'],
    'Ciências da Terra': ['magneticField', 'climate', 'earth', 'aurora'],
}

BAD_IMAGE_HINTS = (
    'logo', 'avatar', 'icon', 'sprite', 'placeholder', 'blank', 'spacer',
    'favicon', 'apple-touch-icon', 'site-logo', 'siteicon', 'social-default-image'
)

ARTICLE_IMAGE_CACHE: dict[str, Optional[str]] = {}
PAGE_IMAGE_FETCH_COUNT = 0
TRANSLATION_CACHE: dict[tuple[str, str], str] = {}


def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
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
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].strip()
    return cut + '…'


def normalize_text(text: str) -> str:
    low = (text or '').lower()
    return (
        low.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
        .replace('é', 'e').replace('ê', 'e')
        .replace('í', 'i')
        .replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
        .replace('ú', 'u').replace('ç', 'c')
    )


def stable_index(seed: str, size: int) -> int:
    if size <= 1:
        return 0
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return int(digest[:12], 16) % size


def unique_keep_order(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
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


def classify_category(text: str, source_name: str) -> str:
    low = normalize_text(f'{source_name} {text}')
    for cat, keywords in CATEGORY_RULES:
        if any(normalize_text(keyword) in low for keyword in keywords):
            return cat
    if 'arxiv' in normalize_text(source_name):
        return 'Física'
    return 'Astronomia'


def cat_cls(cat: str) -> str:
    low = normalize_text(cat).replace(' ', '-')
    return 'terra' if low == 'ciencias-da-terra' else low


def reading_time(text: str) -> str:
    words = max(1, len((text or '').split()))
    mins = max(2, round(words / 180))
    return f'{mins} min de leitura'


def format_date_pt(dt: datetime) -> str:
    return f'{dt.day:02d} {MESES_PT[dt.month]} {dt.year}'


def format_date_en(dt: datetime) -> str:
    return dt.strftime('%d %b %Y')


def translate_text(text: str, target_lang: str) -> str:
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    if not text:
        return ''
    cache_key = (target_lang, text)
    cached = TRANSLATION_CACHE.get(cache_key)
    if cached is not None:
        return cached

    params = urllib.parse.urlencode({
        'client': 'gtx',
        'sl': 'auto',
        'tl': target_lang,
        'dt': 't',
        'q': text,
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


def reading_time_en(text: str) -> str:
    words = max(1, len((text or '').split()))
    mins = max(2, round(words / 180))
    return f'{mins} min read'


EDITORIAL_SKIP_HINTS = (
    'image credit', 'photo credit', 'credit:', 'read more', 'continue reading',
    'copyright', 'all rights reserved', 'source:', 'original source:'
)


def collapse_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '')).strip()


def clip_text_nicely(text: str, max_chars: int = 1200) -> str:
    text = collapse_ws(strip_html(text))
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].strip()
    parts = re.split(r'(?<=[.!?])\s+', clipped)
    if len(parts) > 1:
        candidate = ' '.join(parts[:-1]).strip()
        if len(candidate) >= max_chars * 0.55:
            return candidate
    return clipped.rsplit(' ', 1)[0].strip()


def split_sentences(text: str) -> list[str]:
    text = collapse_ws(strip_html(text))
    if not text:
        return []
    text = re.sub(r'\s*([;:])\s*', '. ', text)
    raw = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for item in raw:
        item = collapse_ws(item).strip(" \"'“”‘’")
        if not item:
            continue
        out.append(item)
    return out


def sentence_key(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', normalize_text(text))


def select_fact_sentences(title: str, summary: str, source_text: str, max_sentences: int = 4) -> list[str]:
    pool = []
    for block in (summary, source_text):
        pool.extend(split_sentences(block))

    title_key = sentence_key(title)
    seen = set()
    chosen = []
    for sentence in pool:
        sent = collapse_ws(sentence)
        if not sent:
            continue
        low = normalize_text(sent)
        if any(hint in low for hint in EDITORIAL_SKIP_HINTS):
            continue
        if len(sent) < 35 and not re.search(r'\d', sent):
            continue
        if len(sent) > 320:
            continue
        key = sentence_key(sent)
        if not key or key in seen or key == title_key:
            continue
        seen.add(key)
        chosen.append(sent)
        if len(chosen) >= max_sentences:
            break
    return chosen


def editorial_headings(lang: str = 'pt') -> tuple[str, str]:
    if lang == 'en':
        return ('What the story actually shows', 'What to watch next')
    return ('O que a notícia realmente mostra', 'O que observar agora')


def category_context(category: str, lang: str = 'pt') -> str:
    pt = {
        'Astronomia': 'Em astronomia, um resultado relevante quase nunca vale apenas pela manchete. O que importa é como ele melhora a reconstrução física do sistema observado, restringe modelos e acrescenta contexto para futuras medições.',
        'Cosmologia': 'Em cosmologia, cada conjunto de dados novo pesa porque toca questões de escala máxima: expansão do universo, distribuição de matéria e consistência do modelo cosmológico padrão.',
        'Astrofísica': 'Na astrofísica, a relevância de um anúncio depende do quanto ele aproxima observação e mecanismo físico. O objetivo não é colecionar exotismos cósmicos, mas entender processos extremos com medidas mais robustas.',
        'Exoplanetas': 'Em exoplanetas, a pergunta correta nunca é apenas se o mundo descoberto parece interessante. O ponto central é o que os dados realmente permitem afirmar sobre massa, atmosfera, temperatura, composição e possível habitabilidade.',
        'Física': 'Em física, manchetes impressionantes só sobrevivem ao tempo quando vêm acompanhadas de método sólido, estatística convincente e compatibilidade cuidadosa com o arcabouço teórico existente.',
        'Biologia': 'Em biologia, a diferença entre indício e demonstração é tudo. Resultados promissores precisam ser lidos à luz do desenho experimental, da reprodutibilidade e das limitações do modelo estudado.',
        'Química': 'Em química, avanços importantes costumam estar menos no anúncio em si do que na qualidade da evidência espectroscópica, estrutural ou cinética que sustenta a interpretação.',
        'Ciências da Terra': 'Nas ciências da Terra, a relevância de um resultado está em conectar observações locais a processos planetários mais amplos, com atenção especial a séries temporais, causalidade e incertezas instrumentais.',
    }
    en = {
        'Astronomia': 'In astronomy, a result matters for more than the headline. What counts is whether it sharpens the physical reconstruction of the observed system, constrains models and adds context for future measurements.',
        'Cosmologia': 'In cosmology, every new dataset matters because it touches the largest-scale questions: cosmic expansion, the distribution of matter and the consistency of the standard cosmological model.',
        'Astrofísica': 'In astrophysics, the value of an announcement depends on how well it links observation to physical mechanism. The goal is not to collect exotic objects, but to understand extreme processes with firmer measurements.',
        'Exoplanetas': 'In exoplanet science, the right question is never just whether a newly reported world sounds exciting. What matters is what the data really support about mass, atmosphere, temperature, composition and possible habitability.',
        'Física': 'In physics, striking headlines only age well when they come with solid method, convincing statistics and careful consistency with the existing theoretical framework.',
        'Biologia': 'In biology, the line between a hint and a demonstration is everything. Promising results have to be read in light of experimental design, reproducibility and the limitations of the model under study.',
        'Química': 'In chemistry, major advances often lie less in the announcement itself than in the quality of the spectroscopic, structural or kinetic evidence behind the interpretation.',
        'Ciências da Terra': 'In Earth science, the importance of a result lies in connecting local observations to broader planetary processes, with special attention to time series, causality and instrumental uncertainty.',
    }
    mapping = en if lang == 'en' else pt
    return mapping.get(category, mapping['Astronomia'])


def build_detail_paragraph(facts: list[str], source_name: str, lang: str = 'pt') -> str:
    details = ' '.join(facts[:2]).strip()
    if lang == 'en':
        if details:
            return (
                f'From the source material credited to {source_name}, the most useful details are these: '
                f'{details} Read without publicity varnish, that is the part that helps separate what was directly observed, '
                f'measured or calculated from what is still interpretation.'
            )
        return (
            f'The source material attributed to {source_name} still needs to be read with the usual scientific discipline: '
            f'what was measured, how it was measured, and how much uncertainty still surrounds the claim.'
        )
    if details:
        return (
            f'No material usado como base para esta reportagem, os detalhes mais úteis são estes: '
            f'{details} Lido sem verniz publicitário, é isso que ajuda a separar o que foi de fato observado, '
            f'medido ou calculado do que ainda permanece como interpretação.'
        )
    return (
        f'O material atribuído a {source_name} ainda precisa ser lido com a disciplina científica básica: '
        f'o que exatamente foi medido, como foi medido e quanta incerteza ainda cerca a afirmação.'
    )


def build_caution_paragraph(source_name: str, lang: str = 'pt') -> str:
    low = normalize_text(source_name)
    if lang == 'en':
        if 'arxiv' in low:
            return 'Because the source includes arXiv, the standard caution applies: a preprint can be valuable and timely, but it does not replace peer review or later independent replication.'
        if any(tag in low for tag in ('nasa', 'esa', 'jpl', 'observatory', 'consortium')):
            return 'Institutional releases are useful starting points, but they naturally foreground the headline result. Mature science reporting has to preserve room for caveats, uncertainty ranges and competing interpretations.'
        return 'As with any science story, the decisive question is not only what was claimed, but what level of evidence, method and uncertainty actually supports the claim.'
    if 'arxiv' in low:
        return 'Como a origem inclui o arXiv, vale a ressalva padrão: preprint pode ser útil e rápido, mas não substitui revisão por pares nem confirmação independente posterior.'
    if any(tag in low for tag in ('nasa', 'esa', 'jpl', 'observatory', 'consortium')):
        return 'Comunicados institucionais são ótimos pontos de partida, mas naturalmente enfatizam o achado principal. Jornalismo científico maduro precisa preservar espaço para ressalvas, margens de incerteza e interpretações concorrentes.'
    return 'Como em qualquer notícia científica, a pergunta decisiva não é apenas o que foi afirmado, mas qual nível de evidência, método e incerteza realmente sustenta a afirmação.'


def build_next_steps_paragraph(category: str, source_name: str, lang: str = 'pt') -> str:
    pt = {
        'Astronomia': 'O próximo passo relevante costuma ser combinar esse resultado com novas observações, idealmente em outros comprimentos de onda, para verificar se o quadro permanece consistente.',
        'Cosmologia': 'O teste decisivo virá da comparação com amostras maiores, calibrações independentes e análises que consigam reduzir vieses sistemáticos sem maquiar a estatística.',
        'Astrofísica': 'Agora, o que mais importa é ver se observações adicionais, simulações e análises independentes convergem para a mesma interpretação física.',
        'Exoplanetas': 'Daqui para frente, o que conta é obter medições independentes de atmosfera, massa, raio, temperatura e composição, porque é aí que especulação cede lugar a caracterização séria.',
        'Física': 'Em física, o filtro verdadeiro é sempre o mesmo: mais dados, mais controle de sistemáticos e uma análise capaz de sobreviver ao escrutínio de outros grupos.',
        'Biologia': 'Em biologia, a etapa seguinte é testar robustez, mecanismo e reprodutibilidade em modelos e condições adicionais antes de qualquer extrapolação ousada.',
        'Química': 'Em química, o avanço se consolida quando outras técnicas e outros grupos confirmam a mesma leitura estrutural ou mecanística.',
        'Ciências da Terra': 'Nas ciências da Terra, a confirmação mais forte vem quando a observação se encaixa em séries mais longas e em diferentes conjuntos instrumentais.'
    }
    en = {
        'Astronomia': 'The next meaningful step is usually to combine this result with new observations, ideally at other wavelengths, to test whether the picture remains consistent.',
        'Cosmologia': 'The decisive test will come from larger samples, independent calibrations and analyses that reduce systematics without massaging the statistics.',
        'Astrofísica': 'What matters next is whether additional observations, simulations and independent analyses converge on the same physical interpretation.',
        'Exoplanetas': 'From here on, what counts is independent atmospheric, mass, radius, temperature and composition measurements, because that is where speculation gives way to serious characterization.',
        'Física': 'In physics, the real filter is always the same: more data, tighter control of systematics and an analysis that survives scrutiny from other groups.',
        'Biologia': 'In biology, the next step is to test robustness, mechanism and reproducibility in additional models and conditions before any bold extrapolation.',
        'Química': 'In chemistry, a result becomes durable when other techniques and other groups confirm the same structural or mechanistic reading.',
        'Ciências da Terra': 'In Earth science, the strongest confirmation comes when an observation fits into longer time series and across different instrumental datasets.'
    }
    lead_pt = pt.get(category, pt['Astronomia'])
    lead_en = en.get(category, en['Astronomia'])
    if lang == 'en':
        return f'{lead_en} That is the standard needed before a finding associated with {source_name} deserves to be treated as settled rather than merely exciting.'
    return f'{lead_pt} Esse é o padrão exigido antes que um resultado associado a {source_name} mereça ser tratado como consolidado e não apenas como empolgante.'


def editorial_pullquote(lang: str = 'pt') -> str:
    if lang == 'en':
        return 'In science reporting, the useful part is not the excitement. It is the evidence that remains standing after the excitement has passed.'
    return 'Em divulgação científica, a parte útil não é o entusiasmo. É a evidência que continua de pé depois que o entusiasmo passa.'


def make_body(title: str, summary: str, source_text: str, source_name: str, category: str, lang: str = 'pt') -> str:
    title = collapse_ws(strip_html(title))
    summary = collapse_ws(strip_html(summary))
    source_text = clip_text_nicely(source_text or summary, 1200)
    facts = select_fact_sentences(title, summary, source_text, max_sentences=4)

    intro = summary or (facts[0] if facts else title)
    if facts and sentence_key(intro) == sentence_key(facts[0]):
        detail_facts = facts[1:3]
    else:
        detail_facts = facts[:2]

    head1, head2 = editorial_headings(lang)
    parts = []

    if intro:
        parts.append(f'<p>{html.escape(intro)}</p>')

    parts.append(f'<p>{html.escape(category_context(category, lang))}</p>')
    parts.append(f'<h2>{html.escape(head1)}</h2>')
    parts.append(f'<p>{html.escape(build_detail_paragraph(detail_facts, source_name, lang))}</p>')
    parts.append(f'<p>{html.escape(build_caution_paragraph(source_name, lang))}</p>')
    parts.append(f'<blockquote>{html.escape(editorial_pullquote(lang))}</blockquote>')
    parts.append(f'<h2>{html.escape(head2)}</h2>')
    parts.append(f'<p>{html.escape(build_next_steps_paragraph(category, source_name, lang))}</p>')

    return ''.join(parts)

def clean_image_url(url: str) -> Optional[str]:
    if not url:
        return None
    url = html.unescape(url).strip()
    if not url:
        return None
    if url.startswith('//'):
        url = 'https:' + url
    if not re.match(r'^https?://', url, flags=re.I):
        return None
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return None
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return None
    return url


def image_url_looks_good(url: str) -> bool:
    low = normalize_text(url)
    if not re.search(r'\.(jpg|jpeg|png|webp)(?:$|[?#])', low):
        if 'image' not in low and 'photo' not in low and 'media' not in low:
            return False
    if any(bad in low for bad in BAD_IMAGE_HINTS):
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
    if src and image_url_looks_good(src):
        return src
    return None


def extract_rss_image(item: ET.Element, link: str, description_html: str) -> Optional[str]:
    candidates = []

    for tag in ('enclosure', '{http://search.yahoo.com/mrss/}content', '{http://search.yahoo.com/mrss/}thumbnail'):
        for el in item.findall(tag):
            url = clean_image_url(el.get('url', ''))
            if url:
                candidates.append(url)

    for tag in ('{http://search.yahoo.com/mrss/}group',):
        for group in item.findall(tag):
            for child_tag in ('{http://search.yahoo.com/mrss/}content', '{http://search.yahoo.com/mrss/}thumbnail'):
                for el in group.findall(child_tag):
                    url = clean_image_url(el.get('url', ''))
                    if url:
                        candidates.append(url)

    for tag_name in ('description', '{http://purl.org/rss/1.0/modules/content/}encoded'):
        raw_html = item.findtext(tag_name, default='') or ''
        url = find_first_image_in_html(raw_html, link)
        if url:
            candidates.append(url)

    desc_img = find_first_image_in_html(description_html, link)
    if desc_img:
        candidates.append(desc_img)

    for url in unique_keep_order(candidates):
        if image_url_looks_good(url):
            return url
    return None


def extract_atom_image(entry: ET.Element, link: str, summary_html: str) -> Optional[str]:
    candidates = []

    for link_el in entry.findall('atom:link', NS):
        rel = (link_el.get('rel') or 'alternate').strip().lower()
        href = clean_image_url(link_el.get('href', ''))
        media_type = (link_el.get('type') or '').lower()
        if href and (rel == 'enclosure' or media_type.startswith('image/')):
            candidates.append(href)

    for media_tag in ('media:content', 'media:thumbnail'):
        for el in entry.findall(media_tag, NS):
            url = clean_image_url(el.get('url', ''))
            if url:
                candidates.append(url)

    for field in ('atom:summary', 'atom:content'):
        html_field = entry.findtext(field, default='', namespaces=NS) or ''
        url = find_first_image_in_html(html_field, link)
        if url:
            candidates.append(url)

    summary_img = find_first_image_in_html(summary_html, link)
    if summary_img:
        candidates.append(summary_img)

    for url in unique_keep_order(candidates):
        if image_url_looks_good(url):
            return url
    return None


def fetch_page_image(article_url: str) -> Optional[str]:
    global PAGE_IMAGE_FETCH_COUNT
    if not article_url:
        return None
    if article_url in ARTICLE_IMAGE_CACHE:
        return ARTICLE_IMAGE_CACHE[article_url]
    if PAGE_IMAGE_FETCH_COUNT >= MAX_PAGE_IMAGE_FETCHES:
        ARTICLE_IMAGE_CACHE[article_url] = None
        return None

    PAGE_IMAGE_FETCH_COUNT += 1
    try:
        req = urllib.request.Request(article_url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=PAGE_IMAGE_TIMEOUT) as resp:
            raw = resp.read(700_000)
        text = raw.decode('utf-8', errors='ignore')
    except Exception:
        ARTICLE_IMAGE_CACHE[article_url] = None
        return None

    patterns = [
        r'<meta[^>]+property=["\']og:image(?:url)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            candidate = urllib.parse.urljoin(article_url, match.group(1).strip())
            candidate = clean_image_url(candidate)
            if candidate and image_url_looks_good(candidate):
                ARTICLE_IMAGE_CACHE[article_url] = candidate
                return candidate

    inline = find_first_image_in_html(text, article_url)
    ARTICLE_IMAGE_CACHE[article_url] = inline
    return inline


def infer_thematic_image(title: str, summary: str, source_name: str, category: str) -> str:
    text = normalize_text(' '.join([title or '', summary or '', source_name or '', category or '']))
    candidates: list[str] = []

    for pattern, keys in TOPIC_IMAGE_RULES:
        if re.search(pattern, text, flags=re.I):
            candidates.extend(IMG[key] for key in keys if key in IMG)

    if not candidates:
        candidates.extend(IMG[key] for key in CATEGORY_IMAGE_FALLBACKS.get(category, ['pillars', 'carina', 'andromeda']) if key in IMG)

    unique = unique_keep_order(candidates)
    if not unique:
        unique = [IMG['pillars'], IMG['carina'], IMG['andromeda']]

    seed = f'{title}|{source_name}|{category}'
    return unique[stable_index(seed, len(unique))]



def parse_rss(xml_bytes: bytes, source_name: str):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall('.//item'):
        title = strip_html(item.findtext('title', default=''))
        link = (item.findtext('link', default='') or '').strip()
        description_html = item.findtext('description', default='') or ''
        content_html = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', default='') or description_html
        desc = strip_html(description_html)
        full_text = clip_text_nicely(content_html or description_html, 1200)
        pub = item.findtext('pubDate', default='') or item.findtext('{http://purl.org/dc/elements/1.1/}date', default='')
        if not title or not link:
            continue
        dt = parse_date(pub)
        feed_img = extract_rss_image(item, link, description_html)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(desc or full_text, 320),
            'full_text': full_text or desc,
            'published': dt,
            'source': source_name,
            'feed_img': feed_img,
        })
    return items


def parse_atom(xml_bytes: bytes, source_name: str):
    root = ET.fromstring(xml_bytes)
    items = []
    for entry in root.findall('atom:entry', NS):
        title = strip_html(entry.findtext('atom:title', default='', namespaces=NS))
        summary_html = entry.findtext('atom:summary', default='', namespaces=NS) or ''
        content_html = entry.findtext('atom:content', default='', namespaces=NS) or summary_html
        summary = strip_html(summary_html or content_html)
        full_text = clip_text_nicely(content_html or summary_html, 1200)
        published = entry.findtext('atom:published', default='', namespaces=NS) or entry.findtext('atom:updated', default='', namespaces=NS)
        link = ''
        for link_el in entry.findall('atom:link', NS):
            href = link_el.get('href', '').strip()
            rel = link_el.get('rel', 'alternate')
            if href and rel == 'alternate':
                link = href
                break
        if not title or not link:
            continue
        dt = parse_date(published)
        feed_img = extract_atom_image(entry, link, summary_html or content_html)
        items.append({
            'title': title,
            'link': link,
            'summary': truncate(summary or full_text, 320),
            'full_text': full_text or summary,
            'published': dt,
            'source': source_name,
            'feed_img': feed_img,
        })
    return items


def load_all_items():
    all_items = []
    for src in SOURCES:
        try:
            raw = fetch(src['url'])
            if src['kind'] == 'atom':
                items = parse_atom(raw, src['name'])
            else:
                items = parse_rss(raw, src['name'])
            all_items.extend(items)
            print(f'OK  {src["name"]}: {len(items)} itens')
        except Exception as exc:
            print(f'ERR {src["name"]}: {exc}')
    return all_items


def dedupe_and_rank(items):
    seen = set()
    cleaned = []
    for item in sorted(items, key=lambda x: x['published'], reverse=True):
        key = re.sub(r'\W+', '', normalize_text(item['title']))
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    return cleaned[:MAX_POSTS]


def choose_post_image(item: dict, category: str) -> str:
    feed_img = clean_image_url(item.get('feed_img') or '')
    if feed_img and image_url_looks_good(feed_img):
        return feed_img

    if 'arxiv' not in normalize_text(item.get('source', '')):
        page_img = fetch_page_image(item.get('link', ''))
        if page_img and image_url_looks_good(page_img):
            return page_img

    return infer_thematic_image(item.get('title', ''), item.get('summary', ''), item.get('source', ''), category)


def to_post(item, idx: int):
    category = classify_category(item['title'] + ' ' + item['summary'], item['source'])
    dt = item['published']
    featured = idx < 3
    trending = idx < 8
    img = choose_post_image(item, category)

    title_en = item['title']
    summary_en = item['summary']
    source_text_en = clip_text_nicely(item.get('full_text') or summary_en, 1200)

    title_pt = translate_text(title_en, 'pt')
    summary_pt = translate_text(summary_en, 'pt')
    source_text_pt = translate_text(source_text_en, 'pt')

    body_pt = make_body(title_pt, summary_pt, source_text_pt, item['source'], category, 'pt')
    body_en = make_body(title_en, summary_en, source_text_en, item['source'], category, 'en')

    excerpt_pt = truncate(summary_pt or strip_html(body_pt), 220)
    excerpt_en = truncate(summary_en or strip_html(body_en), 220)
    sub_pt = truncate(summary_pt or excerpt_pt, 140)
    sub_en = truncate(summary_en or excerpt_en, 140)

    return {
        'id': idx + 1,
        'cat': category,
        'catCls': cat_cls(category),
        'img': img,

        'title': title_pt,
        'title_pt': title_pt,
        'title_en': title_en,

        'sub': sub_pt,
        'sub_pt': sub_pt,
        'sub_en': sub_en,

        'excerpt': excerpt_pt,
        'excerpt_pt': excerpt_pt,
        'excerpt_en': excerpt_en,

        'body': body_pt,
        'body_pt': body_pt,
        'body_en': body_en,

        'date': format_date_pt(dt),
        'date_pt': format_date_pt(dt),
        'date_en': format_date_en(dt),

        'time': dt.strftime('%Hh%M'),
        'time_pt': dt.strftime('%Hh%M'),
        'time_en': dt.strftime('%H:%M UTC'),

        'read': reading_time(strip_html(body_pt)),
        'read_pt': reading_time(strip_html(body_pt)),
        'read_en': reading_time_en(strip_html(body_en)),

        'publishedIso': dt.isoformat(),
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
    posts = [to_post(item, idx) for idx, item in enumerate(ranked)]
    save_posts(posts)
    print(f'{len(posts)} posts salvos em {datetime.now(timezone.utc).isoformat()}')
    if ARTICLE_IMAGE_CACHE:
        print(f'Imagens de páginas consultadas: {sum(1 for v in ARTICLE_IMAGE_CACHE.values() if v)} válidas / {len(ARTICLE_IMAGE_CACHE)} tentativas')


if __name__ == '__main__':
    main()
