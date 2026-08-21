"""Does the owner answer reviews — and do they only answer the good ones?

Response rate split by star rating is one of the few review metrics that is
genuinely actionable, and it is invisible in the Maps UI.

    python3 response_rate.py --query "Blue Bottle Coffee" --location "San Francisco" --max 250
"""
from __future__ import annotations

import argparse
from collections import Counter

from qd import rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-id", dest="data_id")
    ap.add_argument("--query")
    ap.add_argument("--location")
    ap.add_argument("--country", default="us")
    ap.add_argument("--max", type=int, default=200)
    args = ap.parse_args()

    payload = {k: v for k, v in {
        "data_id": args.data_id, "query": args.query, "location": args.location,
        "country": args.country, "sort_by": "newest", "max_results": args.max,
    }.items() if v}
    reviews = rows("place_reviews", payload)

    total = Counter()
    answered = Counter()
    for r in reviews:
        star = r.get("rating")
        if not star:
            continue
        total[star] += 1
        if r.get("owner_response_text"):
            answered[star] += 1

    print(f"{len(reviews)} reviews\n")
    print(f"{'rating':<8}{'reviews':>9}{'answered':>10}{'rate':>8}")
    for star in (5, 4, 3, 2, 1):
        n, a = total.get(star, 0), answered.get(star, 0)
        rate = f"{100 * a / n:.0f}%" if n else "-"
        print(f"{star}★{'':<6}{n:>9}{a:>10}{rate:>8}")

    n, a = sum(total.values()), sum(answered.values())
    print(f"\noverall {a}/{n} = {100 * a / n:.0f}%" if n else "\nno rated reviews")

    negative = sum(total.get(s, 0) for s in (1, 2))
    negative_answered = sum(answered.get(s, 0) for s in (1, 2))
    if negative:
        print(f"negative (1-2★): {negative_answered}/{negative} answered "
              f"= {100 * negative_answered / negative:.0f}%")


if __name__ == "__main__":
    main()
