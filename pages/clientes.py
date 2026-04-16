import streamlit as st
from collections import defaultdict

from database import listar_clientes, buscar_cliente_por_nome, criar_cliente, deletar_cliente, historico_todos_clientes
from constants import STATUS_CONFIG


# ── Helpers ───────────────────────────────────────────────────────────────────

def _status_pill(status: str) -> str:
    cfg = STATUS_CONFIG.get(status, {"cor": "#888", "label": status})
    cor = cfg["cor"]
    return (
        f'<span class="hist-status" '
        f'style="color:{cor};background:{cor}22;border:1px solid {cor}44;">'
        f'{cfg["label"]}</span>'
    )


def _render_historico(historico: list):
    if not historico:
        st.markdown(
            "<p style='color:#444;font-size:13px;padding:10px 0;'>Nenhum atendimento registrado ainda.</p>",
            unsafe_allow_html=True,
        )
        return
    for h in historico[:8]:
        st.markdown(
            f'<div class="hist-item">'
            f'<span class="hist-data">📅 {h["data"]}</span>'
            f'<span class="hist-hora">🕐 {h["horario"]}</span>'
            f'<span class="hist-serv">✂️ {h["servico"]}</span>'
            f'{_status_pill(h["status"])}'
            f'</div>',
            unsafe_allow_html=True,
        )
    if len(historico) > 8:
        st.caption(f"… e mais {len(historico) - 8} atendimento(s) anteriores.")


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    aba1, aba2 = st.tabs(["📋  Lista de clientes", "➕  Cadastrar cliente"])

    with aba1:
        col_busca, col_total = st.columns([4, 1])
        with col_busca:
            busca = st.text_input("", placeholder="🔍  Buscar cliente por nome...", key="cl_busca")
        with col_total:
            todos = listar_clientes()
            st.markdown(
                f"<div style='text-align:right;padding-top:32px;font-size:13px;color:#555;'>"
                f"{len(todos)} total</div>",
                unsafe_allow_html=True,
            )

        clientes = buscar_cliente_por_nome(busca) if busca else todos

        if not clientes:
            st.markdown(
                '<div class="cl-empty"><div class="cl-empty-icon">🔍</div>'
                'Nenhum cliente encontrado.</div>',
                unsafe_allow_html=True,
            )
        else:
            if busca:
                st.markdown(
                    f'<p style="font-size:13px;color:#555;margin-bottom:12px;">'
                    f'{len(clientes)} resultado(s) para '
                    f'<b style="color:#f0ebe3;">&ldquo;{busca}&rdquo;</b></p>',
                    unsafe_allow_html=True,
                )

            # Uma única query para todos os históricos — evita N queries no loop
            todos_historicos_raw = historico_todos_clientes()
            hist_por_cliente: dict = defaultdict(list)
            for h in todos_historicos_raw:
                hist_por_cliente[h["cliente_id"]].append(h)

            for cl in clientes:
                hist    = hist_por_cliente[cl["id"]]
                n_atend = len(hist)
                ultimo  = hist[0]["data"] if hist else None
                tel_str = cl.get("telefone") or "sem telefone"
                badge   = f"  ·  {n_atend} atend." if n_atend else "  ·  sem atendimentos"
                ult_str = f"  ·  último: {ultimo}" if ultimo else ""
                label_exp = f"{cl['nome']}   |   📞 {tel_str}{badge}{ult_str}"

                with st.expander(label_exp, expanded=False):
                    ini = cl.get("criado_em", "")[:10]
                    st.markdown(
                        f"<small style='color:#555;'>Cadastrado em: {ini}</small>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("---")
                    st.markdown(f"**📋 Histórico de atendimentos** ({n_atend})")
                    _render_historico(hist)
                    st.markdown("<br>", unsafe_allow_html=True)

                    col_ag, col_del = st.columns([3, 1])
                    with col_ag:
                        if st.button(
                            "📅 Novo agendamento para este cliente",
                            key=f"ag_cl_{cl['id']}",
                            use_container_width=True,
                        ):
                            st.session_state.ag_cliente_id   = cl["id"]
                            st.session_state.ag_cliente_nome = cl["nome"]
                            st.session_state.ag_cliente_tel  = cl.get("telefone") or ""
                            st.session_state.ag_modo         = "existente"
                            st.session_state.ag_passo        = 2
                            st.session_state.ag_trocando     = False
                            st.session_state.pagina          = "📅 Agendar"
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Excluir", key=f"del_cl_{cl['id']}", use_container_width=True):
                            deletar_cliente(cl["id"])
                            st.toast(f"Cliente {cl['nome']} excluído.", icon="🗑️")
                            st.rerun()

    with aba2:
        st.markdown("<br>", unsafe_allow_html=True)
        col_form, _ = st.columns([2, 1])
        with col_form:
            st.markdown("### ✨ Novo cliente")
            st.markdown("---")
            nome     = st.text_input("Nome completo *", placeholder="Ex: João Silva", key="cad_nome")
            telefone = st.text_input("Telefone", placeholder="Ex: 11999998888", key="cad_tel")
            if nome.strip():
                st.markdown(
                    f"<p style='font-size:13px;color:#555;margin-top:-8px;'>"
                    f"Será cadastrado: <b style='color:#f0ebe3;'>{nome.strip()}</b></p>",
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Cadastrar cliente", use_container_width=True):
                if not nome.strip():
                    st.error("O nome é obrigatório.")
                else:
                    criar_cliente(nome.strip(), telefone.strip())
                    st.toast(f"Cliente {nome.strip()} cadastrado!", icon="✅")
                    st.balloons()
                    for k in ["cad_nome", "cad_tel"]:
                        st.session_state.pop(k, None)
                    st.rerun()