#!/usr/bin/env python3
"""gerar-pedra-override.py -- gera o PickaxeItem.override.cs a partir do arquivo do JOGO.

    python3 gerar-pedra-override.py --seco     # gera em /opt/eco/diag-pedra, nao instala
    python3 gerar-pedra-override.py            # gera e instala
    python3 gerar-pedra-override.py --com-diario

Porte do gerar-pedra-override.ps1 para o servidor Linux, 03/09/2026.
E a PICARETA que e alterada, nao a pa -- a pa entra so como referencia.

A DESCOBERTA QUE RESOLVEU ISSO (CLAUDE.md 21.1)
    ShovelItem.cs:  pack.DeleteBlock(otherContext, player?.User.Inventory);   -> vai para a MAO
    PickaxeItem.cs: pack.DeleteBlock(ctx, spawnRubble: false);  + RubbleObject -> vai para o CHAO

    Passando um INVENTARIO DE DESTINO, o jogo entrega o item; sem ele, cria entulho.
    E como a pa da terra na mao. Logo NAO precisamos inventar quantidade -- quem decide
    continua sendo o jogo. Isso era a incognita central, porque o RubbleObject esta em
    DLL e nao da para ler quanto ele rende.

MEDIDO EM CAMPO: 4 blocos por bloco minerado, exatamente igual ao caminho do entulho.
    A economia de mineracao NAO mudou -- so sumiu o passo de pegar o entulho do chao.

A TRAVA AQUI E A MAIS FORTE POSSIVEL
    Como nao ha troca de constante, o invariante e: fora do bloco marcado, o corpo e
    IDENTICO ao original -- ZERO linhas diferentes. No TreeObject o esperado e 2.
    Vale copiar este formato em todo gerador novo.
"""

import argparse
import hashlib
import os
import re
import sys

ORIGEM = "/opt/eco/server/Mods/__core__/Tools/PickaxeItem.cs"
DESTINO = "/opt/eco/server/Mods/UserCode/Tools/PickaxeItem.override.cs"
DIAG = "/opt/eco/diag-pedra/PickaxeItem.override.cs"

ANCORA = "spawnRubble: false"

RE_DIARIO = re.compile(r"KabongBrasil\.KabongLog\.(?:Tronco|Pedra)\([^;]*\);\s*")

