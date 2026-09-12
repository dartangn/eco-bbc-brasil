#!/usr/bin/env python3
"""gerar-pa-override.py -- gera o ShovelItem.override.cs a partir do arquivo do JOGO.

    python3 gerar-pa-override.py --seco
    python3 gerar-pa-override.py
    python3 gerar-pa-override.py --caps 10,20,30,50

PAGA UMA DIVIDA DOCUMENTADA. O ShovelItem.override.cs era o unico override do projeto
MANTIDO A MAO (CLAUDE.md 19.10 e 22.4), e mao e exatamente o defeito que degradou o
Big fast shovel sem avisar: copia congelada de um arquivo do jogo que depois mudou.

E A COPIA A MAO FICOU MENOR DO QUE ERA, porque metade do que ela fazia deixou de ser
necessario. Conferido no arquivo do jogo da 0.14.1.0:

    linha 54: if (this.MaxTake > 0 && !carried.IgnoreStackLimit
                  && !carried.Stacks.Any(s => s.Empty() || s.Quantity < this.MaxTake))
    linha 69: ... CarriedStackSizeCap = this.MaxTake;

    O JOGO JA TEM a verificacao POR SLOT (com .Any()) e JA TEM o CarriedStackSizeCap.
    Era isso que o nosso override "restaurava" -- porque o mod Big fast shovel havia
    apagado o cap e trocado a verificacao por slot por uma verificacao do TOTAL, o que
    travava a pa de madeira (MaxTake 1: "se ja carrega 1 ou mais, nao pode cavar").
    Como NAO instalamos aquele mod, o conserto perdeu o objeto.

SOBRA UMA COISA SO: a tabela de capacidade pedida pelos jogadores.
    do jogo:  madeira 1  | ferro 3  | aco 5  | moderna 10
    pedida:   madeira 10 | ferro 20 | aco 30 | moderna 50

    POR QUE TABELA E NAO MULTIPLICADOR: a primeira versao multiplicava o valor do jogo
    por 10, dando 10/30/50/100. A curva pedida seria x10, x6,67, x6 e x5 -- NENHUM
    multiplicador unico a produz. Por isso os dois vetores.

    O casamento e por TRECHO do nome da classe, nao por nome exato, para que as pas do
    AOE Tools (WoodenAOEShovelItem, ...) recebam o valor do nivel correspondente.
    Pa que nao casar com nenhum trecho cai em MaxTake x 10, como reserva.

ONDE A MUDANCA E FEITA, E POR QUE NO ShovelItem E NAO NAS 4 PAS
    As pas concretas declaram MaxTake em AutoGen/Tool/*Shovel.cs, e `partial class` NAO
    pode redeclarar membro ja declarado (CS0111 -- a mesma armadilha do SpecialtyCost).
    Mas o metodo Dig() vive na classe ABSTRATA ShovelItem, e e ele que consome o valor.
    Trocando o consumo em UM arquivo, resolve para as quatro pas -- em vez dos 4 ou 5
    .override.cs que seriam necessarios sobrescrevendo cada pa.
"""

import argparse
import hashlib
import os
import re
import sys

ORIGEM = "/opt/eco/server/Mods/__core__/Tools/ShovelItem.cs"
DESTINO = "/opt/eco/server/Mods/UserCode/Tools/ShovelItem.override.cs"
DIAG = "/opt/eco/diag-pa/ShovelItem.override.cs"

# Insere o bloco ANTES da linha do atributo do Dig -- unica no arquivo.
ANCORA = "[Interaction(InteractionTrigger.LeftClick, tags: BlockTags.Diggable"

TRECHOS = ["Wooden", "Iron", "Steel", "Modern"]


