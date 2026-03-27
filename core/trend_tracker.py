"""
AACIE v2 - Trend & Anomaly Tracker
===================================
Tracks keyword velocity over time and detects sentiment anomalies
to surface breaking news or shifting public opinion.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"

class TrendTracker:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.snapshots_file = DATA_DIR / "trends.json"
        
    def _load_snapshots(self) -> list:
        if self.snapshots_file.exists():
            with open(self.snapshots_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_snapshots(self, data: list):
        with open(self.snapshots_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def process_new_batch(self, analysed_articles: list) -> dict:
        """
        Process a new batch of articles, update historical trends,
        and generate alerts for anomalies.
        """
        if not analysed_articles:
            return {}

        current_time = datetime.utcnow().isoformat()
        
        # 1. Aggregate current batch
        keywords = {}
        total_score = 0
        valid_scores = 0
        
        for art in analysed_articles:
            a = art.get('analysis', {})
            # Aggregate keywords
            for kw in a.get('keywords', []):
                keywords[kw] = keywords.get(kw, 0) + 1
            # Aggregate sentiment
            if 'sentiment_score' in a:
                total_score += a['sentiment_score']
                valid_scores += 1
                
        avg_sentiment = total_score / valid_scores if valid_scores > 0 else 0
        top_keywords = {k: v for k, v in sorted(keywords.items(), key=lambda item: item[1], reverse=True)[:20]}

        snapshot = {
            "timestamp": current_time,
            "article_count": len(analysed_articles),
            "avg_sentiment": avg_sentiment,
            "top_keywords": top_keywords
        }
        
        history = self._load_snapshots()
        history.append(snapshot)
        # Keep last 100 snapshots
        history = history[-100:]
        self._save_snapshots(history)
        
        # 2. Detect Anomalies (compare with previous snapshot)
        alerts = []
        if len(history) >= 2:
            prev = history[-2]
            
            # Sentiment swing alert
            sentiment_diff = avg_sentiment - prev.get('avg_sentiment', 0)
            if abs(sentiment_diff) > 0.4:
                alerts.append({
                    "type": "sentiment_swing",
                    "severity": "high",
                    "message": f"تحول حاد في المشاعر! ({sentiment_diff:+.2f})",
                    "timestamp": current_time
                })
                
            # Surging keyword alert
            prev_kws = prev.get('top_keywords', {})
            for kw, count in top_keywords.items():
                prev_count = prev_kws.get(kw, 0)
                if prev_count == 0 and count >= 3:
                     alerts.append({
                        "type": "keyword_surge",
                        "severity": "medium",
                        "message": f"موضوع صاعد بقوة: '{kw}'",
                        "timestamp": current_time
                    })
        
        return {
            "snapshot": snapshot,
            "alerts": alerts
        }
        
    def get_timeline_data(self) -> dict:
        """Format historical data for UI charting."""
        history = self._load_snapshots()
        return {
            "timestamps": [s["timestamp"] for s in history],
            "sentiments": [s["avg_sentiment"] for s in history],
            "volumes": [s["article_count"] for s in history]
        }
