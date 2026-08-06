from src.sql import sql_saldos, sql_lancamentos, sql_cadconta

CONTAS_BANCO = ["10101","10102","10103","10104","10105","10106","10107","10108"]

SALDOS_INICIAIS = {
    # "10101": 1500.00,
    # "10102": 2300.00,
}

def gerar_saldos_iniciais():
    contas = sql_cadconta.listar()

    for linha in contas:
        conta = linha[0]
        descrcta = linha[1]

        saldo_inicial = SALDOS_INICIAIS.get(conta, 0.0)

        sql_saldos.inserir(
            conta=conta,
            descrcta=descrcta,
            data="2017-01-01",
            saldo_ant=saldo_inicial,
            debito=0,
            credito=0,
            saldo_atu=saldo_inicial
        )


def recompor_saldos():
    sql_saldos.apagar_todos()
    gerar_saldos_iniciais()
    print("veio aqui---------------------------------------------->")
    lancs = sql_lancamentos.listar_todos_ordenados()
    saldos = {}
    print("veio aqui tambem---------------------------------------------->")

    print (lancs)

    # AGRUPAR POR CONTA + DATA
    agrupado = {}

    for lan in lancs:
        conta = lan["conta"]
        data = lan["data"]
        valor = lan["valor"] or 0
        tipo = lan["tipo"]

        chave = (conta, data)

        if chave not in agrupado:
            agrupado[chave] = {"debito": 0, "credito": 0}

        if tipo == "D":
            agrupado[chave]["debito"] += valor
        else:
            agrupado[chave]["credito"] += valor

    # PROCESSAR DIA A DIA
    for (conta, data), valores in sorted(agrupado.items(), key=lambda x: (x[0][0], x[0][1])):
        descrcta = sql_cadconta.buscar_descr(conta)

        saldo_ant = saldos.get(conta, sql_saldos.buscar_primeiro_saldo(conta))

        debito = valores["debito"]
        credito = valores["credito"]

        saldo_atu = saldo_ant + debito - credito
        saldos[conta] = saldo_atu

        sql_saldos.inserir(
            conta=conta,
            descrcta=descrcta,
            data=data,
            saldo_ant=saldo_ant,
            debito=debito,
            credito=credito,
            saldo_atu=saldo_atu
        )
