# -*- coding: utf-8 -*-
"""
Gera os .override.cs que mudam a CAPACIDADE DE CARGA dos veiculos de escavacao.

O QUE FOI MEDIDO (CLAUDE.md 67.1 e 67.2)
----------------------------------------
So TRES veiculos do jogo tem VehicleToolComponent, e a assinatura e
  Initialize(numSlots, maxWeight, joulesPerDigBlock, joulesPerMineBlock, ...)
com maxWeight em GRAMAS (a unidade interna do Eco).

  Steam Tractor  jogo 2.500 kg   com o mod Early Skid: 1.950 kg   <- o mod REDUZIU 22%
  Skid Steer     jogo 2.800 kg
  Excavator      jogo 3.500 kg

O mod Early Skid faz duas coisas em dois arquivos diferentes, e so uma e anunciada:
  Vehicles/SteamTractor.override.cs          Minable = false -> true   <- a funcao do mod
  AutoGen/Vehicle/SteamTractor.override.cs   2500000 -> 1950000        <- o preco escondido

Este gerador substitui o SEGUNDO (paga a divida da copia congelada, 19.4) e NAO TOCA no
primeiro -- o `Minable = true` e o que faz o trator minerar, e continua valendo.

POR QUE .override.cs GERADO, E NAO `partial`
--------------------------------------------
`MaxWeight`/`InventoryMaxWeightRestriction` nao aparece uma vez em todo o __core__, a API
nao expoe propriedade de peso no VehicleToolComponent, e chamar Initialize de novo pode
ACRESCENTAR restricao em vez de trocar (restricao de inventario e AND: a MENOR venceria e
o valor novo nao teria efeito, EM SILENCIO). Ver 67.3.

TRAVAS (o molde dos geradores que ja rodam aqui -- 33.4)
--------------------------------------------------------
 1. a ancora `Initialize(<slots>, <peso>,` tem de aparecer EXATAMENTE 1 vez
 2. o corpo gerado difere do original do jogo em EXATAMENTE 1 linha
 3. encoding casado com o original (BOM e fim de linha) -- a regra invertida de 19.6
 4. confere RELENDO do disco, nunca o que esta em memoria
 5. --seco grava em pasta separada e nao encosta no servidor

USO (no servidor)
-----------------
  python3 gerar-peso-veiculo.py --seco   --tractor 5000 --skid 5600 --excavator 7000
  python3 gerar-peso-veiculo.py          --tractor 5000 --skid 5600 --excavator 7000
Omitir um veiculo deixa ele intocado.
"""
import argparse
import io
import os
import re
import sys

CORE = "/opt/eco/server/Mods/__core__"
USER = "/opt/eco/server/Mods/UserCode"
DIAG = "/opt/eco/diag-peso"

# nome -> (arquivo relativo, slots esperados, peso ORIGINAL do jogo em gramas)
VEICULOS = {
    "tractor":   ("AutoGen/Vehicle/SteamTractor.cs", 12, 2500000),
    "skid":      ("AutoGen/Vehicle/SkidSteer.cs",     5, 2800000),
    "excavator": ("AutoGen/Vehicle/Excavator.cs",     7, 3500000),
}


