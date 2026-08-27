#!/usr/bin/env python3
"""Serve the static site locally while preserving the custom 404 response."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class CosmosWeekHandler(SimpleHTTPRequestHandler):
    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        if code != 404:
            super().send_error(code, message, explain)
            return

        page = Path(self.directory) / "404.html"
        content = page.read_bytes()
        self.send_response(404, "Not Found")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    handler = partial(CosmosWeekHandler, directory=str(args.root.resolve()))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f"Serving {args.root.resolve()} on {args.bind}:{args.port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
