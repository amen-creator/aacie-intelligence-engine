"""
AACIE v2 - Multi-Source Data Aggregator
========================================
Pulls data from multiple APIs and Feeds to provide a rich dataset.
Sources: RSS Feeds, DuckDuckGo Search APIs, NewsAPI (opt), Firecrawl (opt).
"""

import os
import json
import time
from datetime import datetime
import feedparser
from duckduckgo_search import DDGS
from duckduckgo_search import DDGS
from core.scraper import ArabicScraper

# ── Multi-Source Configuration ───────────────────────────────────────────────
RSS_FEEDS = [
    {"name": "الجزيرة",      "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9", "region": "gulf"},
    {"name": "سكاي نيوز",   "url": "https://www.skynewsarabia.com/rss.xml",     "region": "global"},
    {"name": "فرانس 24",    "url": "https://www.france24.com/ar/rss",           "region": "global"},
    {"name": "بي بي سي",    "url": "http://feeds.bbci.co.uk/arabic/rss.xml",    "region": "global"},
    {"name": "اليوم السابع", "url": "https://www.youm7.com/rss/SectionRss?SectionID=65", "region": "egypt"},
    {"name": "هسبريس",       "url": "https://www.hespress.com/feed",            "region": "morocco"},
]


class DataAggregator:
    """Aggregates content autonomously from various free/cheap sources."""

    def __init__(self):
        self.scraper = ArabicScraper()
        
    def fetch_all(self, limit_per_source=5) -> list[dict]:
        """Fetch from all available sources and normalize."""
        print("\n[Aggregator] Starting multi-source data collection...")
        all_articles = []
        
        # 1. Fetch RSS Feeds (Fast, Free, Reliable)
        all_articles.extend(self._fetch_rss(limit_per_source))
        
        # 2. Fetch DuckDuckGo News (Trending, Free)
        all_articles.extend(self._fetch_ddg_news(limit_per_source))
        
        # 3. Firecrawl Deep Scrapes (High Value, Quota limited)
        # We only deep scrape 1-2 articles to save quota in v2
        print("[Aggregator] Running deep scrape on top headlines...")
        deep_articles = self.scraper.scrape_all_sources(pages_per_source=1)
        all_articles.extend(deep_articles)
        
        # Deduplicate by URL
        unique = {art['url']: art for art in all_articles if art.get('url')}
        final_list = list(unique.values())
        print(f"[Aggregator] Collected {len(final_list)} unique raw articles.")
        return final_list

    def _fetch_rss(self, limit: int) -> list[dict]:
        """Parse RSS feeds and return normalized article dicts."""
        articles = []
        for feed in RSS_FEEDS:
            try:
                print(f"  -> Pulling RSS: {feed['name']}...")
                parsed = feedparser.parse(feed["url"])
                for entry in parsed.entries[:limit]:
                    # Build markdown from title and summary
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    # Clean HTML tags roughly
                    import re
                    clean_summary = re.sub(r'<[^>]+>', '', summary)
                    
                    md_content = f"## {title}\n\n{clean_summary}"
                    
                    articles.append({
                        "url": entry.get("link", f"rss_{hash(title)}"),
                        "title": title,
                        "markdown": md_content,
                        "source_name": feed["name"],
                        "region": feed["region"],
                        "scraped_at": datetime.utcnow().isoformat(),
                        "is_mock": False,
                        "source_type": "rss"
                    })
            except Exception as e:
                print(f"  [X] Failed RSS {feed['name']}: {e}")
        return articles

    def _fetch_ddg_news(self, limit: int) -> list[dict]:
        """Fetch trending Arabic news from DDG Search."""
        print(f"  -> Pulling DuckDuckGo News (Arabic)...")
        articles = []
        try:
            with DDGS() as ddgs:
                # Search for general news terms in Arabic
                results = list(ddgs.news("أخبار الشرق الأوسط الاقتصاد", region="xa-ar", max_results=limit*2))
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    md_content = f"## {title}\n\n{body}"
                    articles.append({
                        "url": r.get("url", f"ddg_{hash(title)}"),
                        "title": title,
                        "markdown": md_content,
                        "source_name": r.get("source", "DDG Search"),
                        "region": "global",
                        "scraped_at": datetime.utcnow().isoformat(),
                        "is_mock": False,
                        "source_type": "ddg_api"
                    })
        except Exception as e:
            print(f"  [X] Failed DDG search: {e}")
        return articles
