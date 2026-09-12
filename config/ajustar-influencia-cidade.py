#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-influencia-cidade.py -- poe a influencia INICIAL da CIDADE no valor pedido (Settlements.eco).

Historico deste numero:
    45   padrao do jogo
    90   aplicado em 11/09/2026 06:47 (dobro). Medido em campo pelo Raul: "funcionou mas ficou
         grande demais"
    65   pedido do Raul em 11/09/2026, depois de ver o 90 no mapa

Influencia se comporta como RAIO em blocos (medido em 27/08/2026: 2000 cobre meia-diagonal de
1414 num mundo de 2000 blocos de lado). Entao:
    45 -> raio 45,  area 1,00x (referencia)
    65 -> raio 65,  area 2,09x
    90 -> raio 90,  area 4,00x
65 e o meio-termo em AREA entre o padrao e o dobro, nao em raio -- por isso ele parece bem menor
que 90 no mapa.

NAO TOCA em nada que mexa na influencia vinda de cultura ou no total:
    CultureToInfluenceMappingPerSettlementType   cultura -> influencia
    SettlementInfluenceMultiplier                multiplicador geral
    ScaleInfluenceBasedOnWorldSize               True
    e o pais e a federacao do trio ficam como estao

    sudo -u ecosrv python3 ajustar-influencia-cidade.py --seco   # so mostra
    sudo -u ecosrv python3 ajustar-influencia-cidade.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Fica em /opt/eco/pendentes/ e o
eco-reiniciar.sh o executa entre o stop e o start.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Settlements.eco"
CAMPO = "SettlementFoundationBaseInfluence"
ESPERADO = 90.0   # o que deve estar la agora; se nao estiver, aborta em vez de adivinhar
ALVO = 65.0
SECO = "--seco" in sys.argv

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== Settlements.eco: influencia INICIAL da cidade ===")
if CAMPO not in d:
    sys.exit("[XX] o campo %s nao existe -- a versao do Eco mudou. Nada foi tocado." % CAMPO)
trio = d[CAMPO]
if not (isinstance(trio, list) and len(trio) == 3):
    sys.exit("[XX] %s nao e um trio: %r. Nada foi tocado." % (CAMPO, trio))

print("  %-38s cidade %-8r pais %-8r federacao %r" % (CAMPO, trio[0], trio[1], trio[2]))
for k in ("SettlementInfluenceMultiplier", "ScaleInfluenceBasedOnWorldSize"):
    if k in d:
        print("  (intocado) %-36s %r" % (k, d[k]))

if float(trio[0]) == ALVO:
    print("[ok] a cidade ja esta em %r -- nada a fazer." % ALVO)
    sys.exit(0)
if float(trio[0]) != ESPERADO:
    sys.exit("[XX] a cidade esta em %r, e eu esperava %r. Alguem mexeu nisto. Nada foi tocado."
             % (trio[0], ESPERADO))

print("  cidade: %r -> %r   (raio %d -> %d blocos, area %.2fx -> %.2fx do padrao 45)"
      % (ESPERADO, ALVO, int(ESPERADO), int(ALVO), (ESPERADO / 45.0) ** 2, (ALVO / 45.0) ** 2))
print("  pais e federacao ficam como estao")
if SECO:
    print("[seco] nada foi gravado.")
    sys.exit(0)

campos_antes = len(d)
bak = CFG + ".antes-influencia65-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak)
print("  backup: %s" % bak)

d[CAMPO] = [ALVO, trio[1], trio[2]]
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
novo = d2.get(CAMPO)
if not (isinstance(novo, list) and len(novo) == 3 and float(novo[0]) == ALVO
        and novo[1] == trio[1] and novo[2] == trio[2]):
    shutil.copy2(bak, CFG)
    sys.exit("[XX] a releitura deu %r, esperava [%r, %r, %r]. Backup devolvido."
             % (novo, ALVO, trio[1], trio[2]))
if len(d2) != campos_antes:
    shutil.copy2(bak, CFG)
    sys.exit("[XX] o arquivo tinha %d campos e ficou com %d. Backup devolvido." % (campos_antes, len(d2)))

print("[ok] gravado e conferido relendo do disco: %s = %r, %d campos preservados"
      % (CAMPO, novo, len(d2)))
