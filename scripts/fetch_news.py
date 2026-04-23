"""
Cosmos Week news aggregator and static site generator.

This script fetches scientific news from a curated list of RSS and Atom
feeds, translates and summarizes content, assigns editorial metadata,
and produces JSON/JS feed files alongside RSS, sitemap and robots.txt.

The core workflow is:
  1. Collect and parse items from feeds while respecting per-source limits.
  2. Normalize and enrich items with editorial scores and categories.
  3. Build bilingual titles, summaries, facts, highlights and bodies.
  4. Optionally revise Portuguese content via the Gemini API.
  5. Export posts to JSON/JavaScript as well as RSS and sitemap files.

Functionality can be customized via environment variables and workflow
configuration without modifying this module. The script is designed to
run unattended from a GitHub Actions workflow on a regular schedule.
"""

import hashlib
import html
import json
import os
import re
import shutil
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
ARCHIVE_POSTS_JSON = ROOT / 'all_posts.json'
PREVIEW_DIR = ROOT / 'noticia'
PREVIEW_EN_DIR = ROOT / 'en' / 'news'

SITE_URL = os.getenv('COSMOS_SITE_URL', 'https://www.cosmosweek.com/').rstrip('/') + '/'
SITE_NAME = 'Cosmos Week'
SITE_DESCRIPTION_PT = 'Portal de jornalismo científico com foco em astronomia, astrofísica, cosmologia e ciência de fronteira.'
SITE_DESCRIPTION_EN = 'Science journalism portal focused on astronomy, astrophysics, cosmology and frontier research.'

MAX_POSTS = 40
MAX_POSTS_PER_SOURCE = 5
MAX_PREPRINTS = 14
MIN_POSTS_PER_CATEGORY = 3
MIN_FRESH_POSTS = 10
FRESH_WINDOW_HOURS = 120
MAX_POST_AGE_DAYS = 45          # posts mais velhos que isso são descartados como noise
USER_AGENT = 'CosmosWeekBot/5.0 (+https://github.com/marambaiajunior/cosmos-week)'
REQUEST_TIMEOUT = 30
ARXIV_TIMEOUT = 60              # arXiv API pode ser lenta; timeout separado e maior
ARXIV_RETRIES = 2               # tentativas extras para feeds arXiv antes de desistir
PAGE_TIMEOUT = 20
TRANSLATE_TIMEOUT = 22
TRANSLATE_ENDPOINT = 'https://translate.googleapis.com/translate_a/single'
MAX_PAGE_FETCHES = 90              # 40 posts × 1 fetch único + 50 de margem para edge cases
PAGE_TEXT_MAX_PARAGRAPHS = 24
FULL_TEXT_LIMIT = 9000
MAX_FACT_SENTENCES = 14
MAX_INLINE_IMAGES = 12
GEMINI_TIMEOUT = max(20, int((os.getenv('GEMINI_TIMEOUT', '45') or '45').strip() or '45'))
# Reduce Gemini rate to minimise HTTP 429/503 errors. The free tier allows up to
# 20 requests per minute, but congestion can still make the service unavailable.
try:
    GEMINI_RPM_LIMIT = max(1, int((os.getenv('GEMINI_RPM_LIMIT', '6') or '6').strip()))
except ValueError:
    GEMINI_RPM_LIMIT = 6
try:
    GEMINI_RETRY_ON_429 = max(0, int((os.getenv('GEMINI_RETRY_ON_429', '1') or '1').strip()))
except ValueError:
    GEMINI_RETRY_ON_429 = 1
try:
    GEMINI_RETRY_DELAY_429 = max(15, int((os.getenv('GEMINI_RETRY_DELAY_429', '20') or '20').strip()))
except ValueError:
    GEMINI_RETRY_DELAY_429 = 20
try:
    GEMINI_RETRY_TRANSIENT = max(0, int((os.getenv('GEMINI_RETRY_TRANSIENT', '0') or '0').strip()))
except ValueError:
    GEMINI_RETRY_TRANSIENT = 0
try:
    GEMINI_RETRY_BASE_DELAY = max(5, int((os.getenv('GEMINI_RETRY_BASE_DELAY', '8') or '8').strip()))
except ValueError:
    GEMINI_RETRY_BASE_DELAY = 8
GEMINI_PAYLOAD_BODY_LIMIT = 2200
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash').strip() or 'gemini-2.0-flash'
GEMINI_MODEL_FALLBACKS = [m.strip() for m in (os.getenv('GEMINI_MODEL_FALLBACKS', '') or '').split(',') if m.strip()]
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
GEMINI_ENDPOINT_TEMPLATE = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
try:
    GEMINI_BATCH_SIZE = max(1, int((os.getenv('GEMINI_BATCH_SIZE', '1') or '1').strip()))
except ValueError:
    GEMINI_BATCH_SIZE = 1
try:
    GEMINI_DISABLE_AFTER_CONSECUTIVE_503 = max(1, int((os.getenv('GEMINI_DISABLE_AFTER_CONSECUTIVE_503', '3') or '3').strip()))
except ValueError:
    GEMINI_DISABLE_AFTER_CONSECUTIVE_503 = 3
try:
    GEMINI_PROBE_RETRIES = max(0, int((os.getenv('GEMINI_PROBE_RETRIES', '1') or '1').strip()))
except ValueError:
    GEMINI_PROBE_RETRIES = 1
GEMINI_PROBE_ENABLED = (os.getenv('GEMINI_PROBE_ENABLED', '1') or '1').strip().lower() not in {'0', 'false', 'no'}
GEMINI_REVIEW_PRIORITY_FIRST = (os.getenv('GEMINI_REVIEW_PRIORITY_FIRST', '1') or '1').strip().lower() not in {'0', 'false', 'no'}
try:
    GEMINI_MAX_REVIEW_SECONDS = max(60, int((os.getenv('GEMINI_MAX_REVIEW_SECONDS', '900') or '900').strip()))
except ValueError:
    GEMINI_MAX_REVIEW_SECONDS = 900
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
    'solar': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/1280px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'jwst': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Webb_Space_Telescope_faint_red_galaxy.jpg/1280px-Webb_Space_Telescope_faint_red_galaxy.jpg',
    'dna': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/DNA_orbit_animated_static_thumb.png/1280px-DNA_orbit_animated_static_thumb.png',
    'cell': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Fluorescent_cells.jpg/1280px-Fluorescent_cells.jpg',
    'molecule': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/HAtomOrbitals.png/1280px-HAtomOrbitals.png',
    'ocean': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24701-nature-natural-beauty.jpg/1280px-24701-nature-natural-beauty.jpg',
}

BAD_TITLE_PATTERNS = [
    r'^week in images', r'^watch live', r'^image:', r'^video:', r'^earth from space', r'^i am artemis',
    r'awards categories', r'crew.?s suits', r'view of', r'views mount', r'photo of',
    r'^listen to this audio excerpt', r'^how europe will', r'^nextstep', r'^where spiral arms',
    r'^earth from ', r'^getting to the core of a medicane', r'^\d+ things', r'^quiz:',
    r'^letter from', r'^editorial:', r'^job:', r'^obituary:', r'^correction:',
    r'^this week.?s sky at a glance', r'^sky at a glance', r'^how to follow\b',
    r'^how to watch\b', r'^nasa invites media\b', r'^media advisory\b',
    r'^\d{4} .* schedule\b', r'\bat a glance\b',
]
BAD_URL_PARTS = [
    '/image-article/', '/images/', '/videos/', '/video/', '/week_in_images/',
    '/photojournal/', '/multimedia/', '/gallery/', '/podcast/', '/live/',
    '/author/', '/authors/', '/people/', '/person/', '/profile/', '/profiles/',
    '/staff/', '/team/', '/contributors/', '/contributor/',
]
BAD_TEXT_HINTS = [
    'listen to this audio excerpt', 'discover our week through the lens', 'category i:',
    'copyright', 'image credit', 'video:', 'image:', 'week in images',
    'earth from space:', 'artist impression', 'all rights reserved',
]
PROMO_HINTS = [
    'award', 'awards', 'profile', 'audio excerpt', 'watch live', 'week in images', 'gallery',
    'contract opportunity', 'broad agency announcement', 'synopsis', 'procurement',
    'solicitation', 'podcast', 'career', 'jobs', 'livestream', 'event coverage',
    'photo essay', 'webcast', 'subscribe', 'newsletter', 'sign up', 'media advisory',
    'invites media', 'media are invited', 'at a glance', 'schedule', 'agenda', 'program',
]
SCIENTIFIC_RESULT_HINTS = [
    'detect', 'detected', 'discovery', 'discover', 'measurement', 'measured', 'results',
    'study', 'paper', 'observations', 'first images', 'first light', 'finds', 'reveals',
    'evidence', 'analysis', 'mission', 'launches', 'data', 'maps', 'constraints',
    'spectrum', 'spectra', 'atmosphere', 'galaxy', 'exoplanet', 'black hole',
    'dark matter', 'dark energy', 'star', 'nebula', 'gravitational wave', 'telescope',
    'survey', 'signal', 'candidate', 'sample return', 'biosignature', 'habitability',
    'interstellar', 'published', 'confirmed', 'breakthrough',
]
BROAD_INTEREST_PREPRINT_HINTS = [
    'dark matter', 'dark energy', 'exoplanet', 'black hole', 'james webb', 'jwst',
    'galaxy', 'cosmology', 'hubble tension', 'gravitational wave', 'supernova', 'mars',
    'moon', 'solar', 'neutron star', 'euclid', 'rubin', 'desi', 'cmb', 'planet',
    'universe', 'biosignature', 'habitability', 'climate', 'ocean', 'atmosphere',
]
TECHNICAL_JARGON_HINTS = [
    'hamiltonian', 'lagrangian', 'puiseux', 'hessenberg', 'all-solid-state',
    'metamodel', 'waveguides', 'crconi', 'adiabatic equations', 'teapot effect',
    'photoluminescence', 'scalar-tensor realization', 'steady-state wind flow transformer',
    'introductory physics', 'emulator-based', 'perturbative',
]
PUBLIC_INTEREST_HINTS = [
    'moon', 'mars', 'exoplanet', 'black hole', 'dark matter', 'dark energy',
    'galaxy', 'universe', 'earth', 'climate', 'magnetic field', 'gravitational wave',
    'life', 'biosignature', 'ocean', 'sample return', 'telescope', 'jwst',
    'hubble', 'euclid', 'rubin', 'nasa', 'esa', 'jpl', 'solar', 'sun', 'aurora',
]
HARD_RESEARCH_HINTS = [
    'published', 'journal', 'analysis', 'dataset', 'observations', 'spectroscopy',
    'transit', 'survey', 'map', 'constraints', 'letters', 'astrophysical journal',
    'nature', 'science', 'peer-reviewed', 'peer reviewed',
]

CATEGORY_RULES = [
    ('Exoplanetas', ['exoplanet', 'exoplaneta', 'biosignature', 'hycean', 'trappist', 'k2-18', 'habitable', 'sub-neptune', 'super-earth']),
    ('Cosmologia', ['cosmology', 'cosmologia', 'dark energy', 'energia escura', 'dark matter', 'matter power', 'cmb', 'hubble tension', 'inflation', 'large-scale structure', 'lss', 'desi', 'euclid survey']),
    ('Astrofísica', ['black hole', 'buraco negro', 'neutron star', 'nêutron', 'gravitational wave', 'kilonova', 'supernova', 'quasar', 'fast radio burst', 'frb', 'magnetar', 'pulsar', 'gamma-ray burst', 'grb', 'accretion']),
    ('Física', ['physics', 'física', 'quânt', 'quantum', 'cern', 'lhc', 'higgs', 'quark', 'muon', 'particle', 'plasma', 'photonic', 'perovskite', 'superconductor', 'materials', 'aps physics', 'condensed matter']),
    ('Ciências da Terra', ['earth', 'climate', 'sea level', 'atmospheric', 'atmosphere', 'weather', 'geodynamo', 'magnetic field', 'magnetosphere', 'earth science', 'river', 'ocean', 'environment', 'geophysics', 'noaa', 'glacier', 'arctic', 'ice sheet']),
    ('Biologia', ['biology', 'biologia', 'biomedical', 'microbe', 'life', 'crispr', 'archaea', 'hiv', 'genetic', 'genome', 'protein', 'cell', 'disease', 'nih', 'evolution', 'species', 'ecology', 'organism']),
    ('Química', ['chemistry', 'química', 'molecule', 'molecular', 'spectroscopy', 'ribose', 'chemical', 'catalyst', 'reaction', 'polymer', 'ice chemistry', 'synthesis', 'compound']),
    ('Astronomia', ['galaxy', 'galax', 'nebula', 'milky way', 'moon', 'mars', 'jupiter', 'saturn', 'comet', 'asteroid', 'telescope', 'artemis', 'jwst', 'webb', 'hubble', 'rubin', 'observatory', 'sky telescope', 'earthsky', 'planetary society', 'eso', 'alma', 'solar system']),
]

TOPIC_IMAGE_RULES = [
    (r'(artemis|shackleton|lunar south pole|polo sul lunar|\bmoon\b|\blua\b)', ['lunarSouthPole', 'moon']),
    (r'(perseverance|jezero|\bmars\b|marte|ingenuity)', ['jezero', 'mars']),
    (r'(jupiter|jovian)', ['jupiter']),
    (r'(saturn|saturno|cassini)', ['saturn']),
    (r'(solar|sunspot|flare|cme|aurora|geomagnetic|\bsun\b|\bsol\b)', ['solar', 'earth']),
    (r'(black hole|buraco negro|event horizon|m87|quasar)', ['blackhole', 'm87jet']),
    (r'(neutron star|estrela de neutrons|nêutrons|gravitational wave|onda gravitacional|kilonova|ligo|virgo)', ['kilonova', 'neutronStar']),
    (r'(supernova)', ['supernova']),
    (r'(comet|cometa)', ['comet']),
    (r'(asteroid|asteroide|kuiper|dwarf planet|planeta anão)', ['asteroid', 'rubin']),
    (r'(rubin|lsst)', ['rubin']),
    (r'(james webb|jwst|\bjwst\b)', ['jwst', 'pillars']),
    (r'(exoplanet|exoplaneta|hycean|biosignature|super-earth|super-terra|sub-neptune)', ['exoplanetTransit', 'exoplanetOcean']),
    (r'(ocean|oceano|water world)', ['exoplanetOcean', 'exoplanetTransit']),
    (r'(nebula|nebulosa|orion|helix|pillars)', ['orion', 'helix', 'pillars']),
    (r'(galaxy|galaxia|galáxia|andromeda|milky way|via láctea|spiral)', ['andromeda', 'milkyway']),
    (r'(cosmology|cosmologia|dark energy|dark matter|cmb|euclid|deep field|universo)', ['hubbledeep', 'andromeda']),
    (r'(lhc|cern|higgs|quark|muon|particle)', ['particleTracks', 'cern']),
    (r'(dna|genome|genetic|crispr|cell\b|protein)', ['dna', 'cell']),
    (r'(molecule|molecular|chemistry|catalyst|spectroscopy)', ['molecule', 'orion']),
    (r'(climate|sea level|glacier|arctic|ice sheet)', ['climate', 'earth']),
    (r'(earth|magnetosphere|magnetic field|atmosphere|ocean)', ['magneticField', 'climate', 'earth']),
]

CATEGORY_IMAGE_FALLBACKS = {
    'Astronomia': ['milkyway', 'andromeda', 'orion', 'comet', 'jwst'],
    'Cosmologia': ['hubbledeep', 'andromeda', 'jwst'],
    'Astrofísica': ['blackhole', 'neutronStar', 'supernova', 'kilonova'],
    'Exoplanetas': ['exoplanetTransit', 'exoplanetOcean'],
    'Física': ['particleTracks', 'cern', 'solar'],
    'Biologia': ['cell', 'dna', 'earth'],
    'Química': ['molecule', 'orion', 'hubbledeep'],
    'Ciências da Terra': ['magneticField', 'climate', 'earth', 'ocean'],
}

SOURCE_TYPE_LABELS = {
    'agency': {'pt': 'Fonte institucional', 'en': 'Institutional source'},
    'preprint': {'pt': 'Preprint', 'en': 'Preprint'},
    'journal': {'pt': 'Artigo científico', 'en': 'Research paper'},
}

