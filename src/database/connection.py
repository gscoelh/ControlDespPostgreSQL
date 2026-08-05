
import psycopg2
from src.core.config import get_postgres_config
def get_connection():
    cfg = get_postgres_config()

    conn = psycopg2.connect(
        host=cfg["host"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"],
        options="-c lc_messages=C"
    )
    return conn