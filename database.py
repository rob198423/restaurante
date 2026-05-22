import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("restaurante.db")


def get_connection():
    """Cria uma conexão com o banco SQLite da aplicação."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    """Cria as tabelas necessárias para o sistema de comandas."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('aberta', 'fechada')),
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fechada_em TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comanda_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comanda_id) REFERENCES comandas (id)
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_comandas_mesa_aberta
            ON comandas (mesa)
            WHERE status = 'aberta'
            """
        )
