import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox

import os
import shutil
from datetime import datetime
import time
import webbrowser
from dateutil.relativedelta import relativedelta

import src.sql.sql_roteirocapa as sql_capa
import src.sql.sql_roteirodeta as sql_deta
import src.sql.sql_lancamentos as sql_lanc
import src.sql.sql_cadconta as sql_conta

from src.core import config

from datetime import datetime
from dateutil.relativedelta import relativedelta


PASTA_COMPROVANTES = config.get_pasta_comprovantes()
AUTOCOMP = set(config.get_complementos())
def verificar_competencia_cartao(conta, anomes):
    """
    Verifica se existe dia de corte cadastrado para a conta no mês AAAAMM.
    Só aplica para contas de cartão: 50200, 50300, 50500.
    """
    # contas que usam dia de corte
    CONTAS_CARTAO = {"50200", "50300", "50500"}

    # se não for cartão → sempre retorna True (não exige dia de corte)
    if str(conta) not in CONTAS_CARTAO:
        return True

    try:
        conn = sql_conta.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1
            FROM cartoes_corte
            WHERE conta = %s AND anomes = %s
            LIMIT 1
        """, (conta, anomes))

        existe = cur.fetchone() is not None
        conn.close()
        return existe

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao verificar competência:\n{e}")
        return False

def tela_lancamentos():

    janela = tk.Toplevel()
    janela.title("Lançamentos Diários")
    janela.geometry("1400x950")
    janela.grab_set()

    ultimo_comprovante = {"nome": ""}

    # ===========================
    # CABEÇALHO
    # ===========================
    frame_top = tk.Frame(janela)
    frame_top.pack(fill="x", pady=10)

    tk.Label(frame_top, text="Roteiro").pack(side="left", padx=5)
    combo_roteiro = ttk.Combobox(frame_top, width=50)
    combo_roteiro.pack(side="left", padx=5)

    roteiros = sql_capa.listar()
    combo_roteiro["values"] = [f"{r[0]} - {r[2]}" for r in roteiros]

    tk.Label(frame_top, text="Competência (MMAAAA)").pack(side="left", padx=5)
    entry_comp = tk.Entry(frame_top, width=10)
    entry_comp.pack(side="left", padx=5)

    btn_carregar = tk.Button(frame_top, text="Carregar")
    btn_carregar.pack(side="left", padx=10)

    # ===========================
    # SALDO INICIAL
    # ===========================
    frame_saldo_inicial = tk.Frame(janela)
    frame_saldo_inicial.pack(fill="x", pady=10)

    tk.Label(frame_saldo_inicial, text="Saldo Inicial").pack(side="left", padx=10)
    entry_saldo_inicial = tk.Entry(frame_saldo_inicial, width=15)
    entry_saldo_inicial.pack(side="left")
    entry_saldo_inicial.insert(0, "0,00")

    # ===========================
    # VALIDAR COMPETÊNCIA
    # ===========================
    def validar_competencia(event):
        comp = entry_comp.get().strip()

        if len(comp) > 6:
            entry_comp.delete(6, tk.END)
            return

        if not comp.isdigit():
            entry_comp.delete(0, tk.END)
            return

        if len(comp) == 6:
            mes = int(comp[:2])
            ano = int(comp[2:])

            if mes < 1 or mes > 12:
                messagebox.showwarning("Competência inválida", "Mês deve estar entre 01 e 12.")
                entry_comp.delete(0, tk.END)
                return

            if ano < 2000 or ano > 2099:
                messagebox.showwarning("Competência inválida", "Ano deve estar entre 2000 e 2099.")
                entry_comp.delete(0, tk.END)
                return

            carregar()

    entry_comp.bind("<KeyRelease>", validar_competencia)

    # ===========================
    # SPREAD
    # ===========================
    frame_tree = tk.Frame(janela)
    frame_tree.pack(fill="both", expand=True, pady=10)

    colunas = (
        "DIA", "CONTA", "HISTORICO", "COMPLHISTORICO", "VALOR",
        "DATAREGISTRO", "COMPROVANTE", "COMPPATH", "DATAFULL"
    )

    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")

    tree.column("COMPPATH", width=0, stretch=False)
    tree.column("DATAFULL", width=0, stretch=False)

    tree.column("DIA", width=80)
    tree.column("CONTA", width=120)
    tree.column("HISTORICO", width=250)
    tree.column("COMPLHISTORICO", width=300)
    tree.column("VALOR", width=120, anchor="e")
    tree.column("DATAREGISTRO", width=150)
    tree.column("COMPROVANTE", width=200)

    for col in colunas[:-2]:
        tree.heading(col, text=col)

    tree.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)

    frame_tree.grid_rowconfigure(0, weight=1)
    frame_tree.grid_columnconfigure(0, weight=1)

    # ===========================
    # TOTAIS
    # ===========================
    frame_totais = tk.Frame(janela)
    frame_totais.pack(fill="x", pady=10)

    tk.Label(frame_totais, text="Total Crédito (C)").grid(row=0, column=0, padx=10)
    entry_total_c = tk.Entry(frame_totais, width=15, state="readonly")
    entry_total_c.grid(row=0, column=1)

    tk.Label(frame_totais, text="Total Débito (D)").grid(row=0, column=2, padx=10)
    entry_total_d = tk.Entry(frame_totais, width=15, state="readonly")
    entry_total_d.grid(row=0, column=3)

    tk.Label(frame_totais, text="Saldo Final").grid(row=0, column=4, padx=10)
    entry_saldo_final = tk.Entry(frame_totais, width=15, state="readonly")
    entry_saldo_final.grid(row=0, column=5)
    # ===========================
    # VERIFICAR COMPETÊNCIA AO ENTRAR NA TELA
    # ===========================
    def verificar_competencia_inicial():
        comp = entry_comp.get().strip()
        if len(comp) != 6:
            return

        mes = comp[:2]
        ano = comp[2:]
        anomes = ano + mes  # formato AAAAMM

        # conta do roteiro selecionado
        if not combo_roteiro.get():
            return

        rot = combo_roteiro.get().split(" - ")[0]
        conta_capa = sql_capa.buscar_conta(rot)

        if not verificar_competencia_cartao(conta_capa, anomes):
            messagebox.showwarning(
                "Competência não configurada",
                f"Não existe dia de corte cadastrado para a conta {conta_capa} no mês {anomes}.\n"
                f"Cadastre o dia de corte antes de lançar."
            )
            return

    # chama automaticamente ao abrir
    janela.after(300, verificar_competencia_inicial)

    # ===========================
    # FILTRO POR DATAREGISTRO
    # ===========================
    frame_filtro = tk.LabelFrame(janela, text="Filtro por Data de Registro")
    frame_filtro.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_filtro, text="Data Inicial (dd/mm/aaaa)").pack(side="left", padx=5)
    entry_data_ini = tk.Entry(frame_filtro, width=12)
    entry_data_ini.pack(side="left", padx=5)

    tk.Label(frame_filtro, text="Data Final (dd/mm/aaaa)").pack(side="left", padx=5)
    entry_data_fim = tk.Entry(frame_filtro, width=12)
    entry_data_fim.pack(side="left", padx=5)

    btn_filtrar = tk.Button(frame_filtro, text="Filtrar")
    btn_filtrar.pack(side="left", padx=10)

    def filtrar_por_data():
        data_ini = entry_data_ini.get().strip()
        data_fim = entry_data_fim.get().strip()

        try:
            dt_ini = datetime.strptime(data_ini, "%d/%m/%Y")
            dt_fim = datetime.strptime(data_fim, "%d/%m/%Y")
        except:
            messagebox.showwarning("Filtro", "Datas inválidas. Use dd/mm/aaaa.")
            return

        for item in tree.get_children():
            valores = tree.item(item, "values")
            datareg = valores[5]

            try:
                dt_reg = datetime.strptime(datareg, "%d/%m/%Y %H:%M")
            except:
                continue

            if dt_reg < dt_ini or dt_reg > dt_fim:
                tree.detach(item)
            else:
                tree.reattach(item, "", "end")

    btn_filtrar.config(command=filtrar_por_data)

    # ===========================
    # ORDENAR POR DATAREGISTRO
    # ===========================
    ordem_atual = {col: False for col in colunas}

    def ordenar_dataregistro():
        itens = [(tree.set(iid, "DATAREGISTRO"), iid) for iid in tree.get_children("")]

        def chave(x):
            try:
                return datetime.strptime(x[0], "%d/%m/%Y %H:%M")
            except:
                return datetime.min

        ordem_atual["DATAREGISTRO"] = not ordem_atual["DATAREGISTRO"]
        reverse = ordem_atual["DATAREGISTRO"]

        itens.sort(key=chave, reverse=reverse)

        for index, (_, iid) in enumerate(itens):
            tree.move(iid, "", index)

    tree.heading("DATAREGISTRO", text="DATAREGISTRO", command=ordenar_dataregistro)

    # ===========================
    # CÁLCULO DE SALDOS (POR COMPETÊNCIA)
    # ===========================
    def calcular_saldos():
        try:
            saldo_inicial = float(entry_saldo_inicial.get().replace(".", "").replace(",", "."))
        except:
            saldo_inicial = 0.0

        total_c = 0.0
        total_d = 0.0

        comp = entry_comp.get().strip()
        if len(comp) != 6 or not combo_roteiro.get():
            entry_total_c.config(state="normal")
            entry_total_d.config(state="normal")
            entry_saldo_final.config(state="normal")

            entry_total_c.delete(0, tk.END)
            entry_total_d.delete(0, tk.END)
            entry_saldo_final.delete(0, tk.END)

            entry_total_c.insert(0, "0,00")
            entry_total_d.insert(0, "0,00")
            entry_saldo_final.insert(0, f"{saldo_inicial:.2f}".replace(".", ","))

            entry_total_c.config(state="readonly")
            entry_total_d.config(state="readonly")
            entry_saldo_final.config(state="readonly")
            return

        mes = int(comp[:2])
        ano = int(comp[2:])
        rot = combo_roteiro.get().split(" - ")[0]

        try:
            existentes = sql_lanc.listar_por_roteiro_competencia(rot, mes, ano)
        except Exception:
            existentes = []

        for lan in existentes:
            try:
                valor = float(lan[4])
            except:
                continue

            natureza = lan[5] if len(lan) > 5 else "D"

            if natureza == "C":
                total_c += valor
            elif natureza == "D":
                total_d += valor

        saldo_final = saldo_inicial + total_c - total_d

        entry_total_c.config(state="normal")
        entry_total_d.config(state="normal")
        entry_saldo_final.config(state="normal")

        entry_total_c.delete(0, tk.END)
        entry_total_d.delete(0, tk.END)
        entry_saldo_final.delete(0, tk.END)

        entry_total_c.insert(0, f"{total_c:.2f}".replace(".", ","))
        entry_total_d.insert(0, f"{total_d:.2f}".replace(".", ","))
        entry_saldo_final.insert(0, f"{saldo_final:.2f}".replace(".", ","))

        entry_total_c.config(state="readonly")
        entry_total_d.config(state="readonly")
        entry_saldo_final.config(state="readonly")

    entry_saldo_inicial.bind("<KeyRelease>", lambda e: calcular_saldos())

    # ===========================
    # CAMPOS DE EDIÇÃO
    # ===========================
    frame_edit = tk.LabelFrame(janela, text="Edição do Lançamento")
    frame_edit.pack(fill="x", padx=10, pady=10)

    def campo(label):
        linha = tk.Frame(frame_edit)
        linha.pack(fill="x", pady=3)
        tk.Label(linha, text=label, width=20, anchor="w").pack(side="left")
        entry = tk.Entry(linha, width=60)
        entry.pack(side="left")
        return entry

    txt_dia = campo("Dia")
    txt_conta = campo("Conta (fixa)")
    txt_hist = campo("Histórico (fixo)")
    txt_compl = campo("Complemento Histórico")
    txt_valor = campo("Valor")
    txt_datareg = campo("Data Registro")
    txt_datareg.config(state="disabled")

    linha_comp = tk.Frame(frame_edit)
    linha_comp.pack(fill="x", pady=3)
    tk.Label(linha_comp, text="Comprovante", width=20, anchor="w").pack(side="left")
    combo_comp = ttk.Combobox(linha_comp, width=57)
    combo_comp.pack(side="left")

    txt_conta.config(state="disabled")
    txt_hist.config(state="disabled")

    linha_parc = tk.Frame(frame_edit)
    linha_parc.pack(fill="x", pady=3)
    tk.Label(linha_parc, text="Parcelas", width=20, anchor="w").pack(side="left")
    combo_parc = ttk.Combobox(linha_parc, width=10, values=[str(i) for i in range(1, 25)])
    combo_parc.current(0)
    combo_parc.pack(side="left")

    # ===========================
    # AUTOCOMPLETE
    # ===========================
    def autocomplete_compl(event):
        texto = txt_compl.get()
        if not texto:
            return

        possiveis = [s for s in AUTOCOMP if s.lower().startswith(texto.lower())]
        if possiveis:
            sugestao = possiveis[0]
            txt_compl.delete(0, tk.END)
            txt_compl.insert(0, sugestao)
            txt_compl.select_range(len(texto), len(sugestao))

    txt_compl.bind("<KeyRelease>", autocomplete_compl)

    # ===========================
    # LIMPAR CAMPOS
    # ===========================
    def limpar_campos():
        for campo in (txt_dia, txt_conta, txt_hist, txt_compl, txt_valor, txt_datareg):
            campo.config(state="normal")
            campo.delete(0, tk.END)
            campo.config(state="disabled")

        combo_comp.set("")
        combo_comp.config(state="disabled")

    limpar_campos()

    # ===========================
    # FORMATAR VALOR
    # ===========================
    def formatar_valor(event):
        valor = txt_valor.get().strip()
        if not valor:
            return

        valor = valor.replace(".", ",")
        if "," in valor:
            partes = valor.split(",")
            if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                centavos = partes[1].ljust(2, "0")[:2]
                txt_valor.delete(0, tk.END)
                txt_valor.insert(0, f"{partes[0]},{centavos}")
                return

        if valor.isdigit():
            if len(valor) == 1:
                txt_valor.delete(0, tk.END)
                txt_valor.insert(0, f"0,0{valor}")
            elif len(valor) == 2:
                txt_valor.delete(0, tk.END)
                txt_valor.insert(0, f"0,{valor}")
            else:
                txt_valor.delete(0, tk.END)
                txt_valor.insert(0, valor[:-2] + "," + valor[-2:])

    txt_valor.bind("<FocusOut>", formatar_valor)

    # ===========================
    # CARREGAR COMPROVANTES
    # ===========================
    def carregar_comprovantes():
        try:
            arquivos = os.listdir(PASTA_COMPROVANTES)
            arquivos = [
                arq for arq in arquivos
                if os.path.isfile(os.path.join(PASTA_COMPROVANTES, arq))
            ]
            arquivos.sort()
            combo_comp["values"] = arquivos
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar comprovantes:\n{e}")

    # ===========================
    # CARREGAR LANÇAMENTOS
    # ===========================
    def carregar():
    # verificar competência antes de carregar
        comp = entry_comp.get().strip()
        if len(comp) == 6:
            mes = comp[:2]
            ano = comp[2:]
            anomes = ano + mes

            rot = combo_roteiro.get().split(" - ")[0]
            conta_capa = sql_capa.buscar_conta(rot)

            if not verificar_competencia_cartao(conta_capa, anomes):
                messagebox.showwarning(
                    "Competência não configurada",
                    f"Não existe dia de corte cadastrado para a conta {conta_capa} no mês {anomes}."
                )
                return
    
        carregar_comprovantes()

        for item in tree.get_children():
            tree.delete(item)

        comp = entry_comp.get().strip()
        if len(comp) != 6:
            calcular_saldos()
            return

        mes = int(comp[:2])
        ano = int(comp[2:])
        rot = combo_roteiro.get().split(" - ")[0]

        conta_capa = sql_capa.buscar_conta(rot)

        linhas = sql_deta.listar()
        for r in linhas:
            if r[0] == rot:
                conta_spread = r[2] if r[1] == "D" else r[3]
                nome = next((c[1] for c in sql_conta.listar() if c[0] == conta_spread), "")
                tree.insert("", tk.END, values=("", conta_spread, nome, "", "", "", "", "", ""))

        existentes = sql_lanc.listar_por_roteiro_competencia(rot, mes, ano)

        for lan in existentes:
            dia = lan[0].strftime("%d")
            datafull = lan[0].strftime("%Y-%m-%d")
            conta = lan[1]
            hist = lan[2]
            compl = lan[3]
            valor = f"{lan[4]:.2f}".replace(".", ",")
            compweb = lan[7]
            datareg = lan[8].strftime("%d/%m/%Y %H:%M")
            nome_arquivo = os.path.basename(compweb) if compweb else ""

            if conta != conta_capa:
                tree.insert(
                    "",
                    tk.END,
                    values=(dia, conta, hist, compl, valor, datareg, nome_arquivo, compweb, datafull)
                )

        calcular_saldos()

    btn_carregar.config(command=carregar)

    # ===========================
    # HEADINGS COM ORDENAÇÃO
    # ===========================
    def treeview_sort_column(tv, col, reverse):
        dados = [(tv.set(k, col), k) for k in tv.get_children('')]

        try:
            dados.sort(key=lambda t: float(t[0].replace(",", ".")), reverse=reverse)
        except:
            dados.sort(reverse=reverse)

        for index, (val, k) in enumerate(dados):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

    tree.heading("DIA", text="DIA", command=lambda: treeview_sort_column(tree, "DIA", False))
    tree.heading("CONTA", text="CONTA", command=lambda: treeview_sort_column(tree, "CONTA", False))
    tree.heading("HISTORICO", text="HISTORICO", command=lambda: treeview_sort_column(tree, "HISTORICO", False))
    tree.heading("COMPLHISTORICO", text="COMPLHISTORICO", command=lambda: treeview_sort_column(tree, "COMPLHISTORICO", False))
    tree.heading("VALOR", text="VALOR", command=lambda: treeview_sort_column(tree, "VALOR", False))
    tree.heading("DATAREGISTRO", text="DATAREGISTRO", command=ordenar_dataregistro)
    tree.heading("COMPROVANTE", text="COMPROVANTE", command=lambda: treeview_sort_column(tree, "COMPROVANTE", False))
 


    # ===========================
    # SELECIONAR LINHA
    # ===========================
    def selecionar(event):
        item = tree.selection()
        if not item:
            return

        valores = tree.item(item[0], "values")

        dia, conta, hist, compl, valor, datareg, nome_comp, compweb, datafull = valores

        for campo in (txt_dia, txt_compl, txt_valor, txt_datareg):
            campo.config(state="normal")

        combo_comp.config(state="normal")

        txt_conta.config(state="normal")
        txt_hist.config(state="normal")

        txt_dia.delete(0, tk.END)
        txt_conta.delete(0, tk.END)
        txt_hist.delete(0, tk.END)
        txt_compl.delete(0, tk.END)
        txt_valor.delete(0, tk.END)
        txt_datareg.delete(0, tk.END)

        txt_dia.insert(0, dia)
        txt_conta.insert(0, conta)
        txt_hist.insert(0, hist)
        txt_compl.insert(0, compl)
        txt_valor.insert(0, valor)
        txt_datareg.insert(0, datareg)

        if ultimo_comprovante["nome"]:
            combo_comp.set(ultimo_comprovante["nome"])
        else:
            combo_comp.set(nome_comp)

        txt_conta.config(state="disabled")
        txt_hist.config(state="disabled")
        txt_datareg.config(state="disabled")

        txt_dia.focus_set()

    tree.bind("<<TreeviewSelect>>", selecionar)

    # ===========================
    # ABRIR COMPROVANTE + MIGRAÇÃO AUTOMÁTICA
    # ===========================
    def abrir_comprovante(event):
        # identificar linha e coluna clicada
        item = tree.identify_row(event.y)
        coluna = tree.identify_column(event.x)

        # coluna "#7" = COMPROVANTE
        if coluna != "#7":
            return

        if not item:
            messagebox.showwarning("Comprovante", "Nenhum comprovante associado.")
            return

        valores = tree.item(item, "values")
        caminho = valores[7]

        if not caminho:
            messagebox.showwarning("Comprovante", "Nenhum comprovante associado.")
            return

        caminho = caminho.strip()
        print("Caminho recebido:", caminho)

        # GOOGLE DRIVE (formato antigo)
        if caminho.startswith("open?id="):
            drive_id = caminho.replace("open?id=", "")
            url = f"https://drive.google.com/uc?id={drive_id}"
            print("Abrindo Drive:", url)
            webbrowser.open(url)
            return

        # GOOGLE DRIVE (completo)
        if "drive.google.com" in caminho:
            print("Abrindo Drive completo:", caminho)
            webbrowser.open(caminho)
            return

        # ONEDRIVE
        if "onedrive.live.com" in caminho or "1drv.ms" in caminho:
            print("Abrindo OneDrive:", caminho)
            webbrowser.open(caminho)
            return

        # HTTP/HTTPS genérico
        if caminho.startswith("http://") or caminho.startswith("https://"):
            print("Abrindo link HTTP:", caminho)
            webbrowser.open(caminho)
            return

        # ARQUIVO LOCAL
        if os.path.exists(caminho):
            print("Abrindo arquivo local:", caminho)
            os.startfile(caminho)
            return

        messagebox.showerror("Erro", f"O caminho informado não existe:\n{caminho}")
    # ===========================
    # AGORA SIM — bind fora da função
    # ===========================
    tree.bind("<Double-1>", abrir_comprovante)   

    # ===========================
    # EXCLUIR LANÇAMENTO
    # ===========================
    def excluir_linha():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Excluir", "Selecione uma linha.")
            return

        dia, conta, hist, compl, valor, datareg, nome_comp, compweb, datafull = tree.item(item[0], "values")

        if not dia or not valor:
            messagebox.showwarning("Excluir", "Linha vazia não pode ser excluída.")
            return

        sql_lanc.excluir_lancamento_duplo(
            datafull, conta, hist, compl, valor.replace(",", "."), compweb
        )
        tree.delete(item[0])

        limpar_campos()
        calcular_saldos()

    # ===========================
    # GRAVAR LINHA (D/C COM PARCELAMENTO)
    # ===========================
    def gravar_linha():
        try:
            # ===========================
            # CAMPOS BÁSICOS
            # ===========================
            dia = txt_dia.get().strip()
            conta_spread = txt_conta.get().strip()
            hist = txt_hist.get().strip()
            compl = txt_compl.get().strip()
            valor = txt_valor.get().strip()
            arquivo = combo_comp.get().strip()

            if not dia or not valor or not conta_spread:
                messagebox.showwarning("Erro", "Preencha todos os campos obrigatórios.")
                return

            # ===========================
            # RECUPERAR COMPROVANTE ORIGINAL (SE EXISTIR)
            # ===========================
            item = tree.selection()
            compweb_old = ""
            nome_old = ""

            if item:
                valores_old = tree.item(item[0], "values")
                # (dia, conta, hist, compl, valor, datareg, nome_comp, compweb, datafull)
                nome_old = valores_old[6]
                compweb_old = valores_old[7]

            # ===========================
            # DEFINIR COMPROVANTE (NOVO OU ANTIGO)
            # ===========================
            if arquivo:
                # se o que veio do combo já é link (Google Drive), não montar caminho local
                if arquivo.startswith("http://") or arquivo.startswith("https://") or arquivo.startswith("open?id="):
                    comprovante = arquivo
                else:
                    comprovante = os.path.join(PASTA_COMPROVANTES, arquivo)
            else:
                # não escolheu novo → mantém o que já estava no registro
                comprovante = compweb_old

            # se não houver nem antigo nem novo, avisa
            if not comprovante:
                messagebox.showwarning(
                    "Comprovante",
                    "Nenhum comprovante associado. Selecione um arquivo ou mantenha o link existente."
                )
                return

            # ===========================
            # FORMATAR VALOR
            # ===========================
            valor = valor.replace(" ", "").replace(".", ",")
            if "," in valor:
                partes = valor.split(",")
                if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit():
                    messagebox.showwarning("Valor inválido", "Digite um valor válido, ex: 345,88")
                    return
                centavos = partes[1].ljust(2, "0")[:2]
                valor_decimal = f"{partes[0]},{centavos}"
            else:
                if not valor.isdigit():
                    messagebox.showwarning("Valor inválido", "Digite apenas números ou números com vírgula.")
                    return
                if len(valor) == 1:
                    valor_decimal = f"0,0{valor}"
                elif len(valor) == 2:
                    valor_decimal = f"0,{valor}"
                else:
                    valor_decimal = valor[:-2] + "," + valor[-2:]

            valor_sql = valor_decimal.replace(",", ".")

            # ===========================
            # COMPETÊNCIA
            # ===========================
            comp = entry_comp.get().strip()
            mes = int(comp[:2])
            ano = int(comp[2:])
            dia_int = int(dia)
            anomes = f"{ano}{str(mes).zfill(2)}"

            # ===========================
            # ROTEIRO E CONTA CAPA
            # ===========================
            rot = combo_roteiro.get().strip()
            if not rot:
                messagebox.showerror("Erro", "Selecione um roteiro antes de gravar o lançamento.")
                return

            try:
                rot_codigo = rot.split(" - ")[0]
                conta_capa = sql_capa.buscar_conta(rot_codigo)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar conta do roteiro:\n{e}")
                return

            if not conta_capa:
                messagebox.showerror(
                    "Erro",
                    f"O roteiro {rot_codigo} não possui conta associada.\n"
                    f"Cadastre a conta na capa do roteiro."
                )
                return

            # ===========================
            # DIA DE CORTE (somente cartões)
            # ===========================
            CONTAS_CARTAO = {"50200", "50300", "50500"}

            if str(conta_capa) in CONTAS_CARTAO:
                dia_corte = sql_conta.buscar_dia_corte(conta_capa, anomes)

                if dia_corte is None:
                    messagebox.showerror(
                        "Competência inválida",
                        f"Não existe dia de corte cadastrado para a conta {conta_capa} no mês {anomes}."
                    )
                    return

                # ajustar data
                data_digitada = datetime(ano, mes, dia_int)
                data_base = ajustar_data_lancamento(data_digitada, dia_corte)

                if data_base != data_digitada:
                    messagebox.showinfo(
                        "Competência Ajustada",
                        f"Lançamento pós-corte.\n"
                        f"Data ajustada automaticamente para {data_base.strftime('%d/%m/%Y')}."
                    )
            else:
                # contas normais → não ajusta competência
                data_base = datetime(ano, mes, dia_int)


            dataregistro = datetime.now().strftime("%d/%m/%Y %H:%M")

            # ===========================
            # LOTE E SEQUENCIAL
            # ===========================
            titulolote = sql_capa.buscar_titulolote(rot_codigo)
            lote = f"{titulolote}{comp}"
            seq = sql_lanc.proximo_sequencial_lote(lote)
            quemweb = "Geraldo"

            # ===========================
            # AUTOCOMPLETE
            # ===========================
            if compl:
                AUTOCOMP.add(compl)
                config.add_complemento(compl)

            ultimo_comprovante["nome"] = arquivo

            # ===========================
            # EXCLUIR LINHA ANTERIOR (EDIÇÃO)
            # ===========================
            if item:
                dia_old, conta_old, hist_old, compl_old, valor_old, datareg_old, nome_old, comp_old, data_old = valores_old
                if valor_old.strip() != "":
                    sql_lanc.excluir_lancamento_duplo(
                        data_old, conta_old, hist_old, compl_old,
                        valor_old.replace(",", "."), comp_old
                    )

            # ===========================
            # GRAVAR PARCELAS
            # ===========================
            parcelas = int(combo_parc.get())
            valor_total = float(valor_sql)
            valor_parcela = round(valor_total / parcelas, 2)

            for i in range(parcelas):
                data_parcela = data_base + relativedelta(months=i)
                datalancto_parcela = data_parcela.strftime("%Y-%m-%d")
                compl_parcela = f"{compl} - {i+1}/{parcelas}"

                # débito
                sql_lanc.inserir(
                    datalancto_parcela, rot_codigo, conta_capa, valor_parcela, "D",
                    hist, compl_parcela, conta_spread, dataregistro,
                    lote, seq, quemweb, comprovante
                )

                # crédito
                sql_lanc.inserir(
                    datalancto_parcela, rot_codigo, conta_spread, valor_parcela, "C",
                    hist, compl_parcela, conta_capa, dataregistro,
                    lote, seq, quemweb, comprovante
                )

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        str(data_parcela.day).zfill(2),
                        conta_spread,
                        hist,
                        compl_parcela,
                        f"{valor_parcela:.2f}".replace(".", ","),
                        dataregistro,
                        arquivo if arquivo else nome_old,
                        comprovante,
                        datalancto_parcela
                    )
                )

                seq += 1

            tree.insert("", tk.END, values=("", conta_spread, hist, "", "", "", "", "", ""))

            limpar_campos()
            messagebox.showinfo("OK", "Lançamento gravado.")
            calcular_saldos()
            carregar()

        except Exception as e:
            messagebox.showerror("Erro ao gravar", str(e))


    def ajustar_data_lancamento(data_real, dia_corte):
        """
        Se o lançamento ocorrer no dia do corte ou depois,
        grava como dia 28 do mês seguinte.
        """
        if data_real.day >= dia_corte:
            # mês seguinte
            data_comp = data_real + relativedelta(months=1)
            return data_comp.replace(day=28)
        else:
            # mês atual
            return data_real

    # ===========================
    # BOTÕES
    # ===========================
    frame_buttons = tk.Frame(janela)
    frame_buttons.pack(fill="x", pady=10)

    tk.Button(frame_buttons, text="Excluir Linha", command=excluir_linha).pack(side="left", padx=10)
    tk.Button(frame_buttons, text="Gravar Linha", command=gravar_linha).pack(side="left", padx=10)
    tk.Button(frame_buttons, text="Finalizar", command=janela.destroy).pack(side="left", padx=10)
