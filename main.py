from src.database.connection import get_connection
import tkinter as tk
from tkinter import messagebox

# Tela de saldos mensais (nova)
from src.telas.tela_saldos import tela_saldos_mensais

# Funções de manutenção de saldos
from src.utils.processa_saldos import (
    recompor_saldos,
    limpar_base,
    mostrar_saldos_iniciais_faltantes
)

# Telas já existentes
from src.telas.tela_cadctaagr import tela_cadctaagr
from src.telas.tela_contaspocusto import tela_contaspocusto
from src.telas.tela_cadconta import tela_cadconta

# Novos cadastros
from src.telas.tela_custo import tela_custo
from src.telas.tela_roteirocapa import tela_roteirocapa
from src.telas.tela_roteirodeta import tela_roteirodeta
from src.telas.tela_tipolote import tela_tipolote

# Tela de movimento (lançamentos)
from src.telas.tela_lancamentos import tela_lancamentos

# Configuração de ambiente
from src.core import config


# ============================================================
# JANELA DE ESCOLHA DE AMBIENTE
# ============================================================
def escolher_ambiente(root):
    janela = tk.Toplevel(root)
    janela.title("Escolher Ambiente")
    janela.geometry("350x250")
    janela.grab_set()

    tk.Label(janela, text="Selecione o ambiente:", font=("Arial", 12)).pack(pady=10)

    var_modo = tk.StringVar(value=config.get_modo())
    var_alerta = tk.StringVar(value=config.get_alerta())

    tk.Radiobutton(janela, text="DESENVOLVIMENTO", variable=var_modo, value="DESENV").pack(anchor="w", padx=20)
    tk.Radiobutton(janela, text="PRODUÇÃO", variable=var_modo, value="PRODUC").pack(anchor="w", padx=20)

    tk.Label(janela, text="Mostrar alerta de ambiente?", font=("Arial", 10)).pack(pady=10)
    tk.Radiobutton(janela, text="Sim", variable=var_alerta, value="SIM").pack(anchor="w", padx=20)
    tk.Radiobutton(janela, text="Não", variable=var_alerta, value="NAO").pack(anchor="w", padx=20)

    def confirmar():
        novo = var_modo.get()
        alerta = var_alerta.get()

        if messagebox.askyesno("Confirmar", f"Confirma trocar para ambiente {novo}?"):
            config.set_modo(novo)
            config.set_alerta(alerta)
            messagebox.showinfo("Ambiente", "Alteração aplicada.\nReabra as telas para usar o novo ambiente.")
            janela.destroy()

    tk.Button(janela, text="Confirmar", command=confirmar).pack(pady=15)


# ============================================================
# MAIN
# ============================================================
def main():
    root = tk.Tk()
    root.title("Sistema de Cadastros")
    root.geometry("600x400")

    menubar = tk.Menu(root)

    # === MENU CADASTRO ===
    menu_cadastro = tk.Menu(menubar, tearoff=0)
    menu_cadastro.add_command(label="Cadastro de Grupos de Contas", command=tela_cadctaagr)
    menu_cadastro.add_command(label="Cadastro de Tipos de Custo (ContasPorCusto)", command=tela_contaspocusto)
    menu_cadastro.add_command(label="Cadastro de Contas", command=tela_cadconta)

    menu_cadastro.add_separator()
    menu_cadastro.add_command(label="Cadastro de Custos", command=tela_custo)
    menu_cadastro.add_command(label="Cadastro de Roteiro - Capa", command=tela_roteirocapa)
    menu_cadastro.add_command(label="Cadastro de Roteiro - Detalhe", command=tela_roteirodeta)
    menu_cadastro.add_command(label="Cadastro de Tipo de Lote", command=tela_tipolote)

    menubar.add_cascade(label="Cadastros", menu=menu_cadastro)

    # === MENU MOVIMENTO ===
    menu_movimento = tk.Menu(menubar, tearoff=0)
    menu_movimento.add_command(label="Lançamentos Diários", command=tela_lancamentos)
    menu_movimento.add_command(label="Saldos Mensais", command=tela_saldos_mensais)
    menubar.add_cascade(label="Movimento", menu=menu_movimento)

    # === MENU AJUDA ===
    menu_ajuda = tk.Menu(menubar, tearoff=0)
    menu_ajuda.add_command(label="Reprocessar Saldos", command=recompor_saldos)
    menu_ajuda.add_command(label="Limpar Base de Saldos", command=limpar_base)
    menu_ajuda.add_command(label="Verificar Saldos Iniciais", command=mostrar_saldos_iniciais_faltantes)
    menu_ajuda.add_command(label="Escolher Ambiente", command=lambda: escolher_ambiente(root))
    menubar.add_cascade(label="Ajuda", menu=menu_ajuda)

    # === MENU FINALIZAR ===
    menu_finalizar = tk.Menu(menubar, tearoff=0)
    menu_finalizar.add_command(label="Sair do Sistema", command=root.destroy)
    menubar.add_cascade(label="Finalizar", menu=menu_finalizar)

    root.config(menu=menubar)

    label = tk.Label(root, text="Bem-vindo ao Sistema de Cadastros", font=("Arial", 16))
    label.pack(pady=40)

    if config.get_alerta() == "SIM":
        ambiente = config.get_modo()
        aviso = tk.Label(root, text=f"AMBIENTE ATUAL: {ambiente}", fg="red", font=("Arial", 12))
        aviso.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()



