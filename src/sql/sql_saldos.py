from src.core.db import get_connection

def inserir(conta, descrcta, data, saldo_ant, debito, credito, saldo_atu):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO saldos_diarios
        (conta, descrcta, data, saldo_ant, debito, credito, saldo_atu)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    cur.execute(sql, (conta, descrcta, data, saldo_ant, debito, credito, saldo_atu))
    conn.commit()
    conn.close()

def apagar_todos():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM saldos_diarios")
    conn.commit()
    conn.close()

def buscar_primeiro(conta):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT conta, descrcta, data, saldo_ant, debito, credito, saldo_atu
        FROM saldos_diarios
        WHERE conta=%s
        ORDER BY data
        LIMIT 1
    """, (conta,))
    r = cur.fetchone()
    conn.close()
    return r

def buscar_primeiro_saldo(conta):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT saldo_atu
        FROM saldos_diarios
        WHERE conta=%s
        ORDER BY data
        LIMIT 1
    """, (conta,))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else 0

def listar_por_periodo(data_ini, data_fim):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT conta, descrcta, data, saldo_ant, debito, credito, saldo_atu
        FROM saldos_diarios
        WHERE data BETWEEN %s AND %s
        ORDER BY conta, data
    """, (data_ini, data_fim))

    rows = cur.fetchall()
    conn.close()
    return rows
def listar_todos_ordenados():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            CONTA,
            DATALANCTO,
            VALLANCTO,
            SINALLANCTO
        FROM LANCAMENTOS
        WHERE DATALANCTO IS NOT NULL
        ORDER BY CONTA, DATALANCTO
    """)

    rows = cur.fetchall()
    conn.close()

    resultado = []
    for r in rows:
        resultado.append({
            "conta": r[0],
            "data": r[1],          # sempre válido
            "valor": r[2] or 0,    # evita None
            "tipo": r[3]
        })

    return resultado
