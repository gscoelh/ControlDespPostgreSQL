from core.db import get_connection

try:
    conn = get_connection()
    print("Conexão OK!")
    conn.close()
except Exception as e:
    print("Erro:", e)
