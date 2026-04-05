import streamlit as st
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import tempfile
from dotenv import load_dotenv

load_dotenv()

# On Streamlit Cloud, secrets are in st.secrets — inject into env so all libraries pick it up
try:
    if "MISTRAL_API_KEY" in st.secrets:
        os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]
except Exception:
    pass  # Running locally, .env already loaded above

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind · RAG Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Tokens — Warm Light Theme ── */
:root {
    --bg:          #f5f3ef;
    --surface:     #ffffff;
    --surface2:    #f0ede8;
    --sidebar-bg:  #1c1917;
    --sidebar-s2:  #292524;
    --sidebar-bdr: #3a3532;
    --border:      #e2ddd7;
    --accent:      #0d9488;
    --accent-lt:   #ccfbf1;
    --accent-dk:   #0f766e;
    --amber:       #d97706;
    --amber-lt:    #fef3c7;
    --success:     #16a34a;
    --success-lt:  #dcfce7;
    --danger:      #dc2626;
    --text:        #1c1917;
    --text-inv:    #f5f5f4;
    --muted:       #78716c;
    --muted-inv:   #a8a29e;
    --radius:      10px;
    --shadow:      0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
}

/* ── Global Reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Main content block ── */
[data-testid="stMain"] {
    background-color: var(--bg) !important;
}

/* ── Sidebar — dark charcoal ── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-bdr) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-inv) !important;
}

/* ── Sidebar collapse button (inside sidebar, top-right) ── */
[data-testid="stSidebarCollapseButton"] {
    background: transparent !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background: var(--accent) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 8px !important;
}
[data-testid="stSidebarCollapseButton"] button svg * {
    stroke: #fff !important;
    fill: #fff !important;
}

/* ── Collapsed control button (outside sidebar, shows when sidebar hidden) ── */
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 32px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapsedControl"] button svg {
    color: #fff !important;
    fill: #fff !important;
    stroke: #fff !important;
}
[data-testid="stSidebarCollapsedControl"] button svg * {
    stroke: #fff !important;
    fill: #fff !important;
}
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stFileUploader label {
    color: var(--muted-inv) !important;
    font-size: 12px !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.025em !important;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 20px;
    border-bottom: 1px solid var(--sidebar-bdr);
    margin-bottom: 18px;
}
.sidebar-brand .brand-icon {
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; line-height: 1;
}
.sidebar-brand .brand-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 18px;
    color: var(--text-inv) !important;
    letter-spacing: -0.03em;
}
.sidebar-brand .brand-tag {
    display: block;
    font-size: 10px;
    font-weight: 500;
    color: var(--accent) !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 1px;
}

/* ── Section labels in sidebar ── */
.section-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted-inv) !important;
    margin-bottom: 8px;
    margin-top: 22px;
    padding-left: 2px;
}

/* ── Status Badges ── */
.status-badge {
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
}
.status-badge.ready {
    background: rgba(13,148,136,0.18);
    color: #5eead4 !important;
    border: 1px solid rgba(13,148,136,0.35);
}
.status-badge.waiting {
    background: rgba(168,162,158,0.12);
    color: var(--muted-inv) !important;
    border: 1px solid rgba(168,162,158,0.2);
}
.status-badge.processing {
    background: rgba(217,119,6,0.15);
    color: #fbbf24 !important;
    border: 1px solid rgba(217,119,6,0.3);
}
.status-badge .dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
}

/* ── Metric Cards ── */
.metric-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 10px 0 4px;
}
.metric-card {
    background: var(--sidebar-s2);
    border: 1px solid var(--sidebar-bdr);
    border-radius: 8px;
    padding: 10px 12px;
}
.metric-card .mc-label {
    font-size: 10px;
    color: var(--muted-inv) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.metric-card .mc-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 500;
    color: var(--text-inv) !important;
    margin-top: 2px;
}

/* ── Sidebar inputs ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    color: var(--text-inv) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
    background: var(--sidebar-s2) !important;
    border: 1px dashed var(--sidebar-bdr) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] * {
    color: var(--muted-inv) !important;
}
/* ── Fix white file uploader on mobile ── */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--sidebar-s2) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] section > input + div {
    background: var(--sidebar-s2) !important;
    color: var(--muted-inv) !important;
}
/* Browse files button */
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    color: var(--muted-inv) !important;
    border-radius: 6px !important;
}

