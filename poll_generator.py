"""
poll_generator.py
Generates engaging Facebook poll-style posts for Filipino audience.
Topics rotate across: OFW life, Health, Money/Savings, Side Income.
Uses Gemini → fallback library of 40+ hand-written polls.
"""

import os
import json
import random
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Topic rotation ─────────────────────────────────────────────────────────────
TOPICS = ["ofw", "health", "money", "sideincome"]

# ── Gemini prompt ──────────────────────────────────────────────────────────────
POLL_PROMPT = """You are writing a Facebook poll post for Filipino professionals — nurses, 
IT workers, engineers, architects, pharmacists — in Singapore and the Philippines.

Write a short poll post that sounds like a real person wrote it, not AI.

LANGUAGE RULES — very important:
- Simple everyday English. Max 10 words per sentence.
- Write like you're asking a friend a genuine question
- Contractions always: "you're", "it's", "don't", "can't"
- NEVER use: leverage, optimise, empower, unlock, actionable, transformative, synergy
- Very optional: 1 Filipino word if it fits perfectly (e.g. "Ikaw?" "Tayo na.")
- NO motivational speeches. NO brand names.

FORMAT — strict:
- Ultra short. Max 60 words total including options.
- Line 1: One direct question or honest observation. No emoji on this line.
- Options A) B) C) D) — max 5 words each, relatable to professionals
- Last line: Short CTA — "Drop your letter! 👇" or "Comment below! 💬"
- Max 2 emojis total, only after line 1

Topic: {topic_description}

Write ONLY the post. No preamble, no quotes."""

# ── Hand-written fallback poll library ────────────────────────────────────────
FALLBACK_POLLS = {
    "ofw": [
        """After years in your career abroad, what's your biggest financial realisation?

A) Salary alone won't build wealth
B) Should have invested earlier
C) Need a second income stream
D) Still figuring it out 💡

Drop your letter! 👇""",

        """How long have you been in your professional career abroad? 🌏

A) Less than 2 years
B) 2–5 years
C) 5–10 years
D) 10+ years — veteran!

Comment your letter + your profession 👇""",

        """What's your main financial goal right now as a professional?

A) Build an investment portfolio
B) Start a side income
C) Pay off debt first
D) Save 6 months emergency fund 💰

Drop your letter! 👇""",

        """What would make you feel truly financially secure? 🎯

A) 3+ income streams
B) Enough savings to quit anytime
C) Passive income covering my bills
D) I'm already there!

Comment your letter 👇""",

        """How much of your salary do you actively invest? 📈

A) Nothing yet
B) Less than 10%
C) 10–20%
D) 20%+ consistently

Drop your letter! 👇""",

        """If you could build one thing outside your career right now?

A) A passive income stream
B) An investment portfolio
C) My own business
D) Real estate 🏠

Tayo na — comment your letter 👇""",
    ],

    "health": [
        """How many hours of quality sleep do you actually get on workdays? 😴

A) Less than 5 hours
B) 5–6 hours
C) 7–8 hours
D) Varies too much to say

Drop your letter! 👇""",

        """How do you manage stress from a demanding professional career? 💆

A) Exercise regularly
B) Mindfulness or meditation
C) Honestly, not well
D) Work IS my stress relief 😅

Comment your letter 👇""",

        """When did you last have a full health check-up? 🏥

A) Within this year
B) 1–2 years ago
C) Only when something feels wrong
D) It's been too long

Drop your letter! 👇""",

        """How often do you skip meals because of work? 🍽️

A) Almost never — I prioritise this
B) Sometimes, maybe 1–2x a week
C) Several times a week
D) Daily reality for me 😅

Comment your letter 👇""",

        """What's your biggest barrier to staying healthy with a demanding career?

A) No time after long shifts
B) Irregular working hours
C) Too exhausted to exercise
D) Stress eating 😅 💡

Drop your letter! 👇""",

        """Do you take daily health supplements? 💊

A) Yes — consistently
B) Sometimes, not consistent
C) No — I rely on diet
D) Thinking about starting

Comment your letter 👇""",
    ],

    "money": [
        """What percentage of your salary goes to savings and investments? 📊

A) Nothing yet
B) Less than 10%
C) 10–20%
D) 20%+ consistently

Drop your letter! 👇""",

        """Where does the biggest chunk of your salary actually go? 💸

A) Living expenses
B) Supporting family
C) Savings and investments
D) It disappears somehow 😅

Comment your letter 👇""",

        """Honest question for professionals — do you have a financial plan? 📈

A) Yes — detailed and active
B) Rough idea, not written
C) Working on building one
D) Not yet 💡

Drop your letter! 👇""",

        """If you lost your income tomorrow — how long could you sustain yourself?

A) Less than 1 month
B) 1–3 months
C) 3–6 months
D) 6+ months — I'm prepared 💪

Comment your letter 👇""",

        """What's your current relationship with investing? 📉📈

A) Actively investing regularly
B) Know I should, haven't started
C) Learning before I begin
D) Already building a portfolio 💰

Drop your letter! 👇""",

        """What's the smartest financial move you've made in your career? 💡

A) Started investing early
B) Built a side income
C) Eliminated debt aggressively
D) Still looking for mine 😅

Comment your letter 👇""",
    ],

    "sideincome": [
        """Do you have any income outside your main career? 💼

A) Yes — already earning
B) Building one right now
C) Exploring options
D) Just my salary for now

Drop your letter! 👇""",

        """What's the biggest barrier stopping you from building a side income?

A) No time after work
B) Don't know where to start
C) Worried about the risk
D) Already have one! 🙌

Comment your letter 👇""",

        """If you had an extra $500/month passive income — what changes? 💡

A) Finally invest consistently
B) Reduce financial stress
C) Accelerate a big goal
D) Build it into more 📈

Drop your letter! 👇""",

        """Which side income model fits a busy professional best? 🎯

A) Freelancing your skills
B) Network marketing
C) Content creation
D) Investments and dividends

No wrong answer — comment your letter 👇""",

        """How many income streams do professionals realistically need? 📈

A) 1 solid salary is enough
B) 2 minimum — salary + 1 side
C) 3+ for real security
D) Already building multiple 💪

Drop your number! 👇""",

        """What would a stable second income of $1,000/month change for you? 🎯

A) Financial freedom faster
B) More investment capital
C) Career choices become freer
D) Retire earlier 🌟

Comment your letter 👇""",
    ],
}


