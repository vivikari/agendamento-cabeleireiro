import calendar

import pandas as pd
import plotly.express as px
import streamlit as st

from database import listar_todos_agendamentos
from constants import PRECO_SERVICOS, CORES_SERVICOS, MESES_PT

PLOT_LAYOUT = dict(
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#888", size=12),
    margin=dict(l=10, r=10, t=10, b=10),
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mes_anterior(ano: int, mes: int):
    return (ano - 1, 12) if mes == 1 else (ano, mes - 1)


def _faturamento(df: pd.DataFrame) -> int:
    return int(df[df["status"] == "concluido"]["faturamento"].sum())


def _delta(atual: int, anterior: int):
    if anterior == 0:
        return None
    return f"{'+' if atual >= anterior else ''}{((atual - anterior) / anterior * 100):.0f}%"


def _destaque_card(label: str, valor: str, sub: str = "") -> str:
    sub_html = f'<div class="destaque-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="destaque-card">'
        f'<div class="destaque-label">{label}</div>'
        f'<div class="destaque-val">{valor}</div>'
        f'{sub_html}'
        f'</div>'
    )


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    todos = listar_todos_agendamentos()
    if not todos:
        st.info("Nenhum dado disponível ainda. Faça alguns agendamentos para ver as estatísticas!")
        return

    df = pd.DataFrame(todos)
    df["data"] = pd.to_datetime(df["data"])
    df["faturamento"] = df.apply(
        lambda r: PRECO_SERVICOS.get(r["servico"], 0) if r["status"] == "concluido" else 0,
        axis=1,
    )

    # ── Filtros de período ──
    col_f1, col_f2, _ = st.columns([1, 1, 2])
    with col_f1:
        ano = st.selectbox(
            "Ano",
            sorted(df["data"].dt.year.unique(), reverse=True),
            label_visibility="collapsed",
        )
    with col_f2:
        meses_disp = sorted(df[df["data"].dt.year == ano]["data"].dt.month.unique())
        mes = st.selectbox(
            "Mês",
            meses_disp,
            format_func=lambda m: MESES_PT[m],
            label_visibility="collapsed",
        )

    df_mes = df[(df["data"].dt.year == ano) & (df["data"].dt.month == mes)]
    if df_mes.empty:
        st.warning("Nenhum dado para o período selecionado.")
        return

    ano_ant, mes_ant = _mes_anterior(ano, mes)
    df_ant = df[(df["data"].dt.year == ano_ant) & (df["data"].dt.month == mes_ant)]

    # ── Métricas calculadas uma vez ──
    total_mes      = len(df_mes)
    concluidos_mes = len(df_mes[df_mes["status"] == "concluido"])
    cancelados_mes = len(df_mes[df_mes["status"] == "cancelado"])
    fat_mes        = _faturamento(df_mes)
    taxa_mes       = int(concluidos_mes / total_mes * 100) if total_mes else 0
    total_ant      = len(df_ant)
    fat_ant        = _faturamento(df_ant)
    taxa_ant       = int(len(df_ant[df_ant["status"] == "concluido"]) / total_ant * 100) if total_ant else 0
    ticket_medio   = int(fat_mes / concluidos_mes) if concluidos_mes else 0
    cliente_top    = (
        df_mes[df_mes["status"] == "concluido"]["cliente_nome"].value_counts().idxmax()
        if concluidos_mes > 0 else "—"
    )
    visitas_top = (
        df_mes[df_mes["status"] == "concluido"]["cliente_nome"].value_counts().max()
        if concluidos_mes > 0 else 0
    )

    # ── Resumo do mês ──
    st.markdown('<div class="secao-titulo">📈 Resumo do mês</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Atendimentos",      total_mes,        delta=_delta(total_mes, total_ant))
    c2.metric("Concluídos",        concluidos_mes)
    c3.metric("Cancelados",        cancelados_mes)
    c4.metric("Taxa de conclusão", f"{taxa_mes}%",   delta=_delta(taxa_mes, taxa_ant))

    st.markdown("---")

    # ── Financeiro ──
    st.markdown('<div class="secao-titulo">💰 Financeiro</div>', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns(3)
    delta_fat = _delta(fat_mes, fat_ant)
    with cf1:
        st.markdown(_destaque_card(
            "💵 Faturamento do mês",
            f"R$ {fat_mes}",
            f"vs mês anterior: {delta_fat}" if delta_fat else "Primeiro mês com dados",
        ), unsafe_allow_html=True)
    with cf2:
        st.markdown(_destaque_card(
            "🎯 Ticket médio",
            f"R$ {ticket_medio}",
            "por atendimento concluído",
        ), unsafe_allow_html=True)
    with cf3:
        st.markdown(_destaque_card(
            "⭐ Cliente do mês",
            cliente_top,
            f"{visitas_top} visita(s) no mês",
        ), unsafe_allow_html=True)

    st.markdown("---")

    # ── Gráficos ──
    st.markdown('<div class="secao-titulo">📊 Análises</div>', unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(
            "<p style='color:#888;font-size:13px;font-weight:600;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:8px;'>Serviços mais realizados</p>",
            unsafe_allow_html=True,
        )
        serv_count = df_mes["servico"].value_counts().reset_index()
        serv_count.columns = ["Serviço", "Quantidade"]
        fig1 = px.bar(serv_count, x="Quantidade", y="Serviço", orientation="h", template="plotly_dark")
        fig1.update_traces(marker_color=[CORES_SERVICOS.get(s, "#888") for s in serv_count["Serviço"]])
        fig1.update_layout(**PLOT_LAYOUT, height=260, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.markdown(
            "<p style='color:#888;font-size:13px;font-weight:600;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:8px;'>Faturamento por serviço</p>",
            unsafe_allow_html=True,
        )
        df_fat_serv = (
            df_mes[df_mes["status"] == "concluido"]
            .groupby("servico")["faturamento"]
            .sum()
            .reset_index()
            .sort_values("faturamento", ascending=False)
        )
        df_fat_serv.columns = ["Serviço", "Faturamento"]
        fig2 = px.bar(df_fat_serv, x="Faturamento", y="Serviço", orientation="h", template="plotly_dark")
        fig2.update_traces(marker_color=[CORES_SERVICOS.get(s, "#888") for s in df_fat_serv["Serviço"]])
        fig2.update_layout(**PLOT_LAYOUT, height=260, yaxis=dict(autorange="reversed"))
        fig2.update_xaxes(tickprefix="R$ ")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "<p style='color:#888;font-size:13px;font-weight:600;text-transform:uppercase;"
        "letter-spacing:1px;margin-bottom:8px;'>Atendimentos por dia do mês</p>",
        unsafe_allow_html=True,
    )
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    todos_dias  = pd.DataFrame({"dia": range(1, dias_no_mes + 1)})
    df_dia      = df_mes.copy()
    df_dia["dia"] = df_dia["data"].dt.day
    por_dia = (
        todos_dias
        .merge(df_dia.groupby("dia").size().reset_index(name="Atendimentos"), on="dia", how="left")
        .fillna(0)
    )
    por_dia["Atendimentos"] = por_dia["Atendimentos"].astype(int)
    fig3 = px.bar(
        por_dia, x="dia", y="Atendimentos",
        color_discrete_sequence=["#a855f7"],
        template="plotly_dark", labels={"dia": "Dia"},
    )
    fig3.update_layout(**PLOT_LAYOUT, height=200, xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    st.plotly_chart(fig3, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.markdown(
            "<p style='color:#888;font-size:13px;font-weight:600;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:8px;'>Horários de pico</p>",
            unsafe_allow_html=True,
        )
        hora_count = df_mes["horario"].value_counts().sort_index().reset_index()
        hora_count.columns = ["Horário", "Agendamentos"]
        fig4 = px.bar(hora_count, x="Horário", y="Agendamentos", color_discrete_sequence=["#26c6a6"], template="plotly_dark")
        fig4.update_layout(**PLOT_LAYOUT, height=220)
        st.plotly_chart(fig4, use_container_width=True)

    with col_g4:
        st.markdown(
            "<p style='color:#888;font-size:13px;font-weight:600;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:8px;'>Status dos agendamentos</p>",
            unsafe_allow_html=True,
        )
        status_count = df_mes["status"].value_counts().reset_index()
        status_count.columns = ["Status", "Quantidade"]
        cores_status = {"confirmado": "#d4a853", "concluido": "#4caf50", "cancelado": "#e53935"}
        cores3 = [cores_status.get(s, "#888") for s in status_count["Status"]]
        fig5 = px.bar(status_count, x="Status", y="Quantidade", color_discrete_sequence=cores3, template="plotly_dark")
        fig5.update_traces(marker_color=cores3)
        fig5.update_layout(**PLOT_LAYOUT, height=220, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Comparativo com mês anterior ──
    if not df_ant.empty:
        st.markdown("---")
        st.markdown('<div class="secao-titulo">🔄 Comparativo com mês anterior</div>', unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        comparativos = [
            (cc1, "Atendimentos",      total_mes, total_ant, "",    ""),
            (cc2, "Faturamento",       fat_mes,   fat_ant,   "R$ ", ""),
            (cc3, "Taxa de conclusão", taxa_mes,  taxa_ant,  "",    "%"),
        ]
        for col, label, v_mes, v_ant, prefix, suffix in comparativos:
            diff  = v_mes - v_ant
            cor   = "#4caf50" if diff >= 0 else "#e53935"
            sinal = "+" if diff >= 0 else ""
            with col:
                st.markdown(f"""
<div class="destaque-card">
    <div class="destaque-label">{label}</div>
    <div style="display:flex;align-items:baseline;gap:12px;">
        <div class="destaque-val">{prefix}{v_mes}{suffix}</div>
        <div style="font-size:16px;color:{cor};font-weight:600;">{sinal}{prefix}{diff}{suffix}</div>
    </div>
    <div class="destaque-sub">vs {MESES_PT[mes_ant]}: {prefix}{v_ant}{suffix}</div>
</div>""", unsafe_allow_html=True)