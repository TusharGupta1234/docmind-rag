import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind · RAG Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",   # FIX: always start expanded
)

# ── Session State Init (must be BEFORE any widget) ────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "vectorstore": None,
        "doc_ready": False,
        "doc_name": None,
        "chunk_count": 0,
        "theme": "dark",          # NEW: "dark" | "light"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Derive theme vars ──────────────────────────────────────────────────────────
IS_DARK = st.session_state.theme == "dark"

# Light-mode tokens
LIGHT = {
    "bg":          "#f5f3ef",
    "surface":     "#ffffff",
    "surface2":    "#f0ede8",
    "sidebar_bg":  "#1c1917",
    "sidebar_s2":  "#292524",
    "sidebar_bdr": "#3a3532",
    "border":      "#e2ddd7",
    "text":        "#1c1917",
    "text_inv":    "#f5f5f4",
    "muted":       "#78716c",
    "muted_inv":   "#a8a29e",
    "chat_ta":     "#1c1917",      # textarea text in chat input
}

# Dark-mode tokens
DARK = {
    "bg":          "#0f0e0d",
    "surface":     "#1a1917",
    "surface2":    "#242220",
    "sidebar_bg":  "#111110",
    "sidebar_s2":  "#1c1b19",
    "sidebar_bdr": "#2e2c29",
    "border":      "#2e2c29",
    "text":        "#f5f5f4",
    "text_inv":    "#f5f5f4",
    "muted":       "#a8a29e",
    "muted_inv":   "#78716c",
    "chat_ta":     "#f5f5f4",
}

T = DARK if IS_DARK else LIGHT

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Tokens ── */
:root {{
    --bg:          {T['bg']};
    --surface:     {T['surface']};
    --surface2:    {T['surface2']};
    --sidebar-bg:  {T['sidebar_bg']};
    --sidebar-s2:  {T['sidebar_s2']};
    --sidebar-bdr: {T['sidebar_bdr']};
    --border:      {T['border']};
    --accent:      #0d9488;
    --accent-lt:   #ccfbf1;
    --accent-dk:   #0f766e;
    --amber:       #d97706;
    --amber-lt:    #fef3c7;
    --success:     #16a34a;
    --success-lt:  #dcfce7;
    --danger:      #dc2626;
    --text:        {T['text']};
    --text-inv:    {T['text_inv']};
    --muted:       {T['muted']};
    --muted-inv:   {T['muted_inv']};
    --chat-ta:     {T['chat_ta']};
    --radius:      10px;
    --shadow:      0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.16), 0 2px 4px rgba(0,0,0,0.08);
}}

/* ── Global Reset ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── FIX: Force sidebar to ALWAYS be visible and never collapse to 0 ── */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-bdr) !important;
    min-width: 260px !important;
    display: block !important;
    visibility: visible !important;
}}
/* Keep the collapse button from hiding the sidebar permanently */
[data-testid="stSidebar"][aria-expanded="false"] {{
    min-width: 0 !important;
}}
[data-testid="stSidebar"] * {{
    color: var(--text-inv) !important;
}}
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stFileUploader label {{
    color: var(--muted-inv) !important;
    font-size: 12px !important;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.025em !important;
    color: var(--text) !important;
}}

/* ── Sidebar brand ── */
.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 20px;
    border-bottom: 1px solid var(--sidebar-bdr);
    margin-bottom: 18px;
}}
.sidebar-brand .brand-icon {{
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; line-height: 1;
}}
.sidebar-brand .brand-name {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 18px;
    color: var(--text-inv) !important;
    letter-spacing: -0.03em;
}}
.sidebar-brand .brand-tag {{
    display: block;
    font-size: 10px;
    font-weight: 500;
    color: var(--accent) !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 1px;
}}

/* ── Section labels in sidebar ── */
.section-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted-inv) !important;
    margin-bottom: 8px;
    margin-top: 22px;
    padding-left: 2px;
}}

/* ── Status Badges ── */
.status-badge {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
    width: 100%;
    box-sizing: border-box;
}}
.status-badge.ready {{
    background: rgba(13,148,136,0.18);
    color: #5eead4 !important;
    border: 1px solid rgba(13,148,136,0.35);
}}
.status-badge.waiting {{
    background: rgba(168,162,158,0.12);
    color: var(--muted-inv) !important;
    border: 1px solid rgba(168,162,158,0.2);
}}
.status-badge.processing {{
    background: rgba(217,119,6,0.15);
    color: #fbbf24 !important;
    border: 1px solid rgba(217,119,6,0.3);
}}
.status-badge .dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
}}

