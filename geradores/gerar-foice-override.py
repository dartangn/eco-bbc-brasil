#!/usr/bin/env python3
"""gerar-foice-override.py -- gera o BlockHarvestItem.override.cs a partir do arquivo do JOGO.
    python3 gerar-foice-override.py --seco     # gera em /opt/eco/diag-foice, nao instala
    python3 gerar-foice-override.py            # gera e instala (vale no proximo reinicio)

O QUE FAZ (07/09/2026, pedido do Raul: "foice para cortar fibra com o E").
    BlockHarvestItem.cs e a classe-mae da FOICE (SickleItem) e da GADANHA (ScytheItem): 24 linhas
    e um unico metodo, Reap(), disparado por LeftClick com animacao. Este gerador copia o arquivo
    do jogo INTEIRO e acrescenta, entre marcadores >>> KABONG E / <<< KABONG E, uma copia do Reap()
    chamada ColherComE, com gatilho InteractKey (tecla E), canHoldToTrigger (segurar a tecla) e
    animationDriven false (sem esperar animacao = rapido). Mesmo desenho do CavarComE da pa.
    O nome do metodo vira o texto do prompt no cliente: "Colher Com E".

TRAVAS (copiadas dos outros geradores):
    1. a ancora (atributo do Reap) tem de aparecer exatamente 1 vez;
    2. o cabecalho so tem comentario;
    3. relendo do disco: fora do bloco marcado o corpo e IDENTICO ao original (0 linhas diferentes).
    TriBool vive em Eco.Shared.Items (lido do binario), e este arquivo do jogo NAO tem esse using
    -- por isso o nome vai totalmente qualificado. Encoding casa com o original (BOM, CRLF).
"""
import argparse
import hashlib
import os
import sys

