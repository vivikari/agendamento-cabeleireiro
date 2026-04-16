import streamlit as st
from datetime import date, timedelta

from database import listar_clientes, criar_cliente, criar_agendamento, horarios_ocupados
from constants import SERVICOS, SERVICO_ICONS, PRECO_SERVICOS, TODOS_HORARIOS


# ── Helpers visuais ───────────────────────────────────────────────────────────

def _step_bar(passo: int):
    labels = ["1 · Cliente", "2 · Serviço & Data", "3 · Confirmar"]
    partes = []
    for i, l in enumerate(labels):
        n = i + 1
        if n < passo:
            cor, bg, txt = "#4caf50", "rgba(76,175,80,0.08)", f"✓ {l}"
        elif n == passo:
            cor, bg, txt = "#d4a853", "rgba(212,168,83,0.10)", l
        else:
            cor, bg, txt = "#333", "#111", l
        borda_r = "" if i == len(labels) - 1 else "border-right:1px solid #2a2a2a;"
        partes.append(
            f'<div style="flex:1;padding:12px 8px;text-align:center;font-size:12px;'
            f'font-weight:600;color:{cor};background:{bg};{borda_r}">{txt}</div>'
        )
    st.markdown(
        f'<div style="display:flex;border:1px solid #2a2a2a;border-radius:10px;'
        f'overflow:hidden;margin-bottom:28px;">{"".join(partes)}</div>',
        unsafe_allow_html=True,
    )


def _lbl_sec(texto: str):
    st.markdown(
        f"<p style='font-size:11px;font-weight:700;color:#555;text-transform:uppercase;"
        f"letter-spacing:1.2px;margin:0 0 8px;'>{texto}</p>",
        unsafe_allow_html=True,
    )


def _card_cliente(nome: str, telefone: str = "", novo: bool = False):
    badge = ' · <span style="color:#d4a853;">novo cadastro</span>' if novo else ""
    st.markdown(f"""
<div style="background:#161616;border:1px solid #2a2a2a;border-radius:10px;
            padding:14px 18px;margin:10px 0;display:flex;align-items:center;gap:12px;">
  <div style="width:38px;height:38px;border-radius:50%;background:rgba(212,168,83,0.15);
              border:1px solid #d4a853;display:flex;align-items:center;justify-content:center;
              font-size:16px;font-weight:700;color:#d4a853;flex-shrink:0;">
    {nome[0].upper()}
  </div>
  <div>
    <div style="font-size:15px;font-weight:600;color:#f0ebe3;">{nome}</div>
    <div style="font-size:12px;color:#666;margin-top:2px;">📞 {telefone or '—'}{badge}</div>
  </div>
</div>""", unsafe_allow_html=True)


