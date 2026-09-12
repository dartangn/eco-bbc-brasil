#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-nome.py -- troca as cores do nome do servidor no Network.eco:
    BBC-BRASIL  verde  -> AMARELO      5X  amarelo -> VERDE
(pedido do Raul, 08/09/2026). O resto do nome nao muda.

    sudo -u ecosrv python3 ajustar-nome.py --seco   # so mostra
    sudo -u ecosrv python3 ajustar-nome.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar; editar com ele no ar se perde).
Por isso este arquivo fica em /opt/eco/pendentes/ e o eco-reiniciar.sh o executa entre o stop e o
start do reinicio diario. Nao ha caminho ao vivo: o RCON nao tem comando de nome, e a rota
/api/v1/admin/set/servername exige authtoken de usuario (SLG/Steam), que nao temos.
Limite do jogo (wiki Network.eco): 250 caracteres, aceita <color=...>.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Network.eco"
SECO = "--seco" in sys.argv
VERDE, AMARELO = "#009C3B", "#FFDF00"
ANTES_ESPERADO = ("<color=%s>BBC-BRASIL</color> <color=%s>5X</color>" % (VERDE, AMARELO))
DEPOIS = ("<color=%s>BBC-BRASIL</color> <color=%s>5X</color>" % (AMARELO, VERDE))

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)
nome = d.get("Name", "")
print("=== Network.eco / Name ===")
print("  antes : %s" % nome)
if ANTES_ESPERADO not in nome:
    sys.exit("[XX] o inicio do nome nao e o esperado (%s) -- nao vou tocar" % ANTES_ESPERADO)
novo = nome.replace(ANTES_ESPERADO, DEPOIS, 1)
print("  depois: %s" % novo)
print("  tamanho: %d/250" % len(novo))
if len(novo) > 250:
    sys.exit("[XX] passa de 250 caracteres")
if SECO:
    print("[seco] nada gravado"); sys.exit(0)
bak = CFG + ".antes-nome-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak); print("  backup: %s" % bak)
d["Name"] = novo
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
if d2["Name"] != novo or len(d2) != len(d):
    sys.exit("[XX] releitura nao bate")
print("[ok] gravado e conferido relendo do disco")