SOURCE_NOTES = {
    'agency': {
        'pt': 'Fonte primária institucional.',
        'en': 'Primary institutional source.',
    },
    'preprint': {
        'pt': 'Preprint ainda sem revisão por pares.',
        'en': 'Preprint not yet peer reviewed.',
    },
    'journal': {
        'pt': 'Artigo científico revisado por pares.',
        'en': 'Peer-reviewed research paper.',
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


# A comprehensive set of high‑quality primary and secondary sources. This list
# preserves the strong international core, removes one duplicate NASA feed and
# adds a curated Brazilian block focused on scientifically reliable reporting.
# The result is a hybrid mix of institutional, journalistic and preprint feeds
# without changing the downstream parsing/export pipeline.
SOURCES = [
    # ── Institutional / Agency ──────────────────────────────────────────────
    SourceConfig('NASA News Releases',          'https://www.nasa.gov/news-release/feed/',                                              'rss',  'agency',   94),
    SourceConfig('JPL News',                    'https://www.jpl.nasa.gov/feeds/news/',                                                 'rss',  'agency',   93),
    # Updated ESO feed (feedburner)
    SourceConfig('ESO Press Releases',          'https://feeds.feedburner.com/EsoTopNews',                                               'rss',  'agency',   92),
    SourceConfig('ESA Space Science',           'https://www.esa.int/rssfeed/Our_Activities/Space_Science',                             'rss',  'agency',   90),
    SourceConfig('ESA Hubble News',             'https://esahubble.org/news/feed/',                                                     'rss',  'agency',   89),
    # ── Journal feeds ───────────────────────────────────────────────────────
    SourceConfig('Nature',                      'http://feeds.nature.com/nature/rss/current',                                           'rss',  'journal',  88),
    SourceConfig('Nature Astronomy',            'http://feeds.nature.com/natastron/rss/current',                                        'rss',  'journal',  87),
    SourceConfig('Science Magazine',            'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science',                'rss',  'journal',  86),
    # ── Major institutions ──────────────────────────────────────────────────
    # CERN updated feed: the old '/news/feed' page is a HTML landing page that breaks XML parsing.
    # Use the dedicated API feed which provides well‑formed RSS items.
    SourceConfig('CERN News',                   'https://home.cern/api/news/news/feed.rss',                                            'rss',  'agency',   86),
    # APS Physics: the physics.aps.org domain requires JavaScript and triggers Cloudflare protection.
    # Use the feeds.aps.org mirror which provides the same recent Physics articles without a 403 barrier.
    SourceConfig('APS Physics',                 'https://feeds.aps.org/rss/recent/physics.xml',                                         'rss',  'journal',  83),
    SourceConfig('NSF News',                    'https://www.nsf.gov/rss/rss_www_news.xml',                                             'rss',  'agency',   80),
    SourceConfig('ESA Space News',              'https://www.esa.int/rssfeed/Our_Activities/Space_News',                                'rss',  'agency',   80),
    SourceConfig('NIH News Releases',           'https://www.nih.gov/news-releases/feed.xml',                                           'rss',  'agency',   79),
    # Planetary Society: updated feed URL
    SourceConfig('The Planetary Society',       'https://www.planetary.org/rss/articles',                                              'rss',  'agency',   78),
    # Bloco brasileiro curado: fontes com reputação forte em jornalismo científico.
    # A duplicata do feed da NASA foi removida para abrir espaço sem degradar cobertura.
    SourceConfig('Agência FAPESP',             'http://agencia.fapesp.br/rss/',                                                       'rss',  'agency',   77),
    # Phys.org sections (URLs corrigidas: /rss-feed/{category}-news/)
    SourceConfig('Phys.org Space',              'https://phys.org/rss-feed/space-news/',                                               'rss',  'agency',   76),
    # NASA Earth Observatory: URL corrigida
    SourceConfig('NASA Earth Observatory',      'https://earthobservatory.nasa.gov/feeds/earth-observatory.rss',                        'rss',  'agency',   75),
    SourceConfig('Sky & Telescope',             'https://skyandtelescope.org/feed/',                                                    'rss',  'agency',   74),
    SourceConfig('Universe Today',              'https://www.universetoday.com/feed/',                                                  'rss',  'agency',   73),
    SourceConfig('EarthSky',                    'https://earthsky.org/feed/',                                                           'rss',  'agency',   72),
    # Pesquisa FAPESP é uma revista de jornalismo científico voltada à produção brasileira.
    SourceConfig('Pesquisa FAPESP Online',      'https://revistapesquisa.fapesp.br/category/online/feed/',                              'rss',  'journal',  72),
    SourceConfig('Pesquisa FAPESP Ciência',     'https://revistapesquisa.fapesp.br/category/impressa/ciencia/feed/',                    'rss',  'journal',  71),
    SourceConfig('Phys.org Biology',            'https://phys.org/rss-feed/biology-news/',                                             'rss',  'agency',   71),
    SourceConfig('Phys.org Physics',            'https://phys.org/rss-feed/physics-news/',                                             'rss',  'agency',   71),
    SourceConfig('Phys.org Chemistry',          'https://phys.org/rss-feed/chemistry-news/',                                           'rss',  'agency',   70),
    # Faixa temática brasileira adicional para astronomia e espaço.
    SourceConfig('Pesquisa FAPESP Astronomia',  'https://revistapesquisa.fapesp.br/tag/astronomia/feed/',                              'rss',  'journal',  69),
    # Removido: feed de Earth Sciences indisponível (404)
    # ── arXiv preprints ─────────────────────────────────────────────────────
    SourceConfig('arXiv Astrophysics',
        'https://export.arxiv.org/api/query?search_query=(cat:astro-ph.*+AND+(all:exoplanet+OR+all:galaxy+OR+all:%22dark+matter%22+OR+all:%22dark+energy%22+OR+all:%22black+hole%22+OR+all:cosmology+OR+all:%22gravitational+wave%22+OR+all:supernova+OR+all:jwst+OR+all:euclid+OR+all:mars+OR+all:moon))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=20',
        'atom', 'preprint', 56),
    SourceConfig('arXiv Cosmology',
        'https://export.arxiv.org/api/query?search_query=(cat:astro-ph.CO+AND+(all:%22dark+energy%22+OR+all:%22dark+matter%22+OR+all:%22hubble+tension%22+OR+all:cmb+OR+all:inflation+OR+all:%22large+scale+structure%22+OR+all:euclid+OR+all:desi+OR+all:cosmology))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 57),
    SourceConfig('arXiv High Energy Astrophysics',
        'https://export.arxiv.org/api/query?search_query=(cat:astro-ph.HE+AND+(all:%22black+hole%22+OR+all:%22neutron+star%22+OR+all:%22gravitational+wave%22+OR+all:%22gamma-ray+burst%22+OR+all:pulsar+OR+all:%22fast+radio+burst%22+OR+all:kilonova+OR+all:ligo))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 54),
    SourceConfig('arXiv Earth & Planetary',
        'https://export.arxiv.org/api/query?search_query=(cat:astro-ph.EP+AND+(all:exoplanet+OR+all:mars+OR+all:moon+OR+all:venus+OR+all:atmosphere+OR+all:biosignature+OR+all:habitability+OR+all:%22solar+system%22))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 56),
    SourceConfig('arXiv Physics Frontiers',
        'https://export.arxiv.org/api/query?search_query=((cat:quant-ph+OR+cat:hep-ph+OR+cat:hep-ex+OR+cat:physics.plasm-ph+OR+cat:cond-mat.mtrl-sci)+AND+(all:quantum+OR+all:particle+OR+all:muon+OR+all:plasma+OR+all:higgs+OR+all:quark+OR+all:superconductor+OR+all:topological))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 53),
    SourceConfig('arXiv Quantitative Biology',
        'https://export.arxiv.org/api/query?search_query=(cat:q-bio.*+AND+(all:biology+OR+all:cell+OR+all:genome+OR+all:protein+OR+all:disease+OR+all:microbe+OR+all:evolution+OR+all:crispr))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 50),
    SourceConfig('arXiv Chemical Physics',
        'https://export.arxiv.org/api/query?search_query=((cat:physics.chem-ph+OR+cat:cond-mat.soft)+AND+(all:chemistry+OR+all:chemical+OR+all:molecule+OR+all:catalyst+OR+all:spectroscopy+OR+all:reaction+OR+all:polymer+OR+all:synthesis))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 49),
    SourceConfig('arXiv Geophysics',
        'https://export.arxiv.org/api/query?search_query=((cat:physics.geo-ph+OR+cat:physics.ao-ph)+AND+(all:earth+OR+all:climate+OR+all:ocean+OR+all:atmosphere+OR+all:geophysics+OR+all:magnetic+OR+all:weather+OR+all:glacier))'
        '&sortBy=submittedDate&sortOrder=descending&max_results=16',
        'atom', 'preprint', 51),
]

TRANSLATION_CACHE: dict[tuple[str, str], str] = {}
PAGE_CACHE: dict[str, str] = {}
IMAGE_CACHE: dict[str, Optional[str]] = {}
PAGE_FETCHES = 0
INLINE_IMAGE_CACHE: dict[tuple[str, str], list[dict]] = {}
VIDEO_CACHE: dict[str, Optional[dict]] = {}
AUDIO_CACHE: dict[str, Optional[dict]] = {}
GEMINI_CACHE: dict[tuple[str, str], object] = {}
# Controle de rate limit: rastreia timestamps das chamadas bem-sucedidas
# para respeitar o limite de GEMINI_RPM_LIMIT req/min da free tier.
_GEMINI_CALL_TIMES: list[float] = []
_GEMINI_CONSECUTIVE_503 = 0
_GEMINI_DISABLED_THIS_RUN = False
_GEMINI_UNAVAILABLE_MODELS: set[str] = set()


# ── Utility functions ─────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_with_retry(url: str, timeout: int = REQUEST_TIMEOUT, retries: int = 0) -> bytes:
    """Fetch *url* with optional retries on transient failures.

    Uses exponential back-off (1 s, 2 s) between attempts.
    Re-raises the last exception when all attempts are exhausted.
    """
    import time as _time
    last_exc: Exception = Exception('no attempts made')
    for attempt in range(max(1, retries + 1)):
        try:
            return fetch(url, timeout=timeout)
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                _time.sleep(2 ** attempt)
    raise last_exc


def collapse_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def normalize_text(text: str) -> str:
    text = collapse_ws(text or '').lower()
    return (text
            .replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a').replace('ä', 'a')
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


def unescape_html_loose(text: str, rounds: int = 3) -> str:
    value = str(text or '')
    for _ in range(max(1, rounds)):
        decoded = html.unescape(value)
        if decoded == value:
            break
        value = decoded
    return value


def sanitize_plain_text(text: str) -> str:
    if text is None:
        return ''
    value = unescape_html_loose(str(text), rounds=3).replace('\xa0', ' ')
    value = re.sub(r'&\s*nbsp\s*;?', ' ', value, flags=re.I)
    value = re.sub(r'\bnbsp\b\.?', ' ', value, flags=re.I)
    value = re.sub(r'&\s*amp\s*;?', '&', value, flags=re.I)
    value = value.replace('&#160;', ' ')
    value = re.sub(r'\s+([,;:.!?])', r'\1', value)
    value = re.sub(r'([\(\[{])\s+', r'\1', value)
    value = re.sub(r'\s+([\)\]}])', r'\1', value)
    value = re.sub(r'([,;:!?])([^\s"\'”’\)\]}])', r'\1 \2', value)
    value = re.sub(r'(?<!\d)\.([^\s\d])', r'. \1', value)
    value = re.sub(r'\s{2,}', ' ', value)
    return value.strip()


def sanitize_text_list(items: list[str], limit: int | None = None) -> list[str]:
    out: list[str] = []
    seen = set()
    for item in items or []:
        cleaned = sanitize_plain_text(str(item or ''))
        if not cleaned:
            continue
        key = normalize_text(cleaned)
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
        if limit and len(out) >= limit:
            break
    return out


def _strip_highlight_prefix(text: str) -> str:
    return re.sub(
        r'^(Ponto central|Dado-chave|Origem institucional|Central point|Key detail|Key datum|Institutional origin)\s*:\s*',
        '',
        sanitize_plain_text(text or ''),
        flags=re.I,
    )


def summary_looks_broken(text: str) -> bool:
    cleaned = sanitize_plain_text(text or '')
    if not cleaned:
        return True
    if 'nbsp' in normalize_text(cleaned):
        return True
    weird_periods = len(re.findall(r'\b[a-zà-ÿ]{3,}\.\s+[a-zà-ÿ]{2,}', cleaned, flags=re.I))
    fragment_periods = len(re.findall(r'\.\s+[a-zà-ÿ]{2,}', cleaned, flags=re.I))
    return weird_periods >= 2 or fragment_periods >= 3


def sanitize_body_html(body_html: str) -> str:
    raw = str(body_html or '')
    if not raw:
        return ''

    paragraphs: list[tuple[str, str]] = []
    for match in re.finditer(r'<p\b([^>]*)>(.*?)</p>', raw, flags=re.I | re.S):
        attrs = match.group(1) or ''
        inner = match.group(2) or ''
        if 'art-source' in attrs.lower():
            paragraphs.append(('source', match.group(0).replace('\xa0', ' ')))
            continue
        cleaned = sanitize_plain_text(strip_html(inner))
        if cleaned:
            paragraphs.append(('text', cleaned))

    text_paragraphs = [text for kind, text in paragraphs if kind == 'text']
    if len(text_paragraphs) >= 2 and summary_looks_broken(text_paragraphs[0]) and not summary_looks_broken(text_paragraphs[1]):
        dropped = False
        rebuilt: list[tuple[str, str]] = []
        for kind, value in paragraphs:
            if kind == 'text' and not dropped:
                dropped = True
                continue
            rebuilt.append((kind, value))
        paragraphs = rebuilt

    out: list[str] = []
    for kind, value in paragraphs:
        if kind == 'source':
            out.append(value)
        else:
            out.append(f'<p>{html.escape(value)}</p>')
    return ''.join(out).strip()


def first_summary_from_body_html(body_html: str, lang: str = 'pt') -> str:
    if not body_html:
        return ''
    for match in re.finditer(r'<p\b([^>]*)>(.*?)</p>', str(body_html), flags=re.I | re.S):
        attrs = (match.group(1) or '').lower()
        if 'art-source' in attrs:
            continue
        cleaned = sanitize_plain_text(strip_html(match.group(2) or ''))
        if not cleaned or len(cleaned) < 40:
            continue
        if lang == 'pt':
            summary = _take_complete_sentences_pt(cleaned, max_sentences=1, max_chars=220)
        else:
            summary = truncate(cleaned, 220)
        summary = sanitize_plain_text(summary)
        if summary_looks_broken(summary):
            continue
        if summary and len(summary) >= 40:
            return summary
    return ''


def sanitize_post_record(post: dict) -> dict:
    if not isinstance(post, dict):
        return post

    plain_fields = [
        'title', 'title_pt', 'title_en',
        'source', 'sourceDomain', 'sourceTypeLabel', 'sourceTypeLabel_pt', 'sourceTypeLabel_en',
        'sourceNote', 'sourceNote_pt', 'sourceNote_en',
        'evidenceLabel', 'evidenceLabel_pt', 'evidenceLabel_en',
        'editorialBandLabel', 'editorialBandLabel_pt', 'editorialBandLabel_en',
        'date', 'date_pt', 'date_en', 'time', 'time_pt', 'time_en',
        'read', 'read_pt', 'read_en',
    ]
    for field in plain_fields:
        if field in post and isinstance(post.get(field), str):
            post[field] = sanitize_plain_text(post.get(field) or '')

    post['body'] = sanitize_body_html(post.get('body') or '')
    post['body_pt'] = sanitize_body_html(post.get('body_pt') or post.get('body') or '')
    post['body_en'] = sanitize_body_html(post.get('body_en') or '')

    summary_specs = [
        ('sub', 'body', 'title', 180, 'pt'),
        ('sub_pt', 'body_pt', 'title_pt', 180, 'pt'),
        ('sub_en', 'body_en', 'title_en', 180, 'en'),
        ('excerpt', 'body', 'title', 260, 'pt'),
        ('excerpt_pt', 'body_pt', 'title_pt', 260, 'pt'),
        ('excerpt_en', 'body_en', 'title_en', 260, 'en'),
    ]
    for field, body_field, title_field, limit, lang in summary_specs:
        current = sanitize_plain_text(post.get(field) or '')
        if summary_looks_broken(current):
            fallback = first_summary_from_body_html(post.get(body_field) or '', lang=lang) or sanitize_plain_text(post.get(title_field) or '')
            current = fallback or current
        post[field] = truncate(sanitize_plain_text(current), limit)

    facts_pt = sanitize_text_list([_strip_highlight_prefix(x) for x in (post.get('highlights_pt') or post.get('highlights') or [])], 6)
    facts_en = sanitize_text_list([_strip_highlight_prefix(x) for x in (post.get('highlights_en') or [])], 6)
    post['highlights'] = build_highlights(post.get('title_pt') or post.get('title') or '', post.get('sub_pt') or post.get('sub') or '', facts_pt, post.get('sourceType') or 'news', 'pt')
    post['highlights_pt'] = post['highlights']
    post['highlights_en'] = build_highlights(post.get('title_en') or post.get('title') or '', post.get('sub_en') or post.get('sub') or '', facts_en, post.get('sourceType') or 'news', 'en')

    post['keywords'] = sanitize_text_list(post.get('keywords') or [], 10)
    post['keywords_pt'] = sanitize_text_list(post.get('keywords_pt') or post.get('keywords') or [], 10)
    post['keywords_en'] = sanitize_text_list(post.get('keywords_en') or post.get('keywords') or [], 10)

    inline_images = []
    seen_images = set()
    for item in post.get('inline_images') or []:
        if not isinstance(item, dict):
            continue
        src = clean_image_url(item.get('src') or '')
        if not src or src in seen_images:
            continue
        seen_images.add(src)
        inline_images.append({
            'src': src,
            'alt': sanitize_plain_text(item.get('alt') or ''),
            'alt_pt': sanitize_plain_text(item.get('alt_pt') or item.get('alt') or ''),
            'alt_en': sanitize_plain_text(item.get('alt_en') or item.get('alt') or ''),
            'caption': sanitize_plain_text(item.get('caption') or ''),
            'caption_pt': sanitize_plain_text(item.get('caption_pt') or item.get('caption') or ''),
            'caption_en': sanitize_plain_text(item.get('caption_en') or item.get('caption') or ''),
        })
    post['inline_images'] = inline_images

    for media_key in ('video', 'audio'):
        media = post.get(media_key)
        if isinstance(media, dict):
            for field in ('title', 'title_pt', 'title_en', 'caption', 'caption_pt', 'caption_en'):
                if field in media:
                    media[field] = sanitize_plain_text(media.get(field) or '')
            for field in ('embedUrl', 'fileUrl', 'poster', 'sourcePage'):
                if field in media and isinstance(media.get(field), str):
                    media[field] = collapse_ws(str(media.get(field) or ''))

    slug = collapse_ws(str(post.get('slug') or ''))
    if slug:
        post['shareUrl'] = article_static_url(slug, 'pt')
        post['shareUrl_pt'] = article_static_url(slug, 'pt')
        post['shareUrl_en'] = article_static_url(slug, 'en')
        post['canonicalUrl'] = article_static_url(slug, 'pt')
        post['canonicalUrl_pt'] = article_static_url(slug, 'pt')
        post['canonicalUrl_en'] = article_static_url(slug, 'en')
        post['realUrl'] = article_dynamic_url(slug, 'pt')
        post['realUrl_pt'] = article_dynamic_url(slug, 'pt')
        post['realUrl_en'] = article_dynamic_url(slug, 'en')
    post['defaultLanguage'] = 'pt-BR'
    post['availableLanguages'] = ['pt-BR', 'en-US']

    post['imageAlt'] = sanitize_plain_text(post.get('imageAlt') or post.get('title_pt') or post.get('title') or '')
    post['imageAlt_pt'] = sanitize_plain_text(post.get('imageAlt_pt') or post.get('title_pt') or post.get('imageAlt') or post.get('title') or '')
    post['imageAlt_en'] = sanitize_plain_text(post.get('imageAlt_en') or post.get('title_en') or post.get('imageAlt') or post.get('title') or '')

    return post


def sanitize_posts(posts: list[dict]) -> list[dict]:
    for post in posts:
        sanitize_post_record(post)
    return posts


def truncate(text: str, limit: int) -> str:
    """
    Truncate a string to at most ``limit`` characters without breaking words or sentences.

    This helper attempts to cut the text at the last sentence‐ending punctuation (period,
    question mark or exclamation point) within the given character limit. If no sentence
    boundary is found, it falls back to cutting at the last space before the limit. A
    trailing period is added when cutting mid‐sentence to make the excerpt feel
    complete. Whitespace is collapsed before truncation.

    Parameters
    ----------
    text: str
        The text to truncate.
    limit: int
        The maximum number of characters allowed in the returned string.

    Returns
    -------
    str
        A truncated version of the input that ends at a natural break point.
    """
    text = collapse_ws(text)
    if len(text) <= limit:
        return text
    # Try to find the last sentence boundary within the limit. Only cut at a
    # sentence boundary if it is reasonably close to the limit to avoid overly
    # short results (heuristically require the boundary after halfway through).
    boundary_pos = -1
    for punct in '.?!':
        pos = text.rfind(punct, 0, limit)
        if pos > boundary_pos:
            boundary_pos = pos
    if boundary_pos >= 0 and boundary_pos >= limit // 2:
        # Include the punctuation mark itself
        return text[:boundary_pos + 1].strip()
    # Fallback: cut at the last space before the limit
    cut = text[:limit].rsplit(' ', 1)[0].strip().rstrip(' .;:,-–—')
    return f'{cut}.' if cut else ''


def smooth_prose(text: str) -> str:
    text = collapse_ws(text)
    if not text:
        return ''
    text = text.replace('…', '.')
    text = re.sub(r'\.{3,}', '.', text)
    # Remove em-dashes e en-dashes — substituir por vírgula ou ponto conforme contexto
    text = re.sub(r'\s+[–—]\s+', ', ', text)
    text = re.sub(r'(?<=\w)[–—](?=\w)', ', ', text)
    # Remove marcadores típicos de IA
    ai_markers = [
        r'^Além disso,\s*', r'^Em resumo,\s*', r'^Vale ressaltar que\s*',
        r'^É importante notar que\s*', r'^Certamente,?\s*', r'^Claro que\s*',
        r'^Portanto,\s*', r'^Em conclusão,\s*', r'^De fato,\s*',
    ]
    for marker in ai_markers:
        text = re.sub(marker, '', text, flags=re.I)
    text = re.sub(r'\s*,\s*,+', ', ', text)
    text = re.sub(r'\s*;\s*', '. ', text)
    text = re.sub(r'\s*:\s*', ': ', text)
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = re.sub(r'([,.;:!?]){2,}', r'\1', text)
    text = re.sub(r'\.(?=[A-Za-z])', '. ', text)
    return collapse_ws(text).strip()


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
    # Rejeitar imagens de interface, logos e retratos de pessoas
    bad_tokens = (
        'logo', 'favicon', 'avatar', 'placeholder', 'sprite', 'icon', 'banner_ad',
        'portrait', 'headshot', 'profile', 'author', 'byline', 'staff', 'team',
        'person', 'people', 'face', 'mugshot', 'contributor', 'editor', 'reporter',
        '/ads/', '/ad/', 'doubleclick', 'tracking', 'pixel', 'newsletter',
    )
    if any(bad in low for bad in bad_tokens):
        return False
    if not re.search(r'\.(jpg|jpeg|png|webp|avif)(?:$|[?#])', low) and not any(t in low for t in ('image', 'photo', 'media', 'img', 'asset')):
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
        # Não armazenar '' no cache por limite atingido — o limite pode
        # ser expandido numa futura chamada ou o URL pode ser válido.
        return ''
    PAGE_FETCHES += 1
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=PAGE_TIMEOUT) as response:
            raw = response.read(1_400_000)
        page = raw.decode('utf-8', errors='ignore')
    except Exception as exc:
        # Só armazena '' no cache para erros HTTP definitivos (4xx/5xx).
        # Timeouts e erros de rede transitórios não são armazenados para
        # permitir que uma segunda chamada (ex: via cache de vídeo) tente novamente.
        if isinstance(exc, urllib.error.HTTPError):
            PAGE_CACHE[url] = ''
        return ''
    PAGE_CACHE[url] = page
    return page



def _json_ld_strings(obj) -> list[str]:
    out = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            low_key = str(key).lower()
            if low_key in {'articlebody', 'description', 'headline', 'alternativeheadline'} and isinstance(value, str):
                out.append(value)
            else:
                out.extend(_json_ld_strings(value))
    elif isinstance(obj, list):
        for value in obj:
            out.extend(_json_ld_strings(value))
    return out


def _extract_json_ld_article_text(page: str) -> str:
    snippets = []
    for match in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page, flags=re.I | re.S):
        raw = html.unescape(match.group(1).strip())
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        snippets.extend(_json_ld_strings(payload))
    cleaned = []
    for snippet in snippets:
        snippet = collapse_ws(strip_html(snippet))
        if len(snippet) >= 120:
            cleaned.append(snippet)
    return ' '.join(unique_keep_order(cleaned))


def _looks_like_article_paragraph(text: str) -> bool:
    text = collapse_ws(text)
    low = normalize_text(text)
    if len(text) < 50:
        return False
    if len(text) > 1400:
        return False
    if any(pattern in low for pattern in BAD_TEXT_HINTS):
        return False
    if low.startswith(('image credit', 'credit:', 'photo credit', 'caption:', 'share this')):
        return False
    if re.search(r'^(related|read more|more information|watch|listen|subscribe)\b', low):
        return False
    return True


def extract_page_text(url: str) -> str:
    page = fetch_page_html(url)
    if not page:
        return ''

    collected = []

    json_ld_text = _extract_json_ld_article_text(page)
    if json_ld_text:
        collected.append(json_ld_text)

    regions = []
    for pattern in (
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<div[^>]+class=["\'][^"\']*(?:article|post|entry|content|story|body)[^"\']*["\'][^>]*>(.*?)</div>',
    ):
        for match in re.finditer(pattern, page, flags=re.I | re.S):
            regions.append(match.group(1))
            if len(regions) >= 5:
                break
        if len(regions) >= 5:
            break

    if not regions:
        regions = [page]

    paragraphs = []
    seen = set()

    def add_candidate(candidate: str) -> None:
        candidate = collapse_ws(strip_html(candidate))
        if not _looks_like_article_paragraph(candidate):
            return
        key = normalize_text(candidate)
        if key in seen:
            return
        seen.add(key)
        paragraphs.append(candidate)

    for region in regions:
        for tag_pattern in (
            r'<p[^>]*>(.*?)</p>',
            r'<li[^>]*>(.*?)</li>',
            r'<blockquote[^>]*>(.*?)</blockquote>',
        ):
            for block in re.findall(tag_pattern, region, flags=re.I | re.S):
                add_candidate(block)
                if len(paragraphs) >= PAGE_TEXT_MAX_PARAGRAPHS:
                    break
            if len(paragraphs) >= PAGE_TEXT_MAX_PARAGRAPHS:
                break
        if len(paragraphs) >= PAGE_TEXT_MAX_PARAGRAPHS:
            break

    merged = ' '.join(collected + paragraphs[:PAGE_TEXT_MAX_PARAGRAPHS])
    return truncate(merged, FULL_TEXT_LIMIT)


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




def _extract_attr(tag_html: str, attr: str) -> str:
    match = re.search(rf'{attr}\s*=\s*["\']([^"\']+)["\']', tag_html, flags=re.I)
    return html.unescape(match.group(1).strip()) if match else ''


def _extract_numeric_attr(tag_html: str, attr: str) -> int:
    raw = _extract_attr(tag_html, attr)
    match = re.search(r'\d{2,5}', raw or '')
    return int(match.group(0)) if match else 0


def _extract_style_background_image(tag_html: str, base_url: str) -> str:
    style = _extract_attr(tag_html, 'style')
    if not style:
        return ''
    match = re.search(r'background-image\s*:\s*url\(([^)]+)\)', style, flags=re.I)
    if not match:
        return ''
    candidate = match.group(1).strip().strip("'\"")
    return urllib.parse.urljoin(base_url, candidate) if candidate else ''


def _best_srcset_candidate(srcset: str, base_url: str) -> str:
    srcset = collapse_ws(srcset or '')
    if not srcset:
        return ''
    best_url = ''
    best_score = -1.0
    for part in srcset.split(','):
        token = collapse_ws(part)
        if not token:
            continue
        pieces = token.split()
        candidate = pieces[0].strip()
        descriptor = pieces[1].strip().lower() if len(pieces) > 1 else ''
        score = 1.0
        if descriptor.endswith('w'):
            try:
                score = float(descriptor[:-1])
            except Exception:
                score = 1.0
        elif descriptor.endswith('x'):
            try:
                score = float(descriptor[:-1]) * 1000.0
            except Exception:
                score = 1.0
        candidate_url = urllib.parse.urljoin(base_url, candidate)
        if score > best_score and clean_image_url(candidate_url):
            best_score = score
            best_url = candidate_url
    return best_url


def _extract_media_dimensions(tag_html: str) -> tuple[int, int]:
    width = _extract_numeric_attr(tag_html, 'width')
    height = _extract_numeric_attr(tag_html, 'height')
    if width and height:
        return width, height
    for attr in ('data-width', 'data-image-width', 'data-full-width', 'data-original-width'):
        width = width or _extract_numeric_attr(tag_html, attr)
    for attr in ('data-height', 'data-image-height', 'data-full-height', 'data-original-height'):
        height = height or _extract_numeric_attr(tag_html, attr)
    return width, height


def _extract_media_src(tag_html: str, base_url: str) -> str:
    srcset = _extract_attr(tag_html, 'srcset') or _extract_attr(tag_html, 'data-srcset') or _extract_attr(tag_html, 'data-lazy-srcset')
    if srcset:
        best = _best_srcset_candidate(srcset, base_url)
        if best:
            return best

    for attr in (
        'src', 'data-src', 'data-lazy-src', 'data-original', 'data-url', 'data-image',
        'data-full', 'data-full-src', 'data-hires', 'data-large-file', 'data-orig-file',
        'data-image-full', 'data-native-src', 'data-zoom-src', 'data-download', 'poster'
    ):
        value = _extract_attr(tag_html, attr)
        if value:
            return urllib.parse.urljoin(base_url, value)

    bg = _extract_style_background_image(tag_html, base_url)
    if bg:
        return bg

    return ''


def _candidate_caption(text: str) -> str:
    text = collapse_ws(strip_html(text or ''))
    if not text or len(text) < 12:
        return ''
    if len(text) > 260:
        text = truncate(text, 240)
    low = normalize_text(text)
    if any(bad in low for bad in ('image credit', 'credit:', 'photo credit', 'copyright', 'all rights reserved')):
        return ''
    return text


def _bad_inline_image(url: str, alt: str = '', caption: str = '', context: str = '') -> bool:
    haystack = normalize_text(' '.join([url or '', alt or '', caption or '', context or '']))
    bad_parts = (
        'logo', 'icon', 'avatar', 'author', 'headshot', 'head shot', 'social', 'share', 'banner',
        'sprite', 'favicon', 'badge', 'tracking', 'pixel', 'ads', 'doubleclick',
        'cookie', 'newsletter', 'promo', 'sponsor', 'placeholder',
        # retratos e pessoas — causam a repetição de fotos de pesquisadores
        'portrait', 'profile', 'staff', 'team', 'person', 'people', 'face',
        'mugshot', 'contributor', 'editor', 'reporter', 'scientist', 'researcher',
        'journalist', 'correspondent', 'reviewer', 'byline', 'edited by', 'written by', 'reviewed by',
        'photo of', 'photo by', 'credit:', 'courtesy',
    )
    return any(part in haystack for part in bad_parts)


def _extract_surrounding_context(html_fragment: str, start: int, end: int, radius: int = 420) -> str:
    if not html_fragment:
        return ''
    left = max(0, start - radius)
    right = min(len(html_fragment), end + radius)
    return html_fragment[left:right]


def _looks_like_person_name(text: str) -> bool:
    text = collapse_ws(strip_html(text or ''))
    if not text or len(text) < 4 or len(text) > 80:
        return False
    if re.search(r'\d', text):
        return False
    parts = [p for p in re.split(r'\s+', text) if p]
    if len(parts) < 2 or len(parts) > 5:
        return False
    cleaned = []
    for part in parts:
        token = re.sub(r"[^A-Za-zÀ-ÿ'’-]", '', part)
        if not token:
            return False
        cleaned.append(token)
    return all(re.fullmatch(r"[A-ZÀ-Ý][a-zà-ÿ'’-]+", token) for token in cleaned)


def _looks_like_small_editor_headshot(
    url: str,
    alt: str = '',
    caption: str = '',
    context: str = '',
    width: int = 0,
    height: int = 0,
) -> bool:
    haystack = normalize_text(' '.join([url or '', alt or '', caption or '', context or '']))
    context_markers = (
        'edited by', 'written by', 'reviewed by', 'byline', 'author', 'author-', 'author_', 'authorphoto',
        'editor', 'editorial', 'reporter', 'journalist', 'correspondent', 'contributor', 'reviewer',
        'profile', 'profile-card', 'profile_card', 'avatar', 'headshot', 'head shot', 'portrait',
        'staff', 'team-member', 'team_member', 'bio', 'biography', 'staffer',
    )
    has_editorial_context = any(marker in haystack for marker in context_markers)

    if has_editorial_context:
        if not width or not height:
            return True
        if width <= 420 or height <= 420 or (width * height) <= 220000:
            return True

    if width and height:
        max_side = max(width, height)
        min_side = min(width, height)
        ratio = max_side / max(1, min_side)
        name_like = collapse_ws(caption or alt or '')
        if max_side <= 420 and min_side <= 420 and ratio <= 1.8:
            if not name_like or len(name_like) <= 48 or _looks_like_person_name(name_like):
                return True

    if has_editorial_context and _looks_like_person_name(collapse_ws(caption or alt or '')):
        return True

    return False


def _extract_article_regions_for_images(page: str) -> list[str]:
    regions = []
    patterns = (
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<div[^>]+class=["\'][^"\']*(?:article|post|entry|content|story|body)[^"\']*["\'][^>]*>(.*?)</div>',
    )
    for pattern in patterns:
        for match in re.finditer(pattern, page, flags=re.I | re.S):
            region = match.group(1)
            if region and len(region) > 200:
                regions.append(region)
                if len(regions) >= 6:
                    return regions
    return regions or [page]


def _extract_meta_image_candidates(page: str, base_url: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    patterns = (
        (r"<meta[^>]+property=['\"]og:image(?:url)?['\"][^>]+content=['\"]([^'\"]+)['\"]", 'og:image'),
        (r"<meta[^>]+name=['\"]twitter:image(?::src)?['\"][^>]+content=['\"]([^'\"]+)['\"]", 'twitter:image'),
        (r"<meta[^>]+itemprop=['\"]image['\"][^>]+content=['\"]([^'\"]+)['\"]", 'itemprop:image'),
        (r"<link[^>]+rel=['\"]image_src['\"][^>]+href=['\"]([^'\"]+)['\"]", 'image_src'),
    )
    for pattern, label in patterns:
        for match in re.finditer(pattern, page, flags=re.I):
            raw = match.group(1).strip()
            if raw:
                candidates.append((urllib.parse.urljoin(base_url, raw), label))
    return candidates


def _json_ld_image_candidates(payload, base_url: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    def visit(node, hint: str = '') -> None:
        if isinstance(node, dict):
            raw_type = node.get('@type') or node.get('type') or ''
            types = raw_type if isinstance(raw_type, list) else [raw_type]
            type_hint = ', '.join(str(t) for t in types if t) or hint

            for key in ('image', 'thumbnailUrl', 'thumbnailURL'):
                value = node.get(key)
                if isinstance(value, str):
                    out.append((urllib.parse.urljoin(base_url, value.strip()), f'jsonld:{type_hint or key}'))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            out.append((urllib.parse.urljoin(base_url, item.strip()), f'jsonld:{type_hint or key}'))
                        else:
                            visit(item, type_hint or key)
                elif isinstance(value, dict):
                    visit(value, type_hint or key)

            if any(normalize_text(str(t)) == 'imageobject' for t in types if t):
                content = node.get('contentUrl') or node.get('url') or ''
                if isinstance(content, str) and content.strip():
                    out.append((urllib.parse.urljoin(base_url, content.strip()), f'jsonld:{type_hint or "ImageObject"}'))

            for child in node.values():
                visit(child, type_hint)
        elif isinstance(node, list):
            for child in node:
                visit(child, hint)

    visit(payload)
    return out


def extract_inline_images(url: str, primary_image: str = '', limit: int = MAX_INLINE_IMAGES) -> list[dict]:
    cache_key = (url, primary_image or '')
    if cache_key in INLINE_IMAGE_CACHE:
        return INLINE_IMAGE_CACHE[cache_key]

    page = fetch_page_html(url)
    if not page:
        INLINE_IMAGE_CACHE[cache_key] = []
        return []

    seen = set()
    out: list[dict] = []
    primary_norm = normalize_text(primary_image or '')
    regions = _extract_article_regions_for_images(page)

    def add_image(src_raw: str, alt_raw: str = '', caption_raw: str = '', width: int = 0, height: int = 0, context_raw: str = '', surrounding_raw: str = ''):
        if len(out) >= limit:
            return
        src = urllib.parse.urljoin(url, src_raw or '')
        src = clean_image_url(src)
        if not src or not image_url_looks_good(src):
            return
        src_norm = normalize_text(src)
        if src_norm == primary_norm or src_norm in seen:
            return
        if width and width < 240:
            return
        if height and height < 160:
            return
        caption_en = _candidate_caption(caption_raw) or _candidate_caption(alt_raw)
        alt_en = _candidate_caption(alt_raw) or caption_en
        combined_context = ' '.join(part for part in (context_raw, surrounding_raw) if part)
        if _bad_inline_image(src, alt_en, caption_en, combined_context):
            return
        if _looks_like_small_editor_headshot(src, alt_en, caption_en, combined_context, width, height):
            return
        seen.add(src_norm)
        caption_pt = translate_text(caption_en, 'pt') if caption_en else ''
        alt_pt = translate_text(alt_en, 'pt') if alt_en else caption_pt
        out.append({
            'src': src,
            'caption': caption_pt or caption_en,
            'caption_pt': caption_pt or caption_en,
            'caption_en': caption_en or caption_pt,
            'alt': alt_pt or alt_en,
            'alt_pt': alt_pt or alt_en,
            'alt_en': alt_en or alt_pt,
        })

    def scan_media_block(block_html: str, surrounding: str = '') -> None:
        if len(out) >= limit or not block_html:
            return
        for tag_match in re.finditer(r'<(?:img|source|picture|div|a)\b[^>]*>', block_html, flags=re.I | re.S):
            if len(out) >= limit:
                break
            tag_html = tag_match.group(0)
            src_raw = _extract_media_src(tag_html, url)
            href_raw = _extract_attr(tag_html, 'href') if re.match(r'<a\b', tag_html, flags=re.I) else ''
            chosen = src_raw or href_raw
            if not chosen:
                continue
            alt_raw = _extract_attr(tag_html, 'alt')
            title_raw = _extract_attr(tag_html, 'title')
            width, height = _extract_media_dimensions(tag_html)
            add_image(chosen, alt_raw, title_raw, width, height, block_html, surrounding)

        for link_match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", block_html, flags=re.I | re.S):
            if len(out) >= limit:
                break
            href = link_match.group(1)
            if not re.search(r'\.(?:jpg|jpeg|png|webp|avif)(?:[?#]|$)', href, flags=re.I):
                continue
            label_html = link_match.group(2)
            img_inside = re.search(r'<img\b[^>]*>', label_html, flags=re.I | re.S)
            img_tag = img_inside.group(0) if img_inside else ''
            alt_raw = _extract_attr(img_tag, 'alt') if img_tag else ''
            title_raw = _extract_attr(img_tag, 'title') if img_tag else ''
            width, height = _extract_media_dimensions(img_tag) if img_tag else (0, 0)
            label = collapse_ws(strip_html(label_html))
            add_image(href, alt_raw or label, title_raw or label, width, height, label_html, surrounding)

    for raw_meta_url, origin in _extract_meta_image_candidates(page, url):
        if len(out) >= limit:
            break
        add_image(raw_meta_url, '', '', 0, 0, origin, origin)

    for match in re.finditer(r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", page, flags=re.I | re.S):
        if len(out) >= limit:
            break
        raw = html.unescape(match.group(1).strip())
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        for candidate_url, origin in _json_ld_image_candidates(payload, url):
            if len(out) >= limit:
                break
            add_image(candidate_url, '', '', 0, 0, origin, origin)

    gallery_patterns = (
        r'<figure\b[^>]*>.*?</figure>',
        r'<picture\b[^>]*>.*?</picture>',
        r"<div\b[^>]+class=[\"'][^\"']*(?:gallery|carousel|swiper|lightbox|fancybox|article-image|story-image|inline-image|media|slideshow)[^\"']*[\"'][^>]*>.*?</div>",
        r"<a\b[^>]+(?:data-fancybox|data-lightbox|data-download|data-full|data-hires|class=[\"'][^\"']*(?:gallery|lightbox|fancybox|image)[^\"']*[\"'])[^>]*>.*?</a>",
    )

    for region in regions:
        if len(out) >= limit:
            break

        for pattern in gallery_patterns:
            for block_match in re.finditer(pattern, region, flags=re.I | re.S):
                if len(out) >= limit:
                    break
                block_html = block_match.group(0)
                surrounding = _extract_surrounding_context(region, block_match.start(), block_match.end(), radius=560)
                scan_media_block(block_html, surrounding)

        for img_match in re.finditer(r'<img\b[^>]*>', region, flags=re.I | re.S):
            if len(out) >= limit:
                break
            tag_html = img_match.group(0)
            surrounding = _extract_surrounding_context(region, img_match.start(), img_match.end(), radius=560)
            src_raw = _extract_media_src(tag_html, url)
            alt_raw = _extract_attr(tag_html, 'alt')
            title_raw = _extract_attr(tag_html, 'title')
            width, height = _extract_media_dimensions(tag_html)
            add_image(src_raw, alt_raw, title_raw, width, height, tag_html, surrounding)

        for link_match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", region, flags=re.I | re.S):
            if len(out) >= limit:
                break
            href = link_match.group(1)
            if not re.search(r'\.(?:jpg|jpeg|png|webp|avif)(?:[?#]|$)', href, flags=re.I):
                continue
            label_html = link_match.group(2)
            surrounding = _extract_surrounding_context(region, link_match.start(), link_match.end(), radius=560)
            img_inside = re.search(r'<img\b[^>]*>', label_html, flags=re.I | re.S)
            img_tag = img_inside.group(0) if img_inside else ''
            alt_raw = _extract_attr(img_tag, 'alt') if img_tag else ''
            title_raw = _extract_attr(img_tag, 'title') if img_tag else ''
            width, height = _extract_media_dimensions(img_tag) if img_tag else (0, 0)
            label = collapse_ws(strip_html(label_html))
            caption_raw = title_raw or label
            add_image(href, alt_raw or caption_raw, caption_raw, width, height, label_html, surrounding)

    INLINE_IMAGE_CACHE[cache_key] = out
    return out





def _extract_meta_video_candidates(page: str, base_url: str) -> list[dict]:
    candidates: list[dict] = []
    patterns = (
        (r"<meta[^>]+property=[\"']og:video(?::url|:secure_url)?[\"'][^>]+content=[\"']([^\"']+)[\"']", 'og:video'),
        (r"<meta[^>]+name=[\"']twitter:player[\"'][^>]+content=[\"']([^\"']+)[\"']", 'twitter:player'),
        (r"<meta[^>]+name=[\"']twitter:player:stream[\"'][^>]+content=[\"']([^\"']+)[\"']", 'twitter:player:stream'),
        (r"<meta[^>]+itemprop=[\"']embedUrl[\"'][^>]+content=[\"']([^\"']+)[\"']", 'itemprop:embedUrl'),
        (r"<meta[^>]+itemprop=[\"']contentUrl[\"'][^>]+content=[\"']([^\"']+)[\"']", 'itemprop:contentUrl'),
    )
    for pattern, origin in patterns:
        for match in re.finditer(pattern, page, flags=re.I):
            value = collapse_ws(match.group(1).strip())
            if not value:
                continue
            absolute = urllib.parse.urljoin(base_url, value)
            candidates.append({
                'embed_url': absolute,
                'content_url': absolute,
                'page_url': '',
                'poster': '',
                'title_en': '',
                'caption_en': origin,
            })
    return candidates


def _json_ld_video_candidates(payload, base_url: str) -> list[dict]:
    candidates: list[dict] = []

    def visit(node) -> None:
        if isinstance(node, dict):
            raw_type = node.get('@type') or node.get('type') or ''
            types = raw_type if isinstance(raw_type, list) else [raw_type]
            low_types = {normalize_text(str(t)) for t in types if t}
            if 'videoobject' in low_types:
                embed = urllib.parse.urljoin(base_url, str(node.get('embedUrl') or '').strip()) if node.get('embedUrl') else ''
                content = urllib.parse.urljoin(base_url, str(node.get('contentUrl') or '').strip()) if node.get('contentUrl') else ''
                page_url = urllib.parse.urljoin(base_url, str(node.get('url') or '').strip()) if node.get('url') else ''
                thumb = node.get('thumbnailUrl') or node.get('thumbnailURL') or ''
                if isinstance(thumb, list):
                    thumb = thumb[0] if thumb else ''
                thumb = urllib.parse.urljoin(base_url, str(thumb).strip()) if thumb else ''
                title_en = collapse_ws(strip_html(str(node.get('name') or node.get('headline') or '')))
                caption_en = collapse_ws(strip_html(str(node.get('description') or '')))
                if embed or content:
                    candidates.append({
                        'embed_url': embed,
                        'content_url': content,
                        'page_url': page_url,
                        'poster': clean_image_url(thumb) if thumb else '',
                        'title_en': title_en,
                        'caption_en': caption_en,
                    })
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(payload)
    return candidates


def _normalize_video_candidate(base_url: str, raw_url: str) -> Optional[dict]:
    raw_url = collapse_ws(raw_url or '')
    if not raw_url:
        return None
    absolute = urllib.parse.urljoin(base_url, raw_url)
    absolute = absolute.replace('&amp;', '&')

    try:
        parsed = urllib.parse.urlparse(absolute)
    except Exception:
        parsed = urllib.parse.urlparse('')

    host = (parsed.netloc or '').lower()
    path = parsed.path or ''
    low = absolute.lower()

    video_id = ''
    if host.endswith('youtu.be'):
        video_id = path.strip('/').split('/')[0]
    elif host.endswith('youtube.com') or host.endswith('youtube-nocookie.com') or host.endswith('m.youtube.com'):
        if path.startswith('/watch'):
            video_id = urllib.parse.parse_qs(parsed.query).get('v', [''])[0]
        elif path.startswith('/embed/') or path.startswith('/live/') or path.startswith('/shorts/'):
            parts = [part for part in path.split('/') if part]
            video_id = parts[1] if len(parts) >= 2 else ''

    if video_id:
        clean_id = re.sub(r'[^A-Za-z0-9_-]', '', video_id)
        if clean_id:
            return {
                'kind': 'embed',
                'platform': 'youtube',
                'embedUrl': f'https://www.youtube-nocookie.com/embed/{clean_id}?rel=0&modestbranding=1',
                'fileUrl': '',
            }

    match = re.search(r'(?:player\.)?vimeo\.com/(?:video/)?(\d+)', absolute, flags=re.I)
    if match:
        video_id = match.group(1)
        return {
            'kind': 'embed',
            'platform': 'vimeo',
            'embedUrl': f'https://player.vimeo.com/video/{video_id}',
            'fileUrl': '',
        }

    if re.search(r'\.(mp4|webm|ogg|m3u8)(?:[?#]|$)', low):
        return {
            'kind': 'file',
            'platform': 'html5',
            'embedUrl': '',
            'fileUrl': absolute,
        }

    if any(token in low for token in ('/embed/', 'player.', 'streamable.com/', 'brightcove', 'jwplayer', 'wistia', 'dailymotion.com/embed', 'loom.com/embed')):
        return {
            'kind': 'embed',
            'platform': 'embed',
            'embedUrl': absolute,
            'fileUrl': '',
        }
    return None



def _video_media_page_links(search_html: str, base_url: str) -> list[str]:
    links: list[str] = []
    seen = set()
    for match in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', search_html or '', flags=re.I | re.S):
        href = collapse_ws(match.group(1))
        label = collapse_ws(strip_html(match.group(2) or ''))
        if not href:
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        low_href = absolute.lower()
        low_label = normalize_text(label)
        looks_like_media_page = (
            '/esa_multimedia/videos/' in low_href
            or '/videos/' in low_href
            or 'access the video' in low_label
            or low_label == 'video'
            or low_label.startswith('watch video')
        )
        if not looks_like_media_page:
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        links.append(absolute)
    return links[:4]


def _extract_video_candidates_from_html(page_html: str, base_url: str) -> list[dict]:
    candidates: list[dict] = []
    regions = _extract_article_regions_for_images(page_html)
    search_html = "\n".join(regions) if regions else page_html
    candidates.extend(_extract_meta_video_candidates(page_html, base_url))

    for match in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page_html, flags=re.I | re.S):
        raw = html.unescape(match.group(1).strip())
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        candidates.extend(_json_ld_video_candidates(payload, base_url))

    for match in re.finditer(r'<iframe\b[^>]*src=["\']([^"\']+)["\'][^>]*>', search_html, flags=re.I | re.S):
        normalized = _normalize_video_candidate(base_url, match.group(1))
        if normalized:
            candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'poster': '', 'title_en': '', 'caption_en': ''})

    for video_match in re.finditer(r'<video\b([^>]*)>(.*?)</video>', search_html, flags=re.I | re.S):
        attrs = video_match.group(1)
        inner = video_match.group(2)
        direct = _extract_attr(attrs, 'src') or _extract_attr(attrs, 'data-src') or ''
        poster = urllib.parse.urljoin(base_url, _extract_attr(attrs, 'poster')) if _extract_attr(attrs, 'poster') else ''
        if not direct:
            source_match = re.search(r'<source\b[^>]*src=["\']([^"\']+)["\']', inner, flags=re.I | re.S)
            direct = source_match.group(1) if source_match else ''
        normalized = _normalize_video_candidate(base_url, direct)
        if normalized:
            candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'poster': clean_image_url(poster) if poster else '', 'title_en': '', 'caption_en': ''})

    link_patterns = (
        r'<a\b[^>]*href=["\']([^"\']*(?:youtu\.be/|youtube\.com/(?:watch|embed|shorts|live)|vimeo\.com/[^"\']+|\.(?:mp4|webm|ogg|m3u8)(?:\?[^"\']*)?))["\'][^>]*>(.*?)</a>',
        r'(https?://(?:www\.)?(?:youtu\.be/[^\s"\'<]+|youtube\.com/(?:watch\?v=|embed/|shorts/|live/)[^\s"\'<]+|vimeo\.com/[^\s"\'<]+))',
    )
    for pattern in link_patterns:
        for match in re.finditer(pattern, search_html, flags=re.I | re.S):
            href = match.group(1)
            normalized = _normalize_video_candidate(base_url, href)
            if normalized:
                label = collapse_ws(strip_html(match.group(2))) if pattern.startswith(r'<a') else ''
                candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'poster': '', 'title_en': '', 'caption_en': label})
    return candidates


def extract_page_video(url: str) -> Optional[dict]:
    if not url:
        return None
    if url in VIDEO_CACHE:
        return VIDEO_CACHE[url]

    page = fetch_page_html(url)
    if not page:
        VIDEO_CACHE[url] = None
        return None

    candidates: list[dict] = []
    candidates.extend(_extract_video_candidates_from_html(page, url))

    regions = _extract_article_regions_for_images(page)
    search_html = "\n".join(regions) if regions else page
    for media_page in _video_media_page_links(search_html, url):
        media_html = fetch_page_html(media_page)
        if not media_html:
            continue
        for item in _extract_video_candidates_from_html(media_html, media_page):
            if not item.get('poster'):
                item['poster'] = fetch_page_image(media_page) or ''
            item['source_page'] = media_page
            candidates.append(item)

    def _candidate_rank(candidate: dict) -> tuple:
        content_url = collapse_ws(str(candidate.get('content_url') or ''))
        embed_url = collapse_ws(str(candidate.get('embed_url') or ''))
        poster = collapse_ws(str(candidate.get('poster') or ''))
        source_page = collapse_ws(str(candidate.get('source_page') or ''))
        low_content = content_url.lower()
        return (
            0 if low_content.endswith('.mp4') or '.mp4?' in low_content else 1,
            0 if poster else 1,
            0 if '/esa_multimedia/videos/' in source_page.lower() else 1,
            0 if content_url else 1,
            0 if embed_url else 1,
        )

    seen = set()
    for candidate in sorted(candidates, key=_candidate_rank):
        raw_video_url = candidate.get('content_url') or candidate.get('embed_url') or candidate.get('page_url') or ''
        normalized = _normalize_video_candidate(url, raw_video_url)
        if not normalized:
            continue
        key = (normalized.get('kind', ''), normalized.get('embedUrl', ''), normalized.get('fileUrl', ''))
        if key in seen:
            continue
        seen.add(key)

        title_en = collapse_ws(strip_html(candidate.get('title_en') or ''))
        caption_en = collapse_ws(strip_html(candidate.get('caption_en') or ''))
        if caption_en.lower().startswith(('og:video', 'twitter:player', 'itemprop:')):
            caption_en = ''
        title_pt = translate_text(title_en, 'pt') if title_en else ''
        caption_pt = translate_text(caption_en, 'pt') if caption_en else ''

        result = {
            'kind': normalized.get('kind', 'embed'),
            'platform': normalized.get('platform', 'embed'),
            'embedUrl': normalized.get('embedUrl', ''),
            'fileUrl': normalized.get('fileUrl', ''),
            'poster': candidate.get('poster', '') or '',
            'title': title_pt or title_en,
            'title_pt': title_pt or title_en,
            'title_en': title_en or title_pt,
            'caption': caption_pt or caption_en,
            'caption_pt': caption_pt or caption_en,
            'caption_en': caption_en or caption_pt,
            'sourcePage': candidate.get('source_page') or url,
        }
        VIDEO_CACHE[url] = result
        return result

    VIDEO_CACHE[url] = None
    return None


def _json_ld_audio_candidates(payload, base_url: str) -> list[dict]:
    candidates: list[dict] = []

    def visit(node) -> None:
        if isinstance(node, dict):
            raw_type = node.get('@type') or node.get('type') or ''
            types = raw_type if isinstance(raw_type, list) else [raw_type]
            low_types = {normalize_text(str(t)) for t in types if t}
            if 'audioobject' in low_types:
                embed = urllib.parse.urljoin(base_url, str(node.get('embedUrl') or '').strip()) if node.get('embedUrl') else ''
                content = urllib.parse.urljoin(base_url, str(node.get('contentUrl') or '').strip()) if node.get('contentUrl') else ''
                page_url = urllib.parse.urljoin(base_url, str(node.get('url') or '').strip()) if node.get('url') else ''
                title_en = collapse_ws(strip_html(str(node.get('name') or node.get('headline') or '')))
                caption_en = collapse_ws(strip_html(str(node.get('description') or '')))
                if embed or content or page_url:
                    candidates.append({
                        'embed_url': embed,
                        'content_url': content,
                        'page_url': page_url,
                        'title_en': title_en,
                        'caption_en': caption_en,
                    })
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(payload)
    return candidates


def _normalize_audio_candidate(base_url: str, raw_url: str) -> Optional[dict]:
    raw_url = collapse_ws(raw_url or '')
    if not raw_url:
        return None
    absolute = urllib.parse.urljoin(base_url, raw_url).replace('&amp;', '&')
    low = absolute.lower()

    if re.search(r'open\.spotify\.com/embed/(episode|show|track)/', low):
        return {'kind': 'embed', 'platform': 'spotify', 'embedUrl': absolute, 'fileUrl': ''}
    if 'w.soundcloud.com/player' in low or 'soundcloud.com/player' in low:
        return {'kind': 'embed', 'platform': 'soundcloud', 'embedUrl': absolute, 'fileUrl': ''}
    if any(token in low for token in ('simplecast.com', 'transistor.fm', 'buzzsprout.com', 'podbean.com', 'megaphone.fm', 'omny.fm', 'audioboom.com')) and ('embed' in low or 'player' in low):
        return {'kind': 'embed', 'platform': 'podcast', 'embedUrl': absolute, 'fileUrl': ''}
    if re.search(r'\.(mp3|m4a|aac|ogg|wav)(?:[?#]|$)', low):
        return {'kind': 'file', 'platform': 'html5-audio', 'embedUrl': '', 'fileUrl': absolute}
    return None


def extract_page_audio(url: str) -> Optional[dict]:
    if not url:
        return None
    if url in AUDIO_CACHE:
        return AUDIO_CACHE[url]

    page = fetch_page_html(url)
    if not page:
        AUDIO_CACHE[url] = None
        return None

    regions = _extract_article_regions_for_images(page)
    search_html = "\n".join(regions) if regions else page
    candidates: list[dict] = []

    for match in re.finditer(r"<script[^>]+type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>", page, flags=re.I | re.S):
        raw = html.unescape(match.group(1).strip())
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        candidates.extend(_json_ld_audio_candidates(payload, url))

    meta_patterns = (
        r"<meta[^>]+property=['\"]og:audio(?::url|:secure_url)?['\"][^>]+content=['\"]([^'\"]+)['\"]",
        r"<meta[^>]+name=['\"]twitter:audio:src['\"][^>]+content=['\"]([^'\"]+)['\"]",
    )
    for pattern in meta_patterns:
        for match in re.finditer(pattern, page, flags=re.I):
            normalized = _normalize_audio_candidate(url, match.group(1).strip())
            if normalized:
                candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'title_en': '', 'caption_en': ''})

    for match in re.finditer(r"<iframe\b[^>]*src=['\"]([^'\"]+)['\"][^>]*>", search_html, flags=re.I | re.S):
        normalized = _normalize_audio_candidate(url, match.group(1))
        if normalized:
            candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'title_en': '', 'caption_en': ''})

    for audio_match in re.finditer(r'<audio\b([^>]*)>(.*?)</audio>', search_html, flags=re.I | re.S):
        attrs = audio_match.group(1)
        inner = audio_match.group(2)
        direct = _extract_attr(attrs, 'src')
        if not direct:
            source_match = re.search(r"<source\b[^>]*src=['\"]([^'\"]+)['\"]", inner, flags=re.I | re.S)
            direct = source_match.group(1) if source_match else ''
        normalized = _normalize_audio_candidate(url, direct)
        if normalized:
            candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'title_en': '', 'caption_en': ''})

    for match in re.finditer(r"<a\b[^>]*href=['\"]([^'\"]+\.(?:mp3|m4a|aac|ogg|wav)(?:\?[^'\"]*)?)['\"][^>]*>(.*?)</a>", search_html, flags=re.I | re.S):
        normalized = _normalize_audio_candidate(url, match.group(1))
        if normalized:
            label = collapse_ws(strip_html(match.group(2)))
            candidates.append({'embed_url': normalized.get('embedUrl', ''), 'content_url': normalized.get('fileUrl', ''), 'page_url': '', 'title_en': label, 'caption_en': ''})

    seen = set()
    for candidate in candidates:
        raw_audio_url = candidate.get('embed_url') or candidate.get('content_url') or candidate.get('page_url') or ''
        normalized = _normalize_audio_candidate(url, raw_audio_url)
        if not normalized:
            continue
        key = (normalized.get('kind', ''), normalized.get('embedUrl', ''), normalized.get('fileUrl', ''))
        if key in seen:
            continue
        seen.add(key)

        title_en = collapse_ws(strip_html(candidate.get('title_en') or ''))
        caption_en = collapse_ws(strip_html(candidate.get('caption_en') or ''))
        title_pt = translate_text(title_en, 'pt') if title_en else ''
        caption_pt = translate_text(caption_en, 'pt') if caption_en else ''

        result = {
            'kind': normalized.get('kind', 'embed'),
            'platform': normalized.get('platform', 'embed'),
            'embedUrl': normalized.get('embedUrl', ''),
            'fileUrl': normalized.get('fileUrl', ''),
            'title': title_pt or title_en,
            'title_pt': title_pt or title_en,
            'title_en': title_en or title_pt,
            'caption': caption_pt or caption_en,
            'caption_pt': caption_pt or caption_en,
            'caption_en': caption_en or caption_pt,
            'sourcePage': url,
        }
        AUDIO_CACHE[url] = result
        return result

    AUDIO_CACHE[url] = None
    return None

