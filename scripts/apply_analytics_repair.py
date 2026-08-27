#!/usr/bin/env python3
"""Apply the Cosmos Week Analytics repair to every existing HTML file.

Run from the repository root:

    python scripts/apply_analytics_repair.py

This script is idempotent: running it more than once will not duplicate the
Analytics tag.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GA_MEASUREMENT_ID = 'G-MX20J1ZG06'
ANALYTICS_TAG = f'  <script src="/assets/js/cw-analytics.js" data-ga-id="{GA_MEASUREMENT_ID}"></script>\n'

OLD_GTAG_RE = re.compile(
    r"""\s*<script\s+async(?:=(?:""|"async"|'async'))?\s+src=["']https://www\.googletagmanager\.com/gtag/js\?id=G-MX20J1ZG06["']\s*></script>\s*<script>.*?gtag\(\s*["']config["']\s*,\s*["']G-MX20J1ZG06["'].*?</script>\s*""",
    re.IGNORECASE | re.DOTALL,
)

INLINE_GTAG_RE = re.compile(
    r"\s*<script(?:\s+[^>]*)?>(?P<body>.*?)</script>\s*",
    re.IGNORECASE | re.DOTALL,
)


def remove_legacy_inline_gtag(match: re.Match[str]) -> str:
    """Remove only the old self-contained GA bootstrap, preserving other JS."""
    body = match.group('body')
    is_legacy_bootstrap = (
        GA_MEASUREMENT_ID in body
        and re.search(r"function\s+gtag\s*\(\s*\)", body)
        and re.search(r"gtag\s*\(\s*['\"]config['\"]", body)
    )
    return '\n' if is_legacy_bootstrap else match.group(0)


def patch_html(path: Path) -> bool:
    original = path.read_text(encoding='utf-8', errors='ignore')
    text = original

    if 'googletagmanager.com/gtag/js?id=G-MX20J1ZG06' in text:
        text = OLD_GTAG_RE.sub('\n', text)

    text = INLINE_GTAG_RE.sub(remove_legacy_inline_gtag, text)

    is_noindex = re.search(
        r'<meta\b[^>]*\bname=["\']robots["\'][^>]*\bcontent=["\'][^"\']*noindex',
        text,
        re.IGNORECASE,
    ) is not None

    if '/assets/js/cw-analytics.js' not in text and not is_noindex:
        text = re.sub(r'(<head\b[^>]*>\s*)', r'\1' + ANALYTICS_TAG, text, count=1, flags=re.IGNORECASE)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main() -> None:
    changed = 0
    scanned = 0

    for path in ROOT.rglob('*.html'):
        if any(part in {'.git', 'node_modules', '.venv', 'venv'} for part in path.parts):
            continue
        scanned += 1
        if patch_html(path):
            changed += 1

    print(f'Analytics repair complete: {changed} HTML files updated / {scanned} scanned.')


if __name__ == '__main__':
    main()
