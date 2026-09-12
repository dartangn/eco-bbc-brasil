#!/usr/bin/env python3
"""mais-minerio.py -- aumenta minerio no subsolo, editando o WorldGenerator.eco.

    python3 mais-minerio.py --seco                 # so mostra o plano, nao grava
    python3 mais-minerio.py                         # aplica (fatores padrao)
    python3 mais-minerio.py --chance 3 --veio 2     # fatores proprios

SO VALE EM MUNDO NOVO. A geracao le este arquivo uma unica vez; mudar depois nao
tem efeito nenhum no mundo existente.

O QUE FOI DESCOBERTO (03/09/2026), e por que ha DOIS botoes e nao um
------------------------------------------------------------------------
Cada deposito e um "Eco.WorldGenerator.DepositTerrainModule" com estes campos:

    SpawnPercentChance  chance de comecar um deposito em cada posicao  -> QUANTOS veios
    BlocksCountRange    min/max de blocos que o veio tera              -> TAMANHO do veio
    DepthRange          onde o deposito pode comecar
    DepositDepthRange   ate onde ele se estende
    DirectionWeights    forma do veio (achatado, vertical...)

Multiplicar so a chance enche o mapa de veios minusculos. Multiplicar so o tamanho
deixa o veio dificil de achar mas rico. O padrao 2x chance + 1,5x tamanho da cerca
de 3x de minerio, mantendo a sensacao de procurar.

O QUE ESTE SCRIPT NAO TOCA, DE PROPOSITO
------------------------------------------------------------------------
    EmptyBlock      -> nao e minerio, e CAVERNA. Multiplicar viraria queijo suico.
    LimestoneBlock  -> e pedra de construcao, nao minerio.
Qualquer bloco fora da lista MINERIOS e ignorado e relatado no fim.
"""

import json
import shutil
import sys
import datetime

ARQ = "/opt/eco/server/Configs/WorldGenerator.eco"

# Somente estes. A lista e explicita de proposito: curinga aqui apagaria cavernas.
MINERIOS = {
    "IronOreBlock",
    "GoldOreBlock",
    "CopperOreBlock",
    "CrushedCopperOreBlock",
    "CoalBlock",
    "SulfurBlock",
}

TIPO_DEPOSITO = "Eco.WorldGenerator.DepositTerrainModule"


def parse_args(argv):
    fator_chance, fator_veio, seco, arq = 2.0, 1.5, False, ARQ
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--seco":
            seco = True
        elif a == "--chance":
            i += 1
            fator_chance = float(argv[i])
        elif a == "--veio":
            i += 1
            fator_veio = float(argv[i])
        elif a == "--arquivo":
            i += 1
            arq = argv[i]
        else:
            sys.exit("argumento desconhecido: %s" % a)
        i += 1
    return fator_chance, fator_veio, seco, arq


def indexa_ids(o, mapa):
    """O JSON usa $id / $ref, entao o mesmo objeto de bloco e compartilhado.
    Precisamos do indice para resolver um $ref de volta ao nome do bloco."""
    if isinstance(o, dict):
        if "$id" in o and "Type" in o:
            mapa[o["$id"]] = o["Type"]
        for v in o.values():
            indexa_ids(v, mapa)
    elif isinstance(o, list):
        for v in o:
            indexa_ids(v, mapa)


def nome_bloco(b, mapa):
    if not isinstance(b, dict):
        return "?"
    if "Type" in b:
        return b["Type"].split(",")[0].split(".")[-1]
    if "$ref" in b:
        return mapa.get(b["$ref"], "?").split(",")[0].split(".")[-1]
    return "?"


def coleta_depositos(o, mapa, achados):
    if isinstance(o, dict):
        if o.get("$type", "").startswith(TIPO_DEPOSITO) and "SpawnPercentChance" in o:
            achados.append(o)
        for v in o.values():
            coleta_depositos(v, mapa, achados)
    elif isinstance(o, list):
        for v in o:
            coleta_depositos(v, mapa, achados)


