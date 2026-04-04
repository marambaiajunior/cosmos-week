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

MAX_POSTS = 40
MAX_POSTS_PER_SOURCE = 5
MAX_PREPRINTS = 14
MIN_POSTS_PER_CATEGORY = 3
USER_AGENT = 'CosmosWeekBot/5.0 (+https://github.com/marambaiajunior/cosmos-week)'
REQUEST_TIMEOUT = 30
PAGE_TIMEOUT = 20
TRANSLATE_TIMEOUT = 22
TRANSLATE_ENDPOINT = 'https://translate.googleapis.com/translate_a/single'
MAX_PAGE_FETCHES = 42
PAGE_TEXT_MAX_PARAGRAPHS = 24
FULL_TEXT_LIMIT = 9000
MAX_FACT_SENTENCES = 14
MIN_PUBLISHABLE_POSTS = 3

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
]
BAD_URL_PARTS = [
    '/image-article/', '/images/', '/videos/', '/video/', '/week_in_images/',
    '/photojournal/', '/multimedia/', '/gallery/', '/podcast/', '/live/',
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
    'photo essay', 'webcast', 'subscribe', 'newsletter', 'sign up',
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


SOURCES = [
    # ── Institutional / Agency ──────────────────────────────────────────────
    SourceConfig('NASA News Releases',          'https://www.nasa.gov/news-release/feed/',                                              'rss',  'agency',   94),
    SourceConfig('JPL News',                    'https://www.jpl.nasa.gov/feeds/news/',                                                 'rss',  'agency',   93),
    SourceConfig('ESO Press Releases',          'https://www.eso.org/public/news/rss/',                                                 'rss',  'agency',   92),
    SourceConfig('ESA Space Science',           'https://www.esa.int/rssfeed/Our_Activities/Space_Science',                             'rss',  'agency',   90),
    SourceConfig('ESA Hubble News',             'https://esahubble.org/news/feed/',                                                     'rss',  'agency',   89),
    SourceConfig('CERN News',                   'https://home.cern/news/feed',                                                          'rss',  'agency',   86),
    SourceConfig('APS Physics',                 'https://feeds.aps.org/rss/recent/physics.rss',                                         'rss',  'journal',  83),
    SourceConfig('NSF News',                    'https://www.nsf.gov/rss/rss_www_news.xml',                                             'rss',  'agency',   80),
    SourceConfig('ESA Space News',              'https://www.esa.int/rssfeed/Our_Activities/Space_News',                                'rss',  'agency',   80),
    SourceConfig('NIH News Releases',           'https://www.nih.gov/news-releases/feed.xml',                                           'rss',  'agency',   79),
    SourceConfig('The Planetary Society',       'https://www.planetary.org/articles/feed',                                             'rss',  'agency',   78),
    SourceConfig('NOAA Science',                'https://www.noaa.gov/news-release/feed',                                               'rss',  'agency',   77),
    SourceConfig('Phys.org Space',              'https://phys.org/rss-feed/space-news/',                                               'rss',  'agency',   76),
    SourceConfig('NASA Earth Observatory',      'https://science.nasa.gov/feed/earth-observatory/natural-events',                       'rss',  'agency',   75),
    SourceConfig('Sky & Telescope',             'https://skyandtelescope.org/feed/',                                                    'rss',  'agency',   74),
    SourceConfig('Universe Today',              'https://www.universetoday.com/feed/',                                                  'rss',  'agency',   73),
    SourceConfig('EarthSky',                    'https://earthsky.org/feed/',                                                           'rss',  'agency',   72),
    SourceConfig('Phys.org Biology',            'https://phys.org/rss-feed/biology/',                                                  'rss',  'agency',   71),
    SourceConfig('Phys.org Chemistry',          'https://phys.org/rss-feed/chemistry/',                                                'rss',  'agency',   70),
    SourceConfig('Phys.org Earth Sciences',     'https://phys.org/rss-feed/earth-sciences/',                                           'rss',  'agency',   70),
    SourceConfig('Phys.org Physics',            'https://phys.org/rss-feed/physics/',                                                  'rss',  'agency',   71),
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


# ── Utility functions ─────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


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


def truncate(text: str, limit: int) -> str:
    text = collapse_ws(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].strip().rstrip(' .;:,-–—')
    return f'{cut}.' if cut else ''


def smooth_prose(text: str) -> str:
    text = collapse_ws(text)
    if not text:
        return ''
    text = text.replace('…', '.')
    text = re.sub(r'\.{3,}', '.', text)
    text = re.sub(r'\s+[–—-]\s+', ', ', text)
    text = re.sub(r'(?<=\w)[–—](?=\w)', ', ', text)
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
    if any(bad in low for bad in ('logo', 'favicon', 'avatar', 'placeholder', 'sprite', 'icon', 'banner_ad')):
        return False
    if not re.search(r'\.(jpg|jpeg|png|webp)(?:$|[?#])', low) and not any(t in low for t in ('image', 'photo', 'media', 'img')):
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
            raw = response.read(1_400_000)
        page = raw.decode('utf-8', errors='ignore')
    except Exception:
        page = ''
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

def parse_rss(xml_bytes: bytes, source: SourceConfig) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall('.//item'):
        title = strip_html(item.findtext('title', default=''))
        link = collapse_ws(item.findtext('link', default=''))
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
    root = ET.fromstring(xml_bytes)
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


def _fact_clause(text: str, limit: int = 175) -> str:
    text = smooth_prose(text)
    text = re.sub(r'^[A-Z][^:]{0,28}:\s+', '', text)
    text = re.sub(r'\s*\[(.*?)\]\s*', ' ', text)
    text = re.sub(r'\s*\((?:credit|image|photo).*?\)\s*', ' ', text, flags=re.I)
    text = re.sub(r'https?://\S+', ' ', text, flags=re.I)
    text = re.sub(r'\b10\.\d{4,9}/\S+\b', ' ', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text).strip()
    return truncate(text, limit).rstrip(' .;:,') + '.' if text else ''


def _fact_bank(facts: list[str], summary: str) -> list[str]:
    bank = []
    if summary:
        bank.append(_fact_clause(summary, 180))
    for fact in facts:
        bank.append(_fact_clause(fact, 180))
    return distinct_facts(bank, 12)


def _clean_fact_sentence(text: str, limit: int = 180) -> str:
    text = _fact_clause(text, limit)
    text = _strip_agent_prefix(text)
    return collapse_ws(text)


def _fact_for_paragraph(text: str, limit: int = 180, lower: bool = False) -> str:
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
    lead = _clean_fact_sentence(summary or title, 280)
    detail_bank = distinct_facts([_clean_fact_sentence(f, 200) for f in useful[1:]], 10)

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
        p2_bits = [_context_bridge(category, lang)]
        p2_bits.append(_fact_for_paragraph(detail_bank[0], 200))
        if len(detail_bank) > 1:
            p2_bits.append(_fact_for_paragraph(detail_bank[1], 200))
        paragraphs.append(_join_sentences(p2_bits))

    # P3 e P4: Blocos de fatos adicionais (pares)
    remaining = detail_bank[2:8]
    for i in range(0, len(remaining), 2):
        chunk = remaining[i:i + 2]
        if not chunk:
            continue
        sentences = [_fact_for_paragraph(chunk[0], 200)]
        if len(chunk) > 1:
            sentences.append(_fact_for_paragraph(chunk[1], 200))
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
    feed_img = clean_image_url(item.get('feed_img') or '')
    if feed_img and image_url_looks_good(feed_img):
        return feed_img
    if item.get('source_type') != 'preprint':
        page_img = fetch_page_image(item.get('link', ''))
        if page_img and image_url_looks_good(page_img):
            return page_img
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

    title_pt = translate_text(title_en, 'pt')
    summary_pt = translate_text(summary_en, 'pt')
    facts_pt = [translate_text(fact, 'pt') for fact in facts_en[:6]]
    highlights_pt = build_highlights(title_pt, summary_pt, facts_pt, item['source_type'], 'pt')
    body_pt = build_body(title_pt, summary_pt, facts_pt, category, item['source'], item['source_type'], 'pt', src_url)

    dt = item['published']
    slug = slugify(title_en)
    canonical = f'{SITE_URL}?article={slug}'
    image = choose_post_image(item, category)
    is_featured = item['source_type'] != 'preprint' and regular_rank < 3 and profile['band'] in ('flagship', 'high')
    is_trending = item['source_type'] != 'preprint' and regular_rank < 6
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
    <generator>CosmosWeekBot 5.0</generator>
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
    ROBOTS_TXT.write_text(
        f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n',
        encoding='utf-8'
    )


def save_posts(posts: list[dict]) -> None:
    POSTS_JSON.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding='utf-8')
    POSTS_JS.write_text(
        '// Dados atualizados automaticamente para o Cosmos Week\n\nwindow.postsData = ' +
        json.dumps(posts, ensure_ascii=False, indent=2) + ';\n',
        encoding='utf-8'
    )
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
    print(f'\nTotal bruto: {len(items)} itens de {len(SOURCES)} fontes')
    ranked = dedupe_and_rank(items)
    posts = []
    regular_rank = 0
    for idx, item in enumerate(ranked):
        current_rank = regular_rank if item['source_type'] != 'preprint' else 99
        if item['source_type'] != 'preprint':
            regular_rank += 1
        posts.append(to_post(item, idx, current_rank))

    if len(posts) < MIN_PUBLISHABLE_POSTS:
        raise SystemExit(f'Abortado: apenas {len(posts)} posts gerados. Preservando os arquivos atuais.')

    save_posts(posts)
    counts_type = Counter(post['sourceType'] for post in posts)
    counts_cat = Counter(post['cat'] for post in posts)
    print(f'\n{len(posts)} posts salvos — {datetime.now(timezone.utc).isoformat()}')
    print(f'Por tipo de fonte: {dict(counts_type)}')
    print('Por categoria:')
    for cat, n in sorted(counts_cat.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {n}')
    print(f'\nBase do site: {SITE_URL}')

if __name__ == '__main__':
    main()