def _extract_json_from_text(text: str):
    text = collapse_ws(text)
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass

    for pattern in (r'\[.*\]', r'\{.*\}'):
        match = re.search(pattern, text, flags=re.S)
        if not match:
            continue
        try:
            return json.loads(match.group(0))
        except Exception:
            continue
    return None


def _gemini_prompt_body(text: str) -> str:
    cleaned = collapse_ws(strip_html(text or ''))
    return truncate(cleaned, GEMINI_PAYLOAD_BODY_LIMIT) if cleaned else ''


def _gemini_response_text(payload: dict) -> str:
    parts = []
    for candidate in payload.get('candidates', []) or []:
        content = candidate.get('content') or {}
        for part in content.get('parts', []) or []:
            if isinstance(part, dict) and isinstance(part.get('text'), str):
                parts.append(part['text'])
    return '\n'.join(parts).strip()



def _gemini_models() -> list[str]:
    models = [GEMINI_MODEL] + [m for m in GEMINI_MODEL_FALLBACKS if m and m != GEMINI_MODEL]
    seen = set()
    ordered = []
    for model in models:
        model = collapse_ws(model)
        if not model or model in seen or model in _GEMINI_UNAVAILABLE_MODELS:
            continue
        seen.add(model)
        ordered.append(model)
    return ordered


def _disable_gemini_for_run(reason: str) -> None:
    global _GEMINI_DISABLED_THIS_RUN
    if _GEMINI_DISABLED_THIS_RUN:
        return
    _GEMINI_DISABLED_THIS_RUN = True
    print(f'⚠️  Gemini desabilitado nesta execução: {reason}')


def _mark_gemini_model_unavailable(model: str, reason: str) -> None:
    cleaned = collapse_ws(model)
    if not cleaned:
        return
    if cleaned not in _GEMINI_UNAVAILABLE_MODELS:
        _GEMINI_UNAVAILABLE_MODELS.add(cleaned)
        print(f'⚠️  Modelo Gemini removido desta execução: {cleaned} ({reason})')


def _gemini_review_budget_exhausted(started_at: float | None) -> bool:
    if not started_at or GEMINI_MAX_REVIEW_SECONDS <= 0:
        return False
    import time as _time
    return (_time.monotonic() - started_at) >= GEMINI_MAX_REVIEW_SECONDS


def gemini_probe() -> bool:
    if not GEMINI_API_KEY or not GEMINI_PROBE_ENABLED:
        return bool(GEMINI_API_KEY)
    prompt = '{"ping":"ok"}'
    for _ in range(GEMINI_PROBE_RETRIES + 1):
        result = call_gemini_json('__gemini_probe__', prompt)
        if isinstance(result, dict):
            print('✓  Gemini respondeu ao probe inicial')
            return True
        if _GEMINI_DISABLED_THIS_RUN:
            break
    print('⚠️  Gemini indisponível no probe inicial; revisão será pulada nesta execução.')
    return False

