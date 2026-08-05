from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT codlote,
               descrlote,
               TO_CHAR(dtaabertura, 'DD/MM/YYYY')
        FROM tipolote
        ORDER BY codlote
    """)
    return cur.fetchall()

def existe(cod):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tipolote WHERE codlote=%s", (cod,))
    return cur.fetchone()[0] > 0

def inserir(cod, descr, dta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tipolote (codlote, descrlote, dtaabertura)
        VALUES (%s, %s, TO_DATE(%s, 'DD/MM/YYYY'))
    """, (cod, descr, dta))
    conn.commit()

def atualizar(cod, descr, dta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tipolote
        SET descrlote=%s,
            dtaabertura=TO_DATE(%s, 'DD/MM/YYYY')
        WHERE codlote=%s
    """, (descr, dta, cod))
    conn.commit()

def excluir(cod):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tipolote WHERE codlote=%s", (cod,))
    conn.commit()
