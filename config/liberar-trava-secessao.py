#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
liberar-trava-secessao.py -- liga a OPCAO que permite a federacao proibir que um assentamento-filho
se separe dela. Pedido do Raul, 11/09/2026: "quero so blindar a saida de qualquer usuario da federacao".

    Settlements.eco:  AllowOptionToPreventSettlementsFromSeceding   false -> true

O QUE ISTO FAZ, E O QUE NAO FAZ. Este campo sozinho NAO proibe nada: ele apenas faz APARECER, na
politica de imigracao da federacao, a caixa "AllowChildSettlementsToSecede" (hoje em true e, com a
opcao desligada, nem visivel -- o binario tem os textos "ShowAllowChildSettlementsToSecede" e
"AllowOptionToPreventSettlementsFromSeceding" justamente para isso). Depois de ligar aqui, alguem
precisa, DENTRO DO JOGO, desmarcar essa caixa na politica da federacao -- o que exige uma Mesa de
Imigracao (ImmigrationDeskItem) plantada dentro da influencia dela, conforme a pagina
Settlements;Immigration Policy.xml da Ecopedia do proprio jogo.

Com as duas coisas feitas, o jogo recusa a separacao com as mensagens que ja existem no binario:
    "{0} cannot secede from {1}."
    "{0} doesn't allow child settlements to secede"

NAO COBRE o caso que originou o pedido (pepsy fundou cidade e tirou a pedra do chao): dissolver o
proprio assentamento nao e secessao, e nao ha campo de configuracao para isso. Ver COMANDOS-VERIFICADOS.md.

    sudo -u ecosrv python3 liberar-trava-secessao.py --seco     # so mostra
    sudo -u ecosrv python3 liberar-trava-secessao.py            # grava
    sudo -u ecosrv python3 liberar-trava-secessao.py --desfazer # volta para false

RODAR COM O SERVIDOR PARADO (o Eco regrava os Configs ao desligar). Fica em /opt/eco/pendentes/ e o
eco-reiniciar.sh o executa entre o stop e o start do reinicio diario.
"""
import json, shutil, sys, time

CFG = "/opt/eco/server/Configs/Settlements.eco"
CAMPO = "AllowOptionToPreventSettlementsFromSeceding"
SECO = "--seco" in sys.argv
DESFAZER = "--desfazer" in sys.argv
ALVO = False if DESFAZER else True

with open(CFG, "r", encoding="utf-8") as f:
    texto = f.read()
d = json.loads(texto)

print("=== Settlements.eco: opcao de proibir secessao ===")
if CAMPO not in d:
    sys.exit("[XX] o campo %s nao existe neste Settlements.eco -- a versao do Eco mudou. Nada foi tocado." % CAMPO)
atual = d[CAMPO]
if not isinstance(atual, bool):
    sys.exit("[XX] %s nao e booleano: %r. Nada foi tocado." % (CAMPO, atual))

print("  %-52s antes %r   depois %r" % (CAMPO, atual, ALVO))
# conferencia de contexto: os campos que dizem se a federacao se sustenta sozinha
for k in ("MinCitizensToMaintainSettlement", "MinSubSettlementsToMaintainSettlement",
          "MinCultureToMaintainSettlement", "PostAnnexationSecessionLockDays"):
    if k in d:
        print("  (contexto) %-40s %r" % (k, d[k]))

if atual == ALVO:
    print("[ok] ja esta em %r -- nada a fazer." % ALVO)
    sys.exit(0)
if SECO:
    print("[seco] nada foi gravado.")
    sys.exit(0)

campos_antes = len(d)
bak = CFG + ".antes-secessao-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(CFG, bak)
print("  backup: %s" % bak)

d[CAMPO] = ALVO
with open(CFG, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# confere RELENDO DO DISCO, que e o unico teste que vale
with open(CFG, "r", encoding="utf-8") as f:
    d2 = json.load(f)
if d2.get(CAMPO) != ALVO:
    shutil.copy2(bak, CFG)
    sys.exit("[XX] a releitura deu %r, esperava %r. Backup devolvido." % (d2.get(CAMPO), ALVO))
if len(d2) != campos_antes:
    shutil.copy2(bak, CFG)
    sys.exit("[XX] o arquivo tinha %d campos e ficou com %d. Backup devolvido." % (campos_antes, len(d2)))

print("[ok] gravado e conferido relendo do disco: %s = %r, %d campos preservados"
      % (CAMPO, d2[CAMPO], len(d2)))
print("     FALTA O PASSO DO JOGO: desmarcar 'AllowChildSettlementsToSecede' na politica de")
print("     imigracao da federacao (exige Mesa de Imigracao dentro da influencia dela).")
