import configparser
import os
import sys

# ============================================================
# LOCALIZAÇÃO DO ARQUIVO CONFIG.INI
# Funciona no VS Code e também no executável PyInstaller
# ============================================================

def get_base_path():
    """
    Retorna o caminho base onde o programa deve procurar o config.ini.
    - No VS Code: pasta real do projeto
    - No executável (.exe): pasta onde o .exe está rodando (dist)
    """
    if hasattr(sys, "_MEIPASS"):
        # Quando rodando como executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Quando rodando via Python normal (VS Code)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_PATH = get_base_path()
INI_PATH = os.path.join(BASE_PATH, "config.ini")
INI_PATH = os.path.abspath(INI_PATH)

config = configparser.ConfigParser()

# ============================================================
# CRIA O INI SE NÃO EXISTIR
# ============================================================

if not os.path.exists(INI_PATH):

    config["AMBIENTE"] = {
        "modo": "DESENV",
        "mostrar_alerta": "SIM"
    }

    config["POSTGRES_DESENV"] = {
        "host": "localhost",
        "port": "5432",
        "database": "controldesp_desenv",
        "user": "postgres",
        "password": ""
    }

    config["POSTGRES_PRODUC"] = {
        "host": "localhost",
        "port": "5432",
        "database": "controldesp",
        "user": "postgres",
        "password": ""
    }

    config["PASTAS"] = {
        "comprovantes": "C:/Users/User/OneDrive/Documents/ComprovantePagamentos"
    }

    config["AUTOCOMPLETE"] = {
        "palavras": ""
    }

    with open(INI_PATH, "w", encoding="utf-8") as f:
        config.write(f)

# ============================================================
# CARREGA O INI
# ============================================================

config.read(INI_PATH, encoding="utf-8")

# ============================================================
# AMBIENTE
# ============================================================

def get_modo():
    return config["AMBIENTE"]["modo"]

def set_modo(valor):
    config["AMBIENTE"]["modo"] = valor
    with open(INI_PATH, "w", encoding="utf-8") as f:
        config.write(f)

def get_alerta():
    return config["AMBIENTE"]["mostrar_alerta"]

def set_alerta(valor):
    config["AMBIENTE"]["mostrar_alerta"] = valor
    with open(INI_PATH, "w", encoding="utf-8") as f:
        config.write(f)

# ============================================================
# PASTAS
# ============================================================

def get_pasta_comprovantes():
    return config["PASTAS"]["comprovantes"]

# ============================================================
# AUTOCOMPLETE
# ============================================================

def get_complementos():
    palavras = config["AUTOCOMPLETE"]["palavras"]
    return [p.strip() for p in palavras.split(",") if p.strip()]

def add_complemento(novo):
    palavras = get_complementos()

    if novo not in palavras:
        palavras.append(novo)
        palavras = palavras[-200:]  # limita a 200 palavras

        config["AUTOCOMPLETE"]["palavras"] = ",".join(palavras)

        with open(INI_PATH, "w", encoding="utf-8") as f:
            config.write(f)

# ============================================================
# POSTGRESQL
# ============================================================

def get_postgres_config():
    """
    Escolhe automaticamente o banco conforme o ambiente:
    DESENV → POSTGRES_DESENV
    PRODUC → POSTGRES_PRODUC
    """
    modo = get_modo()

    section = "POSTGRES_DESENV" if modo == "DESENV" else "POSTGRES_PRODUC"

    return {
        "host": config[section]["host"],
        "port": int(config[section]["port"]),
        "database": config[section]["database"],
        "user": config[section]["user"],
        "password": config[section]["password"],
    }
