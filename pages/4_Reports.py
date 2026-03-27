"""
AACIE V5 - Page 4: Intel Drop Reports
=======================================
"""
import sys
from pathlib import Path
import streamlit as st
import json

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.database import Database
from core.reporter import ReportGenerator
from core.theme import inject_css, page_header

st.set_page_config(page_title="Intel Drops | AACIE v5", page_icon="📋", layout="wide")
inject_css()
page_header("📋 Intel Drop Reports", "Mission Briefings & Classified Extractions")

db = Database()
articles = db.get_recent_articles(limit=100)

if not articles:
    st.markdown("""
    <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                border-radius:12px;padding:2rem;text-align:center;font-family:'Share Tech Mono',monospace;
                color:#64748b;letter-spacing:1px;">
      // INTELLIGENCE DATABASE EMPTY — ACTIVATE AGENT FIRST //
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Stats ──────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Database Intelligence Summary")
c1, c2, c3, c4 = st.columns(4)
analysed = [a for a in articles if a.get("analysis")]
avg_urg = sum(a.get("analysis", {}).get("urgency_score", 0) for a in analysed) / max(len(analysed), 1)
sarcastic = sum(1 for a in analysed if a.get("analysis", {}).get("sarcasm_probability", 0) > 0.6)

with c1: st.metric("📰 Total Intel Records", len(articles))
with c2: st.metric("🔬 Analysed by Groq", len(analysed))
with c3: st.metric("🎯 Avg Urgency Score", f"{avg_urg:.2f}")
with c4: st.metric("🎭 Sarcasm Detected", sarcastic)
st.markdown("---")

# ── Report Generator ───────────────────────────────────────────────────────────
st.markdown("### 🖨️ Generate Mission Report")
col_sel, col_btn = st.columns([3, 1])
with col_sel:
    n = st.slider("Articles to include in report", 5, min(50, len(articles)), value=min(20, len(articles)))
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("⚡ Generate Intel Drop", type="primary", use_container_width=True)

if generate:
    with st.spinner("// COMPILING MISSION BRIEFING... //"):
        rg = ReportGenerator()
        stats = db.get_analysis_stats()
        report_path = rg.generate(articles[:n], stats)
        st.success(f"✅ Report generated: `{report_path}`")
        suffix = Path(report_path).suffix.lower()
        if suffix == ".pdf":
            with open(report_path, "rb") as f:
                st.download_button("📥 Download Intel Drop (PDF)", f.read(),
                                   file_name="aacie_intel_drop.pdf", mime="application/pdf")
        else:
            with open(report_path, "r", encoding="utf-8") as f:
                st.download_button("📥 Download Intel Drop (HTML)", f.read(),
                                   file_name="aacie_intel_drop.html", mime="text/html")

st.markdown("---")

# ── Article Feed ───────────────────────────────────────────────────────────────
st.markdown("### 🗃️ Recent Intelligence Feed")
filter_sentiment = st.selectbox("Filter by Sentiment", ["All", "إيجابي", "سلبي", "محايد"])

for art in articles[:30]:
    ana = art.get("analysis", {}) or {}
    sentiment = ana.get("sentiment", "محايد")
    if filter_sentiment != "All" and sentiment != filter_sentiment:
        continue

    urgency = ana.get("urgency_score", 0)
    sarcasm = ana.get("sarcasm_probability", 0)
    summary = ana.get("summary", art.get("title", ""))[:220]
    color = "#10b981" if sentiment == "إيجابي" else "#ef4444" if sentiment == "سلبي" else "#94a3b8"
    urg_color = "#ef4444" if urgency > 0.7 else "#f59e0b" if urgency > 0.4 else "#10b981"

    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.6);border:1px solid rgba(59,130,246,0.12);
                border-left:3px solid {color};border-radius:10px;
                padding:1rem 1.2rem;margin-bottom:0.6rem;font-family:'Rajdhani',sans-serif;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
        <span style="color:#e2e8f0;font-size:0.95rem;font-weight:600;max-width:75%;">{art.get('title','—')}</span>
        <div style="display:flex;gap:0.5rem;flex-shrink:0;">
          <span style="background:rgba{('(16,185,129' if sentiment=='إيجابي' else '(239,68,68' if sentiment=='سلبي' else '(148,163,184')},0.15);
                 color:{color};border-radius:5px;padding:2px 8px;font-size:0.72rem;
                 letter-spacing:1px;font-family:'Share Tech Mono',monospace;">{sentiment}</span>
          <span style="background:rgba(239,68,68,0.12);color:{urg_color};border-radius:5px;
                 padding:2px 8px;font-size:0.72rem;letter-spacing:1px;
                 font-family:'Share Tech Mono',monospace;">URG {urgency:.1f}</span>
        </div>
      </div>
      <div style="color:#64748b;font-size:0.82rem;margin-top:0.5rem;direction:rtl;font-family:'Cairo',sans-serif;">{summary}</div>
    </div>""", unsafe_allow_html=True)
