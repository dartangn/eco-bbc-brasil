#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-estacas.py -- estacas de terreno geradas por cidadao que entra na FEDERACAO (Settlements.eco):
    ClaimStakesPerCitizen[federacao]   1.5 -> 5     (estacas geradas por cidadao)
    BasePlotsOnClaimStake[federacao]   5   -> 20    (lotes que cada estaca deixa reivindicar)
Pedido do Raul, 09/09/2026: "hoje quem entra na federacao gera 1,5 estacas com 5 papeis; preciso 5 estacas
cada uma com 20". Os arrays sao [cidade, pais, federacao]; so o terceiro valor muda.
Texto do proprio jogo (binario): "As new citizens join this settlement, more claim papers and claim stakes
will be spawned" e "BasePlotsOnClaimStake: the number of plots that a claim stake allows you to claim by
default, specified by settlement type".

    sudo -u ecosrv python3 ajustar-estacas.py --seco   # so mostra
    sudo -u ecosrv python3 ajustar-estacas.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Por isso fica em /opt/eco/pendentes/
e o eco-reiniciar.sh o executa entre o stop e o start do reinicio diario.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Settlements.eco"
SECO = "--seco" in sys.argv
FED = 2   # indice da federacao nos trios [cidade, pais, federacao]
MUDANCAS = {            # chave: (valor esperado hoje, valor novo)
    "ClaimStakesPerCitizen": (1.5, 5.0),
    "BasePlotsOnClaimStake": (5, 20),
}

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)
print("=== Settlements.eco (federacao = 3o valor) ===")
for chave, (esperado, novo) in MUDANCAS.items():
    lista = d.get(chave)
    if not isinstance(lista, list) or len(lista) != 3:
        sys.exit("[XX] %s nao e um trio: %r" % (chave, lista))
    print("  %-24s antes %-22r federacao=%r" % (chave, lista, lista[FED]))
    if lista[FED] != esperado:
        sys.exit("[XX] %s[federacao] = %r, esperava %r -- nao vou tocar" % (chave, lista[FED], esperado))
    lista[FED] = novo
    print("  %-24s depois %r" % ("", lista))
if SECO:
    print("[seco] nada gravado"); sys.exit(0)
bak = CFG + ".antes-estacas-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak); print("  backup: %s" % bak)
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
for chave, (_, novo) in MUDANCAS.items():
    if d2[chave][FED] != novo:
        sys.exit("[XX] releitura nao bate em %s" % chave)
if len(d2) != len(d):
    sys.exit("[XX] releitura: numero de campos mudou")
print("[ok] gravado e conferido relendo do disco")
