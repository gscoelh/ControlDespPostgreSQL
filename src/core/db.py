import psycopg2
from src.core.config import get_postgres_config

def get_connection():
    cfg = get_postgres_config()

    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"]
    )
