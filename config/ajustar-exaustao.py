#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-exaustao.py -- desliga a exaustao no Difficulty.eco (GameSettings.ExhaustionEnabled).

    sudo -u ecosrv python3 /opt/eco/scripts-py/ajustar-exaustao.py --seco   # so mostra
    sudo -u ecosrv python3 /opt/eco/scripts-py/ajustar-exaustao.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar).
Chave confirmada em 07/09/2026: Configs/Difficulty.eco -> "GameSettings": { "ExhaustionEnabled": true }
(o Difficulty.eco e ANINHADO -- ler pelo primeiro nivel devolve vazio, CLAUDE 16.2).
Motivo: a testadora Pinky ficou 9h22m sem poder trabalhar em 05/09; servidor de teste/aberto
com exaustao ligada bloqueia jogador. Exhaustion.eco (horas por dia) fica intocado.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Difficulty.eco"
SECO = "--seco" in sys.argv

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)
gs = d.get("GameSettings")
if not isinstance(gs, dict) or "ExhaustionEnabled" not in gs:
    sys.exit("[XX] nao achei GameSettings.ExhaustionEnabled -- nao vou tocar")
print("=== Difficulty.eco ===")
print("  GameSettings.ExhaustionEnabled  %s -> False" % gs["ExhaustionEnabled"])
print("  (intocados) StackSizeMultiplier=%s WeightMultiplier=%s AnimalBehavior=%s" % (
    gs.get("AdvancedGameSettings", {}).get("StackSizeMultiplier"),
    gs.get("AdvancedGameSettings", {}).get("WeightMultiplier"), gs.get("AnimalBehavior")))
if SECO:
    print("[seco] nada gravado"); sys.exit(0)
bak = CFG + ".antes-exaustao-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak); print("  backup: %s" % bak)
gs["ExhaustionEnabled"] = False
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
if d2["GameSettings"]["ExhaustionEnabled"] is not False:
    sys.exit("[XX] releitura nao bate")
if d2["GameSettings"].get("AdvancedGameSettings") != gs.get("AdvancedGameSettings"):
    sys.exit("[XX] AdvancedGameSettings mudou sem querer")
print("[ok] gravado e conferido relendo do disco")
