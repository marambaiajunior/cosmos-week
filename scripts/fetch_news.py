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
MAX_PAGE_FETCHES = 28

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
        if len(paragraphs) >= 14:
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
    parts = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for part in parts:
        part = collapse_ws(part).strip(' \"""\'\'\'')
        if len(part) < 35:
            continue
        out.append(part)
    return out


def sentence_score(sentence: str) -> tuple[int, int]:
    low = normalize_text(sentence)
    score = 0
    if re.search(r'\d', sentence):
        score += 4
    if re.search(r'\b(jwst|nasa|esa|jpl|cern|euclid|desi|hubble|rubin|mars|moon|earth|arxiv|eso|nih|noaa)\b', low):
        score += 4
    if re.search(r'\b(first|new|detected|measured|observed|analysis|results|reveals|maps|launch|mission|constraints|published|confirmed)\b', low):
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


def build_deck(summary: str, facts: list[str]) -> str:
    def clean(t: str) -> str:
        t = collapse_ws(t)
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
    """Lowercase first character of a string."""
    return s[0].lower() + s[1:] if len(s) > 1 else s.lower()


def _strip_agent_prefix(s: str) -> str:
    """Remove common agent-lead phrases to avoid double-agent constructions."""
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
    """Short category field name for use in prose."""
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


def _p1_lede(title: str, summary: str, facts: list[str], source_type: str, category: str, lang: str, seed: str) -> str:
    s = truncate(collapse_ws(summary or title), 250)
    f0 = trimmed_fact(facts[0], 220) if facts else s
    cat = _cat_field(category, lang)

    if lang == 'en':
        sc = _strip_agent_prefix(s)
        if source_type == 'preprint':
            opts = [
                f'{s}',
                f'New work in {cat} puts forward a significant finding: {_lc(sc)}',
                f'Researchers have identified something worth a closer look: {_lc(f0)}',
                f'A team studying {cat} reports {_lc(sc)}',
            ]
        elif source_type == 'agency':
            opts = [
                f'{s}',
                f'{sc} The update follows an extended period of data collection and mission operations.',
                f'New findings in {cat}: {_lc(sc)}',
                f'{f0}',
            ]
        else:
            opts = [
                f'{s}',
                f'Published research in {cat} has established: {_lc(sc)}',
                f'A new peer-reviewed study confirms {_lc(sc)}',
                f'{s} The finding, reviewed and published, moves the field a measurable step forward.',
            ]
    else:
        sc = _strip_agent_prefix(s)
        if source_type == 'preprint':
            opts = [
                f'{s}',
                f'Um novo trabalho em {cat} apresenta uma descoberta significativa: {_lc(sc)}',
                f'Pesquisadores identificaram algo que merece atenção cuidadosa: {_lc(f0)}',
                f'Uma equipe que estuda {cat} relata {_lc(sc)}',
            ]
        elif source_type == 'agency':
            opts = [
                f'{s}',
                f'{sc} A atualização é resultado de um extenso período de coleta de dados e operações de missão.',
                f'Novos resultados em {cat}: {_lc(sc)}',
                f'{f0}',
            ]
        else:
            opts = [
                f'{s}',
                f'Uma pesquisa publicada em {cat} estabelece: {_lc(sc)}',
                f'Um novo estudo revisado por pares confirma {_lc(sc)}',
                f'{s} O resultado, revisado e publicado, avança o campo de forma mensurável.',
            ]
    return stable_pick(opts, seed + 'p1')


