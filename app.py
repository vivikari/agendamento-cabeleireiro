import streamlit as st
from database import init_db

st.set_page_config(
    page_title="BarberPro",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL — único lugar onde os estilos são definidos.
# Páginas NÃO devem redefinir classes já presentes aqui.
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stSidebarNav"] { display: none; }
html, body, [class*="css"]  { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0f0f0f; color: #f0ebe3; }
h1, h2, h3 { font-family: 'Playfair Display', serif; color: #f0ebe3; }

/* ── Layout ── */
.block-container {
    padding-top: 10rem !important;
    padding-left: 3rem  !important;
    padding-right: 3rem !important;
}

/* ── Cabeçalho de página ── */
.page-header { margin-bottom: 1.75rem; }
.ph-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 42px; font-weight: 600; color: #f0ebe3;
    line-height: 1; margin: 0; letter-spacing: -0.5px;
}
.page-header hr { border: none; border-top: 1px solid #1e1e1e; margin: 16px 0 0 0; }

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 16px;
}
[data-testid="metric-container"] label {
    color: #888 !important; font-size: 12px !important;
    text-transform: uppercase; letter-spacing: 1px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #d4a853 !important;
    font-family: 'Playfair Display', serif;
    font-size: 2rem !important;
}

/* ── Botões globais (fora da sidebar) ── */
.stButton > button {
    background: #d4a853; color: #0f0f0f; border: none;
    border-radius: 8px; font-family: 'DM Sans', sans-serif;
    font-weight: 500; padding: 10px 20px; transition: all 0.2s;
}
.stButton > button:hover {
    background: #e6be73; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(212,168,83,0.3);
}
.stButton > button:disabled {
    background: #1e1e1e !important; color: #3a3a3a !important;
    border: 1px solid #2a2a2a !important; cursor: not-allowed !important;
    transform: none !important; box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1a1a1a !important; border: 1px solid #2a2a2a !important;
    color: #f0ebe3 !important; border-radius: 8px !important;
}

/* ── Misc ── */
.stDataFrame { border: 1px solid #2a2a2a; border-radius: 12px; overflow: hidden; }
hr { border-color: #1e1e1e; }
.stSuccess { background: #1a2e1a; border-left: 3px solid #4caf50; }
.stWarning { background: #2e2a1a; border-left: 3px solid #d4a853; }
.stError   { background: #2e1a1a; border-left: 3px solid #e53935; }

/* ══════════════════════════════════════════
   COMPONENTES COMPARTILHADOS ENTRE PÁGINAS
   ══════════════════════════════════════════ */

/* Título de seção */
.secao-titulo {
    font-size: 13px; font-weight: 700; color: #555;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin: 28px 0 14px;
}
.secao-titulo.first { margin-top: 0; }

/* Card destaque (Dashboard, Início) */
.destaque-card {
    background: #161616; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 20px 24px; margin-bottom: 8px;
}
.destaque-icon  { font-size: 18px; margin-bottom: 10px; }
.destaque-val   { font-size: 32px; font-weight: 700; color: #d4a853; line-height: 1; }
.destaque-label { font-size: 13px; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }
.destaque-sub   { font-size: 13px; color: #666; margin-top: 4px; }

/* Card de agendamento (Agenda, Início) */
.ag-card {
    display: flex; align-items: stretch;
    background: #161616; border: 1px solid #222;
    border-radius: 12px; margin-bottom: 8px; overflow: hidden;
    transition: border-color 0.15s;
}
.ag-card:hover { border-color: #333; }
.ag-card.current { background: #1a1600; }
.ag-card-time {
    min-width: 72px; display: flex; align-items: center; justify-content: center;
    background: #111; border-right: 1px solid #1e1e1e;
    padding: 16px 8px; flex-shrink: 0;
}
.ag-time-txt    { font-size: 15px; font-weight: 700; color: #d4a853; }
.ag-card-body   { flex: 1; padding: 12px 16px; }
.ag-card-top    { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; flex-wrap: wrap; }
.ag-card-name   { font-size: 15px; font-weight: 600; color: #f0ebe3; }
.ag-card-meta   { font-size: 13px; color: #666; margin: 0; }
.ag-card-obs    { font-size: 12px; color: #555; margin: 5px 0 0; font-style: italic; }
.ag-status-pill {
    font-size: 11px; font-weight: 600;
    border-radius: 20px; padding: 2px 9px; letter-spacing: 0.3px;
}

/* Separador de data (Agenda) */
.date-sep { display: flex; align-items: center; gap: 10px; margin: 24px 0 10px; }
.date-sep-badge {
    font-size: 11px; font-weight: 600; color: #d4a853;
    background: rgba(212,168,83,0.10); border: 1px solid rgba(212,168,83,0.22);
    border-radius: 6px; padding: 3px 10px; white-space: nowrap;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.date-sep-line  { flex: 1; height: 1px; background: #1e1e1e; }
.date-sep-count { font-size: 11px; color: #444; }

/* Barra de progresso (Agenda) */
.prog-wrap {
    background: #161616; border: 1px solid #222;
    border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;
}
.prog-top   { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.prog-label { font-size: 13px; color: #666; }
.prog-bg    { height: 4px; background: #222; border-radius: 2px; overflow: hidden; margin-bottom: 12px; }
.prog-fill  { height: 100%; background: linear-gradient(90deg, #d4a853, #4caf50); border-radius: 2px; }
.prog-stats { display: flex; gap: 18px; flex-wrap: wrap; }
.prog-stat  { font-size: 12px; color: #666; display: flex; align-items: center; gap: 5px; }
.stat-dot   { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex-shrink: 0; }

/* Estado vazio */
.ag-empty      { text-align: center; padding: 56px 0; color: #333; font-size: 14px; }
.ag-empty-icon { font-size: 36px; margin-bottom: 10px; }

/* Histórico de clientes */
.hist-item      { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #1a1a1a; font-size: 13px; }
.hist-item:last-child { border-bottom: none; }
.hist-data      { color: #666; font-size: 12px; min-width: 90px; }
.hist-hora      { color: #888; font-size: 12px; min-width: 50px; }
.hist-serv      { color: #f0ebe3; flex: 1; }
.hist-status    { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; letter-spacing: 0.4px; text-transform: uppercase; }
.cl-empty       { text-align: center; padding: 50px 0; color: #333; font-size: 14px; }
.cl-empty-icon  { font-size: 40px; margin-bottom: 10px; }

/* Card de cliente (Início) */
.client-row     { display: flex; align-items: center; gap: 14px; padding: 13px 0; border-bottom: 1px solid #1a1a1a; }
.client-row:last-child { border-bottom: none; }
.cl-avatar      {
    width: 46px; height: 46px; border-radius: 50%;
    background: #1e1e1e; border: 1px solid #2a2a2a;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700; color: #d4a853; flex-shrink: 0;
}
.cl-name        { font-size: 16px; font-weight: 600; color: #f0ebe3; }
.cl-phone       { font-size: 13px; color: #555; margin-top: 2px; }

/* Próximo atendimento (Início) */
.next-card {
    background: #161616; border: 1px solid #2a2a2a;
    border-left: 4px solid #d4a853; border-radius: 12px; padding: 24px 28px;
}
.next-inner       { display: flex; align-items: flex-start; gap: 24px; }
.next-time-block  { min-width: 120px; }
.next-time        { font-size: 52px; font-weight: 800; color: #d4a853; line-height: 1; font-family: 'Playfair Display', serif; }
.next-time-end    { font-size: 14px; color: #444; margin-top: 5px; }
.next-name        { font-size: 26px; font-weight: 600; color: #f0ebe3; }
.next-service     { font-size: 16px; color: #888; margin-top: 5px; }
.next-phone       { font-size: 14px; color: #555; margin-top: 3px; }
.next-footer      { display: flex; align-items: center; gap: 14px; border-top: 1px solid #222; margin-top: 18px; padding-top: 14px; }
.no-next          { font-size: 16px; color: #444; padding: 20px 4px; }
.badge-conf       { font-size: 13px; padding: 5px 14px; border-radius: 20px; background: #1a2e1a; color: #4caf50; font-weight: 600; border: 1px solid #2a4a2a; }
.badge-atr        { font-size: 13px; padding: 5px 14px; border-radius: 20px; background: #2e1a1a; color: #e57373; font-weight: 600; border: 1px solid #4a2a2a; }

/* ════════════════════════════════════════
   SIDEBAR
   ════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid #1a1a1a !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-logo          { padding: 32px 24px 24px 24px; border-bottom: 1px solid #1e1e1e; margin-bottom: 8px; }
.sb-logo-row      { display: flex; align-items: center; gap: 10px; }
.sb-logo-icon     { width: 36px; height: 36px; background: #d4a853; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; line-height: 1; flex-shrink: 0; }
.sb-logo-title    { font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #f0ebe3; line-height: 1; }
.sb-logo-sub      { font-size: 11px; color: #3a3a3a; margin-top: 6px; text-transform: uppercase; letter-spacing: 1.5px; }
.sb-group         { padding: 20px 24px 8px 24px; }
.sb-group-label   { font-size: 10px; font-weight: 700; color: #2e2e2e; text-transform: uppercase; letter-spacing: 2.5px; }

.nav-item-wrap    {
    position: relative; display: flex; align-items: center; gap: 12px;
    padding: 13px 24px; margin: 2px 0;
    font-family: 'DM Sans', sans-serif; font-size: 15px; font-weight: 400;
    color: #555; pointer-events: none; z-index: 1;
}
.nav-item-wrap .nav-icon  { font-size: 17px; width: 22px; text-align: center; flex-shrink: 0; opacity: 0.35; }
.nav-item-wrap .nav-label { flex: 1; }
.nav-item-wrap.ativo      { background: rgba(212,168,83,0.08); border-left: 3px solid #d4a853; padding-left: 21px; color: #d4a853; font-weight: 500; }
.nav-item-wrap.ativo .nav-icon   { opacity: 1; }
.nav-item-wrap.principal         { color: #999; font-weight: 500; }
.nav-item-wrap.principal .nav-icon { opacity: 0.55; }
.nav-item-wrap.secundario        { color: #3d3d3d; font-size: 14px; }
.nav-item-wrap.secundario .nav-icon { opacity: 0.25; }

section[data-testid="stSidebar"] .stButton > button {
    position: relative !important; background: transparent !important;
    border: none !important; border-radius: 0 !important; box-shadow: none !important;
    color: transparent !important; font-size: 0 !important; padding: 0 !important;
    margin: 0 !important; width: 100% !important; height: 48px !important;
    cursor: pointer !important; transform: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(212,168,83,0.04) !important;
    transform: none !important; box-shadow: none !important;
}
section[data-testid="stSidebar"] .nav-item-wrap { margin-bottom: -48px; }

.sb-footer      { padding: 20px 24px; border-top: 1px solid #161616; margin-top: 20px; }
.sb-footer-text { font-size: 11px; color: #2a2a2a; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# ── Grupos de navegação ───────────────────────────────────────────────────────
GRUPOS = [
    {
        "label": "Principal",
        "itens": [
            {"key": "🏠 Início",        "icon": "🏠", "label": "Início",        "tipo": "principal"},
            {"key": "📋 Agenda do Dia",  "icon": "📋", "label": "Agenda do Dia", "tipo": "principal"},
            {"key": "📅 Agendar",        "icon": "📅", "label": "Agendar",       "tipo": "normal"},
        ],
    },
    {
        "label": "Gestão",
        "itens": [
            {"key": "👤 Clientes",   "icon": "👤", "label": "Clientes",   "tipo": "normal"},
            {"key": "📊 Dashboard",  "icon": "📊", "label": "Dashboard",  "tipo": "secundario"},
        ],
    },
]

PAGE_META = {
    "🏠 Início":        ("✂",  "Início"),
    "📋 Agenda do Dia": ("📋", "Agenda"),
    "📅 Agendar":       ("📅", "Novo Agendamento"),
    "👤 Clientes":      ("👤", "Clientes"),
    "📊 Dashboard":     ("📊", "Dashboard"),
}

if "pagina" not in st.session_state:
    st.session_state.pagina = "🏠 Início"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div class="sb-logo">
    <div class="sb-logo-row">
        <div class="sb-logo-icon">✂</div>
        <div class="sb-logo-title">BarberPro</div>
    </div>
    <div class="sb-logo-sub">Sistema de agendamento</div>
</div>
""", unsafe_allow_html=True)

    for grupo in GRUPOS:
        st.markdown(
            f'<div class="sb-group"><span class="sb-group-label">{grupo["label"]}</span></div>',
            unsafe_allow_html=True,
        )
        for item in grupo["itens"]:
            ativo   = st.session_state.pagina == item["key"]
            classes = "nav-item-wrap"
            if ativo:
                classes += " ativo"
            elif item["tipo"] == "principal":
                classes += " principal"
            elif item["tipo"] == "secundario":
                classes += " secundario"

            st.markdown(f"""
<div class="{classes}">
    <span class="nav-icon">{item['icon']}</span>
    <span class="nav-label">{item['label']}</span>
</div>""", unsafe_allow_html=True)

            if st.button("​", key=f"nav_{item['key']}", use_container_width=True):
                st.session_state.pagina = item["key"]
                st.rerun()

    st.markdown(
        '<div class="sb-footer"><div class="sb-footer-text">v1.0 — Projeto acadêmico</div></div>',
        unsafe_allow_html=True,
    )


# ── Cabeçalho padronizado ─────────────────────────────────────────────────────
def page_header(pagina: str):
    _, title = PAGE_META.get(pagina, ("", pagina))
    st.markdown(f"""
<div class="page-header">
    <div class="ph-title">{title}</div>
    <hr>
</div>
""", unsafe_allow_html=True)


# ── Roteamento ────────────────────────────────────────────────────────────────
pagina = st.session_state.pagina

if pagina == "🏠 Início":
    from pages.inicio import render
elif pagina == "📅 Agendar":
    from pages.agendar import render
elif pagina == "📋 Agenda do Dia":
    from pages.agenda_dia import render
elif pagina == "👤 Clientes":
    from pages.clientes import render
elif pagina == "📊 Dashboard":
    from pages.dashboard import render

page_header(pagina)
render()