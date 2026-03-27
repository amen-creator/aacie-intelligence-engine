"""
AACIE V5 - Page 6: AI Core Assistant
======================================
Live chat interface powered by Groq Llama-3 70B.
"""
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.database import Database
from core.config import Config
from core.theme import inject_css

st.set_page_config(page_title="AI Core | AACIE v5", page_icon="💬", layout="wide")
inject_css()

st.markdown("""
<style>
.stChatMessage { 
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(59,130,246,0.1) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px);
}
[data-testid="stChatMessageContent"] p { line-height: 1.8; }
.stChatInputContainer {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(16,185,129,0.08),rgba(59,130,246,0.05));
            border:1px solid rgba(16,185,129,0.2);border-radius:12px;
            padding:1.5rem 2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#10b981,transparent);"></div>
  <h1 style="font-family:'Rajdhani',sans-serif;font-size:2rem;
             background:linear-gradient(135deg,#10b981,#3b82f6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             letter-spacing:3px;margin:0;">💬 AACIE CORE ASSISTANT</h1>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
              color:#64748b;letter-spacing:2px;margin-top:0.25rem;">
    // DIRECT UPLINK TO LLAMA-3 70B INTELLIGENCE MATRIX // GROQ ACCELERATOR //
  </div>
</div>
""", unsafe_allow_html=True)

# ── Validate Groq ──────────────────────────────────────────────────────────────
if not Config.GROQ_API_KEY:
    st.markdown("""
    <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                border-radius:10px;padding:1.5rem;font-family:'Share Tech Mono',monospace;
                color:#ef4444;letter-spacing:1px;">
      ⛔ // GROQ API KEY NOT CONFIGURED — CHECK YOUR .env FILE //
    </div>""", unsafe_allow_html=True)
    st.stop()

try:
    from groq import Groq
    client = Groq(api_key=Config.GROQ_API_KEY)
except ImportError:
    st.error("Groq SDK not installed. Run `pip install groq`.")
    st.stop()

# ── Build context from DB ──────────────────────────────────────────────────────
@st.cache_resource
def get_db(): return Database()

db = get_db()
articles = db.get_recent_articles(limit=50)

context_lines = []
for art in articles[:20]:
    ana = art.get('analysis', {}) or {}
    kws = ", ".join(ana.get('keywords', []))
    urg = ana.get('urgency_score', 0)
    context_lines.append(f"- {art.get('title','—')} | المشاعر: {ana.get('sentiment','؟')} | أهمية: {urg:.1f} | الكلمات: {kws}")

context_str = "\n".join(context_lines) if context_lines else "لا توجد أخبار في قاعدة البيانات بعد."

system_prompt = f"""
أنت AACIE — وكيل ذكاء اصطناعي متقدم يعمل ضمن منظومة Mission Control v5.
محرك استدلالك: Groq Llama-3 70B — أسرع نموذج ذكاء اصطناعي في العالم.
تحدث دائماً بأسلوب احترافي، هادئ، دقيق، كأنك عقل آلي متقدم.
اللغة الأساسية: العربية. يمكنك الرد بالإنجليزية إذا طُلب.

أنت مطّلع على أحدث الأخبار المستخرجة من قاعدة بياناتك:
{context_str}

استخدم هذا السياق دائماً للإجابة بثقة واستناداً للبيانات الفعلية.
"""

# ── Chat State ─────────────────────────────────────────────────────────────────
if "v5_messages" not in st.session_state:
    st.session_state.v5_messages = [
        {"role": "assistant", "content": f"مرحباً أيها القائد. أنا AACIE V5 — وكيل الاستخبارات الذكي. قاعدة بياناتي تحتوي الآن على **{len(articles)} تقرير استخباراتي**. كيف يمكنني مساعدتك اليوم؟ 🎯"}
    ]

# ── Render History ─────────────────────────────────────────────────────────────
for msg in st.session_state.v5_messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='arabic'>{msg['content']}</div>", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("اسأل AACIE عن الأخبار، التحليلات، أو أي شيء..."):
    st.session_state.v5_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='arabic'>{prompt}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;
                    color:#64748b;letter-spacing:1px;animation:pulse 1s infinite;">
          // PROCESSING THROUGH GROQ ACCELERATOR... //
        </div>""", unsafe_allow_html=True)
        try:
            history_ctx = [{"role": m["role"], "content": m["content"]}
                           for m in st.session_state.v5_messages[-6:]]
            completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, *history_ctx],
                model="llama-3.3-70b-versatile",
                temperature=0.3, max_tokens=900,
            )
            reply = completion.choices[0].message.content
            placeholder.markdown(f"<div class='arabic'>{reply}</div>", unsafe_allow_html=True)
            st.session_state.v5_messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            placeholder.error(f"⚠️ Groq API Error: {e}")