ORIGEM = "/opt/eco/server/Mods/__core__/Tools/BlockHarvestItem.cs"
DESTINO = "/opt/eco/server/Mods/UserCode/Tools/BlockHarvestItem.override.cs"
DIAG = "/opt/eco/diag-foice/BlockHarvestItem.override.cs"
ANCORA = "[Interaction(InteractionTrigger.LeftClick, tags:BlockTags.Reapable"
NOVO_ATRIBUTO = ("        [Interaction(InteractionTrigger.InteractKey, tags:BlockTags.Reapable, "
                 "canHoldToTrigger: Eco.Shared.Items.TriBool.True, animationDriven: false)]")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seco", action="store_true")
    a = p.parse_args()

    print("############ GERAR BlockHarvestItem.override.cs (foice e gadanha com E) ############")
    print("origem: %s" % ORIGEM)
    print("modo  : %s" % ("SECO -- nao instala" if a.seco else "INSTALAR"))

    print("=== 1. conferindo o arquivo do jogo ===")
    if not os.path.isfile(ORIGEM):
        sys.exit("[XX] nao achei %s" % ORIGEM)
    with open(ORIGEM, "rb") as f:
        cru = f.read()
    tem_bom = cru.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in cru
    nl = "\r\n" if crlf else "\n"
    linhas = cru.decode("utf-8-sig").split(nl)
    fim_nl = linhas and linhas[-1] == ""
    if fim_nl:
        linhas = linhas[:-1]
    orig = list(linhas)
    n_orig = len(orig)
    print("  %d linhas   MD5 %s   BOM %s   %s" % (n_orig, hashlib.md5(cru).hexdigest(),
                                                 "sim" if tem_bom else "nao", "CRLF" if crlf else "LF"))
    anc = [i for i, l in enumerate(linhas) if ANCORA in l]
    if len(anc) != 1:
        sys.exit("[XX] a ancora apareceu %d vez(es), esperado 1 -- o arquivo do jogo mudou" % len(anc))
    i_anc = anc[0]
    if "public bool Reap(" not in linhas[i_anc + 1]:
        sys.exit("[XX] esperava 'public bool Reap(' logo apos a ancora (linha %d)" % (i_anc + 2))
    j = i_anc + 1
    while j < len(linhas) and linhas[j] != "        }":
        j += 1
    if j >= len(linhas):
        sys.exit("[XX] nao achei o fim do Reap()")
    reap = linhas[i_anc:j + 1]
    if sum(1 for l in reap if "public bool Reap(" in l) != 1:
        sys.exit("[XX] o trecho copiado nao tem exatamente um 'public bool Reap('")
    print("  ancora na linha %d; Reap() vai da %d a %d (%d linhas)" % (i_anc + 1, i_anc + 1, j + 1, len(reap)))

    print("=== 2. montando ===")
    copia = []
    for l in reap:
        if ANCORA in l:
            copia.append(NOVO_ATRIBUTO)
        elif "public bool Reap(" in l:
            copia.append(l.replace("public bool Reap(", "public bool ColherComE("))
        else:
            copia.append(l)
    bloco_e = [
        "",
        "        // >>> KABONG E: colher (fibra, plantas) com a tecla E, segurando, sem animacao.",
        "        // Copia fiel do Reap() acima com dois trocados: o gatilho (InteractKey, canHold,",
        "        // animationDriven false) e o nome -- que vira o texto do prompt no cliente.",
        "        // Mesmo desenho do CavarComE do ShovelItem.override.cs. Vale para foice e gadanha,",
        "        // porque as duas herdam desta classe sem codigo proprio.",
    ] + copia + [
        "        // <<< KABONG E",
    ]
    linhas = linhas[:j + 1] + bloco_e + linhas[j + 1:]
    print("  bloco E: %d linhas, depois da linha %d" % (len(bloco_e), j + 1))

    cab = [
        "// ============================================================================",
        "// BlockHarvestItem.override.cs  --  GERADO por gerar-foice-override.py",
        "// Servidor Kabong Brasil",
        "//",
        "// NAO EDITE A MAO. Copia do BlockHarvestItem.cs do jogo (classe-mae da foice e",
        "// da gadanha) com UMA adicao, marcada >>> KABONG E: o metodo ColherComE, copia",
        "// do Reap() com gatilho na tecla E, segurando, sem animacao.",
        "//",
        "// Depois de ATUALIZAR O ECO, rode o gerador de novo. Para reverter: apague.",
        "// ============================================================================",
        "",
    ]
    for i, e in enumerate(cab):
        if not isinstance(e, str) or (e.strip() and not e.strip().startswith("//")):
            sys.exit("[XX] cabecalho, elemento %d nao e comentario nem vazio" % (i + 1))
    print("  TRAVA 1: cabecalho, %d elementos, todos comentario ou vazio  [ok]" % len(cab))

    destino = DIAG if a.seco else DESTINO
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "wb") as f:
        if tem_bom:
            f.write(b"\xef\xbb\xbf")
        f.write((nl.join(cab + linhas) + (nl if fim_nl else "")).encode("utf-8"))
    print("=== 3. gravado: %s (%d bytes) ===" % (destino, os.path.getsize(destino)))

    with open(destino, "rb") as f:
        conf = f.read().decode("utf-8-sig").split(nl)
    if conf and conf[-1] == "":
        conf = conf[:-1]
    if len(conf) != len(cab) + n_orig + len(bloco_e):
        sys.exit("[XX] contagem de linhas: %d, esperado %d" % (len(conf), len(cab) + n_orig + len(bloco_e)))
    corpo = conf[len(cab):]
    dentro, regioes, sem_bloco = False, 0, []
    for l in corpo:
        if not dentro and ">>> KABONG" in l:
            dentro, regioes = True, regioes + 1
            continue
        if dentro:
            if "<<< KABONG" in l:
                dentro = False
            continue
        sem_bloco.append(l)
    if dentro or regioes != 1:
        sys.exit("[XX] marcadores: %d regiao(oes), dentro=%s" % (regioes, dentro))
    # a linha vazia que abre o bloco fica FORA dos marcadores: descontar
    if len(sem_bloco) == n_orig + 1 and sem_bloco[j + 1] == "":
        del sem_bloco[j + 1]
    if len(sem_bloco) != n_orig:
        sys.exit("[XX] sem o bloco sobraram %d linhas, esperado %d" % (len(sem_bloco), n_orig))
    difs = [i + 1 for i in range(n_orig) if sem_bloco[i] != orig[i]]
    if difs:
        sys.exit("[XX] fora do bloco o corpo difere nas linhas %s; esperado 0" % difs[:5])
    print("  TRAVA 2: 1 regiao marcada, corpo IDENTICO ao original fora dela  [ok]")
    chaves = sum(l.count("{") for l in bloco_e if not l.strip().startswith("//")) - \
             sum(l.count("}") for l in bloco_e if not l.strip().startswith("//"))
    if chaves != 0:
        sys.exit("[XX] chaves desbalanceadas no bloco: %d" % chaves)
    print("  TRAVA 3: chaves do bloco balanceadas  [ok]")

    if a.seco:
        print("=== MODO SECO CONCLUIDO -- nada instalado. Rode sem --seco para instalar. ===")
        return
    print("############ INSTALADO -- compila no proximo reinicio ############")
    print("Prova de que o override substituiu o arquivo do jogo: compilar sem CS0101.")
    print("Conferir no jogo: mirar fibra/planta com a foice; deve aparecer 'Colher Com E'.")


if __name__ == "__main__":
    main()
