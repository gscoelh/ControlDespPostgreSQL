from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT TPCUSTO, CONTA, PERCENTUAL FROM CONTASPORCUSTO ORDER BY TPCUSTO")
    return cur.fetchall()

def existe(tpCusto, conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CONTASPORCUSTO WHERE TPCUSTO=%s AND CONTA=%s", (tpCusto, conta))
    return cur.fetchone()[0] > 0

def inserir(tpCusto, conta, percentual):
    if existe(tpCusto, conta):
        return False  # já existe
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO CONTASPORCUSTO (TPCUSTO, CONTA, PERCENTUAL) VALUES (%s, %s, %s)", 
                (tpCusto, conta, percentual))
    conn.commit()
    return True

def atualizar(tpCusto, conta, percentual):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE CONTASPORCUSTO SET PERCENTUAL=%s WHERE TPCUSTO=%s AND CONTA=%s", 
                (percentual, tpCusto, conta))
    conn.commit()

def excluir(tpCusto, conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM CONTASPORCUSTO WHERE TPCUSTO=%s AND CONTA=%s", (tpCusto, conta))
    conn.commit()
