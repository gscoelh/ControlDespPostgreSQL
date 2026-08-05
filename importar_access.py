import subprocess
import pandas as pd
from sqlalchemy import create_engine
from io import StringIO

mdb_file = "/home/user/accessdb/NOVODESPESAS.mdb"

engine = create_engine("postgresql://postgres:00025G&c@172.30.144.1:5432/controldesp")

tables = subprocess.check_output(["mdb-tables", "-1", mdb_file]).decode().split()

print("Tabelas encontradas:", tables)

for table in tables:
    print(f"Importando tabela: {table}")

    try:
        csv_data = subprocess.check_output(["mdb-export", mdb_file, table]).decode()

        df = pd.read_csv(StringIO(csv_data))

        df.to_sql(table.lower(), engine, if_exists="replace", index=False)

        print(f"✔ Tabela {table} importada com sucesso.")

    except Exception as e:
        print(f"❌ Erro ao importar {table}: {e}")

print("Migração concluída!")
