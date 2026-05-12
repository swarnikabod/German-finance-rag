import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from src.config import Config
from src.rag.chain import chain_with_sources
from src.vectorstore.store import get_collection_size

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECB · BaFin RAG Analyst",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0a0f1e; }
.block-container { padding: 2rem 3rem; max-width: 1100px; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0d1b2a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #60a5fa;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0f6ff;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}
.hero p {
    color: #8ba3c7;
    font-size: 0.95rem;
    margin: 0;
    max-width: 600px;
}

/* Stats row */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.stat-card {
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #60a5fa;
    line-height: 1;
}
.stat-label {
    font-size: 0.7rem;
    color: #4a6fa5;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

/* Quick questions */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #4a6fa5;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.7rem;
}

/* Chat messages */
.msg-user {
    background: linear-gradient(135deg, #1e3a5f, #1a2f50);
    border: 1px solid #2a4a7f;
    border-radius: 12px 12px 4px 12px;
    padding: 1rem 1.2rem;
    margin: 1rem 0 0.5rem 3rem;
    color: #e2eeff;
    font-size: 0.92rem;
}
.msg-bot {
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 12px 12px 12px 4px;
    padding: 1.2rem 1.4rem;
    margin: 0.5rem 3rem 1rem 0;
    color: #c8daf5;
    font-size: 0.92rem;
    line-height: 1.7;
}
.msg-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.msg-label.user { color: #60a5fa; }
.msg-label.bot { color: #34d399; }

/* Source chips */
.source-chip {
    display: inline-block;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
    color: #60a5fa;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    margin: 0.2rem 0.2rem 0.2rem 0;
    font-family: 'Courier New', monospace;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #060d1a !important;
    border-right: 1px solid #1e3a5f;
}
.sidebar-section {
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.sidebar-title {
    font-size: 0.65rem;
    font-weight: 700;
    color: #4a6fa5;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.7rem;
}
.sidebar-item {
    font-size: 0.78rem;
    color: #8ba3c7;
    padding: 0.3rem 0;
    border-bottom: 1px solid #0d1b2a;
}
.sidebar-item span { color: #60a5fa; float: right; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ── Init ─────────────────────────────────────────────────────────────────────
config = Config()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "en"

try:
    collection_size = get_collection_size(config)
except:
    collection_size = 481

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 RAG Analyst")
    st.markdown("---")

    # Language toggle
    lang = st.radio(
        "Response language",
        ["🇬🇧 English", "🇩🇪 Deutsch"],
        index=0 if st.session_state.language == "en" else 1,
        key="lang_radio"
    )
    st.session_state.language = "en" if "English" in lang else "de"

    st.markdown("---")

    st.markdown('<div class="sidebar-title">System</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-section">
        <div class="sidebar-item">Embedding<span>Jina-DE v2</span></div>
        <div class="sidebar-item">LLM<span>{config.ollama_model}</span></div>
        <div class="sidebar-item">Vector DB<span>ChromaDB</span></div>
        <div class="sidebar-item">Docs indexed<span>{collection_size}</span></div>
        <div class="sidebar-item">Chunk size<span>{config.chunk_size} tok</span></div>
        <div class="sidebar-item">Top-K<span>{config.top_k}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">Data Sources</div>', unsafe_allow_html=True)
    st.markdown("""
    # FIND the sidebar-section for Data Sources and replace with:
    <div class="sidebar-section">
        <div class="sidebar-item">ECB Annual Report 2024<span>✅</span></div>
        <div class="sidebar-item">ECB Annual Report 2023<span>✅</span></div>
        <div class="sidebar-item">ECB Annual Accounts 2024<span>✅</span></div>
        <div class="sidebar-item">ECB FSR Nov 2025<span>✅</span></div>
        <div class="sidebar-item">ECB FSR May 2025<span>✅</span></div>
        <div class="sidebar-item">ECB FSR Nov 2024<span>✅</span></div>
        <div class="sidebar-item">BaFin Annual Report 2024 EN+DE<span>✅</span></div>
        <div class="sidebar-item">BaFin Annual Report 2023 EN+DE<span>✅</span></div>
        <div class="sidebar-item">BaFin Annual Report 2025<span>🔜 Jun 2026</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown('<p style="font-size:0.65rem;color:#2a4a7f;text-align:center;">Built with LangChain · ChromaDB · Mistral · Jina-DE</p>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🔬 Regulatory Intelligence · ECB · BaFin</div>
    <h1>German Financial Document RAG</h1>
    <p>Query ECB and BaFin regulatory documents with source citations. Built for financial analysts, risk teams, and compliance professionals.</p>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-value">{collection_size}</div>
        <div class="stat-label">Pages Indexed</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">2,619</div>
        <div class="stat-label">Chunks</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">3</div>
        <div class="stat-label">Source Documents</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">100%</div>
        <div class="stat-label">Free · Local LLM</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick questions ───────────────────────────────────────────────────────────
if not st.session_state.messages:
    questions_en = [
        "What was the ECB deposit facility rate in December 2024?",
        "What are the main financial stability risks in ECB 2023?",
        "How did ECB handle inflation above 2% target in 2024?",
        "What is ECB's monetary policy stance on APP and PEPP?",
    ]
    questions_de = [
        "Was war der EZB-Einlagensatz im Dezember 2024?",
        "Was sind die Hauptrisiken für die Finanzstabilität laut EZB 2023?",
        "Wie hat die EZB auf Inflation über 2% im Jahr 2024 reagiert?",
        "Was ist die Haltung der EZB zu APP und PEPP?",
    ]
    questions = questions_en if st.session_state.language == "en" else questions_de

    st.markdown('<div class="section-label">💡 Try these questions</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, q in enumerate(questions):
        with cols[i % 2]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-label user">▶ Analyst Query</div>
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        answer = msg["content"]["answer"]
        docs = msg["content"].get("documents", [])

        source_chips = ""
        seen = set()
        for doc in docs:
            src = doc.metadata.get("source", "unknown")
            pg = doc.metadata.get("page", "?")
            key = f"{src}·p{pg}"
            if key not in seen:
                seen.add(key)
                short = src.replace("ecb_", "").replace("_", " ").replace(".pdf", "")
                source_chips += f'<span class="source-chip">📄 {short} · p{pg}</span>'

        st.markdown(f"""
        <div class="msg-bot">
            <div class="msg-label bot">◉ RAG Response · Mistral + Jina-DE</div>
            {answer}
            <div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid #1e3a5f;">
                <span style="font-size:0.65rem;color:#4a6fa5;text-transform:uppercase;letter-spacing:0.08em;">Sources · </span>
                {source_chips}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Input + response ──────────────────────────────────────────────────────────
lang_hint = "Ask about ECB/BaFin documents in English or German..." if st.session_state.language == "en" else "Stellen Sie eine Frage zu EZB/BaFin-Dokumenten auf Englisch oder Deutsch..."

user_input = st.chat_input(lang_hint)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    lang_instruction = (
        "Respond in English." if st.session_state.language == "en"
        else "Antworte auf Deutsch."
    )
    augmented_query = f"{user_input}\n\n[{lang_instruction}]"

    with st.spinner("🔍 Searching 2,619 document chunks..."):
        try:
            result = chain_with_sources(augmented_query, config)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": {"answer": f"❌ Error: {str(e)}", "documents": []}
            })
    st.rerun()