#!/usr/bin/env bash
# eco-reiniciar.sh -- reinicio DIARIO do servidor, com aviso, limpeza de entulho e save.
# Roda sozinho, por timer (eco-reiniciar.timer, 03:55 Sao Paulo -> servidor de volta ~04:07).
#
#   bash eco-reiniciar.sh --seco       # mostra o que faria, sem tocar em nada
#   bash eco-reiniciar.sh --so-rcon    # so os passos de RCON (aviso curto, entulho, save); NAO reinicia
#   bash eco-reiniciar.sh --agora      # tudo, sem os 5 min de aviso
#   bash eco-reiniciar.sh              # o que o timer roda
#
# O QUE ELE FAZ, NA ORDEM
#   1. avisa no jogo (/manage announce) 5 min e 1 min antes
#   2. /world clearallrubble  -- "Destroys all rubble in the world" (texto do /help, 07/09/2026)
#   3. /manage save           -- "Save the world!"
#   4. PARA o servico, roda os scripts PENDENTES de config (/opt/eco/pendentes/*.py, como ecosrv:
#      mudanca de .eco so vale editando com o servidor parado, porque o Eco regrava os Configs ao
#      desligar), SOBE, espera a porta web abrir e le o log do arranque. Script que rodou bem vai
#      para /opt/eco/pendentes/feitos/; o que falhou fica onde esta e e avisado no log.
#
# AVISO E ENTULHO VAO PELA PONTE (08/09/2026): "/manage announce" pelo RCON responde vazio e o
# jogador NAO ve nada; "/world clearallrubble" pelo RCON responde "requires a in-game user".
# O mod PonteServidor.cs (UserCode/KabongBrasil) vigia /opt/eco/ponte a cada 5 s:
#   anuncio.txt    -> texto mandado a todos no jogo      limpar-entulho -> RubbleObject.ClearAllRubble
# e registra o que fez em /opt/eco/ponte-vida.txt. O RCON continua so para o /manage save.
#
# POR QUE NAO /manage maintenance
#   Ele "Schedules an automatic shutdown": DESLIGA. O servico e Restart=on-failure, e um
#   desligamento limpo nao e falha -- o servidor ficaria fora do ar. Por isso o restart e nosso.
set -u

MODO=normal
case "${1:-}" in
    --seco)    MODO=seco ;;
    --so-rcon) MODO=sorcon ;;
    --agora)   MODO=agora ;;
esac

SRV=ecosrv
RCON=/opt/eco/scripts-py/rcon.py
LOG=/home/eco/eco-reiniciar.log       # log no home do usuario que roda (eco)
PORTA_WEB=27041
ESPERA=2700                            # ate 45 min pelo arranque

ex()  { sudo -n -u "$SRV" "$@"; }
diz() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*" | tee -a "$LOG"; }
# manda um comando pelo RCON e devolve so a resposta do jogo (sem o cabecalho do rcon.py)
rcon() {
    ex python3 "$RCON" "$1" 2>&1 | grep -v -E '^\[ok\]|^=+$|^>>>|^$' | head -6
}
PONTE=/opt/eco/ponte
PONTE_VIDA=/opt/eco/ponte-vida.txt
# CONFERE SE O MOD DA PONTE ESTA VIVO antes de confiar nela. De 09 a 12/09/2026 este script
# escreveu aviso e pedido de entulho num arquivo que NINGUEM lia -- o PonteServidor.cs nao
# estava instalado -- e o log nao reclamou, porque a unica verificacao lia o diario com
# 2>/dev/null e seguia em frente. Verificacao que nao pode falhar tambem nao pode passar.
ponte_viva() { ex test -f "$PONTE_VIDA" 2>/dev/null; }
# AVISO AO JOGADOR: "/manage alert" pelo RCON -- CAIXA COM OK, que fica na tela ate o jogador
# clicar. PROVADO EM CAMPO em 12/09/2026, 15:50 -04, com 12 jogadores online: o Raul viu a
# caixa e disse "o primeiro aviso de reinicio deveria ser assim".
#
# CORRECAO de um registro meu de 08/09: eu havia anotado que "aviso por RCON nao chega ao
# jogador" e mudei tudo para a ponte por causa disso. Aquilo valia para o "/manage announce"
# (que, mesmo digitado no jogo, pisca rapido demais para ler). O "/manage alert" chega.
# Por isso o aviso NAO depende mais de mod nenhum; a ponte ficou so para o entulho.
anuncia() {
    local r
    r=$(rcon "/manage alert $1")
    diz "   alert por RCON: $1"
    [ -n "$r" ] && diz "   (resposta: $r)"
    return 0
}

diz "================================================================"
diz "REINICIO DIARIO  --  modo: $MODO"
diz "hora da maquina: $(date '+%H:%M %Z')   Sao Paulo: $(TZ=America/Sao_Paulo date '+%H:%M %Z')"
diz "================================================================"