/* ── Metric Cards ── */
.metric-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 10px 0 4px;
}}
.metric-card {{
    background: var(--sidebar-s2);
    border: 1px solid var(--sidebar-bdr);
    border-radius: 8px;
    padding: 10px 12px;
}}
.metric-card .mc-label {{
    font-size: 10px;
    color: var(--muted-inv) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}}
.metric-card .mc-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 500;
    color: var(--text-inv) !important;
    margin-top: 2px;
}}

/* ── Sidebar inputs ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {{
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    color: var(--text-inv) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {{
    background: var(--sidebar-s2) !important;
    border: 1px dashed var(--sidebar-bdr) !important;
    border-radius: var(--radius) !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] * {{
    color: var(--muted-inv) !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"],
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section > input + div {{
    background: var(--sidebar-s2) !important;
    color: var(--muted-inv) !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    color: var(--muted-inv) !important;
    border-radius: 6px !important;
}}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {{
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.01em !important;
    padding: 9px 18px !important;
    width: 100% !important;
    transition: background .2s !important;
    box-shadow: 0 1px 3px rgba(13,148,136,0.3) !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: var(--accent-dk) !important;
}}

/* Theme toggle & clear buttons — ghost style */
[data-testid="stSidebar"] .stButton:nth-last-child(-n+2) > button {{
    background: transparent !important;
    color: var(--muted-inv) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton:nth-last-child(-n+2) > button:hover {{
    border-color: var(--muted-inv) !important;
    color: var(--text-inv) !important;
}}

/* ── Main Header ── */
.main-header {{
    padding: 28px 0 20px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
}}
.main-header h1 {{
    font-size: 32px !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    margin: 0 0 5px !important;
    letter-spacing: -0.03em !important;
}}
.main-header h1 span {{ color: var(--accent); }}
.main-header p {{
    color: var(--muted) !important;
    font-size: 14px !important;
    margin: 0 !important;
    font-weight: 400 !important;
}}

/* ── Empty State ── */
.empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    text-align: center;
    gap: 10px;
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 16px;
    margin-top: 16px;
    box-shadow: var(--shadow);
}}
.empty-state .es-icon  {{ font-size: 44px; line-height: 1; filter: grayscale(0.2); }}
.empty-state .es-title {{
    font-size: 17px; font-weight: 700;
    color: var(--text);
    margin-top: 4px;
}}
.empty-state .es-sub {{
    font-size: 13px; color: var(--muted);
    max-width: 320px; line-height: 1.6;
}}
.empty-state .es-arrow {{
    font-size: 13px; color: var(--accent); font-weight: 600;
    background: var(--accent-lt); padding: 6px 14px;
    border-radius: 20px; margin-top: 6px;
}}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    margin-bottom: 10px !important;
    box-shadow: var(--shadow) !important;
}}
/* All text inside chat messages uses the MAIN text color (not sidebar inverted) */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] code,
[data-testid="stChatMessage"] * {{
    color: var(--text) !important;
}}

/* ── Chat Input bottom bar ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div,
[data-testid="stBottomBlockContainer"] > div > div {{
    background: var(--bg) !important;
    border-top: none !important;
    box-shadow: none !important;
}}

[data-testid="stChatInput"] {{
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06) !important;
    overflow: hidden !important;
    transition: border-color .15s, box-shadow .15s !important;
}}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

/* Textarea text color adapts to theme */
[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: var(--chat-ta) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    caret-color: var(--accent) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--muted) !important;
    opacity: 0.7;
}}
[data-testid="stChatInput"] textarea:focus {{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,0.1), 0 2px 16px rgba(0,0,0,0.06) !important;
}}
[data-testid="stChatInput"] button {{
    background: var(--accent) !important;
    border: none !important;
    border-radius: 9px !important;
    margin: 6px !important;
    transition: background .15s !important;
}}
[data-testid="stChatInput"] button:hover {{ background: var(--accent-dk) !important; }}
[data-testid="stChatInput"] button svg {{ fill: #fff !important; stroke: #fff !important; }}

/* ── Sliders ── */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}}

/* ── Expander in sidebar ── */
[data-testid="stSidebar"] [data-testid="stExpander"] {{
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    color: var(--muted-inv) !important;
    font-size: 12px !important;
}}

/* ── Divider ── */
[data-testid="stSidebar"] hr {{
    border-color: var(--sidebar-bdr) !important;
    margin: 12px 0 !important;
}}

/* ── Warning / error boxes in main area ── */
[data-testid="stAlert"] {{
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}}

