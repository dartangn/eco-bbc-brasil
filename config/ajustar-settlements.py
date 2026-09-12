#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-settlements.py -- baixa os requisitos de FUNDAR e MANTER assentamento no
Settlements.eco, para uma federacao de 1 cidadao nao se dissolver.

    sudo -u ecosrv python3 /opt/eco/scripts/ajustar-settlements.py --seco   # so mostra
    sudo -u ecosrv python3 /opt/eco/scripts/ajustar-settlements.py          # grava

RODAR COM O SERVIDOR PARADO. O Eco regrava os Configs ao desligar; editar com ele no
ar faz a mudanca sumir.

POR QUE (05/09/2026): a federacao fundada pelo Raul num mundo zerado sumiu, com a
pedra de fundacao, no instante em que um segundo jogador entrou. A wiki oficial
(Server_Configuration/Settlements.eco) define:
  MinCitizensToMaintainSettlement  [2,6,15]  "citizens ... in order for a settlement to continue"
  MinCultureToMaintainSettlement   [0,30,120] "culture ... required to continue a parent settlement"
  MinSubSettlementsToMaintainSettlement [2,2] "... or else it goes invalid"
Uma federacao com 1 cidadao, 0 cultura e 0 filhos nao cumpre nenhum dos tres.
O force-enable da pedra dispensa a SALA, nao os requisitos do assentamento.

Valores novos (indice 0 = cidade, 1 = pais, 2 = federacao):
  fundar : 1 cidadao, 0 cultura, 0 sub-assentamentos
  manter : 1 cidadao, 0 cultura, 0 sub-assentamentos
Sobrevive ao wipe (Configs nao sao apagados) e a reinicio. E o plano B que o modelo
anterior escreveu em 28/08 para o Windows (configurar-assentamentos.ps1) e nunca aplicou aqui.
"""
import json, os, shutil, sys, time

CFG = "/opt/eco/server/Configs/Settlements.eco"
SECO = "--seco" in sys.argv

NOVOS = {
    "MinCitizensToFoundSettlement":        [1, 1, 1],
    "MinCitizensToMaintainSettlement":     [1, 1, 1],
    "MinCultureToFoundSettlement":         [0.0, 0.0, 0.0],
    "MinCultureToMaintainSettlement":      [0.0, 0.0, 0.0],
    "MinSubSettlementsToFoundSettlement":  [0, 0],
    "MinSubSettlementsToMaintainSettlement": [0, 0],
}

with open(CFG, "r", encoding="utf-8") as f:
    txt = f.read()
d = json.loads(txt)

print("=== Settlements.eco: requisitos de fundar/manter ===")
faltando = [k for k in NOVOS if k not in d]
if faltando:
    sys.exit("[XX] chaves ausentes no arquivo: %s -- nao vou tocar" % faltando)
for k, v in NOVOS.items():
    atual = d[k]
    if len(atual) != len(v):
        sys.exit("[XX] %s tem %d valores, esperava %d -- nao vou tocar" % (k, len(atual), len(v)))
    print("  %-40s %-20s -> %s" % (k, atual, v))
print("  (intocado) SettlementFoundationBaseInfluence = %s" % d.get("SettlementFoundationBaseInfluence"))

if SECO:
    print("[seco] nada gravado"); sys.exit(0)

bak = CFG + ".antes-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak)
print("  backup: %s" % bak)
for k, v in NOVOS.items():
    d[k] = v
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")

# confere RELENDO do disco
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
erros = [k for k, v in NOVOS.items() if d2.get(k) != v]
if erros:
    sys.exit("[XX] releitura nao bate: %s" % erros)
if d2.get("SettlementFoundationBaseInfluence") != d.get("SettlementFoundationBaseInfluence"):
    sys.exit("[XX] a influencia mudou sem querer")
print("[ok] gravado e conferido relendo do disco: %d chaves" % len(NOVOS))
