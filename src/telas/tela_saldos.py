import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.sql import sql_saldos, sql_cadconta


from calendar import monthrange

#def mm_aaaa_para_datas(mmaaaa):
#    if len(mmaaaa) != 6 or not mmaaaa.isdigit():
#        return None, None
#
#    mes = int(mmaaaa[:2])
#    ano = int(mmaaaa[2:])
#
#    data_ini = datetime(ano, mes, 1)
#    ultimo_dia = monthrange(ano, mes)[1]
#    data_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)
#    print("data_fim  xxxx=====>", data_fim)
#    return data_ini, data_fim

# ============================================================
# SALDOS FIXOS — contas que acumulam mês a mês
# ============================================================
SALDOS_FIXOS = {
    "10101": +338.20
}


# ============================================================
# SALDO INICIAL — somente para contas em SALDOS_FIXOS
# ============================================================
def buscar_saldo_inicial(conta, data_ini):
    conta_str = str(conta)

    conn = sql_saldos.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo_inicial(%s::text, %s::date)", (conta_str, data_ini.date()))
    row = cur.fetchone()
    conn.close()

    saldo_banco = float(row[0]) if row else 0.0

    # saldo fixo deve entrar SEMPRE para contas que o possuem
    if conta_str in SALDOS_FIXOS:
        return saldo_banco + SALDOS_FIXOS[conta_str]

    return saldo_banco


