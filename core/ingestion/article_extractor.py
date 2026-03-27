"""
AACIE V5 - Article Extractor (Jina Reader API)
==============================================
Extracts pristine markdown from any URL using the Jina AI Reader API.
"""

import requests
from datetime import datetime
from core.config import Config, get_logger

logger = get_logger("ArticleExtractor")

class ArticleExtractor:
    def __init__(self):
        self.api_key = Config.JINA_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": "markdown"
        } if self.api_key else {}

    def extract(self, url: str) -> dict:
        jina_url = f"https://r.jina.ai/{url}"
        logger.info(f"Extracting markdown via Jina: {url}")
        
        try:
            resp = requests.get(jina_url, headers=self.headers, timeout=Config.SCRAPE_TIMEOUT)
            resp.raise_for_status()
            
            markdown_content = resp.text
            title = "Article"
            
            # Simple heuristic to find Title in markdown
            for line in markdown_content.split('\n')[:15]:
                if line.startswith('#'):
                    title = line.strip('#* ').strip()
                    break

            return {
                "url": url,
                "title": title[:200],
                "markdown": markdown_content[:20000],  # Give Llama-3 plenty of context
                "scraped_at": datetime.utcnow().isoformat(),
                "success": True
            }
        except Exception as e:
            logger.error(f"Jina Reader extraction failed for {url}: {e}")
            return {
                "url": url,
                "title": "Failed to scrape",
                "markdown": "",
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }
