"""
AACIE V5 - Intelligence Module
==============================
Exposes the ArabicAnalyzer which intelligently routes NLP 
workloads to Groq Llama-3 70B and HuggingFace fallbacks.
"""

from datetime import datetime
from .groq_analyzer import GroqAnalyzer
from .huggingface_fallback import HuggingFaceAnalyzer
from core.config import get_logger

logger = get_logger("ArabicAnalyzer")

class ArabicAnalyzer:
    def __init__(self):
        self.primary = GroqAnalyzer()
        self.fallback = HuggingFaceAnalyzer()

    def analyse(self, text: str) -> dict:
        """Analyzes text using the V5 Enterprise Architecture (Groq -> Rule-based)."""
        if not text.strip():
            return self._empty_result()
            
        if self.primary.is_available():
            res = self.primary.analyse(text)
            if res:
                return res
                
        # If Groq fails or is not configured, fallback to rule-based + HF sentiment
        logger.warning("Groq analysis failed or omitted. Falling back to specialized NLP.")
        sentiment = self.fallback.analyse_sentiment(text)
        return self._rule_based_analyse(text, sentiment)

    def _rule_based_analyse(self, text: str, sentiment: str) -> dict:
        return {
            "dialect": "فصحى", 
            "dialect_confidence": 0.5,
            "sentiment": sentiment,
            "sentiment_score": 0.5 if sentiment == "إيجابي" else -0.5 if sentiment == "سلبي" else 0.0,
            "sarcasm_probability": 0.0,
            "entities": {"persons": [], "locations": [], "orgs": []},
            "topics": ["عام"],
            "keywords": [],
            "summary": text[:200] + "...",
            "urgency_score": 0.3
        }

    def _empty_result(self) -> dict:
        return {
            "dialect": "غير محدد", "dialect_confidence": 0.0,
            "sentiment": "محايد", "sentiment_score": 0.0,
            "sarcasm_probability": 0.0, "entities": {},
            "topics": [], "keywords": [], "summary": "", "urgency_score": 0.0
        }

    def analyse_articles(self, articles: list[dict]) -> list[dict]:
        results = []
        for art in articles:
            content = art.get("markdown", art.get("title", ""))
            analysis = self.analyse(content)
            results.append({
                **art,
                "analysis": analysis,
                "analysed_at": datetime.utcnow().isoformat(),
            })
        return results
