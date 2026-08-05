from src.core.db import get_connection

def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ROTEIRO, ROTNATUREZA, ROTCTADEB, ROTCTACRED, ROTHIST
        FROM ROTEIRODETA
        ORDER BY ROTEIRO
    """)
    return cur.fetchall()

def listar_por_roteiro(rot):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ROTEIRO, ROTNATUREZA, ROTCTADEB, ROTCTACRED, ROTHIST
        FROM ROTEIRODETA
        WHERE ROTEIRO = %s
    """, (rot,))
    return cur.fetchall()

def existe_conta_no_roteiro(rot, deb, cred):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM ROTEIRODETA
        WHERE ROTEIRO = %s
          AND ROTCTADEB = %s
          AND ROTCTACRED = %s
    """, (rot, deb, cred))
    return cur.fetchone()[0] > 0

def inserir(rot, natureza, deb, cred, hist):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ROTEIRODETA (ROTEIRO, ROTNATUREZA, ROTCTADEB, ROTCTACRED, ROTHIST)
        VALUES (%s, %s, %s, %s, %s)
    """, (rot, natureza, deb, cred, hist))
    conn.commit()

def atualizar(rot, natureza, deb, cred, hist):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE ROTEIRODETA
        SET ROTNATUREZA=%s, ROTCTADEB=%s, ROTCTACRED=%s, ROTHIST=%s
        SET ROTNATUREZA=%s, ROTCTADEB=%s, ROTCTACRED=%s, ROTHIST=%s
        WHERE ROTEIRO=
    """, (natureza, deb, cred, hist, rot))
    conn.commit()

def excluir(rot, deb, cred):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM ROTEIRODETA
        SET ROTNATUREZA=%s, ROTCTADEB=%s, ROTCTACRED=%s, ROTHIST=%s
        WHERE ROTEIRO=%s AND ROTCTADEB= AND ROTCTACRED=%s
    """, (rot, deb, cred))
    conn.commit()
