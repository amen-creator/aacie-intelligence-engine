"""
AACIE V5 - Page 1: 3D Intelligence Network
===========================================
"""
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.database import Database
from core.theme import inject_css, page_header

st.set_page_config(page_title="3D Intelligence | AACIE v5", page_icon="🕸️", layout="wide")
inject_css()
page_header("🕸️ 3D Intelligence Network", "Entity Relationship Matrix")

db = Database()
articles = db.get_recent_articles(limit=200)

# ── Build entity data ──────────────────────────────────────────────────────────
persons, locations, orgs, edges = set(), set(), set(), []
for art in articles:
    ana = art.get("analysis", {})
    ents = ana.get("entities", {}) if isinstance(ana, dict) else {}
    title = art.get("title", "")
    p_list = ents.get("persons", [])
    l_list = ents.get("locations", [])
    o_list = ents.get("orgs", [])
    persons.update(p_list)
    locations.update(l_list)
    orgs.update(o_list)
    for p in p_list[:2]:
        for o in o_list[:2]:
            edges.append((p, o))
        for l in l_list[:1]:
            edges.append((p, l))

# ── Summary metrics ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🧑 Persons Identified", len(persons))
with c2: st.metric("📍 Locations Mapped", len(locations))
with c3: st.metric("🏢 Organizations", len(orgs))
with c4: st.metric("🔗 Connections", len(edges))

st.markdown("---")

# ── PyVis Network ──────────────────────────────────────────────────────────────
try:
    from pyvis.network import Network
    import networkx as nx

    G = nx.Graph()
    for n in list(persons)[:30]:
        G.add_node(n, group=1, title=f"[PERSON] {n}", color="#ef4444")
    for n in list(locations)[:20]:
        G.add_node(n, group=2, title=f"[LOCATION] {n}", color="#3b82f6")
    for n in list(orgs)[:20]:
        G.add_node(n, group=3, title=f"[ORG] {n}", color="#10b981")
    for a, b in edges[:40]:
        if G.has_node(a) and G.has_node(b):
            G.add_edge(a, b)

    net = Network(height="580px", width="100%", bgcolor="#020617", font_color="#cbd5e1", directed=False)
    net.from_nx(G)
    net.set_options("""{
        "nodes": {"borderWidth": 2, "shadow": true},
        "edges": {"color": {"color": "#334155"}, "width": 1.5, "smooth": {"type": "continuous"}},
        "physics": {"forceAtlas2Based": {"gravitationalConstant": -40}, "solver": "forceAtlas2Based"},
        "interaction": {"hover": true, "tooltipDelay": 150}
    }""")

    html_file = ROOT / "data" / "entity_graph.html"
    html_file.parent.mkdir(exist_ok=True)
    net.save_graph(str(html_file))

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    st.markdown("<div style='border:1px solid rgba(59,130,246,0.2);border-radius:12px;overflow:hidden;'>", unsafe_allow_html=True)
    components.html(html_content, height=590, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)

except ImportError:
    st.warning("⚠️ Install pyvis with `pip install pyvis` for the 3D network view.")
    if articles:
        st.markdown("### 📋 Entity List")
        st.json({"Persons": list(persons)[:15], "Locations": list(locations)[:15], "Orgs": list(orgs)[:15]})

# ── Legend ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;gap:2rem;margin-top:1rem;font-size:0.85rem;font-family:'Share Tech Mono',monospace;">
  <span style="color:#ef4444">● PERSONS</span>
  <span style="color:#3b82f6">● LOCATIONS</span>
  <span style="color:#10b981">● ORGANIZATIONS</span>
</div>
""", unsafe_allow_html=True)
