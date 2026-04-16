# ✂️ BarberPro — Sistema de Agendamento

Sistema web de agendamento desenvolvido em Python com Streamlit, voltado para barbearias e salões de cabeleireiro. Permite gerenciar clientes, horários, serviços e acompanhar o desempenho do negócio através de um dashboard interativo.

---

## 🚀 Funcionalidades

- **Início:** visão geral do dia, próximo atendimento, resumo de clientes e ações rápidas
- **Agenda do Dia:** visualização de agendamentos por data com filtros de status e barra de progresso
- **Novo Agendamento:** fluxo guiado em 3 passos — cliente, serviço/horário e confirmação
- **Clientes:** cadastro, busca, histórico de atendimentos e acesso rápido a novo agendamento
- **Dashboard:** métricas mensais de faturamento, ticket médio, taxa de conclusão e gráficos por serviço, horário e dia

---

## 🗂️ Estrutura do Projeto

```
agendamento-cabeleireiro/
│
├── pages/
│   ├── inicio.py         # Página inicial com resumo do dia
│   ├── agenda_dia.py     # Visualização e gestão da agenda
│   ├── agendar.py        # Wizard de criação de agendamento
│   ├── clientes.py       # Listagem e cadastro de clientes
│   └── dashboard.py      # Gráficos e métricas do negócio
│
├── app.py                # Entrada da aplicação, navegação e CSS global
├── database.py           # Conexão SQLite e todas as funções de banco
├── constants.py          # Constantes compartilhadas (serviços, preços, status)
├── requirements.txt      # Dependências do projeto
└── README.md
```

> O banco de dados `barbearia.db` é criado automaticamente na primeira execução.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| Streamlit | Framework web e interface |
| SQLite | Banco de dados local |
| Pandas | Manipulação de dados no dashboard |
| Plotly | Gráficos interativos |

---

## ▶️ Como Rodar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/vivikari/agendamento-cabeleireiro.git
cd agendamento-cabeleireiro
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o projeto

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

> O banco de dados é criado automaticamente — nenhuma configuração adicional é necessária.

---

## 💡 Exemplo de Uso

1. Acesse a página **Início** para ver o resumo do dia
2. Clique em **Agendar** na sidebar para criar um novo agendamento
3. Selecione ou cadastre um cliente no Passo 1
4. Escolha o serviço, a data e o horário disponível no Passo 2
5. Revise e confirme no Passo 3
6. Acompanhe o agendamento na **Agenda do Dia** e marque como concluído após o atendimento
7. Consulte o **Dashboard** para ver o desempenho do mês

---

## 🔮 Melhorias Futuras

- Notificações por WhatsApp ou SMS para lembrete de agendamento
- Autenticação com login e senha
- Suporte a múltiplos profissionais
- Exportação da agenda em PDF ou CSV
- Controle de estoque de produtos

---

## 📄 Licença

Projeto acadêmico. Livre para uso e adaptação.