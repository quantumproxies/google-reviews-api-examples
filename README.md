# Google reviews API — pull a place's reviews, with the owner's replies

The [`place_reviews` collector](https://quanticdata.io/collectors/google-reviews-scraper-api/)
paginates a single place's Google reviews and returns them as rows: rating, text, author,
absolute and ISO dates, review link, attached images, and the **owner's response** with its date.

$0.0005 per delivered review. Address a place by `data_id` (from
[`google_maps_places`](https://quanticdata.io/collectors/google-maps-scraper-api/)), by
`place_id`, or just by `query` + `location` and let the collector resolve it.

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here

# by name — the collector finds the place first
python3 reviews.py --query "Orsonero Coffee" --location "Milan, Italy" --max 200

# by handle — deterministic, and what you want in a scheduled job
python3 reviews.py --data-id "0x4786c…:0x…" --sort newest --max 500
```

## Files

| File | What it does |
|---|---|
| [`reviews.py`](reviews.py) | pull one place's reviews to CSV or JSONL |
| [`sentiment_report.py`](sentiment_report.py) | rating distribution, monthly trend, most-repeated complaint words — stdlib only |
| [`response_rate.py`](response_rate.py) | how often the owner replies, and how fast |
| [`watch_competitors.py`](watch_competitors.py) | several places at once, incremental — only reviews newer than the last run |

## Input

| Field | Notes |
|---|---|
| `data_id` | the Maps data id, e.g. `0x4786c…:0x…` — the most reliable handle |
| `place_id` | `ChIJ…`, resolved server-side |
| `query` + `location` | resolve by name; use when you have no id yet |
| `sort_by` | `relevance` (default), `newest`, `rating_high`, `rating_low` |
| `country`, `lang` | exit geo and review language |
| `max_results` | how many reviews to deliver |

## Output row

```jsonc
{ "rank": 1, "review_id": "…", "rating": 5, "date": "2 weeks ago",
  "iso_date": "2026-08-05T09:12:00Z", "text": "…",
  "author": "Marta R.", "author_url": "https://www.google.com/maps/contrib/…",
  "author_thumbnail": "https://…", "link": "https://…", "source": "google",
  "images": ["https://…"],
  "owner_response_date": "1 week ago", "owner_response_text": "Thanks Marta …",
  "data_id": "0x…", "place_name": "Orsonero Coffee" }
```

`date` is Google's relative label; `iso_date` is the parsed timestamp — always sort and diff
on `iso_date`, never on the label.

## Two things worth knowing

**Sort order matters for incremental jobs.** `sort_by: "newest"` plus "stop when you reach a
review you already have" is far cheaper than re-pulling everything — `watch_competitors.py`
implements it.

**Reviews are personal data.** They are published publicly, but author names and photos still
fall under GDPR/CCPA if you store them. Keep ratings and text if that is what you need, and drop
the author fields — `reviews.py --anonymise` does it for you.

## Related

- [Google reviews scraper API](https://quanticdata.io/collectors/google-reviews-scraper-api/) · [Google Maps scraper API](https://quanticdata.io/collectors/google-maps-scraper-api/)
- [All collectors](https://quanticdata.io/collectors/) · [Market research data](https://quanticdata.io/market-research-data/)
- [Is web scraping legal in Europe?](https://quanticdata.io/blog/is-web-scraping-legal-in-europe/)

MIT licensed.