BLOCO = [
    "                        // >>> KABONG PEDRA: manda o bloco direto para a MAO.",
    "                        // Usa a MESMA sobrecarga que a pa usa (ShovelItem.cs),",
    "                        // passando um inventario de destino - assim quem decide a",
    "                        // quantidade continua sendo o jogo, nao nos.",
    "                        // Sem espaco na mao, nao faz nada e o codigo original abaixo",
    "                        // roda normalmente: entulho no chao. O fallback e de graca.",
    "                        {",
    "                            var kabongItem = block is IRepresentsItem ? Item.Get((IRepresentsItem)block) : null;",
    "                            if (kabongItem != null && player.User.Inventory.Carried.RoomFor(kabongItem) > 0)",
    "                            {",
    "                                var kabongPos   = pos;",
    "                                var kabongBloco = block;",
    "                                pack.DeleteBlock(this.CreateMultiblockContext(player, false, pos), player?.User.Inventory);",
    "                                pack.AddPostEffect(() =>",
    "                                {",
    "                                    try",
    "                                    {",
    "                                        // o que o post-effect do entulho fazia e nao e sobre entulho:",
    "                                        // XP de mineracao, limpeza do BlockHitCache e o BlockMinedEvent.",
    "                                        // Fica de fora so o user.UserUI.OnCreateRubble, que avisa a",
    "                                        // interface que nasceu entulho -- e nao nasce nenhum.",
    '                                        this.AddExperience(user, 1f, new LocString(Localizer.Format("mining") + " " + kabongItem.UILink()));',
    "                                        user.BlockHitCache.ForgetHit(target.BlockPosition.Value);",
    "                                        UserEvents.BlockMinedEvent.Invoke(context.Player?.User, (Vector3i)kabongPos, kabongBloco);",
    "",
    '                                        KabongBrasil.KabongLog.Pedra("bloco para a mao: agora tenho " + player.User.Inventory.Carried.Stacks.Where(s => s.Item != null && s.Item.Type == kabongItem.Type).Sum(s => s.Quantity) + " de " + kabongItem.DisplayName);',
    "                                    }",
    '                                    catch (System.Exception kabongEx) { KabongBrasil.KabongLog.Pedra("EXCECAO: " + kabongEx.Message); }',
    "                                });",
    "                                continue;   // pula o caminho do entulho",
    "                            }",
    '                            KabongBrasil.KabongLog.Pedra("sem espaco na mao - vai entulho para o chao");',
    "                        }",
    "                        // <<< KABONG PEDRA",
    "",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--com-diario", action="store_true")
    p.add_argument("--seco", action="store_true")
    a = p.parse_args()

    print("############ GERAR PickaxeItem.override.cs ############")
    print("origem: %s" % ORIGEM)
    print("diario: %s" % ("LIGADO" if a.com_diario else "desligado"))
    print("modo  : %s" % ("SECO -- nao instala" if a.seco else "INSTALAR"))
    print("")

    print("=== 1. conferindo o arquivo do jogo ===")
    if not os.path.isfile(ORIGEM):
        sys.exit("[XX] nao achei %s" % ORIGEM)
    with open(ORIGEM, "rb") as f:
        cru = f.read()
    # Copia de arquivo do jogo: casar o encoding do original (este TEM BOM).
    tem_bom = cru.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in cru
    linhas = cru.decode("utf-8-sig").split("\r\n" if crlf else "\n")
    fim_nl = linhas and linhas[-1] == ""
    if fim_nl:
        linhas = linhas[:-1]
    orig = list(linhas)
    n_orig = len(orig)
    print("  %d linhas   MD5 %s" % (n_orig, hashlib.md5(cru).hexdigest()))
    print("  BOM: %s   fim-de-linha: %s" % ("sim" if tem_bom else "nao", "CRLF" if crlf else "LF"))

    achados = [i for i, l in enumerate(linhas) if ANCORA in l]
    if len(achados) != 1:
        print("  [XX] a ancora <%s> apareceu %d vez(es), esperado 1" % (ANCORA, len(achados)))
        for i in achados:
            print("       linha %d: %s" % (i + 1, linhas[i].strip()))
        sys.exit("ABORTANDO -- o arquivo do jogo mudou. Revise antes de gerar.")
    i_anc = achados[0]
    print("  ancora na linha %d: %s" % (i_anc + 1, linhas[i_anc].strip()))
    print("")

    print("=== 2. montando ===")
    bloco = list(BLOCO)
    if not a.com_diario:
        n = sum(len(RE_DIARIO.findall(l)) for l in BLOCO)
        bloco = [RE_DIARIO.sub("", l) for l in bloco]
        print("  diario desligado: %d chamadas retiradas SEM apagar linha" % n)

    linhas = linhas[:i_anc] + bloco + linhas[i_anc:]
    print("  bloco: %d linhas, antes da linha %d" % (len(bloco), i_anc + 1))

    cab = [
        "// ============================================================================",
        "// PickaxeItem.override.cs  --  GERADO por gerar-pedra-override.py",
        "// Servidor Kabong Brasil",
        "//",
        "// NAO EDITE ESTE ARQUIVO A MAO. E uma copia do PickaxeItem.cs do jogo com UMA",
        "// mudanca, entre  >>> KABONG PEDRA  e  <<< KABONG PEDRA:",
        "//",
        "//   Se houver espaco na MAO, o bloco minerado vai direto para ela, usando a",
        "//   mesma sobrecarga de DeleteBlock que a pa usa. Sem espaco, o codigo original",
        "//   roda e o entulho cai no chao -- o fallback e o proprio jogo, de graca.",
        "//",
        "//   Quem decide a QUANTIDADE continua sendo o jogo. Medido em campo: 4 blocos",
        "//   por bloco minerado, identico ao caminho do entulho. A economia nao mudou.",
        "//",
        "// Depois de ATUALIZAR O ECO, rode o gerador de novo para recopiar do arquivo novo.",
        "// Para reverter: apague este arquivo e reinicie.",
        "// ============================================================================",
        "",
    ]
    for i, e in enumerate(cab):
        if not isinstance(e, str):
            sys.exit("[XX] cabecalho, elemento %d: tipo %s" % (i + 1, type(e).__name__))
        if e.strip() and not e.strip().startswith("//"):
            sys.exit("[XX] cabecalho, elemento %d nao e comentario nem vazio: <%s>" % (i + 1, e))
    print("  TRAVA 1: cabecalho, %d elementos, todos comentario ou vazio  [ok]" % len(cab))
    print("")

    destino = DIAG if a.seco else DESTINO
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    nl = "\r\n" if crlf else "\n"
    with open(destino, "wb") as f:
        if tem_bom:
            f.write(b"\xef\xbb\xbf")
        f.write((nl.join(cab + linhas) + (nl if fim_nl else "")).encode("utf-8"))
    print("=== 3. gravado: %s (%d bytes) ===" % (destino, os.path.getsize(destino)))

    with open(destino, "rb") as f:
        conf = f.read().decode("utf-8-sig").split(nl)
    if conf and conf[-1] == "":
        conf = conf[:-1]
    esperado = len(cab) + n_orig + len(bloco)
    if len(conf) != esperado:
        sys.exit("[XX] contagem de linhas: %d, esperado %d" % (len(conf), esperado))

    corpo = conf[len(cab):]
    dentro, regioes, sem_bloco = False, 0, []
    i = 0
    while i < len(corpo):
        l = corpo[i]
        if not dentro and ">>> KABONG" in l:
            dentro, regioes = True, regioes + 1
            i += 1
            continue
        if dentro:
            if "<<< KABONG" in l:
                dentro = False
                i += 1  # pula a linha vazia do fim do bloco
            i += 1
            continue
        sem_bloco.append(l)
        i += 1
    if dentro:
        sys.exit("[XX] marcador >>> KABONG sem o <<< correspondente")
    if regioes != 1:
        sys.exit("[XX] %d regiao(oes) marcada(s); esperado 1" % regioes)
    if len(sem_bloco) != n_orig:
        sys.exit("[XX] sem o bloco sobraram %d linhas, esperado %d" % (len(sem_bloco), n_orig))

    # A TRAVA MAIS FORTE: aqui nao ha troca de constante, entao o esperado e ZERO.
    difs = [(i + 1, orig[i], sem_bloco[i]) for i in range(n_orig) if sem_bloco[i] != orig[i]]
    if difs:
        for n, o, d in difs[:6]:
            print("     ! linha %d:  <%s>  ->  <%s>" % (n, o.strip(), d.strip()))
        sys.exit("[XX] fora do bloco o corpo difere em %d linha(s); esperado ZERO" % len(difs))
    print("  TRAVA 2: 1 regiao marcada, corpo IDENTICO ao original fora dela  [ok]")
    print("")

    if a.seco:
        print("=== MODO SECO CONCLUIDO -- as duas travas passaram ===")
        print("  O servidor NAO foi tocado. Para instalar, rode sem --seco.")
        return

    print("############ INSTALADO ############")
    print("Compilar sem erro CS0101 e a prova de que o override substituiu o arquivo.")


if __name__ == "__main__":
    main()
