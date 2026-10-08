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
    CONTAS_CARTAO = {"50200", "50300", "50500"}

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
    lista_comprovantes = None


    conta_capa = None
    janela.selected_original = None  # para edição/exclusão
    ultima_ordem = {"coluna": None, "reverse": False}

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
    # INFORMAÇÃO DA CONTA DO ROTEIRO
    # ===========================
    label_conta_info = tk.Label(
        frame_top,
        text="Conta do Roteiro: ---",
        font=("Arial", 10, "bold"),
        fg="blue"
    )
    label_conta_info.pack(side="left", padx=20)

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
    # SPREAD
    # ===========================
    frame_tree = tk.Frame(janela)
    frame_tree.pack(fill="both", expand=True, pady=10)

    colunas = (
        "DIA", "CONTA", "HISTORICO", "COMPLHISTORICO", "VALOR",
        "NATUREZA", "DATAREGISTRO", "COMPROVANTE", "COMPPATH", "DATAFULL"
    )

    tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")

    tree.column("COMPPATH", width=0, stretch=False)
    tree.column("DATAFULL", width=0, stretch=False)

    tree.column("DIA", width=80)
    tree.column("CONTA", width=120)
    tree.column("HISTORICO", width=250)
    tree.column("COMPLHISTORICO", width=300)
    tree.column("VALOR", width=120, anchor="e")

    tree.column("NATUREZA", width=80, anchor="center")
    tree.heading("NATUREZA", text="NAT")

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
    # VERIFICAR COMPETÊNCIA AO ENTRAR
    # ===========================
    def verificar_competencia_inicial():
        comp = entry_comp.get().strip()
        if len(comp) != 6:
            return

        mes = comp[:2]
        ano = comp[2:]
        anomes = ano + mes

        if not combo_roteiro.get():
            return

        rot = combo_roteiro.get().split(" - ")[0]
        conta_local = sql_capa.buscar_conta(rot)

        if not verificar_competencia_cartao(conta_local, anomes):
            messagebox.showwarning(
                "Competência não configurada",
                f"Não existe dia de corte cadastrado para a conta {conta_local} no mês {anomes}.\n"
                f"Cadastre o dia de corte antes de lançar."
            )

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
            datareg = valores[6]

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
# CÁLCULO DE SALDOS
# ===========================
    def calcular_saldos():
        try:
            saldo_inicial = float(entry_saldo_inicial.get().replace(".", "").replace(",", "."))
        except:
            saldo_inicial = 0.0

        saldo_final = saldo_inicial

        # natureza da conta capa (vem do cadastro)
        rot = combo_roteiro.get().split(" - ")[0]
        conta_capa_local = sql_capa.buscar_conta(rot)
        natureza_capa = sql_conta.buscar_natureza(conta_capa_local)  # "D" ou "C"

        for item in tree.get_children():
            valores = tree.item(item, "values")

            valor_str = valores[4]
            sinal_spread = valores[5]  # "D" ou "C"

            if not valor_str:
                continue

            try:
                valor_float = float(valor_str.replace(".", "").replace(",", "."))
            except:
                continue

            # regra contábil final
            if natureza_capa == "D":
                if sinal_spread == "C":
                    saldo_final -= valor_float
                else:
                    saldo_final += valor_float
            else:  # natureza capa = C
                if sinal_spread == "D":
                    saldo_final -= valor_float
                else:
                    saldo_final += valor_float

        # totais
        total_c = sum(
            float(tree.item(i, "values")[4].replace(".", "").replace(",", "."))
            for i in tree.get_children()
            if tree.item(i, "values")[5] == "C" and tree.item(i, "values")[4]
        )

        total_d = sum(
            float(tree.item(i, "values")[4].replace(".", "").replace(",", "."))
            for i in tree.get_children()
            if tree.item(i, "values")[5] == "D" and tree.item(i, "values")[4]
        )

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
        combo_parc.set("1")
       # combo_parc.config(state="disabled")
 
        janela.selected_original = None

    limpar_campos()

    # ===========================
    # FORMATAR VALOR
    # ===========================
    def formatar_valor(event):
        valor = txt_valor.get().strip()
        if not valor:
            return

        # detectar sinal digitado
        tem_sinal_negativo = valor.startswith("-")

        # remover sinal para formatar
        valor_sem_sinal = valor.replace("-", "").replace(".", "").replace(",", "")

        if not valor_sem_sinal.isdigit():
            return

        # aplicar formatação: duas casas decimais
        if len(valor_sem_sinal) == 1:
            valor_formatado = f"0,0{valor_sem_sinal}"
        elif len(valor_sem_sinal) == 2:
            valor_formatado = f"0,{valor_sem_sinal}"
        else:
            valor_formatado = valor_sem_sinal[:-2] + "," + valor_sem_sinal[-2:]

        # recolocar sinal se necessário
        if tem_sinal_negativo:
            valor_formatado = "-" + valor_formatado

        txt_valor.delete(0, tk.END)
        txt_valor.insert(0, valor_formatado)

        # ===========================
        # ALERTA DE CONSISTÊNCIA
        # ===========================

        conta_spread = txt_conta.get().strip()
        if not conta_spread:
            return

        natureza_spread = sql_conta.buscar_natureza(conta_spread)  # "D" ou "C"

        if natureza_spread == "D" and tem_sinal_negativo:
            messagebox.showwarning(
                "Atenção",
                "A conta é de natureza DEVEDORA (D), mas o valor digitado está NEGATIVO.\n"
                "Verifique se o sinal está correto."
            )

        if natureza_spread == "C" and not tem_sinal_negativo:
            messagebox.showwarning(
                "Atenção",
                "A conta é de natureza CREDORA (C), mas o valor digitado está POSITIVO.\n"
                "Verifique se o sinal está correto."
            )


    # ===========================
    #Adicionar linhas no spread
    # ===========================
    def adicionar_linha_spread(dia, conta, hist, compl, valor, natureza, datareg, nome_comp, compweb, datafull):
        tree.insert(
            "",
            tk.END,
            values=(dia, conta, hist, compl, valor, natureza, datareg, nome_comp, compweb, datafull)
        )

    # ===========================
    # CARREGAR COMPROVANTES
    # ===========================
    def carregar_comprovantes():
        nonlocal lista_comprovantes

        arquivos = os.listdir(PASTA_COMPROVANTES)
        arquivos = [
            arq for arq in arquivos
            if os.path.isfile(os.path.join(PASTA_COMPROVANTES, arq))
        ]

        lista = []
        for nome in arquivos:
            caminho = os.path.join(PASTA_COMPROVANTES, nome)
            try:
                data_mod = os.path.getmtime(caminho)  # timestamp da data/hora do arquivo
            except:
                data_mod = 0  # fallback seguro
            lista.append((data_mod, nome))

        # ordenar do mais novo para o mais antigo
        lista.sort(reverse=True)

        # extrair só os nomes para o combobox
        lista_comprovantes = [nome for (_, nome) in lista]
        combo_comp["values"] = lista_comprovantes


    # ===========================
    # CARREGAR LANÇAMENTOS
    # ===========================
    def carregar():
        nonlocal conta_capa

        comp = entry_comp.get().strip()
        if len(comp) == 6:
            mes = comp[:2]
            ano = comp[2:]
            anomes = ano + mes

            rot = combo_roteiro.get().split(" - ")[0]
            conta_capa = sql_capa.buscar_conta(rot)

            dados_conta = next((c for c in sql_conta.listar() if c[0] == conta_capa), None)

            if dados_conta:
                nome_conta = dados_conta[1]
                natureza_conta = dados_conta[5]
                label_conta_info.config(
                    text=f"Conta do Roteiro: {conta_capa} – {nome_conta} – Natureza: {natureza_conta}"
                )
            else:
                label_conta_info.config(text=f"Conta do Roteiro: {conta_capa} – (não encontrada)")

        carregar_comprovantes()

        for item in tree.get_children():
            tree.delete(item)

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
                natureza_spread = sql_conta.buscar_natureza(conta_spread)

                tree.insert(
                    "",
                    tk.END,
                    values=("", conta_spread, nome, "", "", natureza_spread, "", "", "", "")
                )

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

            natureza = sql_conta.buscar_natureza(conta)

            natureza = lan[5]  # usa o sinal do lançamento, não da conta

            if conta != conta_capa:
                tree.insert(
                    "",
                    tk.END,
                    values=(dia, conta, hist, compl, valor, natureza, datareg, nome_arquivo, compweb, datafull)
                )
        calcular_saldos()
        limpar_campos()
        if ultima_ordem["coluna"]:
            treeview_sort_column(tree, ultima_ordem["coluna"], ultima_ordem["reverse"])


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
    # SALVAR A ÚLTIMA ORDENAÇÃO
        ultima_ordem["coluna"] = col
        ultima_ordem["reverse"] = reverse
        
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

        # linhas do spread têm 10 colunas, mas datafull é vazio
        dia        = valores[0]
        conta      = valores[1]
        hist       = valores[2]
        compl      = valores[3]
        valor      = valores[4]
        natureza   = valores[5]
        datareg    = valores[6]
        nome_comp  = valores[7]
        compweb    = valores[8]
        datafull   = valores[9] if len(valores) == 10 else ""

        # só guarda original se for lançamento gravado
        if datafull and compweb and dia:
            janela.selected_original = {
                "datafull": datafull,
                "conta_spread": conta,
                "hist": hist,
                "compl": compl,
                "valor": valor.replace(",", "."),
                "compweb": compweb
            }
        else:
            janela.selected_original = None


        # habilitar campos
        for campo in (txt_dia, txt_compl, txt_valor, txt_datareg):
            campo.config(state="normal")

        combo_comp.config(state="normal")
        txt_conta.config(state="normal")
        txt_hist.config(state="normal")

        # preencher campos
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

        combo_comp.set(nome_comp)

        txt_conta.config(state="disabled")
        txt_hist.config(state="disabled")
        txt_datareg.config(state="disabled")

        txt_dia.focus_set()


    tree.bind("<<TreeviewSelect>>", selecionar)

    # ===========================
    # ABRIR COMPROVANTE
    # ===========================
    def abrir_comprovante(event):
        item = tree.identify_row(event.y)
        coluna = tree.identify_column(event.x)

        if coluna != "#8":
            return

        if not item:
            messagebox.showwarning("Comprovante", "Nenhum comprovante associado.")
            return

        valores = tree.item(item, "values")
        caminho = valores[8]

        if not caminho:
            messagebox.showwarning("Comprovante", "Nenhum comprovante associado.")
            return

        caminho = caminho.strip()

        if caminho.startswith("open?id="):
            drive_id = caminho.replace("open?id=", "")
            url = f"https://drive.google.com/uc?id={drive_id}"
            webbrowser.open(url)
            return

        if "drive.google.com" in caminho:
            webbrowser.open(caminho)
            return

        if "onedrive.live.com" in caminho or "1drv.ms" in caminho:
            webbrowser.open(caminho)
            return

        if caminho.startswith("http://") or caminho.startswith("https://"):
            webbrowser.open(caminho)
            return

        if os.path.exists(caminho):
            os.startfile(caminho)
            return

        messagebox.showerror("Erro", f"O caminho informado não existe:\n{caminho}")

    tree.bind("<Double-1>", abrir_comprovante)

    # ===========================
    # EXCLUIR LANÇAMENTO
    # ===========================
    def excluir_linha():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Excluir", "Selecione uma linha.")
            return

        if not janela.selected_original:
            messagebox.showwarning("Excluir", "Nenhum lançamento gravado selecionado.")
            return

        orig = janela.selected_original

        try:
            sql_lanc.excluir_lancamento_duplo(
                orig["datafull"],
                orig["conta_spread"],
                orig["hist"],
                orig["compl"],
                float(orig["valor"]),
                orig["compweb"]
            )

            tree.delete(item[0])
            limpar_campos()
            calcular_saldos()

            messagebox.showinfo("OK", "Lançamento excluído.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir:\n{e}")
    def ajustar_data_lancamento(data_real, dia_corte):
        """
        Ajusta a competência do lançamento conforme o dia de corte.
        Regra:
        - Se o dia do lançamento > dia_corte -> competência vai para mês seguinte.
        - Caso contrário -> permanece no mesmo mês.
        """
        dia = data_real.day
        mes = data_real.month
        ano = data_real.year

        if dia > dia_corte:
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1

        # aqui mantenho o mesmo dia; se quiser, pode ajustar para último dia do mês
        return datetime(ano, mes, dia)

    # ===========================
    # GRAVAR LINHA (D/C COM PARCELAMENTO)
    # ===========================
     # ===========================
    # GRAVAR LINHA (D/C COM PARCELAMENTO)
    # ===========================
    def gravar_linha():
        try:
            dia = txt_dia.get().strip()
            conta_spread = txt_conta.get().strip()
            hist = txt_hist.get().strip()
            compl = txt_compl.get().strip()
            valor_digitado = txt_valor.get().strip()
            arquivo = combo_comp.get().strip()

            if not dia or not valor_digitado or not conta_spread:
                messagebox.showwarning("Erro", "Preencha todos os campos obrigatórios.")
                return

            # detectar sinal digitado pelo usuário
            tem_sinal_negativo = valor_digitado.startswith("-")

            # valor sem sinal para gravar no banco
            valor_sql = valor_digitado.replace(".", "").replace(",", ".")
            valor_float_abs = abs(float(valor_sql))

            # comprovante
            item = tree.selection()
            compweb_old = ""
            if item:
                valores_old = tree.item(item[0], "values")
                if len(valores_old) >= 9:
                    compweb_old = valores_old[8]

            comprovante = os.path.join(PASTA_COMPROVANTES, arquivo) if arquivo else compweb_old

            if not comprovante:
                messagebox.showwarning("Comprovante", "Nenhum comprovante associado.")
                return

            # competência digitada (MMAAAA)
            comp = entry_comp.get().strip()
            mes = int(comp[:2])
            ano = int(comp[2:])
            dia_int = int(dia)

            data_real = datetime(ano, mes, dia_int)

            # montar AAAAMM para buscar na tabela cartoes_corte
            anomes = f"{ano}{str(mes).zfill(2)}"

            # buscar conta da capa (é ela que tem dia de corte)
            rot = combo_roteiro.get().split(" - ")[0]
            conta_capa_local = sql_capa.buscar_conta(rot)

            # buscar dia de corte da conta da capa
            dia_corte = sql_conta.buscar_dia_corte(str(conta_capa_local).strip(), str(anomes).strip())

            print("DEBUG -> conta_capa_local:", conta_capa_local)
            print("DEBUG -> dia_corte:", dia_corte)
            print("DEBUG gravar_linha -> conta_spread:", conta_spread, "anomes:", anomes, "dia_corte:", dia_corte)
            print("DEBUG gravar_linha -> data_real:", data_real)

            # determinar mês original da competência digitada
            mes_original = mes
            ano_original = ano

            # determinar mês atual do lançamento (data_real)
            mes_lanc = data_real.month
            ano_lanc = data_real.year

            # determinar mês ajustado (mês seguinte)
            mes_ajustado = mes_original + 1
            ano_ajustado = ano_original
            if mes_ajustado > 12:
                mes_ajustado = 1
                ano_ajustado += 1

            # CASO 1: lançamento está no mês original → aplicar regra normal com pergunta
            if mes_lanc == mes_original and ano_lanc == ano_original:
                if dia_corte and data_real.day > dia_corte:
                    resposta = messagebox.askyesno(
                        "Ajustar competência",
                        f"O dia {data_real.day} está acima do dia de corte ({dia_corte}).\n"
                        f"Deseja mover este lançamento para {mes_ajustado:02d}/{ano_ajustado}?"
                    )
                    if resposta:
                        data_base = ajustar_data_lancamento(data_real, dia_corte)
                    else:
                        data_base = data_real
                else:
                    data_base = data_real

            # CASO 2: lançamento já está no mês ajustado → NÃO ajustar automaticamente
            elif mes_lanc == mes_ajustado and ano_lanc == ano_ajustado:
                data_base = data_real

            # CASO 3: qualquer outro mês → NÃO ajustar automaticamente
            else:
                data_base = data_real

            print("DEBUG gravar_linha -> data_base (ajustada):", data_base)

            # ============================================================
            # 🔥 EXCLUIR LANÇAMENTO ORIGINAL (SE ESTIVER EDITANDO)
            # ============================================================
            if janela.selected_original:
                orig = janela.selected_original
                sql_lanc.excluir_lancamento_duplo(
                    orig["datafull"],
                    orig["conta_spread"],
                    orig["hist"],
                    orig["compl"],
                    float(orig["valor"]),
                    orig["compweb"]
                )
                print("DEBUG -> original excluído:", orig)
            # remover linha antiga da tela
            if item and janela.selected_original:
                tree.delete(item[0])

            # ===========================
            # DEFINIÇÃO DO SINAL FINAL
            # ===========================
            natureza_capa = sql_conta.buscar_natureza(conta_capa_local)

            if not tem_sinal_negativo:
                if natureza_capa == "D":
                    sinal_spread = "C"
                    sinal_capa = "D"
                else:
                    sinal_spread = "D"
                    sinal_capa = "C"
            else:
                if natureza_capa == "D":
                    sinal_spread = "D"
                    sinal_capa = "C"
                else:
                    sinal_spread = "C"
                    sinal_capa = "D"

            # ===========================
            # PARCELAMENTO
            # ===========================
            parcelas = int(combo_parc.get())

            if parcelas > 1:
                valor_parcela = round(valor_float_abs / parcelas, 2)

                mes_parc = data_base.month
                ano_parc = data_base.year

                for i in range(parcelas):

                    # cada parcela usa a data_base como referência
                    data_parcela = datetime(ano_parc, mes_parc, data_base.day)

                    lote_parc = f"{rot}-{data_parcela.year}{str(data_parcela.month).zfill(2)}"
                    seq_parc = sql_lanc.proximo_sequencial_lote(lote_parc)
                    dataregistro = datetime.now().strftime("%d/%m/%Y %H:%M")

                    # grava spread
                    sql_lanc.inserir(
                        data_parcela, rot, conta_spread, valor_parcela, sinal_spread,
                        hist, f"{compl} PARC {i+1}/{parcelas}", conta_capa_local, dataregistro,
                        lote_parc, seq_parc, "WEB", comprovante
                    )

                    # grava capa
                    sql_lanc.inserir(
                        data_parcela, rot, conta_capa_local, valor_parcela, sinal_capa,
                        hist, f"{compl} PARC {i+1}/{parcelas}", conta_spread, dataregistro,
                        lote_parc, seq_parc + 1, "WEB", comprovante
                    )

                    adicionar_linha_spread(
                        data_parcela.day,
                        conta_spread,
                        hist,
                        f"{compl} PARC {i+1}/{parcelas}",
                        f"{valor_parcela:.2f}".replace(".", ","),
                        sinal_spread,
                        dataregistro,
                        os.path.basename(comprovante),
                        comprovante,
                        data_parcela.strftime("%Y-%m-%d")
                    )

                    mes_parc += 1
                    if mes_parc > 12:
                        mes_parc = 1
                        ano_parc += 1

                calcular_saldos()
                limpar_campos()
                carregar_comprovantes()
                messagebox.showinfo("OK", "Parcelamento gravado.")
                return

            # ===========================
            # GRAVAÇÃO NORMAL (SEM PARCELAS)
            # ===========================
            lote = f"{rot}-{data_base.year}{str(data_base.month).zfill(2)}"
            sequencialote = sql_lanc.proximo_sequencial_lote(lote)
            dataregistro = datetime.now().strftime("%d/%m/%Y %H:%M")

            sql_lanc.inserir(
                data_base, rot, conta_spread, valor_float_abs, sinal_spread,
                hist, compl, conta_capa_local, dataregistro,
                lote, sequencialote, "WEB", comprovante
            )

            sql_lanc.inserir(
                data_base, rot, conta_capa_local, valor_float_abs, sinal_capa,
                hist, compl, conta_spread, dataregistro,
                lote, sequencialote + 1, "WEB", comprovante
            )

            adicionar_linha_spread(
                dia,
                conta_spread,
                hist,
                compl,
                valor_digitado,
                sinal_spread,
                dataregistro,
                os.path.basename(comprovante),
                comprovante,
                data_base.strftime("%Y-%m-%d")
            )

            calcular_saldos()
            limpar_campos()
            carregar_comprovantes()
            messagebox.showinfo("OK", "Lançamento gravado.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gravar:\n{e}")



    def ajustar_data_lancamento(data_real, dia_corte):
        """
        Ajusta a competência para o mês seguinte quando a data da compra
        é igual ou superior ao dia de corte do cartão.
        """
        if data_real.day >= dia_corte:
            data_comp = data_real + relativedelta(months=1)
            return data_comp.replace(day=28)
        else:
            return data_real
        
    def mover_lancamento():
        if not janela.selected_original:
            messagebox.showwarning("Mover", "Selecione um lançamento gravado.")
            return

        orig = janela.selected_original

        # descobrir conta origem e conta despesa
        conta_origem = orig["conta_spread"]
        conta_despesa = None

        # buscar a outra linha do par
        linhas = sql_lanc.buscar_par(orig["datafull"], orig["compweb"], orig["valor"])
        for l in linhas:
            if l[1] != conta_origem:
                conta_despesa = l[1]

        if not conta_despesa:
            messagebox.showerror("Erro", "Não foi possível identificar a conta de despesa.")
            return

        # janela para escolher novo roteiro e conta origem
        win = tk.Toplevel(janela)
        win.title("Mover Lançamento")
        win.geometry("400x200")
        win.grab_set()

        tk.Label(win, text="Novo Roteiro").pack(pady=5)
        combo_novo_rot = ttk.Combobox(win, values=[f"{r[0]} - {r[2]}" for r in sql_capa.listar()], width=40)
        combo_novo_rot.pack()

        tk.Label(win, text="Nova Conta de Origem").pack(pady=5)
        combo_nova_conta = ttk.Combobox(win, values=[c[0] for c in sql_conta.listar()], width=40)
        combo_nova_conta.pack()

        def confirmar():
            novo_rot = combo_novo_rot.get().split(" - ")[0]
            nova_conta_origem = combo_nova_conta.get().strip()

            if not novo_rot or not nova_conta_origem:
                messagebox.showwarning("Mover", "Escolha roteiro e conta.")
                return

            try:
                # excluir par antigo
                sql_lanc.excluir_lancamento_duplo(
                    orig["datafull"],
                    conta_origem,
                    orig["hist"],
                    orig["compl"],
                    float(orig["valor"]),
                    orig["compweb"]
                )

                # recriar par novo
                sql_lanc.inserir_lancamento_duplo(
                    data=orig["datafull"],
                    conta_origem=nova_conta_origem,
                    conta_despesa=conta_despesa,
                    historico=orig["hist"],
                    compl=orig["compl"],
                    valor=float(orig["valor"]),
                    compweb=orig["compweb"],
                    roteiro=novo_rot
                )

                messagebox.showinfo("OK", "Lançamento movido com sucesso.")
                win.destroy()
                carregar()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao mover:\n{e}")

        tk.Button(win, text="Confirmar", command=confirmar).pack(pady=20)


    # ===========================
    # BOTÕES
    # ===========================
    frame_buttons = tk.Frame(janela)
    frame_buttons.pack(fill="x", pady=10)

    tk.Button(frame_buttons, text="Excluir Linha", command=excluir_linha).pack(side="left", padx=10)
    tk.Button(frame_buttons, text="Gravar Linha", command=gravar_linha).pack(side="left", padx=10)
    tk.Button(frame_buttons, text="Finalizar", command=janela.destroy).pack(side="left", padx=10)
    tk.Button(frame_buttons, text="Mover Lançamento", command=mover_lancamento).pack(side="left", padx=10)

