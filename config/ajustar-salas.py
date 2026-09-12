#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-salas.py -- vao de ate 2 blocos passa a contar como janela, e a sala continua valendo.

    Rooms.eco:  EmptyBlocksCountAsWindows   false -> true

PEDIDO DO RAUL, 11/09/2026: "mude o nosso para permitir apenas dois blocos seja permitido e
contar como sala fechada". Ele observou que em outros servidores um bloco aberto continua sendo
sala, e aqui nao.

O QUE ESTE CAMPO FAZ, pela wiki oficial (Server_Configuration/Rooms.eco):
    "If enabled, rooms can have empty blocks serve as windows AND STILL COUNT AS A ROOM."

E o TAMANHO do vao nao e configuravel -- e regra de geometria do proprio jogo, descrita na pagina
Rooms da wiki:
    "A room is a space that is completely enclosed with blocks. Gaps in walls for windows and
     doorways can be up to 2 BLOCKS WIDE and 1 block tall, or 2 blocks tall and 1 block wide."

Ou seja: o "ate dois blocos" que o Raul pediu JA E o comportamento padrao do Eco. O que o desliga
neste servidor e o campo estar em false. Ligando, volta a tolerancia de 2 blocos -- nao ha numero
a escolher, e nao da para pedir 3 ou 1.

POR QUE O ARQUIVO NAO EXISTE HOJE
    So existe /opt/eco/server/Configs/Rooms.eco.template. Quando o .eco nao existe, valem os
    padroes do jogo -- e o padrao desta versao (0.14.1.1) e FALSE. A wiki diz que o padrao e
    true: a Strange Loop mudou em alguma versao e a wiki ficou para tras. Por isso servidor mais
    antigo se comporta diferente.

CONSEQUENCIA DE CRIAR O ARQUIVO, e vale saber:
    a partir daqui o jogo le o NOSSO Rooms.eco. Se a Strange Loop mudar o padrao de qualquer campo
    deste arquivo numa atualizacao, a mudanca NAO chega aqui. Por isso o script copia o template
    inteiro e muda UM campo -- o resto continua identico ao de fabrica de hoje.

NAO TOCA em WallBlocksPerWindow (10), que e outra coisa: quantos blocos de parede sao precisos
para permitir um vao SEM PENALIDADE. Aquilo mexe no VALOR da sala, nao em ela ser ou nao ser sala.

    sudo -u ecosrv python3 ajustar-salas.py --seco      # so mostra
    sudo -u ecosrv python3 ajustar-salas.py             # grava
    sudo -u ecosrv python3 ajustar-salas.py --desfazer  # apaga o Rooms.eco (volta ao padrao)

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Fica em /opt/eco/pendentes/ e o
eco-reiniciar.sh o executa entre o stop e o start.
"""
import json, os, shutil, sys, time

CFG = "/opt/eco/server/Configs/Rooms.eco"
TPL = CFG + ".template"
CAMPO = "EmptyBlocksCountAsWindows"
ALVO = True
SECO = "--seco" in sys.argv
DESFAZER = "--desfazer" in sys.argv

print("=== Rooms.eco: vao de ate 2 blocos conta como janela ===")

if DESFAZER:
    if not os.path.exists(CFG):
        print("[ok] o %s nao existe -- ja esta no padrao do jogo." % os.path.basename(CFG))
        sys.exit(0)
    bak = CFG + ".desfeito-" + time.strftime("%Y-%m-%d_%H%M")
    shutil.move(CFG, bak)
    print("[ok] movido para %s -- voltam os padroes do jogo." % bak)
    sys.exit(0)

if not os.path.exists(TPL):
    sys.exit("[XX] nao achei o template %s. Nada foi tocado." % TPL)

with open(TPL, "r", encoding="utf-8-sig") as f:
    base = json.load(f)
if CAMPO not in base:
    sys.exit("[XX] o campo %s nao existe no template -- a versao do Eco mudou. Nada foi tocado." % CAMPO)

existia = os.path.exists(CFG)
d = base
if existia:
    with open(CFG, "r", encoding="utf-8-sig") as f:
        d = json.load(f)
    print("  o Rooms.eco JA existe -- vou alterar so o %s dele" % CAMPO)
else:
    print("  o Rooms.eco NAO existe -- vou cria-lo a partir do template, mudando so um campo")

print("  %-36s de %r para %r" % (CAMPO, d.get(CAMPO), ALVO))
for k in ("WallBlocksPerWindow", "RoomCategoryDiminishingReturnRate", "PaintedBlockHousingBonus"):
    if k in d:
        print("  (intocado) %-30s %r" % (k, d[k]))

if d.get(CAMPO) == ALVO:
    print("[ok] ja esta em %r -- nada a fazer." % ALVO)
    sys.exit(0)
if SECO:
    print("[seco] nada foi gravado.")
    sys.exit(0)

campos_antes = len(d)
if existia:
    bak = CFG + ".antes-salas-" + time.strftime("%Y-%m-%d_%H%M")
    shutil.copy2(CFG, bak)
    print("  backup: %s" % bak)

d[CAMPO] = ALVO
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# confere RELENDO DO DISCO, que e o unico teste que vale
with open(CFG, "r", encoding="utf-8-sig") as f:
    d2 = json.load(f)
if d2.get(CAMPO) is not ALVO:
    if existia:
        shutil.copy2(bak, CFG)
    else:
        os.remove(CFG)
    sys.exit("[XX] a releitura deu %r, esperava %r. Desfeito." % (d2.get(CAMPO), ALVO))
if len(d2) != campos_antes:
    sys.exit("[XX] o arquivo tinha %d campos e ficou com %d. CONFERIR A MAO." % (campos_antes, len(d2)))

try:
    os.chmod(CFG, 0o644)
except Exception:
    pass

print("[ok] gravado e conferido relendo do disco: %s = %r, %d campos (iguais aos do template)"
      % (CAMPO, d2[CAMPO], len(d2)))
print("     Efeito esperado no jogo: vao de ate 2 blocos de largura por 1 de altura (ou 2 de")
print("     altura por 1 de largura) deixa de invalidar a sala. Buraco no TETO continua unindo")
print("     ou invalidando a sala -- isso e regra do jogo e nao muda com este campo.")
