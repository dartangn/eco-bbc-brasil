#!/usr/bin/env python3
"""fechar-rcon.py -- poe senha no RCON do Eco, que estava escutando SEM senha.

    python3 fechar-rcon.py --seco
    python3 fechar-rcon.py

O QUE ESTAVA ERRADO (achado em 03/09/2026 numa varredura do servidor)
    Network.eco:  RconServerPort 3002 | RconIPAddress "Any" | RconPassword ""
    E o socket:   LISTEN 0.0.0.0:3002
    E o log:      Starting RconPlugin ... Finished

    O plugin de RCON subiu e esta escutando em TODAS as interfaces com o campo de
    senha vazio. O binario diz que ele "follows the Source RCON standard", e nesse
    padrao a senha e o unico controle de acesso.

    NAO ha regra de NAT para a 3002 no roteador, entao isto NAO vem da internet. Mas
    vem de toda a rede local, que hospeda outros servidores de jogo e equipamento do dono.
    O risco e movimento lateral dentro da rede.

POR QUE SENHA E NAO TROCAR O RconIPAddress
    Trocar "Any" por "127.0.0.1" seria mais limpo, mas "Any" provavelmente vira
    IPAddress.Any no parser, e nao ha documentacao de que ele aceite IP literal. Se
    recusar, o servidor NAO SOBE -- e descobrir isso custa um ciclo de 7 minutos.
    O campo de senha e string livre: risco zero de parser, e resolve o acesso.

    Nao usamos RCON para nada. A senha existe so para fechar a porta.

A SENHA E GERADA AQUI, NO SERVIDOR, e nunca passa pelo chat nem por log.
Ela fica no proprio Network.eco (640, dono ecosrv) e uma copia em /opt/eco/rcon-senha.txt
(600, dono ecosrv) para o Raul consultar se algum dia quiser usar RCON.

O SERVIDOR TEM DE ESTAR PARADO: o Eco REGRAVA os Configs ao desligar.
"""

import json
import os
import secrets
import shutil
import string
import sys
import datetime

ARQ = "/opt/eco/server/Configs/Network.eco"
COPIA = "/opt/eco/rcon-senha.txt"


def main():
    seco = "--seco" in sys.argv

    print("############ FECHAR O RCON ############")
    print("arquivo: %s" % ARQ)
    print("modo   : %s" % ("SECO -- nada sera gravado" if seco else "APLICAR"))
    print("")

    with open(ARQ, "r", encoding="utf-8") as f:
        d = json.load(f)

    print("=== antes ===")
    for k in ("RconServerPort", "RconIPAddress", "RconPassword"):
        v = d.get(k, "<ausente>")
        mostra = "(vazio)" if v == "" else ("(definida, %d chars)" % len(v)
                                            if k == "RconPassword" else v)
        print("   %-18s %s" % (k, mostra))
    print("")

    if d.get("RconPassword"):
        print("############ JA TEM SENHA -- nada a fazer ############")
        return

    # 40 chars sem ambiguidade visual; secrets, nao random
    alfabeto = string.ascii_letters + string.digits
    senha = "".join(secrets.choice(alfabeto) for _ in range(40))

    print("=== o que muda ===")
    print("   RconPassword: (vazio)  ->  senha aleatoria de 40 caracteres")
    print("   nada mais e tocado -- porta e RconIPAddress ficam como estao")
    print("")

    if seco:
        print("############ MODO SECO -- nada foi gravado ############")
        return

    selo = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    bkp = "%s.antes-rcon-%s" % (ARQ, selo)
    shutil.copy2(ARQ, bkp)
    print("backup: %s" % bkp)

    d["RconPassword"] = senha
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    # copia legivel so pelo ecosrv, para o Raul consultar se um dia usar RCON
    with open(COPIA, "w", encoding="utf-8") as f:
        f.write("Senha do RCON do Eco, gerada em %s\n" % selo)
        f.write("Porta 3002. Nao usamos RCON; a senha existe para fechar a porta.\n\n")
        f.write(senha + "\n")
    os.chmod(COPIA, 0o600)

    # conferir RELENDO DO DISCO -- nunca afirmar sem reler
    with open(ARQ, "r", encoding="utf-8") as f:
        conf = json.load(f)
    ok = conf.get("RconPassword") == senha
    campos_antes = len(d)
    print("")
    print("=== relido do disco ===")
    print("   RconPassword definida: %s (%d chars)" % (ok, len(conf.get("RconPassword", ""))))
    print("   RconServerPort       : %s" % conf.get("RconServerPort"))
    print("   RconIPAddress        : %s" % conf.get("RconIPAddress"))
    print("   campos no arquivo    : %d  (esperado %d)" % (len(conf), campos_antes))
    print("   copia da senha       : %s (%s)" % (COPIA, oct(os.stat(COPIA).st_mode)[-3:]))

    if not ok or len(conf) != campos_antes:
        sys.exit("[XX] nao bateu -- restaurar %s" % bkp)

    print("")
    print("############ APLICADO ############")
    print("So vale depois de SUBIR o servidor -- o Eco le os Configs no arranque.")


if __name__ == "__main__":
    main()
