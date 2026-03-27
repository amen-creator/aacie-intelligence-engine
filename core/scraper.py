"""
AACIE v4 - Jina Data Ingestion Engine
======================================
Blazing fast markdown extraction using the Jina Reader API
replacing the heavy Firecrawl engine.
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

_JINA_API_KEY = os.getenv("JINA_API_KEY", "")

class ArabicScraper:
    """
    V4 Ultra-Fast Scraper using Jina Reader API.
    Converts any web URL into pristine Markdown instantaneously.
    """
    def __init__(self):
        self.api_key = _JINA_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": "markdown"
        } if self.api_key else {}

    def extract_article(self, url: str) -> dict:
        """
        Uses Jina API to extract markdown text from a news URL.
        """
        jina_url = f"https://r.jina.ai/{url}"
        
        try:
            resp = requests.get(jina_url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            
            markdown_content = resp.text
            
            title = "Article"
            # Attempt to extract title from the first heading if present
            for line in markdown_content.split('\n')[:10]:
                if line.startswith('#'):
                    title = line.strip('#* ').strip()
                    break

            return {
                "url": url,
                "title": title[:200],
                "markdown": markdown_content[:15000],  # Give enough for Llama3 70B
                "scraped_at": datetime.utcnow().isoformat(),
                "success": True
            }
        except Exception as e:
            print(f"[!] Jina Reader extraction failed for {url}: {e}")
            return {
                "url": url,
                "title": "Failed to scrape",
                "markdown": "",
                "scraped_at": datetime.utcnow().isoformat(),
                "success": False
            }

def get_remaining_quota() -> str:
    """Jina Free Tier is very generous but doesn't expose headers easily, returning mock."""
    return "Unlimited (Free Tier)"