def _gemini_rate_limit_wait() -> None:
    """Aguarda o tempo necessário para não ultrapassar GEMINI_RPM_LIMIT req/min.

    Mantém uma janela deslizante de 60 segundos dos timestamps das chamadas.
    Se a janela já estiver cheia, dorme até que a chamada mais antiga saia dela.
    """
    import time as _time
    now = _time.monotonic()
    # Remove chamadas mais velhas que 60 segundos
    cutoff = now - 60.0
    while _GEMINI_CALL_TIMES and _GEMINI_CALL_TIMES[0] < cutoff:
        _GEMINI_CALL_TIMES.pop(0)
    if len(_GEMINI_CALL_TIMES) >= GEMINI_RPM_LIMIT:
        # Espera até a mais antiga completar 60s
        wait = 60.0 - (now - _GEMINI_CALL_TIMES[0]) + 0.5   # +0.5s de margem
        if wait > 0:
            print(f'    [Gemini] rate limit: aguardando {wait:.1f}s ...')
            _time.sleep(wait)
    _GEMINI_CALL_TIMES.append(_time.monotonic())


def call_gemini_json(task_key: str, prompt: str):
    import socket
    import time as _time

    global _GEMINI_CONSECUTIVE_503, _GEMINI_DISABLED_THIS_RUN

    if not GEMINI_API_KEY:
        return None
    if _GEMINI_DISABLED_THIS_RUN:
        return None
    cache_key = (task_key, prompt)
    if cache_key in GEMINI_CACHE:
        return GEMINI_CACHE[cache_key]

    models = _gemini_models()
    if not models:
        GEMINI_CACHE[cache_key] = None
        return None

    body = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'temperature': 0.1,
            'responseMimeType': 'application/json',
        },
    }
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    transient_codes = {408, 500, 502, 503, 504}
    unavailable_codes = {400, 404}

    for model in models:
        endpoint = GEMINI_ENDPOINT_TEMPLATE.format(model=urllib.parse.quote(model, safe=''))
        url = f'{endpoint}?key={urllib.parse.quote(GEMINI_API_KEY)}'
        retry_on_429 = max(0, GEMINI_RETRY_ON_429)
        retry_transient = max(0, GEMINI_RETRY_TRANSIENT)
        max_attempts = 1 + max(retry_on_429, retry_transient)

        for attempt in range(max_attempts):
            req = urllib.request.Request(
                url,
                data=data,
                method='POST',
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'User-Agent': USER_AGENT,
                },
            )
            _gemini_rate_limit_wait()
            try:
                with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as response:
                    raw = response.read().decode('utf-8', errors='ignore')
                parsed = json.loads(raw)
                out = _extract_json_from_text(_gemini_response_text(parsed))
                _GEMINI_CONSECUTIVE_503 = 0
                GEMINI_CACHE[cache_key] = out
                return out
            except urllib.error.HTTPError as exc:
                try:
                    err_body = exc.read().decode('utf-8', errors='ignore')[:400]
                except Exception:
                    err_body = '(sem corpo)'

                if exc.code == 429 and attempt < retry_on_429:
                    wait = GEMINI_RETRY_DELAY_429
                    print(f'    [Gemini:{model}] 429 quota — aguardando {wait}s e tentando novamente ({attempt + 1}/{retry_on_429}) ...')
                    _time.sleep(wait)
                    continue

                if exc.code in transient_codes and attempt < retry_transient:
                    wait = GEMINI_RETRY_BASE_DELAY * (attempt + 1)
                    print(f'    [Gemini:{model}] HTTP {exc.code} transitório — aguardando {wait}s e tentando novamente ({attempt + 1}/{retry_transient}) ...')
                    _time.sleep(wait)
                    continue

                print(f'ERR Gemini {model} HTTP {exc.code} ({exc.reason}): {err_body}')

                if exc.code in unavailable_codes:
                    _mark_gemini_model_unavailable(model, f'HTTP {exc.code}')
                    if model == GEMINI_MODEL:
                        _disable_gemini_for_run(f'modelo principal inválido ({model}, HTTP {exc.code})')
                    _GEMINI_CONSECUTIVE_503 = 0
                    break

                if exc.code == 503:
                    _GEMINI_CONSECUTIVE_503 += 1
                    if _GEMINI_CONSECUTIVE_503 >= GEMINI_DISABLE_AFTER_CONSECUTIVE_503:
                        _disable_gemini_for_run(f'{_GEMINI_CONSECUTIVE_503} falhas consecutivas HTTP 503 do modelo principal')
                        GEMINI_CACHE[cache_key] = None
                        return None
                else:
                    _GEMINI_CONSECUTIVE_503 = 0
                break
            except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
                if attempt < retry_transient:
                    wait = GEMINI_RETRY_BASE_DELAY * (attempt + 1)
                    print(f'    [Gemini:{model}] timeout/rede — aguardando {wait}s e tentando novamente ({attempt + 1}/{retry_transient}) ...')
                    _time.sleep(wait)
                    continue
                print(f'ERR Gemini {model}: {exc}')
                _GEMINI_CONSECUTIVE_503 = 0
                break
            except Exception as exc:
                print(f'ERR Gemini {model}: {exc}')
                _GEMINI_CONSECUTIVE_503 = 0
                break

    GEMINI_CACHE[cache_key] = None
    return None


_GENERIC_TEMPLATE_MARKERS_PT = [
    'isso importa porque',
    'isso e relevante porque',
    'e importante porque',
    'importa pois',
    'a relevancia esta em que',
    'o relato institucional enquadra',
    'a analise ainda aguarda revisao por pares',
    'o estudo publicado da ao resultado',
    'o interesse mais amplo reside',
    'o interesse mais amplo esta',
    'a biologia aprendeu',
    'a astronomia nao avanca',
    'a fisica so leva um resultado a serio',
    'a cosmologia opera na fronteira',
    'a astrofisica so se torna persuasiva',
    'a ciencia de exoplanetas ja passou',
    'e fundamental reconhecer',
    'como o relato se origina',
    'comunicacoes institucionais',
    'o proximo passo e',
    'o proximo passo crucial',
    'o caminho de uma descoberta',
    'o que da peso a historia',
    'isso nao as torna nao confiaveis',
    'os editores destacaram os seguintes atributos',
    'garantindo a credibilidade do conteudo',
]

_GENERIC_FACT_MARKERS_PT = [
    'origem institucional',
    'resultado ainda sem revisao por pares',
    'material com lastro cientifico publicado',
    'cobertura jornalistica',
    'os editores destacaram os seguintes atributos',
    'garantindo a credibilidade do conteudo',
]

_BAD_ENDING_TOKENS_PT = {
    'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
    'e', 'em', 'no', 'na', 'nos', 'nas', 'ao', 'aos', 'à', 'às', 'com', 'sem', 'por',
    'para', 'pra', 'que', 'se', 'como', 'quando', 'onde', 'esse', 'essa', 'este',
    'esta', 'isso', 'aquele', 'aquela', 'cujo', 'cuja', 'cujos', 'cujas', 'seu', 'sua',
    'seus', 'suas', 'num', 'numa', 'nuns', 'numas', 'apenas', 'durante', 'sobre',
    'esse.', 'essa.', 'este.', 'esta.', 'numa.', 'num.', 'apenas.', 'apos', 'apos.'
}

_PROMOTIONAL_OR_CREDIT_MARKERS_PT = [
    'explore o universo com', 'sua melhor fonte de observacao', 'sua melhor fonte de observação',
    'siga @', 'bluesky', 'instagram', 'youtube', 'facebook', 'linkedin', 'tiktok',
    'cobertura detalhada ao vivo', 'acompanhe ao vivo', 'acompanhe em', 'siga os marcos mais importantes',
    '@esa', '@science.esa', '@transport.esa', '@esascience', 'crédito:', 'credito:',
    'dominio publico', 'domínio público', 'pixabay/cc0', 'public domain', 'image credit',
    'photo credit', 'arxiv doi', 'doi:', 'todos os direitos reservados'
]


def _strip_highlight_prefix_pt(text: str) -> str:
    text = collapse_ws(strip_html(text or ''))
    text = re.sub(r'^(Ponto central|Dado-chave|Dado chave|Core point|Key detail|Institutional origin|Origem institucional)\b\s*:\s*', '', text, flags=re.I)
    return collapse_ws(text)


def _looks_generic_template_paragraph_pt(text: str) -> bool:
    low = normalize_text(text)
    return any(marker in low for marker in _GENERIC_TEMPLATE_MARKERS_PT)


def _looks_promotional_or_credit_paragraph_pt(text: str) -> bool:
    low = normalize_text(text)
    if any(marker in low for marker in _PROMOTIONAL_OR_CREDIT_MARKERS_PT):
        return True
    if low.count('@') >= 2:
        return True
    social_hits = sum(token in low for token in ('instagram', 'youtube', 'facebook', 'linkedin', 'tiktok', 'bluesky'))
    if social_hits >= 2:
        return True
    return False


def _extract_source_paragraph_html(body_html: str) -> str:
    match = re.search(r"(<p\s+class=['\"]art-source['\"][^>]*>.*?</p>)", body_html or '', flags=re.I | re.S)
    return match.group(1) if match else ''


def _source_link_paragraph_html(src_url: str, lang: str = 'pt') -> str:
    if not src_url:
        return ''
    label = 'Fonte' if lang == 'pt' else 'Source'
    return (
        f'<p class="art-source"><a href="{html.escape(src_url)}" ' 
        f'target="_blank" rel="noopener noreferrer">{label}</a></p>'
    )


def _paragraphs_from_html(body_html: str) -> list[str]:
    paragraphs = []
    for raw in re.findall(r'<p\b[^>]*>(.*?)</p>', body_html or '', flags=re.I | re.S):
        cleaned = collapse_ws(strip_html(raw))
        if cleaned:
            paragraphs.append(cleaned)
    if not paragraphs:
        cleaned = collapse_ws(strip_html(body_html or ''))
        if cleaned:
            paragraphs.append(cleaned)
    return paragraphs


def _strip_noise_prefix_pt(text: str) -> str:
    text = collapse_ws(strip_html(text or ''))
    text = re.sub(r'^[\*#>•·\-\u2022\u25cf\u25aa\u25ab\s]+', '', text)
    text = re.sub(r'^["“”\'\'`´]+', '', text)
    text = re.sub(r'^\*+\s*', '', text)
    text = re.sub(r'^(?:atualizacao|atualização)\b\s*', 'Atualização ', text, flags=re.I)
    text = re.sub(r'^(?:cr[eé]dito|credito)\s*:\s*(?:arxiv\s+doi|doi)\s*:\s*\S+\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:cr[eé]dito|credito)\s*:\s*\S+\s+(?:arxiv\s+doi|doi)\s*:\s*\S+\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:cr[eé]dito|credito)\s*:\s*[^.!?]{0,220}[.!?]?\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:arxiv\s+doi|doi)\s*:\s*\S+\s*', '', text, flags=re.I)
    text = re.sub(r'^(?:pixabay/cc0\s+)?(?:dom[ií]nio p[uú]blico|public domain)\s*', '', text, flags=re.I)
    text = re.sub(r'^\d{1,2}\s+\d{1,2}\s+(?:CEST|UTC|GMT|EST|EDT|PST|PDT|CET|BST)\b(?:\s+de\s+hoje)?[,:\-\s]*', '', text, flags=re.I)
    text = re.sub(r'^\d{1,2}:\d{2}\s+(?:CEST|UTC|GMT|EST|EDT|PST|PDT|CET|BST)\b(?:\s+de\s+hoje)?[,:\-\s]*', '', text, flags=re.I)
    text = re.sub(r'^[-–—,:;\s]+', '', text)
    return collapse_ws(text)


def _normalize_fallback_fragment_pt(text: str) -> str:
    text = _strip_noise_prefix_pt(_strip_highlight_prefix_pt(text))
    text = smooth_prose(text)
    text = re.sub(r'https?://\S+', ' ', text, flags=re.I)
    text = re.sub(r'\b10\.\d{4,9}/\S+\b', ' ', text, flags=re.I)
    text = re.sub(r'\s*\((?:credit|image|photo).*?\)\s*', ' ', text, flags=re.I)
    text = re.sub(r'os editores destacaram os seguintes atributos,?\s*garantindo a credibil(?:i|í)dade do conte[úu]do\.?', ' ', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text).strip(' \t\n\r-–—,:;')
    return collapse_ws(text)


def _sentence_is_fragment_pt(text: str) -> bool:
    norm = normalize_text(text.rstrip('.!?'))
    words = norm.split()
    if not words:
        return True
    last_word = words[-1]
    if last_word in _BAD_ENDING_TOKENS_PT or len(last_word) == 1:
        return True
    if len(words) < 5:
        return True
    return False


def _take_complete_sentences_pt(text: str, max_sentences: int = 2, max_chars: int = 420) -> str:
    text = _normalize_fallback_fragment_pt(text)
    if not text or _looks_promotional_or_credit_paragraph_pt(text):
        return ''

    sentences = [
        collapse_ws(s) for s in re.split(r'(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9])', text)
        if collapse_ws(s)
    ]
    clean_sentences: list[str] = []
    for sentence in sentences:
        sentence = _normalize_fallback_fragment_pt(sentence)
        if not sentence:
            continue
        if _looks_generic_template_paragraph_pt(sentence) or _looks_promotional_or_credit_paragraph_pt(sentence):
            continue
        if len(sentence) < 28:
            continue
        if len(sentence) > max_chars:
            sentence = truncate(sentence, max_chars)
            sentence = _normalize_fallback_fragment_pt(sentence)
        if _sentence_is_fragment_pt(sentence):
            continue
        sentence = sentence.rstrip(' .;,:')
        if sentence and sentence[0].isalpha():
            sentence = sentence[0].upper() + sentence[1:]
        clean_sentences.append(sentence + '.')
        if len(clean_sentences) >= max_sentences:
            break
    if clean_sentences:
        return ' '.join(clean_sentences)

    trimmed = _normalize_fallback_fragment_pt(text).rstrip(' .;,:')
    if not trimmed:
        return ''
    if len(trimmed) > max_chars:
        trimmed = truncate(trimmed, max_chars)
        trimmed = _normalize_fallback_fragment_pt(trimmed).rstrip(' .;,:')
    if _looks_promotional_or_credit_paragraph_pt(trimmed) or _sentence_is_fragment_pt(trimmed):
        return ''
    if trimmed and trimmed[0].isalpha():
        trimmed = trimmed[0].upper() + trimmed[1:]
    return trimmed.rstrip('.') + '.'


def _safe_sentence_pt(text: str) -> str:
    return _take_complete_sentences_pt(text, max_sentences=1, max_chars=280)


def _build_natural_fallback_body(
    title_pt: str,
    summary_pt: str,
    facts_pt: list[str],
    body_pt: str,
    extra_sentences_pt: Optional[list[str]] = None,
    src_url: str = '',
) -> str:
    source_html = _extract_source_paragraph_html(body_pt) or _source_link_paragraph_html(src_url, 'pt')
    title_norm = normalize_text(_normalize_fallback_fragment_pt(title_pt))
    seen = set()

    def sentence_candidates(values: list[str]) -> list[str]:
        out: list[str] = []
        for value in values:
            if not value:
                continue
            pieces = split_sentences(collapse_ws(strip_html(value))) or [value]
            for piece in pieces:
                cleaned = _safe_sentence_pt(piece)
                if not cleaned:
                    continue
                low = normalize_text(cleaned)
                if low == title_norm:
                    continue
                if any(marker in low for marker in _GENERIC_FACT_MARKERS_PT):
                    continue
                if _looks_generic_template_paragraph_pt(cleaned):
                    continue
                if _looks_promotional_or_credit_paragraph_pt(cleaned):
                    continue
                if low in seen:
                    continue
                seen.add(low)
                out.append(cleaned)
        return out

    ordered_sentences: list[str] = []
    summary_sentence = _take_complete_sentences_pt(summary_pt or '', max_sentences=2, max_chars=420)
    if summary_sentence and not _looks_generic_template_paragraph_pt(summary_sentence):
        ordered_sentences.extend(sentence_candidates([summary_sentence]))

    ordered_sentences.extend(sentence_candidates(facts_pt or []))
    ordered_sentences.extend(sentence_candidates(extra_sentences_pt or []))

    body_paragraphs = _paragraphs_from_html(body_pt)
    for paragraph in body_paragraphs:
        ordered_sentences.extend(sentence_candidates([paragraph]))

    cleaned_sentences: list[str] = []
    sentence_seen = set()
    for sentence in ordered_sentences:
        key = normalize_text(sentence)
        if key in sentence_seen:
            continue
        sentence_seen.add(key)
        cleaned_sentences.append(sentence)
        if len(cleaned_sentences) >= 12:
            break

    if not cleaned_sentences:
        backup = _safe_sentence_pt(summary_pt or title_pt or '')
        if backup:
            cleaned_sentences = [backup]

    paragraphs: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in cleaned_sentences:
        sentence_len = len(sentence)
        if current and (len(current) >= 2 or current_len + 1 + sentence_len > 520):
            paragraph = ' '.join(current)
            if len(collapse_ws(paragraph)) >= 45:
                paragraphs.append(paragraph)
            current = [sentence]
            current_len = sentence_len
        else:
            current.append(sentence)
            current_len = current_len + (1 if current_len else 0) + sentence_len
        if len(paragraphs) >= 5:
            break
    if current and len(paragraphs) < 6:
        paragraph = ' '.join(current)
        if len(collapse_ws(paragraph)) >= 45:
            paragraphs.append(paragraph)

    if len(paragraphs) < 2:
        existing_keys = {normalize_text(p) for p in paragraphs}
        for paragraph in body_paragraphs:
            cleaned = _take_complete_sentences_pt(paragraph, max_sentences=2, max_chars=420)
            if not cleaned:
                continue
            if _looks_generic_template_paragraph_pt(cleaned) or _looks_promotional_or_credit_paragraph_pt(cleaned):
                continue
            key = normalize_text(cleaned)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            paragraphs.append(cleaned)
            if len(paragraphs) >= 4:
                break

    html_parts = [
        f'<p>{html.escape(collapse_ws(paragraph))}</p>'
        for paragraph in paragraphs[:6]
        if len(collapse_ws(paragraph)) >= 45
    ]
    if source_html:
        html_parts.append(source_html)
    return ''.join(html_parts)

def review_portuguese_content(title_pt: str, summary_pt: str, facts_pt: list[str], body_pt: str) -> dict:
    facts_pt = [collapse_ws(f) for f in facts_pt if collapse_ws(f)]
    payload = {
        'title': collapse_ws(title_pt),
        'summary': collapse_ws(summary_pt),
        'facts': facts_pt[:6],
        'body': _gemini_prompt_body(body_pt),
    }
    fallback = {
        'title': payload['title'],
        'summary': payload['summary'],
        'facts': payload['facts'],
        'body': _build_natural_fallback_body(payload['title'], payload['summary'], payload['facts'], body_pt),
    }
    prompt = (
        'Você é um revisor científico e copy editor sênior em português do Brasil. '
        'Sua tarefa é corrigir e melhorar o texto científico fornecido em JSON.\n\n'
        'REGRAS OBRIGATÓRIAS:\n'
        '1. Corrija TODA ortografia, concordância, pontuação, regência e sintaxe.\n'
        '2. Nunca corte frases no meio — toda frase deve terminar com pontuação completa.\n'
        '3. Nunca use travessão (—) nem reticências (...) no texto.\n'
        '4. Nunca use marcadores de IA como "Além disso,", "Em resumo,", "Vale ressaltar que", "É importante notar que", "Certamente", "Claro que".\n'
        '5. Preserve rigor factual: números, nomes próprios, datas, unidades e cautelas científicas.\n'
        '6. Não invente fatos, não adicione opiniões e não remova ressalvas científicas.\n'
        '7. No campo "body": texto corrido em português natural, SEM HTML, com 5 a 8 parágrafos completos separados por "\\n\\n".\n'
        '8. Cada parágrafo deve ter entre 60 e 400 palavras e terminar com ponto final.\n'
        '9. Mantenha "facts" curtos, claros, objetivos e com frase completa.\n'
        '10. Responda SOMENTE em JSON válido com as chaves exatas: title, summary, facts, body.\n\n'
        + json.dumps(payload, ensure_ascii=False)
    )
    reviewed = call_gemini_json('pt_review_bundle', prompt)
    success = isinstance(reviewed, dict)
    # When the call fails or returns an unexpected type, fall back to the original
    # unreviewed content. We'll track whether a review succeeded via the
    # ``success`` flag.
    if not success:
        result_dict = {
            'title': fallback['title'],
            'summary': fallback['summary'],
            'facts': fallback['facts'],
            'body': fallback['body'],
        }
        # Mark that the review fell back to the original content
        result_dict['status'] = 'fallback'
        result_dict['provider'] = 'gemini'
        return result_dict

    title = collapse_ws(str(reviewed.get('title') or payload['title']))
    summary = collapse_ws(str(reviewed.get('summary') or payload['summary']))
    facts = []
    for item in reviewed.get('facts') or payload['facts']:
        cleaned = collapse_ws(str(item))
        if cleaned:
            facts.append(cleaned)
    facts = distinct_facts(facts, 6) or payload['facts']

    body_raw = str(reviewed.get('body') or payload['body'])
    # Split on double newlines provided by the model; fallback to sentence splitting
    body_paragraphs = [collapse_ws(p) for p in re.split(r'\n{2,}', body_raw) if collapse_ws(p)]
    if not body_paragraphs:
        body_paragraphs = [collapse_ws(p) for p in re.split(r'(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ])', payload['body']) if collapse_ws(p)]
    body_html = ''.join(
        f'<p>{html.escape(collapse_ws(paragraph))}</p>'
        for paragraph in body_paragraphs[:8]
        if len(paragraph) >= 45
    ) or body_pt

    # Compose the result dictionary with review status and provider metadata
    result_dict = {
        'title': title or payload['title'],
        'summary': summary or payload['summary'],
        'facts': facts or payload['facts'],
        'body': body_html,
    }
    result_dict['status'] = 'success'
    result_dict['provider'] = 'gemini'
    return result_dict


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


# ── Feed parsers ──────────────────────────────────────────────────────────────

def _clean_xml_bytes(xml_bytes: bytes) -> bytes:
    """Normalise raw feed bytes before passing to ElementTree.

    Handles the most common reasons for 'invalid token' and 'mismatched tag'
    errors in the wild:
      • UTF-8 BOM at the start of the stream
      • Invalid XML control characters (U+0000-U+001F except tab/LF/CR)
      • Windows-1252 / Latin-1 bytes that slip through as UTF-8
    """
    try:
        text = xml_bytes.decode('utf-8-sig', errors='replace')
    except Exception:
        text = xml_bytes.decode('latin-1', errors='replace')
    # Strip XML-illegal control characters (keep \t \n \r)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Some feeds (notably JPL's) embed malformed <content:encoded> tags like
    # ``<content:encoded<![CDATA[...]``, which lack a closing ``>`` after the tag
    # name. This breaks the XML parser with an "invalid token" error. To make
    # these feeds parseable, normalise the opening tag by inserting the missing
    # angle bracket. This replacement is conservative and only affects the
    # malformed pattern; well‑formed tags (``<content:encoded><![CDATA[``) are
    # untouched.
    text = text.replace('<content:encoded<![CDATA[', '<content:encoded><![CDATA[')

    return text.encode('utf-8')


def parse_rss(xml_bytes: bytes, source: SourceConfig) -> list[dict]:
    root = ET.fromstring(_clean_xml_bytes(xml_bytes))
    items = []
    for item in root.findall('.//item'):
        title = strip_html(item.findtext('title', default=''))
        link  = collapse_ws(item.findtext('link', default=''))
        # Some feeds (e.g. Nature) put the canonical URL in <guid> instead of <link>
        if not link:
            guid = collapse_ws(item.findtext('guid', default=''))
            if guid.startswith('http'):
                link = guid
        description_html = item.findtext('description', default='') or ''
        content_html = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', default='') or description_html
        summary = strip_html(description_html or content_html)
        full_text = truncate(strip_html(content_html or description_html), FULL_TEXT_LIMIT)
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
    root = ET.fromstring(_clean_xml_bytes(xml_bytes))
    items = []
    for entry in root.findall('atom:entry', NS):
        title = strip_html(entry.findtext('atom:title', default='', namespaces=NS))
        summary_html = entry.findtext('atom:summary', default='', namespaces=NS) or ''
        content_html = entry.findtext('atom:content', default='', namespaces=NS) or summary_html
        summary = strip_html(summary_html or content_html)
        full_text = truncate(strip_html(content_html or summary_html), FULL_TEXT_LIMIT)
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


# ── Classification & scoring ──────────────────────────────────────────────────

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


def _looks_like_author_profile_item(item: dict) -> bool:
    title = collapse_ws(strip_html(item.get('title') or ''))
    summary = collapse_ws(strip_html(item.get('summary') or ''))
    link = normalize_text(item.get('link') or '')
    haystack = normalize_text(' '.join([title, summary, item.get('link', ''), item.get('source', '')]))
    if not title:
        return False
    profile_url = bool(re.search(r'/(author|authors|people|person|profile|profiles|staff|team|contributor|contributors|biography|bio)/', link))
    bio_markers = (
        'author', 'editor', 'reporter', 'journalist', 'researcher', 'scientist', 'professor',
        'biography', 'biografia', 'profile', 'perfil', 'staff', 'team', 'contributor',
        'written by', 'edited by', 'reviewed by', 'correspondent'
    )
    if _looks_like_person_name(title):
        if profile_url:
            return True
        if len(title.split()) <= 5 and (not summary or len(summary) < 180 or any(marker in haystack for marker in bio_markers)):
            if not any(hint in haystack for hint in SCIENTIFIC_RESULT_HINTS):
                return True
    if profile_url and not any(hint in haystack for hint in SCIENTIFIC_RESULT_HINTS):
        return True
    return False


def _looks_like_service_or_schedule_item(item: dict) -> bool:
    title = collapse_ws(strip_html(item.get('title') or ''))
    low_title = normalize_text(title)
    haystack = normalize_text(' '.join([title, item.get('summary', ''), item.get('link', ''), item.get('source', '')]))
    if not title:
        return False
    if re.search(r'^(this week.?s sky at a glance|sky at a glance|how to follow\b|how to watch\b|watch live\b|nasa invites media\b|media advisory\b)', low_title):
        return True
    if re.search(r'^\d{4} .* schedule\b', low_title):
        return True
    if re.search(r'\b(schedule|agenda|program|programme|calendar|at a glance|media advisory|press advisory|invites media|media are invited)\b', haystack):
        if not any(hint in haystack for hint in SCIENTIFIC_RESULT_HINTS):
            return True
    return False


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
    if _looks_like_author_profile_item(item):
        risk_score += 90
        relevance_score -= 28
        accessibility_score -= 8
    if _looks_like_service_or_schedule_item(item):
        risk_score += 80
        relevance_score -= 22
        accessibility_score -= 6
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
    if item.get('source_type') == 'preprint' and not any(kw in low for kw in BROAD_INTEREST_PREPRINT_HINTS):
        risk_score += 24
        relevance_score -= 12
    if item.get('source_type') == 'preprint' and any(kw in low for kw in BROAD_INTEREST_PREPRINT_HINTS):
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
    if _looks_like_author_profile_item(item):
        return True
    if _looks_like_service_or_schedule_item(item):
        return True
    if profile['overall'] < 58:
        return True
    if len(item['summary']) < 40:
        return True
    if low.startswith('image:'):
        return True
    if _looks_like_person_name(collapse_ws(strip_html(item.get('title') or ''))) and not any(hint in low for hint in SCIENTIFIC_RESULT_HINTS):
        return True
    # Rejeitar posts mais velhos que o limite de idade máxima.
    # Isso evita que matérias de meses atrás ocupem vagas no feed apenas
    # para satisfazer a cota mínima por categoria.
    age_days = (datetime.now(timezone.utc) - item['published']).total_seconds() / 86400
    if age_days > MAX_POST_AGE_DAYS:
        return True
    return False


def is_fresh_item(item: dict) -> bool:
    age_hours = max(0.0, (datetime.now(timezone.utc) - item['published']).total_seconds() / 3600)
    return age_hours <= FRESH_WINDOW_HOURS


def dedupe_and_rank(items: list[dict]) -> list[dict]:
    seen = set()
    per_source: Counter = Counter()
    preprints = 0
    per_category: Counter = Counter()
    ranked = []
    category_order = [
        'Astronomia', 'Cosmologia', 'Astrofísica', 'Exoplanetas',
        'Física', 'Biologia', 'Química', 'Ciências da Terra'
    ]

    decorated = []
    for item in items:
        profile = compute_editorial_profile(item)
        item['editorial_profile'] = profile
        decorated.append(item)

    decorated.sort(
        key=lambda x: (x['editorial_profile']['overall'], x['editorial_profile']['relevance_score'], x['published']),
        reverse=True
    )

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

    # Pull in a minimum quota of truly fresh stories first so the homepage stops feeling stale.
    fresh_candidates = [item for item in decorated if is_fresh_item(item)]
    fresh_candidates.sort(
        key=lambda x: (x['published'], x['editorial_profile']['overall'], x['editorial_profile']['relevance_score']),
        reverse=True
    )
    fresh_taken = 0
    for item in fresh_candidates:
        if fresh_taken >= MIN_FRESH_POSTS or len(ranked) >= MAX_POSTS:
            break
        if can_take(item):
            take(item)
            fresh_taken += 1

    # Guarantee minimum coverage per category
    for category in category_order:
        if MIN_POSTS_PER_CATEGORY <= 0:
            break
        while per_category[category] < MIN_POSTS_PER_CATEGORY:
            filled = False
            for item in decorated:
                if item['editorial_profile']['category'] != category:
                    continue
                if can_take(item):
                    take(item)
                    filled = True
                    break
            if not filled:
                break

    for item in decorated:
        if can_take(item):
            take(item)
        if len(ranked) >= MAX_POSTS:
            break

    return ranked


# ── Sentence extraction ───────────────────────────────────────────────────────


def split_sentences(text: str) -> list[str]:
    text = collapse_ws(strip_html(text))
    if not text:
        return []
    text = re.sub(r'(?<=[a-z0-9])\s*•\s*', '. ', text, flags=re.I)
    parts = re.split(r'(?<=[.!?])\s+|(?<=;)\s+', text)
    out = []
    for part in parts:
        part = collapse_ws(part).strip(' \""\'\'\'')
        if len(part) < 28:
            continue
        if len(part) > 380:
            subparts = re.split(r'(?<=,)\s+(?=[A-Z0-9])', part)
            for sub in subparts:
                sub = collapse_ws(sub)
                if 28 <= len(sub) <= 260:
                    out.append(sub)
            continue
        out.append(part)
    return out


def sentence_score(sentence: str) -> tuple[int, int]:
    low = normalize_text(sentence)
    score = 0
    if re.search(r'\d', sentence):
        score += 4
    if re.search(r'\b(jwst|nasa|esa|jpl|cern|euclid|desi|hubble|rubin|mars|moon|earth|arxiv|eso|nih|noaa|nature|science)\b', low):
        score += 4
    if re.search(r'\b(first|new|detected|measured|observed|analysis|results|reveals|maps|launch|mission|constraints|published|confirmed|survey|spectrum|spectra|atmosphere|dataset|signal)\b', low):
        score += 3
    if re.search(r'\b(using|with|from|based on|derived from|measured by|collected by)\b', low):
        score += 2
    if len(sentence) > 240:
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
        if len(sentence) < 28:
            continue
        scored.append((sentence_score(sentence), sentence))

    scored.sort(reverse=True)
    top = [sentence for _, sentence in scored[:MAX_FACT_SENTENCES]]

    order = {normalize_text(sentence): idx for idx, sentence in enumerate(pool)}
    top.sort(key=lambda s: order.get(normalize_text(s), 10**9))
    return top


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
    text = smooth_prose(text)
    text = re.sub(r'^[A-Z][^:]{0,28}:\s+', '', text)
    return truncate(text, limit)


def build_deck(summary: str, facts: list[str]) -> str:
    def clean(t: str) -> str:
        t = smooth_prose(t)
        t = re.sub(r'^[A-Z][^:]{0,24}:\s+', '', t)
        t = re.sub(r'\s*\(.*?\)', '', t)
        return truncate(t, 240)

    base = clean(summary) if summary else ''
    if len(base) >= 90:
        return base
    for fact in distinct_facts(facts, 2):
        candidate = clean(fact)
        if len(candidate) >= 90:
            return candidate
    return base



# ── Body building — flowing prose, no section headings ───────────────────────

def _lc(s: str) -> str:
    return s[0].lower() + s[1:] if len(s) > 1 else s.lower()


def _strip_agent_prefix(s: str) -> str:
    patterns = [
        r'^(scientists?|researchers?|a team of researchers?|astronomers?|physicists?|biologists?|chemists?)\s+(have|has|report|reports|found|say|says|announce[ds]?|reveal[s]?)\s+',
        r'^(a new study|new research|new work|a new paper|a new analysis)\s+(shows?|finds?|reveals?|reports?|confirms?|suggests?|indicates?)\s+(that\s+)?',
        r'^(according to (new|recent) research[,]?\s*)',
    ]
    for pat in patterns:
        m = re.match(pat, s, flags=re.I)
        if m:
            remainder = s[m.end():].strip()
            if remainder:
                return remainder[0].upper() + remainder[1:] if len(remainder) > 1 else remainder.upper()
    return s


def _cat_field(category: str, lang: str) -> str:
    pt_names = {
        'Astronomia': 'astronomia', 'Cosmologia': 'cosmologia',
        'Astrofísica': 'astrofísica', 'Exoplanetas': 'ciência de exoplanetas',
        'Física': 'física', 'Biologia': 'biologia',
        'Química': 'química', 'Ciências da Terra': 'ciências da Terra',
    }
    en_names = {
        'Astronomia': 'astronomy', 'Cosmologia': 'cosmology',
        'Astrofísica': 'astrophysics', 'Exoplanetas': 'exoplanet science',
        'Física': 'physics', 'Biologia': 'biology',
        'Química': 'chemistry', 'Ciências da Terra': 'Earth science',
    }
    return (pt_names if lang == 'pt' else en_names).get(category, category.lower())


