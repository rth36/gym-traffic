"""Makes FAKE data so I can test my code before I scrape the real thing.

!!! IMPORTANT !!!
These numbers are made up by me. They are NOT real Google data. I built them to
roughly match what I see at my school so I could check that my scripts run and
my regression is set up right.

Nothing in my writeup should ever quote results from this file. Once I run
scrape_traffic.py, the real data overwrites it and I redo the analysis.

Run:
    python scripts/make_placeholder.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from places import DAYS

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "foot_traffic.csv"
OPEN_HOURS = range(5, 24)

rng = np.random.default_rng(7)


def shape(place, day, hour):
    """My guess at the busyness pattern for each place."""
    friday = day == "Friday"
    base = 12

    if place == "planet_fitness":
        # Big after-school rush Mon-Thu, smaller on Friday.
        if 15 <= hour <= 17:
            base += 55 if not friday else 30
        if 18 <= hour <= 21:
            base += 25          # adults after work
        if 6 <= hour <= 8:
            base += 20          # morning adults
    elif place == "fitness_19":
        # Pretty quiet all week, then Friday night.
        if 15 <= hour <= 17:
            base += 10 if not friday else 35
        if 18 <= hour <= 21:
            base += 22 if not friday else 60
        if 6 <= hour <= 8:
            base += 18
    elif place == "lucky":
        # Snack run lands an hour before the gym rush.
        if 14 <= hour <= 16:
            base += 45
        if 17 <= hour <= 19:
            base += 35          # dinner shopping
        if hour >= 20:
            base -= 5

    return base


rows = []
for place in ["planet_fitness", "fitness_19", "lucky"]:
    for day in DAYS:
        for hour in OPEN_HOURS:
            value = shape(place, day, hour) + rng.normal(0, 5)
            rows.append({
                "place": place,
                "day": day,
                "hour": hour,
                "busyness": int(np.clip(round(value), 0, 100)),
            })

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print(f"Wrote {len(df)} rows of FAKE data to {OUT.relative_to(ROOT)}")
print("Replace it with real data by running: python scripts/scrape_traffic.py")
