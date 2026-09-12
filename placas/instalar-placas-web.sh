#!/usr/bin/env bash
# Recoloca a galeria de icones (montador de placa) no painel web do Eco:
#     http://ENDERECO-DO-SERVIDOR:27041/placas/
# O painel serve arquivos estaticos de /opt/eco/server/WebClient/WebBin, e uma atualizacao do Eco
# pode substituir essa pasta. A copia-mestra fica em /opt/eco/placas-web (index.html + png/), fora do jogo.
# Roda como usuario `eco` (usa sudo -u ecosrv). Nao precisa reiniciar o servidor: e arquivo estatico.
#   bash instalar-placas-web.sh          # copia e confere com curl
set -u
M=/opt/eco/placas-web
D=/opt/eco/server/WebClient/WebBin/placas
run() { sudo -u ecosrv bash -c "$1"; }
run "test -f '$M/index.html' && test -d '$M/png'" || { echo "[XX] copia-mestra $M incompleta"; exit 1; }
run "rm -rf '$D' && cp -r '$M' '$D'" || { echo "[XX] copia falhou"; exit 1; }
n=$(run "ls -1 '$D/png' | wc -l")
code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:27041/placas/)
echo "[ok] $n icones em $D; http://localhost:27041/placas/ -> HTTP $code"
[ "$code" = "200" ] || echo "[!!] o painel nao respondeu 200; o servidor esta no ar?"
