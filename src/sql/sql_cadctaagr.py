from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT CODCTAAGR, DESCRCTAAGR, DTAABERTURA
        FROM CADCTAAGR
        ORDER BY CODCTAAGR
    """)
    return cur.fetchall()


def inserir(cod, descricao, dtaabert):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO CADCTAAGR (CODCTAAGR, DESCRCTAAGR, DTAABERTURA) VALUES (%s, %s, %s)", (cod, descricao, dtaabert))
    conn.commit()

def atualizar(cod, descricao):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE CADCTAAGR SET DESCRCTAAGR=%s WHERE CODCTAAGR=%s", (descricao, cod))
    conn.commit()

def excluir(cod):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM CADCTAAGR WHERE CODCTAAGR=%s", (cod,))
    conn.commit()
def existe(cod):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CADCTAAGR WHERE CODCTAAGR=%s", (cod,))
    return cur.fetchone()[0] > 0
