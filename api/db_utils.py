import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "soil_health.sqlite")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def execute_statement(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_path = os.path.join(os.path.dirname(__file__), "..", "db", "init.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
