#!/usr/bin/env python3
"""List works on your ORCID record that are not yet in content/cv.yaml.

    python fetch_orcid.py                      # uses the ORCID link in cv.yaml
    python fetch_orcid.py 0000-0002-2938-6184

Uses the public ORCID API (no login). Prints YAML stubs you can paste into
content/cv.yaml; authors are not included in the summary endpoint, so fill
them in by hand. Google Scholar has no public API and blocks scraping, so it
is not queried; use Scholar's "Export" (BibTeX) if you want to compare.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

#import yaml
from ruamel.yaml import YAML
yaml = YAML() # defaults v1.2 accepts comments

ROOT = Path(__file__).parent


def orcid_id(cv: dict) -> str:
    for link in cv["person"].get("links", []):
        m = re.search(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", link["url"])
        if m:
            return m.group(0)
    sys.exit("No ORCID id found in cv.yaml; pass it as an argument.")


def works(oid: str) -> list[dict]:
    req = urllib.request.Request(
        f"https://pub.orcid.org/v3.0/{oid}/works", headers={"Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = []
    for g in data.get("group", []):
        s = g["work-summary"][0]
        ids = {e["external-id-type"]: e["external-id-value"]
               for e in (s.get("external-ids") or {}).get("external-id", [])}
        date = s.get("publication-date") or {}
        out.append({
            "title": s["title"]["title"]["value"],
            "year": int(date["year"]["value"]) if date.get("year") else None,
            "venue": (s.get("journal-title") or {}).get("value", ""),
            "doi": ids.get("doi", "").lower() or None,
            "arxiv": ids.get("arxiv"),
        })
    return sorted(out, key=lambda w: w["year"] or 0, reverse=True)


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def main() -> None:
    cv = yaml.load((ROOT / "content" / "cv.yaml").read_text())
    oid = sys.argv[1] if len(sys.argv) > 1 else orcid_id(cv)
    have_doi, have_title = set(), set()
    for g in cv.get("publications", []):
        for p in g["items"]:
            if p.get("doi"):
                have_doi.add(p["doi"].lower())
            have_title.add(norm(p["title"]))

    missing = [w for w in works(oid)
               if not (w["doi"] and w["doi"] in have_doi) and norm(w["title"]) not in have_title]
    print(f"# {len(missing)} ORCID works not in cv.yaml ({oid})\n")
    for w in missing:
        stub = {k: v for k, v in {**w, "authors": ["TODO"]}.items() if v}
        yaml.dump([stub], sys.stdout)
        print()


if __name__ == "__main__":
    main()
