#!/usr/bin/env python3
"""Fetch citation stats from the Semantic Scholar Graph API and emit
shields.io endpoint JSON files (one per metric) into ./stats/.

Semantic Scholar is used instead of Google Scholar because Scholar blocks
GitHub Actions runner IPs (CAPTCHA), whereas the S2 API is CI-friendly.
Author is pinned by S2 authorId (ORCID-matched record for Gabriel Devenyi).
"""
import json
import os
import sys
import time
import urllib.request

AUTHOR_ID = "7852314"  # ORCID 0000-0002-7766-1187 (Gabriel A. Devenyi)
FIELDS = "name,paperCount,citationCount,hIndex"
URL = f"https://api.semanticscholar.org/graph/v1/author/{AUTHOR_ID}?fields={FIELDS}"
OUT_DIR = "stats"
COLOR = "blue"


def fetch(url, attempts=5):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gdevenyi-profile"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"attempt {i + 1} failed: {e}", file=sys.stderr)
        time.sleep(15 * (i + 1))  # linear backoff for 429s
    raise SystemExit("Semantic Scholar API unreachable after retries")


def badge(label, message):
    return {"schemaVersion": 1, "label": label, "message": str(message), "color": COLOR}


def main():
    data = fetch(URL)
    os.makedirs(OUT_DIR, exist_ok=True)
    metrics = {
        "citations": badge("citations", f"{data['citationCount']:,}"),
        "hindex": badge("h-index", data["hIndex"]),
        "publications": badge("publications", data["paperCount"]),
    }
    for name, payload in metrics.items():
        path = os.path.join(OUT_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(payload, f)
        print(f"wrote {path}: {payload['message']}")


if __name__ == "__main__":
    main()
