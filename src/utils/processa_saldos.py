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
    """
    Nova rotina de recomposição de saldos.
    Usa o MÊS DO LOTE para cartões e a DATA REAL para contas normais.
    """

    global cancelar_flag
    cancelar_flag = False

    # 1) Limpa tudo e recria saldos iniciais
    sql_saldos.apagar_todos()
    gerar_saldos_iniciais()

    # 2) Carrega lançamentos
    lancs = sql_lancamentos.listar_todos_ordenados()

    # 3) Carrega dados auxiliares
    contas = {c[0]: c[1] for c in sql_cadconta.listar()}  # conta → descr
    cortes = carregar_datas_de_corte()  # conta → dia_corte

    saldos = {}  # saldo atual por conta
    agrupado = {}

    prog, barra = janela_progresso()
    total = len(lancs)

    # ============================================================
    # 4) AGRUPAR LANÇAMENTOS POR CONTA + DATA DE COMPETÊNCIA
    # ============================================================
    for lan in lancs:
        conta = lan["conta"]
        data_real = lan["data"]
        valor = lan["valor"] or 0
        tipo = lan["tipo"]

        # ------------------------------------------------------------
        # DEFINIR DATA DE COMPETÊNCIA
        # ------------------------------------------------------------
        anomes_real = data_real.strftime("%Y%m")

        dia_corte = cortes.get((conta, anomes_real))

        if dia_corte is None:
            # fallback: usa dia do mês real
            data_comp = data_real.replace(day=1)
        else:
            data_comp = calcular_competencia_cartao(data_real, dia_corte)
 
        chave = (conta, data_comp)

        if chave not in agrupado:
            agrupado[chave] = {"debito": 0, "credito": 0}

        if tipo == "D":
            agrupado[chave]["debito"] += valor
        else:
            agrupado[chave]["credito"] += valor

    # Ordenar por conta + data_competência
    agrupado_ordenado = sorted(agrupado.items(), key=lambda x: (x[0][0], x[0][1]))

    # ============================================================
    # 5) GRAVAR SALDOS DIÁRIOS
    # ============================================================
    for i, ((conta, data_comp), valores) in enumerate(agrupado_ordenado):
        if cancelar_flag:
            messagebox.showwarning("Cancelado", "Processamento interrompido pelo usuário.")
            break

        descrcta = contas.get(conta, "")
        saldo_ant = saldos.get(conta, sql_saldos.buscar_primeiro_saldo(conta))

        debito = valores["debito"]
        credito = valores["credito"]
        saldo_atu = saldo_ant + debito - credito
        saldos[conta] = saldo_atu

        sql_saldos.inserir(
            conta=conta,
            descrcta=descrcta,
            data=data_comp,
            saldo_ant=saldo_ant,
            debito=debito,
            credito=credito,
            saldo_atu=saldo_atu
        )

        barra["value"] = (i + 1) / total * 100
        prog.update()

    prog.destroy()
    messagebox.showinfo("OK", "Reprocessamento concluído com competência corrigida.")
def carregar_datas_de_corte():
    conn = sql_saldos.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT conta, datacorte FROM cartoes_corte")
    rows = cur.fetchall()
    conn.close()
    return {conta: dia for conta, dia in rows}
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calcular_competencia_cartao(data_real, dia_corte):
    dia = data_real.day

    if dia > dia_corte:
        # pós-corte → mês seguinte
        return (data_real + relativedelta(months=1)).replace(day=1)
    else:
        # pré-corte → mês atual
        return data_real.replace(day=1)

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

