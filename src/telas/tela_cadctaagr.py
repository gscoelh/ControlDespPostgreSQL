import tkinter as tk
from tkinter import messagebox, ttk
import src.sql.sql_cadctaagr as sql
from datetime import datetime
from src.core.db import get_connection


def tela_cadctaagr():

    janela = tk.Toplevel()
    janela.title("Cadastro de Grupos de Contas")
    janela.geometry("900x700")  # janela maior
    janela.grab_set()
    janela.focus_force()

    # ============================
    # VALIDADORES
    # ============================

    def somente_numeros(P):
        return P.isdigit() or P == ""

    def limitar_5(P):
        return len(P) <= 5

    def limitar_50(P):
        return len(P) <= 50

    validar_num = janela.register(somente_numeros)
    validar_5 = janela.register(limitar_5)
    validar_50 = janela.register(limitar_50)

    registro_original = {"CODCTAAGR": None}

    # ============================
    # FUNÇÕES PRINCIPAIS
    # ============================

    def atualizar_lista():
        for item in tree.get_children():
            tree.delete(item)

        for r in sql.listar():
            tree.insert("", tk.END, values=(r[0], r[1], r[2]))

        limpar_campos()

    def preencher_campos(event):
        item = tree.selection()
        if item:
            valores = tree.item(item, "values")

            entry_cod.delete(0, tk.END)
            entry_cod.insert(0, valores[0])

            entry_desc.delete(0, tk.END)
            entry_desc.insert(0, valores[1])

            entry_dta.delete(0, tk.END)
            entry_dta.insert(0, valores[2])

            registro_original["CODCTAAGR"] = valores[0]

            ao_selecionar(event)

    def inserir():
        if not messagebox.askyesno("Confirmação", "Deseja inserir este grupo?"):
            return

        cod = entry_cod.get()
        desc = entry_desc.get()
        dta = entry_dta.get()

        if not cod or not desc or not dta:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        if sql.existe(cod):
            messagebox.showwarning("Duplicado", "Já existe um grupo com este código.")
            return

        sql.inserir(cod, desc, dta)
        atualizar_lista()
        messagebox.showinfo("OK", "Grupo inserido.")

    def atualizar():
        if not messagebox.askyesno("Confirmação", "Deseja atualizar este grupo?"):
            return

        cod_original = registro_original["CODCTAAGR"]

        if cod_original is None:
            messagebox.showwarning("Erro", "Selecione um grupo antes de atualizar.")
            return

        if not sql.existe(cod_original):
            messagebox.showerror("Inexistente", "O grupo original não existe mais.")
            return

        cod_novo = entry_cod.get()
        desc = entry_desc.get()
        dta = entry_dta.get()

        if cod_novo != cod_original and sql.existe(cod_novo):
            messagebox.showwarning("Duplicado", "Já existe um grupo com este novo código.")
            return

        sql.excluir(cod_original)
        sql.inserir(cod_novo, desc, dta)

        atualizar_lista()
        messagebox.showinfo("OK", "Grupo atualizado.")

        registro_original["CODCTAAGR"] = None

    def excluir():
        if not messagebox.askyesno("Confirmação", "Deseja excluir este grupo?"):
            return

        cod = entry_cod.get()

        if not sql.existe(cod):
            messagebox.showerror("Inexistente", "Este grupo não existe.")
            return

        if not pode_excluir_grupo(cod):
            messagebox.showerror("Erro", "Este grupo está sendo usado por contas. Exclua ou altere as contas antes.")
            return

        sql.excluir(cod)
        atualizar_lista()
        messagebox.showinfo("OK", "Grupo excluído.")

    def pode_excluir_grupo(codctaagr):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*) 
            FROM cadconta 
            WHERE codctaagr = %s
        """, (codctaagr,))
        qtd = cur.fetchone()[0]
        return qtd == 0

    # ============================
    # FUNÇÕES DE CONTROLE DE BOTÕES
    # ============================

    def ao_selecionar(event):
        btn_inserir.config(state="disabled")

    def limpar_campos():
        btn_inserir.config(state="normal")
        entry_cod.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        entry_dta.delete(0, tk.END)
        entry_dta.insert(0, datetime.now().strftime("%d/%m/%Y"))
        tree.selection_remove(tree.selection())

    # ============================
    # CAMPOS
    # ============================

    tk.Label(janela, text="Código do Grupo").pack()
    entry_cod = tk.Entry(janela, validate="key", validatecommand=(validar_num, "%P"))
    entry_cod.pack()
    entry_cod.config(validatecommand=(validar_5, "%P"))

    tk.Label(janela, text="Descrição do Grupo").pack()
    entry_desc = tk.Entry(janela, validate="key", validatecommand=(validar_50, "%P"))
    entry_desc.pack()

    tk.Label(janela, text="Data de Abertura (dd/mm/aaaa)").pack()
    entry_dta = tk.Entry(janela)
    entry_dta.pack()
    entry_dta.insert(0, datetime.now().strftime("%d/%m/%Y"))

    # ============================
    # TREEVIEW
    # ============================

    frame_tree = tk.Frame(janela)
    frame_tree.pack(pady=10, fill="both", expand=True)

    colunas = ("CODCTAAGR", "DESCRCTAAGR", "DTAABERTURA")
    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")

    for col in colunas:
        tree.heading(col, text=col)
        if col == "DESCRCTAAGR":
            tree.column(col, width=450)
        else:
            tree.column(col, width=150)

    scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    frame_tree.grid_rowconfigure(0, weight=1)
    frame_tree.grid_columnconfigure(0, weight=1)

    tree.bind("<<TreeviewSelect>>", preencher_campos)

    # ============================
    # BOTÕES
    # ============================

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)

    btn_inserir = tk.Button(frame_botoes, text="Inserir", command=inserir)
    btn_inserir.pack(side="left", padx=5)

    tk.Button(frame_botoes, text="Atualizar", command=atualizar).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Excluir", command=excluir).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Finalizar", command=janela.destroy).pack(side="left", padx=5)

    atualizar_lista()
