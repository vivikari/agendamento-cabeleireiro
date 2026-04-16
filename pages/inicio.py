import streamlit as st
from datetime import date, datetime

from database import listar_agendamentos_por_data, listar_clientes
from constants import PRECO_SERVICOS, MESES_PT_MIN, DIAS_PT, STATUS_CONFIG


def render():
    hoje  = date.today()
    ags_hoje = listar_agendamentos_por_data(hoje.isoformat())
    clientes  = listar_clientes()

    confirmados = [a for a in ags_hoje if a["status"] == "confirmado"]
    concluidos  = [a for a in ags_hoje if a["status"] == "concluido"]
    proximo     = confirmados[0] if confirmados else None
    faturamento = sum(PRECO_SERVICOS.get(a["servico"], 0) for a in concluidos)

    hora_atual = datetime.now().hour
    saudacao   = "Bom dia" if hora_atual < 12 else ("Boa tarde" if hora_atual < 18 else "Boa noite")
    dia_semana = DIAS_PT[hoje.weekday()]
    data_br    = f"{dia_semana}, {hoje.day} de {MESES_PT_MIN[hoje.month]} de {hoje.year}"

    st.markdown(
        f"<p style='color:#555;font-size:15px;margin-top:-12px;margin-bottom:24px;'>"
        f"👋 {saudacao} &nbsp;·&nbsp; {data_br}</p>",
        unsafe_allow_html=True,
    )

    col_esq, col_dir = st.columns([3, 2], gap="large")

    # ── Coluna esquerda ──────────────────────────────────────────────────────
    with col_esq:
        st.markdown('<div class="secao-titulo first">⚡ Próximo atendimento</div>', unsafe_allow_html=True)

        if proximo:
            try:
                h, m        = map(int, proximo["horario"].split(":"))
                m_fim       = m + 40
                horario_fim = f"{h + m_fim // 60:02d}:{m_fim % 60:02d}"
            except Exception:
                horario_fim = "—"

            cfg      = STATUS_CONFIG.get(proximo["status"], STATUS_CONFIG["confirmado"])
            telefone = proximo.get("telefone") or "—"
            badge    = (
                f'<span style="font-size:13px;padding:5px 14px;border-radius:20px;'
                f'background:#1a2e1a;color:#4caf50;font-weight:600;border:1px solid #2a4a2a;">'
                f'{cfg["label"]}</span>'
            )

            st.markdown(f"""
<div class="next-card">
    <div class="next-inner">
        <div class="next-time-block">
            <div class="next-time">{proximo['horario']}</div>
            <div class="next-time-end">até {horario_fim}</div>
        </div>
        <div>
            <div class="next-name">{proximo['cliente_nome']}</div>
            <div class="next-service">✂️ {proximo['servico']}</div>
            <div class="next-phone">📞 {telefone}</div>
        </div>
    </div>
    <div class="next-footer">{badge}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="no-next">Nenhum atendimento pendente hoje.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="secao-titulo">📊 Resumo do dia</div>', unsafe_allow_html=True)
        total = len(confirmados) + len(concluidos)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="destaque-card">'
                f'<div class="destaque-icon">📅</div>'
                f'<div class="destaque-val">{total}</div>'
                f'<div class="destaque-label">Total hoje</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="destaque-card">'
                f'<div class="destaque-icon">✅</div>'
                f'<div class="destaque-val">{len(concluidos)}</div>'
                f'<div class="destaque-label">Concluídos</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="destaque-card">'
                f'<div class="destaque-icon">💰</div>'
                f'<div class="destaque-val">R$ {faturamento}</div>'
                f'<div class="destaque-label">Faturamento</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="secao-titulo">👥 Clientes recentes</div>', unsafe_allow_html=True)
        if clientes:
            html = ""
            for cl in clientes[:4]:
                html += (
                    f'<div class="client-row">'
                    f'<div class="cl-avatar">{cl["nome"][0].upper()}</div>'
                    f'<div>'
                    f'<div class="cl-name">{cl["nome"]}</div>'
                    f'<div class="cl-phone">{cl.get("telefone") or "—"}</div>'
                    f'</div></div>'
                )
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#444;font-size:15px;">Nenhum cliente cadastrado.</span>',
                unsafe_allow_html=True,
            )

    # ── Coluna direita ───────────────────────────────────────────────────────
    with col_dir:
        st.markdown('<div class="secao-titulo first">⚡ Ações rápidas</div>', unsafe_allow_html=True)

        if st.button("📅 Novo agendamento", key="btn_agendar", use_container_width=True):
            st.session_state.pagina = "📅 Agendar"
            st.rerun()
        if st.button("👤 Novo cliente", key="btn_cliente", use_container_width=True):
            st.session_state.pagina = "👤 Clientes"
            st.rerun()
        if st.button("📋 Ver agenda de hoje", key="btn_agenda", use_container_width=True):
            st.session_state.pagina = "📋 Agenda do Dia"
            st.rerun()

        st.markdown('<div class="secao-titulo">📅 Agenda de hoje</div>', unsafe_allow_html=True)
        if ags_hoje:
            html = ""
            for ag in ags_hoje[:6]:
                cfg       = STATUS_CONFIG.get(ag["status"], STATUS_CONFIG["confirmado"])
                extra_cls = " current" if (ag["status"] == "confirmado" and ag == proximo) else ""
                html += (
                    f'<div class="ag-card{extra_cls}" style="border-left:3px solid {cfg["cor"]};">'
                    f'<div class="ag-card-time"><span class="ag-time-txt">{ag["horario"]}</span></div>'
                    f'<div class="ag-card-body">'
                    f'<div class="ag-card-top">'
                    f'<span class="ag-card-name">{ag["cliente_nome"]}</span>'
                    f'<span class="ag-status-pill" '
                    f'style="color:{cfg["cor"]};background:{cfg["bg"]};border:1px solid {cfg["cor"]}33;">'
                    f'{cfg["label"]}</span>'
                    f'</div>'
                    f'<p class="ag-card-meta">✂️ {ag["servico"]}</p>'
                    f'</div></div>'
                )
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="color:#444;font-size:15px;">Sem agendamentos hoje.</span>',
                unsafe_allow_html=True,
            )