import tkinter as tk
from tkinter import ttk, messagebox
from src.sql import sql_saldos, sql_lancamentos, sql_cadconta

cancelar_flag = False

SALDOS_INICIAIS = {
    "10101": 1500.00,   # exemplo
}

def gerar_saldos_iniciais():
    contas = sql_cadconta.listar()

    for conta, descrcta, *_ in contas:
        saldo_inicial = SALDOS_INICIAIS.get(conta, 0.0)

        sql_saldos.inserir(
            conta=conta,
            descrcta=descrcta,
            data="2017-01-01",
            saldo_ant=saldo_inicial,
            debito=0,
            credito=0,
            saldo_atu=saldo_inicial
        )


def janela_progresso():
    prog = tk.Toplevel()
    prog.title("Reprocessando Saldos")
    prog.geometry("400x150")
    prog.grab_set()

    lbl = tk.Label(prog, text="Processando saldos, aguarde...")
    lbl.pack(pady=10)

    barra = ttk.Progressbar(prog, length=350, mode="determinate")
    barra.pack(pady=10)

    btn_cancelar = tk.Button(prog, text="Cancelar", command=lambda: cancelar_processamento(prog))
    btn_cancelar.pack()

    return prog, barra


def cancelar_processamento(janela):
    global cancelar_flag
    cancelar_flag = True
    janela.destroy()


def recompor_saldos():
    global cancelar_flag
    cancelar_flag = False

    sql_saldos.apagar_todos()
    gerar_saldos_iniciais()

    lancs = sql_lancamentos.listar_todos_ordenados()
    saldos = {}

    prog, barra = janela_progresso()
    total = len(lancs)

    agrupado = {}

    for lan in lancs:
        conta = lan["conta"]
        data = lan["data"]
        valor = lan["valor"] or 0
        tipo = lan["tipo"]

        chave = (conta, data)

        if chave not in agrupado:
            agrupado[chave] = {"debito": 0, "credito": 0}

        if tipo == "D":
            agrupado[chave]["debito"] += valor
        else:
            agrupado[chave]["credito"] += valor

    agrupado_ordenado = sorted(agrupado.items(), key=lambda x: (x[0][0], x[0][1]))

    for i, ((conta, data), valores) in enumerate(agrupado_ordenado):
        if cancelar_flag:
            messagebox.showwarning("Cancelado", "Processamento interrompido pelo usuário.")
            break

        descrcta = sql_cadconta.buscar_descr(conta)
        saldo_ant = saldos.get(conta, sql_saldos.buscar_primeiro_saldo(conta))

        debito = valores["debito"]
        credito = valores["credito"]
        saldo_atu = saldo_ant + debito - credito
        saldos[conta] = saldo_atu

        sql_saldos.inserir(
            conta=conta,
            descrcta=descrcta,
            data=data,
            saldo_ant=saldo_ant,
            debito=debito,
            credito=credito,
            saldo_atu=saldo_atu
        )

        barra["value"] = (i + 1) / total * 100
        prog.update()

    prog.destroy()
    messagebox.showinfo("OK", "Reprocessamento concluído.")
def limpar_base():
    if messagebox.askyesno("Confirmar", "Deseja realmente limpar todos os saldos?"):
        sql_saldos.apagar_todos()
        gerar_saldos_iniciais()
        messagebox.showinfo("OK", "Base de saldos reiniciada.")

def mostrar_saldos_iniciais_faltantes():
    contas = sql_cadconta.listar()
    faltantes = []
    print("Tipo de contas:", type(contas))
    for item in contas[:5]:  # mostra só os primeiros 5
        print("Item:", item, " -> tamanho:", len(item) if hasattr(item, "__len__") else "não é sequência")

    for conta, descrcta, *_ in contas:

        if conta not in SALDOS_INICIAIS:
            faltantes.append(f"{conta} - {descrcta}")

    if not faltantes:
        messagebox.showinfo("OK", "Todas as contas possuem saldo inicial definido.")
    else:
        msg = "\n".join(faltantes)
        messagebox.showwarning("Faltando saldo inicial", msg)

