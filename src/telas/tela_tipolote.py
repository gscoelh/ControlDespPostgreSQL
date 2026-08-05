import tkinter as tk
from tkinter import messagebox, ttk
import src.sql.sql_tipolote as sql
from datetime import datetime

def tela_tipolote():

    janela = tk.Toplevel()
    janela.title("Cadastro de Tipo de Lote")
    janela.geometry("600x600")
    janela.grab_set()
    janela.focus_force()

    def limitar_5(P):
        return len(P) <= 5

    def limitar_50(P):
        return len(P) <= 50

    validar_5 = janela.register(limitar_5)
    validar_50 = janela.register(limitar_50)

    registro_original = {"CODLOTE": None}

    def atualizar_lista():
        for item in tree.get_children():
            tree.delete(item)
        for r in sql.listar():
            tree.insert("", tk.END, values=(r[0], r[1], r[2]))

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

            registro_original["CODLOTE"] = valores[0]
            btn_atualizar.config(state="normal")
            btn_excluir.config(state="normal")

    def bloquear_botoes(event=None):
        btn_atualizar.config(state="disabled")
        btn_excluir.config(state="disabled")

    def inserir():
        cod = entry_cod.get()
        desc = entry_desc.get()
        dta = entry_dta.get()

        if not cod or not desc or not dta:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        if sql.existe(cod):
            messagebox.showwarning("Duplicado", "Já existe este tipo de lote.")
            return

        sql.inserir(cod, desc, dta)
        atualizar_lista()
        messagebox.showinfo("OK", "Registro inserido.")

    def atualizar():
        cod_original = registro_original["CODLOTE"]
        if cod_original is None:
            messagebox.showwarning("Erro", "Selecione um registro.")
            return

        cod_novo = entry_cod.get()
        desc_novo = entry_desc.get()
        dta_novo = entry_dta.get()

        if cod_novo != cod_original and sql.existe(cod_novo):
            messagebox.showwarning("Duplicado", "Já existe este novo código.")
            return

        sql.excluir(cod_original)
        sql.inserir(cod_novo, desc_novo, dta_novo)

        atualizar_lista()
        messagebox.showinfo("OK", "Registro atualizado.")
        registro_original["CODLOTE"] = None

    def excluir():
        cod = entry_cod.get()
        if not sql.existe(cod):
            messagebox.showerror("Inexistente", "Este registro não existe.")
            return
        sql.excluir(cod)
        atualizar_lista()
        messagebox.showinfo("OK", "Registro excluído.")

    tk.Label(janela, text="Código do Lote").pack()
    entry_cod = tk.Entry(janela, validate="key",
                         validatecommand=(validar_5, "%P"))
    entry_cod.pack()
    entry_cod.bind("<KeyRelease>", bloquear_botoes)

    tk.Label(janela, text="Descrição do Lote").pack()
    entry_desc = tk.Entry(janela, validate="key",
                          validatecommand=(validar_50, "%P"))
    entry_desc.pack()

    tk.Label(janela, text="Data de Abertura (dd/mm/aaaa)").pack()
    entry_dta = tk.Entry(janela)
    entry_dta.pack()
    entry_dta.insert(0, datetime.now().strftime("%d/%m/%Y"))

    frame_tree = tk.Frame(janela)
    frame_tree.pack(pady=10)

    colunas = ("CODLOTE", "DESCRLOTE", "DTAABERTURA")
    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", height=15)
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0)
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.bind("<<TreeviewSelect>>", preencher_campos)

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)

    tk.Button(frame_botoes, text="Inserir", command=inserir).pack(side="left", padx=5)
    btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar)
    btn_atualizar.pack(side="left", padx=5)
    btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir)
    btn_excluir.pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Finalizar", command=janela.destroy).pack(side="left", padx=5)

    btn_atualizar.config(state="disabled")
    btn_excluir.config(state="disabled")

    atualizar_lista()
