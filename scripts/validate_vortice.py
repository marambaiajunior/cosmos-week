#!/usr/bin/env python3
"""Reproducible acceptance checks for the Vórtice Maligno pages.

The script deliberately uses only the Python standard library. Pillow is used
opportunistically to verify responsive image dimensions when it is available.
Run from the repository root with:

    python3 scripts/validate_vortice.py
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BOOK_PATH = ROOT / "livro" / "vortice-maligno" / "index.html"
GUIDE_PATH = ROOT / "livro" / "vortice-maligno" / "checklist" / "index.html"
BOOK_URL = "https://www.cosmosweek.com/livro/vortice-maligno/"
GUIDE_URL = f"{BOOK_URL}checklist/"
STORE_URL = "https://clubedeautores.com.br/livro/vortice-maligno"
IMAGE_ROOT = ROOT / "assets" / "img" / "livro"
EXPECTED_WIDTHS = (320, 480, 640, 960, 1280)
OLD_ISBN_PATTERNS = (
    re.compile(r"978[-–— ]?65[-–— ]?02[-–— ]?26650[-–— ]?2", re.I),
    re.compile("97865" + "02266502"),
)


def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in attrs}


@dataclass
class HtmlDocument:
    html_attrs: dict[str, str] = field(default_factory=dict)
    titles: list[str] = field(default_factory=list)
    meta: list[dict[str, str]] = field(default_factory=list)
    links: list[dict[str, str]] = field(default_factory=list)
    headings: list[tuple[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    sources: list[dict[str, str]] = field(default_factory=list)
    anchors: list[dict[str, str]] = field(default_factory=list)
    scripts: list[dict[str, str]] = field(default_factory=list)
    forms: int = 0
    text: str = ""


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doc = HtmlDocument()
        self.stack: list[str] = []
        self.title_buffer: list[str] | None = None
        self.heading_tag = ""
        self.heading_buffer: list[str] | None = None
        self.script_attrs: dict[str, str] | None = None
        self.script_buffer: list[str] | None = None
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = attrs_dict(attrs)
        tag = tag.lower()
        self.stack.append(tag)
        if tag == "html":
            self.doc.html_attrs = values
        elif tag == "title":
            self.title_buffer = []
        elif tag == "meta":
            self.doc.meta.append(values)
        elif tag == "link":
            self.doc.links.append(values)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_tag = tag
            self.heading_buffer = []
        elif tag == "img":
            self.doc.images.append(values)
        elif tag == "source":
            self.doc.sources.append(values)
        elif tag == "a":
            self.doc.anchors.append(values)
        elif tag == "script":
            self.script_attrs = values
            self.script_buffer = []
        elif tag == "form":
            self.doc.forms += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_chunks.append(data)
        if self.title_buffer is not None:
            self.title_buffer.append(data)
        if self.heading_buffer is not None:
            self.heading_buffer.append(data)
        if self.script_buffer is not None:
            self.script_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self.title_buffer is not None:
            self.doc.titles.append("".join(self.title_buffer).strip())
            self.title_buffer = None
        elif tag == self.heading_tag and self.heading_buffer is not None:
            self.doc.headings.append((tag, " ".join("".join(self.heading_buffer).split())))
            self.heading_tag = ""
            self.heading_buffer = None
        elif tag == "script" and self.script_attrs is not None:
            self.doc.scripts.append({**self.script_attrs, "text": "".join(self.script_buffer or [])})
            self.script_attrs = None
            self.script_buffer = None
        if self.stack:
            self.stack.pop()

    def close(self) -> None:
        super().close()
        self.doc.text = " ".join(" ".join(self.text_chunks).split())


def parse_html(path: Path) -> tuple[str, HtmlDocument]:
    raw = path.read_text(encoding="utf-8")
    parser = AuditParser()
    parser.feed(raw)
    parser.close()
    return raw, parser.doc


def meta_values(doc: HtmlDocument, *, name: str = "", prop: str = "") -> list[str]:
    result = []
    for item in doc.meta:
        if name and item.get("name", "").lower() != name.lower():
            continue
        if prop and item.get("property", "").lower() != prop.lower():
            continue
        result.append(item.get("content", ""))
    return result


def links_by_rel(doc: HtmlDocument, rel: str) -> list[dict[str, str]]:
    return [item for item in doc.links if rel.lower() in item.get("rel", "").lower().split()]


def classes(item: dict[str, str]) -> set[str]:
    return set(item.get("class", "").split())


def local_asset(url: str) -> Path | None:
    if not url.startswith("/") or url.startswith("//"):
        return None
    return ROOT / url.split("?", 1)[0].lstrip("/")


def srcset_urls(value: str) -> Iterable[tuple[str, str]]:
    for candidate in value.split(","):
        parts = candidate.strip().split()
        if parts:
            yield parts[0], parts[1] if len(parts) > 1 else ""


def json_ld_nodes(doc: HtmlDocument) -> list[dict]:
    nodes: list[dict] = []
    for script in doc.scripts:
        if script.get("type", "").lower() != "application/ld+json":
            continue
        payload = json.loads(script.get("text", ""))
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            nodes.extend(node for node in payload["@graph"] if isinstance(node, dict))
        elif isinstance(payload, dict):
            nodes.append(payload)
    return nodes


def node_of_type(nodes: list[dict], schema_type: str) -> dict:
    return next((node for node in nodes if node.get("@type") == schema_type), {})


@dataclass
class Result:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def check(self, condition: bool, label: str) -> None:
        (self.passed if condition else self.failed).append(label)


def check_metadata(result: Result, doc: HtmlDocument, *, title: str, canonical: str) -> None:
    result.check(doc.html_attrs.get("lang") == "pt-BR", f"{canonical}: html lang=pt-BR")
    result.check(doc.titles == [title], f"{canonical}: exactly one expected title")
    result.check(len(meta_values(doc, name="description")) == 1, f"{canonical}: exactly one meta description")
    result.check(len(meta_values(doc, name="robots")) == 1 and "index" in meta_values(doc, name="robots")[0], f"{canonical}: indexable robots meta")
    canonical_links = links_by_rel(doc, "canonical")
    result.check(len(canonical_links) == 1 and canonical_links[0].get("href") == canonical, f"{canonical}: one absolute canonical")
    alternates = {(item.get("hreflang"), item.get("href")) for item in links_by_rel(doc, "alternate")}
    result.check({("pt-BR", canonical), ("x-default", canonical)} <= alternates, f"{canonical}: pt-BR and x-default hreflang")
    result.check(sum(1 for level, _ in doc.headings if level == "h1") == 1, f"{canonical}: exactly one h1")
    result.check(len(links_by_rel(doc, "icon")) == 1 and links_by_rel(doc, "icon")[0].get("href") == "/assets/favicon.svg", f"{canonical}: favicon declared")
    result.check(any(item.get("rel") == "manifest" and item.get("href") == "/site.webmanifest" for item in doc.links), f"{canonical}: web manifest declared")
    result.check(meta_values(doc, prop="article:modified_time") == ["2026-08-27"], f"{canonical}: legitimate lastmod metadata")


def check_social(result: Result, doc: HtmlDocument, *, canonical: str, og_type: str) -> None:
    expected = {
        "og:type": og_type,
        "og:site_name": "Cosmos Week",
        "og:locale": "pt_BR",
        "og:url": canonical,
        "og:image": "https://www.cosmosweek.com/assets/img/livro/vortice-maligno-og.jpg",
        "og:image:type": "image/jpeg",
        "og:image:width": "1200",
        "og:image:height": "630",
    }
    for prop, value in expected.items():
        result.check(meta_values(doc, prop=prop) == [value], f"{canonical}: {prop}={value}")
    result.check(len(meta_values(doc, prop="og:image:alt")) == 1 and bool(meta_values(doc, prop="og:image:alt")[0]), f"{canonical}: og:image:alt")
    result.check(meta_values(doc, name="twitter:card") == ["summary_large_image"], f"{canonical}: Twitter large card")
    result.check(len(meta_values(doc, name="twitter:title")) == 1, f"{canonical}: Twitter title")
    result.check(len(meta_values(doc, name="twitter:description")) == 1, f"{canonical}: Twitter description")
    result.check(meta_values(doc, name="twitter:image") == [expected["og:image"]], f"{canonical}: Twitter image")
    result.check(len(meta_values(doc, name="twitter:image:alt")) == 1 and bool(meta_values(doc, name="twitter:image:alt")[0]), f"{canonical}: twitter:image:alt")


def check_images(result: Result, raw: str, doc: HtmlDocument, *, page_label: str) -> None:
    result.check(bool(doc.images), f"{page_label}: images present")
    result.check(all("alt" in image for image in doc.images), f"{page_label}: every image has alt")
    result.check(all(image.get("width", "").isdigit() and image.get("height", "").isdigit() for image in doc.images), f"{page_label}: intrinsic dimensions on every image")
    result.check("<picture" in raw and "srcset=" in raw and "sizes=" in raw, f"{page_label}: responsive picture/srcset/sizes markup")
    for image in doc.images:
        path = local_asset(image.get("src", ""))
        if path:
            result.check(path.is_file(), f"{page_label}: asset exists {image.get('src')}")
    for source in doc.sources:
        result.check(bool(source.get("type")) and bool(source.get("srcset")) and bool(source.get("sizes")), f"{page_label}: responsive source is complete")
        for url, descriptor in srcset_urls(source.get("srcset", "")):
            path = local_asset(url)
            result.check(path is not None and path.is_file(), f"{page_label}: srcset asset exists {url}")
            result.check(bool(re.fullmatch(r"\d+w", descriptor)), f"{page_label}: width descriptor for {url}")


def check_markup(result: Result, raw: str, doc: HtmlDocument, *, page_label: str) -> None:
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', raw, re.I)
    result.check(len(ids) == len(set(ids)), f"{page_label}: no duplicate HTML ids")
    labelled = re.findall(r'\baria-labelledby=["\']([^"\']+)["\']', raw, re.I)
    result.check(all(token in set(ids) for value in labelled for token in value.split()), f"{page_label}: aria-labelledby references exist")
    buttons = re.findall(r'<button\b([^>]*)>', raw, re.I)
    result.check(all(re.search(r'\btype=["\'](?:button|submit|reset)["\']', attrs, re.I) for attrs in buttons), f"{page_label}: every button has an explicit type")
    blank_links = [item for item in doc.anchors if item.get("target") == "_blank"]
    result.check(all({"noopener", "noreferrer"} <= set(item.get("rel", "").split()) for item in blank_links), f"{page_label}: every new-tab link is protected")


def check_book(result: Result, raw: str, doc: HtmlDocument) -> None:
    check_metadata(
        result,
        doc,
        title="Vórtice Maligno | Livro sobre pseudociência e desinformação",
        canonical=BOOK_URL,
    )
    check_social(result, doc, canonical=BOOK_URL, og_type="book")
    check_images(result, raw, doc, page_label="landing")
    check_markup(result, raw, doc, page_label="landing")

    result.check("Capa do livro Vórtice Maligno, de Humberto Marambaia Junior" in [item.get("alt") for item in doc.images], "landing: descriptive cover alt")
    result.check("Retrato de Humberto Marambaia Junior" in [item.get("alt") for item in doc.images], "landing: descriptive portrait alt")
    logo = next((item for item in doc.images if "book-page-logo-avatar" in classes(item)), {})
    result.check((logo.get("width"), logo.get("height")) == ("150", "150"), "landing: logo intrinsic 150x150 dimensions")
    hero = next((item for item in doc.images if "book-cover" in classes(item)), {})
    result.check(hero.get("fetchpriority") == "high" and hero.get("loading") != "lazy", "landing: hero is eager LCP candidate")
    portrait = next((item for item in doc.images if "book-author-portrait" in classes(item)), {})
    final_cover = next((item for item in doc.images if "book-final-cover" in classes(item)), {})
    result.check(portrait.get("loading") == "lazy" and portrait.get("decoding") == "async", "landing: author portrait is lazy")
    result.check(final_cover.get("loading") == "lazy" and final_cover.get("decoding") == "async", "landing: final cover is lazy")

    store_links = [item for item in doc.anchors if "data-book-store" in item]
    result.check(bool(store_links) and all(item.get("href") == STORE_URL for item in store_links), "landing: every store CTA uses Clube de Autores")
    result.check(all({"noopener", "noreferrer"} <= set(item.get("rel", "").split()) for item in store_links if item.get("target") == "_blank"), "landing: external store links are protected")
    cta_locations = {item.get("data-book-cta") for item in store_links}
    result.check({"header", "hero", "sticky_mobile", "final_cta"} <= cta_locations, "landing: conversion locations are distinguishable")

    analytics_tags = [script for script in doc.scripts if script.get("src") == "/assets/js/cw-analytics.js"]
    result.check(len(analytics_tags) == 1 and analytics_tags[0].get("data-ga-id") == "G-MX20J1ZG06", "landing: one GA4 loader with the public ID")
    result.check("googletagmanager.com/gtag/js" not in raw, "landing: no second inline GA loader")
    result.check(doc.forms == 0, "landing: forms not applicable")
    result.check(raw.count("<details>") == raw.count("<summary>") == 6, "landing: six native keyboard-operable FAQ entries")

    nodes = json_ld_nodes(doc)
    result.check({"WebPage", "Book", "FAQPage", "BreadcrumbList"} <= {node.get("@type") for node in nodes}, "landing: required JSON-LD graph nodes")
    webpage = node_of_type(nodes, "WebPage")
    book = node_of_type(nodes, "Book")
    offer = book.get("offers", {}) if isinstance(book.get("offers"), dict) else {}
    result.check(book.get("isbn") == "9786526681633", "landing: JSON-LD ISBN")
    result.check(book.get("numberOfPages") == 314, "landing: JSON-LD page count")
    result.check(book.get("bookEdition") == "1ª edição (2026)", "landing: JSON-LD edition")
    result.check(webpage.get("dateModified") == "2026-08-27", "landing: JSON-LD dateModified")
    result.check(offer.get("url") == STORE_URL and offer.get("price") == "59.12" and offer.get("priceCurrency") == "BRL", "landing: JSON-LD offer")
    result.check(offer.get("seller", {}).get("name") == "Clube de Autores", "landing: JSON-LD seller")
    result.check(offer.get("availability") == "https://schema.org/InStock", "landing: JSON-LD availability")
    faq = node_of_type(nodes, "FAQPage")
    questions = [item.get("name", "") for item in faq.get("mainEntity", []) if isinstance(item, dict)]
    result.check(bool(questions) and all(question in doc.text for question in questions), "landing: every FAQ schema question is visible")


def check_guide(result: Result, raw: str, doc: HtmlDocument) -> None:
    check_metadata(
        result,
        doc,
        title="Checklist: 7 perguntas antes de acreditar ou compartilhar",
        canonical=GUIDE_URL,
    )
    check_social(result, doc, canonical=GUIDE_URL, og_type="article")
    check_images(result, raw, doc, page_label="checklist")
    check_markup(result, raw, doc, page_label="checklist")
    result.check(doc.forms == 0, "checklist: no artificial form")
    nodes = json_ld_nodes(doc)
    result.check({"WebPage", "CreativeWork", "BreadcrumbList"} <= {node.get("@type") for node in nodes}, "checklist: required JSON-LD graph nodes")
    webpage = node_of_type(nodes, "WebPage")
    work = node_of_type(nodes, "CreativeWork")
    result.check(webpage.get("dateModified") == "2026-08-27", "checklist: WebPage dateModified")
    result.check(work.get("dateModified") == "2026-08-27", "checklist: JSON-LD dateModified")


def check_responsive_assets(result: Result) -> None:
    try:
        from PIL import Image
    except ImportError:
        for extension in ("avif", "webp"):
            for width in EXPECTED_WIDTHS:
                path = IMAGE_ROOT / f"vortice-maligno-capa-{width}.{extension}"
                result.check(path.is_file() and path.stat().st_size > 0, f"responsive assets: {path.name} exists (dimensions require Pillow)")
        return
    for extension in ("avif", "webp"):
        for width in EXPECTED_WIDTHS:
            path = IMAGE_ROOT / f"vortice-maligno-capa-{width}.{extension}"
            result.check(path.is_file(), f"responsive assets: {path.name} exists")
            if path.is_file():
                with Image.open(path) as image:
                    result.check(image.width == width and image.height == round(width * 1.6), f"responsive assets: {path.name} dimensions")
    og = IMAGE_ROOT / "vortice-maligno-og.jpg"
    cover_jpg = IMAGE_ROOT / "vortice-maligno-capa.jpg"
    with Image.open(og) as image:
        result.check(image.size == (1200, 630) and image.format == "JPEG", "responsive assets: OG remains JPEG 1200x630")
    with Image.open(cover_jpg) as image:
        result.check(image.size == (1280, 2048) and image.format == "JPEG", "responsive assets: JSON-LD cover JPG remains 1280x2048")


def check_infrastructure(result: Result) -> None:
    favicon = ROOT / "assets" / "favicon.svg"
    result.check(favicon.is_file() and "<svg" in favicon.read_text(encoding="utf-8"), "infrastructure: SVG favicon exists")
    manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    result.check(any(icon.get("src") == "/assets/favicon.svg" for icon in manifest.get("icons", [])), "infrastructure: manifest references favicon")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    result.check("User-agent: *" in robots and "Allow: /" in robots, "infrastructure: robots allows public crawling")
    result.check("Sitemap: https://www.cosmosweek.com/sitemap.xml" in robots, "infrastructure: robots declares canonical sitemap")

    sitemap = ElementTree.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    rows = []
    for node in sitemap.findall("sm:url", namespace):
        loc = node.findtext("sm:loc", default="", namespaces=namespace)
        lastmod = node.findtext("sm:lastmod", default="", namespaces=namespace)
        rows.append((loc, lastmod))
    urls = [loc for loc, _ in rows]
    result.check(len(urls) == len(set(urls)), "infrastructure: sitemap has no duplicate URLs")
    result.check((BOOK_URL, "2026-08-27") in rows, "infrastructure: landing in sitemap with real lastmod")
    result.check((GUIDE_URL, "2026-08-27") in rows, "infrastructure: checklist in sitemap with real lastmod")

    raw_404, doc_404 = parse_html(ROOT / "404.html")
    result.check(doc_404.titles == ["Página não encontrada | Cosmos Week"], "infrastructure: custom 404 title")
    result.check(("h1", "Esta órbita não existe.") in doc_404.headings, "infrastructure: custom 404 h1")
    result.check(meta_values(doc_404, name="robots") == ["noindex,follow"], "infrastructure: custom 404 noindex,follow")
    result.check(not links_by_rel(doc_404, "canonical"), "infrastructure: custom 404 has no canonical")
    result.check('href="/"' in raw_404, "infrastructure: custom 404 return link")

    result.check(GUIDE_PATH.is_file(), "infrastructure: lowercase checklist route exists")
    result.check(not (ROOT / "Livro" / "vortice-maligno" / "checklist" / "index.html").exists(), "infrastructure: no conflicting uppercase checklist route")


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check_accessibility_css(result: Result) -> None:
    css = (ROOT / "assets" / "css" / "book.css").read_text(encoding="utf-8")
    result.check(re.search(r"body\.book-page,\s*body\.book-guide-page\s*\{[^}]*overflow-x:clip", css, re.S) is not None, "responsive CSS: overflow clipped only on book experiences")
    result.check("overflow-x:hidden" not in css.replace(" ", ""), "responsive CSS: no global overflow-x hidden workaround")
    result.check(re.search(r"\.book-btn\s*\{[^}]*min-height:52px", css, re.S) is not None, "accessibility CSS: primary CTA target is at least 52px")
    result.check(re.search(r"\.book-page \.book-buy-mini,\s*\.book-guide-page \.book-buy-mini\s*\{[^}]*min-height:44px", css, re.S) is not None, "accessibility CSS: header CTA target is at least 44px")
    result.check(re.search(r"\.book-sticky-bar a\s*\{[^}]*min-height:44px", css, re.S) is not None, "accessibility CSS: sticky CTA target is at least 44px")
    result.check("env(safe-area-inset-bottom)" in css, "accessibility CSS: mobile safe area compensation")
    result.check("@media(prefers-reduced-motion:reduce)" in css, "accessibility CSS: reduced motion support")
    result.check(contrast_ratio("#59697b", "#f7f4ef") >= 4.5, "accessibility CSS: header navigation contrast >= 4.5:1")
    result.check(contrast_ratio("#66554b", "#ead7bc") >= 4.5, "accessibility CSS: purchase note contrast >= 4.5:1")
    result.check(contrast_ratio("#6f665f", "#f7f3ed") >= 4.5, "accessibility CSS: footer contrast >= 4.5:1")


def check_related_forms(result: Result) -> None:
    for path in (ROOT / "contato" / "index.html", ROOT / "en" / "contact" / "index.html"):
        _, doc = parse_html(path)
        result.check(doc.forms == 0, f"forms: {path.relative_to(ROOT)} has no functional form (not applicable)")


def check_obsolete_content(result: Result) -> None:
    text_suffixes = {".html", ".json", ".js", ".mjs", ".py", ".xml", ".txt", ".md", ".yml", ".yaml"}
    old_isbn_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in OLD_ISBN_PATTERNS):
            old_isbn_hits.append(str(path.relative_to(ROOT)))
    result.check(not old_isbn_hits, f"content: old ISBN absent ({', '.join(old_isbn_hits) or 'no hits'})")

    scoped = {
        *ROOT.glob("*VORTICE*"),
        *ROOT.glob("*Vortice*"),
        *ROOT.glob("AJUSTES-LANDING-VORTICE*"),
        ROOT / "livro" / "vortice-maligno" / "index.html",
        GUIDE_PATH,
        ROOT / "assets" / "js" / "book.js",
    }
    amazon_urls = []
    for path in scoped:
        if path.is_file() and re.search(r"https?://(?:www\.)?amazon\.", path.read_text(encoding="utf-8", errors="ignore"), re.I):
            amazon_urls.append(str(path.relative_to(ROOT)))
    result.check(not amazon_urls, f"content: obsolete Amazon purchase URLs absent ({', '.join(amazon_urls) or 'no hits'})")


def check_scripts(result: Result) -> None:
    book_js = (ROOT / "assets" / "js" / "book.js").read_text(encoding="utf-8")
    analytics_js = (ROOT / "assets" / "js" / "cw-analytics.js").read_text(encoding="utf-8")
    for event in ("book_cta_click", "book_store_click", "book_guide_click", "book_guide_share"):
        result.check(event in book_js, f"analytics: {event} is implemented")
    result.check("window.cwHasAnalyticsConsent" in analytics_js, "analytics: consent state is exposed")
    result.check("if (!hasAnalyticsConsent()) return;" in analytics_js, "analytics: page views are blocked without consent")
    result.check("loadGoogleTag();" in analytics_js and "enableAnalytics" in analytics_js, "analytics: Google tag loads only through consent activation")
    result.check("G-MX20J1ZG06" in analytics_js, "analytics: expected GA4 public ID")
    result.check(not re.search(r"(?:user_name|user_email|email|e-mail)\s*:", book_js, re.I), "analytics: no explicit name/email event parameters")


def main() -> int:
    result = Result()
    try:
        book_raw, book_doc = parse_html(BOOK_PATH)
        check_book(result, book_raw, book_doc)
    except Exception as error:
        result.failed.append(f"landing: parser failure: {error}")
    try:
        guide_raw, guide_doc = parse_html(GUIDE_PATH)
        check_guide(result, guide_raw, guide_doc)
    except Exception as error:
        result.failed.append(f"checklist: parser failure: {error}")

    for check in (check_responsive_assets, check_infrastructure, check_accessibility_css, check_related_forms, check_obsolete_content, check_scripts):
        try:
            check(result)
        except Exception as error:
            result.failed.append(f"{check.__name__}: {error}")

    print(f"PASS {len(result.passed)}")
    for label in result.passed:
        print(f"  ✓ {label}")
    print(f"FAIL {len(result.failed)}")
    for label in result.failed:
        print(f"  ✗ {label}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())