/* ── Spinner text ── */
.stSpinner > div {{ color: var(--muted) !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}

/* ── Kill outlines ── */
*:focus {{ outline: none !important; }}
textarea:focus, input:focus {{ box-shadow: none !important; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_embeddings():
    from langchain_mistralai import MistralAIEmbeddings
    return MistralAIEmbeddings()


def process_pdf(uploaded_file, chunk_size: int, chunk_overlap: int) -> int:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_documents(docs)

        embeddings = get_embeddings()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="chroma_db",
        )

        st.session_state.vectorstore = vectorstore
        st.session_state.doc_ready = True
        st.session_state.doc_name = uploaded_file.name
        st.session_state.chunk_count = len(chunks)
        return len(chunks)

    finally:
        os.unlink(tmp_path)


def get_retriever(k: int, fetch_k: int, lambda_mult: float):
    return st.session_state.vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
    )


def query_rag(question: str, k: int, fetch_k: int, lambda_mult: float, model: str) -> str:
    from langchain_mistralai import ChatMistralAI
    from langchain_core.prompts import ChatPromptTemplate

    retriever = get_retriever(k, fetch_k, lambda_mult)
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful AI assistant.\n\n"
         "Use ONLY the provided context to answer the question.\n\n"
         "If the answer is not present in the context, "
         "say: \"I could not find the answer in the document.\""),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    ])

    llm = ChatMistralAI(model=model)
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    return response.content


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
      <div class="brand-icon">🧠</div>
      <div>
        <div class="brand-name">DocMind</div>
        <span class="brand-tag">RAG · MistralAI</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Document Status ──
    if st.session_state.doc_ready:
        st.markdown(f"""
        <div class="status-badge ready">
          <span class="dot"></span> {st.session_state.doc_name}
        </div>
        <div class="metric-row">
          <div class="metric-card">
            <div class="mc-label">Chunks</div>
            <div class="mc-value">{st.session_state.chunk_count}</div>
          </div>
          <div class="metric-card">
            <div class="mc-label">Store</div>
            <div class="mc-value">Chroma</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="status-badge waiting"><span class="dot"></span> No document indexed</div>',
            unsafe_allow_html=True,
        )

    # ── PDF Upload ──
    st.markdown('<div class="section-label">📄 Document</div>', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

    with st.expander("⚙️ Chunking Options", expanded=False):
        chunk_size    = st.number_input("Chunk Size",    min_value=200, max_value=4000, value=1000, step=100)
        chunk_overlap = st.number_input("Chunk Overlap", min_value=0,   max_value=800,  value=200,  step=50)

    if uploaded_pdf:
        if st.button("⚡ Process & Index Document"):
            st.markdown(
                '<div class="status-badge processing"><span class="dot"></span> Indexing…</div>',
                unsafe_allow_html=True,
            )
            with st.spinner("Splitting, embedding, and persisting…"):
                try:
                    n = process_pdf(uploaded_pdf, chunk_size, chunk_overlap)
                    st.success(f"✅ Indexed {n} chunks successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # ── Model Config ──
    st.markdown('<div class="section-label">🤖 Model</div>', unsafe_allow_html=True)
    model_choice = st.selectbox(
        "MistralAI Model",
        ["mistral-small-2506", "mistral-medium-latest", "mistral-large-latest"],
        label_visibility="collapsed",
    )

    # ── MMR Parameters ──
    st.markdown('<div class="section-label">🎛️ MMR Retriever</div>', unsafe_allow_html=True)
    mmr_k       = st.slider("k  (final docs returned)", 1, 10, 4)
    mmr_fetch_k = st.slider("fetch_k  (candidates)", mmr_k, 30, max(10, mmr_k))
    mmr_lambda  = st.slider("λ  diversity ↔ relevance", 0.0, 1.0, 0.5, 0.05,
                             help="0 = max diversity · 1 = max relevance")

    st.divider()

    # ── Theme Toggle ──
    # FIX: Use a button that stores theme in session_state and reruns,
    # so the toggle survives sidebar collapse/expand cycles.
    theme_label = "☀️ Switch to Light Mode" if IS_DARK else "🌙 Switch to Dark Mode"
    if st.button(theme_label):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>Doc<span>Mind</span></h1>
  <p>Ask anything about your document — powered by MistralAI + ChromaDB retrieval.</p>
</div>
""", unsafe_allow_html=True)

# Empty state when no document is loaded
if not st.session_state.doc_ready and not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <span class="es-icon">📑</span>
      <div class="es-title">No document loaded yet</div>
      <div class="es-sub">Upload a PDF from the sidebar and click
        <strong>Process &amp; Index Document</strong> to get started.</div>
      <div class="es-arrow">← Start in the sidebar</div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your document…"):
    if not st.session_state.doc_ready:
        with st.chat_message("assistant"):
            st.warning("⚠️ Please upload and index a PDF document first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer…"):
                try:
                    answer = query_rag(
                        question=prompt,
                        k=mmr_k,
                        fetch_k=mmr_fetch_k,
                        lambda_mult=mmr_lambda,
                        model=model_choice,
                    )
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    err_msg = f"❌ An error occurred: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})