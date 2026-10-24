"""Pull Google Maps "Popular Times" for the three places into one CSV.

Google has no official API for this, so we go through Apify, which runs the
scraper for us. Free tier covers 3 places easily.

Setup:
    1. make a free account at apify.com
    2. copy your token from Settings -> Integrations
    3. put it in a file called .env like this:   APIFY_API_TOKEN=your_token_here

Run:
    python scripts/scrape_traffic.py
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from places import PLACES, DAY_KEYS

ROOT = Path(__file__).parent.parent
CACHE = ROOT / "data" / "cache"
OUT = ROOT / "data" / "foot_traffic.csv"
ACTOR = "compass/crawler-google-places"


def load_token():
    """Read APIFY_API_TOKEN from the environment or a .env file."""
    token = os.environ.get("APIFY_API_TOKEN")
    if token:
        return token
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("APIFY_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    return None


def scrape_one(client, search):
    """Ask Apify for one place and hand back the raw record."""
    run = client.actor(ACTOR).call(run_input={
        "searchStringsArray": [search],
        "maxCrawledPlacesPerSearch": 1,
        "language": "en",
        # Popular Times only comes back when the detail page is scraped.
        "scrapePlaceDetailPage": True,
    })
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not items:
        raise RuntimeError(f"Apify found nothing for: {search}")
    return items[0]


def to_rows(key, record):
    """Flatten one place's histogram into tidy rows.

    Heads up: Google leaves out hours when the place is closed. A missing hour
    is NOT a zero. If we filled those with 0 the averages would get dragged
    down and the regression would be wrong. So we just skip them.
    """
    histogram = record.get("popularTimesHistogram") or {}
    rows = []
    for day_key, hours in histogram.items():
        day = DAY_KEYS.get(day_key, day_key)
        for entry in hours:
            rows.append({
                "place": key,
                "day": day,
                "hour": entry["hour"],
                "busyness": entry["occupancyPercent"],
            })
    return rows


def main():
    token = load_token()
    if not token:
        print("No APIFY_API_TOKEN found. See the setup notes at the top of this file.")
        return 1

    from apify_client import ApifyClient
    client = ApifyClient(token)
    CACHE.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for key, meta in PLACES.items():
        cached = CACHE / f"{key}.json"
        if cached.exists():
            print(f"{key}: using cached copy")
            record = json.loads(cached.read_text())
        else:
            print(f"{key}: scraping...")
            record = scrape_one(client, meta["search"])
            cached.write_text(json.dumps(record, indent=2))

        rows = to_rows(key, record)
        if not rows:
            print(f"  WARNING: no Popular Times for {key}. Google hides this for "
                  f"places without enough traffic data. Check you got the right store.")
        else:
            print(f"  got {len(rows)} hours  ({record.get('title', '?')})")
        all_rows.extend(rows)

    if not all_rows:
        print("Nothing to save.")
        return 1

    df = pd.DataFrame(all_rows).sort_values(["place", "day", "hour"])
    df.to_csv(OUT, index=False)
    print(f"\nSaved {len(df)} rows to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
