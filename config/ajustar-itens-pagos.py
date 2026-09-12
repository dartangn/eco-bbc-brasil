#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
ajustar-itens-pagos.py -- libera os itens do Marketplace (comprados com Eco Credits) para serem
VENDIDOS em loja de jogador e COLOCADOS por qualquer um. Pedido do Raul, 10/09/2026:
"deixarmos vender os itens que sao comprados no marketplace para qualquer um colocar e a pessoa
que fez vender".

O arquivo e o Configs/StrangeWorlds.eco, que NAO EXISTE neste servidor -- so o .template. Enquanto
nao existe, valem os padroes do template, e os dois campos que interessam vem FALSE. Este script
cria o arquivo a partir do template, mudando so os dois campos.

Os quatro campos, com a descricao da wiki oficial (Server_Configuration/StrangeWorlds.eco, lida em
10/09/2026) e o que o proprio binario diz nas mensagens de UI:

  AllowPaidItemsInPlayerStores          false -> TRUE
      wiki: "If true, paid variants of items will be allowed in stores."
      binario, com o valor false: "Paid items can't be sold on this server" e "Paid items cannot be
      bought or sold in stores in this world (due to world config setting)" e "Note: this item
      requires a Strange Blueprint to build, and you cannot list it in stores on this world due to
      current config." E ESTE que libera a venda.

  AllowUsingPaidItemsWithoutBlueprint   false -> TRUE
      TRUE = quem NAO tem o blueprint pode colocar o item no mundo. Confirmado pelo Raul, dono do
      servidor, em 10/09/2026: "essa segunda e permitir que quem nao tem blueprint coloque o item
      no mundo". Concorda com o nome do campo e com as mensagens que o binario mostra quando o
      valor e false: "You do not own the blueprint needed for that recipe", "Could not place: too
      many {0} in world, not enough blueprints owned by users", "If you own this blueprint but
      cant place it, a server admin may have spawned items without ownership".
      A WIKI ESTA ERRADA neste campo: ela diz "If true, only players owning a blueprint can place
      items using it", que e a descricao do FALSE. Tres fontes contra uma; fica registrado para
      ninguem "corrigir" o valor lendo a wiki depois.
      E este campo, junto com o de cima, que fecha o par pedido: quem tem o blueprint fabrica e
      vende na loja, e quem comprou consegue colocar.

  BlockUsingAnyPaidItem                 false, INTOCADO
      wiki: "If true, paid variants cannot be crafted at all and the marketplace cannot be opened."
      E o oposto do que se quer.

  AcceptItemsBoughtInAnyWorld           true, INTOCADO -- item comprado em qualquer mundo vale aqui.

AVISO que o proprio jogo carrega, e que vale ler antes de decidir: "Detected {0} in world but not
enough Blueprint ownership for that to be possible. (allowed during amnesty period, but will be
deleted in a near-future update)." Ou seja, a Strange Loop monitora item pago em mundo sem posse
correspondente e avisa que vai apagar o excedente numa atualizacao futura. Nao se sabe se esse
monitor respeita o AllowUsingPaidItemsWithoutBlueprint; se um dia esses itens sumirem do mundo,
esta e a primeira suspeita.

    sudo -u ecosrv python3 ajustar-itens-pagos.py --seco   # so mostra
    sudo -u ecosrv python3 ajustar-itens-pagos.py          # grava

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Fica em /opt/eco/pendentes/ e o
eco-reiniciar.sh o executa entre o stop e o start do reinicio diario.
"""
import json, os, shutil, sys, time

CFG = "/opt/eco/server/Configs/StrangeWorlds.eco"
TPL = CFG + ".template"
SECO = "--seco" in sys.argv
QUERO = {"AllowPaidItemsInPlayerStores": True, "AllowUsingPaidItemsWithoutBlueprint": True}
# o que NAO pode mudar, com o valor esperado -- armadilha contra template diferente numa atualizacao
INTOCADOS = {"BlockUsingAnyPaidItem": False, "AcceptItemsBoughtInAnyWorld": True}

origem = CFG if os.path.exists(CFG) else TPL
if not os.path.exists(origem):
    sys.exit("[XX] nao achei nem %s nem %s" % (CFG, TPL))
with open(origem, "r", encoding="utf-8") as f:
    d = json.load(f)
print("=== StrangeWorlds.eco: itens do Marketplace em loja de jogador ===")
print("  origem: %s%s" % (origem, "  (o .eco nao existia; criando do template)" if origem == TPL else ""))

for k, esperado in QUERO.items():
    if k not in d:
        sys.exit("[XX] o campo %s nao existe em %s -- template mudou, revisar antes de gravar" % (k, origem))
    if not isinstance(d[k], bool):
        sys.exit("[XX] %s nao e booleano: %r" % (k, d[k]))
    print("  %-38s %r -> %r" % (k, d[k], esperado))
    d[k] = esperado
for k, esperado in INTOCADOS.items():
    if d.get(k) != esperado:
        sys.exit("[XX] %s esta %r e eu esperava %r -- parando para nao mudar o que nao entendi"
                 % (k, d.get(k), esperado))
    print("  %-38s %r  (intocado)" % (k, d[k]))

if SECO:
    print("[seco] nada gravado"); sys.exit(0)
if os.path.exists(CFG):
    bak = CFG + ".antes-itens-pagos-" + time.strftime("%Y-%m-%d_%H%M")
    shutil.copy2(CFG, bak); print("  backup: %s" % bak)
else:
    print("  (sem backup: o arquivo nao existia; para desfazer, apagar %s)" % CFG)
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
for k, esperado in QUERO.items():
    if d2.get(k) is not esperado:
        sys.exit("[XX] releitura nao bate em %s: %r" % (k, d2.get(k)))
for k, esperado in INTOCADOS.items():
    if d2.get(k) is not esperado:
        sys.exit("[XX] releitura mudou %s: %r" % (k, d2.get(k)))
if len(d2) != len(d):
    sys.exit("[XX] releitura: numero de campos mudou")
print("[ok] gravado e conferido relendo do disco (%d campos)" % len(d2))
