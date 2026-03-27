"""
AACIE v4 - Executive Mission Control (Main Page)
=================================================
Legendary Cyberpunk UI combining glassmorphism, glowing accents, 
and a dynamic "Red Alert" mode for high-urgency intelligence.
Powered by Groq Llama-3 70B and Jina Reader API.
"""

import sys
from pathlib import Path
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from core.database import Database
from core.scheduler import AgentScheduler
from core.trend_tracker import TrendTracker
from core.config import Config

st.set_page_config(
    page_title="AACIE V4 | Mission Control",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dynamic Red Alert Detection ───────────────────────────────────────────────
@st.cache_resource
def init_services():
    return Database(), AgentScheduler(), TrendTracker()

db, scheduler, tracker = init_services()
articles = db.get_recent_articles(limit=50)

# Detect if the system should be in "Red Alert"
red_alert = any(art.get('analysis', {}).get('urgency_score', 0) > 0.8 for art in articles[:5])

theme_color = "#ef4444" if red_alert else "#3b82f6"
bg_gradient = "linear-gradient(135deg, #450a0a 0%, #000000 100%)" if red_alert else "linear-gradient(135deg, #020617 0%, #0f172a 100%)"
glow_color = "rgba(239, 68, 68, 0.5)" if red_alert else "rgba(59, 130, 246, 0.4)"

# ── Legendary V4 CSS ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Share+Tech+Mono&display=swap');
  
  .stApp {{ background: {bg_gradient}; background-attachment: fixed; color: #e2e8f0; }}
  h1, h2, h3, p, span, div {{ font-family: 'Cairo', sans-serif; }}
  .cyber-font {{ font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }}
  
  .stApp::before {{
      content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background-image: linear-gradient({glow_color} 1px, transparent 1px),
                        linear-gradient(90deg, {glow_color} 1px, transparent 1px);
      background-size: 40px 40px; opacity: 0.05; z-index: -1;
      transform: perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px);
      animation: gridMove 20s linear infinite;
  }}
  @keyframes gridMove {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 0 40px; }} }}
  
  .hero-v3 {{
    background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.05); border-top: 2px solid {theme_color};
    border-radius: 16px; padding: 3rem; text-align: center;
    box-shadow: 0 0 40px {glow_color}, inset 0 0 20px rgba(0,0,0,0.5);
    position: relative; overflow: hidden; margin-bottom: 2rem;
  }}
  .hero-v3 h1 {{
      font-size: 3.5rem; font-weight: 900; margin: 0;
      background: -webkit-linear-gradient(#fff, {theme_color});
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      text-shadow: 0 0 20px {glow_color};
  }}
  
  .alert-banner {{
      background: #7f1d1d; color: #fca5a5; padding: 0.2rem 1rem; border-radius: 4px;
      font-size: 0.8rem; font-weight: bold; letter-spacing: 2px;
      animation: pulseAlert 1.5s infinite; position: absolute; top: 1rem; left: 1rem;
  }}
  @keyframes pulseAlert {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
  
  /* Groq / API Badge */
  .api-badge {{
      background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 0.3rem 0.8rem; border-radius: 20px;
      font-size: 0.8rem; font-weight: bold; position: absolute; top: 1rem; right: 1rem;
      border: 1px solid #10b981; animation: glow 2s infinite; font-family: 'Share Tech Mono', monospace;
  }}
  @keyframes glow {{ 0% {{ box-shadow: 0 0 5px #10b981; }} 50% {{ box-shadow: 0 0 15px #10b981; }} 100% {{ box-shadow: 0 0 5px #10b981; }} }}

  div[data-testid="stMetric"] {{
    background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.1); border-left: 3px solid {theme_color};
    border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }}
  div[data-testid="stMetric"]:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px {glow_color}; }}
  
  .cyber-ticker-wrap {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.5); border-top: 1px solid {theme_color}; border-bottom: 1px solid {theme_color}; padding: 10px 0; margin: 1.5rem 0; box-shadow: 0 0 15px {glow_color}; }}
  .cyber-ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; animation: ticker 40s linear infinite; }}
  .cyber-ticker-item {{ display: inline-block; padding: 0 3rem; color: #fff; font-size: 1.15rem; text-shadow: 0 0 5px {theme_color}; direction: rtl; }}
  @keyframes ticker {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}
  
  section[data-testid="stSidebar"] {{ background-color: rgba(2, 6, 23, 0.85) !important; backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.05); }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Globe_icon.svg/500px-Globe_icon.svg.png", width=60)
    st.markdown(f"<h2 style='text-align:center;color:{theme_color};text-shadow:0 0 10px {theme_color};'>AACIE V4</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#94a3b8;font-size:0.8rem;margin-bottom:2rem;'>MISSION CONTROL (FREE TIER)</div>", unsafe_allow_html=True)
    
    st.page_link("app.py", label="🌍 Mission Control", icon="🛰️")
    st.page_link("pages/1_Analysis.py", label="🧠 3D Intelligence", icon="🌐")
    st.page_link("pages/2_Trends.py", label="📈 Trend Velocity", icon="⚡")
    st.page_link("pages/3_Sources.py", label="📡 Comms Array", icon="📡")
    st.page_link("pages/4_Reports.py", label="📑 Intel Drops", icon="🗃️")
    st.page_link("pages/5_Agent.py", label="🤖 Agent Core", icon="🔋")
    st.page_link("pages/6_Assistant.py", label="💬 Chat AI", icon="💬")
    
    st.markdown("---")
    st.caption("CORE STATUS:")
    agent_state = "Stopped"
    if Config.AGENT_LOG_PATH.exists():
        with open(Config.AGENT_LOG_PATH, "r") as f:
            log_data = json.load(f)
            agent_state = log_data.get("status", "stopped")
    
    color = "🟢" if agent_state == "running" else "🔴" if agent_state == "error" else "🟡"
    st.markdown(f"**{color} {agent_state.upper()}**")


# ── Hero Section ──────────────────────────────────────────────────────────────
alert_html = '<div class="alert-banner">CRITICAL INTEL DETECTED</div>' if red_alert else '<div class="alert-banner" style="background:#064e3b;color:#34d399;animation:none;">SYSTEM NOMINAL</div>'
api_badge = '<div class="api-badge">⚡ POWERED BY GROQ & JINA</div>'

st.markdown(f"""
<div class="hero-v3">
  {alert_html}
  {api_badge}
  <h1>AACIE MISSION CONTROL</h1>
  <p class="arabic" style="font-size:1.3rem; margin-top:1rem; color:#cbd5e1;">محرك الذكاء العربي المستقل V4</p>
  <p class="cyber-font" style="color:{theme_color}; margin-top:15px;">OPTICAL DATALINK: ACTIVE // INFERENCE: LLAMA-3 70B</p>
</div>
""", unsafe_allow_html=True)

# ── Live Ticker ───────────────────────────────────────────────────────────────
if articles:
    ticker_items = []
    for art in articles[:12]:
        title = art.get('title', 'N/A')
        src = art.get('source_name', 'Unknown')
        urgency = art.get('analysis', {}).get('urgency_score', 0)
        u_tag = "<span style='color:#ef4444;font-weight:900;'>[URGENT]</span>" if urgency > 0.8 else ""
        ticker_items.append(f"<div class='cyber-ticker-item'> {u_tag} {title} ــ <span class='cyber-font' style='font-size:0.9rem;opacity:0.7;'>{src}</span></div>")
    
    ticker_html = f"""
    <div class="cyber-ticker-wrap"><div class="cyber-ticker">{"".join(ticker_items)}</div></div>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)

# ── Metrics Dashboard ─────────────────────────────────────────────────────────
stats = db.get_analysis_stats()
total = stats.get('total_analysed', 0)
avg_score = stats.get('avg_sentiment_score', 0.0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("INTEL PROCESSED", f"{total:,}", "Records Extracted")
col2.metric("GLOBAL SENTIMENT", f"{avg_score:+.2f}", "Index")
col3.metric("INFERENCE PLATFORM", "Llama-3 70B", "Groq Accelerator")
col4.metric("SYSTEM THREAT LEVEL", "ELEVATED" if red_alert else "LOW", "Urgency")

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Top Keywords Heatmap ──────────────────────────────────────────────────────
st.markdown("<h3 class='cyber-font' style='color:#e2e8f0;border-bottom:1px solid #334155;padding-bottom:10px;'>// HOT ZONES (TOP TRENDS)</h3>", unsafe_allow_html=True)
top_kws = stats.get("top_keywords", {})
if top_kws:
    df_kw = pd.DataFrame(list(top_kws.items()), columns=["Keyword", "Frequency"])
    fig = px.bar(df_kw.head(10), x="Frequency", y="Keyword", orientation='h',
                 color="Frequency", color_continuous_scale="Inferno" if red_alert else "Teal",
                 text="Frequency")
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        font_color="#cbd5e1", font_family="Cairo",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Awaiting intel drops... Start the Agent.")
