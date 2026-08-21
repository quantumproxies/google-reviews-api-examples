"""A readable report from a place's reviews — no pandas, no model, no API key beyond ours.

Rating histogram, month-by-month trend, and the words that show up far more often
in 1-2★ reviews than in 4-5★ ones. That last list is usually the actual problem.

    python3 sentiment_report.py --query "Hotel Danieli" --location "Venice, Italy" --max 300
"""
from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict

from qd import rows

STOP = set("""
a about after all also am an and any are as at be because been but by can could did do does for
from had has have he her here his how i if in into is it its just like me more most my no not of
on one only or other our out over own said same she should so some such than that the their them
then there these they this those to too us very was we were what when where which while who will
with would you your it's we're don't didn't very really place staff time day get got go went
""".split())


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z']{3,}", (text or "").lower()) if w not in STOP]


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
    if not reviews:
        raise SystemExit("no reviews returned")

    print(f"{reviews[0].get('place_name') or 'place'} — {len(reviews)} reviews\n")

    hist = Counter(r.get("rating") for r in reviews if r.get("rating"))
    total = sum(hist.values())
    for star in (5, 4, 3, 2, 1):
        n = hist.get(star, 0)
        print(f"{star}★ {n:>4}  {'█' * round(40 * n / total)}")
    mean = sum(s * n for s, n in hist.items()) / total
    print(f"\nmean {mean:.2f}★")

    by_month: dict[str, list[int]] = defaultdict(list)
    for r in reviews:
        iso = r.get("iso_date") or ""
        if len(iso) >= 7 and r.get("rating"):
            by_month[iso[:7]].append(r["rating"])
    if by_month:
        print("\nmonthly mean")
        for month in sorted(by_month)[-12:]:
            vals = by_month[month]
            print(f"  {month}  {sum(vals) / len(vals):.2f}  ({len(vals):>3} reviews)")

    low = Counter(w for r in reviews if (r.get("rating") or 5) <= 2 for w in words(r.get("text")))
    high = Counter(w for r in reviews if (r.get("rating") or 0) >= 4 for w in words(r.get("text")))
    low_total, high_total = sum(low.values()) or 1, sum(high.values()) or 1

    scored = [
        (w, n, (n / low_total) / ((high.get(w, 0) / high_total) or (0.5 / high_total)))
        for w, n in low.items() if n >= 3
    ]
    scored.sort(key=lambda t: -t[2])
    if scored:
        print("\nwords over-represented in 1-2★ reviews")
        for word, n, ratio in scored[:15]:
            print(f"  {word:<18} {n:>3}×   {ratio:5.1f}× more likely than in 4-5★")


if __name__ == "__main__":
    main()