# ============================================================
# CÁLCULO DO MOVIMENTO MENSAL
# ============================================================
def calcular_net_mensal(conta, data_ini, data_fim):
    conta_str = str(conta)

    conn = sql_saldos.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            TO_CHAR(datalancto, 'YYYYMM') AS comp,
            SUM(efeito_contabil(%s::text, datalancto, sinallancto, vallancto, contrapartida)) AS net
        FROM lancamentos
        WHERE conta = %s::text
            AND datalancto BETWEEN %s AND %s        
        GROUP BY comp
        ORDER BY comp
    """, (conta_str, conta_str, data_ini.date(), data_fim.date()))

    rows = cur.fetchall()
    print("NETS:", rows)

    conn.close()
    return rows


# ============================================================
# TELA PRINCIPAL
# ============================================================
def tela_saldos_mensais():
    win = tk.Toplevel()
    win.title("Demonstração de Saldos Mensais")
    win.geometry("1400x700")

    contas = sql_cadconta.listar()

    frame_top = tk.Frame(win)
    frame_top.pack(pady=10, fill="x")

    tk.Label(frame_top, text="Período inicial (MMAAAA):").grid(row=0, column=0, padx=5)
    ent_ini = tk.Entry(frame_top, width=10)
    ent_ini.grid(row=0, column=1, padx=5)

    tk.Label(frame_top, text="Período final (MMAAAA):").grid(row=0, column=2, padx=5)
    ent_fim = tk.Entry(frame_top, width=10)
    ent_fim.grid(row=0, column=3, padx=5)

    btn_demo = tk.Button(frame_top, text="Demonstrar")
    btn_demo.grid(row=0, column=4, padx=10)

    tk.Button(frame_top, text="Sair", command=win.destroy).grid(row=0, column=5, padx=10)

    btn_limpar = tk.Button(frame_top, text="Limpar seleção")
    btn_limpar.grid(row=0, column=6, padx=10)

    frame_main = tk.Frame(win)
    frame_main.pack(fill="both", expand=True)

    # ============================================================
    # TREEVIEW DE CONTAS
    # ============================================================
    frame_contas = tk.Frame(frame_main)
    frame_contas.pack(side="left", fill="y", padx=10, pady=10)

    tk.Label(frame_contas, text="Contas (selecione várias)").pack(anchor="w")

    scroll_contas_y = tk.Scrollbar(frame_contas, orient="vertical")

    tree_contas = ttk.Treeview(
        frame_contas,
        columns=("conta", "descr"),
        show="headings",
        height=25,
        selectmode="extended",
        yscrollcommand=scroll_contas_y.set
    )

    scroll_contas_y.config(command=tree_contas.yview)
    scroll_contas_y.pack(side="right", fill="y")

    tree_contas.pack(side="left", fill="y", expand=True)

    tree_contas.heading("conta", text="Conta")
    tree_contas.heading("descr", text="Descrição")
    tree_contas.column("conta", width=100, anchor="w", stretch=False)
    tree_contas.column("descr", width=250, anchor="w", stretch=False)

    tree_contas.tag_configure("selecionada", background="#cce5ff")

    for codcta, descrcta, *_ in contas:
        tree_contas.insert("", tk.END, iid=str(codcta), values=(codcta, descrcta))

    def marcar_selecao(event):
        for item in tree_contas.get_children():
            tree_contas.item(item, tags=())
        for item in tree_contas.selection():
            tree_contas.item(item, tags=("selecionada",))

    tree_contas.bind("<<TreeviewSelect>>", marcar_selecao)

    def limpar_selecao():
        for item in tree_contas.get_children():
            tree_contas.selection_remove(item)
            tree_contas.item(item, tags=())

    btn_limpar.config(command=limpar_selecao)

    # ============================================================
    # TREEVIEW DE SALDOS
    # ============================================================
    frame_spread = tk.Frame(frame_main)
    frame_spread.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    scroll_y = tk.Scrollbar(frame_spread, orient="vertical")
    scroll_x = tk.Scrollbar(frame_spread, orient="horizontal")

    tree_saldos = ttk.Treeview(
        frame_spread,
        columns=[],
        show="headings",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    scroll_y.config(command=tree_saldos.yview)
    scroll_x.config(command=tree_saldos.xview)

    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    tree_saldos.pack(side="left", fill="both", expand=True)

    tree_saldos.tag_configure("zero", foreground="#999999")
    tree_saldos.tag_configure("total", background="#e0e0e0", foreground="blue")

    # ============================================================
    # ATUALIZAR SPREAD — LÓGICA CORRIGIDA
    # ============================================================
    def atualizar_spread(lista_contas, data_ini, data_fim):
        meses = []
        ano = data_ini.year
        mes = data_ini.month

        while True:
            meses.append((mes, ano))
            if ano == data_fim.year and mes == data_fim.month:
                break
            mes += 1
            if mes == 13:
                mes = 1
                ano += 1

        cols = ["conta", "descrcta", "saldo_inicial"]
        for m, a in meses:
            cols.append(f"{m:02d}/{a}")
        cols.append("saldo_final")

        tree_saldos["columns"] = cols

        for c in cols:
            tree_saldos.heading(c, text=c)
            tree_saldos.column(c, width=120, anchor="e", stretch=False)

        tree_saldos.column("conta", width=100, anchor="w", stretch=False)
        tree_saldos.column("descrcta", width=250, anchor="w", stretch=False)

        for item in tree_saldos.get_children():
            tree_saldos.delete(item)

        totais = {c: 0 for c in cols}

        for conta, descrcta in lista_contas:
            saldo_ini = buscar_saldo_inicial(conta, data_ini)
            print("saldo_ini em atualizar_spread-->", saldo_ini)

            linha = {
                "conta": conta,
                "descrcta": descrcta,
                "saldo_inicial": saldo_ini
            }

            nets = calcular_net_mensal(conta, data_ini, data_fim)
         #
         #    print("nets---->",nets)
            acumulado = saldo_ini
            conta_str = str(conta)
            acumula = conta_str in SALDOS_FIXOS

            for m, a in meses:   # <-- AGORA DENTRO DO BLOCO DA CONTA
                comp = f"{a}{m:02d}"

                valor_mes = 0.0
                for comp_sql, net in nets:
                    if str(comp_sql).strip() == str(comp).strip():
                        valor_mes = float(net)
                        break

                if acumula:
                    print("m-->",m,"a==>",a,"vlrMes-->", valor_mes,"acumulado",acumulado)
                    acumulado += valor_mes
                    linha[f"{m:02d}/{a}"] = acumulado
                else:
                    linha[f"{m:02d}/{a}"] = valor_mes

            linha["saldo_final"] = acumulado if acumula else sum(
                linha[f"{m:02d}/{a}"] for m, a in meses
            )

            valores = [linha[c] for c in cols]
            tree_saldos.insert("", tk.END, values=valores)

            for idx, c in enumerate(cols):
                try:
                    totais[c] += float(valores[idx])
                except:
                    pass


        linha_total = ["TOTAL", ""]

        linha_total.append(
            f"{totais['saldo_inicial']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        for m, a in meses:
            chave = f"{m:02d}/{a}"
            valor = totais[chave]
            linha_total.append(
                f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

        linha_total.append(
            f"{totais['saldo_final']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        tree_saldos.insert("", tk.END, values=linha_total, tags=("total",))

    # ============================================================
    # BOTÃO DEMONSTRAR
    # ============================================================
    def demonstrar():
        mmaaaa_ini = ent_ini.get().strip()
        if len(mmaaaa_ini) != 6 or not mmaaaa_ini.isdigit():
            return None, None

        mes = int(mmaaaa_ini[:2])
        ano = int(mmaaaa_ini[2:])

        data_ini = datetime(ano, mes, 1)

#        print("mmaaaa_ini===========>",mmaaaa_ini)
#        data_ini, _ = mm_aaaa_para_datas(mmaaaa_ini)
        mmaaaa_fim = ent_fim.get().strip()
        if len(mmaaaa_fim) != 6 or not mmaaaa_fim.isdigit():
            return None, None
        mes = int(mmaaaa_fim[:2])
        ano = int(mmaaaa_fim[2:])
        ultimo_dia = monthrange(ano, mes)[1]
        data_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)
 
#        print("mmaaaa_fim=================>",mmaaaa_fim)
#        data_fim, _ = mm_aaaa_para_datas(mmaaaa_fim)
        
        print("data_ini----->",data_ini)
        print("data_fim---->", data_fim)

        if not data_ini or not data_fim:
            messagebox.showerror("Erro", "Informe períodos válidos no formato MMAAAA.")
            return

        selecionadas = tree_contas.selection()

        if not selecionadas:
            lista = [(r[0], r[1]) for r in contas]
        else:
            lista = []
            for iid in selecionadas:
                conta = tree_contas.item(iid)["values"][0]
                descr = tree_contas.item(iid)["values"][1]
                lista.append((conta, descr))

        atualizar_spread(lista, data_ini, data_fim)

    btn_demo.config(command=demonstrar)
