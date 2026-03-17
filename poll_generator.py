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
POLL_PROMPT = """You are a Facebook community manager for a page targeting Filipinos 
in Singapore and the Philippines. Your audience includes OFWs, overseas workers, and people 
exploring side income and better health habits.

Create ONE engaging Facebook poll-style post about: {topic_description}

STYLE — very important:
- Ultra short. Max 60 words total including options.
- Casual, fun, zero fluff — like texting a close friend
- First line: 1 punchy question or statement. No emoji on first line.
- 4 options: A) B) C) D) — each MAX 5 words, honest and relatable
- Last line: very short CTA e.g. "Drop your letter! 👇" or "Comment below! 💬"
- 1-2 emojis max, only after the first line
- Optional: 1 Tagalog word if natural (e.g. "Ikaw?" "Ano?" "Tara!")
- NO long sentences. NO motivational speeches. NO brand mentions.

Topic: {topic_description}

Respond ONLY with the post. No preamble, no quotes."""

# ── Hand-written fallback poll library ────────────────────────────────────────
FALLBACK_POLLS = {
    "ofw": [
        """How much of your salary do you actually keep? 💸

A) Less than 10%
B) 10–20%
C) More than 20%
D) Still figuring it out 😅

Drop your letter! 👇""",

        """How long na you've been working abroad?

A) Less than 2 years
B) 2–5 years
C) 5–10 years
D) 10+ years 🏆

Comment your letter + where you're based! 👇""",

        """Hardest part of being an OFW? 😔

A) Missing family milestones
B) Loneliness
C) Financial pressure
D) Uncertain future

Drop your letter 👇""",

        """Biggest worry about going home for good? 🏠

A) Not enough savings
B) No income waiting
C) Starting over
D) Ready na actually! 😄

Ikaw? Comment below 👇""",

        """Emergency fund check 👀

A) Less than 1 month
B) 1–3 months
C) 3–6 months
D) What fund? 😅

No shame — drop your letter! 👇""",

        """If you could tell your first-day-OFW self one thing?

A) Save more, spend less
B) Invest earlier
C) Take care of yourself too
D) Build a business sooner

Drop your letter 👇""",
    ],

    "health": [
        """Be honest — glasses of water today? 💧

A) Less than 4
B) 4–6
C) 7–8
D) Lost count 😄

Drop your letter! 👇""",

        """What time did you sleep last night? 😴

A) Before 10 PM
B) 10 PM–12 AM
C) 12–2 AM
D) Sleep? What's that 😅

Comment your letter 👇""",

        """Which meal do you skip the most?

A) Breakfast
B) Lunch
C) Dinner
D) Never skip! 💪

Kumain ka na? Drop your letter 👇""",

        """Honest diet check 🥗

A) Mostly healthy
B) 50/50 lol
C) Eat whatever's available
D) Send help 😅

No judgment! Drop your letter 👇""",

        """Why don't you exercise regularly? 🏃

A) No time
B) Too tired after work
C) No gym access
D) Motivation issue 😅

Comment your letter! 👇""",

        """Last time you had a full check-up? 🏥

A) This year
B) 2–3 years ago
C) Only when sick
D) Too long ago 😬

Drop your letter 👇""",
    ],

    "money": [
        """Where does most of your salary go? 💸

A) Rent + daily expenses
B) Sending money home
C) Savings + investments
D) Disappears somehow 😅

Drop your letter 👇""",

        """Do you have a budget? 📊

A) Yes, I track everything
B) Rough idea lang
C) Used to, then stopped
D) Never tried 😅

Comment your letter! 👇""",

        """Your relationship with money? 💰

A) Solid — I save consistently
B) Complicated 😅
C) Comes and goes too fast
D) Need serious help lol

Drop your letter 👇""",

        """How much do you save monthly? 🏦

A) Nothing yet
B) Less than 10%
C) 10–20%
D) 20%+ 💪

Any amount counts! Drop your letter 👇""",

        """If you lost your job tomorrow — how long could you survive? 😬

A) Less than 1 month
B) 1–3 months
C) 3–6 months
D) 6+ months, I'm ready 💪

Real talk. Drop your letter 👇""",

        """Biggest money mistake? 💭

A) Not saving earlier
B) Lent money, never returned 😅
C) Bought things I didn't need
D) Didn't invest when I could

We've all been there! Drop your letter 👇""",
    ],

    "sideincome": [
        """Do you have income outside your main job? 💼

A) Yes!
B) Building one now
C) Want to but don't know how
D) Just salary for now

Drop your letter 👇""",

        """What stops you from starting a side income? 🤔

A) No time
B) Don't know what to start
C) Scared to lose money
D) Already have one! 🙌

Comment your letter 👇""",

        """Extra $500 right now — what do you do? 💡

A) Save it
B) Invest in stocks
C) Start a small business
D) Expenses talaga 😅

Drop your letter! 👇""",

        """What side income are you most interested in? 🌱

A) Online selling
B) Freelancing
C) Network marketing
D) Content creation

No wrong answer! Comment your letter 👇""",

        """How many income streams do you have? 📈

A) Just 1 (salary)
B) Salary + 1 side
C) Multiple already 💪
D) Working on #2 now

Drop your number 👇""",

        """If you had a stable $500/month extra income? 🎯

A) Finally save properly
B) Send more home
C) Invest it
D) Pay off debt first

Comment your letter! 👇""",
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
