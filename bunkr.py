import os, sys, json, time, base64, requests
from math import floor
from itertools import cycle
from urllib.parse import urlparse

BUNKRR_API = "https://bunkr.cr/api/vs"
BUNKRR_DOMAINS = ("bunkr.si", "bunkr.fi", "bunkr.ru", "bunkr.cr", "bunkr.rip", "bunkrr.su")
BUNKRR_DOWNLOAD_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://get.bunkrr.su/"}
_offline_subs = set()

def is_bunkr_url(url): return any(dom in url for dom in BUNKRR_DOMAINS)

def get_slug(url):
    match = __import__("re").search(r"/([a-zA-Z0-9_-]+)$", url)
    return match.group(1) if match else None

def fetch_api(url):
    slug = get_slug(url)
    if not slug: return None
    for dom in (BUNKRR_API.split("/")[2], *_offline_subs):
        try:
            resp = requests.post(f"https://{dom}/api/vs", json={"slug": slug}, headers=BUNKRR_DOWNLOAD_HEADERS, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 502:
                _offline_subs.add(dom)
        except:
            continue
    return None

def decrypt(api_resp):
    try:
        t, enc = api_resp["timestamp"], base64.b64decode(api_resp["url"])
        key_cycle = cycle(f"SECRET_KEY_{floor(t/3600)}".encode("utf-8"))
        dec = bytearray(b ^ next(key_cycle) for b in enc)
        return dec.decode("utf-8", errors="ignore")
    except:
        return None

if __name__ == "__main__":
    url = sys.argv[1]
    outdir = sys.argv[2]
    api_resp = fetch_api(url)
    dl_link = decrypt(api_resp) if api_resp else None
    if dl_link:
        filepath = os.path.join(outdir, urlparse(dl_link).path.rstrip("/").split("/")[-1])
        resp = requests.get(dl_link, headers=BUNKRR_DOWNLOAD_HEADERS, stream=True)
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
