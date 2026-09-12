#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-abandono.py -- cidadao ABANDONADO passa a gerar o mesmo que cidadao ativo (Settlements.eco),
para cidade, pais e federacao. Pedido do Raul, 09/09/2026: "atualizar o valor do abandono pra ser o mesmo
de cidadao nao abandonado (que ai nao perde estaca/papel)".

Copia, trio por trio [cidade, pais, federacao]:
    SettlementClaimsPerCitizen        -> SettlementClaimsPerAbandonedCitizen
    HomesteadSupportClaimsPerCitizen  -> HomesteadSupportClaimsPerAbandonedCitizen
    ClaimStakesPerCitizen             -> ClaimStakesPerAbandonedCitizen
Le os valores ATUAIS do arquivo (nao ha numero fixo aqui): o que o cidadao ativo gera, o abandonado tambem gera.
O painel da federacao no jogo (print do Raul, 09/09) mostrava: ativo 40 papeis / 5 homestead / 5 estacas;
abandonado 5 / 3 / 0,5.

    sudo -u ecosrv python3 ajustar-abandono.py --seco   # so mostra
    sudo -u ecosrv python3 ajustar-abandono.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Fica em /opt/eco/pendentes/ e o
eco-reiniciar.sh o executa entre o stop e o start do reinicio diario.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Settlements.eco"
SECO = "--seco" in sys.argv
PARES = [
    ("SettlementClaimsPerCitizen",       "SettlementClaimsPerAbandonedCitizen"),
    ("HomesteadSupportClaimsPerCitizen", "HomesteadSupportClaimsPerAbandonedCitizen"),
    ("ClaimStakesPerCitizen",            "ClaimStakesPerAbandonedCitizen"),
]

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)
print("=== Settlements.eco: abandonado = ativo, nos trios [cidade, pais, federacao] ===")
for ativo, abandonado in PARES:
    a, b = d.get(ativo), d.get(abandonado)
    if not (isinstance(a, list) and isinstance(b, list) and len(a) == 3 and len(b) == 3):
        sys.exit("[XX] %s / %s nao sao trios: %r / %r" % (ativo, abandonado, a, b))
    print("  %-42s ativo %-18r abandonado antes %-18r" % (abandonado, a, b))
    d[abandonado] = list(a)
    print("  %-42s %-24s abandonado depois %r" % ("", "", d[abandonado]))
if SECO:
    print("[seco] nada gravado"); sys.exit(0)
bak = CFG + ".antes-abandono-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak); print("  backup: %s" % bak)
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
for ativo, abandonado in PARES:
    if d2[abandonado] != d2[ativo]:
        sys.exit("[XX] releitura nao bate em %s" % abandonado)
if len(d2) != len(d):
    sys.exit("[XX] releitura: numero de campos mudou")
print("[ok] gravado e conferido relendo do disco")
