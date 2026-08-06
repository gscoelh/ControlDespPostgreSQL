from src.core.db import get_connection

def listar_por_roteiro_competencia(roteiro, mes, ano):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        DATALANCTO,
        CONTA,
        HISTORICO,
        COMPLHISTORICO,
        VALLANCTO,
        SINALLANCTO,
        CONTRAPARTIDA,
        COMPROVANTEWEB,
        DATAREGISTRO
    FROM LANCAMENTOS
    WHERE ROTEIRO = %s
        AND EXTRACT(MONTH FROM DATALANCTO) = %s
        AND EXTRACT(YEAR FROM DATALANCTO) = %s
    ORDER BY DATALANCTO, SINALLANCTO, SEQUENCIALOTE;
    """, (roteiro, mes, ano))

    return cur.fetchall()

def proximo_sequencial_lote(lote):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(SEQUENCIALOTE)
        FROM LANCAMENTOS
        WHERE LOTE = %s
    """, (lote,))

    row = cur.fetchone()
    return (row[0] + 1) if row[0] else 1

def inserir(datalancto, roteiro, conta, valor, sinal,
            historico, complhist, contrap, dataregistro,
            lote, sequencialote, quemweb, comprovante):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO LANCAMENTOS          
        (DATALANCTO, ROTEIRO, CONTA, VALLANCTO, SINALLANCTO,
         HISTORICO, COMPLHISTORICO, CONTRAPARTIDA, DATAREGISTRO,
         LOTE, SEQUENCIALOTE, QUEMWEB, COMPROVANTEWEB)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (datalancto, roteiro, conta, float(valor), sinal,
          historico, complhist, contrap, dataregistro,
          lote, sequencialote, quemweb, comprovante))

    conn.commit()

def excluir_lancamento_duplo(datalancto, conta, hist, compl, valor, comprovante):
    conn = get_connection()
    cur = conn.cursor()

    valor = float(valor)

    # Excluir linha C
    cur.execute("""
        DELETE FROM LANCAMENTOS
        WHERE DATALANCTO = %s
        AND CONTA = %s
        AND HISTORICO = %s
        AND COMPLHISTORICO = %s
        AND VALLANCTO = %s
        AND COMPROVANTEWEB = %s
        AND SINALLANCTO = 'C'
    """, (datalancto, conta, hist, compl, valor, comprovante))

    # Excluir linha D
    cur.execute("""
        DELETE FROM LANCAMENTOS
        WHERE DATALANCTO = %s
        AND CONTRAPARTIDA = %s
        AND HISTORICO = %s
        AND COMPLHISTORICO = %s
        AND VALLANCTO = %s
        AND COMPROVANTEWEB = %s
        AND SINALLANCTO = 'D'
    """, (datalancto, conta, hist, compl, valor, comprovante))

    conn.commit() 
    conn.close()

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
        valor = r[2]
        if valor is None:
            valor = 0

        resultado.append({
            "conta": r[0],
            "data": r[1],
            "valor": valor,
            "tipo": r[3]
        })

    return resultado

