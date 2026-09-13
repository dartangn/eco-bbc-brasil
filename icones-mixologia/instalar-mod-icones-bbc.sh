#!/bin/bash
# Instala o NOSSO mod de icones: IconesMixologiaBBC.unity3d
#
# O QUE E
#   Um mod SO DE ASSET -- um unico .unity3d, zero C#. Ele acrescenta 71 icones com
#   os nomes terminados em BBC (PinaColadaItemBBC, ...), recortados, com canal alfa.
#   O mod original da Mixologia NAO e tocado.
#
# POR QUE ASSIM, e nao substituindo o arquivo do autor
#   Substituir morre na proxima atualizacao da Mixologia. Este pacote e nosso, fica
#   na nossa pasta, e as placas apontam para os nossos nomes.
#
# POR QUE NAO TEM C#
#   Mod nosso que referencia TIPO de outro mod derruba o servidor quando aquele mod
#   nao esta instalado -- e a armadilha do PergaminhosDosMods.cs. Sem C#, esse risco
#   nao existe: se a Mixologia sair, os icones continuam funcionando.
#
# O QUE AINDA NAO FOI PROVADO
#   Que o cliente acha icone por nome de prefab em bundle de OUTRO mod. E o teste:
#   por <icon name="PinaColadaItemBBC" type="nobg"> numa placa e olhar.
#
# USO
#   bash instalar-mod-icones-bbc.sh --seco
#   bash instalar-mod-icones-bbc.sh
#   bash instalar-mod-icones-bbc.sh --desfazer

set -u

DESTDIR="/opt/eco/server/Mods/UserCode/KabongBrasil/IconesBBC"
ALVO="$DESTDIR/IconesMixologiaBBC.unity3d"
FONTE="/home/eco/IconesMixologiaBBC.unity3d"
MD5_NOVO="270ed583507f6c347ec2b82838b56102"

SECO=0; DESFAZER=0
for a in "$@"; do
    [ "$a" = "--seco" ] && SECO=1
    [ "$a" = "--desfazer" ] && DESFAZER=1
done
diz() { echo "$*"; }

diz "=== mod de icones BBC"
diz "    destino : $ALVO"

if [ "$DESFAZER" = "1" ]; then
    if ! sudo -u ecosrv test -d "$DESTDIR"; then diz "[..] nada instalado."; exit 0; fi
    if [ "$SECO" = "1" ]; then diz "    (seco) apagaria $DESTDIR"; exit 0; fi
    sudo -u ecosrv rm -rf "$DESTDIR"
    diz "[OK] removido. Reinicie o servidor."
    diz "     Lembre de DESMARCAR 'icones BBC' na galeria de placas,"
    diz "     senao as placas continuam pedindo nomes que nao existem mais."
    exit 0
fi

if [ ! -f "$FONTE" ]; then
    diz "[XX] nao achei $FONTE"
    diz "     envie antes: .\\eco-conectar.ps1 -Scp \"mixologia-icones\\IconesMixologiaBBC.unity3d\""
    exit 1
fi
FMD5=$(md5sum "$FONTE" | cut -d' ' -f1)
diz "    fonte md5 : $FMD5"
if [ "$MD5_NOVO" != "__MD5__" ] && [ "$FMD5" != "$MD5_NOVO" ]; then
    diz "[XX] o arquivo enviado nao e o que este script conhece (esperado $MD5_NOVO)."
    exit 1
fi

if [ "$(sudo -n systemctl is-active eco-server)" = "active" ]; then
    diz "[!!] servidor NO AR. E asset de cliente: pare antes."
    [ "$SECO" = "0" ] && { diz "     abortando."; exit 1; }
fi

if [ "$SECO" = "1" ]; then
    diz "    (seco) criaria $DESTDIR e copiaria o pacote"
    exit 0
fi

sudo -u ecosrv mkdir -p "$DESTDIR" || { diz "[XX] nao consegui criar a pasta"; exit 1; }
sudo -u ecosrv cp "$FONTE" "$ALVO" || { diz "[XX] falhou a copia"; exit 1; }
DEPOIS=$(sudo -u ecosrv md5sum "$ALVO" | cut -d' ' -f1)
diz "    md5 no destino : $DEPOIS"
[ "$DEPOIS" != "$FMD5" ] && { diz "[XX] md5 nao bateu. Desfazendo."; sudo -u ecosrv rm -rf "$DESTDIR"; exit 1; }

diz "[OK] instalado. Nao ha C# aqui, entao NAO ha o que compilar e nada pode"
diz "     derrubar o arranque por causa deste mod."
diz "     Suba o servidor e teste numa placa:"
diz "       <icon name=\"PinaColadaItemBBC\" type=\"nobg\"></icon>"
diz "     Se NAO aparecer, o cliente nao indexa prefab de bundle de outro mod --"
diz "     e o caminho volta a ser instalar-icones-mixologia.sh, que substitui o"
diz "     arquivo do autor. Os dois estao prontos; um teste decide."
