#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-remote-address.py -- grava RemoteAddress e WebServerUrl no Network.eco.

    sudo -u ecosrv python3 /opt/eco/scripts-py/ajustar-remote-address.py --seco   # so mostra
    sudo -u ecosrv python3 /opt/eco/scripts-py/ajustar-remote-address.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar).

Por que (07/09/2026): jogadoras entram por IP direto (ENDERECO-DO-SERVIDOR:27040) mas pela LISTA
publica "aparece e nao baixa nada". No arranque das 16:50 o servidor logou
"No UPnP device with public ip was found" e o Network.eco tem RemoteAddress = "" e
WebServerUrl = "". A wiki oficial (Server_Configuration/Network.eco) e o texto do proprio
jogo dizem: RemoteAddress e "o endereco que deve ser usado para acessar o servidor; se nao
informado, e detectado automaticamente"; WebServerUrl "se nao informado, usa o IP remoto".
Com UPnP falhando atras do MikroTik, a deteccao automatica e a suspeita. Gravar o endereco
exato tira a adivinhacao do caminho. Formato do jogo: remote_host[:port].
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Network.eco"
REMOTO = "ENDERECO-DO-SERVIDOR:27040"
WEB = "http://ENDERECO-DO-SERVIDOR:27041"
SECO = "--seco" in sys.argv

with open(CFG, "r", encoding="utf-8") as f:
    d = json.load(f)
for k in ("RemoteAddress", "WebServerUrl", "GameServerPort", "WebServerPort"):
    if k not in d:
        sys.exit("[XX] nao achei %s no Network.eco -- nao vou tocar" % k)
if d["GameServerPort"] != 27040 or d["WebServerPort"] != 27041:
    sys.exit("[XX] portas inesperadas: %s/%s" % (d["GameServerPort"], d["WebServerPort"]))
print("=== Network.eco ===")
print("  RemoteAddress  %r -> %r" % (d["RemoteAddress"], REMOTO))
print("  WebServerUrl   %r -> %r" % (d["WebServerUrl"], WEB))
print("  (intocados) PublicServer=%s GameServerPort=%s WebServerPort=%s UPnPEnabled=%s" % (
    d["PublicServer"], d["GameServerPort"], d["WebServerPort"], d["UPnPEnabled"]))
if SECO:
    print("[seco] nada gravado"); sys.exit(0)
bak = CFG + ".antes-remote-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak); print("  backup: %s" % bak)
d["RemoteAddress"] = REMOTO
d["WebServerUrl"] = WEB
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
if d2["RemoteAddress"] != REMOTO or d2["WebServerUrl"] != WEB:
    sys.exit("[XX] releitura nao bate")
if len(d2) != len(d):
    sys.exit("[XX] numero de campos mudou")
print("[ok] gravado e conferido relendo do disco")