def main():
    fator_chance, fator_veio, seco, arq = parse_args(sys.argv)

    print("############ MAIS MINERIO NO SUBSOLO ############")
    print("arquivo      : %s" % arq)
    print("fator chance : %sx  (quantos veios)" % fator_chance)
    print("fator veio   : %sx  (blocos por veio)" % fator_veio)
    print("modo         : %s" % ("SECO -- nada sera gravado" if seco else "APLICAR"))
    print("")

    with open(arq, "r", encoding="utf-8") as f:
        dados = json.load(f)

    mapa = {}
    indexa_ids(dados, mapa)

    achados = []
    coleta_depositos(dados, mapa, achados)
    print("=== depositos encontrados: %d ===" % len(achados))
    if not achados:
        sys.exit("[XX] nenhum DepositTerrainModule -- arquivo inesperado, abortando")

    print("")
    print("%-24s %10s %10s   %14s %14s" % ("BLOCO", "chance", "-> nova", "veio", "-> novo"))
    print("-" * 80)

    alterados, ignorados = 0, {}
    for d in achados:
        bloco = nome_bloco(d.get("BlockType") or d.get("Block") or {}, mapa)
        if bloco not in MINERIOS:
            ignorados[bloco] = ignorados.get(bloco, 0) + 1
            continue

        ch_velha = d["SpawnPercentChance"]
        # Teto de 0.25: acima disso o subsolo vira minerio macico em vez de veio.
        ch_nova = min(round(ch_velha * fator_chance, 6), 0.25)

        bc = d.get("BlocksCountRange")
        if isinstance(bc, dict) and "min" in bc and "max" in bc:
            v_velho = "%g..%g" % (bc["min"], bc["max"])
            n_min = round(bc["min"] * fator_veio, 1)
            n_max = round(bc["max"] * fator_veio, 1)
            v_novo = "%g..%g" % (n_min, n_max)
        else:
            v_velho = v_novo = "-"
            n_min = n_max = None

        print("%-24s %10g %10g   %14s %14s" % (bloco, ch_velha, ch_nova, v_velho, v_novo))

        if not seco:
            d["SpawnPercentChance"] = ch_nova
            if n_min is not None:
                bc["min"] = n_min
                bc["max"] = n_max
        alterados += 1

    print("-" * 80)
    print("depositos de minerio alterados: %d" % alterados)
    if ignorados:
        print("")
        print("=== IGNORADOS de proposito (nao sao minerio) ===")
        for b, n in sorted(ignorados.items()):
            porque = {
                "EmptyBlock": "e CAVERNA -- multiplicar viraria queijo suico",
                "LimestoneBlock": "e pedra de construcao, nao minerio",
            }.get(b, "fora da lista MINERIOS")
            print("   %-24s %dx   %s" % (b, n, porque))

    if alterados == 0:
        sys.exit("[XX] nada casou com a lista de minerios -- abortando sem gravar")

    if seco:
        print("")
        print("############ MODO SECO -- nada foi gravado ############")
        return

    # Backup com a data, ao lado do arquivo. Sobrescrever config sem copia foi
    # armadilha paga neste projeto mais de uma vez.
    selo = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    bkp = "%s.antes-minerio-%s" % (arq, selo)
    shutil.copy2(arq, bkp)
    print("")
    print("backup: %s" % bkp)

    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    # Conferir LENDO DE VOLTA do disco, nao confiando no objeto em memoria.
    # A regra do projeto: o Eco regrava configs, e afirmacao sem releitura ja enganou.
    with open(arq, "r", encoding="utf-8") as f:
        conf = json.load(f)
    m2 = {}
    indexa_ids(conf, m2)
    a2 = []
    coleta_depositos(conf, m2, a2)
    ok = sum(
        1
        for d in a2
        if nome_bloco(d.get("BlockType") or d.get("Block") or {}, m2) in MINERIOS
    )
    print("relido do disco: %d depositos, %d de minerio" % (len(a2), ok))
    if ok != alterados:
        sys.exit("[XX] contagem nao bate depois de gravar -- restaurar %s" % bkp)

    print("")
    print("############ APLICADO ############")
    print("SO tem efeito em mundo NOVO. Regerar para valer.")


if __name__ == "__main__":
    main()
