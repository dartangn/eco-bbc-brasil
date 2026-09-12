#!/usr/bin/env bash
# instalar-reiniciar.sh -- instala o timer do REINICIO DIARIO (eco-reiniciar).
#
#   sudo bash instalar-reiniciar.sh --seco     # mostra o plano e a proxima hora
#   sudo bash instalar-reiniciar.sh            # instala
#   sudo bash instalar-reiniciar.sh --remover  # tira
#
# PRECISA DE ROOT so para escrever em /etc/systemd/system e /usr/local/bin. O script em si
# roda como 'eco', que ja tem a regra de sudo para systemctl/journalctl do eco-server.
# Mesmo desenho do instalar-agendamentos.sh (03/09): timer do systemd com FUSO no
# OnCalendar, Persistent=false, script em /usr/local/bin, log em /home/eco.
set -u

MODO=instalar
case "${1:-}" in
    --seco)    MODO=seco ;;
    --remover) MODO=remover ;;
esac
if [ "$MODO" != seco ] && [ "$(id -u)" -ne 0 ]; then
    echo "Rodar como root:  sudo bash instalar-reiniciar.sh"; exit 1
fi

ORIGEM=/home/eco
SCRIPTS=/usr/local/bin
UD=/etc/systemd/system
NOME=eco-reiniciar

# ---- AJUSTE AQUI -------------------------------------------------------------
# Hora em SAO PAULO. O script avisa por 5 min antes de reiniciar, e o arranque leva
# ~7 min: disparando 03:55 o servidor cai ~04:00 e volta ~04:07.
HORA="03:55:00"
FUSO="America/Sao_Paulo"
# ------------------------------------------------------------------------------
CAL="*-*-* $HORA $FUSO"

if [ "$MODO" = remover ]; then
    systemctl disable --now "$NOME.timer" 2>/dev/null
    rm -f "$UD/$NOME.timer" "$UD/$NOME.service"
    systemctl daemon-reload
    echo "removido: $NOME"; exit 0
fi

echo "############ REINICIO DIARIO ############"
echo "maquina em: $(timedatectl show -p Timezone --value 2>/dev/null)   agora: $(date '+%Y-%m-%d %H:%M %Z')"
echo "Sao Paulo : $(TZ=America/Sao_Paulo date '+%Y-%m-%d %H:%M %Z')"
echo "agendamento: $CAL"
systemd-analyze calendar "$CAL" 2>&1 | grep -E "Next elapse|Normalized|Failed" | sed 's/^/   /'
echo ""
if [ "$MODO" = seco ]; then
    echo "MODO SECO -- nada foi instalado."; exit 0
fi

# UMA copia so de cada script, em /usr/local/bin (08/09: as copias em ~/bin e /home/eco com o mesmo
# nome confundiam a conferencia). Os icones do desktop apontam para /usr/local/bin.
for s in eco-reiniciar.sh eco-atualizar.sh vigiar-arranque.sh; do
    if [ ! -f "$ORIGEM/$s" ]; then echo "[XX] falta $ORIGEM/$s (scp antes)"; exit 1; fi
    bash -n "$ORIGEM/$s" || { echo "[XX] $s: erro de sintaxe -- ABORTANDO"; exit 1; }
    install -o root -g root -m 755 "$ORIGEM/$s" "$SCRIPTS/$s"
    echo "   $ORIGEM/$s  ->  $SCRIPTS/$s"
done
rm -f /home/eco/bin/eco-reiniciar.sh /home/eco/bin/eco-atualizar.sh /home/eco/bin/vigiar-arranque.sh 2>/dev/null && echo "   copias em /home/eco/bin removidas"
[ -f "/home/eco/$NOME.log" ] || { touch "/home/eco/$NOME.log"; chown eco:eco "/home/eco/$NOME.log"; }

cat > "$UD/$NOME.service" <<SVC
[Unit]
Description=Reinicio diario do servidor Eco (aviso, entulho, save, restart)
After=network-online.target

[Service]
Type=oneshot
User=eco
Group=eco
TimeoutStartSec=0
ExecStart=/usr/bin/env bash $SCRIPTS/$NOME.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$NOME
SVC

cat > "$UD/$NOME.timer" <<TMR
[Unit]
Description=Reinicio diario do servidor Eco (agendamento)

[Timer]
OnCalendar=$CAL
Persistent=false
AccuracySec=1s

[Install]
WantedBy=timers.target
TMR

systemctl daemon-reload
systemctl enable --now "$NOME.timer" >/dev/null 2>&1
echo ""
systemctl list-timers "$NOME*" --all --no-pager 2>/dev/null | sed 's/^/   /'
echo ""
echo "############ PRONTO ############"
echo "Log: /home/eco/$NOME.log   Acompanhar: sudo journalctl -u $NOME -f"
echo "Rodar a mao: bash $SCRIPTS/$NOME.sh --seco   |   --so-rcon   |   --agora"
