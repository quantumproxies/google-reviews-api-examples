"""Collector calls for the review examples — run, poll, and stream CSV."""
from __future__ import annotations

import os
import time
from typing import Any

import requests

BASE = "https://api.quanticdata.io/v1"
_s = requests.Session()


def _h() -> dict[str, str]:
    key = os.environ.get("QUANTICDATA_API_KEY")
    if not key:
        raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
    return {"Authorization": f"Bearer {key}"}


def run(slug: str, payload: dict[str, Any]) -> dict:
    r = _s.post(f"{BASE}/scraper/collectors/{slug}/run", json=payload, headers=_h(), timeout=300)
    body = r.json()
    if body.get("type") == "error" or not r.ok:
        raise RuntimeError(f"{slug} ({r.status_code}): {body.get('message')}")
    out = body.get("payload", {})

    while out.get("status") in ("queued", "running"):
        time.sleep(3)
        s = _s.get(f"{BASE}/scraper/collectors/runs/{out['run_id']}", headers=_h(), timeout=60)
        out = s.json().get("payload", {})
    return out


def rows(slug: str, payload: dict[str, Any]) -> list[dict]:
    return run(slug, payload).get("results") or []
