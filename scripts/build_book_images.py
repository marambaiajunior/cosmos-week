#!/usr/bin/env python3
"""Build responsive AVIF/WebP variants of the Vórtice Maligno cover.

The original 1280×2048 JPG remains untouched because it is the stable image
referenced by Book JSON-LD and may also be useful for print-quality contexts.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "img" / "livro"
SOURCE = IMAGE_DIR / "vortice-maligno-capa.jpg"
WIDTHS = (320, 480, 640, 960, 1280)


def build() -> None:
    with Image.open(SOURCE) as source:
        source.load()
        rgb = source.convert("RGB")
        if rgb.size != (1280, 2048):
            raise SystemExit(f"Capa-fonte inesperada: {rgb.size}; esperado 1280x2048")

        for width in WIDTHS:
            height = round(width * rgb.height / rgb.width)
            image = rgb if width == rgb.width else rgb.resize((width, height), Image.Resampling.LANCZOS)
            outputs = (
                (IMAGE_DIR / f"vortice-maligno-capa-{width}.avif", {"quality": 62, "speed": 6}),
                (IMAGE_DIR / f"vortice-maligno-capa-{width}.webp", {"quality": 82, "method": 6}),
            )
            for path, options in outputs:
                image.save(path, **options)
                print(f"{path.relative_to(ROOT)}\t{path.stat().st_size}\t{width}x{height}")


if __name__ == "__main__":
    build()