def ler_bytes(p):
    with open(p, "rb") as fh:
        return fh.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    for v in VEICULOS:
        ap.add_argument("--" + v, type=int, default=None,
                        help="capacidade nova em KG (nao em gramas)")
    a = ap.parse_args()

    pedidos = {v: getattr(a, v) for v in VEICULOS if getattr(a, v) is not None}
    if not pedidos:
        print("[XX] nenhum veiculo pedido. Use --tractor N --skid N --excavator N (em kg).")
        return 1

    destino_base = DIAG if a.seco else USER
    if a.seco and not os.path.isdir(DIAG):
        os.makedirs(DIAG)

    falhou = False
    for nome, kg in sorted(pedidos.items()):
        rel, slots, peso_jogo = VEICULOS[nome]
        origem = os.path.join(CORE, rel)
        print("=" * 70)
        print("%s  ->  %s kg" % (nome.upper(), kg))
        if not os.path.isfile(origem):
            print("  [XX] nao achei %s" % origem)
            falhou = True
            continue

        bruto = ler_bytes(origem)
        tem_bom = bruto.startswith(b"\xef\xbb\xbf")
        crlf = bruto.count(b"\r\n")
        texto = bruto.decode("utf-8-sig")
        linhas = texto.split("\n")
        print("  original: %d bytes - %d linhas - BOM=%s - CRLF em %d linhas"
              % (len(bruto), len(linhas), tem_bom, crlf))

        # TRAVA 1: ancora unica
        alvo = "Initialize(%d, %d," % (slots, peso_jogo)
        hits = [i for i, l in enumerate(linhas) if alvo in l]
        if len(hits) != 1:
            print("  [XX] a ancora %r aparece %d vezes (esperava 1). ABORTEI."
                  % (alvo, len(hits)))
            print("       -> o jogo mudou o valor ou a forma; conferir antes de gerar C#.")
            falhou = True
            continue
        i = hits[0]
        print("  ancora na linha %d: %s" % (i + 1, linhas[i].strip()))

        novo_peso = kg * 1000
        novas = list(linhas)
        novas[i] = novas[i].replace(alvo, "Initialize(%d, %d," % (slots, novo_peso))
        print("  vira        %d: %s" % (i + 1, novas[i].strip()))

        # TRAVA 2: difere em exatamente 1 linha
        dif = [k for k in range(len(linhas)) if linhas[k] != novas[k]]
        if len(dif) != 1:
            print("  [XX] o corpo diferiria em %d linhas (esperava 1). ABORTEI." % len(dif))
            falhou = True
            continue
        print("  [ok] TRAVA 2: difere do original em exatamente 1 linha")

        # TRAVA 3: encoding casado com o original
        saida_txt = "\n".join(novas)
        dados = saida_txt.encode("utf-8")
        if tem_bom:
            dados = b"\xef\xbb\xbf" + dados

        rel_saida = rel.replace(".cs", ".override.cs")
        destino = os.path.join(destino_base, rel_saida)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        antigo = None
        if os.path.isfile(destino):
            antigo = ler_bytes(destino)
            print("  ja existe um override ali (%d bytes) -- sera SUBSTITUIDO" % len(antigo))
        with open(destino, "wb") as fh:
            fh.write(dados)

        # TRAVA 4: reler do disco
        conf = ler_bytes(destino)
        if conf != dados:
            print("  [XX] o arquivo gravado difere do que eu montei. ABORTEI.")
            falhou = True
            continue
        ctexto = conf.decode("utf-8-sig").split("\n")
        if len(ctexto) != len(linhas):
            print("  [XX] contagem de linhas mudou: %d -> %d" % (len(linhas), len(ctexto)))
            falhou = True
            continue
        redif = [k for k in range(len(linhas)) if linhas[k] != ctexto[k]]
        if len(redif) != 1 or ("Initialize(%d, %d," % (slots, novo_peso)) not in ctexto[redif[0]]:
            print("  [XX] relendo do disco, a diferenca nao e a esperada. ABORTEI.")
            falhou = True
            continue
        print("  [ok] relido do disco: %d bytes, BOM=%s, 1 linha diferente, e a certa"
              % (len(conf), conf.startswith(b"\xef\xbb\xbf")))
        print("  -> %s" % destino)

    print("=" * 70)
    if falhou:
        print("[XX] alguma trava reprovou. NAO instalar.")
        return 1
    if a.seco:
        print("[ok] MODO SECO -- nada foi instalado. Os arquivos estao em %s" % DIAG)
    else:
        print("[ok] instalado. Precisa de REINICIO VIGIADO (Regra 18).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