def _p2_context(summary: str, facts: list[str], category: str, source_type: str, lang: str, seed: str) -> str:
    f0 = trimmed_fact(facts[0], 210) if facts else ''
    cat = _cat_field(category, lang)

    cat_context_en = {
        'Astronomia': 'Astronomy advances by accumulating observations across wavelengths and missions, each result either reinforcing or challenging the models that preceded it.',
        'Cosmologia': 'Cosmology is currently in a productive tension: precision surveys are returning data detailed enough to test the standard model in ways not previously possible.',
        'Astrofísica': 'Astrophysics depends on isolating the physical mechanism behind an observed phenomenon. The difference between a detected signal and an understood process can take years to close.',
        'Exoplanetas': 'Exoplanet science is now large enough to look for patterns across populations, not just individual worlds, which makes each new atmospheric or orbital measurement more valuable than it would have been a decade ago.',
        'Física': 'Physics builds on precision. A result gains credibility not from how surprising it is, but from how well the measurement was controlled and how consistently it reproduces.',
        'Biologia': 'Biology rarely produces results that apply everywhere at once. Understanding what system was studied, under what conditions, is the first step in judging how far the conclusion extends.',
        'Química': 'Chemistry is fundamentally about characterization: the strength of a result depends on how completely and independently the new compound, reaction, or process has been described.',
        'Ciências da Terra': 'Earth science results become meaningful when they can be situated within longer records. A single measurement is a starting point; a trend across instruments and time is evidence.',
    }
    cat_context_pt = {
        'Astronomia': 'A astronomia avança acumulando observações em diferentes comprimentos de onda e missões, cada resultado reforçando ou contestando os modelos que o precederam.',
        'Cosmologia': 'A cosmologia vive uma tensão produtiva: levantamentos de alta precisão estão retornando dados detalhados o suficiente para testar o modelo padrão de formas antes impossíveis.',
        'Astrofísica': 'A astrofísica depende de isolar o mecanismo físico por trás de um fenômeno observado. A diferença entre um sinal detectado e um processo compreendido pode levar anos para ser superada.',
        'Exoplanetas': 'A ciência de exoplanetas é hoje ampla o suficiente para buscar padrões entre populações de planetas, o que torna cada nova medida atmosférica ou orbital mais valiosa do que teria sido uma década atrás.',
        'Física': 'A física se constrói sobre precisão. Um resultado ganha credibilidade não por ser surpreendente, mas pela qualidade do controle experimental e pela consistência de sua reprodução.',
        'Biologia': 'A biologia raramente produz resultados aplicáveis em todos os contextos ao mesmo tempo. Entender qual sistema foi estudado e em quais condições é o primeiro passo para julgar o alcance da conclusão.',
        'Química': 'A química é fundamentalmente sobre caracterização: a solidez de um resultado depende do quão completa e independentemente o novo composto, reação ou processo foi descrito.',
        'Ciências da Terra': 'Os resultados em ciências da Terra ganham sentido quando situados dentro de registros mais longos. Uma única medição é um ponto de partida; uma tendência ao longo de instrumentos e tempo é evidência.',
    }
    ctx = (cat_context_en if lang == 'en' else cat_context_pt).get(category, '')

    if lang == 'en':
        connectors = [
            f'{ctx}',
            f'To place the result in context: {_lc(ctx)}',
            f'The field has been building toward moments like this. {ctx}',
        ]
        if f0:
            tail = [
                f' The current work adds a specific data point: {_lc(f0)}',
                f' This result contributes directly to that effort: {_lc(f0)}',
                '',
            ]
        else:
            tail = ['', '', '']
    else:
        connectors = [
            f'{ctx}',
            f'Para situar o resultado no contexto: {_lc(ctx)}',
            f'O campo vinha se construindo em direção a momentos como este. {ctx}',
        ]
        if f0:
            tail = [
                f' O trabalho atual acrescenta um dado concreto: {_lc(f0)}',
                f' Este resultado contribui diretamente para esse esforço: {_lc(f0)}',
                '',
            ]
        else:
            tail = ['', '', '']

    idx = stable_index(seed + 'p2', len(connectors))
    return connectors[idx] + tail[idx]


