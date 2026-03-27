"""
AACIE - Report Generator
=========================
Generates two complementary reports from analysis results:
  1. A structured PDF (English/Latin stats) using fpdf2
  2. A full UTF-8 HTML report with complete Arabic content
Falls back to plain TXT when fpdf2 is not installed.
"""

import os
from datetime import datetime
from pathlib import Path


# Graceful import
try:
    from fpdf import FPDF
    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False


REPORT_DIR = Path(__file__).parent.parent / "reports"


class ReportGenerator:
    """
    Converts analysis results into two report files:
      - A PDF with Latin-only stats (safe for fpdf2/Helvetica)
      - A UTF-8 HTML file with full Arabic article details
    Falls back to plain TXT when fpdf2 is not installed.
    """

    def __init__(self):
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def generate(self, articles: list, stats: dict, title: str = "AACIE Report") -> Path:
        """
        Generate reports. Returns the path to the primary report file.
        Always generates an HTML companion with Arabic content.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = self._html_report(articles, stats, timestamp)
        if _FPDF_AVAILABLE:
            return self._pdf_report(articles, stats, timestamp, html_path)
        else:
            return self._txt_report(articles, stats, timestamp)

    # ---- HTML (primary Arabic report) ----------------------------------------

    def _html_report(self, articles: list, stats: dict, ts: str) -> Path:
        """Full Arabic HTML report -- all text encoded as UTF-8."""
        dist = stats.get("sentiment_distribution", {})
        avg  = stats.get("avg_sentiment_score", 0.0)

        article_rows = ""
        for i, art in enumerate(articles[:30], 1):
            a = art.get("analysis", {})
            s = a.get("sentiment", "")
            color = "#16a34a" if s in ("ايجابي", "ايجابى", "\u0627\u064a\u062c\u0627\u0628\u064a") else \
                    "#dc2626" if s == "\u0633\u0644\u0628\u064a" else "#6b7280"
            kws = " ".join(
                f'<span style="background:#1e40af22;border-radius:4px;padding:1px 6px;'
                f'font-size:0.78rem;color:#3b82f6">{k}</span>'
                for k in a.get("keywords", [])
            )
            article_rows += f"""
            <div style="background:#1e293b;border-radius:10px;padding:1rem;margin-bottom:0.8rem;
                        border-left:4px solid {color};">
              <div style="font-size:0.95rem;font-weight:600;color:#f1f5f9;
                          direction:rtl;text-align:right;font-family:Cairo,sans-serif">
                {i}. {art.get('title', '---')}
              </div>
              <div style="font-size:0.78rem;color:#94a3b8;margin:4px 0">
                Source: {art.get('source_name', '-')} &nbsp;|&nbsp;
                Dialect: {a.get('dialect', '-')} &nbsp;|&nbsp;
                Sentiment: <span style="color:{color}">{s} ({a.get('sentiment_score', 0):+.2f})</span>
              </div>
              <div style="margin:4px 0">{kws}</div>
              <p style="font-size:0.85rem;color:#cbd5e1;direction:rtl;text-align:right;
                         font-family:Cairo,sans-serif;margin-top:6px">
                {a.get('summary', '')[:300]}
              </p>
            </div>"""

        pos = dist.get("\u0625\u064a\u062c\u0627\u0628\u064a", dist.get("\u0627\u064a\u062c\u0627\u0628\u064a", 0))
        neg = dist.get("\u0633\u0644\u0628\u064a", 0)

        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AACIE Report - {ts}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body{{margin:0;padding:2rem;background:#0f172a;color:#e2e8f0;font-family:Inter,sans-serif}}
    .hero{{background:linear-gradient(135deg,#1e3a5f,#0f172a);border-radius:12px;padding:2rem;text-align:center;margin-bottom:2rem}}
    .hero h1{{font-size:2rem;margin:0;color:#fff}}
    .hero p{{color:#94a3b8;margin:0.5rem 0 0}}
    .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-bottom:2rem}}
    .stat{{background:#1e293b;border-radius:10px;padding:1rem;text-align:center}}
    .stat .val{{font-size:1.8rem;font-weight:700;color:#60a5fa}}
    .stat .lbl{{font-size:0.8rem;color:#94a3b8;margin-top:4px;font-family:Cairo,sans-serif}}
    h2{{color:#f1f5f9;border-bottom:1px solid #1e293b;padding-bottom:0.5rem}}
  </style>
</head>
<body>
  <div class="hero">
    <h1>AACIE Intelligence Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | Articles: {len(articles)}</p>
  </div>
  <div class="stats">
    <div class="stat"><div class="val">{len(articles)}</div><div class="lbl">\u0645\u0642\u0627\u0644\u0627\u062a</div></div>
    <div class="stat"><div class="val" style="color:#22c55e">{pos}</div><div class="lbl">\u0625\u064a\u062c\u0627\u0628\u064a</div></div>
    <div class="stat"><div class="val" style="color:#ef4444">{neg}</div><div class="lbl">\u0633\u0644\u0628\u064a</div></div>
    <div class="stat"><div class="val">{avg:+.2f}</div><div class="lbl">\u0645\u062a\u0648\u0633\u0637 \u0627\u0644\u0645\u0634\u0627\u0639\u0631</div></div>
  </div>
  <h2>Article Summaries</h2>
  {article_rows}
  <p style="text-align:center;color:#475569;font-size:0.78rem;margin-top:2rem">
    AACIE v5.0 -- Built with Python, Streamlit, Groq (Llama-3), Jina AI
  </p>
</body>
</html>"""

        out_path = REPORT_DIR / f"aacie_report_{ts}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"[OK] HTML report saved: {out_path}")
        return out_path

    # ---- PDF (Latin stats only) -----------------------------------------------

    def _pdf_report(self, articles: list, stats: dict, ts: str, html_path: Path) -> Path:
        """Build a PDF with Latin-only content (no Arabic glyphs)."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 22)
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 16, "AACIE Intelligence Report", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Articles: {stats.get('total_analysed', len(articles))}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

        pdf.set_fill_color(240, 245, 255)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Aggregate Statistics", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)

        dist = stats.get("sentiment_distribution", {})
        pos = dist.get("\u0625\u064a\u062c\u0627\u0628\u064a", dist.get("\u0627\u064a\u062c\u0627\u0628\u064a", 0))
        neg = dist.get("\u0633\u0644\u0628\u064a", 0)
        neu = dist.get("\u0645\u062d\u0627\u064a\u062f", 0)
        pdf.cell(0, 7, f"  Positive: {pos}  |  Negative: {neg}  |  Neutral: {neu}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"  Avg Sentiment Score: {stats.get('avg_sentiment_score', 0.0):.2f}", new_x="LMARGIN", new_y="NEXT")

        dial = stats.get("dialect_distribution", {})
        if dial:
            dial_summary = " | ".join([f"{v}x" for v in list(dial.values())[:4]])
            pdf.cell(0, 7, f"  Dialect counts: {dial_summary}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(240, 245, 255)
        pdf.cell(0, 10, "Article Index", fill=True, new_x="LMARGIN", new_y="NEXT")

        for i, art in enumerate(articles[:20], 1):
            a = art.get("analysis", {})
            src   = art.get("source_name", "-")
            score = a.get("sentiment_score", 0.0)
            dial_str = a.get("dialect", "-")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(15, 23, 42)
            # Use only ASCII-safe characters for the source name
            src_safe = src.encode("ascii", "replace").decode("ascii")
            pdf.cell(0, 6, f"  {i:2d}. [{src_safe}]  Score: {score:+.2f}", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 5, f"Full Arabic content: see {html_path.name}")

        out_path = REPORT_DIR / f"aacie_report_{ts}.pdf"
        pdf.output(str(out_path))
        print(f"[OK] PDF report saved: {out_path}")
        return out_path

    # ---- TXT fallback ---------------------------------------------------------

    def _txt_report(self, articles: list, stats: dict, ts: str) -> Path:
        lines = [
            "=" * 60,
            "  AACIE Intelligence Report",
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"  Total Analysed: {stats.get('total_analysed', len(articles))}",
            "=" * 60, "",
            "AGGREGATE STATS", "-" * 40,
            f"Sentiment: {stats.get('sentiment_distribution', {})}",
            f"Dialects:  {stats.get('dialect_distribution', {})}",
            f"Avg Score: {stats.get('avg_sentiment_score', 0.0):.2f}",
            "", "ARTICLES", "-" * 40,
        ]
        for i, art in enumerate(articles[:20], 1):
            a = art.get("analysis", {})
            lines += [
                f"\n{i}. {art.get('title', 'N/A')}",
                f"   Source:    {art.get('source_name', '-')}",
                f"   Dialect:   {a.get('dialect', '-')}",
                f"   Sentiment: {a.get('sentiment', '-')} ({a.get('sentiment_score', 0):.2f})",
                f"   Keywords:  {', '.join(a.get('keywords', []))}",
                f"   Summary:   {a.get('summary', '')[:200]}",
            ]

        out_path = REPORT_DIR / f"aacie_report_{ts}.txt"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] TXT report saved: {out_path}")
        return out_path