/* ── Sidebar button ── */
[data-testid="stSidebar"] .stButton > button {
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
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-dk) !important;
}

/* Clear button — ghost style */
[data-testid="stSidebar"] .stButton:last-child > button {
    background: transparent !important;
    color: var(--muted-inv) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton:last-child > button:hover {
    border-color: var(--muted-inv) !important;
    color: var(--text-inv) !important;
}

/* ── Main Header ── */
.main-header {
    padding: 28px 0 20px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
}
.main-header h1 {
    font-size: 32px !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    margin: 0 0 5px !important;
    letter-spacing: -0.03em !important;
}
.main-header h1 span { color: var(--accent); }
.main-header p {
    color: var(--muted) !important;
    font-size: 14px !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

/* ── Empty State ── */
.empty-state {
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
}
.empty-state .es-icon {
    font-size: 44px;
    line-height: 1;
    filter: grayscale(0.2);
}
.empty-state .es-title {
    font-size: 17px;
    font-weight: 700;
    color: var(--text);
    margin-top: 4px;
}
.empty-state .es-sub {
    font-size: 13px;
    color: var(--muted);
    max-width: 320px;
    line-height: 1.6;
}
.empty-state .es-arrow {
    font-size: 13px;
    color: var(--accent);
    font-weight: 600;
    background: var(--accent-lt);
    padding: 6px 14px;
    border-radius: 20px;
    margin-top: 6px;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    margin-bottom: 10px !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] * {
    color: var(--text) !important;
}

/* ── Fix: Chat message text must be dark on white surface ── */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] code {
    color: var(--text) !important;
}

/* ── Chat Input — full bottom bar override ── */

/* Sticky bottom wrapper Streamlit generates */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div,
[data-testid="stBottomBlockContainer"] > div > div {
    background: var(--bg) !important;
    border-top: none !important;
    box-shadow: none !important;
}

/* Input widget shell — force white bg, dark text always */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div {
    background: #ffffff !important;
    border-color: var(--border) !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06) !important;
    overflow: visible !important;
}
/* Send button — teal with visible arrow icon */
[data-testid="stChatInput"] button,
[data-testid="stChatInputSubmitButton"] {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 9px !important;
    margin: 6px !important;
    color: #ffffff !important;
    transition: background .15s !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: visible !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] button:hover,
[data-testid="stChatInputSubmitButton"]:hover {
    background: var(--accent-dk) !important;
}
/* Force the SVG arrow icon to show white */
[data-testid="stChatInputSubmitButton"] svg,
[data-testid="stChatInput"] button svg {
    overflow: visible !important;
    display: block !important;
    width: 18px !important;
    height: 18px !important;
}
/* Hide the invisible bounding-box path Streamlit includes (M0 0h24v24H0V0z) */
[data-testid="stChatInputSubmitButton"] svg path:first-child,
[data-testid="stChatInput"] button svg path:first-child {
    display: none !important;
    fill: none !important;
    stroke: none !important;
}
/* Color only the actual arrow path (second path) */
[data-testid="stChatInputSubmitButton"] svg path:last-child,
[data-testid="stChatInput"] button svg path:last-child {
    fill: #ffffff !important;
    stroke: none !important;
}

/* ── Chat input textarea — use theme color so visible in both light & dark ── */
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #1c1917 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    caret-color: var(--accent) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #78716c !important;
}
[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,0.1), 0 2px 16px rgba(0,0,0,0.06) !important;
}
/* Kill ALL outlines site-wide */
*:focus { outline: none !important; }
textarea:focus, input:focus { box-shadow: none !important; }

/* ── Sliders ── */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ── Expander in sidebar ── */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: var(--sidebar-s2) !important;
    border: 1px solid var(--sidebar-bdr) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: var(--muted-inv) !important;
    font-size: 12px !important;
}

