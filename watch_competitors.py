"""Watch several places and only pay for reviews you have not seen.

sort_by="newest" plus a stored high-water mark per place means each run pulls a
small page and stops. Run it daily from cron; the state file is plain JSON.

    python3 watch_competitors.py places.json --state seen.json
    # places.json: [{"name": "…", "data_id": "0x…:0x…"}, …]
"""
from __future__ import annotations

import argparse
import json
import pathlib

from qd import rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("places", type=pathlib.Path)
    ap.add_argument("--state", type=pathlib.Path, default=pathlib.Path("seen.json"))
    ap.add_argument("--page", type=int, default=40, help="reviews to pull per place per run")
    ap.add_argument("--country", default="us")
    args = ap.parse_args()

    places = json.loads(args.places.read_text(encoding="utf-8"))
    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}

    for place in places:
        key = place.get("data_id") or place.get("place_id") or place["name"]
        known = set(state.get(key, {}).get("review_ids", []))
        high_water = state.get(key, {}).get("latest_iso", "")

        payload = {k: v for k, v in {
            "data_id": place.get("data_id"), "place_id": place.get("place_id"),
            "query": place.get("query"), "location": place.get("location"),
            "sort_by": "newest", "country": args.country, "max_results": args.page,
        }.items() if v}

        batch = rows("place_reviews", payload)
        fresh = [r for r in batch
                 if r.get("review_id") not in known and (r.get("iso_date") or "") > high_water]

        print(f"\n{place.get('name', key)}: {len(fresh)} new of {len(batch)} pulled")
        for r in fresh[:10]:
            text = (r.get("text") or "").replace("\n", " ")[:110]
            print(f"  {r.get('rating')}★ {r.get('iso_date', '')[:10]}  {text}")

        state[key] = {
            "review_ids": list(known | {r.get("review_id") for r in batch if r.get("review_id")})[-2000:],
            "latest_iso": max([high_water] + [r.get("iso_date") or "" for r in batch]),
        }

    args.state.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"\nstate → {args.state}")


if __name__ == "__main__":
    main()