EST=$(sudo -n systemctl is-active eco-server 2>/dev/null)
diz "servico agora: $EST"
JOG=$(curl -s --max-time 10 "http://localhost:$PORTA_WEB/info" 2>/dev/null \
      | python3 -c "import sys,json; print(json.load(sys.stdin).get('OnlinePlayers','?'))" 2>/dev/null)
diz "jogadores online: ${JOG:-?}"

if [ "$MODO" = seco ]; then
    diz ""
    diz "MODO SECO -- faria isto:"
    diz "   1. aviso por RCON (/manage alert, caixa com OK), 5 min e 1 min antes, PT e EN"
    diz "   2. limpar entulho pela ponte (/opt/eco/ponte/limpar-entulho)"
    diz "      ponte viva agora: $(ponte_viva && echo SIM || echo NAO -- entulho NAO sera limpo)"
    diz "   3. /manage save"
    diz "   4. parar, rodar /opt/eco/pendentes/*.py ($(ex sh -c "ls /opt/eco/pendentes/*.py 2>/dev/null" | wc -l) pendente(s)), subir e esperar ate ${ESPERA}s pela porta $PORTA_WEB"
    diz "   rcon.py existe: $(ex test -f "$RCON" && echo sim || echo NAO)"
    diz "MODO SECO -- nada foi alterado."
    exit 0
fi

if ! ponte_viva; then
    diz "[XX] A PONTE NAO ESTA VIVA: nao existe $PONTE_VIDA."
    diz "     O mod PonteServidor.cs nao esta em Mods/UserCode/KabongBrasil, entao ninguem le o"
    diz "     pedido de limpar entulho: o reinicio acontece SEM limpar o entulho."
    diz "     (O AVISO aos jogadores nao depende dele -- vai por RCON /manage alert.)"
    diz "     Conserto: instalar o PonteServidor.cs.corrigido-nao-instalado de"
    diz "     /opt/eco/mods-desativados/KabongBrasil/ com instalar-mod.sh, em reinicio VIGIADO."
fi

if [ "$EST" != active ]; then
    diz "[!!] servico nao esta ativo -- nao ha o que avisar nem limpar. Subindo direto."
    sudo -n systemctl start eco-server
    exit 0
fi

# ---------------------------------------------------------------- 1. avisos
if [ "$MODO" = normal ]; then
    diz "1. aviso de 5 min"
    anuncia "Reinicio diario do servidor em 5 minutos. Guarde o que estiver fazendo.  /  Daily server restart in 5 minutes. Please save your work."
    sleep 240
    diz "   aviso de 1 min"
    anuncia "Reinicio diario em 1 minuto.  /  Daily server restart in 1 minute."
    sleep 60
else
    diz "1. aviso curto (modo $MODO)"
    anuncia "Manutencao rapida do servidor agora. Voltamos em ~8 minutos.  /  Quick server maintenance now. Back in ~8 minutes."
    sleep 10
fi

# ---------------------------------------------------------------- 2. entulho
diz "2. limpar entulho (pela ponte)"
ex touch "$PONTE/limpar-entulho" && sleep 8
# o mod CONSOME o arquivo; se ele continuar la, ninguem leu
if ex test -f "$PONTE/limpar-entulho"; then
    diz "   [XX] o pedido continuou em $PONTE/limpar-entulho -- NINGUEM leu. Entulho NAO foi limpo."
else
    diz "   ponte-vida (fim): $(ex tail -1 "$PONTE_VIDA" 2>/dev/null)"
fi

# ---------------------------------------------------------------- 3. save
diz "3. /manage save"
rcon "/manage save" | sed 's/^/   /' | tee -a "$LOG"
sleep 10

if [ "$MODO" = sorcon ]; then
    diz "modo --so-rcon: NAO reiniciando."
    exit 0
fi

# ---------------------------------------------------------------- 4. reiniciar
diz "4. parando"
sudo -n systemctl stop eco-server
for i in $(seq 1 30); do [ "$(sudo -n systemctl is-active eco-server 2>/dev/null)" != active ] && break; sleep 4; done
diz "   estado: $(sudo -n systemctl is-active eco-server 2>/dev/null)"
PEND=/opt/eco/pendentes
for s in $(ex sh -c "ls $PEND/*.py 2>/dev/null"); do
    diz "   pendente: $(basename "$s")"
    SAIDA=$(ex python3 "$s" 2>&1); RC=$?
    echo "$SAIDA" | sed 's/^/      /' | tee -a "$LOG"
    if [ "$RC" -eq 0 ] && echo "$SAIDA" | grep -q '^\[ok\]'; then
        ex mkdir -p "$PEND/feitos"
        ex mv "$s" "$PEND/feitos/$(basename "$s" .py).$(date +%Y-%m-%d_%H%M).py"
        diz "   -> feito; movido para $PEND/feitos/"
    else
        diz "   [!!] $(basename "$s") falhou (rc=$RC) -- ficou em $PEND para revisao"
    fi
done
diz "   subindo"
T0=$(date '+%Y-%m-%d %H:%M:%S')
sudo -n systemctl start eco-server
t0=$(date +%s)
RES=espera
while :; do
    a=$(( $(date +%s) - t0 ))
    if ss -ltn 2>/dev/null | grep -q ":$PORTA_WEB "; then RES=ok; break; fi
    L=$(sudo -n journalctl -u eco-server --since "$T0" --no-pager 2>/dev/null)
    echo "$L" | grep -q "Failed to start the server" && { RES=naosobe; break; }
    [ "$a" -ge "$ESPERA" ] && { RES=demorou; break; }
    sleep 20
done
diz "   resultado: $RES apos ${a}s"

L=$(sudo -n journalctl -u eco-server --since "$T0" --no-pager 2>/dev/null)
CS=$(echo "$L" | grep -c -E "error CS[0-9]+")
FS=$(echo "$L" | grep -c "Failed to start the server")
diz "   erros de compilacao neste arranque: $CS   Failed to start: $FS"
[ "$CS" -gt 0 ] && echo "$L" | grep -E "error CS[0-9]+" | head -5 | cut -c60-260 | sed 's/^/   /' | tee -a "$LOG"

# ------------------------------------------------- 4b. DESFAZER .cs que reprovou
# A regra do projeto e "nunca instalar .cs novo e deixar para o proximo reinicio", porque foi
# assim que o servidor caiu em 08/09: erro de compilacao, 3 arranques falhos, unidade do systemd
# travada por 30 min, e ninguem olhando. Aqui o risco e desarmado por DESFAZER AUTOMATICO: o
# script pendente anota o que instalou, e se ESTE arranque acusar erro, o arquivo sai e o
# servidor sobe de novo sem ele. O pior caso vira "voltou sem o mod", nao "nao voltou".
LISTA_INST=/opt/eco/pendentes/instalados-neste-reinicio.txt
if { [ "$CS" -gt 0 ] || [ "$RES" = naosobe ]; } && ex test -s "$LISTA_INST" 2>/dev/null; then
    diz "[XX] arranque com problema E houve .cs instalado por pendente -- DESFAZENDO"
    for f in $(ex cat "$LISTA_INST"); do
        ex mv "$f" "/opt/eco/mods-desativados/KabongBrasil/$(basename "$f").reprovado-$(date +%F_%H%M)" \
            && diz "   tirado: $f" || diz "   [!!] nao consegui tirar $f"
    done
    ex rm -f "$LISTA_INST"
    diz "   subindo de novo, agora sem o arquivo reprovado"
    T0=$(date '+%Y-%m-%d %H:%M:%S')
    sudo -n systemctl restart eco-server
    t0=$(date +%s); RES=espera
    while :; do
        a=$(( $(date +%s) - t0 ))
        if ss -ltn 2>/dev/null | grep -q ":$PORTA_WEB "; then RES=ok; break; fi
        sudo -n journalctl -u eco-server --since "$T0" --no-pager 2>/dev/null \
            | grep -q "Failed to start the server" && { RES=naosobe; break; }
        [ "$a" -ge "$ESPERA" ] && { RES=demorou; break; }
        sleep 20
    done
    L=$(sudo -n journalctl -u eco-server --since "$T0" --no-pager 2>/dev/null)
    CS=$(echo "$L" | grep -c -E "error CS[0-9]+")
    diz "   depois de desfazer: $RES apos ${a}s, erros de compilacao: $CS"
fi
ex rm -f "$LISTA_INST" 2>/dev/null

# ------------------------------------------------- 4c. a ponte acordou?
if ex test -f "$PONTE_VIDA" 2>/dev/null; then
    diz "   ponte: VIVA -- $(ex tail -1 "$PONTE_VIDA" 2>/dev/null)"
else
    diz "   ponte: sem $PONTE_VIDA (o entulho nao sera limpo no proximo reinicio)"
fi

if [ "$RES" = ok ]; then
    curl -s --max-time 15 "http://localhost:$PORTA_WEB/info" 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k in ('Version', 'Access', 'OnlinePlayers'):
    if k in d: print('   %-14s %s' % (k, d[k]))
" 2>/dev/null | tee -a "$LOG"
    diz "REINICIO CONCLUIDO"
else
    diz "[XX] o servidor NAO voltou ($RES). Ver: sudo journalctl -u eco-server --since '$T0'"
    diz "     se houver 'error CS', o ultimo override gerado e o suspeito: devolver o backup de /opt/eco/backups/"
    exit 1
fi
diz ""
