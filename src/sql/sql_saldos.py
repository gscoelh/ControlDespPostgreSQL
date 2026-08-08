from src.database.connection import get_connection

# ============================================================
# APAGAR TODOS OS SALDOS
# ============================================================
def apagar_todos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM saldos_diarios")
    conn.commit()
    conn.close()


# ============================================================
# INSERIR LINHA NA TABELA
# ============================================================
def inserir(conta, descrcta, data, saldo_ant, debito, credito, saldo_atu):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO saldos_diarios (conta, descrcta, data, saldo_ant, debito, credito, saldo_atu)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (conta, descrcta, data, saldo_ant, debito, credito, saldo_atu))
    conn.commit()
    conn.close()


# ============================================================
# BUSCAR PRIMEIRO SALDO DA CONTA
# ============================================================
def buscar_primeiro_saldo(conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT saldo_atu FROM saldos_diarios
        WHERE conta = %s
        ORDER BY data ASC LIMIT 1
    """, (conta,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


# ============================================================
# BUSCAR DESCRIÇÃO DA CONTA
# ============================================================
def buscar_descr(conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT descrcta FROM cadconta
        WHERE conta = %s
    """, (conta,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


# ============================================================
# LISTAR TODOS OS SALDOS (ORDENADOS)
# ============================================================
def listar_todos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT conta, descrcta, data, saldo_ant, debito, credito, saldo_atu
        FROM saldos_diarios
        ORDER BY conta, data
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# LISTAR SALDOS MENSAIS (ÚLTIMO DIA DE CADA MÊS)
# ============================================================
def listar_saldos_mensais(ano):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (conta, date_trunc('month', data))
            conta,
            descrcta,
            date_trunc('month', data) AS mes,
            saldo_atu
        FROM saldos_diarios
        WHERE EXTRACT(YEAR FROM data) = %s
        ORDER BY conta, date_trunc('month', data), data DESC
    """, (ano,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# LISTAR DIAS DO MÊS PARA UMA CONTA
# ============================================================
def listar_por_conta_e_mes(conta, mes, ano):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT conta, descrcta, data, saldo_ant, debito, credito, saldo_atu
        FROM saldos_diarios
        WHERE conta = %s
          AND EXTRACT(MONTH FROM data) = %s
          AND EXTRACT(YEAR FROM data) = %s
        ORDER BY data
    """, (conta, mes, ano))
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# LISTAR POR PERÍODO
# ============================================================
def listar_por_periodo(inicio, fim):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT conta, descrcta, data, saldo_ant, debito, credito, saldo_atu
        FROM saldos_diarios
        WHERE data BETWEEN %s AND %s
        ORDER BY conta, data
    """, (inicio, fim))
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# BUSCAR SALDO EM UM DIA ESPECÍFICO
# ============================================================
def buscar_saldo_no_dia(conta, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT saldo_atu FROM saldos_diarios
        WHERE conta = %s AND data = %s
    """, (conta, data))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
def listar_net_mensal(conta, data_ini, data_fim):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            date_trunc('month', data) AS mes,
            SUM(credito) AS total_credito,
            SUM(debito) AS total_debito,
            SUM(credito) - SUM(debito) AS net
        FROM saldos_diarios
        WHERE conta = %s
          AND data BETWEEN %s AND %s
        GROUP BY date_trunc('month', data)
        ORDER BY mes;
    """, (str(conta), data_ini, data_fim))

    rows = cur.fetchall()
    conn.close()
    return rows
