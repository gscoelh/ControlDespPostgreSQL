from src.core.db import get_connection

# ============================================================
# LISTAR LANÇAMENTOS POR ROTEIRO E COMPETÊNCIA
# ============================================================
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

    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# PRÓXIMO SEQUENCIAL DO LOTE
# ============================================================
def proximo_sequencial_lote(lote):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(SEQUENCIALOTE)
        FROM LANCAMENTOS
        WHERE LOTE = %s
    """, (lote,))

    row = cur.fetchone()
    conn.close()
    return (row[0] + 1) if row[0] else 1


# ============================================================
# INSERIR LANÇAMENTO (PADRÃO FIXO D/C)
# ============================================================
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
    conn.close()


# ============================================================
# EXCLUIR LANÇAMENTO DUPLO (PADRÃO FIXO D/C)
# ============================================================
def excluir_lancamento_duplo(datalancto, conta_spread, hist, compl, valor, comprovante):
    conn = get_connection()
    cur = conn.cursor()
    
    valor = float(valor)
                    
    # Linha D → conta_spread  ###    AND SINALLANCTO = 'D'
    cur.execute("""
        DELETE FROM LANCAMENTOS
        WHERE DATALANCTO::date = %s
        AND CONTA = %s
        AND HISTORICO = %s
        AND COMPLHISTORICO = %s
        AND VALLANCTO = %s
        AND COMPROVANTEWEB = %s
   
    """, (datalancto, conta_spread, hist, compl, valor, comprovante))
    # Linha C → conta_capa (contrapartida) #    AND SINALLANCTO = 'C'
    cur.execute("""
        DELETE FROM LANCAMENTOS
        WHERE DATALANCTO::date = %s
        AND CONTRAPARTIDA = %s
        AND HISTORICO = %s
        AND COMPLHISTORICO = %s
        AND VALLANCTO = %s
        AND COMPROVANTEWEB = %s
    
    """, (datalancto, conta_spread, hist, compl, valor, comprovante))

    conn.commit()
    conn.close()


# ============================================================
# LISTAR TODOS ORDENADOS
# ============================================================
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
        valor = r[2] if r[2] is not None else 0

        resultado.append({
            "conta": r[0],
            "data": r[1],
            "valor": valor,
            "tipo": r[3]
        })

    return resultado


# ============================================================
# BUSCAR PAR D/C (COMPATÍVEL COM LANÇAMENTOS ANTIGOS E NOVOS)
# ============================================================
def buscar_lancamento_duplo(datafull, conta_spread, hist, compl, valor, compweb):
    conn = get_connection()
    cur = conn.cursor()

    valor = float(valor)

    cur.execute("""
        SELECT 
            DATALANCTO, CONTA, HISTORICO, COMPLHISTORICO,
            VALLANCTO, COMPROVANTEWEB, SINALLANCTO, CONTRAPARTIDA
        FROM LANCAMENTOS
        WHERE DATALANCTO::date = %s
        AND (CONTA = %s OR CONTRAPARTIDA = %s)
        AND HISTORICO = %s
        AND COMPLHISTORICO = %s
        AND VALLANCTO = %s
        AND COMPROVANTEWEB = %s
        ORDER BY SINALLANCTO
    """, (datafull, conta_spread, conta_spread, hist, compl, valor, compweb))

    rows = cur.fetchall()
    conn.close()

    if len(rows) == 2:
        linhaD = rows[0] if rows[0][6] == "D" else rows[1]
        linhaC = rows[1] if rows[0][6] == "D" else rows[0]
        return linhaD, linhaC

    return None

def inserir_lancamento_duplo(data, conta_origem, conta_despesa, historico, compl, valor, compweb, roteiro):
    """
    Insere o par de lançamentos (C/D) usando nextval() para evitar duplicação.
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        # pegar sequências novas da sequence oficial
        cur.execute("SELECT nextval('lancamentos_sequencia_seq')")
        seq1 = cur.fetchone()[0]

        cur.execute("SELECT nextval('lancamentos_sequencia_seq')")
        seq2 = cur.fetchone()[0]

        # linha 1: origem -> despesa (C)
        cur.execute("""
            INSERT INTO lancamentos (
                sequencia, datalancto, conta, historico, complhistorico,
                vallancto, sinallancto, contrapartida, comprovanteweb,
                dataregistro, roteiro
            )
            VALUES (%s, %s, %s, %s, %s,
                    %s, 'C', %s, %s,
                    NOW(), %s)
        """, (
            seq1, data, conta_origem, historico, compl,
            valor, conta_despesa, compweb, roteiro
        ))

        # linha 2: despesa -> origem (D)
        cur.execute("""
            INSERT INTO lancamentos (
                sequencia, datalancto, conta, historico, complhistorico,
                vallancto, sinallancto, contrapartida, comprovanteweb,
                dataregistro, roteiro
            )
            VALUES (%s, %s, %s, %s, %s,
                    %s, 'D', %s, %s,
                    NOW(), %s)
        """, (
            seq2, data, conta_despesa, historico, compl,
            valor, conta_origem, compweb, roteiro
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        raise Exception(f"Erro ao inserir lançamento duplo: {e}")

def buscar_par(datafull, compweb, valor):
    """
    Retorna as duas linhas do lançamento duplo (C e D)
    que possuem a mesma data, comprovante e valor.
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                datalancto,
                conta,
                historico,
                complhistorico,
                vallancto,
                sinallancto,
                contrapartida,
                comprovanteweb,
                dataregistro,
                roteiro
            FROM lancamentos
            WHERE datalancto = %s
            AND comprovanteweb = %s
            AND vallancto = %s
            ORDER BY sinallancto
        """, (datafull, compweb, valor))

        linhas = cur.fetchall()
        conn.close()

        return linhas

    except Exception as e:
        raise Exception(f"Erro ao buscar par: {e}")
    

