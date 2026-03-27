"""
AACIE v4 – Advanced NLP & Intelligence Engine
===============================================
Employs Groq (Llama-3 70B) for blazing fast inference 
and Gemini 1.5 Flash as a fallback.
"""

import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Groq Primary
try:
    from groq import Groq
    _GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    if _GROQ_KEY and not _GROQ_KEY.startswith("your_"):
        _GROQ_CLIENT = Groq(api_key=_GROQ_KEY)
        _GROQ_AVAILABLE = True
    else:
        _GROQ_AVAILABLE = False
except ImportError:
    _GROQ_AVAILABLE = False
    _GROQ_CLIENT = None

# ── JSON Extraction Prompt ────────────────────────────────────────────────────

ANALYSIS_PROMPT_TEMPLATE = """
أنت محلّل استخباراتي متقدم متخصص في معالجة اللغة الطبيعية العربية للأنظمة الذاتية (AI Agents).
قم بتحليل النص التالي بعمق واستخرج التفاصيل الدقيقة كـ JSON صالح ONLY.

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


class ArabicAnalyzer:
    def __init__(self):
        pass

    def analyse(self, text: str) -> dict:
        text = text.strip()
        if not text:
            return self._empty_result()
            
        if _GROQ_AVAILABLE:
            res = self._groq_analyse(text)
            if res: return res
            
        # Final fallback: rule-based (HuggingFace is used via core.intelligence separately)
        return self._rule_based_analyse(text)

    def analyse_articles(self, articles: list[dict]) -> list[dict]:
        results = []
        for art in articles:
            content = art.get("markdown", art.get("title", ""))
            content_trimmed = content[:4500] # Safe limit for Llama3 context
            analysis = self.analyse(content_trimmed)
            results.append({
                **art,
                "analysis": analysis,
                "analysed_at": datetime.utcnow().isoformat(),
            })
        return results

    def _groq_analyse(self, text: str) -> dict | None:
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(text=text)
        try:
            chat_completion = _GROQ_CLIENT.chat.completions.create(
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
            print(f"[!] Groq error: {exc}")
            return None

    def _parse_json(self, raw: str) -> dict:
        try:
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(raw)
                
            if "entities" not in data:
                data["entities"] = {"persons": [], "locations": [], "orgs": []}
            return data
        except Exception:
            raise ValueError(f"Failed to parse JSON: {raw[:200]}")

    @staticmethod
    def _rule_based_analyse(text: str) -> dict:
        text_lower = text.lower()
        pos_words = {"جيد", "ممتاز", "رائع", "ايجابي", "ارتفاع", "أرباح", "نجاح"}
        neg_words = {"سيء", "تراجع", "خسائر", "أزمة", "حرب", "انهيار"}
        
        pos_count = sum(1 for w in pos_words if w in text_lower)
        neg_count = sum(1 for w in neg_words if w in text_lower)
        if pos_count > neg_count:
            sentiment, score = "إيجابي", 0.6
        elif neg_count > pos_count:
            sentiment, score = "سلبي", -0.6
        else:
            sentiment, score = "محايد", 0.0

        return {
            "dialect": "فصحى", 
            "dialect_confidence": 0.5,
            "sentiment": sentiment,
            "sentiment_score": score,
            "sarcasm_probability": 0.0,
            "entities": {"persons": [], "locations": [], "orgs": []},
            "topics": ["عام"],
            "keywords": re.findall(r"[\u0600-\u06FF]{5,}", text)[:5],
            "summary": text[:200] + "...",
            "urgency_score": 0.3
        }

    @staticmethod
    def _empty_result() -> dict:
        return {
            "dialect": "غير محدد", "dialect_confidence": 0.0,
            "sentiment": "محايد", "sentiment_score": 0.0,
            "sarcasm_probability": 0.0, "entities": {},
            "topics": [], "keywords": [], "summary": "", "urgency_score": 0.0
        }

