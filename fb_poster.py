"""
fb_poster.py
Posts text-only poll posts to Facebook Page.
No image needed — text polls get more comments which boosts algorithm reach.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FB_PAGE_ID      = os.getenv("FB_PAGE_ID", "")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
GRAPH_API_URL   = "https://graph.facebook.com/v19.0"


def post_poll_to_facebook(caption: str) -> bool:
    """Post a text-only poll post to the Facebook Page."""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("  ❌ FB_PAGE_ID or FB_ACCESS_TOKEN not set in .env")
        return False

    try:
        print("  📢 Publishing poll post to Facebook...")
        resp = requests.post(
            f"{GRAPH_API_URL}/{FB_PAGE_ID}/feed",
            data={
                "access_token": FB_ACCESS_TOKEN,
                "message":      caption,
            },
            timeout=30,
        )
        data = resp.json()
        if "id" in data:
            print(f"  ✅ Poll posted! Post ID: {data['id']}")
            return True
        else:
            print(f"  ❌ Post failed: {data}")
            return False

    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


if __name__ == "__main__":
    print("FB_PAGE_ID set     :", bool(FB_PAGE_ID))
    print("FB_ACCESS_TOKEN set:", bool(FB_ACCESS_TOKEN))
