# 📊 Poll Post Auto-Poster

Automated Facebook poll post generator that runs Mon/Wed/Fri at 12:30 PM SGT.
Targets Filipinos in Singapore and Philippines with relatable, engaging poll questions
across 4 rotating topics.

## Why polls?

Poll-style posts (A/B/C/D comment format) consistently get the highest engagement
on Facebook because:
- People love sharing opinions
- Commenting signals high engagement to Facebook's algorithm
- More comments = more reach = more followers

## Topic rotation

| Day | Topic |
|-----|-------|
| Monday | 🌏 OFW / Overseas worker life |
| Wednesday | 🏥 Health & wellness habits |
| Friday | 💰 Money/savings OR 💼 Side income (alternates weekly) |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys

# Test all topics without posting
python main.py --dry-run
python main.py --dry-run --topic ofw
python main.py --dry-run --topic health
python main.py --dry-run --topic money
python main.py --dry-run --topic sideincome

# Run for real
python main.py
```

## Keys needed (same as your other posters!)

| Key | Required |
|-----|---------|
| `FB_PAGE_ID` | ✅ Yes |
| `FB_ACCESS_TOKEN` | ✅ Yes |
| `GEMINI_API_KEY` | Optional (uses fallback library if not set) |

## Fallback library

Even without Gemini, the app has 24 hand-written polls (6 per topic) that rotate
automatically — so it never fails to post.

## Full daily schedule (all 3 repos combined)

| Time SGT | Post | Repo |
|----------|------|------|
| 9:00 AM | 🏥 Health news | news-generator |
| 12:30 PM | 📊 Poll post | poll-poster (this repo) |
| 7:00 PM | 💰 Finance news | finance-poster |
