from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        C.CODCTA,
        C.DESCRCTA,
        C.CODCTAAGR,
        A.DESCRCTAAGR,
        C.TPCUSTO,
        C.NATUREZACTA,
        TO_CHAR(C.DTAABERTURACTA, 'DD/MM/YYYY')
    FROM CADCONTA AS C
    LEFT JOIN CADCTAAGR AS A ON C.CODCTAAGR = A.CODCTAAGR
    ORDER BY C.CODCTA
    """)

    
    return cur.fetchall()

def existe(cod_conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CADCONTA WHERE CODCTA=%s", (cod_conta,))
    return cur.fetchone()[0] > 0

def inserir(cod_conta, descricao, cod_agr, cod_custo, natureza, dtaabert):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO CADCONTA (CODCTA, DESCRCTA, CODCTAAGR, TPCUSTO, NATUREZACTA, DTAABERTURACTA)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (cod_conta, descricao, cod_agr, cod_custo, natureza, dtaabert))
    conn.commit()

def atualizar(cod_conta, descricao, cod_agr, cod_custo, natureza, dtaabert):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE CADCONTA
        SET DESCRCTA=%s, CODCTAAGR=%s, TPCUSTO=%s, NATUREZACTA=%s, DTAABERTURACTA=%s
        WHERE CODCTA=%s
    """, (descricao, cod_agr, cod_custo, natureza, dtaabert, cod_conta))
    conn.commit()

def excluir(cod_conta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM CADCONTA WHERE CODCTA=%s", (cod_conta,))
    conn.commit()

# LISTAS PARA COMBOBOXES
def listar_grupos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT CODCTAAGR, DESCRCTAAGR FROM CADCTAAGR ORDER BY CODCTAAGR")
    return cur.fetchall()

def listar_tipos_custo():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT TPCUSTO FROM CONTASPORCUSTO GROUP BY TPCUSTO ORDER BY TPCUSTO")
    return cur.fetchall()
def listar_por_grupo(cod_agr):
    conn = get_connection()
    cur = conn.cursor()

    if cod_agr == "TODOS":
        cur.execute("""
            SELECT 
                C.CODCTA,
                C.DESCRCTA,
                C.CODCTAAGR,
                A.DESCRCTAAGR,
                C.TPCUSTO,
                C.NATUREZACTA,
                TO_CHAR(C.DTAABERTURACTA, 'DD/MM/YYYY')
            FROM CADCONTA AS C
            LEFT JOIN CADCTAAGR AS A ON C.CODCTAAGR = A.CODCTAAGR
            ORDER BY C.CODCTA
        """)
    else:
        cur.execute("""
            SELECT 
                C.CODCTA,
                C.DESCRCTA,
                C.CODCTAAGR,
                A.DESCRCTAAGR,
                C.TPCUSTO,
                C.NATUREZACTA,
                TO_CHAR(C.DTAABERTURACTA, 'DD/MM/YYYY')
            FROM CADCONTA AS C
            LEFT JOIN CADCTAAGR AS A ON C.CODCTAAGR = A.CODCTAAGR
            WHERE C.CODCTAAGR = %s
            ORDER BY C.CODCTA
        """, (cod_agr,))

    return cur.fetchall()

def listar_por_roteiro(rot):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            datalancto,
            conta,
            historico,
            complhistorico,
            valor,
            natureza,
            conta_capa,
            comprovante,
            dataregistro,
            seq
        FROM lancamentos
        WHERE roteiro = %s
        ORDER BY datalancto, seq
    """, (rot,))

    return cur.fetchall()

