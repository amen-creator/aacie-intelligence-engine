"""
AACIE V5 - Autonomous Agent Coordinator
=======================================
Manages the background execution cycle (Scrape -> Extract -> Analyze -> Save)
using the V5 Enterprise Pipeline.
"""

import time
import json
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from core.config import Config, get_logger
from core.database import Database
from core.ingestion import IngestionPipeline
from core.intelligence import ArabicAnalyzer

logger = get_logger("AgentCore")

class AgentScheduler:
    def __init__(self):
        self.db = Database()
        self.ingestion = IngestionPipeline()
        self.analyzer = ArabicAnalyzer()
        self.scheduler = BackgroundScheduler()
        
        # Track agent state
        self.state = {"status": "stopped", "last_run": None, "records_processed": 0}
        self._save_state()

        self.sources = [
            "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9",
            "https://arabic.cnn.com/api/v1/rss/middle_east/rss.xml"
        ]
        self.queries = ["الذكاء الاصطناعي", "اقتصاد الشرق الأوسط"]

    def _save_state(self):
        with open(Config.AGENT_LOG_PATH, "w") as f:
            json.dump(self.state, f)

    def _agent_cycle(self):
        """The main autonomous loop."""
        logger.info("=== STARTING AUTONOMOUS CYCLE V5 ===")
        self.state["status"] = "running"
        self._save_state()

        try:
            # 1. Ingestion (ScraperAPI + Jina)
            logger.info("Phase 1: Ingestion & Extraction...")
            articles = self.ingestion.gather_and_extract(self.sources, self.queries, limit=3)
            
            # 2. Intelligence (Groq Llama-3)
            logger.info("Phase 2: NLP Analysis...")
            analyzed_articles = self.analyzer.analyse_articles(articles)
            
            # 3. Storage
            logger.info("Phase 3: Persistence...")
            for art in analyzed_articles:
                saved = self.db.upsert_article(art)
                if saved and "id" in saved:
                    self.db.save_analysis(saved["id"], art["analysis"])
                self.state["records_processed"] += 1
                
            self.state["last_run"] = datetime.utcnow().isoformat()
            self.state["status"] = "idle"
            logger.info("=== CYCLE COMPLETE ===")
        except Exception as e:
            logger.error(f"Agent Cycle Failed: {e}")
            self.state["status"] = "error"
        finally:
            self._save_state()

    def start(self, interval_minutes: int = 120):
        if not self.scheduler.running:
            self.scheduler.add_job(self._agent_cycle, 'interval', minutes=interval_minutes, id="v5_cycle")
            self.scheduler.start()
            logger.info(f"Agent started. Cycle every {interval_minutes} minutes.")
            self.state["status"] = "idle"
            self._save_state()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Agent stopped.")
            self.state["status"] = "stopped"
            self._save_state()

    def trigger_now(self):
        """Manually trigger the cycle in a background thread."""
        logger.info("Manual override triggered.")
        thread = threading.Thread(target=self._agent_cycle)
        thread.start()
