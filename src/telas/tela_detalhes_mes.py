import tkinter as tk
from tkinter import ttk
from src.sql import sql_saldos

def tela_detalhes_mes(conta, mes, ano):
    win = tk.Toplevel()
    win.title(f"Detalhes do mês - Conta {conta} - {mes}/{ano}")
    win.geometry("700x500")

    cols = ("data","saldo_ant","debito","credito","saldo_atu")
    tree = ttk.Treeview(win, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120)

    tree.pack(fill="both", expand=True)

    dados = sql_saldos.listar_por_conta_e_mes(conta, mes, ano)

    for d in dados:
        tree.insert("", tk.END, values=d[2:])
