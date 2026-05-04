#!/usr/bin/env python3
"""
Pornhub Model Page Scraper
Usage: ph_scraper.py <model_url>
Output: One video URL per line (newest first)
"""
import requests
import re
import sys
import time
from urllib.parse import urljoin

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

def get_videos_from_page(html):
    """Extract video viewkeys from a model's page HTML."""
    # الگوی رایج در لینک‌های ویدیو
    pattern = r'<a\s+href="/view_video.php\?viewkey=([a-zA-Z0-9]+)"'
    keys = re.findall(pattern, html)
    return [f"https://www.pornhub.com/view_video.php?viewkey={k}" for k in keys]

def scrape_model(base_url):
    """Scrape all pages of a model's video list."""
    base_url = base_url.rstrip("/")
    # مدل‌ها دو نوع URL دارند: /model/username یا /pornstar/username
    # هر دو از پارامتر صفحه پشتیبانی می‌کنند: ?page=1
    page = 1
    videos = []
    seen = set()

    while True:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"

        print(f"Fetching page {page}...", file=sys.stderr)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"Error on page {page}: {e}", file=sys.stderr)
            break

        new_videos = get_videos_from_page(html)
        if not new_videos:
            # No videos found -> probably last page
            break

        added = 0
        for v in new_videos:
            if v not in seen:
                seen.add(v)
                videos.append(v)
                added += 1

        if added == 0:
            # All new videos were already seen (duplicate page? stop)
            break

        # Check if there is a next page link (optional, for safety)
        if "page=" in url and "?page=" in url:
            # already on a numbered page, try next
            page += 1
        else:
            # first page: check if there is a "next" link or just try ?page=2
            page += 1

        time.sleep(1)  # مودبانه اسکرپ کن

    return videos

def main():
    if len(sys.argv) < 2:
        print("Usage: ph_scraper.py <model_url>", file=sys.stderr)
        sys.exit(1)

    model_url = sys.argv[1]
    video_list = scrape_model(model_url)

    if not video_list:
        print("No videos found.", file=sys.stderr)
        sys.exit(0)

    # چاپ آدرس ویدیوها (اول جدیدترین)
    for v in video_list:
        print(v)

if __name__ == "__main__":
    main()
