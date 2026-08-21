"""Pull one place's Google reviews.

    python3 reviews.py --query "Orsonero Coffee" --location "Milan, Italy" --max 200
    python3 reviews.py --data-id "0x4786c…:0x…" --sort newest --out reviews.jsonl --anonymise
"""
from __future__ import annotations

import argparse
import csv
import json

from qd import rows

FIELDS = ["rank", "rating", "iso_date", "date", "author", "text",
          "owner_response_date", "owner_response_text", "link", "place_name"]
PERSONAL = ("author", "author_url", "author_thumbnail")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-id", dest="data_id")
    ap.add_argument("--place-id", dest="place_id")
    ap.add_argument("--query")
    ap.add_argument("--location")
    ap.add_argument("--sort", default="relevance",
                    choices=["relevance", "newest", "rating_high", "rating_low"])
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--anonymise", action="store_true", help="drop author name, URL and photo")
    ap.add_argument("--out", default="reviews.csv")
    args = ap.parse_args()

    payload = {k: v for k, v in {
        "data_id": args.data_id, "place_id": args.place_id,
        "query": args.query, "location": args.location,
        "sort_by": args.sort, "country": args.country, "lang": args.lang,
        "max_results": args.max,
    }.items() if v}

    if not (args.data_id or args.place_id or args.query):
        raise SystemExit("give --data-id, --place-id, or --query (+ --location)")

    reviews = rows("place_reviews", payload)
    if args.anonymise:
        reviews = [{k: v for k, v in r.items() if k not in PERSONAL} for r in reviews]

    if args.out.endswith(".jsonl"):
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in reviews:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(reviews)

    replied = sum(1 for r in reviews if r.get("owner_response_text"))
    ratings = [r["rating"] for r in reviews if r.get("rating")]
    print(f"{len(reviews)} reviews → {args.out}")
    if ratings:
        print(f"mean {sum(ratings) / len(ratings):.2f}★, {replied} answered by the owner")


if __name__ == "__main__":
    main()
