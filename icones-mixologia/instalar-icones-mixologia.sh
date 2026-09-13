#!/bin/bash
# Troca o MixologyMod.unity3d por uma versao com os icones RECORTADOS (com canal alfa).
#
# POR QUE
#   Os 65 icones do mod estao em DXT1 -- formato SEM canal alfa -- sobre um fundo
#   degrade pastel. Por isso saem com um quadrado na placa e o type="nobg" nao faz
#   nada: nao ha transparencia para respeitar. Medido em campo em 12/09/2026.
#
# O QUE ESTE SCRIPT FAZ
#   backup datado -> troca o arquivo -> confere md5 -> diz o que fazer em seguida.
#   NAO reinicia o servidor. NAO mexe em mais nada.
#
# USO
#   bash instalar-icones-mixologia.sh --seco        mostra o plano, nao toca em nada
#   bash instalar-icones-mixologia.sh               instala
#   bash instalar-icones-mixologia.sh --desfazer    volta o original
#
# ORDEM CERTA
#   1. servidor PARADO (e asset de cliente; trocar com gente conectada nao tem efeito
#      para quem ja baixou, e pode deixar metade dos jogadores com cada versao)
#   2. este script
#   3. subir o servidor
#   4. ENTRAR NO JOGO e olhar uma placa -- compilar nao e funcionar, e aqui nem ha
#      compilacao: o unico teste que vale e o olho.

set -u

ALVO="/opt/eco/server/Mods/UserCode/Mixology 14.0.3/Mixology/Unity/MixologyMod.unity3d"
FONTE="/home/eco/MixologyMod.unity3d.novo"
BKDIR="/opt/eco/backups"
MD5_ORIGINAL="1b549c38fb591411e96b7bb331a399d1"
MD5_NOVO="b0cf7c1326caafd2dd70288789665a33"

SECO=0; DESFAZER=0
for a in "$@"; do
    [ "$a" = "--seco" ] && SECO=1
    [ "$a" = "--desfazer" ] && DESFAZER=1
done

diz() { echo "$*"; }
md5() { sudo -u ecosrv md5sum "$1" 2>/dev/null | cut -d' ' -f1; }

diz "=== icones da Mixologia"
diz "    alvo : $ALVO"

if ! sudo -u ecosrv test -f "$ALVO"; then
    diz "[XX] nao achei o arquivo do mod. A Mixologia esta instalada?"
    exit 1
fi

ATUAL=$(md5 "$ALVO")
diz "    md5 atual : $ATUAL"
if [ "$ATUAL" = "$MD5_ORIGINAL" ]; then diz "                (e o ORIGINAL do autor)"
elif [ "$ATUAL" = "$MD5_NOVO" ];   then diz "                (ja e o NOSSO recortado)"
else diz "                (NAO RECONHECIDO -- o mod pode ter sido atualizado; ver o README)"; fi

# ---------------------------------------------------------------- desfazer
if [ "$DESFAZER" = "1" ]; then
    ULTIMO=$(sudo -u ecosrv ls -1t "$BKDIR"/MixologyMod.unity3d.original-* 2>/dev/null | head -1)
    if [ -z "$ULTIMO" ]; then diz "[XX] nao ha backup em $BKDIR"; exit 1; fi
    diz "    voltando de : $ULTIMO"
    if [ "$SECO" = "1" ]; then diz "    (seco: nada foi feito)"; exit 0; fi
    sudo -u ecosrv cp "$ULTIMO" "$ALVO" || { diz "[XX] falhou a copia"; exit 1; }
    diz "    md5 depois : $(md5 "$ALVO")"
    diz "[OK] original de volta. Reinicie o servidor."
    exit 0
fi

# ---------------------------------------------------------------- instalar
if [ ! -f "$FONTE" ]; then
    diz "[XX] nao achei $FONTE"
    diz "     envie antes:  .\\eco-conectar.ps1 -Scp \"mixologia-icones\\MixologyMod.unity3d.novo\""
    exit 1
fi
FMD5=$(md5sum "$FONTE" | cut -d' ' -f1)
diz "    fonte md5 : $FMD5"
if [ "$FMD5" != "$MD5_NOVO" ]; then
    diz "[XX] o arquivo enviado nao e o que este script conhece."
    diz "     esperado $MD5_NOVO"
    diz "     Se voce REGEROU o pacote, atualize MD5_NOVO no topo deste script."
    exit 1
fi

if [ "$(sudo -n systemctl is-active eco-server)" = "active" ]; then
    diz "[!!] o servidor esta NO AR. E asset de cliente: pare antes, senao os jogadores"
    diz "     ficam com versoes diferentes conforme a hora em que entraram."
    [ "$SECO" = "0" ] && { diz "     abortando."; exit 1; }
fi

if [ "$SECO" = "1" ]; then
    diz "    (seco) faria: backup em $BKDIR e troca do arquivo"
    exit 0
fi

sudo -u ecosrv mkdir -p "$BKDIR"
BK="$BKDIR/MixologyMod.unity3d.original-$(date +%Y-%m-%d_%H%M)"
sudo -u ecosrv cp "$ALVO" "$BK" || { diz "[XX] falhou o backup -- nao troquei nada"; exit 1; }
diz "    backup : $BK"

sudo -u ecosrv cp "$FONTE" "$ALVO" || { diz "[XX] falhou a troca"; exit 1; }
DEPOIS=$(md5 "$ALVO")
diz "    md5 depois : $DEPOIS"
if [ "$DEPOIS" != "$MD5_NOVO" ]; then
    diz "[XX] o md5 nao bateu depois da copia. Desfazendo."
    sudo -u ecosrv cp "$BK" "$ALVO"
    exit 1
fi

diz "[OK] trocado."
diz "     Agora: suba o servidor e ENTRE NO JOGO para olhar uma placa."
diz "     O cliente pode ter o pacote velho em cache -- se o quadrado continuar,"
diz "     e cache, nao o arquivo. Ver o README."
