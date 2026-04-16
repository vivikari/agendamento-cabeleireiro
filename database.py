import sqlite3

DB_PATH = "barbearia.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Habilita FK cascade no SQLite (precisa ser ativado por conexão)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nome       TEXT    NOT NULL,
            telefone   TEXT,
            criado_em  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Recria a tabela com ON DELETE CASCADE caso ainda não exista com essa FK
    c.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id  INTEGER NOT NULL,
            servico     TEXT    NOT NULL,
            data        TEXT    NOT NULL,
            horario     TEXT    NOT NULL,
            status      TEXT    DEFAULT 'confirmado',
            observacoes TEXT,
            criado_em   TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ── CLIENTES ──────────────────────────────────────────────────────────────────

def criar_cliente(nome: str, telefone: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
    conn.commit()
    cliente_id = c.lastrowid
    conn.close()
    return cliente_id


def listar_clientes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM clientes ORDER BY nome")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def buscar_cliente_por_nome(nome: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE nome LIKE ?", (f"%{nome}%",))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def deletar_cliente(cliente_id: int):
    """
    Deleta o cliente. Com PRAGMA foreign_keys = ON e ON DELETE CASCADE,
    os agendamentos são removidos automaticamente pelo banco.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()


# ── AGENDAMENTOS ──────────────────────────────────────────────────────────────

def criar_agendamento(cliente_id: int, servico: str, data: str,
                      horario: str, observacoes: str = "") -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO agendamentos (cliente_id, servico, data, horario, observacoes)
        VALUES (?, ?, ?, ?, ?)
    """, (cliente_id, servico, data, horario, observacoes))
    conn.commit()
    ag_id = c.lastrowid
    conn.close()
    return ag_id


def listar_agendamentos_por_data(data: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT a.*, cl.nome AS cliente_nome, cl.telefone
        FROM agendamentos a
        JOIN clientes cl ON cl.id = a.cliente_id
        WHERE a.data = ?
        ORDER BY a.horario
    """, (data,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def listar_todos_agendamentos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT a.*, cl.nome AS cliente_nome, cl.telefone
        FROM agendamentos a
        JOIN clientes cl ON cl.id = a.cliente_id
        ORDER BY a.data DESC, a.horario
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def atualizar_status(ag_id: int, novo_status: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE agendamentos SET status = ? WHERE id = ?", (novo_status, ag_id))
    conn.commit()
    conn.close()


def deletar_agendamento(ag_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM agendamentos WHERE id = ?", (ag_id,))
    conn.commit()
    conn.close()


def horarios_ocupados(data: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT horario FROM agendamentos
        WHERE data = ? AND status != 'cancelado'
    """, (data,))
    rows = [r["horario"] for r in c.fetchall()]
    conn.close()
    return rows


def agendamentos_por_mes(ano: int, mes: int):
    conn = get_connection()
    c = conn.cursor()
    prefixo = f"{ano}-{str(mes).zfill(2)}"
    c.execute("""
        SELECT a.*, cl.nome AS cliente_nome
        FROM agendamentos a
        JOIN clientes cl ON cl.id = a.cliente_id
        WHERE a.data LIKE ?
        ORDER BY a.data, a.horario
    """, (f"{prefixo}%",))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def historico_cliente(cliente_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM agendamentos
        WHERE cliente_id = ?
        ORDER BY data DESC, horario DESC
    """, (cliente_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def historico_todos_clientes():
    """
    Retorna todos os agendamentos agrupáveis por cliente_id.
    Evita N queries no loop de listagem de clientes.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT cliente_id, data, horario, servico, status
        FROM agendamentos
        ORDER BY data DESC, horario DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows