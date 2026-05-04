#!/usr/bin/env python3
"""
Bunkr Album Link Extractor
Usage: bunkr.py <album_url>
Output: One link per line (direct download or media page)
"""
import requests
import re
import sys
import json

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

def extract_album_id(url):
    # لینک‌های Bunkr معمولاً به شکل https://bunkr.is/a/abc123 یا https://bunkr.is/album/abc123
    m = re.search(r'/(?:a|album)/([a-zA-Z0-9]+)', url)
    return m.group(1) if m else None

def get_album_files(album_id):
    api_url = f"https://bunkr.is/api/api/{album_id}/getFiles"
    resp = requests.get(api_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # ساختار پاسخ: {"data": {"items": [{"file": {"urlDownload": "..."}}, ...]}}
    items = data.get("data", {}).get("items", [])
    links = []
    for item in items:
        file_info = item.get("file", {})
        download_url = file_info.get("urlDownload") or file_info.get("cd?
        # گاهی لینک مستقیم در urlDownload هست
        if download_url:
            links.append(download_url)
    return links

def main():
    if len(sys.argv) < 2:
        print("Usage: bunkr.py <album_url>", file=sys.stderr)
        sys.exit(1)

    album_url = sys.argv[1]
    album_id = extract_album_id(album_url)
    if not album_id:
        print("Could not extract album ID from URL.", file=sys.stderr)
        sys.exit(1)

    try:
        links = get_album_files(album_id)
    except Exception as e:
        print(f"Error fetching album: {e}", file=sys.stderr)
        sys.exit(1)

    if not links:
        print("No downloadable files found.", file=sys.stderr)
    else:
        for link in links:
            print(link)

if __name__ == "__main__":
    main()
