import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import src.sql.sql_cadconta as sql

def tela_cadconta():

    janela = tk.Toplevel()
    janela.title("Cadastro de Contas")
    janela.geometry("1200x700")
    janela.grab_set()
    janela.focus_force()

    registro_original = {"CODCTA": None}

    # ===========================
    # VALIDAÇÕES
    # ===========================
    def somente_numeros(P):
        return P.isdigit() or P == ""

    def limitar_5(P):
        return len(P) <= 5

    def limitar_50(P):
        return len(P) <= 50

    validar_num = janela.register(somente_numeros)
    validar_5 = janela.register(limitar_5)
    validar_50 = janela.register(limitar_50)

    # ===========================
    # CARREGAR COMBOS
    # ===========================
    def carregar_comboboxes():
        grupos = sql.listar_grupos()
        valores = ["TODOS"] + [f"{g[0]} - {g[1]}" for g in grupos]
        combo_grupo['values'] = valores
        combo_grupo.set("TODOS")

        custos = sql.listar_tipos_custo()
        combo_tpcusto['values'] = [c[0] for c in custos]

    # ===========================
    # ATUALIZAR LISTA
    # ===========================
    def atualizar_lista():
        grupo = combo_grupo.get()

        for item in tree.get_children():
            tree.delete(item)

        if grupo == "TODOS":
            linhas = sql.listar()
        else:
            cod_agr = grupo.split(" - ")[0]
            linhas = sql.listar_por_grupo(cod_agr)

        for r in linhas:
            tree.insert("", tk.END, values=(r[0], r[1], r[2], r[4], r[5], r[6]))

    # ===========================
    # ORDENAR COLUNAS
    # ===========================
    def ordenar(col):
        dados = [(tree.set(k, col), k) for k in tree.get_children("")]
        dados.sort()
        for index, (val, k) in enumerate(dados):
            tree.move(k, "", index)

    # ===========================
    # PREENCHER CAMPOS AO CLICAR
    # ===========================
    def preencher_campos(event):
        item = tree.selection()
        if not item:
            return

        valores = tree.item(item, "values")

        codcta = valores[0]
        descr = valores[1]
        codagr = valores[2]
        tpcusto = valores[3]
        natureza = valores[4]
        dtaabert = valores[5]

        # ====== AJUSTE: MUDAR COMBO DE AGRUPAMENTO AUTOMATICAMENTE ======
        for v in combo_grupo['values']:
            if v.startswith(codagr):
                combo_grupo.set(v)
                break

        atualizar_lista()

        # ====== Preencher campos ======
        entry_cod.delete(0, tk.END)
        entry_cod.insert(0, codcta)

        entry_desc.delete(0, tk.END)
        entry_desc.insert(0, descr)

        combo_tpcusto.set(tpcusto)
        var_natureza.set(natureza)

        entry_dtaabert.delete(0, tk.END)
        entry_dtaabert.insert(0, dtaabert)

        registro_original["CODCTA"] = codcta
        btn_inserir.config(state="disabled")

    # ===========================
    # GERAR CÓDIGO AUTOMÁTICO
    # ===========================
    def gerar_codigo():
        grupo = combo_grupo.get()
        if grupo == "TODOS":
            return

        agr = grupo.split(" - ")[0]
        prefixo = agr[:3]

        maior = 0
        for r in sql.listar():
            if r[0].startswith(prefixo):
                try:
                    num = int(r[0][3:])
                    maior = max(maior, num)
                except:
                    pass

        novo = f"{prefixo}{str(maior + 1).zfill(2)}"
        entry_cod.delete(0, tk.END)
        entry_cod.insert(0, novo)

    # ===========================
    # INSERIR
    # ===========================
    def inserir():
        cod = entry_cod.get()
        desc = entry_desc.get()
        grupo = combo_grupo.get()

        if grupo == "TODOS":
            messagebox.showwarning("Agrupamento", "Selecione um agrupamento antes de inserir.")
            return

        agr = grupo.split(" - ")[0]
        prefixo = agr[:3]

        # ====== VALIDAR RADICAL ======
        if not cod.startswith(prefixo):
            messagebox.showerror("Código inválido",
                                 f"O código deve começar com '{prefixo}'.")
            return

        custo = combo_tpcusto.get()
        natureza = var_natureza.get()
        dtaabert = entry_dtaabert.get()

        if not cod or not desc or not custo or not natureza or not dtaabert:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        if sql.existe(cod):
            messagebox.showwarning("Duplicado", "Já existe uma conta com este código.")
            return

        sql.inserir(cod, desc, agr, custo, natureza, dtaabert)
        atualizar_lista()
        messagebox.showinfo("OK", "Conta inserida.")

    # ===========================
    # ATUALIZAR (NOVO COMPORTAMENTO)
    # ===========================
    def atualizar():
        cod_original = registro_original["CODCTA"]

        if cod_original is None:
            messagebox.showwarning("Erro", "Selecione uma conta antes de atualizar.")
            return

        desc = entry_desc.get()
        custo = combo_tpcusto.get()
        natureza = var_natureza.get()
        dtaabert = datetime.now().strftime("%d/%m/%Y")  # DATA CORRENTE

        if not desc or not custo or not natureza:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        # AGRUPAMENTO MASTER
        grupo = combo_grupo.get()
        agr = grupo.split(" - ")[0]

        # UPDATE REAL
        sql.atualizar(cod_original, desc, agr, custo, natureza, dtaabert)

        atualizar_lista()
        messagebox.showinfo("OK", "Conta atualizada.")

        registro_original["CODCTA"] = None
        btn_inserir.config(state="normal")

    # ===========================
    # EXCLUIR
    # ===========================
    def excluir():
        cod = entry_cod.get()

        if not sql.existe(cod):
            messagebox.showerror("Inexistente", "Esta conta não existe.")
            return

        sql.excluir(cod)
        atualizar_lista()
        messagebox.showinfo("OK", "Conta excluída.")

        btn_inserir.config(state="normal")

    # ===========================
    # INTERFACE
    # ===========================

    # AGRUPAMENTO MASTER
    tk.Label(janela, text="Agrupamento (CADCTAAGR)").pack()
    combo_grupo = ttk.Combobox(janela, width=60, state="readonly")
    combo_grupo.pack()
    combo_grupo.bind("<<ComboboxSelected>>", lambda e: [atualizar_lista(), gerar_codigo()])

    # CAMPOS
    frame_campos = tk.Frame(janela)
    frame_campos.pack(pady=10)

    tk.Label(frame_campos, text="Código da Conta").grid(row=0, column=0)
    entry_cod = tk.Entry(frame_campos, validate="key",
                         validatecommand=(validar_num, "%P"))
    entry_cod.grid(row=0, column=1)
    entry_cod.config(validatecommand=(validar_5, "%P"))

    tk.Label(frame_campos, text="Descrição").grid(row=1, column=0)
    entry_desc = tk.Entry(frame_campos, width=80, validate="key",
                          validatecommand=(validar_50, "%P"))
    entry_desc.grid(row=1, column=1)

    tk.Label(frame_campos, text="Tipo de Custo").grid(row=2, column=0)
    combo_tpcusto = ttk.Combobox(frame_campos, width=50)
    combo_tpcusto.grid(row=2, column=1)

    tk.Label(frame_campos, text="Natureza").grid(row=3, column=0)
    var_natureza = tk.StringVar(value="D")
    tk.Radiobutton(frame_campos, text="Débito (D)", variable=var_natureza, value="D").grid(row=3, column=1)
    tk.Radiobutton(frame_campos, text="Crédito (C)", variable=var_natureza, value="C").grid(row=3, column=2)

    tk.Label(frame_campos, text="Data de Abertura").grid(row=4, column=0)
    entry_dtaabert = tk.Entry(frame_campos)
    entry_dtaabert.grid(row=4, column=1)
    entry_dtaabert.insert(0, datetime.now().strftime("%d/%m/%Y"))

    # SPREAD
    frame_tree = tk.Frame(janela)
    frame_tree.pack()

    colunas = ("CODCTA", "DESCRCTA", "CODCTAAGR", "TPCUSTO", "NATUREZA", "DTAABERT")
    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", height=20)

    tree.heading("CODCTA", text="CODCTA", command=lambda: ordenar("CODCTA"))
    tree.heading("DESCRCTA", text="DESCRCTA", command=lambda: ordenar("DESCRCTA"))
    tree.heading("CODCTAAGR", text="CODCTAAGR", command=lambda: ordenar("CODCTAAGR"))
    tree.heading("TPCUSTO", text="TPCUSTO", command=lambda: ordenar("TPCUSTO"))
    tree.heading("NATUREZA", text="NATUREZA", command=lambda: ordenar("NATUREZA"))
    tree.heading("DTAABERT", text="DTAABERT", command=lambda: ordenar("DTAABERT"))

    # LARGURAS PROPORCIONAIS
    tree.column("CODCTA", width=120)
    tree.column("DESCRCTA", width=350)
    tree.column("CODCTAAGR", width=120)
    tree.column("TPCUSTO", width=120)
    tree.column("NATUREZA", width=90)
    tree.column("DTAABERT", width=120)

    scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0)
    scrollbar.grid(row=0, column=1, sticky="ns")

    tree.bind("<<TreeviewSelect>>", preencher_campos)

    # BOTÕES
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)

    btn_inserir = tk.Button(frame_botoes, text="Inserir", command=inserir)
    btn_inserir.pack(side="left", padx=5)

    tk.Button(frame_botoes, text="Atualizar", command=atualizar).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Excluir", command=excluir).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Finalizar", command=janela.destroy).pack(side="left", padx=5)

    carregar_comboboxes()
    atualizar_lista()
