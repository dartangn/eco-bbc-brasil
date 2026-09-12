#!/usr/bin/env python3
"""adicionar-admin.py -- grava os admins no Users.eco do servidor Linux.

    python3 adicionar-admin.py --seco
    python3 adicionar-admin.py
    python3 adicionar-admin.py --id 7656119xxxxxxxxxx --id 7656119yyyyyyyyyy

O SERVIDOR TEM DE ESTAR PARADO. O Eco REGRAVA os Configs ao desligar, entao editar
com ele no ar faz a mudanca desaparecer. Quem chama este script cuida disso.

FAZ UNIAO, NUNCA SOBRESCREVE. Se um admin ja existe no arquivo e nao esta na lista
passada, ele PERMANECE -- e o script avisa. Sobrescrever lista de admin por engano
tiraria o poder de alguem sem ninguem notar.

A VALIDACAO NAO E ENFEITE -- ela pegou um erro real neste projeto: o primeiro numero
que nos passaram para um admin era um ID do DISCORD, nao da Steam. O Eco teria aceitado
o texto sem reclamar e a pessoa nao teria poder nenhum: falha silenciosa. Steam64 tem
17 digitos e comeca com 7656119.

OS IDs NAO FICAM AQUI. Este repositorio e publico, entao a lista vem vazia e cada
servidor poe os seus -- em PADRAO, abaixo, ou por --id na linha de comando. Sem nenhum
dos dois o script nao tem o que gravar e avisa.
"""

import json
import shutil
import sys
import datetime

ARQ = "/opt/eco/server/Configs/Users.eco"

# Os admins do SEU servidor. Steam64 tem 17 digitos e comeca com 7656119.
# Cada jogador ve o proprio numero em steamcommunity.com, ou no jogo com /manage listusers.
PADRAO = [
    # ("7656119xxxxxxxxxx", "nome de quem e"),
]


def valida(sid):
    """Devolve None se ok, ou o motivo da recusa."""
    if not sid.isdigit():
        return "nao e so digito"
    if len(sid) != 17:
        return "tem %d digitos, Steam64 tem 17" % len(sid)
    if not sid.startswith("7656119"):
        return "nao comeca com 7656119 -- pode ser ID de Discord"
    return None


def main():
    argv = sys.argv[1:]
    seco = "--seco" in argv
    ids = []
    i = 0
    while i < len(argv):
        if argv[i] == "--id":
            i += 1
            ids.append((argv[i], "passado na linha de comando"))
        i += 1
    if not ids:
        ids = PADRAO
    if not ids:
        sys.exit("[XX] nenhum admin informado. Ponha os Steam64 em PADRAO, no topo deste"
                 " arquivo, ou passe --id 7656119xxxxxxxxxx. Nada foi tocado.")

    print("############ ADMINS DO ECO ############")
    print("arquivo: %s" % ARQ)
    print("modo   : %s" % ("SECO -- nada sera gravado" if seco else "APLICAR"))
    print("")

    print("=== 1. validando o formato ANTES de tocar no arquivo ===")
    bons = []
    for sid, quem in ids:
        erro = valida(sid)
        if erro:
            print("   [XX] %-20s %-28s %s" % (sid, quem, erro))
        else:
            print("   [ok] %-20s %s" % (sid, quem))
            bons.append(sid)
    if len(bons) != len(ids):
        sys.exit("\n[XX] algum ID nao passou -- ABORTANDO sem tocar no arquivo")
    print("")

    with open(ARQ, "r", encoding="utf-8") as f:
        dados = json.load(f)

    try:
        colecao = dados["UserPermission"]["Admins"]["Collection"]["System.String"]
        atuais = colecao["$values"]
    except (KeyError, TypeError):
        sys.exit(
            "[XX] estrutura de UserPermission.Admins nao e a esperada.\n"
            "     A versao do Eco pode ter mudado o formato -- conferir a mao."
        )

    print("=== 2. quem ja esta no arquivo ===")
    if atuais:
        for a in atuais:
            print("   %s" % a)
    else:
        print("   (nenhum)")
    print("")

    # Uniao preservando a ordem: primeiro os que ja estavam, depois os novos.
    final = list(atuais)
    novos = []
    for sid in bons:
        if sid not in final:
            final.append(sid)
            novos.append(sid)

    sumiu = [a for a in atuais if a not in final]
    if sumiu:
        sys.exit("[XX] a uniao perderia %s -- defeito de logica, ABORTANDO" % sumiu)

    print("=== 3. resultado ===")
    print("   ja estavam    : %d" % len(atuais))
    print("   acrescentados : %d  %s" % (len(novos), novos if novos else ""))
    print("   total final   : %d" % len(final))
    for a in final:
        marca = "  <- novo" if a in novos else ""
        print("      %s%s" % (a, marca))

    if not novos:
        print("")
        print("############ NADA A FAZER -- os admins ja estavam todos la ############")
        return

    if seco:
        print("")
        print("############ MODO SECO -- nada foi gravado ############")
        return

    selo = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    bkp = "%s.antes-admin-%s" % (ARQ, selo)
    shutil.copy2(ARQ, bkp)
    print("")
    print("backup: %s" % bkp)

    colecao["$values"] = final
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    # Conferir RELENDO DO DISCO. Afirmar sem reler ja enganou neste projeto.
    with open(ARQ, "r", encoding="utf-8") as f:
        conf = json.load(f)
    lidos = conf["UserPermission"]["Admins"]["Collection"]["System.String"]["$values"]
    print("relido do disco: %d admins  %s" % (len(lidos), lidos))
    if sorted(lidos) != sorted(final):
        sys.exit("[XX] o que foi relido nao bate -- restaurar %s" % bkp)

    print("")
    print("############ APLICADO ############")
    print("So vale depois de SUBIR o servidor. Conferir no jogo: /manage listadmins")


if __name__ == "__main__":
    main()
