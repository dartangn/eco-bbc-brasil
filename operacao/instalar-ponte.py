#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
instalar-ponte.py -- instala o PonteServidor.cs no reinicio diario, com rede de seguranca.

    /opt/eco/mods-desativados/KabongBrasil/PonteServidor.cs.corrigido-nao-instalado
        ->  /opt/eco/server/Mods/UserCode/KabongBrasil/PonteServidor.cs

POR QUE ELE PRECISA EXISTIR
    O eco-reiniciar.sh avisa os jogadores e manda limpar o entulho escrevendo em /opt/eco/ponte.
    Quem LE essa pasta e o PonteServidor.cs -- e ele nao esta instalado desde 08/09/2026, quando
    uma chamada errada dele (NotificationCategory, 18 erros CS) derrubou o servidor. Sem ele, o
    aviso e o pedido de entulho ficam no disco e ninguem ve: foi exatamente o que os jogadores
    relataram em 12/09 ("os avisos de reinicio nao chegam mais").

    A correcao e de UMA linha, ja feita no arquivo `.corrigido-nao-instalado`:
        ServerMessageToAll(Localizer.DoStr(texto))      <- 1 argumento, forma do SimCommands.cs:446
    em vez da forma de 3 argumentos, cujo `NotificationCategory` nao resolvia neste arquivo.

A REGRA QUE ESTE SCRIPT TEM DE RESPEITAR, E COMO ELE RESPEITA
    "Nunca instalar .cs novo e deixar para o proximo reinicio" existe porque foi assim que o
    servidor caiu: erro de compilacao, 3 arranques falhos, e a unidade do systemd travada por
    30 min exigindo root -- de madrugada, sem ninguem olhando.

    Aqui o risco e desarmado por DESFAZER AUTOMATICO, e nao por confianca: este script anota o
    que instalou em /opt/eco/pendentes/instalados-neste-reinicio.txt, e o eco-reiniciar.sh, se
    achar `error CS` ou "Failed to start" no arranque, TIRA o arquivo e sobe de novo. O pior caso
    passa a ser "o servidor volta sem a ponte", que e exatamente o estado de hoje.

    sudo -u ecosrv python3 instalar-ponte.py --seco   # so mostra
    sudo -u ecosrv python3 instalar-ponte.py         # instala