def _init_state():
    defaults = {
        "ag_modo":         "existente",
        "ag_cliente_id":   None,
        "ag_cliente_nome": "",
        "ag_cliente_tel":  "",
        "ag_servico_idx":  0,
        "ag_horario":      None,
        "ag_data":         date.today(),
        "ag_obs":          "",
        "ag_passo":        1,
        "ag_trocando":     False,   # flag: usuário pediu para trocar cliente
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Passos ────────────────────────────────────────────────────────────────────

def _passo1(nomes_map: dict):
    st.markdown("### 👤 Quem vai ser atendido?")

    # Mostra cliente pré-selecionado SOMENTE se tiver um ID válido E não estiver em modo "trocar"
    tem_cliente = (
        st.session_state.ag_cliente_id
        and st.session_state.ag_cliente_id != "novo"
        and not st.session_state.ag_trocando
    )

    if tem_cliente:
        st.markdown(
            "<p style='font-size:13px;color:#d4a853;margin-bottom:4px;'>"
            "✓ Cliente já selecionado:</p>",
            unsafe_allow_html=True,
        )
        _card_cliente(st.session_state.ag_cliente_nome, st.session_state.ag_cliente_tel)
        st.markdown("<br>", unsafe_allow_html=True)
        col_manter, col_trocar = st.columns(2)
        with col_manter:
            if st.button("Continuar com este cliente →", use_container_width=True):
                st.session_state.ag_trocando = False
                st.session_state.ag_passo    = 2
                st.rerun()
        with col_trocar:
            if st.button("Trocar cliente", use_container_width=True):
                st.session_state.ag_cliente_id   = None
                st.session_state.ag_cliente_nome = ""
                st.session_state.ag_cliente_tel  = ""
                st.session_state.ag_trocando     = True
                st.rerun()
        return

    # ── Seleção normal (sem pré-seleção ou após "Trocar") ──
    modo = st.radio("", ["Cliente existente", "Novo cliente"], horizontal=True, key="ag_modo_radio")
    st.markdown("<br>", unsafe_allow_html=True)

    if modo == "Cliente existente":
        if not nomes_map:
            st.warning("Nenhum cliente cadastrado. Cadastre um novo.")
        else:
            busca = st.text_input("🔍 Buscar cliente", placeholder="Digite o nome...")
            lista = [n for n in nomes_map if busca.lower() in n.lower()] if busca else list(nomes_map.keys())
            if lista:
                nome_sel = st.selectbox("Selecione", lista)
                cl = nomes_map[nome_sel]
                _card_cliente(cl["nome"], cl.get("telefone") or "")
                st.session_state.ag_cliente_id   = cl["id"]
                st.session_state.ag_cliente_nome = cl["nome"]
                st.session_state.ag_cliente_tel  = cl.get("telefone") or ""
            else:
                st.info("Nenhum cliente corresponde à busca.")
                st.session_state.ag_cliente_id = None
    else:
        col_n, col_t = st.columns(2)
        with col_n:
            novo_nome = st.text_input("Nome completo *", placeholder="Ex: João Silva")
        with col_t:
            novo_tel = st.text_input("Telefone", placeholder="11999998888")
        if novo_nome.strip():
            _card_cliente(novo_nome.strip(), novo_tel.strip(), novo=True)
            st.session_state.ag_cliente_nome = novo_nome.strip()
            st.session_state.ag_cliente_tel  = novo_tel.strip()
            st.session_state.ag_cliente_id   = "novo"
        else:
            st.session_state.ag_cliente_id = None

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Próximo →", use_container_width=True):
        if not st.session_state.ag_cliente_id:
            st.error("Selecione ou preencha um cliente para continuar.")
        else:
            st.session_state.ag_trocando = False
            st.session_state.ag_passo    = 2
            st.rerun()


def _passo2():
    serv_idx = st.session_state.ag_servico_idx
    st.markdown("### ✂️ Serviço & Horário")

    # ── Serviço ──
    _lbl_sec("Escolha o serviço")
    row1 = st.columns(3)
    row2 = st.columns(3)
    for i, col in enumerate([*row1, *row2]):
        s       = SERVICOS[i]
        ativo   = i == serv_idx
        # Destaque visual mais claro para o serviço selecionado
        borda   = "border: 2px solid #d4a853 !important;" if ativo else ""
        prefixo = "✓ " if ativo else ""
        with col:
            if st.button(
                f"{prefixo}{SERVICO_ICONS[s]} {s} — R$ {PRECO_SERVICOS[s]}",
                key=f"serv_{i}",
                use_container_width=True,
            ):
                st.session_state.ag_servico_idx = i
                st.rerun()

    s_ativo = SERVICOS[serv_idx]
    st.markdown(
        f"<p style='font-size:13px;color:#d4a853;margin:8px 0 0;'>"
        f"✓ Selecionado: <b>{SERVICO_ICONS[s_ativo]} {s_ativo} — R$ {PRECO_SERVICOS[s_ativo]}</b></p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data e Observações ──
    col_d, col_obs = st.columns(2)
    with col_d:
        _lbl_sec("Data do atendimento")
        data_anterior = st.session_state.ag_data
        data_sel = st.date_input(
            "Data",
            min_value=date.today(),
            max_value=date.today() + timedelta(days=60),
            value=st.session_state.ag_data,
            key="ag_date",
        )
        st.session_state.ag_data = data_sel
    with col_obs:
        _lbl_sec("Observações (opcional)")
        obs = st.text_area(
            "Observações",
            value=st.session_state.ag_obs,
            height=104,
            placeholder="Ex: cliente prefere tesoura...",
            key="ag_obs_input",
        )
        st.session_state.ag_obs = obs

    # ── Horários ──
    st.markdown("<br>", unsafe_allow_html=True)
    _lbl_sec("Horário disponível")
    data_str    = data_sel.isoformat()
    ocupados    = horarios_ocupados(data_str)
    disponiveis = [h for h in TODOS_HORARIOS if h not in ocupados]

    if not disponiveis:
        st.error("⚠️ Sem horários disponíveis nessa data. Escolha outra data.")
        st.session_state.ag_horario = None
    else:
        # Detecta se o horário atual ficou indisponível por mudança de data
        horario_atual = st.session_state.ag_horario
        if horario_atual not in disponiveis:
            st.session_state.ag_horario = disponiveis[0]
            # Avisa o usuário somente se já havia um horário selecionado antes
            if horario_atual is not None and data_sel != data_anterior:
                st.warning(
                    f"O horário {horario_atual} não está disponível nessa data. "
                    f"Selecionamos {disponiveis[0]} automaticamente — confirme se está correto."
                )

        horario_ativ = st.session_state.ag_horario
        cols_h = st.columns(5)
        for i, h in enumerate(TODOS_HORARIOS):
            with cols_h[i % 5]:
                if h in ocupados:
                    st.button(h, key=f"h_{h}", disabled=True, use_container_width=True)
                else:
                    prefixo = "✓ " if h == horario_ativ else ""
                    if st.button(f"{prefixo}{h}", key=f"h_{h}", use_container_width=True):
                        st.session_state.ag_horario = h
                        st.rerun()

        st.markdown(
            f"<p style='font-size:13px;color:#d4a853;margin-top:4px;'>"
            f"✓ Horário selecionado: <b>{horario_ativ}</b></p>",
            unsafe_allow_html=True,
        )

    # ── Navegação ──
    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_p = st.columns(2)
    with col_v:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.ag_passo = 1
            st.rerun()
    with col_p:
        if st.button("Revisar →", use_container_width=True):
            if not st.session_state.ag_horario:
                st.error("Escolha um horário disponível.")
            else:
                st.session_state.ag_passo = 3
                st.rerun()


def _passo3():
    st.markdown("### 📋 Revisar e confirmar")
    servico_sel = SERVICOS[st.session_state.ag_servico_idx]
    data_br     = st.session_state.ag_data.strftime("%d/%m/%Y")
    preco       = PRECO_SERVICOS.get(servico_sel, 0)
    obs_row     = ""
    if st.session_state.ag_obs:
        obs_row = (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:8px 0;border-bottom:1px solid #1e1e1e;font-size:14px;">'
            f'<span style="color:#666;">📝 Obs</span>'
            f'<span style="color:#888;font-style:italic;">{st.session_state.ag_obs}</span></div>'
        )

    st.markdown(f"""
<div style="background:#161616;border:1px solid #2a2a2a;border-left:4px solid #d4a853;
            border-radius:12px;padding:18px 22px;margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e1e1e;font-size:14px;">
    <span style="color:#666;">👤 Cliente</span>
    <span style="color:#f0ebe3;font-weight:600;">{st.session_state.ag_cliente_nome}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e1e1e;font-size:14px;">
    <span style="color:#666;">✂️ Serviço</span>
    <span style="color:#f0ebe3;font-weight:600;">{SERVICO_ICONS.get(servico_sel,'')} {servico_sel}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e1e1e;font-size:14px;">
    <span style="color:#666;">📅 Data</span>
    <span style="color:#f0ebe3;font-weight:600;">{data_br}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e1e1e;font-size:14px;">
    <span style="color:#666;">🕐 Horário</span>
    <span style="color:#f0ebe3;font-weight:600;">{st.session_state.ag_horario}</span>
  </div>
  {obs_row}
  <div style="display:flex;justify-content:space-between;padding:12px 0 0;border-top:1px solid #2a2a2a;margin-top:4px;">
    <span style="color:#f0ebe3;font-weight:700;">Valor total</span>
    <span style="color:#d4a853;font-size:20px;font-weight:700;">R$ {preco}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    col_v, col_c = st.columns(2)
    with col_v:
        if st.button("← Editar", use_container_width=True):
            st.session_state.ag_passo = 2
            st.rerun()
    with col_c:
        if st.button("✅ Confirmar Agendamento", use_container_width=True):
            cliente_id = st.session_state.ag_cliente_id
            if cliente_id == "novo":
                cliente_id = criar_cliente(
                    st.session_state.ag_cliente_nome,
                    st.session_state.ag_cliente_tel,
                )
            criar_agendamento(
                cliente_id,
                servico_sel,
                st.session_state.ag_data.isoformat(),
                st.session_state.ag_horario,
                st.session_state.ag_obs,
            )
            horario_ok  = st.session_state.ag_horario
            nome_ok     = st.session_state.ag_cliente_nome
            # Limpa estado do wizard
            for k in ["ag_cliente_id", "ag_cliente_nome", "ag_cliente_tel",
                       "ag_servico_idx", "ag_horario", "ag_obs", "ag_passo", "ag_trocando"]:
                st.session_state.pop(k, None)

            st.toast(f"Agendamento confirmado para {nome_ok} às {horario_ok}!", icon="✅")
            st.balloons()
            st.rerun()


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    _init_state()

    clientes  = listar_clientes()
    nomes_map = {c["nome"]: c for c in clientes}

    _step_bar(st.session_state.ag_passo)

    if st.session_state.ag_passo == 1:
        _passo1(nomes_map)
    elif st.session_state.ag_passo == 2:
        _passo2()
    elif st.session_state.ag_passo == 3:
        _passo3()