"""My AP Econ project: do kids pick a gym, or just pick the one they can reach?

The thing I noticed
-------------------
Freshmen and sophomores at my school all go to the Planet Fitness on Fremont
Blvd, because you can walk there from campus. Once people start driving junior
year, they show up at Fitness 19 in Newark, which is way too far to walk.

So I wanted to know: do kids actually LIKE Fitness 19 better, or was the only
reason nobody went that they physically couldn't get there?

The econ part
-------------
I just started AP Econ so I had to look most of this up. The idea I found is
called revealed preference: what you choose shows what you want, BUT only if you
actually had options. If there's one thing on the menu, ordering it doesn't mean
you wanted it.

Think of it as:

    how good a gym is for you = how much you like it - what it costs to get there

If you can't drive, getting to Fitness 19 basically costs infinity. Your only
real option is Planet Fitness. You didn't choose it, it chose you.

What I compare
--------------
I only look at 3-5 PM, right after school lets out. Same hour of the day every
time, so I'm not accidentally measuring "people work out after dinner."

    Mon-Thu 3-5 PM  ->  kids walk. Fitness 19 is unreachable.
    Friday  3-5 PM  ->  people who drive actually go out, and they give rides.

So the comparison is a 2x2:

                     Mon-Thu 3-5     Friday 3-5
    Planet Fitness        a               b
    Fitness 19            c               d

and the answer is (d - c) - (b - a).

Stuff I deliberately cut
------------------------
- Saturday and Sunday. Too much other stuff going on (sports, family, jobs).
- Evenings. Mon-Thu after 5 PM everyone's home, so there are no students in
  that window to measure.
- Counting dual memberships. Google only tells me how busy a place is. It never
  tells me who's inside or what they pay for, so I can't count memberships at
  all. I'd need a survey and I'm not doing one.

Run:
    python scripts/analyze_traffic.py
"""

import sys
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).parent))
from places import PLACES, DAYS, AFTER_SCHOOL, FREE_DAY, SCHOOL_DAYS

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "foot_traffic.csv"
VISUALS = ROOT / "visuals"
GYMS = ["planet_fitness", "fitness_19"]


def load():
    """Read the CSV and keep only the rows I actually use: weekdays, 3-5 PM."""
    if not DATA.exists():
        print(f"Can't find {DATA.relative_to(ROOT)}.")
        print("Run one of these first:")
        print("  python scripts/make_placeholder.py   (fake data, just to test)")
        print("  python scripts/scrape_traffic.py     (the real thing)")
        raise SystemExit(1)

    df = pd.read_csv(DATA)
    df = df[df["day"].isin(DAYS)]                   # Mon-Fri only
    df = df[df["hour"].isin(AFTER_SCHOOL)].copy()   # 3-5 PM only
    df = df[df["place"].isin(GYMS)].copy()          # just the two gyms

    df["friday"] = (df["day"] == FREE_DAY).astype(int)
    df["f19"] = (df["place"] == "fitness_19").astype(int)
    return df


def cell_means(df):
    """The 2x2 table. Four averages, which is the whole project really."""
    table = df.pivot_table(index="place", columns="friday", values="busyness", aggfunc="mean")
    table = table.rename(columns={0: "mon_thu_3to5", 1: "friday_3to5"})
    table.index = [PLACES[i]["label"] for i in table.index]
    table["change"] = table["friday_3to5"] - table["mon_thu_3to5"]
    return table.round(2)


def did_by_hand(table):
    """Compute the difference-in-differences with arithmetic, not a model.

    I do it both ways on purpose. If the regression coefficient doesn't match
    this number, I set the regression up wrong.
    """
    pf = table.loc["Planet Fitness", "change"]
    f19 = table.loc["Fitness 19", "change"]
    return f19 - pf, pf, f19


def fit_did(df):
    """The same thing as a regression, so I get a p-value and a CI.

    friday * f19 gives me three terms:
        friday      - how much busier Friday is in general
        f19         - how Fitness 19 differs from Planet Fitness overall
        friday:f19  - the extra Friday bump that ONLY Fitness 19 gets

    That last one is the difference-in-differences, and it's my answer.

    Why I need the double subtraction: Google scales busyness so each place's
    own busiest hour is 100. So a 70 at Planet Fitness and a 70 at Fitness 19
    are not the same number of people, and I can't compare the two gyms head to
    head. Subtracting each gym from itself first cancels out its scale, and
    subtracting again cancels out anything that hits both gyms. What's left is
    the part that's actually different.

    I use robust (HC1) standard errors because busyness bounces around more at
    busy hours than at quiet ones, and regular standard errors assume it
    doesn't.
    """
    return smf.ols("busyness ~ friday * f19", data=df).fit(cov_type="HC1")


