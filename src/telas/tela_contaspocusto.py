import tkinter as tk
from tkinter import messagebox, ttk
import src.sql.sql_contaspocusto as sql
import src.sql.sql_cadconta as sql_conta
from src.core.db import get_connection


def tela_contaspocusto():

    janela = tk.Toplevel()
    janela.title("Cadastro de Tipos de Custo")
    janela.geometry("900x700")  # janela maior
    janela.grab_set()
    janela.focus_force()

    # ============================
    # VALIDADORES
    # ============================

    def limitar_5(P):
        return len(P) <= 5

    def somente_numeros_percentual(P):
        if P == "":
            return True
        try:
            v = float(P.replace(",", "."))
            return 0 <= v <= 100
        except:
            return False

    validar_5 = janela.register(limitar_5)
    validar_perc = janela.register(somente_numeros_percentual)

    registro_original = {"TPCUSTO": None, "CONTA": None}

    # ============================
    # FUNÇÕES PRINCIPAIS
    # ============================

    def carregar_contas():
        contas = sql_conta.listar()
        combo_conta['values'] = [f"{c[0]} - {c[1]}" for c in contas]

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

            entry_tpCusto.delete(0, tk.END)
            entry_tpCusto.insert(0, valores[0])

            combo_conta.set(valores[1])

            entry_percentual.delete(0, tk.END)
            entry_percentual.insert(0, valores[2])

            registro_original["TPCUSTO"] = valores[0]
            registro_original["CONTA"] = valores[1]

            btn_atualizar.config(state="normal")
            btn_excluir.config(state="normal")
            btn_inserir.config(state="disabled")

    def bloquear_botoes(event=None):
        btn_atualizar.config(state="disabled")
        btn_excluir.config(state="disabled")

    def ao_selecionar(event):
        btn_inserir.config(state="disabled")

    def limpar_campos():
        entry_tpCusto.delete(0, tk.END)
        combo_conta.set("")
        entry_percentual.delete(0, tk.END)

        tree.selection_remove(tree.selection())

        btn_inserir.config(state="normal")
        btn_atualizar.config(state="disabled")
        btn_excluir.config(state="disabled")

    def inserir():
        if not messagebox.askyesno("Confirmação", "Deseja inserir este registro?"):
            return

        tp = entry_tpCusto.get()
        conta = combo_conta.get().split(" - ")[0]
        perc = entry_percentual.get().replace(",", ".")

        if not tp or not conta or not perc:
            messagebox.showwarning("Campos", "Preencha todos os campos.")
            return

        if sql.existe(tp, conta):
            messagebox.showwarning("Duplicado", "Este registro já existe!")
            return

        ok = sql.inserir(tp, conta, perc)
        if ok:
            atualizar_lista()
            messagebox.showinfo("OK", "Registro inserido.")
        else:
            messagebox.showwarning("Erro", "Não foi possível inserir.")

    def atualizar():
        if not messagebox.askyesno("Confirmação", "Deseja atualizar este registro?"):
            return

        tp_original = registro_original["TPCUSTO"]
        conta_original = registro_original["CONTA"]

        if tp_original is None or conta_original is None:
            messagebox.showwarning("Erro", "Selecione um registro antes de atualizar.")
            return

        if not sql.existe(tp_original, conta_original):
            messagebox.showerror("Inexistente", "O registro original não existe mais.")
            return

        tp_novo = entry_tpCusto.get()
        conta_novo = combo_conta.get().split(" - ")[0]
        perc_novo = entry_percentual.get().replace(",", ".")

        if (tp_novo != tp_original or conta_novo != conta_original) and sql.existe(tp_novo, conta_novo):
            messagebox.showwarning("Duplicado", "Já existe um registro com esta nova chave.")
            return

        sql.excluir(tp_original, conta_original)
        sql.inserir(tp_novo, conta_novo, perc_novo)

        atualizar_lista()
        messagebox.showinfo("OK", "Registro atualizado.")

        registro_original["TPCUSTO"] = None
        registro_original["CONTA"] = None

    def excluir():
        if not messagebox.askyesno("Confirmação", "Deseja excluir este registro?"):
            return

        tp = entry_tpCusto.get()
        conta = combo_conta.get().split(" - ")[0]

        if not sql.existe(tp, conta):
            messagebox.showerror("Inexistente", "Este registro não existe.")
            return

        sql.excluir(tp, conta)
        atualizar_lista()
        messagebox.showinfo("OK", "Registro excluído.")

    # ============================
    # CAMPOS
    # ============================

    tk.Label(janela, text="Código Tipo de Custo").pack()
    entry_tpCusto = tk.Entry(janela, validate="key", validatecommand=(validar_5, "%P"))
    entry_tpCusto.pack()
    entry_tpCusto.bind("<KeyRelease>", bloquear_botoes)

    tk.Label(janela, text="Conta Contábil envolvida").pack()
    combo_conta = ttk.Combobox(janela, width=50)
    combo_conta.pack()
    combo_conta.bind("<<ComboboxSelected>>", bloquear_botoes)

    tk.Label(janela, text="Percentual").pack()
    entry_percentual = tk.Entry(janela, validate="key", validatecommand=(validar_perc, "%P"))
    entry_percentual.pack()

    # ============================
    # TREEVIEW
    # ============================

    frame_tree = tk.Frame(janela)
    frame_tree.pack(pady=10, fill="both", expand=True)

    colunas = ("TPCUSTO", "CONTA", "PERCENTUAL")
    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=200)

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

    btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar)
    btn_atualizar.pack(side="left", padx=5)

    btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir)
    btn_excluir.pack(side="left", padx=5)

    tk.Button(frame_botoes, text="Finalizar", command=janela.destroy).pack(side="left", padx=5)

    btn_atualizar.config(state="disabled")
    btn_excluir.config(state="disabled")

    carregar_contas()
    atualizar_lista()
