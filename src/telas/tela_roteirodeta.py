import tkinter as tk
from tkinter import ttk, messagebox

import src.sql.sql_roteirocapa as sql_capa
import src.sql.sql_roteirodeta as sql_deta
import src.sql.sql_cadconta as sql_conta


def tela_roteirodeta():

    janela = tk.Toplevel()
    janela.title("Cadastro de Roteiro - Detalhe")
    janela.geometry("900x600")
    janela.grab_set()

    # ===========================
    # CABEÇALHO
    # ===========================
    frame_top = tk.Frame(janela)
    frame_top.pack(fill="x", pady=10)

    tk.Label(frame_top, text="Roteiro (Capa)").pack(side="left", padx=5)
    combo_roteiro = ttk.Combobox(frame_top, width=50, state="readonly")
    combo_roteiro.pack(side="left", padx=5)

    roteiros = sql_capa.listar()
    combo_roteiro["values"] = [f"{r[0]} - {r[2]}" for r in roteiros]

    # ===========================
    # NATUREZA DO ROTEIRO
    # ===========================
    frame_nat = tk.LabelFrame(janela, text="Natureza")
    frame_nat.pack(fill="x", padx=10, pady=10)

    lbl_nat_capa = tk.Label(frame_nat, text="Natureza do Roteiro (Capa): ")
    lbl_nat_capa.pack(anchor="w")

    lbl_nat_detalhe = tk.Label(frame_nat, text="Natureza do Detalhe (automática): ")
    lbl_nat_detalhe.pack(anchor="w")

    # ===========================
    # CONTA (somente 1 combo)
    # ===========================
    frame_conta = tk.LabelFrame(janela, text="Conta para o Detalhe")
    frame_conta.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_conta, text="Conta:").pack(anchor="w")
    combo_conta = ttk.Combobox(frame_conta, width=50, state="readonly")
    combo_conta.pack(padx=5, pady=5)

    # rótulo para feedback visual
    lbl_conta_status = tk.Label(frame_conta, text="", fg="red")
    lbl_conta_status.pack(anchor="w", padx=5)

    # ===========================
    # HISTÓRICO
    # ===========================
    frame_hist = tk.LabelFrame(janela, text="Histórico")
    frame_hist.pack(fill="x", padx=10, pady=10)

    entry_hist = tk.Entry(frame_hist, width=80)
    entry_hist.pack(padx=10, pady=10)

    # ===========================
    # LISTA
    # ===========================
    frame_lista = tk.Frame(janela)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ROTNATUREZA", "ROTCTADEB", "ROTCTACRED", "ROTHIST")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=200)

    tree.pack(fill="both", expand=True)

    # ===========================
    # FUNÇÕES
    # ===========================
    def atualizar_lista_por_roteiro(rot):
        for item in tree.get_children():
            tree.delete(item)

        linhas = sql_deta.listar_por_roteiro(rot)
        for r in linhas:
            tree.insert("", tk.END, values=(r[1], r[2], r[3], r[4]))

    def carregar_contas_para_combo(rot):
        conta_capa = sql_capa.buscar_conta(rot)
        todas_contas = sql_conta.listar()

        contas = [
            c for c in todas_contas
            if c[0] != conta_capa
        ]

        combo_conta["values"] = [f"{c[0]} - {c[1]}" for c in contas]
        combo_conta.set("")
        lbl_conta_status.config(text="", fg="red")

    # ===========================
    # SELEÇÃO DO ROTEIRO
    # ===========================
    def on_select_roteiro(event):
        rot = combo_roteiro.get().split(" - ")[0]

        natureza_capa = sql_capa.buscar_natureza(rot)
        conta_capa = sql_capa.buscar_conta(rot)

        if not natureza_capa or not conta_capa:
            messagebox.showerror("Erro", "Roteiro sem natureza ou conta definida na capa.")
            return

        lbl_nat_capa.config(text=f"Natureza do Roteiro (Capa): {natureza_capa}")

        natureza_detalhe = "C" if natureza_capa == "D" else "D"
        lbl_nat_detalhe.config(text=f"Natureza do Detalhe (automática): {natureza_detalhe}")

        carregar_contas_para_combo(rot)
        atualizar_lista_por_roteiro(rot)

    combo_roteiro.bind("<<ComboboxSelected>>", on_select_roteiro)

    # ===========================
    # VALIDAÇÃO VISUAL DA CONTA
    # ===========================
    def validar_conta_visual():
        if not combo_conta.get():
            lbl_conta_status.config(text="", fg="red")
            return

        conta_escolhida = combo_conta.get().split(" - ")[0]
        todas_contas = [c[0] for c in sql_conta.listar()]

        if conta_escolhida not in todas_contas:
            lbl_conta_status.config(text="Conta inexistente no plano de contas.", fg="red")
        else:
            lbl_conta_status.config(text="Conta válida.", fg="green")

    combo_conta.bind("<<ComboboxSelected>>", lambda e: validar_conta_visual())

    # ===========================
    # INSERIR
    # ===========================
    def inserir():
        rot = combo_roteiro.get().split(" - ")[0]
        natureza_capa = sql_capa.buscar_natureza(rot)
        conta_capa = sql_capa.buscar_conta(rot)
        hist = entry_hist.get().strip()

        if not rot:
            messagebox.showwarning("Aviso", "Selecione um roteiro.")
            return

        if not natureza_capa or not conta_capa:
            messagebox.showerror("Erro", "Roteiro sem natureza ou conta definida na capa.")
            return

        if not hist:
            messagebox.showwarning("Aviso", "Informe o histórico.")
            return

        if not combo_conta.get():
            messagebox.showwarning("Aviso", "Escolha a conta.")
            return

        conta_escolhida = combo_conta.get().split(" - ")[0]

        todas_contas = [c[0] for c in sql_conta.listar()]
        if conta_escolhida not in todas_contas:
            lbl_conta_status.config(text="Conta inexistente no plano de contas.", fg="red")
            messagebox.showerror("Erro", "Conta inexistente no plano de contas.")
            return

        if natureza_capa == "D":
            rotnatureza = "C"
            rotctadeb = conta_capa
            rotctacred = conta_escolhida
        else:
            rotnatureza = "D"
            rotctadeb = conta_escolhida
            rotctacred = conta_capa

        if rotctadeb == rotctacred:
            messagebox.showerror("Erro", "Conta de débito e crédito não podem ser iguais.")
            return

        if sql_deta.existe_conta_no_roteiro(rot, rotctadeb, rotctacred):
            messagebox.showerror("Duplicidade", "Esta combinação já existe no roteiro.")
            return

        if not messagebox.askyesno(
            "Confirmar gravação",
            f"Roteiro: {rot}\n"
            f"Natureza do detalhe: {rotnatureza}\n"
            f"Conta Débito: {rotctadeb}\n"
            f"Conta Crédito: {rotctacred}\n\n"
            "Deseja confirmar?"
        ):
            return

        sql_deta.inserir(rot, rotnatureza, rotctadeb, rotctacred, hist)

        messagebox.showinfo("Sucesso", "Registro inserido com sucesso!")
        atualizar_lista_por_roteiro(rot)
        carregar_contas_para_combo(rot)
        entry_hist.delete(0, tk.END)

    # ===========================
    # EXCLUIR
    # ===========================
    def excluir():
        rot = combo_roteiro.get().split(" - ")[0]
        if not rot:
            messagebox.showwarning("Aviso", "Selecione um roteiro.")
            return

        item = tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return

        valores = tree.item(item, "values")
        rotnatureza, deb, cred, hist = valores

        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Excluir o detalhe?\n\n"
            f"Débito: {deb}\n"
            f"Crédito: {cred}\n"
            f"Histórico: {hist}"
        ):
            return

        sql_deta.excluir(rot, deb, cred)
        atualizar_lista_por_roteiro(rot)
        carregar_contas_para_combo(rot)
        messagebox.showinfo("Sucesso", "Registro excluído.")

    # ===========================
    # BOTÕES
    # ===========================
    frame_btn = tk.Frame(janela)
    frame_btn.pack(fill="x", pady=10)

    tk.Button(frame_btn, text="Inserir", command=inserir).pack(side="left", padx=10)
    tk.Button(frame_btn, text="Excluir", command=excluir).pack(side="left", padx=10)
    tk.Button(frame_btn, text="Finalizar", command=janela.destroy).pack(side="left", padx=10)
