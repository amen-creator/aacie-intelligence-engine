"""
AACIE V5 - Ingestion Module
===========================
Exports unified components for gathering and extracting news.
"""

from .feed_reader import FeedReader
from .article_extractor import ArticleExtractor

class IngestionPipeline:
    def __init__(self):
        self.reader = FeedReader()
        self.extractor = ArticleExtractor()

    def gather_and_extract(self, rss_sources: list[str], search_queries: list[str], limit: int = 5) -> list[dict]:
        """Gathers URLs from feeds and DDG, then uses Jina to extract markdown."""
        urls = set()
        for src in rss_sources:
            for item in self.reader.fetch_rss(src, limit):
                urls.add(item["url"])
                
        for q in search_queries:
            for item in self.reader.fetch_ddg(q, limit):
                urls.add(item["url"])

        extracted = []
        for url in list(urls)[:limit * 2]: # Safe limit to avoid overwhelming Jina
            data = self.extractor.extract(url)
            if data["success"]:
                extracted.append(data)
                
        return extracted
