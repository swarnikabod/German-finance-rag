import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from src.config import Config
from src.rag.chain import chain_with_sources
from src.vectorstore.store import get_collection_size

st.set_page_config(
    page_title="RegDoc Analyst · ECB & BaFin RAG",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── MAIN BG ── */
.main { background: #fafaf8; }
.block-container { padding: 2rem 2.8rem; max-width: 1100px; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #1e1e1e !important;
    padding: 0 !important;
}

.sb-inner { padding: 1.8rem 1.4rem; }

.sb-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #f5e6c8;
    letter-spacing: -0.01em;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}
.sb-tagline {
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.6rem;
    font-weight: 500;
}
.sb-divider {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 1.2rem 0;
}
.sb-section {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #c9a84c;
    margin: 1.4rem 0 0.7rem 0;
}
.sb-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.38rem 0;
    border-bottom: 1px solid #161616;
    font-size: 0.76rem;
}
.sb-row-key { color: #666; font-weight: 400; }
.sb-row-val { color: #e8e8e8; font-weight: 500; font-size: 0.74rem; }
.sb-doc {
    display: flex;
    justify-content: space-between;
    padding: 0.32rem 0;
    border-bottom: 1px solid #141414;
    font-size: 0.72rem;
    color: #555;
}
.sb-doc-name { color: #888; }
.sb-doc-check { color: #c9a84c; font-weight: 600; }
.sb-doc-soon { color: #444; font-style: italic; }

.sb-author {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #1e1e1e;
    font-size: 0.7rem;
    color: #444;
    line-height: 1.8;
}
.sb-author strong { color: #c9a84c; font-size: 0.8rem; display: block; margin-bottom: 0.3rem; }
.sb-author a { color: #8a7a5a; text-decoration: none; }
.sb-author a:hover { color: #c9a84c; }

/* ── HERO ── */
.hero {
    background: #ffffff;
    border: 1px solid #ede9e0;
    border-radius: 14px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #fdf8ee;
    border: 1px solid #e8d9b0;
    color: #9a7a3a;
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.28rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #0f0f0f;
    margin: 0 0 0.6rem 0;
    line-height: 1.15;
    font-weight: 600;
    letter-spacing: -0.02em;
}
.hero-desc {
    font-size: 0.9rem;
    color: #777;
    line-height: 1.65;
    max-width: 520px;
    font-weight: 300;
}
.hero-right {
    text-align: right;
    min-width: 120px;
    padding-left: 2rem;
}
.hero-num {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    color: #c9a84c;
    line-height: 1;
    font-weight: 400;
}
.hero-num-label {
    font-size: 0.68rem;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
    line-height: 1.5;
}

/* ── STATS ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.4rem;
}
.stat-card {
    background: #ffffff;
    border: 1px solid #ede9e0;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c9a84c, #e8cc80);
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    color: #0f0f0f;
    line-height: 1;
    font-weight: 400;
}
.stat-lbl {
    font-size: 0.62rem;
    font-weight: 600;
    color: #bbb;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-top: 0.35rem;
}

/* ── QUICK QUESTIONS ── */
.qs-header {
    font-size: 0.62rem;
    font-weight: 700;
    color: #c9a84c;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.7rem;
}

/* ── CHAT ── */
.msg-user-wrap { margin: 1rem 0 0.5rem 0; }
.msg-user-lbl {
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 0.4rem;
    padding-left: 0.2rem;
}
.msg-user {
    background: #0f0f0f;
    color: #f0ead8;
    border-radius: 10px 10px 3px 10px;
    padding: 1rem 1.3rem;
    margin-left: 5rem;
    font-size: 0.9rem;
    line-height: 1.6;
    font-weight: 300;
}
.msg-bot-wrap { margin: 0.5rem 0 1rem 0; }
.msg-bot-lbl {
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.4rem;
    padding-left: 0.2rem;
}
.msg-bot {
    background: #ffffff;
    border: 1px solid #ede9e0;
    border-left: 3px solid #c9a84c;
    border-radius: 3px 10px 10px 10px;
    padding: 1.2rem 1.5rem;
    margin-right: 5rem;
    font-size: 0.88rem;
    line-height: 1.75;
    color: #2a2a2a;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.citations {
    margin-top: 1rem;
    padding-top: 0.8rem;
    border-top: 1px solid #f0ece4;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.4rem;
}
.cit-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-right: 0.2rem;
}
.cit-chip {
    background: #fdf8ee;
    border: 1px solid #e8d9b0;
    color: #8a7040;
    font-size: 0.66rem;
    font-family: 'Courier New', monospace;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    font-weight: 500;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #ffffff !important;
    border: 1px solid #e0d8c8 !important;
    color: #555 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    text-align: left !important;
    padding: 0.65rem 1rem !important;
    line-height: 1.4 !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stButton > button:hover {
    background: #0f0f0f !important;
    border-color: #0f0f0f !important;
    color: #f5e6c8 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}

/* ── RADIO ── */
.stRadio > div { gap: 0.4rem !important; }
.stRadio label {
    font-size: 0.8rem !important;
    color: #888 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── CHAT INPUT ── */
.stChatInput {
    border-top: 1px solid #ede9e0 !important;
    background: #fafaf8 !important;
    padding: 1rem 0 !important;
}
.stChatInput textarea {
    background: #ffffff !important;
    border: 1px solid #e0d8c8 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    color: #0f0f0f !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #c9a84c !important; }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
config = Config()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "en"
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

try:
    collection_size = get_collection_size(config)
except:
    collection_size = 22655

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 RegDoc Analyst")
    st.caption("ECB · BaFin · Regulatory Intelligence")
    st.divider()

    lang = st.radio(
        "Response language",
        ["🇬🇧  English", "🇩🇪  Deutsch"],
        index=0 if st.session_state.language == "en" else 1,
    )
    st.session_state.language = "en" if "English" in lang else "de"

    st.divider()

    st.markdown("**⚙️ SYSTEM**")
    st.markdown(f"""
| | |
|:--|--:|
| Embedding | `multilingual-e5` |
| LLM | `{config.ollama_model}` |
| Vector DB | `ChromaDB` |
| Chunks | `{collection_size:,}` |
| Chunk size | `256 · 128 overlap` |
| Top-K | `{config.top_k}` |
""")
    

    st.divider()

    st.markdown("**DATA SOURCES**")
    sources = [
        ("ECB Annual Report 2024", "✓"),
        ("ECB Annual Report 2023", "✓"),
        ("ECB Annual Accounts 2024", "✓"),
        ("ECB FSR Nov 2025", "✓"),
        ("ECB FSR May 2025", "✓"),
        ("ECB FSR Nov 2024", "✓"),
        ("BaFin AR 2024 EN+DE", "✓"),
        ("BaFin AR 2023 EN+DE", "✓"),
        ("BaFin AR 2025", "soon"),
    ]
    for name, status in sources:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(name)
        with c2:
            st.caption(status)

    st.divider()
    st.markdown("""
**👩‍💻 Swarnika Boddula**  
ML Engineer · German Finance RAG  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/swarnika-boddula-1b5166209/)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?style=flat&logo=github)](https://github.com/swarnikabod/German-finance-rag)
""")

    st.divider()

    if st.button("↺ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-left">
        <div class="hero-badge">⚡ Regulatory Intelligence · ECB · BaFin</div>
        <h1>German Financial<br>Document RAG</h1>
        <p class="hero-desc">Ask questions about ECB monetary policy and BaFin regulatory guidance in English or German — get precise answers with page-level citations from official regulatory documents.</p>
    </div>
    <div class="hero-right">
        <div class="hero-num">9</div>
        <div class="hero-num-label">source<br>documents<br>1,126 pages</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-num">1,126</div>
        <div class="stat-lbl">Pages indexed</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">22,655</div>
        <div class="stat-lbl">Vector chunks</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">+26%</div>
        <div class="stat-lbl">vs MiniLM baseline</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">Free</div>
        <div class="stat-lbl">Zero API cost · Local LLM</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Questions ─────────────────────────────────────────────────────────────────
EN_QUESTIONS = [
    "What was the ECB deposit facility rate in December 2024?",
    "What are the main financial stability risks in ECB FSR Nov 2025?",
    "What does BaFin say about AML compliance requirements?",
    "What is ECB's monetary policy stance on APP and PEPP?",
]
DE_QUESTIONS = [
    "Was war der EZB-Einlagensatz im Dezember 2024?",
    "Was sind die wichtigsten Finanzstabilitätsrisiken laut EZB FSR Nov 2025?",
    "Was sagt BaFin zu den AML-Compliance-Anforderungen?",
    "Wie ist die geldpolitische Haltung der EZB zu APP und PEPP?",
]
questions = EN_QUESTIONS if st.session_state.language == "en" else DE_QUESTIONS


def process_question(question: str):
    lang_instruction = (
        "Respond in English. Be direct and cite sources."
        if st.session_state.language == "en"
        else "Antworte auf Deutsch. Sei präzise und zitiere Quellen."
    )
    augmented = f"{question}\n\n[{lang_instruction}]"
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Searching 22,655 document chunks..."):
        try:
            result = chain_with_sources(augmented, config)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": {"answer": f"Error: {str(e)}", "documents": []}
            })


# ── Quick questions (only when chat is empty) ─────────────────────────────────
if not st.session_state.messages and st.session_state.pending_question is None:
    st.markdown('<div class="qs-header">💡 Try these questions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, q in enumerate(questions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user-wrap">
            <div class="msg-user-lbl">Your question</div>
            <div class="msg-user">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        answer = msg["content"].get("answer", "")
        docs_list = msg["content"].get("documents", [])
        seen = set()
        chips = ""
        for d in docs_list:
            src = d.metadata.get("source", "?")
            pg = d.metadata.get("page", "?")
            key = f"{src}·{pg}"
            if key not in seen:
                seen.add(key)
                short = (src.replace("ecb_", "ECB ")
                           .replace("bafin_", "BaFin ")
                           .replace("annual_report_", "AR ")
                           .replace("annual_accounts_", "Accounts ")
                           .replace("fsr_", "FSR ")
                           .replace(".pdf", "")
                           .replace("_", " ")
                           .strip())
                chips += f'<span class="cit-chip">{short} · p{pg}</span>'

        st.markdown(f"""
        <div class="msg-bot-wrap">
            <div class="msg-bot-lbl">◉ RAG Response · {config.ollama_model} + multilingual-e5</div>
            <div class="msg-bot">
                {answer}
                <div class="citations">
                    <span class="cit-label">Sources</span>
                    {chips if chips else '<span style="color:#ccc;font-size:0.7rem;">No sources retrieved</span>'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Process pending (quick button click) ──────────────────────────────────────
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    process_question(q)
    st.rerun()

# ── Chat input ────────────────────────────────────────────────────────────────
hint = (
    "Ask about ECB/BaFin documents in English or German..."
    if st.session_state.language == "en"
    else "Stellen Sie eine Frage zu EZB/BaFin-Dokumenten auf Englisch oder Deutsch..."
)
user_input = st.chat_input(hint)
if user_input:
    process_question(user_input)
    st.rerun()