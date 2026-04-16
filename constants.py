SERVICOS = [
    "Corte de cabelo",
    "Barba",
    "Corte + Barba",
    "Degradê",
    "Tingimento",
    "Hidratação",
]

PRECO_SERVICOS = {
    "Corte de cabelo": 45,
    "Barba":           35,
    "Corte + Barba":   70,
    "Degradê":         55,
    "Tingimento":      120,
    "Hidratação":      60,
}

SERVICO_ICONS = {
    "Corte de cabelo": "✂️",
    "Barba":           "🪒",
    "Corte + Barba":   "💈",
    "Degradê":         "🎨",
    "Tingimento":      "🖌️",
    "Hidratação":      "💧",
}

CORES_SERVICOS = {
    "Corte de cabelo": "#4a90d9",
    "Barba":           "#26c6a6",
    "Corte + Barba":   "#a855f7",
    "Degradê":         "#f59e0b",
    "Tingimento":      "#ef5350",
    "Hidratação":      "#ec4899",
}

STATUS_CONFIG = {
    "confirmado": {"cor": "#d4a853", "label": "Confirmado", "bg": "rgba(212,168,83,0.12)"},
    "concluido":  {"cor": "#4caf50", "label": "Concluído",  "bg": "rgba(76,175,80,0.12)"},
    "cancelado":  {"cor": "#e53935", "label": "Cancelado",  "bg": "rgba(229,57,53,0.12)"},
}

MESES_PT = {
    1: "Janeiro",  2: "Fevereiro", 3: "Março",    4: "Abril",
    5: "Maio",     6: "Junho",     7: "Julho",     8: "Agosto",
    9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro",
}

MESES_PT_MIN = {k: v.lower() for k, v in MESES_PT.items()}

DIAS_PT = {
    0: "Segunda-feira", 1: "Terça-feira",  2: "Quarta-feira",
    3: "Quinta-feira",  4: "Sexta-feira",  5: "Sábado",
    6: "Domingo",
}

DIAS_PT_CURTO = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

TODOS_HORARIOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30",
]