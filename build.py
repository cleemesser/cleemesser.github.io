#!/usr/bin/env python3
"""Build a one-page academic CV site from content/cv.yaml.

    python build.py            # writes _site/
    python build.py --serve    # build, then serve on http://localhost:8000
"""
# %%
from __future__ import annotations

import argparse
import functools
import http.server
import json
import math
import random
import shutil
from pathlib import Path

import markdown
#import yaml
from ruamel.yaml import YAML

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
# %%
yaml = YAML()
ROOT = Path(__file__).parent
OUT = ROOT / "_site"
# %%

# --------------------------------------------------------------------------
# Filters
# --------------------------------------------------------------------------
def md_inline(text: str) -> Markup:
    """Render inline Markdown without the wrapping <p>."""
    html = markdown.markdown(str(text or "").strip())
    if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
        html = html[3:-4]
    return Markup(html)


def author_list(authors: list[str], me: list[str]) -> Markup:
    mine = {m.replace(".", "").strip() for m in me}
    parts = []
    for a in authors:
        key = a.replace(".", "").strip()
        parts.append(f"<strong>{escape(a)}</strong>" if key in mine else str(escape(a)))
    return Markup(", ".join(parts))


# --------------------------------------------------------------------------
# Header figure: a short EEG montage, generated deterministically.
# The last channel carries a sleep spindle (waxing-waning ~13 Hz burst).
# --------------------------------------------------------------------------
def eeg_montage(width=720, channel_h=22, seconds=6.0, fs=120, seed=7) -> Markup:
    labels = ["Fp1–F3", "F3–C3", "C3–P3", "P3–O1", "Fz–Cz", "Cz–Pz"]
    rng = random.Random(seed)
    n = int(seconds * fs)
    label_w = 64
    x_scale = (width - label_w) / (n - 1)
    height = channel_h * len(labels) + 8
    # one faint vertical line per second, as on EEG paper
    grid = [
        f'<line class="sec" x1="{label_w + s * fs * x_scale:.1f}" y1="0" '
        f'x2="{label_w + s * fs * x_scale:.1f}" y2="{height}"/>'
        for s in range(int(seconds) + 1)
    ]
    paths = []
    for ch, label in enumerate(labels):
        # 1/f-like background: sum of sinusoids with random phase
        comps = [(f, 1.0 / f ** 0.9, rng.uniform(0, 2 * math.pi))
                 for f in (0.7, 1.3, 2.1, 3.4, 5.2, 7.9, 10.1, 16.0, 23.0)]
        spindle = ch == len(labels) - 1
        y0 = 4 + channel_h * (ch + 0.5)
        pts = []
        for i in range(n):
            t = i / fs
            v = sum(a * math.sin(2 * math.pi * f * t + p) for f, a, p in comps)
            v += rng.gauss(0, 0.05)
            if spindle:
                env = math.exp(-((t - 3.6) ** 2) / (2 * 0.28 ** 2))
                v += 1.4 * env * math.sin(2 * math.pi * 13.0 * t)
            pts.append((label_w + i * x_scale, y0 - v * channel_h * 0.2))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        cls = "trace trace--spindle" if spindle else "trace"
        paths.append(
            f'<text class="montage-label" x="0" y="{y0 + 3:.1f}">{label}</text>'
            f'<path class="{cls}" d="{d}"/>'
        )
    svg = (
        f'<svg class="montage" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Six channels of EEG; the bottom channel shows a sleep spindle" '
        f'>{"".join(grid)}{"".join(paths)}</svg>'
    )
    return Markup(svg)


# --------------------------------------------------------------------------
# Structured data for search engines
# --------------------------------------------------------------------------
def json_ld(cv: dict) -> Markup:
    p = cv["person"]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": p["name"],
        "honorificSuffix": p.get("postnominals", ""),
        "jobTitle": p.get("role", ""),
        "email": f"mailto:{p['email']}" if p.get("email") else None,
        "sameAs": [l["url"] for l in p.get("links", [])],
        "affiliation": {"@type": "Organization", "name": "Stanford University"},
    }
    data = {k: v for k, v in data.items() if v}
    return Markup(json.dumps(data, ensure_ascii=False, indent=2))


# --------------------------------------------------------------------------
def build() -> None:
    cv = yaml.load((ROOT / "content" / "cv.yaml").read_text(encoding="utf-8"))

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["md"] = md_inline
    env.filters["authors"] = lambda a: author_list(a, cv.get("me", []))

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    (OUT / ".nojekyll").touch()  # tell GitHub Pages to serve files as-is

    html = env.get_template("index.html").render(
        cv=cv,
        # montage=eeg_montage(), # disable
        json_ld=json_ld(cv)
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")

    n = sum(len(g["items"]) for g in cv.get("publications", []))
    print(f"Built {OUT/'index.html'} ({n} publications)")


def serve(port: int = 8000) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Serving on http://localhost:{port}  (Ctrl-C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--serve", action="store_true", help="serve _site after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build()
    if args.serve:
        serve(args.port)