RODA COM O SERVIDOR PARADO, pela fila /opt/eco/pendentes/ do eco-reiniciar.sh.
Imprimir "[ok]" na ultima linha e o que faz o eco-reiniciar.sh mover este arquivo para feitos/.
"""
import io, os, shutil, sys

FONTE  = "/opt/eco/mods-desativados/KabongBrasil/PonteServidor.cs.corrigido-nao-instalado"
DESTINO = "/opt/eco/server/Mods/UserCode/KabongBrasil/PonteServidor.cs"
LISTA  = "/opt/eco/pendentes/instalados-neste-reinicio.txt"
DIARIO = "/opt/eco/ponte-vida.txt"
SECO   = "--seco" in sys.argv

print("=== instalar PonteServidor.cs (a ponte do aviso e do entulho) ===")

if os.path.exists(DESTINO):
    print("[ok] ja esta instalado em %s -- nada a fazer." % DESTINO)
    sys.exit(0)

if not os.path.exists(FONTE):
    sys.exit("[XX] nao achei %s. Nada foi tocado." % FONTE)

# A REDE DE SEGURANCA TEM DE ESTAR NO LUGAR ANTES DO SALTO.
# Este script so pode instalar um .cs de madrugada porque o eco-reiniciar.sh DESFAZ sozinho se o
# arranque acusar erro. Se a versao instalada em /usr/local/bin for a antiga, esse desfazer nao
# existe -- e ai seria de novo "instalar .cs e deixar para o proximo reinicio", que em 08/09
# deixou o servidor fora do ar com a unidade do systemd travada por 30 min.
# Conferir a dependencia aqui, e nao confiar em alguem lembrar.
REINICIADOR = "/usr/local/bin/eco-reiniciar.sh"
try:
    orquestrador = io.open(REINICIADOR, encoding="utf-8", errors="replace").read()
except Exception as e:
    sys.exit("[XX] nao consegui ler %s (%s). Nada foi tocado." % (REINICIADOR, e))
if "DESFAZENDO" not in orquestrador:
    sys.exit("[XX] o %s instalado NAO tem o desfazer automatico.\n"
             "     Sem ele, um erro de compilacao as 03h deixa o servidor fora do ar.\n"
             "     Rode antes, como root:  sudo bash ~/instalar-reiniciar.sh\n"
             "     Nada foi tocado." % REINICIADOR)

texto = io.open(FONTE, encoding="utf-8", errors="strict").read()

# O CODIGO, sem os comentarios de linha. A primeira versao desta trava procurava
# "NotificationCategory" no arquivo inteiro e reprovou a versao CERTA, porque a palavra aparece
# no comentario que explica por que ela saiu. Filtro largo produz falso alarme, e falso alarme
# treina a ignorar aviso -- a trava tem de olhar o que o compilador olha.
codigo = "\n".join(linha.split("//")[0] for linha in texto.splitlines())

# --- travas de entrada: o que quebrou em 08/09 nao pode voltar --------------
if "NotificationCategory" in codigo:
    sys.exit("[XX] o CODIGO ainda usa NotificationCategory -- e o tipo que deu CS0103 e derrubou\n"
             "     o servidor em 08/09. Esta e a versao QUEBRADA. Nada foi tocado.")
if "ServerMessageToAll(Localizer.DoStr(texto))" not in codigo:
    sys.exit("[XX] nao achei a chamada de 1 argumento que e a correcao. Nada foi tocado.")
if "using System.Threading;" not in codigo:
    sys.exit("[XX] falta `using System.Threading;` e o arquivo usa Timer. Nada foi tocado.")
nao_ascii = [c for c in texto if ord(c) > 127]
if nao_ascii:
    sys.exit("[XX] o arquivo tem %d caractere(s) fora do ASCII. Nada foi tocado." % len(nao_ascii))
if texto.count("{") != texto.count("}"):
    sys.exit("[XX] chaves desbalanceadas (%d x %d). Nada foi tocado." % (texto.count("{"), texto.count("}")))

print("  fonte  : %s (%d bytes)" % (FONTE, len(texto)))
print("  destino: %s" % DESTINO)
print("  travas : sem NotificationCategory, com a chamada de 1 argumento, ASCII, chaves ok")

if SECO:
    print("[seco] nada foi gravado.")
    sys.exit(0)

# o diario e a PROVA DE VIDA: apagar antes para que a presenca dele depois signifique
# "o mod acordou NESTE arranque", e nao "existia de antes"
try:
    if os.path.exists(DIARIO):
        os.remove(DIARIO)
        print("  diario anterior apagado (para a prova de vida valer so deste arranque)")
except Exception as e:
    print("  (nao consegui apagar o diario: %s -- segue)" % e)

shutil.copy2(FONTE, DESTINO)

conferido = io.open(DESTINO, encoding="utf-8", errors="strict").read()
if conferido != texto:
    os.remove(DESTINO)
    sys.exit("[XX] a releitura do destino nao bateu com a fonte. Desfeito.")

# anota para o eco-reiniciar.sh saber o que TIRAR se o arranque acusar erro
with io.open(LISTA, "a", encoding="ascii") as f:
    f.write(DESTINO + "\n")

print("[ok] instalado e conferido relendo do disco (%d bytes)." % len(conferido))
print("     Se este arranque acusar 'error CS' ou 'Failed to start', o eco-reiniciar.sh TIRA")
print("     este arquivo e sobe de novo sozinho.")
print("     Prova de que funcionou: %s deve existir e trazer 'ATIVO por Initialize'." % DIARIO)
