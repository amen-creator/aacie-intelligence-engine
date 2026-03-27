# 🧠 AACIE – Arabic Autonomous Content Intelligence Engine

> تحليل ذكي للمحتوى العربي • كشف اللهجات • تحليل المشاعر • رصد الاتجاهات

**Zero-cost** Arabic content intelligence platform built with Python, Firecrawl, Supabase, and Streamlit.

---

## ⚡ Quick Start

```bash
# 1. Clone & setup
cd c:\Users\amend\Documents\gomycode\aacie

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your API keys (all optional for demo mode)

# 5. Launch dashboard
streamlit run app.py

# 6. Or run the CLI pipeline (demo mode, no API needed)
python main.py --demo
```

---

## 🏗️ Project Structure

```
aacie/
├── app.py               # Streamlit dashboard
├── main.py              # CLI pipeline entrypoint
├── requirements.txt
├── .env.example         # API key template
├── core/
│   ├── scraper.py       # Firecrawl web scraper + budget tracker
│   ├── analyzer.py      # Gemini NLP: dialect, sentiment, keywords
│   ├── database.py      # Supabase ORM (in-memory fallback)
│   └── reporter.py      # PDF/TXT report generator
├── data/
│   ├── demo_articles.json   # Sample Arabic articles (offline demo)
│   └── cache/               # URL-keyed scrape cache (auto-created)
└── reports/                 # Generated PDF/TXT reports (auto-created)
```

---

## 🔑 API Keys (All Optional)

| Key | Source | Used For |
|-----|--------|----------|
| `FIRECRAWL_API_KEY` | [firecrawl.dev](https://firecrawl.dev) | Live web scraping (500 pages/month free) |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | NLP analysis (free tier) |
| `SUPABASE_URL` + `SUPABASE_KEY` | [supabase.com](https://supabase.com) | Persistent storage (free tier) |

> **Without any keys**: the app runs in full demo mode using heuristic NLP and in-memory storage.

---

## 🗄️ Supabase Schema

Run the SQL in `core/database.py → SCHEMA_SQL` in your Supabase SQL Editor to create tables.

---

## 🚀 Deploy (Free)

| Platform | Command |
|----------|---------|
| Hugging Face Spaces | Push to HF repo with `app.py` as entrypoint |
| PythonAnywhere | Upload files, `pip install -r requirements.txt`, set web app |
| Streamlit Cloud | Connect GitHub repo → auto deploy |

---

## 📄 License

MIT © 2026 – Built with Google Antigravity + Claude AI