def _fact_clause(text: str, limit: int = 260) -> str:
    text = _normalize_fallback_fragment_pt(text)
    text = re.sub(r'^[A-Z][^:]{0,28}:\s+', '', text)
    text = re.sub(r'\s*\[(.*?)\]\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text or _looks_promotional_or_credit_paragraph_pt(text):
        return ''
    if len(text) <= limit:
        return '' if _sentence_is_fragment_pt(text) else text + ('' if text.endswith('.') else '.')
    cut = text[:limit]
    last_period = max(cut.rfind('.'), cut.rfind('!'), cut.rfind('?'))
    if last_period > limit // 2:
        candidate = text[:last_period + 1].strip()
        return '' if _sentence_is_fragment_pt(candidate) else candidate
    cut = text[:limit].rsplit(' ', 1)[0].rstrip(' .;:,–—')
    if not cut or _sentence_is_fragment_pt(cut):
        return ''
    return cut + '.'


def _fact_bank(facts: list[str], summary: str) -> list[str]:
    bank = []
    if summary:
        bank.append(_fact_clause(summary, 180))
    for fact in facts:
        bank.append(_fact_clause(fact, 180))
    return distinct_facts(bank, 12)


def _clean_fact_sentence(text: str, limit: int = 260) -> str:
    text = _fact_clause(text, limit)
    text = _strip_agent_prefix(text)
    return collapse_ws(text)


def _fact_for_paragraph(text: str, limit: int = 260, lower: bool = False) -> str:
    cleaned = _clean_fact_sentence(text, limit)
    return _lc(cleaned) if lower and cleaned else cleaned


def _join_sentences(sentences: list[str]) -> str:
    parts = [smooth_prose(s).rstrip(' .') for s in sentences if smooth_prose(s)]
    cleaned = []
    for part in parts:
        if not part:
            continue
        if part and part[0].isalpha():
            part = part[0].upper() + part[1:]
        cleaned.append(part)
    if not cleaned:
        return ''
    return '. '.join(cleaned).strip().rstrip('.') + '.'


def _intro_connector(lang: str, source_type: str) -> str:
    if lang == 'en':
        return {
            'preprint': 'The new analysis still awaits peer review, but it already lays out the central claim clearly.',
            'agency': 'The institutional report frames the development in practical terms and ties it to the broader mission or observing effort.',
            'journal': 'The published study gives the result a firmer scientific footing and helps place it inside the wider research landscape.',
        }[source_type]
    return {
        'preprint': 'A análise ainda aguarda revisão por pares, mas já apresenta com clareza o ponto central da história.',
        'agency': 'O relato institucional enquadra o desenvolvimento de forma concreta e o conecta ao esforço mais amplo de observação ou missão.',
        'journal': 'O estudo publicado dá ao resultado um lastro científico mais firme e ajuda a situá-lo no panorama mais amplo da pesquisa.',
    }[source_type]


def _context_bridge(category: str, lang: str) -> str:
    en = {
        'Astronomia': (
            'That matters because astronomy does not advance on single detections. '
            'The field builds confidence by accumulating independent observations across different wavelengths, '
            'instruments and epochs until isolated signals become defensible conclusions. '
            'What looks convincing in one dataset can dissolve when a second instrument looks at the same target, '
            'and what looks marginal can solidify when follow-up campaigns confirm the original reading. '
            'The current standard requires that a result survive this triangulation before the community treats it as settled.'
        ),
        'Cosmologia': (
            'That matters because cosmology operates at the edge of what current instruments can measure, '
            'where systematic errors and model assumptions are never trivial. '
            'Small discrepancies between independent measurements have historically pointed toward missing physics '
            'rather than simple calibration errors, and the ongoing tension in the Hubble constant is a live example '
            'of how a persistent disagreement between methods can reshape the theoretical landscape. '
            'Each new dataset that approaches this territory with independent systematics adds real information to a problem '
            'that has resisted easy resolution for more than a decade.'
        ),
        'Astrofísica': (
            'That matters because astrophysics becomes persuasive only when an observed signal can be tied to a '
            'physically defensible explanation. '
            'Compact objects such as neutron stars and black holes are natural laboratories for extreme physics, '
            'but the distance and complexity of these systems make interpretation difficult without multi-wavelength coverage '
            'and careful modeling. '
            'A detection without a mechanism is only half a result; the other half comes from showing that the signal '
            'fits quantitatively inside a coherent physical picture rather than merely being consistent with a broad family of models.'
        ),
        'Exoplanetas': (
            'That matters because exoplanet science has moved beyond the era of simple discovery into a period of comparative characterization. '
            'With more than five thousand confirmed planets known, the scientifically productive questions now concern '
            'atmospheric composition, internal structure, orbital history and the statistical properties of populations '
            'rather than the existence of individual worlds. '
            'A new detection or spectral measurement is most valuable when it adds a well-constrained data point to those '
            'comparative frameworks, not when it stands alone as an anecdote.'
        ),
        'Física': (
            'That matters because physics only takes a result seriously when the measurement chain remains robust under scrutiny. '
            'Experimental particle physics and precision metrology both operate in regimes where the signal sits '
            'far below the background noise, and where systematic uncertainties can mimic new physics if not controlled rigorously. '
            'The history of the field contains numerous anomalies that generated theoretical excitement before better data '
            'showed them to be artifacts, and it also contains genuine discoveries that were initially dismissed as noise. '
            'The difference is almost always resolved by independent replication with different instruments and different systematics.'
        ),
        'Biologia': (
            'That matters because biology becomes more informative when an observed effect begins to look like a mechanism '
            'rather than an isolated pattern. '
            'The gap between identifying a correlation in biological data and understanding the causal chain that produces it '
            'is routinely underestimated, and the history of biomedical research is populated with associations that collapsed '
            'when the mechanism was sought and not found. '
            'A result that comes with a proposed mechanism, even a partial one, is more useful than a purely descriptive '
            'finding because it generates testable predictions that can narrow the hypothesis space.'
        ),
        'Química': (
            'That matters because chemistry gains force when a claimed structure or process can be described with '
            'enough precision to be reproduced by others. '
            'Synthetic routes, spectroscopic signatures, yield under defined conditions and stability under realistic '
            'operating parameters are the currency of credibility in chemistry, and a result that lacks these details '
            'cannot be evaluated independently. '
            'The distance between a discovery on a laboratory bench and a process that works reliably at scale is '
            'measured in years of optimization, and each step reveals constraints that were invisible at smaller scale.'
        ),
        'Ciências da Terra': (
            'That matters because Earth science becomes stronger when local observations can be placed inside a '
            'broader physical pattern that spans time and geography. '
            'The planet operates as a coupled system in which atmospheric, oceanic, cryospheric and solid-Earth '
            'processes interact across timescales from days to millions of years. '
            'A measurement that captures one variable at one location and one moment has limited interpretive value '
            'until it is embedded in the longer series and wider spatial coverage that allow natural variability to '
            'be separated from forced change.'
        ),
    }
    pt = {
        'Astronomia': (
            'Isso importa porque a astronomia não avança com detecções isoladas. '
            'O campo constrói confiança acumulando observações independentes em diferentes comprimentos de onda, '
            'instrumentos e épocas até que sinais isolados se tornem conclusões defensáveis. '
            'O que parece convincente em um conjunto de dados pode se dissolver quando um segundo instrumento olha '
            'para o mesmo alvo, e o que parece marginal pode se solidificar quando campanhas de acompanhamento '
            'confirmam a leitura original. '
            'O padrão atual exige que um resultado sobreviva a essa triangulação antes de a comunidade tratá-lo como estabelecido.'
        ),
        'Cosmologia': (
            'Isso importa porque a cosmologia opera na fronteira do que os instrumentos atuais conseguem medir, '
            'onde erros sistemáticos e suposições de modelo nunca são triviais. '
            'Pequenas discrepâncias entre medições independentes historicamente apontaram para física ausente '
            'em vez de simples erros de calibração, e a tensão em curso na constante de Hubble é um exemplo vivo '
            'de como um desacordo persistente entre métodos pode remodelar o panorama teórico. '
            'Cada novo conjunto de dados que se aproxima desse território com sistemáticos independentes '
            'adiciona informação real a um problema que resiste a resolução fácil há mais de uma década.'
        ),
        'Astrofísica': (
            'Isso importa porque a astrofísica se torna convincente apenas quando um sinal observado pode ser '
            'ligado a uma explicação física defensável. '
            'Objetos compactos como estrelas de nêutrons e buracos negros são laboratórios naturais para física extrema, '
            'mas a distância e a complexidade desses sistemas tornam a interpretação difícil sem cobertura '
            'em múltiplos comprimentos de onda e modelagem cuidadosa. '
            'Uma detecção sem mecanismo é apenas metade de um resultado; a outra metade vem de mostrar que o sinal '
            'se encaixa quantitativamente dentro de um quadro físico coerente, em vez de ser apenas consistente '
            'com uma ampla família de modelos.'
        ),
        'Exoplanetas': (
            'Isso importa porque a ciência de exoplanetas passou da era das descobertas simples para um período '
            'de caracterização comparativa. '
            'Com mais de cinco mil planetas confirmados conhecidos, as questões cientificamente produtivas agora '
            'dizem respeito à composição atmosférica, estrutura interna, história orbital e propriedades estatísticas '
            'de populações, e não mais à existência de mundos individuais. '
            'Uma nova detecção ou medição espectral é mais valiosa quando adiciona um ponto de dados bem restringido '
            'a esses quadros comparativos, não quando existe isolada como anedota.'
        ),
        'Física': (
            'Isso importa porque a física só leva um resultado a sério quando a cadeia de medição permanece '
            'robusta sob escrutínio. '
            'A física de partículas experimental e a metrologia de precisão operam em regimes onde o sinal '
            'está muito abaixo do ruído de fundo, e onde incertezas sistemáticas podem imitar nova física '
            'se não forem controladas rigorosamente. '
            'A história do campo contém inúmeras anomalias que geraram entusiasmo teórico antes de dados '
            'melhores mostrarem que eram artefatos, e também contém descobertas genuínas inicialmente descartadas como ruído. '
            'A diferença é quase sempre resolvida por replicação independente com instrumentos diferentes e sistemáticos distintos.'
        ),
        'Biologia': (
            'Isso importa porque a biologia se torna mais informativa quando um efeito observado começa a parecer '
            'um mecanismo e não um padrão isolado. '
            'A distância entre identificar uma correlação em dados biológicos e compreender a cadeia causal que a produz '
            'é rotineiramente subestimada, e a história da pesquisa biomédica está repleta de associações que '
            'desmoronaram quando o mecanismo foi buscado e não encontrado. '
            'Um resultado que vem com um mecanismo proposto, mesmo que parcial, é mais útil do que uma descoberta '
            'puramente descritiva porque gera previsões testáveis que podem estreitar o espaço de hipóteses.'
        ),
        'Química': (
            'Isso importa porque a química ganha força quando uma estrutura ou processo alegado pode ser descrito '
            'com precisão suficiente para ser reproduzido por outros. '
            'Rotas sintéticas, assinaturas espectroscópicas, rendimento em condições definidas e estabilidade '
            'em parâmetros operacionais realistas são a moeda de credibilidade na química, e um resultado que '
            'carece desses detalhes não pode ser avaliado de forma independente. '
            'A distância entre uma descoberta em bancada de laboratório e um processo que funciona '
            'confiavelmente em escala é medida em anos de otimização, e cada etapa revela restrições '
            'que eram invisíveis em escala menor.'
        ),
        'Ciências da Terra': (
            'Isso importa porque as ciências da Terra ficam mais fortes quando observações locais podem ser '
            'encaixadas em um padrão físico mais amplo que abrange tempo e geografia. '
            'O planeta opera como um sistema acoplado no qual processos atmosféricos, oceânicos, criosféricos '
            'e da Terra sólida interagem em escalas de tempo de dias a milhões de anos. '
            'Uma medição que captura uma variável em um local e um momento tem valor interpretativo limitado '
            'até ser incorporada nas séries mais longas e na cobertura espacial mais ampla que permitem '
            'separar variabilidade natural de mudança forçada.'
        ),
    }
    d = en if lang == 'en' else pt
    return d.get(category, d['Astronomia'])


def _significance_bridge(category: str, lang: str) -> str:
    en = {
        'Astronomia': (
            'What gives the story weight is not just the object itself, but the way the measurement '
            'trims the range of plausible physical explanations. '
            'Astronomy has accumulated enough cases to know that the most interesting results are rarely '
            'the ones that confirm expectations cleanly; they are the ones that confirm some expectations '
            'while complicating others, or that open a parameter space that previous instruments could not reach. '
            'The scientific community evaluates these contributions by asking whether the new data constrain '
            'a model in a way that older data could not, and whether those constraints survive systematic review.'
        ),
        'Cosmologia': (
            'The relevance goes beyond one dataset because even small shifts in measured parameters can matter '
            'when the field is testing the limits of the standard cosmological model. '
            'The Lambda-CDM framework describes the observable universe with remarkable economy, '
            'but its success rests on two components, dark matter and dark energy, '
            'whose physical nature remains entirely unknown. '
            'Any credible measurement that tightens or loosens the constraints on those components '
            'moves the entire theoretical enterprise forward, regardless of whether the immediate result '
            'looks dramatic on its own terms.'
        ),
        'Astrofísica': (
            'The broader interest lies in turning an observational clue into something that can be '
            'weighed against competing models of the underlying physics. '
            'Astrophysics does not have the luxury of controlled experiments; everything is inferred '
            'from radiation that traveled across cosmic distances under conditions that cannot be reproduced '
            'in a terrestrial laboratory. '
            'This makes the interpretation chain longer and more uncertain than in bench science, '
            'but it also means that a well-constrained measurement of an extreme object carries '
            'theoretical information that no earthbound experiment can provide.'
        ),
        'Exoplanetas': (
            'The broader interest lies in making the target less anecdotal and more comparable '
            'with the rest of the known planetary population. '
            'Population-level questions, such as the frequency of atmospheres around small rocky planets '
            'or the prevalence of water-rich worlds in the habitable zone, require well-characterized '
            'individual data points before statistical patterns become meaningful. '
            'Each new planet with a measured radius, mass and, ideally, atmospheric constraint '
            'is a brick in that larger structure, and the accumulation of bricks eventually '
            'allows theorists to test formation models against real distributions rather than projections.'
        ),
        'Física': (
            'The broader interest lies as much in the method as in the headline number, '
            'because a durable measurement procedure can travel farther than a single result. '
            'When experimental physicists develop a technique that achieves new sensitivity or '
            'controls a previously uncharacterized systematic, that methodological contribution '
            'persists even if the specific measurement is later revised. '
            'This is one reason why precision physics experiments often generate long-term value '
            'that is not immediately visible in the original publication.'
        ),
        'Biologia': (
            'The broader interest lies in whether the reported effect points toward a real mechanism '
            'and not merely a reproducible but unexplained association. '
            'Biology has learned from decades of biomarker failures that correlation, even robust correlation, '
            'is not a substitute for mechanistic understanding. '
            'A pathway that can be traced from molecular interaction to cellular response '
            'to organismal phenotype provides a far stronger foundation for intervention '
            'than a statistical association discovered in a large dataset, '
            'however well the statistics are done.'
        ),
        'Química': (
            'The broader interest lies in whether the claimed property or reaction pathway '
            'can be characterized with enough precision to support replication by other groups. '
            'Chemistry has a replication problem that is less discussed than the one in psychology or medicine, '
            'but it is real: synthetic procedures that work reliably in one laboratory sometimes fail '
            'to transfer, for reasons ranging from impure starting materials to undocumented temperature sensitivities. '
            'A result that comes with full experimental detail and a clear characterization of the product '
            'is far more valuable than one that reports a discovery without the procedural backbone.'
        ),
        'Ciências da Terra': (
            'The broader interest lies in linking the observation to climatic, geophysical '
            'or environmental dynamics that extend well beyond the immediate event or location. '
            'Earth science is unusual in that its most important questions operate on timescales '
            'that no single research career can observe directly, '
            'making the archival record, whether in ice, sediment, rock or satellite data, '
            'as important as any new measurement. '
            'Results that can be embedded in that record, and that either confirm or challenge '
            'the patterns it reveals, carry disproportionate scientific weight.'
        ),
    }
    pt = {
        'Astronomia': (
            'O que dá peso à história não é apenas o objeto em si, mas a maneira como a medição '
            'reduz o espaço das explicações físicas plausíveis. '
            'A astronomia acumulou casos suficientes para saber que os resultados mais interessantes '
            'raramente são os que confirmam expectativas de forma limpa; são os que confirmam algumas '
            'expectativas enquanto complicam outras, ou que abrem um espaço de parâmetros que instrumentos '
            'anteriores não podiam alcançar. '
            'A comunidade científica avalia essas contribuições perguntando se os novos dados restringem '
            'um modelo de uma forma que dados mais antigos não podiam, e se essas restrições '
            'sobrevivem à revisão sistemática.'
        ),
        'Cosmologia': (
            'A relevância vai além de um único conjunto de dados porque até pequenas variações nos parâmetros '
            'medidos podem importar quando o campo testa os limites do modelo cosmológico padrão. '
            'O arcabouço Lambda-CDM descreve o universo observável com notável economia, '
            'mas seu sucesso repousa sobre dois componentes, matéria escura e energia escura, '
            'cuja natureza física permanece completamente desconhecida. '
            'Qualquer medição confiável que aperte ou afrouxa as restrições sobre esses componentes '
            'faz avançar todo o empreendimento teórico, independentemente de o resultado imediato '
            'parecer dramático por si só.'
        ),
        'Astrofísica': (
            'O interesse mais amplo está em transformar uma pista observacional em algo que possa '
            'ser comparado com modelos concorrentes da física subjacente. '
            'A astrofísica não tem o luxo de experimentos controlados; tudo é inferido '
            'a partir de radiação que percorreu distâncias cósmicas sob condições que não podem '
            'ser reproduzidas em laboratório terrestre. '
            'Isso torna a cadeia de interpretação mais longa e incerta do que na ciência de bancada, '
            'mas também significa que uma medição bem restringida de um objeto extremo carrega '
            'informação teórica que nenhum experimento terrestre pode fornecer.'
        ),
        'Exoplanetas': (
            'O interesse mais amplo está em tornar o alvo menos anedótico e mais comparável '
            'com o restante da população planetária conhecida. '
            'Questões em nível de população, como a frequência de atmosferas em torno de planetas '
            'rochosos pequenos ou a prevalência de mundos ricos em água na zona habitável, '
            'exigem pontos de dados individuais bem caracterizados antes que padrões estatísticos '
            'se tornem significativos. '
            'Cada novo planeta com raio, massa e, idealmente, restrição atmosférica medidos '
            'é um tijolo nessa estrutura maior, e o acúmulo de tijolos eventualmente permite '
            'que teóricos testem modelos de formação contra distribuições reais.'
        ),
        'Física': (
            'O interesse mais amplo está tanto no método quanto no número principal, '
            'porque um procedimento de medição duradouro pode viajar mais longe do que um único resultado. '
            'Quando físicos experimentais desenvolvem uma técnica que alcança nova sensibilidade '
            'ou controla um sistemático anteriormente não caracterizado, essa contribuição metodológica '
            'persiste mesmo que a medição específica seja revisada posteriormente. '
            'Essa é uma das razões pelas quais experimentos de física de precisão frequentemente '
            'geram valor de longo prazo que não é imediatamente visível na publicação original.'
        ),
        'Biologia': (
            'O interesse mais amplo está em saber se o efeito relatado aponta para um mecanismo real '
            'e não apenas para uma associação reproduzível mas inexplicada. '
            'A biologia aprendeu com décadas de fracassos de biomarcadores que correlação, '
            'mesmo correlação robusta, não substitui compreensão mecanística. '
            'Uma via que pode ser rastreada da interação molecular à resposta celular '
            'ao fenótipo do organismo fornece uma base muito mais sólida para intervenção '
            'do que uma associação estatística descoberta em um grande conjunto de dados, '
            'por melhores que sejam as estatísticas.'
        ),
        'Química': (
            'O interesse mais amplo está em saber se a propriedade ou rota de reação alegada '
            'pode ser caracterizada com precisão suficiente para sustentar replicação por outros grupos. '
            'A química tem um problema de replicação menos discutido do que o da psicologia ou da medicina, '
            'mas ele é real: procedimentos sintéticos que funcionam confiavelmente em um laboratório '
            'às vezes não se transferem, por razões que vão de materiais de partida impuros '
            'a sensibilidades de temperatura não documentadas. '
            'Um resultado que vem com detalhes experimentais completos e caracterização clara do produto '
            'é muito mais valioso do que um que relata uma descoberta sem o arcabouço procedimental.'
        ),
        'Ciências da Terra': (
            'O interesse mais amplo está em ligar a observação a dinâmicas climáticas, geofísicas '
            'ou ambientais que se estendem muito além do evento ou local imediato. '
            'As ciências da Terra são incomuns porque suas questões mais importantes operam em escalas '
            'de tempo que nenhuma carreira científica pode observar diretamente, '
            'tornando o registro de arquivo, seja em gelo, sedimento, rocha ou dados de satélite, '
            'tão importante quanto qualquer nova medição. '
            'Resultados que podem ser incorporados a esse registro e que confirmam ou desafiam '
            'os padrões que ele revela carregam peso científico desproporcional.'
        ),
    }
    d = en if lang == 'en' else pt
    return d.get(category, d['Astronomia'])


def _evidence_note(source: str, source_type: str, lang: str) -> str:
    if lang == 'en':
        if source_type == 'preprint':
            return (
                'Because this is still a preprint, the result should be read with genuine interest '
                'and proportionate caution. '
                'Peer review is not a guarantee of correctness, but it is a process that forces authors '
                'to respond to technical criticism from specialists who have no stake in a particular outcome. '
                'Preprints that survive that process, often with substantive revisions, emerge with a '
                'stronger evidential base than the version that first appeared. '
                'Until that stage is complete, the responsible reading keeps uncertainty explicitly visible '
                'rather than treating the claims as established findings.'
            )
        if source_type == 'agency':
            return (
                f'Because the account originates with {source}, it functions best as a primary institutional '
                'report that is close to the data and operations, not as independent scientific validation. '
                'Institutional communications are produced by organizations with legitimate interests in '
                'presenting their work in a favorable light, which does not make them unreliable '
                'but does make them partial. '
                'Details that complicate the narrative, including instrument limitations, unexpected failures '
                'and results below projections, tend to be minimized relative to progress messages. '
                'Technical documentation and peer-reviewed publications, where they exist, '
                'provide the complementary layer that institutional releases cannot substitute.'
            )
        return (
            'Because the study has cleared peer review, the evidential footing is stronger than it would '
            'be for a preprint or institutional release, though no published result is beyond revision '
            'when better data or better analysis arrive. '
            'Publication in a peer-reviewed journal signals that independent specialists found the '
            'methodology defensible and the conclusions proportionate to the evidence presented. '
            'It does not signal that the result is final; the scientific record contains many peer-reviewed '
            'papers that were later qualified, partially retracted or superseded by studies with broader samples '
            'or improved controls.'
        )
    if source_type == 'preprint':
        return (
            'Como este trabalho ainda é um preprint, o resultado deve ser lido com interesse genuíno '
            'e cautela proporcional. '
            'A revisão por pares não é uma garantia de correção, mas é um processo que obriga os autores '
            'a responder a críticas técnicas de especialistas que não têm interesse em um resultado particular. '
            'Preprints que sobrevivem a esse processo, muitas vezes com revisões substantivas, emergem com '
            'uma base evidencial mais sólida do que a versão que apareceu pela primeira vez. '
            'Até que essa etapa seja concluída, a leitura responsável mantém a incerteza explicitamente visível '
            'em vez de tratar as afirmações como descobertas estabelecidas.'
        )
    if source_type == 'agency':
        return (
            f'Como o relato se origina de {source}, ele funciona melhor como um relatório institucional primário '
            'próximo dos dados e das operações, não como validação científica independente. '
            'Comunicações institucionais são produzidas por organizações com interesses legítimos em apresentar '
            'seu trabalho de forma favorável, o que não as torna não confiáveis, mas as torna parciais. '
            'Detalhes que complicam a narrativa, incluindo limitações de instrumentos, falhas inesperadas '
            'e resultados abaixo das projeções, tendem a ser minimizados em relação às mensagens de progresso. '
            'Documentação técnica e publicações revisadas por pares, quando existem, '
            'fornecem a camada complementar que releases institucionais não podem substituir.'
        )
    return (
        'Como o estudo passou pela revisão por pares, o lastro evidencial é mais sólido do que seria '
        'para um preprint ou comunicado institucional, embora nenhum resultado publicado esteja imune '
        'a revisão quando chegam dados melhores ou análises mais rigorosas. '
        'A publicação em periódico revisado por pares sinaliza que especialistas independentes '
        'consideraram a metodologia defensável e as conclusões proporcionais à evidência apresentada. '
        'Isso não sinaliza que o resultado é definitivo; o registro científico contém muitos artigos '
        'revisados por pares que foram posteriormente qualificados, parcialmente retratados '
        'ou superados por estudos com amostras mais amplas ou controles aprimorados.'
    )


def _closing_line(category: str, source_type: str, lang: str) -> str:
    en = {
        'Astronomia': (
            'The next step is to see whether other instruments and other wavelengths tell the same story. '
            'Campaigns with JWST, the VLT, the forthcoming Extremely Large Telescopes and radio arrays '
            'will provide the spectral coverage and spatial resolution needed to move from detection to '
            'physical characterization. '
            'The timeline for that kind of confirmation is typically measured in years, '
            'not months, which is worth keeping in mind when reading the current result.'
        ),
        'Cosmologia': (
            'The next step is to see whether the effect survives when independent surveys, '
            'different calibration strategies and tighter control of systematic uncertainties '
            'enter the picture. '
            'Programmes such as Euclid, DESI and the Rubin Observatory will deliver datasets '
            'over the next several years that cover the same parameter space with largely independent methods. '
            'If the current signal persists through those tests, its theoretical implications will '
            'become impossible to set aside.'
        ),
        'Astrofísica': (
            'The next step is to see whether independent datasets and physical modeling converge '
            'on the same interpretation. '
            'Multi-wavelength follow-up, combining X-ray, radio and optical data where possible, '
            'is typically what separates a compelling detection from a robust physical characterization. '
            'In high-energy astrophysics, results that initially looked definitive have been revised '
            'when data from a second messenger arrived; the current result should be read '
            'with that history in mind.'
        ),
        'Exoplanetas': (
            'The next step is to improve independent constraints on the mass, radius, '
            'atmospheric composition and orbital dynamics of the target. '
            'Transmission spectroscopy with JWST, radial velocity campaigns with high-resolution '
            'ground-based spectrographs and phase-curve measurements from space photometry '
            'represent the observational toolkit that can move characterization from plausible to robust. '
            'That convergence of techniques is the standard the community now expects '
            'before a planetary atmosphere result is treated as confirmed.'
        ),
        'Física': (
            'The next step is more measurement, tighter systematic control and scrutiny '
            'from groups whose experimental setups are genuinely independent. '
            'In experimental particle physics and precision metrology, the threshold for a discovery claim '
            'is a five-sigma excess surviving multiple analyses; an intriguing signal at lower significance '
            'is a reason to run more experiments, not a reason to revise the textbooks. '
            'Next-generation experiments currently under construction or commissioning will revisit '
            'several of the open questions that give the current result its context.'
        ),
        'Biologia': (
            'The next step is to test whether the effect repeats across different methods, '
            'cell types, model organisms and experimental conditions. '
            'Reproducibility is the first test, but mechanistic dissection is the second, '
            'and a result that passes both has a substantially better chance of translating '
            'into something clinically or biotechnologically useful. '
            'The path from a laboratory finding to an applied outcome typically takes a decade '
            'or more, and most findings do not complete it; the current result sits '
            'at the beginning of that process.'
        ),
        'Química': (
            'The next step is to see whether independent groups working with orthogonal techniques '
            'reach compatible conclusions, and whether the result scales '
            'beyond the conditions used in the original study. '
            'Chemical discoveries that matter tend to be ones whose key properties '
            'can be measured by multiple spectroscopic, crystallographic or computational methods '
            'that are unlikely to share the same blind spots. '
            'Scalability, cost and long-term stability under realistic operating conditions '
            'are additional filters that come into play before any practical application becomes viable.'
        ),
        'Ciências da Terra': (
            'The next step is to place the result inside longer time series '
            'and to compare it with independent instruments and independent sites. '
            'Earth system observations gain most of their interpretive power from network density '
            'and temporal depth, not from any single measurement however precise. '
            'Model simulations that assimilate the new data will help clarify whether the observation '
            'fits comfortably within known natural variability or represents a shift '
            'that existing models do not reproduce.'
        ),
    }
    pt = {
        'Astronomia': (
            'O próximo passo é verificar se outros instrumentos e outros comprimentos de onda '
            'contam a mesma história. '
            'Campanhas com o JWST, o VLT, os futuros Telescópios Extremamente Grandes e arranjos de rádio '
            'fornecerão a cobertura espectral e a resolução espacial necessárias para passar da detecção '
            'à caracterização física. '
            'O cronograma para esse tipo de confirmação é tipicamente medido em anos, '
            'não meses, o que vale ter em mente ao ler o resultado atual.'
        ),
        'Cosmologia': (
            'O próximo passo é saber se o efeito resiste quando levantamentos independentes, '
            'diferentes estratégias de calibração e controle mais rigoroso das incertezas '
            'sistemáticas entram em cena. '
            'Programas como Euclid, DESI e o Observatório Rubin fornecerão conjuntos de dados '
            'nos próximos anos que cobrem o mesmo espaço de parâmetros com métodos em grande parte independentes. '
            'Se o sinal atual persistir através desses testes, suas implicações teóricas '
            'se tornarão impossíveis de ignorar.'
        ),
        'Astrofísica': (
            'O próximo passo é verificar se conjuntos de dados independentes e modelagem física '
            'convergem para a mesma interpretação. '
            'O acompanhamento em múltiplos comprimentos de onda, combinando dados de raios X, '
            'rádio e óptico onde possível, é tipicamente o que separa uma detecção convincente '
            'de uma caracterização física robusta. '
            'Na astrofísica de alta energia, resultados que inicialmente pareciam definitivos '
            'foram revisados quando dados de um segundo mensageiro chegaram; '
            'o resultado atual deve ser lido com essa história em mente.'
        ),
        'Exoplanetas': (
            'O próximo passo é melhorar as restrições independentes sobre massa, raio, '
            'composição atmosférica e dinâmica orbital do alvo. '
            'Espectroscopia de transmissão com o JWST, campanhas de velocidade radial com espectrógrafos '
            'de alta resolução em solo e medições de curva de fase da fotometria espacial '
            'representam o conjunto de ferramentas observacionais que pode mover a caracterização '
            'de plausível para robusta. '
            'Essa convergência de técnicas é o padrão que a comunidade agora espera '
            'antes de um resultado de atmosfera planetária ser tratado como confirmado.'
        ),
        'Física': (
            'O próximo passo é mais medição, controle sistemático mais rigoroso e escrutínio '
            'de grupos cujas configurações experimentais são genuinamente independentes. '
            'Em física de partículas experimental e metrologia de precisão, o limiar para uma afirmação '
            'de descoberta é um excesso de cinco sigma sobrevivendo a múltiplas análises; '
            'um sinal intrigante em significância menor é razão para executar mais experimentos, '
            'não para revisar os livros-texto. '
            'Experimentos de próxima geração atualmente em construção ou comissionamento '
            'revisitarão várias das questões abertas que dão ao resultado atual seu contexto.'
        ),
        'Biologia': (
            'O próximo passo é testar se o efeito se repete em diferentes métodos, '
            'tipos celulares, organismos modelo e condições experimentais. '
            'A reprodutibilidade é o primeiro teste, mas a dissecção mecanística é o segundo, '
            'e um resultado que passa em ambos tem uma chance substancialmente melhor de se traduzir '
            'em algo clinicamente ou biotecnologicamente útil. '
            'O caminho de uma descoberta laboratorial para um resultado aplicado tipicamente leva '
            'uma década ou mais, e a maioria das descobertas não o completa; '
            'o resultado atual está no início desse processo.'
        ),
        'Química': (
            'O próximo passo é verificar se grupos independentes trabalhando com técnicas ortogonais '
            'chegam a conclusões compatíveis e se o resultado escala '
            'além das condições usadas no estudo original. '
            'Descobertas químicas que importam tendem a ser aquelas cujas propriedades principais '
            'podem ser medidas por múltiplos métodos espectroscópicos, cristalográficos ou computacionais '
            'que provavelmente não compartilham os mesmos pontos cegos. '
            'Escalabilidade, custo e estabilidade de longo prazo sob condições operacionais realistas '
            'são filtros adicionais que entram em jogo antes que qualquer aplicação prática se torne viável.'
        ),
        'Ciências da Terra': (
            'O próximo passo é situar o resultado em séries temporais mais longas '
            'e compará-lo com instrumentos independentes e locais independentes. '
            'Observações do sistema terrestre obtêm a maior parte de seu poder interpretativo '
            'da densidade da rede e da profundidade temporal, não de qualquer medição única '
            'por mais precisa que seja. '
            'Simulações de modelos que assimilam os novos dados ajudarão a esclarecer se a observação '
            'se encaixa confortavelmente dentro da variabilidade natural conhecida ou representa '
            'uma mudança que os modelos existentes não reproduzem.'
        ),
    }
    d = en if lang == 'en' else pt
    base = d.get(category, d['Astronomia'])
    if source_type == 'preprint':
        addon = (
            ' Until peer review and independent follow-up address those open questions, '
            'skepticism is not a failure of appreciation for the work; it is part of how science decides what to keep.'
            if lang == 'en' else
            ' Até que a revisão por pares e a verificação independente respondam a essas questões abertas, '
            'o ceticismo não é uma falha em apreciar o trabalho; é parte de como a ciência decide o que manter.'
        )
        return base + addon
    return base


def build_body(title: str, summary: str, facts: list[str], category: str, source: str,
               source_type: str, lang: str, src_url: str) -> str:
    useful = _fact_bank(facts, summary)
    lead = _clean_fact_sentence(summary or title, 360)
    detail_bank = distinct_facts([_clean_fact_sentence(f, 260) for f in useful[1:]], 10)

    paragraphs = []

    # P1: Abertura — lede + conector de fonte
    intro = _join_sentences([
        lead,
        _intro_connector(lang, source_type),
    ])
    if intro:
        paragraphs.append(intro)

    # P2: Contexto + 2 primeiros fatos de detalhe
    if detail_bank:
        # Get the contextual bridge and vary its introductory phrase to avoid repetitious
        # openings like "Isso importa porque" / "That matters because". We replace the
        # introductory segment with one drawn from a small pool of alternatives to
        # produce more natural variation across articles.
        bridge = _context_bridge(category, lang)
        def _vary_intro(text: str, lang: str) -> str:
            """Substitui a abertura fixa da ponte de contexto por um sinônimo
            escolhido deterministicamente via hash do título do artigo,
            evitando repetição sem depender de random."""
            synonyms_pt = [
                'Isso importa porque',
                'Isso é relevante porque',
                'É importante porque',
                'Importa pois',
                'A relevância está em que',
            ]
            synonyms_en = [
                'That matters because',
                'This matters because',
                'It is relevant because',
                'It matters because',
                'The significance lies in',
            ]
            if lang == 'pt':
                target = 'Isso importa porque'
                synonyms = synonyms_pt
            else:
                target = 'That matters because'
                synonyms = synonyms_en
            if text.startswith(target):
                seed = f'{title}|{lang}'
                replacement = stable_pick(synonyms, seed)
                return replacement + text[len(target):]
            return text
        varied_bridge = _vary_intro(bridge, lang)
        p2_bits = [varied_bridge]
        p2_bits.append(_fact_for_paragraph(detail_bank[0], 260))
        if len(detail_bank) > 1:
            p2_bits.append(_fact_for_paragraph(detail_bank[1], 260))
        paragraphs.append(_join_sentences(p2_bits))

    # P3 e P4: Blocos de fatos adicionais (pares)
    remaining = detail_bank[2:8]
    for i in range(0, len(remaining), 2):
        chunk = remaining[i:i + 2]
        if not chunk:
            continue
        sentences = [_fact_for_paragraph(chunk[0], 260)]
        if len(chunk) > 1:
            sentences.append(_fact_for_paragraph(chunk[1], 260))
        paragraphs.append(_join_sentences(sentences))

    # P5: Significado para o campo
    sig = _significance_bridge(category, lang)
    if sig:
        paragraphs.append(sig)

    # P6: Fatos finais restantes se existirem
    tail = detail_bank[8:]
    if tail:
        tail_sentences = [_fact_for_paragraph(t, 200) for t in tail[:3]]
        paragraphs.append(_join_sentences(tail_sentences))

    # P7: Nota sobre qualidade evidencial da fonte
    paragraphs.append(_evidence_note(source, source_type, lang))

    # P8: Encerramento — próximos passos
    paragraphs.append(_closing_line(category, source_type, lang))

    parts = []
    seen = set()
    for paragraph in paragraphs:
        cleaned = collapse_ws(paragraph)
        if not cleaned or len(cleaned) <= 45:
            continue
        key = normalize_text(cleaned)
        if key in seen:
            continue
        seen.add(key)
        parts.append(f'<p>{html.escape(cleaned)}</p>')

    if src_url:
        label = 'Fonte' if lang == 'pt' else 'Source'
        parts.append(
            f'<p class="art-source"><a href="{html.escape(src_url)}" '
            f'target="_blank" rel="noopener noreferrer">{label}</a></p>'
        )

    return ''.join(parts)


def build_highlights(title: str, summary: str, facts: list[str], source_type: str, lang: str) -> list[str]:
    useful = distinct_facts(facts, 2)
    caution_pt = {
        'preprint': 'Resultado ainda sem revisão por pares.',
        'agency': 'Origem institucional: distinguir anúncio de evidência.',
        'journal': 'Material com lastro científico publicado.',
        'news': 'Cobertura jornalística: verificar documentação técnica primária.',
    }
    caution_en = {
        'preprint': 'Result not yet peer reviewed.',
        'agency': 'Institutional origin: separate announcement from evidence.',
        'journal': 'Material with published scientific backing.',
        'news': 'Science reporting: verify primary technical documentation.',
    }
    if lang == 'pt':
        bullets = [f'Ponto central: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Dado-chave: {trimmed_fact(useful[0], 145)}')
        bullets.append(caution_pt.get(source_type, caution_pt['news']))
    else:
        bullets = [f'Core point: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Key detail: {trimmed_fact(useful[0], 145)}')
        bullets.append(caution_en.get(source_type, caution_en['news']))
    return bullets[:3]

# ── Image selection ───────────────────────────────────────────────────────────

def choose_post_image(item: dict, category: str) -> str:
    # Prioridade 1: imagem da página original (og:image / twitter:image)
    # Essas são sempre de alta resolução e otimizadas para compartilhamento.
    # A imagem do feed RSS é frequentemente uma miniatura de baixa resolução
    # que fica borrada quando esticada para cobrir a capa do artigo.
    if item.get('source_type') != 'preprint':
        page_img = fetch_page_image(item.get('link', ''))
        if page_img and image_url_looks_good(page_img):
            return page_img

    # Prioridade 2: imagem do feed RSS (fallback — pode ser baixa resolução)
    feed_img = clean_image_url(item.get('feed_img') or '')
    if feed_img and image_url_looks_good(feed_img):
        return feed_img

    # Prioridade 3: imagem temática baseada no título/categoria
    return infer_thematic_image(item.get('title', ''), item.get('summary', ''), item.get('source', ''), category)


# ── Post assembly ─────────────────────────────────────────────────────────────

def to_post(item: dict, idx: int, regular_rank: int) -> dict:
    profile = item.get('editorial_profile') or compute_editorial_profile(item)
    category = profile['category']
    src_url = item['link']

    facts_en = gather_fact_sentences(item)
    title_en = collapse_ws(item['title'])
    summary_en = build_deck(item['summary'], facts_en)
    highlights_en = build_highlights(title_en, summary_en, facts_en, item['source_type'], 'en')
    body_en = build_body(title_en, summary_en, facts_en, category, item['source'], item['source_type'], 'en', src_url)

    title_pt_raw = translate_text(title_en, 'pt')
    summary_pt_raw = translate_text(summary_en, 'pt')
    facts_pt_raw = [translate_text(fact, 'pt') for fact in facts_en[:6]]
    extra_story_pt = [translate_text(fact, 'pt') for fact in facts_en[6:12]]
    body_pt_seed = build_body(title_pt_raw, summary_pt_raw, facts_pt_raw, category, item['source'], item['source_type'], 'pt', src_url)
    body_pt_raw = (
        _build_natural_fallback_body(title_pt_raw, summary_pt_raw, facts_pt_raw, '', extra_story_pt, src_url)
        or _build_natural_fallback_body(title_pt_raw, summary_pt_raw, facts_pt_raw, body_pt_seed, extra_story_pt, src_url)
        or body_pt_seed
    )

    # A revisão Gemini é feita em lote em main() após todos os posts serem montados.
    # Aqui guardamos o conteúdo bruto e marcamos como 'pending'.
    title_pt   = title_pt_raw
    summary_pt = summary_pt_raw
    facts_pt   = facts_pt_raw
    body_pt    = body_pt_raw
    review_status  = 'pending'
    review_provider = 'gemini'

    highlights_pt = build_highlights(title_pt, summary_pt, facts_pt, item['source_type'], 'pt')

    dt = item['published']
    slug = slugify(title_en)
    canonical = article_dynamic_url(slug, 'pt')
    canonical_en = article_dynamic_url(slug, 'en')
    share_url = article_static_url(slug, 'pt')
    share_url_en = article_static_url(slug, 'en')
    image = choose_post_image(item, category)
    inline_images = extract_inline_images(src_url, primary_image=image)
    video = extract_page_video(src_url)
    audio = extract_page_audio(src_url)
    is_featured = (
        item['source_type'] != 'preprint'
        and regular_rank < 3
        and profile['band'] in ('flagship', 'high')
        and is_fresh_item(item)   # featured só para posts frescos (< 120h)
    )
    is_trending = (
        item['source_type'] != 'preprint'
        and regular_rank < 8      # janela um pouco maior para garantir cobertura
        and is_fresh_item(item)   # trending só para posts frescos
    )
    evidence_key = profile['evidence_key']
    editorial_band = profile['band']

    keywords_pt = unique_keep_order(
        [category, item['source'], 'Cosmos Week'] +
        [frag.strip() for frag in re.split(r'[,;:\-]', title_pt) if len(frag.strip()) > 3]
    )[:8]
    keywords_en = [
        translate_text(kw, 'en') if kw not in (item['source'], 'Cosmos Week') else kw
        for kw in keywords_pt
    ]
    domain = source_domain(src_url)

    return {
        'id': idx + 1,
        'slug': slug,
        'cat': category,
        'catCls': cat_cls(category),
        'img': image,
        'inline_images': inline_images,
        'video': video,
        'audio': audio,
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
        'evidenceLabel': EVIDENCE_LABELS[evidence_key]['pt'],
        'evidenceLabel_pt': EVIDENCE_LABELS[evidence_key]['pt'],
        'evidenceLabel_en': EVIDENCE_LABELS[evidence_key]['en'],
        'editorialBand': editorial_band,
        'editorialBandLabel': EDITORIAL_BANDS[editorial_band]['pt'],
        'editorialBandLabel_pt': EDITORIAL_BANDS[editorial_band]['pt'],
        'editorialBandLabel_en': EDITORIAL_BANDS[editorial_band]['en'],
        'keywords': keywords_pt,
        'keywords_pt': keywords_pt,
        'keywords_en': keywords_en,
        'srcUrl': src_url,
        'realUrl': canonical,
        'realUrl_pt': canonical,
        'realUrl_en': canonical_en,
        'shareUrl': share_url,
        'shareUrl_pt': share_url,
        'shareUrl_en': share_url_en,
        'canonicalUrl': share_url,
        'canonicalUrl_pt': share_url,
        'canonicalUrl_en': canonical_en,
        'defaultLanguage': 'pt-BR',
        'availableLanguages': ['pt-BR', 'en-US'],
        'featured': is_featured,
        'trending': is_trending,
        'isPreprint': item['source_type'] == 'preprint',
        'geminiReviewed': review_status == 'success',
        'geminiModel': GEMINI_MODEL if GEMINI_API_KEY else '',
        # Review tracking: record whether the Portuguese content underwent AI review or fell back,
        # along with the provider used. These fields allow downstream consumers to audit
        # editorial quality and differentiate between machine‑reviewed and unreviewed text.
        'reviewStatus': review_status,
        'reviewProvider': review_provider,
        'score': profile['overall'],
        'scoreBreakdown': {
            'source': profile['source_score'],
            'evidence': profile['evidence_score'],
            'relevance': profile['relevance_score'],
            'accessibility': profile['accessibility_score'],
            'novelty': profile['novelty_score'],
        },
    }


def strip_tags_for_meta(html_text: str) -> str:
    return collapse_ws(strip_html(html_text or ''))

def html_escape_attr(value: str) -> str:
    return html.escape(value or '', quote=True)

def article_static_url(slug: str, lang: str = 'pt') -> str:
    safe_slug = urllib.parse.quote(collapse_ws(slug or '').strip(), safe='')
    if not safe_slug:
        return SITE_URL
    if lang == 'en':
        return urllib.parse.urljoin(SITE_URL, f'en/news/{safe_slug}/')
    return urllib.parse.urljoin(SITE_URL, f'noticia/{safe_slug}/')


def article_dynamic_url(slug: str, lang: str = 'pt') -> str:
    safe_slug = urllib.parse.quote(collapse_ws(slug or '').strip(), safe='')
    if not safe_slug:
        return f'{SITE_URL}?lang=en' if lang == 'en' else SITE_URL
    suffix = f'?article={safe_slug}'
    if lang == 'en':
        suffix += '&lang=en'
    return f'{SITE_URL}{suffix}'


def article_meta_description(post: dict, lang: str = 'pt', limit: int = 180) -> str:
    body_field = 'body_en' if lang == 'en' else 'body_pt'
    title_field = 'title_en' if lang == 'en' else 'title_pt'
    candidate_fields = [
        post.get('excerpt_en') if lang == 'en' else post.get('excerpt_pt'),
        post.get('excerpt'),
        post.get('sub_en') if lang == 'en' else post.get('sub_pt'),
        post.get('sub'),
        first_summary_from_body_html(post.get(body_field) or '', lang=lang),
        post.get(title_field),
        post.get('title'),
    ]
    title_fallback = sanitize_plain_text(post.get(title_field) or post.get('title') or '')
    for idx, candidate in enumerate(candidate_fields):
        cleaned = sanitize_plain_text(strip_tags_for_meta(candidate or ''))
        if not cleaned:
            continue
        if len(cleaned) < 40 and idx < len(candidate_fields) - 2:
            continue
        if summary_looks_broken(cleaned) and cleaned != title_fallback:
            continue
        return truncate(cleaned, limit)
    return truncate(SITE_DESCRIPTION_EN if lang == 'en' else SITE_DESCRIPTION_PT, limit)


def article_primary_image(post: dict) -> str:
    primary = clean_image_url(post.get('img') or '')
    if primary:
        return primary
    for item in (post.get('inline_images') or []):
        if not isinstance(item, dict):
            continue
        src = clean_image_url(item.get('src') or '')
        if src:
            return src
    return urllib.parse.urljoin(SITE_URL, 'assets/og-default.jpg')


def article_primary_alt(post: dict, lang: str = 'pt') -> str:
    if lang == 'en':
        candidates = [post.get('title_en'), post.get('imageAlt_en'), post.get('imageAlt'), post.get('title')]
    else:
        candidates = [post.get('title_pt'), post.get('imageAlt_pt'), post.get('imageAlt'), post.get('title')]
    for candidate in candidates:
        cleaned = sanitize_plain_text(candidate or '')
        if cleaned:
            return cleaned
    return SITE_NAME


def article_json_ld(
    post: dict,
    lang: str,
    canonical_url: str,
    home_url: str,
    alternate_url: str,
    title: str,
    description: str,
    image_url: str,
    author_name: str,
    section_label: str,
    keywords: list[str],
    body_text: str,
    source_name: str,
    source_url: str,
) -> str:
    lang_code = 'en-US' if lang == 'en' else 'pt-BR'
    breadcrumb_home = 'Home' if lang == 'en' else 'Início'
    schema_graph = [
        {
            '@context': 'https://schema.org',
            '@type': 'NewsMediaOrganization',
            '@id': f'{SITE_URL}#organization',
            'name': SITE_NAME,
            'url': SITE_URL,
            'logo': {
                '@type': 'ImageObject',
                'url': urllib.parse.urljoin(SITE_URL, 'assets/og-default.jpg')
            }
        },
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': breadcrumb_home, 'item': home_url},
                {'@type': 'ListItem', 'position': 2, 'name': section_label, 'item': home_url},
                {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canonical_url},
            ]
        },
        {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            '@id': canonical_url,
            'url': canonical_url,
            'name': title,
            'description': description,
            'inLanguage': lang_code,
            'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': home_url},
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': image_url},
            'about': [{'@type': 'Thing', 'name': key} for key in keywords[:8]],
            'hasPart': [{'@type': 'WebPage', 'url': alternate_url, 'inLanguage': 'pt-BR' if lang == 'en' else 'en-US'}],
        },
        {
            '@context': 'https://schema.org',
            '@type': 'NewsArticle',
            'headline': title,
            'description': description,
            'image': [image_url],
            'thumbnailUrl': image_url,
            'datePublished': post.get('publishedIso') or '',
            'dateModified': post.get('lastModifiedIso') or post.get('publishedIso') or '',
            'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical_url},
            'url': canonical_url,
            'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': home_url},
            'publisher': {
                '@type': 'Organization',
                'name': SITE_NAME,
                'url': SITE_URL,
                'logo': {'@type': 'ImageObject', 'url': urllib.parse.urljoin(SITE_URL, 'assets/og-default.jpg')}
            },
            'author': [{'@type': 'Organization', 'name': author_name}],
            'articleSection': section_label,
            'keywords': keywords,
            'isAccessibleForFree': True,
            'inLanguage': lang_code,
            'about': [{'@type': 'Thing', 'name': key} for key in keywords[:8]],
            'articleBody': body_text[:8000],
        }
    ]
    if source_url:
        schema_graph[-1]['isBasedOn'] = source_url
        schema_graph[-1]['citation'] = [{'@type': 'CreativeWork', 'name': source_name or source_url, 'url': source_url}]
    return json.dumps(schema_graph, ensure_ascii=False)



