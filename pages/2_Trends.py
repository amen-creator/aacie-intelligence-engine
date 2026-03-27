"""
AACIE V5 - Page 2: Trend Velocity Intelligence
===============================================
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.trend_tracker import TrendTracker
from core.theme import inject_css, page_header

st.set_page_config(page_title="Trend Velocity | AACIE v5", page_icon="📈", layout="wide")
inject_css()
page_header("📈 Trend Velocity Intelligence", "Live Narrative Shift Detection")

tracker = TrendTracker()
history = tracker._load_snapshots()

if not history:
    st.info("⚡ No trend data yet. Run the Agent once to start recording snapshots.")
    st.stop()

df = pd.DataFrame(history)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ── Summary metrics ────────────────────────────────────────────────────────────
latest = history[-1]
c1, c2, c3 = st.columns(3)
with c1: st.metric("📊 Snapshots Recorded", len(history))
with c2:
    avg_sent = df['avg_sentiment'].mean()
    st.metric("🧭 Avg Sentiment Index", f"{avg_sent:.3f}", f"{'↑ Positive' if avg_sent > 0 else '↓ Negative'}")
with c3:
    vol = df['article_count'].sum()
    st.metric("📰 Total Articles Tracked", int(vol))

st.markdown("---")

# ── Sentiment Timeline ─────────────────────────────────────────────────────────
st.markdown("### 📉 Sentiment Velocity Waveform")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['avg_sentiment'],
    mode='lines+markers', name='Sentiment',
    line=dict(color='#10b981', width=3),
    marker=dict(size=7, color='#10b981', line=dict(color='#020617', width=2)),
    fill='tozeroy',
    fillcolor='rgba(16, 185, 129, 0.07)'
))
fig.add_trace(go.Bar(
    x=df['timestamp'], y=df['article_count'],
    name='Article Volume', marker_color='rgba(59, 130, 246, 0.25)',
    yaxis='y2'
))
fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.15)")
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Rajdhani"),
    yaxis=dict(title='Sentiment Score', range=[-1.2, 1.2], gridcolor='rgba(59,130,246,0.07)'),
    yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
    hovermode="x unified", height=380,
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(59,130,246,0.2)', borderwidth=1),
    margin=dict(l=10, r=10, t=20, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# ── Top Keywords ───────────────────────────────────────────────────────────────
st.markdown("### 🔥 Top Surging Topics (Latest Snapshot)")
top_kws = latest.get("top_keywords", {})
if top_kws:
    df_kw = pd.DataFrame(list(top_kws.items()), columns=["Keyword", "Mentions"]).sort_values("Mentions", ascending=True)
    fig_bar = px.bar(
        df_kw.tail(15), x="Mentions", y="Keyword", orientation='h',
        color="Mentions", color_continuous_scale=[[0, "#1e293b"], [0.5, "#3b82f6"], [1, "#10b981"]]
    )
    fig_bar.update_traces(marker_line_width=0)
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Rajdhani"),
        height=400, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No keyword data in the latest snapshot yet.")

# ── Anomaly Alerts ─────────────────────────────────────────────────────────────
st.markdown("### 🚨 Sentiment Anomaly Alerts")
has_alerts = False
for i in range(1, len(history)):
    prev, curr = history[i-1], history[i]
    diff = curr['avg_sentiment'] - prev['avg_sentiment']
    if abs(diff) > 0.4:
        has_alerts = True
        color = "#ef4444" if abs(diff) > 0.6 else "#f59e0b"
        icon = "🔴" if abs(diff) > 0.6 else "🟡"
        ts = str(curr['timestamp'])[:16]
        st.markdown(f"""
        <div style="background:rgba({('239,68,68' if abs(diff)>0.6 else '245,158,11')},0.1);
                    border-left:3px solid {color};border-radius:8px;
                    padding:0.8rem 1rem;margin-bottom:0.5rem;font-family:'Rajdhani',sans-serif;">
          {icon} <b style="color:{color}">[{ts}]</b>
          &nbsp;|&nbsp; <span style="color:#cbd5e1">Sentiment Shift: <b>{diff:+.2f}</b></span>
        </div>""", unsafe_allow_html=True)

if not has_alerts:
    st.markdown("""
    <div style="background:rgba(16,185,129,0.08);border-left:3px solid #10b981;
                border-radius:8px;padding:0.8rem 1rem;font-family:'Share Tech Mono',monospace;
                font-size:0.85rem;color:#94a3b8;">
      ✅ // NO ANOMALIES DETECTED — NARRATIVE STREAM STABLE //
    </div>""", unsafe_allow_html=True)
