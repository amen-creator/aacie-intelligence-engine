"""
AACIE V5 - HuggingFace Specialized Fallback Engine
===================================================
Optionally utilizes HuggingFace Inference API for specialized 
zero-shot classification if the primary Groq engine fails.
"""

import requests
from core.config import Config, get_logger

logger = get_logger("HuggingFaceFallback")

class HuggingFaceAnalyzer:
    def __init__(self):
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self.model = "CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def analyse_sentiment(self, text: str) -> str:
        """Fallback sentiment analysis using an open-source Arabic model."""
        if not self.is_available():
            return "محايد"
            
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        try:
            response = requests.post(url, headers=self.headers, json={"inputs": text[:500]}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Returns [[{'label': 'positive', 'score': 0.9}, ...]]
                best_label = data[0][0]["label"]
                if "positive" in best_label.lower(): return "إيجابي"
                if "negative" in best_label.lower(): return "سلبي"
        except Exception as e:
            logger.warning(f"HuggingFace inference failed: {e}")
            
        return "محايد"
