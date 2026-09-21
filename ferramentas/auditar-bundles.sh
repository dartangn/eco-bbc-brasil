#!/usr/bin/env bash
# Cada pacote de cliente carrega arquivos internos 'BuildPlayer-<cena>'. Dois pacotes com o
# MESMO nome interno: o Unity recusa o segundo e a ENTRADA DO JOGADOR TRAVA (medido em
# 16/09/2026 no log do cliente). O exemplo oficial da Strange Loop (EcoModKit/Examples/
# EcopediaPage) confirma o padrao: uma cena por mod, com nome proprio.
#
# CORRECAO 21/09/2026 -- a versao anterior deste script era INUTIL, e pior que inutil.
# Ela lia `head -c 8192` de cada pacote, e o nome da cena NAO esta no comeco: no
# Assets_PumpGasMod_English.unity3d ele fica no byte ~4.713.287 de 4.715.472, ou seja no
# FIM. Lendo so 8 KB nenhum pacote produzia linha, `rep` saia vazio, e o script imprimia
# "[ok] nenhum nome de cena interno repetido" -- aprovando sem ter olhado nada. E a
# familia de erro que este projeto ja pagou em 43.2, 50.1, 51.3, 60.5, 65.5 e 67.10:
# VERIFICACAO QUE NAO PODE FALHAR TAMBEM NAO PODE PASSAR.
#
# Duas mudancas: le o arquivo INTEIRO, e ABORTA se algum pacote nao entregar nome --
# porque "nao li" nunca mais pode ser confundido com "nao ha repetido".
export LC_ALL=C

sudo -n -u ecosrv bash -c '
  find /opt/eco/server/Mods -name "*.unity3d" -print0 |
  while IFS= read -r -d "" f; do
    # nome base da cena, sem o sufixo .sharedAssets; arquivo INTEIRO, nao os primeiros 8 KB
    n=$(grep -ao "BuildPlayer-[A-Za-z0-9_ -]*" "$f" | sed "s/\.sharedAssets.*//" | sort -u | head -1)
    printf "%s\t%s\n" "${n:-SEM-NOME}" "$f"
  done' | sort > /tmp/bundles.txt

total=$(wc -l < /tmp/bundles.txt)
semnome=$(grep -c "^SEM-NOME" /tmp/bundles.txt || true)
echo "   pacotes encontrados: $total"

# TRAVA DE SANIDADE -- vem ANTES do veredito
if [ "$total" -eq 0 ]; then
  echo "   [XX] nenhum pacote encontrado. A varredura falhou; NAO concluir nada."
  exit 1
fi
if [ "$semnome" -gt 0 ]; then
  echo "   [XX] $semnome de $total pacotes nao entregaram nome de cena:"
  grep "^SEM-NOME" /tmp/bundles.txt | cut -f2 | sed 's/^/         /'
  echo "   Sem ler todos, 'nenhum repetido' nao significa nada. ABORTEI."
  exit 1
fi
echo "   [ok] todos os $total entregaram nome de cena -- o veredito abaixo vale"

rep=$(cut -f1 /tmp/bundles.txt | sort | uniq -d)
if [ -z "$rep" ]; then
  echo "   [ok] nenhum nome de cena interno repetido"
else
  echo "   [XX] nomes de cena REPETIDOS -- quem entrar VAI TRAVAR no carregamento:"
  for r in $rep; do
    echo "      $r"
    awk -F'\t' -v r="$r" '$1==r {print "         " $2}' /tmp/bundles.txt
  done
  exit 1
fi
