from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT TPCUSTO, NOMECUSTO
        FROM CUSTOS
        ORDER BY TPCUSTO
    """)
    return cur.fetchall()

def existe(tp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CUSTOS WHERE TPCUSTO=%s", (tp,))
    return cur.fetchone()[0] > 0

def inserir(tp, nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO CUSTOS (TPCUSTO, NOMECUSTO) VALUES (%s, %s)", (tp, nome))
    conn.commit()

def atualizar(tp, nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE CUSTOS SET NOMECUSTO=%s WHERE TPCUSTO=%s", (nome, tp))
    conn.commit()

def excluir(tp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM CUSTOS WHERE TPCUSTO=%s", (tp,))
    conn.commit()
