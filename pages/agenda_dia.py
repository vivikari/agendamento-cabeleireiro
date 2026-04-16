import streamlit as st
from datetime import date, timedelta
from collections import defaultdict

from database import listar_agendamentos_por_data, listar_todos_agendamentos, atualizar_status, deletar_agendamento
from constants import STATUS_CONFIG, DIAS_PT_CURTO


# ── Componentes ───────────────────────────────────────────────────────────────

def _barra_progresso(ags: list):
    total       = len(ags)
    concluidos  = sum(1 for a in ags if a["status"] == "concluido")
    confirmados = sum(1 for a in ags if a["status"] == "confirmado")
    cancelados  = sum(1 for a in ags if a["status"] == "cancelado")
    pct         = int(concluidos / total * 100) if total else 0
    st.markdown(f"""
<div class="prog-wrap">
  <div class="prog-top">
    <span class="prog-label">{concluidos} de {total} concluídos</span>
    <span style="font-size:20px;">{pct}%</span>
  </div>
  <div class="prog-bg"><div class="prog-fill" style="width:{pct}%;"></div></div>
  <div class="prog-stats">
    <span class="prog-stat"><span class="stat-dot" style="background:#d4a853;"></span>{confirmados} confirmado(s)</span>
    <span class="prog-stat"><span class="stat-dot" style="background:#4caf50;"></span>{concluidos} concluído(s)</span>
    <span class="prog-stat"><span class="stat-dot" style="background:#e53935;"></span>{cancelados} cancelado(s)</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _card(ag: dict, idx):
    cfg = STATUS_CONFIG.get(ag["status"], STATUS_CONFIG["confirmado"])
    obs = f'<p class="ag-card-obs">📝 {ag["observacoes"]}</p>' if ag.get("observacoes") else ""
    st.markdown(f"""
<div class="ag-card" style="border-left: 3px solid {cfg['cor']};">
  <div class="ag-card-time">
    <span class="ag-time-txt">{ag['horario']}</span>
  </div>
  <div class="ag-card-body">
    <div class="ag-card-top">
      <span class="ag-card-name">{ag['cliente_nome']}</span>
      <span class="ag-status-pill" style="color:{cfg['cor']};background:{cfg['bg']};border:1px solid {cfg['cor']}33;">
        {cfg['label']}
      </span>
    </div>
    <p class="ag-card-meta">✂️ {ag['servico']} &nbsp;·&nbsp; 📞 {ag.get('telefone') or '—'}</p>
    {obs}
  </div>
</div>
""", unsafe_allow_html=True)

    changed = False
    if ag["status"] in ("cancelado", "concluido"):
        if st.button("🗑️ Excluir", key=f"del_{ag['id']}_{idx}", use_container_width=True):
            deletar_agendamento(ag["id"])
            changed = True
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Concluir", key=f"ok_{ag['id']}_{idx}", use_container_width=True):
                atualizar_status(ag["id"], "concluido")
                changed = True
        with c2:
            if st.button("❌ Cancelar", key=f"cx_{ag['id']}_{idx}", use_container_width=True):
                atualizar_status(ag["id"], "cancelado")
                changed = True
        with c3:
            if st.button("🗑️ Excluir", key=f"del2_{ag['id']}_{idx}", use_container_width=True):
                deletar_agendamento(ag["id"])
                changed = True

    if changed:
        st.toast("Agendamento atualizado!", icon="✅")
        st.rerun()


def _init_state():
    defaults = {
        "agenda_data_sel":      date.today(),
        "agenda_filtro_status": ["confirmado", "concluido", "cancelado"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    _init_state()

    hoje  = date.today()
    todos = listar_todos_agendamentos()

    # ── Filtros ──
    col_modo, col_data, col_status = st.columns([3, 2, 3])
    with col_modo:
        modo = st.radio(
            "Visualizar",
            ["Hoje", "Próximos 7 dias", "Data específica", "Todos"],
            horizontal=True,
            key="agenda_modo_radio",
        )
    with col_data:
        data_especifica = None
        if modo == "Data específica":
            data_especifica = st.date_input(
                "Data",
                value=st.session_state.agenda_data_sel,
                min_value=date(2020, 1, 1),
                max_value=date(2030, 12, 31),
                key="agenda_date_picker",
            )
            st.session_state.agenda_data_sel = data_especifica
    with col_status:
        filtro_status = st.multiselect(
            "Status",
            ["confirmado", "concluido", "cancelado"],
            default=st.session_state.agenda_filtro_status,
            format_func=lambda s: STATUS_CONFIG[s]["label"],
            key="agenda_status_filter",
        )
        st.session_state.agenda_filtro_status = filtro_status

    st.markdown("---")

    # ── Seleção de período ──
    if modo == "Hoje":
        ags_raw           = listar_agendamentos_por_data(hoje.isoformat())
        titulo            = f"Hoje — {hoje.strftime('%d/%m/%Y')}"
        mostrar_progresso = True
    elif modo == "Próximos 7 dias":
        fim               = hoje + timedelta(days=7)
        ags_raw           = [a for a in todos if hoje.isoformat() <= a["data"] <= fim.isoformat()]
        titulo            = "Próximos 7 dias"
        mostrar_progresso = False
    elif modo == "Data específica" and data_especifica:
        ags_raw           = listar_agendamentos_por_data(data_especifica.isoformat())
        titulo            = "Hoje" if data_especifica == hoje else data_especifica.strftime("%d/%m/%Y")
        mostrar_progresso = True
    else:
        ags_raw           = todos
        titulo            = "Todos os agendamentos"
        mostrar_progresso = False

    ags_filtrados = [a for a in ags_raw if a["status"] in (filtro_status or [])]

    # ── Cabeçalho da lista ──
    col_t, col_c = st.columns([5, 1])
    with col_t:
        st.markdown(f"### {titulo}")
    with col_c:
        st.markdown(
            f"<div style='text-align:right;padding-top:8px;font-size:13px;color:#555;'>"
            f"{len(ags_filtrados)} ag.</div>",
            unsafe_allow_html=True,
        )

    # Barra de progresso só aparece quando há dados (consistência com o contador acima)
    if mostrar_progresso and ags_filtrados:
        _barra_progresso(ags_filtrados)

    if not ags_filtrados:
        st.markdown(
            '<div class="ag-empty"><div class="ag-empty-icon">📭</div>'
            'Nenhum agendamento para este filtro.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Agrupamento por data ──
    grupos: dict = defaultdict(list)
    for ag in ags_filtrados:
        grupos[ag["data"]].append(ag)

    for data_str in sorted(grupos.keys()):
        grupo = grupos[data_str]
        try:
            d = date.fromisoformat(data_str)
            if d == hoje:
                label_data = f"Hoje — {d.strftime('%d/%m/%Y')}"
            elif d == hoje + timedelta(days=1):
                label_data = f"Amanhã — {d.strftime('%d/%m/%Y')}"
            else:
                label_data = f"{DIAS_PT_CURTO[d.weekday()]}, {d.strftime('%d/%m/%Y')}"
        except Exception:
            label_data = data_str

        if len(grupos) > 1:
            st.markdown(f"""
<div class="date-sep">
  <span class="date-sep-badge">{label_data}</span>
  <div class="date-sep-line"></div>
  <span class="date-sep-count">{len(grupo)} ag.</span>
</div>""", unsafe_allow_html=True)

        for i, ag in enumerate(sorted(grupo, key=lambda x: x["horario"])):
            _card(ag, f"{data_str}_{i}")