def lucky_side_note():
    """Side thing: does the Lucky snack run happen before or after the gym?

    This isn't my main question, it's just something I noticed. Lucky
    Supermarket is in the same plaza as Planet Fitness and everyone grabs stuff
    there around a workout.

    In econ, two things are COMPLEMENTS if you use them together, instead of
    picking one over the other. You don't choose between snacks and working
    out - you do both on the same trip. So Lucky's traffic should move with the
    gym's.

    To find out which comes first I line up Lucky's hourly busyness against
    Planet Fitness's, slide it a few hours each way, and see which offset
    matches best.

        shift(+1) lines up Lucky at 3 PM with the gym at 4 PM.
        So if +1 wins, Lucky filled up an hour EARLIER -> snacks come first.

    I got this backwards the first time. The fake test data caught it, which is
    exactly why I made fake data before scraping anything real.

    Note: this one uses the whole day, not just 3-5 PM, because I need hours on
    both sides of the rush to see the lag at all.
    """
    full = pd.read_csv(DATA)
    full = full[full["day"].isin(DAYS)]
    wide = full.pivot_table(index=["day", "hour"], columns="place", values="busyness")
    if "lucky" not in wide.columns or "planet_fitness" not in wide.columns:
        return None

    wide = wide.reset_index()
    rows = []
    for lag in range(-3, 4):
        # grouping by day stops the shift from running Friday 11 PM into
        # Monday 5 AM, which would be meaningless
        shifted = wide.groupby("day", sort=False)["lucky"].shift(lag)
        rows.append({"lag_hours": lag,
                     "correlation": round(shifted.corr(wide["planet_fitness"]), 3)})
    return pd.DataFrame(rows)


def by_day(df):
    """Average 3-5 PM busyness for each day, so I can eyeball the Friday jump."""
    table = df.pivot_table(index="day", columns="place", values="busyness", aggfunc="mean")
    table = table.rename(columns={k: PLACES[k]["label"] for k in table.columns})
    return table.reindex(DAYS).round(1)


def main():
    df = load()
    VISUALS.mkdir(exist_ok=True)
    lines = []

    def say(text=""):
        print(text)
        lines.append(str(text))

    say("=" * 70)
    say("DO KIDS PICK A GYM, OR PICK THE ONE THEY CAN REACH?")
    say("Google Maps busyness, 3-5 PM only, Mon-Fri")
    say("=" * 70)
    say()
    say(f"{len(df)} rows (2 gyms x 5 days x {len(AFTER_SCHOOL)} hours)")
    say()

    table = cell_means(df)
    say("-" * 70)
    say("1. THE 2x2")
    say("-" * 70)
    say(table.to_string())
    say()

    did, pf_change, f19_change = did_by_hand(table)
    say(f"Planet Fitness changes {pf_change:+.2f} from Mon-Thu to Friday")
    say(f"Fitness 19     changes {f19_change:+.2f}")
    say(f"Difference-in-differences, by hand = {did:+.2f}")
    say()

    say("-" * 70)
    say("2. SAME THING AS A REGRESSION")
    say("-" * 70)
    res = fit_did(df)
    say(res.summary().tables[1].as_text())
    say()

    coef = res.params.get("friday:f19")
    pval = res.pvalues.get("friday:f19")
    low, high = res.conf_int().loc["friday:f19"]

    say(f"friday:f19 = {coef:+.2f}   (by hand I got {did:+.2f})")
    if abs(coef - did) < 0.01:
        say("Those match, so the regression is set up right.")
    else:
        say("These DON'T match - something's wrong with my setup.")
    say()
    say(f"95% confidence interval: {low:+.2f} to {high:+.2f}")
    say(f"p-value: {pval:.4f}")
    say()

    say("What this means:")
    if coef > 0:
        say(f"  On Friday afternoons, Fitness 19 gets {coef:.1f} points busier than")
        say("  you'd expect from Planet Fitness's own Friday change. That's the")
        say("  direction I predicted - once rides are available, kids go to Newark.")
    else:
        say(f"  Fitness 19 gets {abs(coef):.1f} points LESS busy on Friday afternoons")
        say("  relative to Planet Fitness. That's the opposite of my prediction.")
    if pval < 0.05:
        say(f"  p = {pval:.4f}, so this is statistically significant.")
    else:
        say(f"  BUT p = {pval:.3f}, so I can't rule out that it's just noise.")
        say("  I only have a few Friday hours, so there isn't much data behind it.")
    say()

    say("-" * 70)
    say("3. EVERY DAY, 3-5 PM")
    say("-" * 70)
    say(by_day(df).to_string())
    say()

    lags = lucky_side_note()
    if lags is not None:
        say("-" * 70)
        say("4. SIDE NOTE: the Lucky snack run")
        say("-" * 70)
        say("Lucky is a COMPLEMENT to the gym - you do both on one trip.")
        say("So does the snack stop come before the workout or after?")
        say()
        say(lags.to_string(index=False))
        best = lags.loc[lags["correlation"].idxmax()]
        lag = int(best["lag_hours"])
        if lag > 0:
            read = f"Lucky peaks {lag}h BEFORE the gym -> kids buy snacks first"
        elif lag < 0:
            read = f"Lucky peaks {abs(lag)}h AFTER the gym -> it's a recovery stop"
        else:
            read = "they peak the same hour -> probably one combined trip"
        say()
        say(f"  best lag = {lag:+d}h (r={best['correlation']:.3f})")
        say(f"  {read}")
        say()

    say("=" * 70)

    out = VISUALS / "results.txt"
    out.write_text("\n".join(lines) + "\n")
    print(f"\nSaved to {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
