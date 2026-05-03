import sys, requests, time
from bs4 import BeautifulSoup

def get_video_urls_from_page(page_url):
    video_urls = []
    try:
        resp = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/view_video.php?viewkey=' in href:
                full = f"https://www.pornhub.com{href}" if not href.startswith('http') else href
                video_urls.append(full)
    except:
        pass
    return video_urls

if __name__ == "__main__":
    model_url = sys.argv[1].rstrip('/')
    all_urls = []
    page = 1
    while True:
        page_url = f"{model_url}?page={page}"
        urls = get_video_urls_from_page(page_url)
        if not urls:
            break
        all_urls.extend(urls)
        page += 1
        time.sleep(1)   # رعایت نرخ درخواست
    for url in all_urls:
        print(url)
