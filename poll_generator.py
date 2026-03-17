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
in Singapore and the Philippines. Your audience includes OFWs, employees, and people 
exploring side income and better health habits.

Create ONE engaging Facebook poll-style post about: {topic_description}

Rules:
- Start with a relatable hook question or statement (no emojis on first line)
- Provide exactly 4 options labeled A) B) C) D)
- Each option should be relatable, honest, and non-judgmental
- Add 1-2 sentences after the options to warm up the audience and invite comments
- End with a soft CTA asking people to drop their letter in comments
- Use 2-3 emojis naturally — NOT on the first line
- Keep it under 150 words total
- Sound warm, human, and conversational — like a trusted friend asking
- Occasionally use 1 Tagalog/Taglish word for warmth (optional, only if natural)
- Do NOT mention any company, product, or brand

Topic: {topic_description}

Respond ONLY with the post caption. No preamble, no quotes around it."""

# ── Hand-written fallback poll library ────────────────────────────────────────
FALLBACK_POLLS = {
    "ofw": [
        """Most OFWs send money home every month — but how much do YOU keep for yourself? 💸

A) Less than 10% of my salary
B) 10–20% of my salary
C) More than 20%
D) Still figuring this out 😅

Be honest — no judgment here! This is something we don't talk about enough.
Drop your letter below 👇""",

        """How long have you been working abroad? 🌏

A) Less than 2 years
B) 2–5 years
C) 5–10 years
D) More than 10 years

Whether you're new or a veteran OFW — you're brave for doing what you do. 💪
Comment your letter and tell us where you're based! 👇""",

        """What's the hardest part of being an OFW? 😔

A) Missing family milestones back home
B) Feeling lonely even in a crowd
C) Financial pressure to support everyone
D) Uncertainty about the future

You're not alone in this. Drop your letter below 👇 Let's support each other. ❤️""",

        """When you imagine going back home for good — what's your biggest worry? 🏠

A) Not having enough savings yet
B) No stable income waiting back home
C) Starting over from scratch
D) I'm actually ready to go home now!

This is the real conversation we need to have. 💬 Drop your letter below 👇""",

        """Honest question for OFWs: What does your emergency fund look like right now? 💰

A) Less than 1 month of expenses
B) 1–3 months of expenses
C) 3–6 months of expenses
D) What emergency fund? 😅

No shame — most of us were never taught this. Comment your letter below! 👇""",

        """If you could go back in time to when you first became an OFW — what would you tell yourself? 🕐

A) Save more, spend less
B) Invest earlier
C) Don't forget to take care of yourself too
D) Build a business back home sooner

Drop your letter below 👇 Your answer might help someone just starting out! 💪""",
    ],

    "health": [
        """Be honest — how many glasses of water do you drink daily? 💧

A) Less than 4 glasses
B) 4–6 glasses
C) 7–8 glasses
D) I lost count (which probably means a lot! 😄)

Most of us are more dehydrated than we think. Drop your letter below 👇""",

        """What time do you usually go to sleep on weekdays? 😴

A) Before 10 PM
B) 10 PM – 12 AM
C) 12 AM – 2 AM
D) What is sleep? 😅

Sleep is the most underrated health habit. Comment your letter below! 👇""",

        """Which meal do you most often skip? 🍽️

A) Breakfast
B) Lunch
C) Dinner
D) I never skip meals 💪

For us Filipinos who grew up with "kumain ka na?" — skipping meals hits different! 😄
Drop your letter below 👇""",

        """How would you honestly describe your diet right now? 🥗

A) Mostly healthy, I'm disciplined
B) 50/50 — healthy some days, not others
C) I eat whatever is available
D) Sending help 😅

No judgment — life gets busy! Drop your letter below 👇 Let's be real with each other.""",

        """What's your biggest barrier to exercising regularly? 🏃

A) No time after work
B) Too tired at the end of the day
C) No gym access or equipment
D) Honestly, motivation is the problem 😅

You're not alone! Drop your letter below 👇""",

        """How often do you get a full medical check-up? 🏥

A) Every year without fail
B) Every 2–3 years
C) Only when I feel sick
D) It's been way too long 😬

Prevention is always better than cure. Comment your letter below! 👇""",
    ],

    "money": [
        """Where does most of your salary go every month? 💸

A) Rent and daily expenses
B) Sending money home to family
C) Savings and investments
D) It disappears before I can track it 😅

This is more common than you think. Drop your letter below 👇 No judgment here!""",

        """Do you currently have a household budget? 📊

A) Yes — I track every dollar/peso
B) I have a rough idea but don't write it down
C) I used to but stopped
D) Budgeting? Never tried it 😅

The first step to financial freedom is knowing where your money goes. 💡
Drop your letter below 👇""",

        """What's your current relationship with money? 💰

A) We get along well — I save consistently
B) It's complicated — I try but struggle
C) Money comes and goes too fast
D) We need serious couples therapy 😅

Wherever you are — there's always a next step forward. Drop your letter! 👇""",

        """How much of your income do you currently save every month? 🏦

A) Nothing yet — expenses are too high
B) Less than 10%
C) 10–20%
D) More than 20% 💪

The golden rule is 20% — but any amount is better than zero! 
Comment your letter below 👇""",

        """If you lost your job tomorrow — how long could you survive financially? 😬

A) Less than 1 month
B) 1–3 months
C) 3–6 months
D) More than 6 months — I'm prepared 💪

This question hits different. Drop your letter honestly below 👇
Let's talk about building that safety net together. 💬""",

        """What's your biggest money mistake you wish you could undo? 💭

A) Not saving earlier in life
B) Lending money that was never returned 😅
C) Spending on things I didn't need
D) Not investing when I had the chance

We've all been there! Drop your letter below 👇 Your story might help someone else.""",
    ],

    "sideincome": [
        """Do you currently have any source of income outside your main job? 💼

A) Yes — I already have a side income
B) I'm actively building one right now
C) I want to but don't know where to start
D) Just my salary for now

Wherever you are in this journey — you're already thinking ahead! 💪
Drop your letter below 👇""",

        """What stops you from starting a side income? 🤔

A) No time after work
B) Don't know which business to start
C) Scared of losing money
D) I actually already have one! 🙌

The biggest risk is depending on just one source. Comment your letter below 👇""",

        """If you had an extra $500 to invest right now — what would you do with it? 💡

A) Put it in a savings account
B) Invest in stocks or funds
C) Start a small online business
D) Honestly, it would go to expenses 😅

Every peso/dollar invested today is working for your future self. 
Drop your letter below 👇""",

        """What kind of side income interests you most? 🌱

A) Online selling or e-commerce
B) Freelancing or online services
C) Network marketing or direct sales
D) Content creation or social media

There's no wrong answer — it's about finding what fits YOUR life. 
Comment your letter below 👇 💬""",

        """How many income streams do you currently have? 📈

A) Just my salary — one stream
B) Salary + 1 side income
C) Multiple streams already 💪
D) Working on my second stream now

Financial experts say you need at least 3. Where are you on this journey?
Drop your number below 👇""",

        """What would you do if you had a stable second income of $500/month? 🎯

A) Finally start saving consistently
B) Send more money home to family
C) Invest it for the future
D) Pay off my debts first

Dreams become plans when we get specific. 💡
Comment below and tell us your letter! 👇""",
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
