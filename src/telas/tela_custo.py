import tkinter as tk
from tkinter import messagebox, ttk
import src.sql.sql_custo as sql

def tela_custo():

    janela = tk.Toplevel()
    janela.title("Cadastro de Custos")
    janela.geometry("600x600")
    janela.grab_set()
    janela.focus_force()

    def limitar_5(P):
        return len(P) <= 5

    def limitar_50(P):
        return len(P) <= 50

    validar_5 = janela.register(limitar_5)
    validar_50 = janela.register(limitar_50)

    registro_original = {"TPCUSTO": None}

    def atualizar_lista():
        for item in tree.get_children():
            tree.delete(item)
        for r in sql.listar():
            tree.insert("", tk.END, values=(r[0], r[1]))

    def preencher_campos(event):
        item = tree.selection()
        if item:
            valores = tree.item(item, "values")
            entry_tp.delete(0, tk.END)
            entry_tp.insert(0, valores[0])
            entry_nome.delete(0, tk.END)
            entry_nome.insert(0, valores[1])
            registro_original["TPCUSTO"] = valores[0]
            btn_atualizar.config(state="normal")
            btn_excluir.config(state="normal")

    def bloquear_botoes(event=None):
        btn_atualizar.config(state="disabled")
        btn_excluir.config(state="disabled")

    def inserir():
        tp = entry_tp.get()
        nome = entry_nome.get()

        if not tp or not nome:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        if sql.existe(tp):
            messagebox.showwarning("Duplicado", "Já existe este tipo de custo.")
            return

        sql.inserir(tp, nome)
        atualizar_lista()
        messagebox.showinfo("OK", "Registro inserido.")

    def atualizar():
        tp_original = registro_original["TPCUSTO"]
        if tp_original is None:
            messagebox.showwarning("Erro", "Selecione um registro.")
            return

        tp_novo = entry_tp.get()
        nome_novo = entry_nome.get()

        if tp_novo != tp_original and sql.existe(tp_novo):
            messagebox.showwarning("Duplicado", "Já existe este novo código.")
            return

        sql.excluir(tp_original)
        sql.inserir(tp_novo, nome_novo)

        atualizar_lista()
        messagebox.showinfo("OK", "Registro atualizado.")
        registro_original["TPCUSTO"] = None

    def excluir():
        tp = entry_tp.get()
        if not sql.existe(tp):
            messagebox.showerror("Inexistente", "Este registro não existe.")
            return
        sql.excluir(tp)
        atualizar_lista()
        messagebox.showinfo("OK", "Registro excluído.")

    tk.Label(janela, text="Código Tipo de Custo").pack()
    entry_tp = tk.Entry(janela, validate="key", validatecommand=(validar_5, "%P"))
    entry_tp.pack()
    entry_tp.bind("<KeyRelease>", bloquear_botoes)

    tk.Label(janela, text="Nome do Custo").pack()
    entry_nome = tk.Entry(janela, validate="key", validatecommand=(validar_50, "%P"))
    entry_nome.pack()

    frame_tree = tk.Frame(janela)
    frame_tree.pack(pady=10)

    colunas = ("TPCUSTO", "NOMECUSTO")
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
