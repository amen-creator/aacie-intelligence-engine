"""
AACIE v2 – Supervisor Database Layer
=====================================
Enhanced schema with tracking for entities, topics, and urgency.
Includes a robust offline JSON fallback that persists across agent cycles.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client, Client
    _SUPABASE_AVAILABLE = True
except ImportError:
    _SUPABASE_AVAILABLE = False
    Client = None  # type: ignore

SCHEMA_SQL = """
-- v2 Schema additions
ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS entities JSONB,
ADD COLUMN IF NOT EXISTS urgency_score FLOAT;
"""

LOCAL_DB_FILE = Path(__file__).parent.parent / "data" / "local_db.json"

class Database:
    def __init__(self):
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        self._mem_articles = []
        self._mem_analysis = []
        
        if _SUPABASE_AVAILABLE and url and key and not url.startswith("your_") and not url.startswith("https://your"):
            self.client: Client = create_client(url, key)
            self._online = True
        else:
            self.client = None
            self._online = False
            self._load_local_db()

    def _load_local_db(self):
        LOCAL_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOCAL_DB_FILE.exists():
            with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._mem_articles = data.get("articles", [])
                self._mem_analysis = data.get("analysis", [])

    def _save_local_db(self):
        with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "articles": self._mem_articles,
                "analysis": self._mem_analysis
            }, f, ensure_ascii=False)

    def upsert_article(self, article: dict) -> dict | None:
        payload = {
            "url":         article.get("url", ""),
            "title":       article.get("title", ""),
            "source_name": article.get("source_name", "DDG"),
            "region":      article.get("region", "global"),
            "markdown":    article.get("markdown", "")[:10000],
            "scraped_at":  article.get("scraped_at", datetime.utcnow().isoformat()),
            "is_mock":     article.get("is_mock", False),
        }
        if self._online:
            try:
                resp = self.client.table("articles").upsert(payload, on_conflict="url").execute()
                return resp.data[0] if resp.data else None
            except: pass
            
        # Offline logic Update or Insert
        for existing in self._mem_articles:
            if existing["url"] == payload["url"]:
                existing.update(payload)
                self._save_local_db()
                return existing
                
        payload["id"] = len(self._mem_articles) + 1
        self._mem_articles.append(payload)
        self._save_local_db()
        return payload

    def get_recent_articles(self, limit: int = 200) -> list[dict]:
        if self._online:
            try:
                resp = self.client.table("articles").select("*, analysis_results(*)").order("scraped_at", desc=True).limit(limit).execute()
                return resp.data or []
            except: pass
            
        # Join memory data
        joined = []
        for a in self._mem_articles[-limit:][::-1]:
            aid = a.get("id")
            ana = next((an for an in self._mem_analysis if an.get("article_id") == aid), {})
            joined.append({**a, "analysis": ana})
        return joined

    def save_analysis(self, article_id: int | None, analysis: dict) -> dict | None:
        payload = {
            "article_id":          article_id,
            "dialect":             analysis.get("dialect"),
            "dialect_confidence":  analysis.get("dialect_confidence", 0.0),
            "sentiment":           analysis.get("sentiment"),
            "sentiment_score":     analysis.get("sentiment_score", 0.0),
            "keywords":            analysis.get("keywords", []),
            "summary":             analysis.get("summary", ""),
            "topics":              analysis.get("topics", []),
            "entities":            analysis.get("entities", {}),
            "urgency_score":       analysis.get("urgency_score", 0.0),
            "sarcasm_detected":    analysis.get("sarcasm_probability", 0.0) > 0.6,
            "analysed_at":         datetime.utcnow().isoformat(),
        }
        if self._online:
            try:
                resp = self.client.table("analysis_results").insert(payload).execute()
                return resp.data[0] if resp.data else None
            except: pass
            
        # Overwrite if exists
        for i, existing in enumerate(self._mem_analysis):
            if existing["article_id"] == article_id:
                self._mem_analysis[i] = payload
                self._save_local_db()
                return payload
                
        payload["id"] = len(self._mem_analysis) + 1
        self._mem_analysis.append(payload)
        self._save_local_db()
        return payload

    def get_analysis_stats(self) -> dict:
        data = self.get_recent_articles()
        total = len(data)
        sent_counts = {}
        dial_counts = {}
        top_kws = {}
        score_sum = 0.0
        
        for row in data:
            a = row.get("analysis", {})
            s = a.get("sentiment", "محايد")
            d = a.get("dialect", "فصحى")
            sc = float(a.get("sentiment_score", 0))
            
            sent_counts[s] = sent_counts.get(s, 0) + 1
            dial_counts[d] = dial_counts.get(d, 0) + 1
            score_sum += sc
            
            for k in a.get("keywords", []):
                top_kws[k] = top_kws.get(k, 0) + 1
                
        sorted_kws = dict(sorted(top_kws.items(), key=lambda x: x[1], reverse=True)[:10])

        return {
            "total_analysed": total,
            "sentiment_distribution": sent_counts,
            "dialect_distribution": dial_counts,
            "avg_sentiment_score": round(score_sum / total, 3) if total else 0.0,
            "top_keywords": sorted_kws
        }
