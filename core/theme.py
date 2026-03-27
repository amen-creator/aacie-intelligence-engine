"""
AACIE V5 - Shared Cyberpunk Theme CSS
======================================
Import this in every Streamlit page for a consistent premium look.
"""

CYBER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Cairo:wght@400;700&family=Rajdhani:wght@400;600;700&display=swap');

/* ── ROOT OVERRIDES ─────────────────────────────────── */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0a0f1e 0%, #020617 60%, #000000 100%) !important;
    color: #cbd5e1;
    font-family: 'Rajdhani', sans-serif;
}
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none; z-index: 0;
}

/* ── SIDEBAR ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.2) !important;
}
[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }

/* ── HEADINGS ────────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 2px;
    text-transform: uppercase;
}
h1 {
    background: linear-gradient(135deg, #10b981, #3b82f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2.2rem !important;
    margin-bottom: 0.5rem;
}
h2 { color: #38bdf8 !important; font-size: 1.4rem !important; }
h3 { color: #10b981 !important; font-size: 1.1rem !important; }

/* ── GLASS CARD ──────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(59, 130, 246, 0.25) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(16, 185, 129, 0.6) !important;
    box-shadow: 0 0 16px rgba(16, 185, 129, 0.15);
}
div[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.75rem !important; letter-spacing: 1.5px; text-transform: uppercase; }
div[data-testid="stMetricValue"] { color: #f8fafc !important; font-size: 2rem !important; font-family: 'Share Tech Mono', monospace !important; }
div[data-testid="stMetricDelta"] { font-size: 0.8rem !important; color: #10b981 !important; }

/* ── BUTTONS ─────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(16,185,129,0.1)) !important;
    border: 1px solid rgba(59, 130, 246, 0.4) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    letter-spacing: 1px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    border-color: #10b981 !important;
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.3) !important;
    background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(59,130,246,0.1)) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(16,185,129,0.35), rgba(59,130,246,0.2)) !important;
    border-color: #10b981 !important;
    color: #fff !important;
}

/* ── DATAFRAME ───────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── DIVIDER ─────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(59, 130, 246, 0.2) !important;
    margin: 1.5rem 0 !important;
}

/* ── INFO / WARNING / ERROR ──────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    backdrop-filter: blur(8px);
}

/* ── SPINNER ─────────────────────────────────────────── */
.stSpinner { color: #10b981 !important; }

/* ── INPUTS ──────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select, .stChatInputContainer {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.2) !important;
}

/* ── PAGE TITLE BAR ──────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(59,130,246,0.05));
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #10b981, transparent);
}
.page-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #64748b;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ── GLASS SECTION BOX ───────────────────────────────── */
.glass-box {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}
.neon-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #10b981;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.arabic { font-family: 'Cairo', sans-serif; direction: rtl; line-height: 1.8; }
</style>
"""

def inject_css():
    """Call this at the top of any Streamlit page to apply the Cyberpunk theme."""
    import streamlit as st
    st.markdown(CYBER_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    """Renders a stylish page header with optional subtitle."""
    import streamlit as st
    sub_html = f"<div class='page-subtitle'>// {subtitle} //</div>" if subtitle else ""
    st.markdown(f"<div class='page-header'><h1>{title}</h1>{sub_html}</div>", unsafe_allow_html=True)

def glass_section(label: str = ""):
    """Returns an HTML glass section wrapper as raw HTML."""
    lbl = f"<div class='neon-label'>{label}</div>" if label else ""
    return f"<div class='glass-box'>{lbl}"

def close_glass():
    return "</div>"