def _p3_findings(facts: list[str], category: str, source_type: str, lang: str, seed: str) -> str:
    f1 = trimmed_fact(facts[1], 220) if len(facts) > 1 else ''
    f2 = trimmed_fact(facts[2], 200) if len(facts) > 2 else ''
    if not f1:
        return ''

    if lang == 'en':
        connectors_mid = [
            'On top of that,',
            'The analysis also shows that',
            'A second thread in the data points to the fact that',
            'Complementing this,',
        ]
        openers = [
            f'The underlying data tell a consistent story. {f1}',
            f'When the measurements are examined carefully, a clearer picture emerges. {f1}',
            f'The observational record provides important detail here. {f1}',
            f'{f1}',
        ]
    else:
        connectors_mid = [
            'Além disso,',
            'A análise também mostra que',
            'Um segundo fio nos dados aponta para o fato de que',
            'Em complemento,',
        ]
        openers = [
            f'Os dados subjacentes contam uma história consistente. {f1}',
            f'Quando as medições são examinadas com cuidado, um quadro mais nítido emerge. {f1}',
            f'O registro observacional oferece um detalhe importante aqui. {f1}',
            f'{f1}',
        ]

    opener = stable_pick(openers, seed + 'p3open')
    if f2 and normalize_text(f2) != normalize_text(f1):
        connector = stable_pick(connectors_mid, seed + 'p3conn')
        return f'{opener} {connector} {_lc(f2)}'
    return opener


def _p4_closing(facts: list[str], category: str, source_type: str, lang: str, seed: str) -> str:
    next_steps_en = {
        'Astronomia': 'Independent observations at other wavelengths, or with different instruments, will be the natural next test for this result.',
        'Cosmologia': 'The key question now is whether the effect holds when confronted with other surveys, tighter systematics controls, and independent calibrations.',
        'Astrofísica': 'From here, the real value of the result depends on convergence between independent datasets and physical modeling.',
        'Exoplanetas': 'The next step is to obtain independent constraints on mass, radius, atmosphere, or orbital geometry, which is where a promising target becomes a robustly characterized one.',
        'Física': 'In physics, the final filter is always the same: more data, more scrutiny, and less tolerance for interpretations that survive only under narrow assumptions.',
        'Biologia': 'The next step is to test reproducibility and generalization in other model systems, without mistaking a promising result for a settled answer.',
        'Química': 'The advance solidifies when other techniques and independent groups reproduce the same interpretation with compatible measurements.',
        'Ciências da Terra': 'The most rigorous test will be to situate this result within longer time series and independent instruments, reducing the risk of reading too much into a single data point.',
    }
    next_steps_pt = {
        'Astronomia': 'Observações independentes em outros comprimentos de onda, ou com instrumentos diferentes, serão o próximo teste natural para este resultado.',
        'Cosmologia': 'A pergunta central agora é se o efeito se mantém quando confrontado com outros levantamentos, controles mais rígidos de sistemáticos e calibrações independentes.',
        'Astrofísica': 'A partir daqui, o valor real do resultado depende da convergência entre conjuntos de dados independentes e modelagem física.',
        'Exoplanetas': 'O próximo passo é obter restrições independentes sobre massa, raio, atmosfera ou geometria orbital, que é onde um alvo promissor se torna um alvo robustamente caracterizado.',
        'Física': 'Em física, o filtro final é sempre o mesmo: mais dados, mais escrutínio e menos tolerância a interpretações que sobrevivem apenas sob premissas estreitas.',
        'Biologia': 'O próximo passo é testar reprodutibilidade e generalização em outros sistemas modelo, sem confundir um resultado promissor com uma resposta definitiva.',
        'Química': 'O avanço se consolida quando outras técnicas e grupos independentes reproduzem a mesma interpretação com medições compatíveis.',
        'Ciências da Terra': 'O teste mais rigoroso será situar este resultado em séries temporais mais longas e instrumentos independentes, reduzindo o risco de extrair conclusões excessivas de um único ponto de dados.',
    }

    next_step = (next_steps_en if lang == 'en' else next_steps_pt).get(
        category, (next_steps_en if lang == 'en' else next_steps_pt)['Astronomia']
    )

    if lang == 'en':
        if source_type == 'preprint':
            opts = [
                f'{next_step} The work has not yet been through formal peer review, so it is best treated as a preliminary result until that evaluation is complete.',
                f'Before any of this, the study still has to clear peer review, the process through which independent experts evaluate whether the methodology and claims hold up. {next_step}',
                f'One important caveat: the work is a preprint, meaning the broader scientific community has not yet had the chance to formally scrutinize it. {next_step}',
            ]
        elif source_type == 'agency':
            opts = [
                f'{next_step}',
                f'The announcement opens a productive path for follow-up. {next_step}',
                f'Independent observations will now determine how well the result holds under different conditions. {next_step}',
            ]
        else:
            opts = [
                f'{next_step}',
                f'The published result now invites replication and extension. {next_step}',
                f'As is typical in this field, the findings are now a target for independent follow-up. {next_step}',
            ]
    else:
        if source_type == 'preprint':
            opts = [
                f'{next_step} O trabalho ainda não passou pela revisão por pares formal, por isso é mais adequado tratá-lo como um resultado preliminar até que essa avaliação seja concluída.',
                f'Antes de qualquer conclusão mais ampla, o estudo ainda precisa passar pela revisão por pares, o processo pelo qual especialistas independentes avaliam se a metodologia e as afirmações são consistentes. {next_step}',
                f'Um ponto importante: o trabalho é um preprint, o que significa que a comunidade científica ainda não teve a oportunidade de examiná-lo formalmente. {next_step}',
            ]
        elif source_type == 'agency':
            opts = [
                f'{next_step}',
                f'O anúncio abre um caminho produtivo para trabalhos de acompanhamento. {next_step}',
                f'Observações independentes determinarão agora com que firmeza o resultado se sustenta em diferentes condições. {next_step}',
            ]
        else:
            opts = [
                f'{next_step}',
                f'O resultado publicado agora convida à replicação e extensão. {next_step}',
                f'Como é habitual neste campo, os resultados são agora um alvo para acompanhamento independente. {next_step}',
            ]
    return stable_pick(opts, seed + 'p4')


