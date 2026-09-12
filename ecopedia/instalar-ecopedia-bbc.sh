#!/usr/bin/env bash
# Instala as paginas da Ecopedia do BBC-Brasil: capitulo "Mods" (paginas BBC-Brasil;* + traducao EcoPulse)
# e capitulo proprio "Parâmetros do servidor". Sao XML (nao compilam); valem no proximo reinicio.
# Roda como usuario `eco` (usa sudo -u ecosrv).
#   bash instalar-ecopedia-bbc.sh --seco      # mostra o que faria
#   bash instalar-ecopedia-bbc.sh             # instala (com backup do que estava)
#   bash instalar-ecopedia-bbc.sh --desfazer  # volta o backup mais recente
set -u
ORIGEM=/opt/eco/mods-desativados/Ecopedia-BBC        # espelha Mods/UserCode/Ecopedia
DESTINO=/opt/eco/server/Mods/UserCode/Ecopedia
BACKUPS=/opt/eco/backups
CAP="Parametros do Servidor"
MODO=${1:-}
run() { sudo -u ecosrv bash -c "$1"; }

n=$(run "ls -1 '$ORIGEM'/*/*.xml 2>/dev/null | wc -l")
[ "$n" -lt 25 ] && { echo "[XX] origem $ORIGEM tem $n xml (esperado ~32). Nada feito."; exit 1; }
run "python3 -c \"import glob,xml.etree.ElementTree as E;[E.parse(f) for f in glob.glob('$ORIGEM/*/*.xml')]\"" \
  || { echo "[XX] algum XML da origem nao parseia. Nada feito."; exit 1; }
echo "[ok] origem: $n xml em $(run "ls -1 '$ORIGEM'" | tr '\n' ' '), todos parseiam"

if [ "$MODO" = "--desfazer" ]; then
  ult=$(run "ls -1d '$BACKUPS'/Ecopedia-* 2>/dev/null | tail -1")
  [ -z "$ult" ] && { echo "[XX] nenhum backup Ecopedia-* em $BACKUPS"; exit 1; }
  echo "voltando $ult -> $DESTINO (apaga o que esta la e recoloca o backup)"
  run "rm -rf '$DESTINO' && cp -r '$ult' '$DESTINO' && ls -R '$DESTINO'"
  echo "[ok] desfeito. Reinicie para valer."; exit 0
fi

echo "destino atual:"; run "ls -R '$DESTINO'"
if [ "$MODO" = "--seco" ]; then
  echo "[seco] copiaria $ORIGEM/Mods/*.xml -> $DESTINO/Mods/ e $ORIGEM/$CAP/*.xml -> $DESTINO/$CAP/, removendo paginas BBC-Brasil;* que nao existem mais na origem; backup em $BACKUPS/Ecopedia-<data>"; exit 0
fi

data=$(date +%Y-%m-%d_%H%M)
run "cp -r '$DESTINO' '$BACKUPS/Ecopedia-$data'" || { echo "[XX] backup falhou. Nada feito."; exit 1; }
echo "[ok] backup em $BACKUPS/Ecopedia-$data"
# paginas nossas que sairam da origem nao podem sobrar no destino
run "cd '$DESTINO/Mods' && for f in BBC-Brasil*.xml; do [ -f '$ORIGEM/Mods/'\"\$f\" ] || { echo \"  removendo obsoleta: \$f\"; rm -f \"\$f\"; }; done"
# idem no capitulo dos parametros: em 10/09 os arquivos mudaram de nome (viraram "Categoria;Pagina.xml") e
# um .xml antigo que sobre ali fica no menu como CATEGORIA VAZIA -- foi esse o defeito do capitulo vazio
run "test -d '$DESTINO/$CAP' && cd '$DESTINO/$CAP' && for f in *.xml; do [ -f '$ORIGEM/$CAP/'\"\$f\" ] || { echo \"  removendo obsoleta: $CAP/\$f\"; rm -f \"\$f\"; }; done"
run "cp '$ORIGEM'/Mods/*.xml '$DESTINO/Mods/' && mkdir -p '$DESTINO/$CAP' && cp '$ORIGEM/$CAP'/*.xml '$DESTINO/$CAP/'" \
  || { echo "[XX] copia falhou"; exit 1; }
echo "[ok] instalado:"; run "ls -R '$DESTINO'"
echo
echo "Vale no proximo reinicio. Depois, no jogo: F1 -> capitulo 'Parâmetros do servidor' e capitulo Mods -> BBC-Brasil."