def bloco(caps):
    return [
        "        // >>> KABONG PA: capacidade da mao por nivel de pa.",
        "        // O jogo usa this.MaxTake (madeira 1, ferro 3, aco 5, moderna 10). Os",
        "        // jogadores pediram 10/20/30/50, e nenhum multiplicador unico produz essa",
        "        // curva -- por isso uma TABELA. Para mudar, mexer SO nos dois vetores.",
        "        //",
        "        // Casamento por TRECHO do nome da classe, nao por nome exato: assim as pas",
        "        // do AOE Tools (WoodenAOEShovelItem, ...) recebem o valor do nivel certo.",
        "        // System.StringComparison vem qualificado de proposito, para nao precisar",
        "        // acrescentar um 'using' -- assim o corpo difere do original em 2 linhas so.",
        "        private static readonly string[] KabongTrechosPa = new string[] { %s };"
        % ", ".join('"%s"' % t for t in TRECHOS),
        "        private static readonly int[]    KabongCapsPa    = new int[]    { %s };"
        % ", ".join("%d" % c for c in caps),
        "",
        "        // Pa que nao casar com trecho nenhum (ex.: pa de mod futuro) ganha isto.",
        "        private const int KabongFatorReserva = 10;",
        "",
        "        /// <summary>Quanto cabe em cada slot da MAO ao cavar com esta pa.</summary>",
        "        private int KabongCapacidadePorSlot",
        "        {",
        "            get",
        "            {",
        "                var kabongNome = this.GetType().Name;",
        "                for (var kabongI = 0; kabongI < KabongTrechosPa.Length; kabongI++)",
        "                    if (kabongNome.IndexOf(KabongTrechosPa[kabongI], System.StringComparison.OrdinalIgnoreCase) >= 0)",
        "                        return KabongCapsPa[kabongI];",
        "                return this.MaxTake * KabongFatorReserva;",
        "            }",
        "        }",
        "        // <<< KABONG PA",
        "",
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--caps", default="10,20,30,50",
                   help="capacidade por pa, na ordem madeira,ferro,aco,moderna")
    p.add_argument("--seco", action="store_true")
    p.add_argument("--sem-e", action="store_true",
                   help="NAO acrescentar o 'cavar com E' (padrao: acrescenta)")
    a = p.parse_args()

    try:
        caps = [int(x.strip()) for x in a.caps.split(",")]
    except ValueError:
        sys.exit("[XX] --caps aceita so numeros separados por virgula")
    if len(caps) != len(TRECHOS):
        sys.exit("[XX] --caps precisa de %d valores (%s), recebi %d"
                 % (len(TRECHOS), ",".join(TRECHOS), len(caps)))
    if any(c <= 0 for c in caps):
        sys.exit("[XX] capacidade tem de ser positiva")

    print("############ GERAR ShovelItem.override.cs ############")
    print("origem: %s" % ORIGEM)
    for t, c in zip(TRECHOS, caps):
        print("   %-8s -> %d" % (t, c))
    print("modo  : %s" % ("SECO -- nao instala" if a.seco else "INSTALAR"))
    print("")

    print("=== 1. conferindo o arquivo do jogo ===")
    if not os.path.isfile(ORIGEM):
        sys.exit("[XX] nao achei %s" % ORIGEM)
    with open(ORIGEM, "rb") as f:
        cru = f.read()
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

    # A ancora tem de ser unica
    anc = [i for i, l in enumerate(linhas) if ANCORA in l]
    if len(anc) != 1:
        print("  [XX] a ancora apareceu %d vez(es), esperado 1" % len(anc))
        for i in anc:
            print("       linha %d: %s" % (i + 1, linhas[i].strip()))
        sys.exit("ABORTANDO -- o arquivo do jogo mudou.")
    i_anc = anc[0]
    print("  ancora (atributo do Dig) na linha %d" % (i_anc + 1))

    # As linhas que consomem this.MaxTake dentro do Dig -- esperado EXATAMENTE 2.
    # Se o jogo passar a usar em 1 ou em 3 lugares, isto aborta em vez de gerar
    # override com metade da mudanca -- que falharia em silencio.
    consumo = [i for i, l in enumerate(linhas) if "this.MaxTake" in l]
    if len(consumo) != 2:
        print("  [XX] 'this.MaxTake' aparece em %d linha(s), esperado exatamente 2" % len(consumo))
        for i in consumo:
            print("       linha %d: %s" % (i + 1, linhas[i].strip()))
        sys.exit("ABORTANDO -- o Dig mudou de forma. Revise antes de gerar.")
    print("  'this.MaxTake' consumido em 2 linhas: %s" % ", ".join(str(i + 1) for i in consumo))

    for i in consumo:
        if i <= i_anc:
            sys.exit("[XX] consumo de MaxTake antes da ancora -- ordem inesperada")
    print("  ordem conferida: ancora < consumo  [ok]")
    print("")

    print("=== 2. montando ===")
    b = bloco(caps)
    # Troca de LINHA (nao insercao) nos dois consumos: mantem a contagem e as travas.
    for i in consumo:
        nova = linhas[i].replace("this.MaxTake", "this.KabongCapacidadePorSlot")
        # comentario no fim so na primeira, para nao poluir
        linhas[i] = nova + "   // KABONG: era this.MaxTake"
        print("  linha %d trocada" % (i + 1))
    linhas = linhas[:i_anc] + b + linhas[i_anc:]
    print("  bloco: %d linhas, antes da linha %d" % (len(b), i_anc + 1))

    # --- cavar com E: copia do Dig() ja gerado, com outro gatilho e outro nome ---------
    bloco_e = []
    if not a.sem_e:
        i_dig = i_anc + len(b)                      # o atributo do Dig, agora deslocado
        if ANCORA not in linhas[i_dig]:
            sys.exit("[XX] esperava o atributo do Dig na linha %d" % (i_dig + 1))
        j = i_dig + 1
        while j < len(linhas) and linhas[j] != "        }":
            j += 1
        if j >= len(linhas):
            sys.exit("[XX] nao achei o fim do Dig()")
        dig = linhas[i_dig:j + 1]
        if sum(1 for l in dig if "public bool Dig(" in l) != 1:
            sys.exit("[XX] o trecho copiado nao tem exatamente um 'public bool Dig('")
        copia = []
        for l in dig:
            if ANCORA in l:
                copia.append("        [Interaction(InteractionTrigger.InteractKey, tags: BlockTags.Diggable, canHoldToTrigger: TriBool.True, animationDriven: false)]")
            elif "public bool Dig(" in l:
                copia.append(l.replace("public bool Dig(", "public bool CavarComE("))
            else:
                copia.append(l)
        bloco_e = [
            "        // >>> KABONG E: cavar com a tecla E, sem animacao (rapido).",
            "        //",
            "        // Copia fiel do Dig() acima -- inclusive a tabela por pa -- com dois",
            "        // trocados: o gatilho (InteractKey em vez de LeftClick, animationDriven",
            "        // false) e o nome. E o que o mod Big fast shovel (mod.io 4266117) fazia",
            "        // no metodo DigFastwithE; aquele mod nao esta instalado porque sobrescreve",
            "        // este mesmo arquivo (CS0101) e trazia uma copia velha do Dig().",
        ] + copia + [
            "        // <<< KABONG E",
            "",
        ]
        linhas = linhas[:j + 1] + bloco_e + linhas[j + 1:]
        print("  cavar com E: %d linhas, depois da linha %d" % (len(bloco_e), j + 1))
    else:
        print("  cavar com E: NAO (--sem-e)")

    cab = [
        "// ============================================================================",
        "// ShovelItem.override.cs  --  GERADO por gerar-pa-override.py",
        "// Servidor Kabong Brasil",
        "//",
        "// NAO EDITE ESTE ARQUIVO A MAO -- foi exatamente essa a divida que este gerador",
        "// pagou. Copia do ShovelItem.cs do jogo com UMA mudanca, marcada:",
        "//",
        "//   As duas linhas do Dig() que consomem this.MaxTake passam a consumir uma",
        "//   TABELA por nivel de pa:  madeira %d | ferro %d | aco %d | moderna %d"
        % tuple(caps),
        "//   (o jogo usa 1 | 3 | 5 | 10). Nenhum multiplicador unico produz essa curva.",
        "//",
        "//   Feito na classe ABSTRATA porque e nela que o Dig() vive. As pas concretas",
        "//   declaram MaxTake em AutoGen/Tool/*Shovel.cs, e partial class nao pode",
        "//   redeclarar membro ja declarado (CS0111). Um arquivo resolve as quatro pas.",
        "//",
        "// A verificacao POR SLOT e o CarriedStackSizeCap NAO sao mais tocados: o jogo",
        "// da 0.14.1.0 ja os tem corretos. Aquilo era conserto de um estrago do mod",
        "// Big fast shovel, que nao esta instalado aqui.",
        "//",
        "// Segunda mudanca, marcada >>> KABONG E: um metodo CavarComE (o nome do metodo vira o texto do prompt: Cavar Com E), copia do",
        "// Dig() com gatilho InteractKey (tecla E) e sem animacao -- o 'cavar rapido'",
        "// que o mod Big fast shovel dava no servidor antigo.",
        "//",
        "// Depois de ATUALIZAR O ECO, rode o gerador de novo. Para reverter: apague.",
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
    esperado = len(cab) + n_orig + len(b) + len(bloco_e)
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
                i += 1
            i += 1
            continue
        sem_bloco.append(l)
        i += 1
    if dentro:
        sys.exit("[XX] marcador >>> KABONG sem o <<<")
    regioes_esperadas = 1 if a.sem_e else 2
    if regioes != regioes_esperadas:
        sys.exit("[XX] %d regiao(oes); esperado %d" % (regioes, regioes_esperadas))
    if len(sem_bloco) != n_orig:
        sys.exit("[XX] sem o bloco sobraram %d linhas, esperado %d" % (len(sem_bloco), n_orig))

    difs = [(i + 1, orig[i], sem_bloco[i]) for i in range(n_orig) if sem_bloco[i] != orig[i]]
    if len(difs) != 2:
        for n, o, d in difs[:6]:
            print("     ! linha %d:  <%s>  ->  <%s>" % (n, o.strip(), d.strip()))
        sys.exit("[XX] fora do bloco o corpo difere em %d linha(s); esperado exatamente 2"
                 % len(difs))
    print("  TRAVA 2: %d regiao(oes) marcada(s), corpo difere do original em exatamente 2 linhas  [ok]" % regioes)
    for n, o, d in difs:
        print("     linha %d: %s" % (n, d.strip()[:110]))
    print("")

    if a.seco:
        print("=== MODO SECO CONCLUIDO -- as duas travas passaram ===")
        print("  O servidor NAO foi tocado. Para instalar, rode sem --seco.")
        return

    print("############ INSTALADO ############")
    print("Compilar sem CS0101 e a prova de que o override substituiu o arquivo do jogo.")
    print("Conferir no jogo: cavar com cada pa e ver quanto vem na mao.")


if __name__ == "__main__":
    main()