/* ── Divider ── */
[data-testid="stSidebar"] hr {
    border-color: var(--sidebar-bdr) !important;
    margin: 12px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

/* ── Hide the stop/running square button ── */
[data-testid="stStatusWidget"],
[data-testid="stAppStatus"],
[data-testid="stDecoration"],
[data-testid="stToolbarActions"] > div:last-child,
.stAppToolbar > div > div:last-child button:last-child {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ── Hamburger / Deploy menu button (top-right) ── */
[data-testid="stToolbarActions"] button,
[data-testid="stDecoration"] button,
.stAppToolbar [data-testid="stBaseButton-headerNoPadding"],
.stAppToolbar button:not([data-testid="stSidebarCollapseButton"]) {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    opacity: 1 !important;
}
.stAppToolbar button:not([data-testid="stSidebarCollapseButton"]) svg,
.stAppToolbar button:not([data-testid="stSidebarCollapseButton"]) svg * {
    stroke: #fff !important;
    fill: #fff !important;
}

/* ── Sidebar toggle button — target stToolbar which holds it ── */
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* The >> button inside the toolbar (collapsed state) */
[data-testid="stToolbar"] button,
[data-testid="stAppToolbar"] button,
.stAppToolbar button {
    background: var(--accent) !important;
    border: none !important;
    color: #fff !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stToolbar"] button svg *,
[data-testid="stAppToolbar"] button svg *,
.stAppToolbar button svg * {
    stroke: #fff !important;
    fill: #fff !important;
}

/* Collapse button inside sidebar */
[data-testid="stSidebarCollapseButton"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] button svg * {
    stroke: #fff !important;
    fill: #fff !important;
}
</style>
""", unsafe_allow_html=True)

# ── JS: Force sidebar toggle button visible ────────────────────────────────────
st.components.v1.html("""
<script>
(function() {
    const ACCENT = '#0d9488';

    function styleBtn(btn) {
        btn.style.setProperty('background', ACCENT, 'important');
        btn.style.setProperty('border', 'none', 'important');
        btn.style.setProperty('opacity', '1', 'important');
        btn.style.setProperty('visibility', 'visible', 'important');
        btn.style.setProperty('color', '#fff', 'important');
        btn.querySelectorAll('svg *').forEach(el => {
            el.style.setProperty('stroke', '#fff', 'important');
            el.style.setProperty('fill', '#fff', 'important');
        });
    }

    function fix() {
        // The JS runs in an iframe — target the parent document
        const doc = window.parent ? window.parent.document : document;

        // Remove the square status widget — try every possible selector
        [
            '[data-testid="stStatusWidget"]',
            '[data-testid="stAppStatus"]',
            '[data-testid="stDecoration"]',
            '[data-testid="stToolbarActions"] button:last-child',
        ].forEach(sel => {
            doc.querySelectorAll(sel).forEach(el => {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('width', '0', 'important');
                el.style.setProperty('overflow', 'hidden', 'important');
            });
        });

        // Fix chat input — white bg, dark text, teal send button
        const chatInput = doc.querySelector('[data-testid="stChatInput"]');
        if (chatInput) {
            // Only fix the direct wrapper divs, not the button container
            chatInput.style.setProperty('background', '#ffffff', 'important');
            chatInput.style.setProperty('background-color', '#ffffff', 'important');
            chatInput.querySelectorAll('div').forEach(d => {
                d.style.setProperty('background', '#ffffff', 'important');
                d.style.setProperty('background-color', '#ffffff', 'important');
            });
            chatInput.querySelectorAll('textarea').forEach(t => {
                t.style.setProperty('background', '#ffffff', 'important');
                t.style.setProperty('color', '#1c1917', 'important');
            });
            chatInput.querySelectorAll('button').forEach(btn => {
                btn.style.setProperty('background', '#0d9488', 'important');
                btn.style.setProperty('background-color', '#0d9488', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                // Fix parent div of button too
                if (btn.parentElement) {
                    btn.parentElement.style.setProperty('background', '#ffffff', 'important');
                    btn.parentElement.style.setProperty('background-color', '#ffffff', 'important');
                }
                btn.querySelectorAll('svg').forEach(svg => {
                    svg.style.setProperty('overflow', 'visible', 'important');
                });
                btn.querySelectorAll('path').forEach((p, i) => {
                    const d = p.getAttribute('d') || '';
                    // Skip the invisible bounding box path (M0 0h24v24H0V0z)
                    if (d === 'M0 0h24v24H0V0z' || d === 'M0 0h24v24H0z') {
                        p.style.setProperty('display', 'none', 'important');
                        p.style.setProperty('fill', 'none', 'important');
                        p.style.setProperty('stroke', 'none', 'important');
                    } else {
                        p.style.setProperty('fill', '#ffffff', 'important');
                        p.style.setProperty('stroke', 'none', 'important');
                        p.setAttribute('fill', '#ffffff');
                    }
                });
            });
        }

        // Sidebar toggle (left)
        const toolbar = doc.querySelector('[data-testid="stToolbar"]');
        if (toolbar) {
            toolbar.querySelectorAll('button').forEach(btn => {
                styleBtn(btn);
                btn.style.setProperty('border-radius', '8px', 'important');
            });
        }
        doc.querySelectorAll('.stAppToolbar button').forEach(btn => {
            styleBtn(btn);
            btn.style.setProperty('border-radius', '8px', 'important');
        });
        doc.querySelectorAll('[data-testid="stSidebarCollapseButton"] button').forEach(styleBtn);
    }

    fix();
    const root = window.parent ? window.parent.document.documentElement : document.documentElement;
    new MutationObserver(fix).observe(root, { childList: true, subtree: true });
    [300, 800, 1500, 3000].forEach(t => setTimeout(fix, t));
})();
</script>
""", height=0)


# ── Session State Init ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "vectorstore": None,
        "doc_ready": False,
        "doc_name": None,
        "chunk_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_embeddings():
    from langchain_mistralai import MistralAIEmbeddings
    return MistralAIEmbeddings()


def clear_vectorstore():
    """Reset all document-related session state."""
    st.session_state.vectorstore = None
    st.session_state.doc_ready = False
    st.session_state.doc_name = None
    st.session_state.chunk_count = 0
    st.session_state.messages = []


def process_pdf(uploaded_file, chunk_size: int, chunk_overlap: int) -> int:
    """Load, split, embed and store a PDF in memory. Returns chunk count."""
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    # Always wipe previous PDF before indexing a new one
    clear_vectorstore()

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
        # No persist_directory — purely in-memory.
        # Avoids all read-only filesystem errors on Streamlit Cloud.
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
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
        st.markdown('<div class="status-badge waiting"><span class="dot"></span> No document indexed</div>',
                    unsafe_allow_html=True)

    # ── PDF Upload ──
    st.markdown('<div class="section-label">📄 Document</div>', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

    with st.expander("⚙️ Chunking Options", expanded=False):
        chunk_size = st.number_input("Chunk Size", min_value=200, max_value=4000,
                                     value=1000, step=100)
        chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=800,
                                        value=200, step=50)

    if uploaded_pdf:
        if st.button("⚡ Process & Index Document"):
            st.markdown('<div class="status-badge processing"><span class="dot"></span> Indexing…</div>',
                        unsafe_allow_html=True)
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
    mmr_k = st.slider("k  (final docs returned)", 1, 10, 4)
    mmr_fetch_k = st.slider("fetch_k  (candidates)", mmr_k, 30, max(10, mmr_k))
    mmr_lambda = st.slider("λ  diversity ↔ relevance", 0.0, 1.0, 0.5, 0.05,
                           help="0 = max diversity · 1 = max relevance")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("❌ Remove PDF", use_container_width=True,
                     disabled=not st.session_state.doc_ready):
            clear_vectorstore()
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
      <div class="es-sub">Upload a PDF from the sidebar and click <strong>Process &amp; Index Document</strong> to get started.</div>
      <div class="es-arrow">← Start in the sidebar</div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your document…"):
    # Guard: no document indexed
    if not st.session_state.doc_ready:
        with st.chat_message("assistant"):
            st.warning("⚠️ Please upload and index a PDF document first using the sidebar.")
    else:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Stream-style response
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