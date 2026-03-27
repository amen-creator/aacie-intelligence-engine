"""
AACIE V5 - Feed Reader & URL Discovery
=======================================
Discovers Arabic news URLs via RSS feeds and DuckDuckGo.
Proxies requests through ScraperAPI for ultimate reliability.
"""

import feedparser
import urllib.parse
from ddgs import DDGS
from datetime import datetime
from core.config import Config, get_logger

logger = get_logger("FeedReader")

class FeedReader:
    def __init__(self):
        self.scraper_api_key = Config.SCRAPER_API_KEY
        
    def _proxied_url(self, target_url: str) -> str:
        """Wraps a URL in the ScraperAPI endpoint to bypass regional/bot blocks."""
        if not self.scraper_api_key:
            return target_url
        payload = {'api_key': self.scraper_api_key, 'url': target_url}
        encoded = urllib.parse.urlencode(payload)
        return f"http://api.scraperapi.com/?{encoded}"

    def fetch_rss(self, feed_url: str, limit: int = 5) -> list[dict]:
        """Fetches an RSS feed using ScraperAPI proxy to prevent blocking."""
        target = self._proxied_url(feed_url) if self.scraper_api_key else feed_url
        logger.info(f"Fetching RSS Feed: {feed_url}")
        
        try:
            feed = feedparser.parse(target)
            results = []
            for entry in feed.entries[:limit]:
                results.append({
                    "url": entry.link,
                    "title": entry.title,
                    "source": "RSS",
                    "published_at": getattr(entry, "published", datetime.utcnow().isoformat())
                })
            return results
        except Exception as e:
            logger.error(f"RSS Fetch Error ({feed_url}): {e}")
            return []

    def fetch_ddg(self, query: str, limit: int = 10) -> list[dict]:
        """Fetches news results using DuckDuckGo via the ddgs library."""
        logger.info(f"Fetching DuckDuckGo News for: {query}")
        try:
            results = []
            with DDGS() as ddgs:
                ddg_news = ddgs.news(query, region="wt-wt", safesearch="moderate", max_results=limit)
                for item in ddg_news:
                    results.append({
                        "url": item.get("url"),
                        "title": item.get("title", ""),
                        "source": item.get("source", "DDG"),
                        "published_at": item.get("date", datetime.utcnow().isoformat())
                    })
            return results
        except Exception as e:
            logger.error(f"DDG Search Error ({query}): {e}")
            return []
