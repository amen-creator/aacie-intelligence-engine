"""
AACIE V5 - Page 3: Communications Array (Sources)
===================================================
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.database import Database
from core.theme import inject_css, page_header

st.set_page_config(page_title="Comms Array | AACIE v5", page_icon="🌐", layout="wide")
inject_css()
page_header("🌐 Communications Array", "Intelligence Source Monitor & API Status")

db = Database()
articles = db.get_recent_articles(limit=500)

# ── API Health Grid ────────────────────────────────────────────────────────────
st.markdown("### ⚡ API Health Matrix")

apis = [
    {"name": "Jina Reader", "status": "ACTIVE", "color": "#10b981", "detail": "Full-Text Extraction", "icon": "🔵"},
    {"name": "ScraperAPI", "status": "ACTIVE", "color": "#10b981", "detail": "Anti-Block Proxy Layer", "icon": "🟢"},
    {"name": "Groq (Llama-3)", "status": "ACTIVE", "color": "#10b981", "detail": "800+ Tokens/sec Inference", "icon": "🟢"},
    {"name": "HuggingFace", "status": "STANDBY", "color": "#f59e0b", "detail": "Arabic Sentiment Fallback", "icon": "🟡"},
    {"name": "DuckDuckGo", "status": "ACTIVE", "color": "#10b981", "detail": "Unlimited News Search", "icon": "🟢"},
    {"name": "Gemini", "status": "DECOMMISSIONED", "color": "#ef4444", "detail": "Removed in V5", "icon": "🔴"},
]

cols = st.columns(3)
for i, api in enumerate(apis):
    with cols[i % 3]:
        st.markdown(f"""
        <div style="background:rgba(15,23,42,0.7);border:1px solid {api['color']}33;
                    border-left:3px solid {api['color']};border-radius:10px;
                    padding:1rem 1.2rem;margin-bottom:0.8rem;
                    font-family:'Rajdhani',sans-serif;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <b style="color:#e2e8f0;font-size:1rem;">{api['icon']} {api['name']}</b>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;
                         color:{api['color']};letter-spacing:1.5px;">{api['status']}</span>
          </div>
          <div style="color:#64748b;font-size:0.8rem;margin-top:0.3rem;">{api['detail']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Source Volume Chart ────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📡 Intel Volume by Source")
    if articles:
        src_counts = {}
        for a in articles:
            s_name = a.get("source_name", a.get("source", "Unknown"))
            src_counts[s_name] = src_counts.get(s_name, 0) + 1
        df = pd.DataFrame(list(src_counts.items()), columns=["Source", "Count"]).sort_values("Count", ascending=True)
        fig = px.pie(df, values="Count", names="Source", hole=0.55,
                     color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Rajdhani"),
            height=320, margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        fig.update_traces(textfont_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No articles in database yet.")

with c2:
    st.markdown("### 📋 Registered Data Feeds")
    feeds = [
        {"Source": "الجزيرة نت", "Method": "ScraperAPI + RSS", "Status": "✅"},
        {"Source": "CNN Arabic", "Method": "ScraperAPI + RSS", "Status": "✅"},
        {"Source": "Sky News Arabia", "Method": "ScraperAPI + RSS", "Status": "✅"},
        {"Source": "DuckDuckGo", "Method": "DDG Search API", "Status": "✅"},
        {"Source": "Web Articles", "Method": "Jina Reader", "Status": "✅"},
        {"Source": "المصادر العامة", "Method": "ScraperAPI Proxy", "Status": "✅"},
    ]
    df_feeds = pd.DataFrame(feeds)
    st.dataframe(df_feeds, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.metric("📦 Total Articles in DB", len(articles))
