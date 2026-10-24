# Do you pick the gym, or does the gym pick you?

A project about something I noticed at my own school, using free data from
Google Maps.

## What I noticed

Freshmen and sophomores at my school all go to the same Planet Fitness on
Fremont Blvd. You can walk there from school, so that's where everyone ends up.

Then people start driving junior year, and suddenly they're at Fitness 19 in
Newark instead. That one is way too far to walk to.

So here's what I actually wanted to know: **do kids like Fitness 19 better, or
was the only reason nobody went that they literally couldn't get there?**

From the outside those two look exactly the same. Same kids, same gym, same
switch. But the reason behind it is completely different, and I wanted to see if
I could tell them apart.

## The econ idea

I had to look this up, but there's a name for it: **revealed preference**. The
idea is that what you pick shows what you want — but only if you actually had
options in the first place.

If there's one thing on the menu, ordering it doesn't mean you wanted it.

That's basically the situation at my school. The way I ended up thinking about
it:

```
how good a gym is for you  =  how much you like it  −  what it costs to get there
```

If you can't drive, getting to Fitness 19 costs you something close to infinity.
So your only real option is Planet Fitness. You didn't pick it. It picked you.

The walking part counts as a cost even though it's free — that's **opportunity
cost**. Walking 20 minutes doesn't cost dollars, but you still spent 20 minutes
you could have used on something else.

## What I compare

I only look at **3–5 PM, Monday through Friday**, right when school lets out.

Keeping the hour the same is the whole trick. If I compared 4 PM to 8 PM,
someone could just say "people work out after dinner" and they'd be right. Using
the same hour every time takes that excuse off the table.

The thing that changes is the day:

- **Mon–Thu 3–5 PM** — kids are walking. Fitness 19 isn't reachable.
- **Friday 3–5 PM** — the people who drive actually go out, and they give rides.

So it's a 2×2:

|  | Mon–Thu 3–5 PM | Friday 3–5 PM |
|---|---|---|
| **Planet Fitness** | a | b |
| **Fitness 19** | c | d |

And my answer is **(d − c) − (b − a)**.

Turns out subtracting twice like that has a name — **difference-in-differences**.
I'm not using it to sound impressive. I needed it, because of a problem with my
data.

Google scales busyness so each place's own busiest hour equals 100. That means a
70 at Planet Fitness and a 70 at Fitness 19 are **not** the same number of
people. I can't compare the two gyms side by side at all.

Subtracting twice gets around it:

- subtracting each gym from itself cancels out that gym's own scale
- subtracting again cancels out stuff that happened to both gyms

Whatever's left after both is the part that's actually different. That one
number is pretty much my whole project.

I do the math twice on purpose — once by hand with four averages, once as a
regression. If the two don't match, I know I set the regression up wrong.

## The data

Google Maps "Popular Times." It's free, it's public, and it's a 0–100 busyness
score for every hour of the week.

Three places:

| Place | How you get there |
|---|---|
| Planet Fitness, Fremont Blvd | walk from school |
| Fitness 19, Jarvis Ave, Newark | drive |
| Lucky Supermarket, Brookvale | walk (side note only) |

## Results

**Not done yet.** The code is all built and tested, but I haven't scraped the
real numbers.

What's in the repo right now is a **fake placeholder dataset that I made up**, so
the scripts can run start to finish. Those numbers are invented. They're not
real and nothing here should ever quote them.

Once I scrape the actual data I'll fill this in with what I found — including if
it turns out I was wrong.

## Charts

| | |
|---|---|
| `visuals/hourly_traffic.png` | All three places across the day, Mon–Thu vs Friday |
| `visuals/by_day.png` | 3–5 PM busyness for both gyms, every weekday |
| `visuals/results.txt` | Full output from the analysis |

## Things that are wrong with this

I'd rather list these myself than have someone else find them.

1. **Google doesn't tell me who's inside.** A busy 3 PM could be students, or
   retired people, or someone who got off work early. I'm assuming it's students
   because of the timing, but I can't actually see that.

2. **I can't count memberships.** I'd really like to know how many kids pay for
   both gyms. There's no way to get that out of busyness data. I'd need a survey.

3. **The gyms aren't the same.** Different prices, different equipment,
   different classes. Some of the gap I'm measuring could just be that, and not
   have anything to do with driving.

4. **Popular Times is an average, not a calendar.** It's a typical week built
   out of months of history. So I get one average Friday. I can't look up a
   specific date, like the Friday before a long weekend.

5. **There aren't many Friday hours.** Friday 3–5 PM is only three hours per
   gym. That's thin, so the confidence interval ends up wide.

6. **It's a correlation.** Nothing in here proves driving *causes* the switch.
   The timing lines up with my explanation, but I didn't run an experiment.

## How to run it

```bash
pip install -r requirements.txt

python scripts/make_placeholder.py    # fake data, just to see it work
python scripts/analyze_traffic.py     # the regression
python scripts/make_charts.py         # the charts
```

To get the real data you need a free Apify token (no credit card). Put it in a
file called `.env`:

```
APIFY_API_TOKEN=your_token_here
```

then:

```bash
python scripts/scrape_traffic.py      # overwrites the fake data with real data
python scripts/analyze_traffic.py
```

## What's in here

```
scripts/places.py            the three places and my time windows
scripts/scrape_traffic.py    pulls Google data -> data/foot_traffic.csv
scripts/make_placeholder.py  fake data for testing (NOT real)
scripts/analyze_traffic.py   the 2x2 and the regression
scripts/make_charts.py       the charts
```

## What I'd do next

- Scrape the live busyness every day for a few months. Then I'd have actual
  dates instead of an average week, and I could check whether the Friday before
  a long weekend looks different.
- Add more gyms, so it's not just Planet Fitness vs Fitness 19.
- Find a way to deal with the fact that the two gyms aren't identical, since
  that's the thing most likely to make my answer wrong.
