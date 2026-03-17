"""
main.py
Poll Post Auto-Poster pipeline.
Runs Mon/Wed/Fri at 12:30 PM SGT via GitHub Actions.

Run modes:
  python main.py                    → full pipeline (generate + post)
  python main.py --dry-run          → generate and print, skip FB post
  python main.py --topic ofw        → force a specific topic
  python main.py --topic health     → force health topic
  python main.py --topic money      → force money topic
  python main.py --topic sideincome → force side income topic
"""

import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from poll_generator import generate_poll, get_topic_for_today, TOPICS
from fb_poster      import post_poll_to_facebook

LOG_DIR = "output_logs"
os.makedirs(LOG_DIR, exist_ok=True)


def save_log(topic: str, caption: str, posted: bool):
    """Save poll log so we can track what was posted."""
    log_file = os.path.join(LOG_DIR, "poll_log.json")
    logs = []

    # Load existing logs
    if os.path.exists(log_file):
        try:
            with open(log_file) as f:
                logs = json.load(f)
        except Exception:
            logs = []

    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic":     topic,
        "posted":    posted,
        "caption":   caption[:100] + "...",
    })

    # Keep last 50 logs only
    logs = logs[-50:]
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


def run_pipeline(dry_run: bool = False, topic: str = None):
    print("\n" + "=" * 60)
    print("  📊  Poll Post Auto-Poster")
    print("  📅  " + datetime.now().strftime("%Y-%m-%d %H:%M") + " (UTC)")
    print("=" * 60)

    # ── Step 1: Determine topic ───────────────────────────────────
    if topic:
        if topic not in TOPICS:
            print(f"❌ Invalid topic '{topic}'. Choose from: {', '.join(TOPICS)}")
            return
        print(f"\n[1/2] Topic forced: {topic.upper()}")
    else:
        topic = get_topic_for_today()
        print(f"\n[1/2] Topic for today: {topic.upper()}")

    # ── Step 2: Generate poll ─────────────────────────────────────
    result  = generate_poll(topic)
    caption = result["caption"]

    print(f"\n{'─'*60}")
    print(caption)
    print(f"{'─'*60}")
    print(f"\n📏 Length: {len(caption)} characters")

    # ── Step 3: Post to Facebook ──────────────────────────────────
    if dry_run:
        print("\n[2/2] DRY RUN — skipping Facebook post.")
        save_log(topic, caption, posted=False)
        print("✅ Dry run complete!")
        return

    print("\n[2/2] Posting to Facebook...")
    success = post_poll_to_facebook(caption)
    save_log(topic, caption, posted=success)

    if success:
        print("\n🎉 Poll posted successfully!")
    else:
        print("\n❌ Poll post failed — check credentials.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll Post Auto-Poster")
    parser.add_argument("--dry-run", action="store_true",  help="Generate without posting")
    parser.add_argument("--topic",   type=str, default=None,
                        help=f"Force topic: {', '.join(TOPICS)}")
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run, topic=args.topic)
