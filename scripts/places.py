"""The three businesses in the study, plus the time windows we test.

Why these three:
  Planet Fitness  - walkable from American High School. 9th/10th graders get here on foot.
  Fitness 19      - in Newark, on Jarvis Ave. You need a car.
  Lucky           - the snack stop in the same plaza as Planet Fitness.
"""

PLACES = {
    "planet_fitness": {
        "label": "Planet Fitness",
        "access": "walk",
        "search": "Planet Fitness Fremont Blvd, Fremont, CA",
    },
    "fitness_19": {
        "label": "Fitness 19",
        "access": "drive",
        "search": "Fitness 19 Jarvis Ave, Newark, CA",
    },
    "lucky": {
        "label": "Lucky Supermarket",
        "access": "walk",
        "search": "Lucky Supermarket Brookvale Shopping Center, Fremont, CA",
    },
}

# I'm only using Monday through Friday. I cut Saturday and Sunday on purpose,
# because weekends have way too much other stuff going on - sports, family
# trips, jobs, sleeping in. Too many things I can't measure. Sticking to the
# school week means the only thing changing is the school week itself.
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Google gives us two-letter day keys. Map them to real names.
DAY_KEYS = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday",
            "Fr": "Friday", "Sa": "Saturday", "Su": "Sunday"}

# 3-5 PM. School lets out and kids walk over. No car needed.
AFTER_SCHOOL = {15, 16, 17}

# 6-10 PM. Too late to walk, so you need a ride either way.
# I widened this from 3 hours to 4 because Friday only has one day's worth of
# evening hours, and 3 data points was not enough to estimate anything.
EVENING = {18, 19, 20, 21}

# Friday is its own thing, so I keep it totally separate from Mon-Thu.
# Mon-Thu is the Planet Fitness pattern: walk over after school, go home for
# dinner because there's school tomorrow.
# Friday is the Fitness 19 pattern: people who drive actually go out, and they
# bring the friends who can't drive with them.
FREE_DAY = "Friday"
SCHOOL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]
