"""
AACIE V5 - Central Configuration & Environment Manager
======================================================
Strictly loads and validates all API keys required for the 
Ultimate Enterprise Architecture (Jina, ScraperAPI, Groq, HF).
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Force overwrite to fetch latest keys in interactive environments
load_dotenv(override=True)

class Config:
    # ── API Keys ───────────────────────────────────────────────────────────
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    JINA_API_KEY = os.getenv("JINA_API_KEY", "")
    SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # ── Storage ────────────────────────────────────────────────────────────
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    LOCAL_DB_PATH = DATA_DIR / "local_db.json"
    AGENT_LOG_PATH = LOG_DIR / "agent_status.json"
    
    # ── Application Settings ───────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    MAX_SCRAPE_RETRIES = 3
    SCRAPE_TIMEOUT = 30
    
    @classmethod
    def validate(cls):
        """Raises errors or logs warnings if critical APIs are missing."""
        missing = []
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY.startswith("your_"): missing.append("GROQ_API_KEY")
        if not cls.JINA_API_KEY or cls.JINA_API_KEY.startswith("your_"): missing.append("JINA_API_KEY")
        if not cls.SCRAPER_API_KEY or cls.SCRAPER_API_KEY.startswith("your_"): missing.append("SCRAPER_API_KEY")
        
        if missing:
            logging.warning(f"[CONFIG] Missing API Keys for V5 Architecture: {', '.join(missing)}")

# ── Dynamic Logger Setup ──────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(Config.LOG_LEVEL)
        # Console Handler
        sh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | [%(name)s] %(message)s')
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger

Config.validate()
