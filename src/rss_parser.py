import requests
import json
import xml.etree.ElementTree as ET

FEEDS = {
    "OilPrice.com": "https://oilprice.com/rss/main",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "S&P Global Commodity": "https://www.spglobal.com/commodityinsights/en/rss-feed/oil",
    "Energy Intelligence": "https://www.energyintel.com/rss",
    "Platts Oil": "https://www.spglobal.com/platts/en/rss-feed/oil",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/marketpulse/",
    "Seeking Alpha Energy": "https://seekingalpha.com/tag/energy.xml",
    "Natural Gas Intel": "https://www.naturalgasintel.com/feed/",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def fetch_feed(name, url, max_items=10):
    print(f"  Парсим: {name}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        print(f"    HTTP {r.status_code}", end=" ")
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "")
            desc = item.findtext("description", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            if title:
                items.append({"source": name, "title": title, "summary": desc, "link": link, "published": pub})
        print(f"→ {len(items)} новостей")
        return items
    except Exception as e:
        print(f"→ недоступен ({type(e).__name__})")
        return []

def main():
    print("=== Проверяем источники ===\n")
    all_news = []
    for name, url in FEEDS.items():
        items = fetch_feed(name, url)
        all_news.extend(items)

    print(f"\nВсего новостей: {len(all_news)}")
    with open("data/raw_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("✓ Сохранено в data/raw_news.json")
    print("\n--- Примеры заголовков ---")
    for item in all_news[:8]:
        print(f"[{item['source']}] {item['title']}")

if __name__ == "__main__":
    main()