def render_static_article_page(post: dict, lang: str = 'pt') -> str:
    is_en = lang == 'en'
    labels = {
        'html_lang': 'en-US' if is_en else 'pt-BR',
        'locale': 'en_US' if is_en else 'pt_BR',
        'alt_locale': 'pt_BR' if is_en else 'en_US',
        'author': 'Cosmos Week Editorial Desk' if is_en else 'Redação do Cosmos Week',
        'author_meta': 'By Cosmos Week Editorial Desk' if is_en else 'Por Redação do Cosmos Week',
        'back': 'Back to Cosmos Week' if is_en else 'Voltar ao Cosmos Week',
        'home': 'Open homepage' if is_en else 'Abrir homepage',
        'dynamic': 'Open live edition' if is_en else 'Abrir versão dinâmica',
        'original': 'Read original source' if is_en else 'Ler fonte original',
        'highlights': 'Key points' if is_en else 'Pontos-chave',
        'source': 'Original source' if is_en else 'Fonte original',
        'context': 'Editorial context' if is_en else 'Contexto editorial',
        'language': 'English edition' if is_en else 'Edição em português',
        'other_language': 'Read in Portuguese' if is_en else 'Read in English',
        'published': 'Published' if is_en else 'Publicado',
        'updated': 'Updated' if is_en else 'Atualizado',
        'home_url': f'{SITE_URL}?lang=en' if is_en else SITE_URL,
        'section': (_cat_field(post.get('cat') or ('Science' if is_en else 'Ciência'), 'en').capitalize() if is_en else sanitize_plain_text(post.get('cat') or 'Ciência')),
        'breadcrumbs_home': 'Home' if is_en else 'Início',
        'breadcrumbs_news': 'News' if is_en else 'Notícias',
        'editorial_header': 'Editorial header' if is_en else 'Cabeçalho editorial',
        'coverage_type': 'Coverage type' if is_en else 'Tipo de cobertura',
        'evidence_level': 'Evidence level' if is_en else 'Nível de evidência',
        'editorial_signature': 'Editorial signature' if is_en else 'Assinatura editorial',
        'source_analysis': 'Source and framing' if is_en else 'Fonte e enquadramento',
        'source_analysis_text': 'This box tells the reader what kind of source originated the story and how strongly the result should be interpreted.' if is_en else 'Fonte que originou a matéria e a interpretação do resultado.',
        'tools': 'Story tools' if is_en else 'Ferramentas da matéria',
        'copy': 'Copy article link' if is_en else 'Copiar link da matéria',
        'share': 'Share article' if is_en else 'Compartilhar matéria',
        'copied': 'Link copied' if is_en else 'Link copiado',
        'copy_fail': 'Copy failed' if is_en else 'Falha ao copiar',
        'standards': 'Editorial standards' if is_en else 'Padrões editoriais',
        'standards_blurb': 'How Cosmos Week labels sources, evidence levels and provisional claims.' if is_en else 'Como o Cosmos Week rotula fontes, níveis de evidência e resultados provisórios.',
        'related': 'Related reading' if is_en else 'Leitura relacionada',
        'related_empty': 'More related stories will appear here as the archive expands.' if is_en else 'Mais leituras relacionadas aparecerão aqui conforme o arquivo crescer.',
        'body_label': 'Full story' if is_en else 'Texto completo',
        'institutional_note': 'Original source cited and editorially framed by Cosmos Week.' if is_en else 'Fonte original citada e enquadrada editorialmente pelo Cosmos Week.',
        'standards_cta': 'Read standards page' if is_en else 'Ler página de padrões',
        'open_source_cta': 'Open source' if is_en else 'Abrir fonte',
        'live_edition_note': 'Dynamic version keeps live navigation and the current homepage context.' if is_en else 'A versão dinâmica mantém navegação viva e o contexto mais recente da homepage.',
        'read_time': 'Read time' if is_en else 'Leitura',
    }

    slug = collapse_ws(str(post.get('slug') or ''))
    canonical_url = article_static_url(slug, 'en' if is_en else 'pt')
    alternate_url = article_static_url(slug, 'pt' if is_en else 'en')
    dynamic_url = article_dynamic_url(slug, 'en' if is_en else 'pt')
    standards_url = urllib.parse.urljoin(SITE_URL, 'en/standards/' if is_en else 'padroes/')
    news_url = urllib.parse.urljoin(SITE_URL, 'en/' if is_en else '')
    title_value = post.get('title_en') if is_en else post.get('title_pt')
    title_raw = collapse_ws(title_value or post.get('title') or SITE_NAME)
    description_raw = article_meta_description(post, 'en' if is_en else 'pt')
    image_raw = article_primary_image(post)
    image_alt = article_primary_alt(post, 'en' if is_en else 'pt')
    published_raw = post.get('publishedIso') or ''
    modified_raw = post.get('lastModifiedIso') or post.get('publishedIso') or ''
    date_raw = collapse_ws((post.get('date_en') if is_en else post.get('date_pt')) or post.get('date') or '')
    time_raw = collapse_ws((post.get('time_en') if is_en else post.get('time_pt')) or post.get('time') or '')
    read_raw = collapse_ws((post.get('read_en') if is_en else post.get('read_pt')) or post.get('read') or '')
    source_raw = collapse_ws(post.get('source') or '')
    source_url = collapse_ws(post.get('srcUrl') or '')
    source_note = sanitize_plain_text((post.get('sourceNote_en') if is_en else post.get('sourceNote_pt')) or post.get('sourceNote') or '')
    source_type_label = sanitize_plain_text((post.get('sourceTypeLabel_en') if is_en else post.get('sourceTypeLabel_pt')) or post.get('sourceTypeLabel') or '')
    evidence_label = sanitize_plain_text((post.get('evidenceLabel_en') if is_en else post.get('evidenceLabel_pt')) or post.get('evidenceLabel') or '')
    body_html = sanitize_body_html((post.get('body_en') if is_en else post.get('body_pt')) or post.get('body') or '').strip()
    if not body_html:
        body_html = f'<p>{html.escape(description_raw)}</p>'
    body_text = strip_tags_for_meta(body_html)

    video = post.get('video') if isinstance(post.get('video'), dict) else {}
    video_html = ''
    embed_url = collapse_ws(str(video.get('embedUrl') or ''))
    file_url = collapse_ws(str(video.get('fileUrl') or ''))
    video_caption_value = (
        video.get('caption_en') if is_en else video.get('caption_pt')
    ) or video.get('caption') or (video.get('title_en') if is_en else video.get('title_pt')) or video.get('title') or ''
    video_caption = sanitize_plain_text(video_caption_value)
    if embed_url:
        video_html = (
            '<figure class="preview-video">'
            '<div class="preview-video-frame">'
            f'<iframe src="{html_escape_attr(embed_url)}" title="{html_escape_attr(title_raw)}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>'
            '</div>'
            + (f'<figcaption>{html.escape(video_caption)}</figcaption>' if video_caption else '')
            + '</figure>'
        )
    elif file_url:
        poster = clean_image_url(video.get('poster') or '') or ''
        poster_attr = f' poster="{html_escape_attr(poster)}"' if poster else ''
        video_html = (
            '<figure class="preview-video">'
            '<div class="preview-video-frame">'
            f'<video controls preload="metadata" playsinline{poster_attr}><source src="{html_escape_attr(file_url)}"></video>'
            '</div>'
            + (f'<figcaption>{html.escape(video_caption)}</figcaption>' if video_caption else '')
            + '</figure>'
        )

    inline_gallery = []
    seen_inline = {image_raw}
    for item in (post.get('inline_images') or [])[:8]:
        if not isinstance(item, dict):
            continue
        src = clean_image_url(item.get('src') or '')
        if not src or src in seen_inline:
            continue
        seen_inline.add(src)
        caption = sanitize_plain_text((item.get('caption_en') if is_en else item.get('caption_pt')) or item.get('caption') or '')
        alt = sanitize_plain_text((item.get('alt_en') if is_en else item.get('alt_pt')) or item.get('alt') or image_alt)
        inline_gallery.append(
            '<figure class="preview-inline-figure">'
            f'<img src="{html_escape_attr(src)}" alt="{html_escape_attr(alt)}" loading="lazy" referrerpolicy="no-referrer">'
            + (f'<figcaption>{html.escape(caption)}</figcaption>' if caption else '')
            + '</figure>'
        )
    inline_gallery_html = ('<section class="preview-gallery">' + ''.join(inline_gallery) + '</section>') if inline_gallery else ''

    highlights = []
    highlight_source = (post.get('highlights_en') if is_en else post.get('highlights_pt')) or post.get('highlights') or []
    for item in highlight_source[:4]:
        clean = collapse_ws(str(item))
        if clean:
            highlights.append(clean)
    highlights_html = ''
    if highlights:
        highlights_html = '<section class="highlights editorial-panel"><h2>' + labels['highlights'] + '</h2><ul>' + ''.join(
            f'<li>{html.escape(item)}</li>' for item in highlights
        ) + '</ul></section>'

    source_html = ''
    if source_url:
        source_html = f'<p class="source-link"><strong>{labels["source"]}:</strong> <a href="{html_escape_attr(source_url)}" target="_blank" rel="noopener noreferrer">{html.escape(source_raw or source_url)}</a></p>'
    elif source_raw:
        source_html = f'<p class="source-link"><strong>{labels["source"]}:</strong> {html.escape(source_raw)}</p>'

    context_bits = [bit for bit in [source_type_label, evidence_label, source_note] if bit]
    context_html = ''
    if context_bits or source_url:
        body = ''.join(f'<p>{html.escape(bit)}</p>' for bit in context_bits)
        if source_url:
            body += f'<p><a href="{html_escape_attr(source_url)}" target="_blank" rel="noopener noreferrer">{labels["original"]}</a></p>'
        context_html = f'<section class="context-box editorial-panel"><h2>{labels["context"]}</h2>{body}</section>'

    keywords = unique_keep_order((post.get('keywords_en') if is_en else post.get('keywords_pt')) or post.get('keywords') or [])
    article_tags = ''.join(
        f'  <meta property="article:tag" content="{html_escape_attr(tag)}">\n'
        for tag in keywords[:6]
    )
    json_ld = article_json_ld(
        post,
        'en' if is_en else 'pt',
        canonical_url,
        labels['home_url'],
        alternate_url,
        title_raw,
        description_raw,
        image_raw,
        labels['author'],
        labels['section'],
        keywords,
        body_text,
        source_raw,
        source_url,
    )

    byline_bits = [
        f'<div class="meta-chip"><span>{html.escape(labels["editorial_signature"])}</span><strong>{html.escape(labels["author"])}</strong></div>',
        f'<div class="meta-chip"><span>{html.escape(labels["published"])}</span><strong>{html.escape(" ".join(bit for bit in [date_raw, time_raw] if bit) or (published_raw[:10] if published_raw else ""))}</strong></div>',
        f'<div class="meta-chip"><span>{html.escape(labels["updated"])}</span><strong>{html.escape((modified_raw[:10] if modified_raw else ""))}</strong></div>' if modified_raw else '',
        f'<div class="meta-chip"><span>{html.escape(labels["coverage_type"])}</span><strong>{html.escape(source_type_label or source_raw)}</strong></div>' if (source_type_label or source_raw) else '',
        f'<div class="meta-chip"><span>{html.escape(labels["evidence_level"])}</span><strong>{html.escape(evidence_label)}</strong></div>' if evidence_label else '',
        f'<div class="meta-chip"><span>{html.escape(labels["read_time"])}</span><strong>{html.escape(read_raw)}</strong></div>' if read_raw else '',
    ]
    byline_rows = ''.join(bit for bit in byline_bits if bit)

    chips = [f'<span>{html.escape(labels["section"])}</span>', f'<span>{html.escape(labels["language"])}</span>']
    if source_type_label:
        chips.append(f'<span>{html.escape(source_type_label)}</span>')
    if evidence_label:
        chips.append(f'<span>{html.escape(evidence_label)}</span>')
    section_lang_chip = ''.join(chips)

    page = f"""<!DOCTYPE html>
<html lang="{labels['html_lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0d3a75">
  <title>{html_escape_attr(title_raw)} | {SITE_NAME}</title>
  <meta name="description" content="{html_escape_attr(description_raw)}">
  <meta name="author" content="{html_escape_attr(labels['author'])}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{html_escape_attr(canonical_url)}">
  <link rel="alternate" hreflang="pt-BR" href="{html_escape_attr(article_static_url(slug, 'pt'))}">
  <link rel="alternate" hreflang="en-US" href="{html_escape_attr(article_static_url(slug, 'en'))}">
  <link rel="alternate" hreflang="x-default" href="{html_escape_attr(article_static_url(slug, 'pt'))}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="{labels['locale']}">
  <meta property="og:locale:alternate" content="{labels['alt_locale']}">
  <meta property="og:title" content="{html_escape_attr(title_raw)} | {SITE_NAME}">
  <meta property="og:description" content="{html_escape_attr(description_raw)}">
  <meta property="og:url" content="{html_escape_attr(canonical_url)}">
  <meta property="og:image" content="{html_escape_attr(image_raw)}">
  <meta property="og:image:secure_url" content="{html_escape_attr(image_raw)}">
  <meta property="og:image:alt" content="{html_escape_attr(image_alt)}">
  <meta property="article:published_time" content="{html_escape_attr(published_raw)}">
  <meta property="article:modified_time" content="{html_escape_attr(modified_raw)}">
  <meta property="article:section" content="{html_escape_attr(labels['section'])}">
{article_tags}  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html_escape_attr(title_raw)} | {SITE_NAME}">
  <meta name="twitter:description" content="{html_escape_attr(description_raw)}">
  <meta name="twitter:image" content="{html_escape_attr(image_raw)}">
  <meta name="twitter:image:alt" content="{html_escape_attr(image_alt)}">
  <script type="application/ld+json">{json_ld}</script>
  <style>
    :root {{
      --bg:#f6f3ed; --panel:#ffffff; --panel-soft:#fbfaf7; --ink:#181714; --muted:#615b55; --line:#ddd6cb;
      --accent:#1451a0; --accent-dark:#0d3a75; --accent-soft:#eef4fc; --accent-ink:#133255; --shadow:0 14px 42px rgba(14,18,25,.08);
    }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; -webkit-text-size-adjust:100%; }}
    body {{ margin:0; background:linear-gradient(180deg,#faf8f3 0%, #f5f2eb 100%); color:var(--ink); font:19px/1.85 Georgia, 'Times New Roman', serif; text-rendering:optimizeLegibility; }}
    img {{ max-width:100%; height:auto; }}
    a {{ color:var(--accent); text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .skip-link {{ position:absolute; left:16px; top:-56px; z-index:30; padding:10px 14px; border-radius:10px; background:#fff; color:var(--ink); border:2px solid var(--accent); box-shadow:var(--shadow); font:600 13px/1.2 Arial, sans-serif; }}
    .skip-link:focus-visible {{ top:16px; }}
    a:focus-visible, button:focus-visible, [role="link"]:focus-visible {{ outline:3px solid rgba(20,81,160,.28); outline-offset:3px; box-shadow:0 0 0 2px rgba(13,58,117,.12); }}
    .wrap {{ max-width:1240px; margin:0 auto; padding:28px 18px 72px; }}
    .top {{ display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:18px; font:600 12px/1.4 Arial, sans-serif; letter-spacing:.08em; text-transform:uppercase; }}
    .brand {{ color:var(--accent-dark); letter-spacing:.12em; }}
    .utility-links {{ display:flex; gap:10px; flex-wrap:wrap; }}
    .pill-link {{ display:inline-flex; align-items:center; padding:8px 12px; border:1px solid var(--line); border-radius:999px; background:#fff; }}
    .card {{ background:var(--panel); border:1px solid var(--line); box-shadow:var(--shadow); border-radius:24px; overflow:hidden; }}
    .hero {{ width:100%; aspect-ratio:16/8.2; object-fit:cover; background:#ece8de; border-bottom:1px solid var(--line); }}
    main:focus {{ outline:none; }}
    .content {{ padding:28px 28px 34px; }}
    .breadcrumbs {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:0 0 18px; color:var(--muted); font:600 12px/1.4 Arial, sans-serif; letter-spacing:.04em; text-transform:uppercase; }}
    .breadcrumbs .sep {{ opacity:.55; }}
    .breadcrumbs a {{ color:var(--muted); }}
    .kicker-row {{ display:flex; flex-wrap:wrap; gap:10px; margin:0 0 18px; font:700 11px/1.2 Arial, sans-serif; letter-spacing:.08em; text-transform:uppercase; }}
    .kicker-row span {{ display:inline-flex; align-items:center; padding:8px 11px; border-radius:999px; background:#eef4fc; color:var(--accent-dark); border:1px solid #d7e4f8; }}
    .hero-head {{ display:grid; gap:14px; margin-bottom:18px; }}
    h1 {{ font-size:clamp(2.2rem,4vw,3.5rem); line-height:1.04; margin:0; max-width:980px; }}
    .dek {{ font-size:1.12rem; color:#2f2b26; margin:0; max-width:820px; }}
    .editorial-strap {{ display:inline-flex; align-items:center; gap:10px; flex-wrap:wrap; color:var(--accent-ink); font:700 13px/1.5 Arial, sans-serif; background:var(--accent-soft); border:1px solid #d6e4f9; padding:12px 14px; border-radius:16px; }}
    .editorial-strap strong {{ color:var(--accent-dark); }}
    .meta-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:20px 0 28px; }}
    .meta-chip {{ background:var(--panel-soft); border:1px solid var(--line); border-radius:16px; padding:12px 14px; min-height:78px; }}
    .meta-chip span {{ display:block; color:var(--muted); font:600 11px/1.4 Arial, sans-serif; letter-spacing:.08em; text-transform:uppercase; margin-bottom:7px; }}
    .meta-chip strong {{ display:block; font:600 15px/1.5 Arial, sans-serif; color:var(--ink); }}
    .article-grid {{ display:grid; grid-template-columns:minmax(0,1fr) 320px; gap:28px; align-items:start; }}
    .main-story {{ min-width:0; }}
    .sidebar {{ display:grid; gap:18px; position:sticky; top:22px; }}
    .editorial-panel {{ margin:0; padding:18px 18px 16px; border-radius:18px; background:var(--panel-soft); border:1px solid var(--line); box-shadow:0 10px 30px rgba(13,18,25,.04); }}
    .editorial-panel h2 {{ margin:0 0 10px; font:700 1rem/1.3 Arial, sans-serif; color:var(--ink); }}
    .editorial-panel p, .editorial-panel li {{ color:#2d2a26; font:400 15px/1.7 Arial, sans-serif; }}
    .body-label {{ color:var(--muted); font:700 12px/1.3 Arial, sans-serif; letter-spacing:.1em; text-transform:uppercase; margin:0 0 14px; }}
    .body {{ font-size:1.04em; max-width:70ch; }}
    .body p {{ margin:0 0 1.28em; }}
    .body blockquote {{ margin:1.4em 0; padding:0 0 0 18px; border-left:3px solid #cfdcf2; color:#2b3947; font-style:italic; }}
    .preview-video {{ margin:0 0 24px; }}
    .preview-video-frame {{ position:relative; width:100%; aspect-ratio:16/9; border-radius:16px; overflow:hidden; background:#0b1220; }}
    .preview-video-frame iframe, .preview-video-frame video {{ width:100%; height:100%; border:0; display:block; }}
    .preview-video figcaption, .preview-inline-figure figcaption {{ color:var(--muted); font:400 14px/1.55 Arial, sans-serif; margin-top:8px; }}
    .preview-gallery {{ display:grid; grid-template-columns:1fr; gap:18px; margin:26px 0 0; }}
    .preview-inline-figure {{ margin:0; }}
    .preview-inline-figure img {{ width:100%; border-radius:16px; display:block; background:#ece8de; }}
    .highlights ul {{ margin:0; padding-left:20px; }}
    .highlights li {{ margin:0 0 8px; }}
    .source-link {{ margin-top:22px; color:#333; font:400 15px/1.6 Arial, sans-serif; }}
    .story-tools {{ display:grid; gap:10px; }}
    .story-tool-btn, .story-link-btn {{ display:inline-flex; align-items:center; justify-content:center; width:100%; min-height:44px; padding:12px 14px; border-radius:999px; border:1px solid var(--line); background:#fff; color:var(--ink); font:600 14px/1.2 Arial, sans-serif; cursor:pointer; text-align:center; }}
    .story-tool-btn.primary, .story-link-btn.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
    .story-tool-status {{ color:var(--muted); font:500 12px/1.4 Arial, sans-serif; min-height:18px; }}
    .related-list {{ display:grid; gap:12px; }}
    .related-item {{ display:block; padding:14px 14px 12px; border:1px solid var(--line); border-radius:16px; background:#fff; }}
    .related-item:hover {{ text-decoration:none; border-color:#c9d8ee; box-shadow:0 8px 24px rgba(20,81,160,.08); }}
    .related-kicker {{ color:var(--accent-dark); font:700 11px/1.3 Arial, sans-serif; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px; }}
    .related-title {{ color:var(--ink); font:700 15px/1.4 Arial, sans-serif; margin-bottom:4px; }}
    .related-meta {{ color:var(--muted); font:500 12px/1.5 Arial, sans-serif; }}
    .footer-links {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:28px; font:600 14px/1.4 Arial, sans-serif; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; padding:12px 16px; border-radius:999px; border:1px solid var(--line); background:#fff; }}
    .btn.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
    .article-footer-note {{ margin-top:14px; color:var(--muted); font:500 13px/1.6 Arial, sans-serif; }}
    @media (max-width: 980px) {{
      .article-grid {{ grid-template-columns:1fr; }}
      .sidebar {{ position:static; order:2; }}
      .body {{ max-width:none; }}
      .meta-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    }}
    @media (max-width: 640px) {{
      body {{ font-size:17px; }}
      .content {{ padding:22px 16px 28px; }}
      .wrap {{ padding:16px 12px 44px; }}
      .top {{ align-items:flex-start; }}
      .meta-grid {{ grid-template-columns:1fr; }}
      .hero {{ aspect-ratio:16/10; }}
      .story-tool-btn, .story-link-btn {{ width:100%; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      html {{ scroll-behavior:auto; }}
      *, *::before, *::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; scroll-behavior:auto !important; }}
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#articleMain">{'Skip to main content' if is_en else 'Pular para o conteúdo principal'}</a>
  <main class="wrap" id="articleMain" tabindex="-1">
    <div class="top">
      <div class="brand">Cosmos Week</div>
      <div class="utility-links">
        <a class="pill-link" href="{html_escape_attr(labels['home_url'])}">{labels['back']}</a>
        <a class="pill-link" href="{html_escape_attr(alternate_url)}">{labels['other_language']}</a>
      </div>
    </div>
    <article class="card" data-article-slug="{html_escape_attr(slug)}" data-article-category="{html_escape_attr(post.get('cat') or '')}" data-article-lang="{'en' if is_en else 'pt'}" data-article-url="{html_escape_attr(canonical_url)}">
      <img class="hero" src="{html_escape_attr(image_raw)}" alt="{html_escape_attr(image_alt)}" loading="eager" fetchpriority="high" decoding="async" referrerpolicy="no-referrer">
      <div class="content">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <a href="{html_escape_attr(labels['home_url'])}">{html.escape(labels['breadcrumbs_home'])}</a>
          <span class="sep">/</span>
          <a href="{html_escape_attr(news_url)}">{html.escape(labels['breadcrumbs_news'])}</a>
          <span class="sep">/</span>
          <span>{html.escape(labels['section'])}</span>
        </nav>

        <div class="hero-head">
          <div class="kicker-row">{section_lang_chip}</div>
          <h1>{html.escape(title_raw)}</h1>
          <p class="dek">{html.escape(description_raw)}</p>
          <div class="editorial-strap"><strong>{html.escape(labels['institutional_note'])}</strong> {html.escape(source_raw or labels['author'])}</div>
        </div>

        <div class="meta-grid">{byline_rows}</div>

        <div class="article-grid">
          <div class="main-story">
            {video_html}
            {highlights_html}
            <div class="body-label">{html.escape(labels['body_label'])}</div>
            <div class="body">{body_html}</div>
            {inline_gallery_html}
            {source_html}
            <div class="footer-links">
              <a class="btn primary" href="{html_escape_attr(labels['home_url'])}">{labels['home']}</a>
              <a class="btn" href="{html_escape_attr(dynamic_url)}">{labels['dynamic']}</a>
            </div>
            <p class="article-footer-note">{html.escape(labels['live_edition_note'])}</p>
          </div>

          <aside class="sidebar" aria-label="{html_escape_attr(labels['editorial_header'])}">
            <section class="editorial-panel">
              <h2>{html.escape(labels['source_analysis'])}</h2>
              <p>{html.escape(labels['source_analysis_text'])}</p>
              <div class="meta-grid" style="grid-template-columns:1fr; margin:14px 0 0; gap:10px;">
                <div class="meta-chip"><span>{html.escape(labels['coverage_type'])}</span><strong>{html.escape(source_type_label or source_raw or SITE_NAME)}</strong></div>
                <div class="meta-chip"><span>{html.escape(labels['evidence_level'])}</span><strong>{html.escape(evidence_label or source_type_label or labels['author'])}</strong></div>
                <div class="meta-chip"><span>{html.escape(labels['source'])}</span><strong>{html.escape(source_raw or canonical_url)}</strong></div>
              </div>
            </section>
            {context_html}
            <section class="editorial-panel">
              <h2>{html.escape(labels['tools'])}</h2>
              <div class="story-tools">
                <button class="story-tool-btn" id="copyArticleLink" type="button">{html.escape(labels['copy'])}</button>
                <button class="story-tool-btn primary" id="shareArticleBtn" type="button">{html.escape(labels['share'])}</button>
                {f'<a class="story-link-btn" href="{html_escape_attr(source_url)}" target="_blank" rel="noopener noreferrer">{html.escape(labels["open_source_cta"])}</a>' if source_url else ''}
              </div>
              <div class="story-tool-status" id="storyToolStatus" aria-live="polite"></div>
            </section>
            <section class="editorial-panel">
              <h2>{html.escape(labels['standards'])}</h2>
              <p>{html.escape(labels['standards_blurb'])}</p>
              <a class="story-link-btn" href="{html_escape_attr(standards_url)}">{html.escape(labels['standards_cta'])}</a>
            </section>
            <section class="editorial-panel">
              <h2>{html.escape(labels['related'])}</h2>
              <div class="related-list" id="relatedStories"><p class="related-meta">{html.escape(labels['related_empty'])}</p></div>
            </section>
          </aside>
        </div>
      </div>
    </article>
  </main>
  <script>
    (function() {{
      const canonicalUrl = {json.dumps(canonical_url)};
      const sourceUrl = {json.dumps(source_url)};
      const articleSlug = {json.dumps(slug)};
      const articleCat = {json.dumps(post.get('cat') or '')};
      const articleSourceType = {json.dumps(post.get('sourceType') or '')};
      const articleSource = {json.dumps(post.get('source') or '')};
      const isEnglish = {str(is_en).lower()};
      const copyBtn = document.getElementById('copyArticleLink');
      const shareBtn = document.getElementById('shareArticleBtn');
      const statusEl = document.getElementById('storyToolStatus');
      const relatedEl = document.getElementById('relatedStories');
      const labels = {{
        copied: {json.dumps(labels['copied'])},
        copyFail: {json.dumps(labels['copy_fail'])},
        relatedEmpty: {json.dumps(labels['related_empty'])},
      }};

      function setStatus(text) {{
        if (statusEl) statusEl.textContent = text || '';
      }}

      async function copyLink() {{
        try {{
          await navigator.clipboard.writeText(canonicalUrl);
          setStatus(labels.copied);
        }} catch (err) {{
          setStatus(labels.copyFail);
        }}
      }}

      async function shareArticle() {{
        try {{
          if (navigator.share) {{
            await navigator.share({{ title: document.title, text: document.title, url: canonicalUrl }});
            setStatus('');
            return;
          }}
        }} catch (err) {{
          if (err && err.name === 'AbortError') return;
        }}
        await copyLink();
      }}

      if (copyBtn) copyBtn.addEventListener('click', copyLink);
      if (shareBtn) shareBtn.addEventListener('click', shareArticle);

      function pickUrl(item) {{
        return isEnglish ? (item.shareUrl_en || item.canonicalUrl_en || item.realUrl_en || item.shareUrl) : (item.shareUrl_pt || item.canonicalUrl_pt || item.realUrl_pt || item.shareUrl || item.canonicalUrl);
      }}

      function pickTitle(item) {{
        return isEnglish ? (item.title_en || item.title || '') : (item.title_pt || item.title || '');
      }}

      function pickRead(item) {{
        return isEnglish ? (item.read_en || item.read || '') : (item.read_pt || item.read || '');
      }}

      function renderRelated(items) {{
        if (!relatedEl) return;
        if (!items.length) {{
          relatedEl.innerHTML = '<p class="related-meta">' + labels.relatedEmpty + '</p>';
          return;
        }}
        relatedEl.innerHTML = items.map((item) => {{
          const url = pickUrl(item) || '#';
          const title = pickTitle(item);
          const meta = [item.cat || '', isEnglish ? (item.date_en || item.date || '') : (item.date_pt || item.date || ''), pickRead(item)].filter(Boolean).join(' · ');
          const coverage = isEnglish ? (item.sourceTypeLabel_en || item.sourceTypeLabel || '') : (item.sourceTypeLabel_pt || item.sourceTypeLabel || '');
          return '<a class="related-item" href="' + url + '"><div class="related-kicker">' + (coverage || (item.cat || '')) + '</div><div class="related-title">' + title + '</div><div class="related-meta">' + meta + '</div></a>';
        }}).join('');
      }}

      fetch('/assets/data/posts-index.json', {{ credentials: 'omit' }})
        .then((response) => response.ok ? response.json() : [])
        .then((items) => Array.isArray(items) ? items : [])
        .then((items) => {{
          const ranked = items
            .filter((item) => item && item.slug && item.slug !== articleSlug)
            .map((item) => {{
              let score = 0;
              if ((item.cat || '') === articleCat) score += 6;
              if ((item.sourceType || '') === articleSourceType) score += 2;
              if ((item.source || '') === articleSource) score += 1;
              if (sourceUrl && (item.srcUrl || '') === sourceUrl) score += 1;
              if (item.featured) score += 1;
              return {{ item, score }};
            }})
            .sort((a, b) => (b.score - a.score) || String(b.item.publishedIso || '').localeCompare(String(a.item.publishedIso || '')))
            .slice(0, 3)
            .map((entry) => entry.item);
          renderRelated(ranked);
        }})
        .catch(() => renderRelated([]));
    }})();
  </script>
</body>
</html>
"""
    return page


