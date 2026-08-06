import tkinter as tk
from tkinter import ttk
from src.sql import sql_saldos
from src.utils.processa_saldos import recompor_saldos

def tela_saldos():
    win = tk.Toplevel()
    win.title("Saldos Diários por Conta")
    win.geometry("900x600")

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True)

    cols = ("conta","descrcta","data","saldo_ant","debito","credito","saldo_atu")
    tree = ttk.Treeview(frame, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120)

    tree.pack(fill="both", expand=True)

    def carregar():
        for i in tree.get_children():
            tree.delete(i)

        dados = sql_saldos.listar_por_periodo("2017-01-01", "2099-12-31")
        for d in dados:
            tree.insert("", tk.END, values=d)

    def reprocessar():
        recompor_saldos()
        carregar()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text="Carregar", command=carregar).pack(side="left")
    tk.Button(btn_frame, text="Reprocessar Saldos", command=reprocessar).pack(side="left")

    carregar()
