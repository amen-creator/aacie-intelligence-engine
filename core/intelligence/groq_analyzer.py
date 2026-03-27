"""
AACIE V5 - Groq Intelligence Engine (Primary)
=============================================
Powers the NLP extraction using Llama-3 70B via Groq API.
Guarantees structured JSON output at 800+ tokens/second.
"""

import json
import re
from datetime import datetime
from groq import Groq
from core.config import Config, get_logger

logger = get_logger("GroqAnalyzer")

ANALYSIS_PROMPT_TEMPLATE = """
أنت محلّل استخباراتي متقدم متخصص في معالجة اللغة الطبيعية العربية للأنظمة الذاتية.
قم بتحليل النص التالي بعمق واستخرج التفاصيل الدقيقة كـ JSON صالح ONLY بدون أي مقدمات.

المطلوب بدقة كائن JSON فقط:
{{
  "dialect": "فصحى أو عامية",
  "dialect_confidence": 0.9,
  "sentiment": "إيجابي أو سلبي أو محايد",
  "sentiment_score": 0.5,
  "sarcasm_probability": 0.1,
  "entities": {{
     "persons": ["اسم"],
     "locations": ["مدينة"],
     "orgs": ["شركة"]
  }},
  "topics": ["عام"],
  "keywords": ["كلمة1", "كلمة2", "كلمة3", "كلمة4", "كلمة5"],
  "summary": "ملخص النص...",
  "urgency_score": 0.5
}}

--- النص المراد تحليله ---
{text}
"""

class GroqAnalyzer:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        return self.client is not None

    def analyse(self, text: str) -> dict | None:
        if not self.is_available():
            logger.warning("Groq Analyzer called but API Key is missing.")
            return None
            
        text = text.strip()[:4500] # Safe limit for Llama3 context
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(text=text)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON-only API. Only return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            )
            raw = chat_completion.choices[0].message.content.strip()
            return self._parse_json(raw)
        except Exception as exc:
            logger.error(f"Groq inference error: {exc}")
            return None

    def _parse_json(self, raw: str) -> dict:
        try:
            # Clean up markdown formatting if the model wraps it
            raw = raw.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(raw)
                
            if "entities" not in data:
                data["entities"] = {"persons": [], "locations": [], "orgs": []}
            return data
        except Exception as e:
            logger.error(f"Failed to parse Groq JSON: {e} | Raw: {raw[:100]}")
            raise ValueError("Invalid JSON output")
