"""
AACIE V5 - Page 5: Agent Core Terminal
========================================
"""
import sys
from pathlib import Path
import streamlit as st
import json
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.scheduler import AgentScheduler
from core.config import Config
from core.theme import inject_css, page_header

st.set_page_config(page_title="Agent Core | AACIE v5", page_icon="🤖", layout="wide")
inject_css()
page_header("🤖 Agent Core Terminal", "Autonomous Intelligence Coordinator Control")

st.markdown("""
<style>
.log-terminal {
    background: #020617;
    font-family: 'Share Tech Mono', monospace;
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 10px;
    padding: 1.5rem;
    height: 460px;
    overflow-y: auto;
    font-size: 0.82rem;
    color: #a1a1aa;
    line-height: 1.8;
}
.log-info  { color: #3b82f6; }
.log-warn  { color: #f59e0b; }
.log-error { color: #ef4444; font-weight: bold; }
.log-success { color: #10b981; }
.t-prompt  { color: #10b981; font-weight: bold; }
.status-pill {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ── State ──────────────────────────────────────────────────────────────────────
agent_state = "stopped"
logs = []
last_run = None
records = 0

if Config.AGENT_LOG_PATH.exists():
    with open(Config.AGENT_LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        agent_state = data.get("status", "stopped")
        logs = data.get("logs", [])
        last_run = data.get("last_run")
        records = data.get("records_processed", 0)

# ── Layout ─────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.markdown("### 🎛️ Agent Controls")

    status_colors = {"running": "#10b981", "idle": "#3b82f6", "error": "#ef4444", "stopped": "#64748b"}
    color = status_colors.get(agent_state, "#64748b")
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#64748b;letter-spacing:2px;margin-bottom:0.4rem;">SYSTEM STATUS</div>
      <span class="status-pill" style="background:rgba({('16,185,129' if agent_state=='idle' else '59,130,246' if agent_state=='running' else '239,68,68' if agent_state=='error' else '100,116,139')},0.15);
             color:{color};border:1px solid {color}55;">{agent_state.upper()}</span>
    </div>""", unsafe_allow_html=True)

    lr_str = str(last_run)[:19] if last_run else "Never"
    st.metric("🕐 Last Cycle", lr_str)
    st.metric("📦 Records Processed", records)
    st.markdown("---")

    sched = AgentScheduler()
    if st.button("▶️ Start Autonomous Mode", type="primary", use_container_width=True):
        sched.start()
        st.rerun()
    if st.button("⏸️ Pause Agent", use_container_width=True):
        sched.stop()
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Trigger Manual Override", use_container_width=True):
        with st.spinner("// AGENT HUNTING NARRATIVES... //"):
            sched.trigger_now()
        st.success("✅ Cycle triggered! Refresh in a moment.")

    if st.button("🗑️ Clear Logs", use_container_width=True):
        if Config.AGENT_LOG_PATH.exists():
            with open(Config.AGENT_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump({"status": agent_state, "last_run": last_run, "logs": [], "records_processed": records}, f)
        st.rerun()

with c2:
    st.markdown("### 📺 Live Terminal Stream")
    log_html = "<div class='log-terminal'>"
    if not logs:
        log_html += "<div><span class='t-prompt'>AACIE&gt;</span> System standing by... Waiting for activation.</div>"
        log_html += "<div><span class='t-prompt'>AACIE&gt;</span> Press [Start Autonomous Mode] to begin intelligence operations.</div>"
    else:
        for entry in logs[-80:]:
            ts = str(entry.get('timestamp', ''))[ 11:19]
            lvl = entry.get('level', 'info').lower()
            msg = entry.get('message', '')
            log_html += f"<div>[{ts}] <span class='log-{lvl}'>[{lvl.upper()}]</span> {msg}</div>"
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)
