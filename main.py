"""
AACIE – Main Pipeline
======================
Orchestrates: Scrape → Analyse → Store → Report
Run:  python main.py
"""

import argparse
import json
from pathlib import Path

from core.scraper import ArabicScraper
from core.analyzer import ArabicAnalyzer
from core.database import Database
from core.reporter import ReportGenerator


def run_pipeline(pages_per_source: int = 3, demo_mode: bool = False) -> None:
    """
    Full end-to-end pipeline:
      1. Scrape Arabic news sources (or use demo data)
      2. Analyse sentiment and dialect
      3. Persist to Supabase (or in-memory)
      4. Generate a PDF/TXT report
    """
    print("\n" + "=" * 55)
    print("  AACIE - Arabic Autonomous Content Intelligence Engine")
    print("=" * 55)

    db = Database()
    scraper = ArabicScraper()
    analyzer = ArabicAnalyzer()
    reporter = ReportGenerator()

    # ── Step 1: Scrape ────────────────────────────────────────────────────────
    if demo_mode:
        print("[DEMO] Loading sample articles from data/demo_articles.json …")
        demo_path = Path(__file__).parent / "data" / "demo_articles.json"
        if demo_path.exists():
            with open(demo_path, encoding="utf-8") as f:
                articles = json.load(f)
        else:
            # Generate mock articles covering all three demo dialects
            articles = [
                scraper._mock_article("https://demo.com/article-1"),
                scraper._mock_article("https://demo.com/article-2"),
                scraper._mock_article("https://demo.com/article-3"),
            ]
    else:
        print(f"[→] Scraping up to {pages_per_source} pages per source …")
        articles = scraper.scrape_all_sources(pages_per_source=pages_per_source)

    print(f"[✓] Fetched {len(articles)} articles.\n")

    # ── Step 2: Analyse ───────────────────────────────────────────────────────
    print("[→] Running NLP analysis …")
    analysed = analyzer.analyse_articles(articles)
    print(f"[✓] Analysis complete.\n")

    # ── Step 3: Persist ───────────────────────────────────────────────────────
    print("[→] Saving to database …")
    for art in analysed:
        saved = db.upsert_article(art)
        article_id = saved.get("id") if saved else None
        if art.get("analysis"):
            db.save_analysis(article_id, art["analysis"])
    print("[✓] Data persisted.\n")

    # ── Step 4: Report ────────────────────────────────────────────────────────
    stats = db.get_analysis_stats()
    report_path = reporter.generate(analysed, stats)
    print(f"\n[OK] Pipeline complete! Report: {report_path}\n")

    # Summary to stdout
    print("-- Quick Stats ----------------------------------------------")
    print(f"   Total articles  : {stats['total_analysed']}")
    print(f"   Sentiment dist. : {stats['sentiment_distribution']}")
    print(f"   Dialect dist.   : {stats['dialect_distribution']}")
    print(f"   Avg score       : {stats['avg_sentiment_score']:.2f}")
    print("------------------------------------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AACIE Data Pipeline")
    parser.add_argument("--pages", type=int, default=3, help="Pages per source (default 3)")
    parser.add_argument("--demo", action="store_true", help="Use demo/mock data (no API calls)")
    args = parser.parse_args()

    run_pipeline(pages_per_source=args.pages, demo_mode=args.demo)