def build_body(title: str, summary: str, facts: list[str], category: str, source: str,
               source_type: str, lang: str, src_url: str) -> str:
    seed = title + lang
    useful = distinct_facts(facts, 5)

    p1 = _p1_lede(title, summary, useful, source_type, category, lang, seed)
    p2 = _p2_context(summary, useful, category, source_type, lang, seed)
    p3 = _p3_findings(useful, category, source_type, lang, seed)
    p4 = _p4_closing(useful, category, source_type, lang, seed)

    parts = []
    for p in [p1, p2, p3, p4]:
        if p and len(p.strip()) > 30:
            parts.append(f'<p>{html.escape(p.strip())}</p>')

    # Source credit — link only, at the end of the article
    if src_url:
        label = 'Fonte' if lang == 'pt' else 'Source'
        parts.append(f'<p class="art-source"><a href="{html.escape(src_url)}" target="_blank" rel="noopener noreferrer">{label}</a></p>')

    return ''.join(parts)


def build_highlights(title: str, summary: str, facts: list[str], source_type: str, lang: str) -> list[str]:
    useful = distinct_facts(facts, 2)
    if lang == 'pt':
        bullets = [f'Ponto central: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Dado-chave: {trimmed_fact(useful[0], 145)}')
        caution = {
            'preprint': 'Resultado ainda sem revisão por pares.',
            'agency': 'Origem institucional: distinguir anúncio de evidência.',
            'journal': 'Material com lastro científico publicado.',
        }[source_type]
        bullets.append(caution)
    else:
        bullets = [f'Core point: {trimmed_fact(summary or title, 150)}']
        if useful:
            bullets.append(f'Key detail: {trimmed_fact(useful[0], 145)}')
        caution = {
            'preprint': 'Result not yet peer reviewed.',
            'agency': 'Institutional origin: separate announcement from evidence.',
            'journal': 'Material with published scientific backing.',
        }[source_type]
        bullets.append(caution)
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