def _get_topic_description(topic: str) -> str:
    descriptions = {
        "ofw":        "OFW (overseas Filipino worker) life, working abroad, missing home, financial pressures of supporting family from afar",
        "health":     "daily health habits, sleep, diet, exercise, wellness routines for busy working professionals",
        "money":      "personal finance, saving money, budgeting, financial struggles of everyday workers in Singapore and Philippines",
        "sideincome": "side income, extra earnings, financial independence, building income streams beyond a single job",
    }
    return descriptions.get(topic, descriptions["ofw"])


def _generate_via_gemini(topic: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
    try:
        prompt = POLL_PROMPT.format(topic_description=_get_topic_description(topic))
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"  ✅ Gemini generated poll for topic: {topic}")
        return text
    except Exception as e:
        print(f"  ⚠️  Gemini poll error: {e}")
        print(f"  ⚠️  Response: {resp.text[:200] if 'resp' in locals() else 'no response'}")
        return None


def _get_fallback_poll(topic: str, seed: str = "") -> str:
    """Pick a fallback poll, rotating through the library using date as seed."""
    polls = FALLBACK_POLLS.get(topic, FALLBACK_POLLS["ofw"])
    # Use date + topic as seed so same topic doesn't repeat on same day
    seed_str = seed or (datetime.now().strftime("%Y-%m-%d") + topic)
    idx = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % len(polls)
    return polls[idx]


def get_topic_for_today() -> str:
    """
    Rotate topics based on week number and day.
    Mon = ofw, Wed = health, Fri = money or sideincome (alternating weeks).
    """
    now        = datetime.now()
    week_num   = now.isocalendar()[1]
    weekday    = now.weekday()  # 0=Mon, 2=Wed, 4=Fri

    if weekday == 0:   # Monday
        return "ofw"
    elif weekday == 2: # Wednesday
        return "health"
    elif weekday == 4: # Friday — alternate money/sideincome by week
        return "money" if week_num % 2 == 0 else "sideincome"
    else:
        # Fallback for manual runs on other days — cycle all topics
        return TOPICS[week_num % len(TOPICS)]


def generate_poll(topic: str = None) -> dict:
    """
    Generate a poll post. Returns dict with topic and caption.
    """
    if not topic:
        topic = get_topic_for_today()

    print(f"\n📊 Generating poll for topic: {topic.upper()}")

    # Try Gemini first
    caption = _generate_via_gemini(topic)

    # Fallback to hand-written library
    if not caption:
        print("  ⚠️  Using fallback poll library.")
        caption = _get_fallback_poll(topic)

    return {
        "topic":   topic,
        "caption": caption,
    }


if __name__ == "__main__":
    # Test all 4 topics
    for topic in TOPICS:
        result = generate_poll(topic)
        print(f"\n{'='*60}")
        print(f"Topic: {result['topic'].upper()}")
        print(f"{'='*60}")
        print(result["caption"])
