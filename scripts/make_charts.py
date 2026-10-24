"""Makes the charts for my project.

The main one shows, for each place, the average Mon-Thu day against Friday.
That's the whole story in one picture: Planet Fitness spikes right after school
on normal days, and Fitness 19 spikes Friday night.

Run:
    python scripts/make_charts.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from places import PLACES, DAYS, AFTER_SCHOOL, FREE_DAY, SCHOOL_DAYS

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "foot_traffic.csv"
VISUALS = ROOT / "visuals"

# Colors picked so they're still tellable apart if you're colorblind, and so
# they have enough contrast against the background.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
INK_FAINT = "#8a8982"
MON_THU = "#2a78d6"   # blue
FRIDAY = "#eb6834"    # orange
BAND = "#eceae4"


def style_axis(ax):
    """Make the axes recessive so the data is what you look at."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_FAINT)
        ax.spines[side].set_linewidth(0.8)
    ax.grid(axis="y", color=INK_FAINT, alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK_SOFT, labelsize=9, length=3, width=0.8)


def hourly_chart(df):
    """Three panels, one per place. Mon-Thu average vs Friday."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
    fig.patch.set_facecolor(SURFACE)

    for ax, (key, meta) in zip(axes, PLACES.items()):
        sub = df[df["place"] == key]
        mon_thu = sub[sub["day"].isin(SCHOOL_DAYS)].groupby("hour")["busyness"].mean()
        friday = sub[sub["day"] == FREE_DAY].set_index("hour")["busyness"]

        style_axis(ax)

        # Shade the only window I actually use in the model: 3-5 PM.
        ax.axvspan(min(AFTER_SCHOOL) - 0.5, max(AFTER_SCHOOL) + 0.5,
                   color=BAND, zorder=0)

        ax.plot(mon_thu.index, mon_thu.values, color=MON_THU, linewidth=2,
                label="Mon-Thu average", zorder=3)
        ax.plot(friday.index, friday.values, color=FRIDAY, linewidth=2,
                label="Friday", zorder=4)

        ax.set_title(f"{meta['label']}\nyou {meta['access']} here",
                     fontsize=11, color=INK, loc="left", pad=10)
        ax.set_xlim(5, 23)
        ax.set_xticks([6, 9, 12, 15, 18, 21])
        ax.set_xticklabels(["6a", "9a", "12p", "3p", "6p", "9p"])
        ax.set_xlabel("hour of day", fontsize=9, color=INK_SOFT)

    axes[0].set_ylabel("Google busyness index (0-100)", fontsize=9, color=INK_SOFT)
    axes[0].set_ylim(0, 100)

    # Label the lines directly on the first panel so you don't have to keep
    # looking back at the legend.
    axes[0].legend(frameon=False, fontsize=9, loc="upper left",
                   labelcolor=INK_SOFT)

    fig.suptitle("Shaded band is 3-5 PM, right after school lets out - the only window I use",
                 fontsize=9.5, color=INK_SOFT, y=0.035)
    fig.tight_layout(rect=[0, 0.09, 1, 1])

    out = VISUALS / "hourly_traffic.png"
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    return out


def day_chart(df):
    """Average 3-5 PM busyness by day, both gyms. This is the actual result."""
    df = df[df["hour"].isin(AFTER_SCHOOL)]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    fig.patch.set_facecolor(SURFACE)
    style_axis(ax)

    width = 0.38
    xs = range(len(DAYS))
    for offset, (key, color) in enumerate([("planet_fitness", MON_THU),
                                           ("fitness_19", FRIDAY)]):
        sub = df[df["place"] == key]
        means = sub.groupby("day")["busyness"].mean().reindex(DAYS)
        positions = [x + (offset - 0.5) * (width + 0.02) for x in xs]
        bars = ax.bar(positions, means.values, width=width, color=color,
                      label=PLACES[key]["label"], zorder=3)
        # Direct labels, so you can read values without squinting at the axis.
        for bar, value in zip(bars, means.values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 1.2,
                    f"{value:.0f}", ha="center", fontsize=8.5, color=INK_SOFT)

    ax.set_xticks(list(xs))
    ax.set_xticklabels([d[:3] for d in DAYS])
    ax.set_ylabel("average busyness, 3-5 PM", fontsize=9, color=INK_SOFT)
    ax.set_title("Friday afternoon flips which gym is busier",
                 fontsize=12, color=INK, loc="left", pad=12)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_SOFT)
    fig.tight_layout()

    out = VISUALS / "by_day.png"
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    return out


def main():
    if not DATA.exists():
        print("No data yet. Run scripts/make_placeholder.py or scripts/scrape_traffic.py")
        return 1
    df = pd.read_csv(DATA)
    df = df[df["day"].isin(DAYS)]
    VISUALS.mkdir(exist_ok=True)
    for out in (hourly_chart(df), day_chart(df)):
        print(f"saved {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
