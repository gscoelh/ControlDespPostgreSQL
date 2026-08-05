from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ROTEIRO, ROTNATUREZA, ROTDESC, CONTADANATUREZA, TITULOLOTE
        FROM ROTEIROCAPA
        ORDER BY ROTEIRO
    """)
    return cur.fetchall()

def existe(rot):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ROTEIROCAPA WHERE ROTEIRO=%s", (rot,))
    return cur.fetchone()[0] > 0

def inserir(rot, natureza, desc, conta, lote):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ROTEIROCAPA (ROTEIRO, ROTNATUREZA, ROTDESC, CONTADANATUREZA, TITULOLOTE)
        VALUES (%s, %s, %s, %s, %s)
    """, (rot, natureza, desc, conta, lote))
    conn.commit()

def atualizar(rot, natureza, desc, conta, lote):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE ROTEIROCAPA
        SET ROTNATUREZA=%s, ROTDESC=%s, CONTADANATUREZA=%s, TITULOLOTE=%s
        WHERE ROTEIRO=%s
    """, (natureza, desc, conta, lote, rot))
    conn.commit()

def excluir(rot):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ROTEIROCAPA WHERE ROTEIRO=%s", (rot,))
    conn.commit()

# CORREÇÃO IMPORTANTE
def buscar_natureza(cod_roteiro):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ROTNATUREZA
        FROM ROTEIROCAPA
        WHERE ROTEIRO = %s
    """, (cod_roteiro,))
    resultado = cur.fetchone()
    return resultado[0] if resultado else None

# CORREÇÃO IMPORTANTE
def buscar_conta(cod_roteiro):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT CONTADANATUREZA
        FROM ROTEIROCAPA
        WHERE ROTEIRO = %s
    """, (cod_roteiro,))
    resultado = cur.fetchone()
    return resultado[0] if resultado else None

def buscar_titulolote(cod_roteiro):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT TITULOLOTE
        FROM ROTEIROCAPA
        WHERE ROTEIRO = %s
    """, (cod_roteiro,))

    resultado = cur.fetchone()

    if resultado:
        return resultado[0]   # retorna o título do lote
    else:
        return None
