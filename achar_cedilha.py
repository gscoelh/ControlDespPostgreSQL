import os

ROOT = r"C:\Users\User\Documents\ControlDespPostgreSQL"

print("\n=== ARQUIVOS QUE CONTÊM O BYTE 0xE7 (CEDILHA) ===\n")

for raiz, dirs, arquivos in os.walk(ROOT):
    for nome in arquivos:
        caminho = os.path.join(raiz, nome)
        try:
            with open(caminho, "rb") as f:
                dados = f.read()
            if b"\xe7" in dados:
                print(">>", caminho)
        except Exception as e:
            print("ERRO AO LER:", caminho, e)