def sort_posts_desc(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=lambda p: p.get('publishedIso', ''), reverse=True)

def load_archive_posts() -> list[dict]:
    if not ARCHIVE_POSTS_JSON.exists():
        return []
    try:
        data = json.loads(ARCHIVE_POSTS_JSON.read_text(encoding='utf-8'))
    except Exception:
        return []
    if not isinstance(data, list):
        return []

    out = []
    seen = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        slug = collapse_ws(str(item.get('slug') or ''))
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(item)
    return sort_posts_desc(out)

def merge_archive_posts(current_posts: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}

    for post in load_archive_posts():
        slug = collapse_ws(str(post.get('slug') or ''))
        if slug:
            merged[slug] = post

    for post in current_posts:
        slug = collapse_ws(str(post.get('slug') or ''))
        if slug:
            merged[slug] = post

    archive_posts = sort_posts_desc(list(merged.values()))
    for idx, post in enumerate(archive_posts, start=1):
        post['id'] = idx
    return archive_posts

def save_archive_posts(posts: list[dict]) -> None:
    sanitized = sanitize_posts(sort_posts_desc(posts))
    ARCHIVE_POSTS_JSON.write_text(
        json.dumps(sanitized, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

def build_preview_pages(posts: list[dict]) -> None:
    if PREVIEW_DIR.exists():
        shutil.rmtree(PREVIEW_DIR)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    if PREVIEW_EN_DIR.exists():
        shutil.rmtree(PREVIEW_EN_DIR)
    PREVIEW_EN_DIR.mkdir(parents=True, exist_ok=True)

    for post in sort_posts_desc(posts):
        slug = collapse_ws(str(post.get('slug') or ''))
        if not slug:
            continue

        article_dir_pt = PREVIEW_DIR / slug
        article_dir_pt.mkdir(parents=True, exist_ok=True)
        (article_dir_pt / 'index.html').write_text(render_static_article_page(post, 'pt'), encoding='utf-8')

        article_dir_en = PREVIEW_EN_DIR / slug
        article_dir_en.mkdir(parents=True, exist_ok=True)
        (article_dir_en / 'index.html').write_text(render_static_article_page(post, 'en'), encoding='utf-8')


# ── Output generation ─────────────────────────────────────────────────────────

def build_feed(posts: list[dict]) -> None:
    items = []
    for post in posts[:20]:
        pub_str = datetime.fromisoformat(post['publishedIso']).strftime('%a, %d %b %Y %H:%M:%S +0000')
        categories = ''.join(
            f'<category>{xml_escape(cat)}</category>'
            for cat in unique_keep_order(post.get('keywords_pt', [])[:4])
        )
        body_preview = xml_escape(strip_html(post.get('body_pt', ''))[:900])
        items.append(
            f'''<item>
              <title>{xml_escape(post['title_pt'])}</title>
              <link>{xml_escape(post.get('shareUrl_pt') or post.get('shareUrl') or post['canonicalUrl'])}</link>
              <guid>{xml_escape(post.get('shareUrl_pt') or post.get('shareUrl') or post['canonicalUrl'])}</guid>
              <pubDate>{pub_str}</pubDate>
              <author>contato@cosmosweek.com (Cosmos Week)</author>
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
    <generator>CosmosWeekBot 5.0</generator>
    {''.join(items)}
  </channel>
</rss>
'''
    FEED_XML.write_text(xml, encoding='utf-8')


def build_sitemap(posts: list[dict], archive_posts: Optional[list[dict]] = None) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    static_urls = [
        (SITE_URL, today),
        (f'{SITE_URL}?lang=en', today),
        (f'{SITE_URL}?page=arquivo', today),
        (f'{SITE_URL}?page=arquivo&lang=en', today),
        (f'{SITE_URL}?page=sobre', today),
        (f'{SITE_URL}?page=sobre&lang=en', today),
        (f'{SITE_URL}?page=padroes', today),
        (f'{SITE_URL}?page=padroes&lang=en', today),
        (urllib.parse.urljoin(SITE_URL, 'anuncie.html'), today),
        (urllib.parse.urljoin(SITE_URL, 'en/advertise/'), today),
        (urllib.parse.urljoin(SITE_URL, 'media-kit.html'), today),
        (urllib.parse.urljoin(SITE_URL, 'en/media-kit/'), today),
        (urllib.parse.urljoin(SITE_URL, 'politica-de-privacidade.html'), today),
        (urllib.parse.urljoin(SITE_URL, 'en/privacy/'), today),
        (urllib.parse.urljoin(SITE_URL, 'termos-de-uso.html'), today),
        (urllib.parse.urljoin(SITE_URL, 'en/terms/'), today),
    ]
    dynamic_urls = []
    for post in posts:
        published = str(post.get('publishedIso') or '')[:10] or today
        pt_url = post.get('shareUrl_pt') or post.get('shareUrl') or post.get('canonicalUrl')
        en_url = post.get('shareUrl_en') or article_static_url(post.get('slug', ''), 'en')
        if pt_url:
            dynamic_urls.append((pt_url, published))
        if en_url:
            dynamic_urls.append((en_url, published))
    archive_urls = []
    for post in archive_posts or []:
        published = str(post.get('publishedIso') or '')[:10] or today
        pt_url = post.get('shareUrl_pt') or post.get('shareUrl') or article_static_url(post.get('slug', '').strip(), 'pt')
        en_url = post.get('shareUrl_en') or article_static_url(post.get('slug', '').strip(), 'en')
        if pt_url:
            archive_urls.append((pt_url, published))
        if en_url:
            archive_urls.append((en_url, published))
    all_urls = unique_keep_order(static_urls + dynamic_urls + archive_urls)
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
    ROBOTS_TXT.write_text(
        f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n',
        encoding='utf-8'
    )


def save_posts(posts: list[dict]) -> None:
    # Sanitiza campos textuais e mídia antes de serializar qualquer artefato.
    sanitize_posts(posts)
    # Garantir saída sempre em ordem cronológica decrescente.
    # A lógica de ranking decide *quais* posts entram; a ordem de saída
    # deve ser mais-recente-primeiro para RSS, sitemap e leitores externos.
    posts_sorted = sort_posts_desc(posts)
    POSTS_JSON.write_text(json.dumps(posts_sorted, ensure_ascii=False, indent=2), encoding='utf-8')
    POSTS_JS.write_text(
        '// Dados atualizados automaticamente para o Cosmos Week\n\nwindow.postsData = ' +
        json.dumps(posts_sorted, ensure_ascii=False, indent=2) + ';\n',
        encoding='utf-8'
    )

    archive_posts = merge_archive_posts(posts_sorted)
    save_archive_posts(archive_posts)

    build_feed(posts_sorted)
    build_sitemap(posts_sorted, archive_posts)
    build_robots()
    build_preview_pages(archive_posts)


def load_all_items() -> list[dict]:
    all_items = []
    for source in SOURCES:
        is_arxiv = 'arxiv.org' in source.url
        timeout  = ARXIV_TIMEOUT if is_arxiv else REQUEST_TIMEOUT
        retries  = ARXIV_RETRIES if is_arxiv else 0
        try:
            raw = fetch_with_retry(source.url, timeout=timeout, retries=retries)
            if source.kind == 'atom':
                items = parse_atom(raw, source)
            else:
                items = parse_rss(raw, source)
            all_items.extend(items)
            print(f'OK  {source.name}: {len(items)} itens')
        except Exception as exc:
            print(f'ERR {source.name}: {exc}')
    return all_items


def _apply_reviewed_post(post: dict, reviewed: dict) -> None:
    """Aplica o resultado da revisão Gemini a um post in-place."""
    title   = collapse_ws(str(reviewed.get('title')   or post['title_pt']))
    summary = collapse_ws(str(reviewed.get('summary') or post['sub_pt']))
    facts   = [collapse_ws(str(f)) for f in (reviewed.get('facts') or []) if collapse_ws(str(f))]
    facts   = distinct_facts(facts, 6) or []

    body_raw = str(reviewed.get('body') or '')
    body_paragraphs = [collapse_ws(p) for p in re.split(r'\n{2,}', body_raw) if collapse_ws(p)]
    if not body_paragraphs:
        return  # resposta inesperada — mantém fallback

    body_html = ''.join(
        f'<p>{html.escape(collapse_ws(p))}</p>'
        for p in body_paragraphs[:8]
        if len(collapse_ws(p)) >= 45
    )
    if not body_html:
        return

    post['title']         = title
    post['title_pt']      = title
    post['sub']           = truncate(summary, 180)
    post['sub_pt']        = truncate(summary, 180)
    post['excerpt']       = truncate(summary, 260)
    post['excerpt_pt']    = truncate(summary, 260)
    post['body']          = body_html
    post['body_pt']       = body_html
    post['highlights']    = build_highlights(title, summary, facts, post['sourceType'], 'pt')
    post['highlights_pt'] = post['highlights']
    post['reviewStatus']  = 'success'
    keywords_pt = unique_keep_order(
        [post['cat'], post['source'], 'Cosmos Week'] +
        [frag.strip() for frag in re.split(r'[,;:\-]', title) if len(frag.strip()) > 3]
    )[:8]
    post['keywords']    = keywords_pt
    post['keywords_pt'] = keywords_pt


def batch_review_all_posts(posts: list[dict]) -> None:
    """Revisa todos os posts priorizando chance de sucesso do Gemini.

    Quando GEMINI_BATCH_SIZE for 1, processa um artigo por chamada. Isso aumenta a
    chance de aproveitar janelas curtas de disponibilidade do serviço em vez de
    perder um lote inteiro por causa de um único 503.
    """
    if not GEMINI_API_KEY:
        for post in posts:
            post['reviewStatus'] = 'fallback'
        return

    queue = list(posts)
    if GEMINI_REVIEW_PRIORITY_FIRST:
        queue.sort(key=lambda p: (-(p.get('score') or 0), p.get('isPreprint', False), p.get('slug', '')))

    success_count = 0
    fallback_count = 0

    import time as _time
    review_started_at = _time.monotonic()

    if GEMINI_BATCH_SIZE <= 1:
        total = len(queue)
        for idx, p in enumerate(queue, start=1):
            if _gemini_review_budget_exhausted(review_started_at):
                _disable_gemini_for_run(f'limite de tempo de revisão Gemini atingido ({GEMINI_MAX_REVIEW_SECONDS}s)')
            if _GEMINI_DISABLED_THIS_RUN:
                p['reviewStatus'] = 'fallback'
                fallback_count += 1
                continue
            print(f'  [Gemini] Artigo {idx}/{total} ({p.get("slug", "")}) ...')
            reviewed_single = review_portuguese_content(p['title_pt'], p['sub_pt'], p.get('highlights_pt', [])[:3], p['body_pt'])
            if reviewed_single.get('status') == 'success':
                p['title'] = reviewed_single['title']
                p['title_pt'] = reviewed_single['title']
                p['sub'] = truncate(reviewed_single['summary'], 180)
                p['sub_pt'] = truncate(reviewed_single['summary'], 180)
                p['excerpt'] = truncate(reviewed_single['summary'], 260)
                p['excerpt_pt'] = truncate(reviewed_single['summary'], 260)
                p['body'] = reviewed_single['body']
                p['body_pt'] = reviewed_single['body']
                facts_single = distinct_facts([collapse_ws(str(f)) for f in reviewed_single.get('facts') or []], 6) or []
                p['highlights'] = build_highlights(reviewed_single['title'], reviewed_single['summary'], facts_single, p['sourceType'], 'pt')
                p['highlights_pt'] = p['highlights']
                p['reviewStatus'] = 'success'
                success_count += 1
            else:
                p['reviewStatus'] = 'fallback'
                fallback_count += 1
        print(f'  [Gemini] Concluído: {success_count} sucesso / {fallback_count} fallback')
        return

    total = len(queue)
    success_count = 0
    fallback_count = 0
    total_batches = (total + GEMINI_BATCH_SIZE - 1) // GEMINI_BATCH_SIZE
    for batch_start in range(0, total, GEMINI_BATCH_SIZE):
        if _gemini_review_budget_exhausted(review_started_at):
            _disable_gemini_for_run(f'limite de tempo de revisão Gemini atingido ({GEMINI_MAX_REVIEW_SECONDS}s)')
        if _GEMINI_DISABLED_THIS_RUN:
            remaining = queue[batch_start:]
            for p in remaining:
                if p.get('reviewStatus') != 'success':
                    p['reviewStatus'] = 'fallback'
                    fallback_count += 1
            print(f'  [Gemini] Revisão abortada para os {len(remaining)} posts restantes por indisponibilidade do serviço')
            break
        batch = queue[batch_start: batch_start + GEMINI_BATCH_SIZE]
        batch_num = batch_start // GEMINI_BATCH_SIZE + 1
        payload_items = [{'slug': p['slug'], 'title': p['title_pt'], 'summary': p['sub_pt'], 'facts': p.get('highlights_pt', [])[:3], 'body': _gemini_prompt_body(p['body_pt'])} for p in batch]
        prompt = (
            'Você é um revisor científico e copy editor sênior em português do Brasil. '
            'Receberá um array JSON com vários artigos. Para cada artigo, corrija ortografia, gramática, pontuação e coesão; preserve rigor factual; não invente fatos; '
            'responda somente em JSON válido com slug, title, summary, facts e body. '
            'O campo body deve vir sem HTML, em 5 a 8 parágrafos completos separados por \\n\\n.\n\n'
            + json.dumps(payload_items, ensure_ascii=False)
        )
        print(f'  [Gemini] Lote {batch_num}/{total_batches} ({len(batch)} posts) ...')
        result = call_gemini_json(f'pt_batch_{batch_start}', prompt)
        if isinstance(result, dict):
            for key in ('items', 'posts', 'articles', 'results'):
                if isinstance(result.get(key), list):
                    result = result[key]
                    break
            else:
                result = list(result.values()) if result else None
        if not isinstance(result, list):
            print(f'  [Gemini] Lote {batch_num} sem resposta válida — fallback individual para {len(batch)} posts')
            for p in batch:
                reviewed_single = review_portuguese_content(p['title_pt'], p['sub_pt'], p.get('highlights_pt', [])[:3], p['body_pt'])
                if reviewed_single.get('status') == 'success':
                    p['title'] = reviewed_single['title']
                    p['title_pt'] = reviewed_single['title']
                    p['sub'] = truncate(reviewed_single['summary'], 180)
                    p['sub_pt'] = truncate(reviewed_single['summary'], 180)
                    p['excerpt'] = truncate(reviewed_single['summary'], 260)
                    p['excerpt_pt'] = truncate(reviewed_single['summary'], 260)
                    p['body'] = reviewed_single['body']
                    p['body_pt'] = reviewed_single['body']
                    facts_single = distinct_facts([collapse_ws(str(f)) for f in reviewed_single.get('facts') or []], 6) or []
                    p['highlights'] = build_highlights(reviewed_single['title'], reviewed_single['summary'], facts_single, p['sourceType'], 'pt')
                    p['highlights_pt'] = p['highlights']
                    p['reviewStatus'] = 'success'
                    success_count += 1
                else:
                    p['reviewStatus'] = 'fallback'
                    fallback_count += 1
            continue
        reviewed_map = {str(r.get('slug', '')): r for r in result if isinstance(r, dict)}
        for p in batch:
            reviewed = reviewed_map.get(p['slug'])
            if reviewed:
                _apply_reviewed_post(p, reviewed)
                success_count += 1
            else:
                p['reviewStatus'] = 'fallback'
                fallback_count += 1
    print(f'  [Gemini] Concluído: {success_count} sucesso / {fallback_count} fallback')


def rebuild_from_existing() -> None:
    if not POSTS_JSON.exists():
        raise SystemExit('posts.json não encontrado para rebuild local.')
    try:
        posts = json.loads(POSTS_JSON.read_text(encoding='utf-8'))
    except Exception as exc:
        raise SystemExit(f'Falha ao ler posts.json existente: {exc}') from exc
    if not isinstance(posts, list):
        raise SystemExit('posts.json existente não contém uma lista de posts.')
    print(f'Rebuild local a partir do snapshot existente: {len(posts)} posts')
    save_posts(posts)


def main() -> None:
    rebuild_mode = (os.getenv('COSMOS_REBUILD_FROM_EXISTING', '') or '').strip().lower() in {'1', 'true', 'yes'}
    if rebuild_mode:
        rebuild_from_existing()
        return

    # ── Validação da chave Gemini ────────────────────────────────────────────
    if not GEMINI_API_KEY:
        print(
            '\n⚠️  AVISO: GEMINI_API_KEY não está configurada ou está vazia.\n'
            '   A revisão do português será pulada para todos os artigos.\n'
            '   Configure o secret GEMINI_API_KEY no repositório GitHub:\n'
            '   Settings → Secrets and variables → Actions → New repository secret\n'
            '   Nome: GEMINI_API_KEY  |  Valor: sua chave da API do Google AI Studio\n'
        )
    else:
        print(f'✓  Gemini configurado: modelo={GEMINI_MODEL} | lotes de {GEMINI_BATCH_SIZE} posts')

    items = load_all_items()
    print(f'\nTotal bruto: {len(items)} itens de {len(SOURCES)} fontes')
    ranked = dedupe_and_rank(items)
    posts = []
    regular_rank = 0
    for idx, item in enumerate(ranked):
        current_rank = regular_rank if item['source_type'] != 'preprint' else 99
        if item['source_type'] != 'preprint':
            regular_rank += 1
        posts.append(to_post(item, idx, current_rank))

    print(f'\nIniciando revisão Gemini em lote ({len(posts)} posts) ...')
    batch_review_all_posts(posts)

    save_posts(posts)
    counts_type = Counter(post['sourceType'] for post in posts)
    counts_cat = Counter(post['cat'] for post in posts)
    gemini_ok  = sum(1 for p in posts if p.get('reviewStatus') == 'success')
    gemini_fb  = sum(1 for p in posts if p.get('reviewStatus') == 'fallback')
    print(f'\n{len(posts)} posts salvos — {datetime.now(timezone.utc).isoformat()}')
    print(f'Por tipo de fonte: {dict(counts_type)}')
    print('Por categoria:')
    for cat, n in sorted(counts_cat.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {n}')
    print(f'\nRevisão Gemini: {gemini_ok} sucesso / {gemini_fb} fallback (sem revisão)')
    print(f'Base do site: {SITE_URL}')


if __name__ == '__main__':
    main()
