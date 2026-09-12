#!/usr/bin/env python3
"""gerar-tronco-override.py -- gera o TreeObject.override.cs a partir do arquivo do JOGO.

    python3 gerar-tronco-override.py --seco          # gera em /opt/eco/diag-tronco, nao instala
    python3 gerar-tronco-override.py                 # gera e instala
    python3 gerar-tronco-override.py --max 95 --fatia 5 --tentativas 1,2,3.5,5,6.5
    python3 gerar-tronco-override.py --com-diario    # liga as linhas de diagnostico

Porte do gerar-tronco-override.ps1 (Windows) para o servidor Linux, 03/09/2026.
Confirmado antes de portar: o TreeObject.cs da 0.14.1.0 tem 1118 linhas e as mesmas
ancoras nas mesmas linhas da 0.14.0.3 (constante 92, targetLength 265).

POR QUE GERAR EM VEZ DE MANTER O OVERRIDE A MAO
    Um .override.cs substitui o arquivo inteiro do jogo, entao ele e uma COPIA CONGELADA.
    Toda atualizacao do Eco que mexa naquele arquivo deixa a nossa versao velha -- foi
    assim que o Big fast shovel degradou sem avisar (CLAUDE.md secao 10-C). Gerando do
    arquivo instalado, ele COMPILA POR CONSTRUCAO e a atualizacao e um comando.

AS QUATRO MUDANCAS (todas medidas em campo, CLAUDE.md 19.20)
    1. MaxTrunkPickupSize 5 -> 95        (sozinha nao tem efeito visivel -- ver 19.11)
    2. FATIA do AutoSliceTrunk = 5       (correcao de 29/08: a constante servia a DOIS
                                          propositos, e a fatia de 95 ficava incatavel)
    3. Entrega automatica do tronco na MAO   -> 75/75 em 8 a 28 ms
    4. Toco destruido / residuo na MOCHILA   -> "sobrou 0"; 27 itens, 0 fallback

RODAR SEMPRE O --seco PRIMEIRO. Ele roda as duas travas em segundos, sem tocar no
servidor. Foi o modo seco que pegou o bug do BOM (19.6) e o da virgula (19.5).
"""

import argparse
import hashlib
import os
import re
import sys

ORIGEM = "/opt/eco/server/Mods/__core__/Objects/TreeObject.cs"
# Mesmo caminho relativo, com .override antes do .cs -- exigencia do ModKit.
DESTINO = "/opt/eco/server/Mods/UserCode/Objects/TreeObject.override.cs"
DIAG = "/opt/eco/diag-tronco/TreeObject.override.cs"

ALVO_CONST = "private const int MaxTrunkPickupSize = 5;"
ALVO_FATIA = "var targetLength = (float)MaxTrunkPickupSize / this.ResourceMultiplier;"
# DUPLICACAO DE MADEIRA -- medida em campo em 03/09/2026, 21:23.
#   Uma arvore de mult=75 rendeu 99 na mao MAIS pecas no chao. O diario mostrou:
#     t=1s  pecas=2   -> levou 9 e 66  (75, o tronco inteiro)
#     t=5s  pecas=14  -> levou 24 mais, faixa 0,058 a 0,517  JA COLETADA
#   Causa: ao fatiar, o jogo cria `new TrunkPiece()` copiando so posicao e rotacao.
#   A peca nova nasce com Collected = false, entao FATIA DE TRONCO JA LEVADO VIRA
#   MADEIRA NOVA. No baunilha isso nunca acontece porque o jogador nao consegue
#   pegar um tronco de 75 antes de fatiar -- e a NOSSA ordem (pegar em 1s, fatiar
#   em 5s) que abre o furo.
#   Conserto: a fatia herda o Collected da origem. Uma linha, e vale para todo
#   caminho que fatie, inclusive os do proprio jogo.
ALVO_COLETADA = "Rotation   = trunkPiece.Rotation,"
ANCORA_TRONCO = "Logger's Luck: single chance proc"
ANCORA_GALHO = "World.SetBlock(this.Species.DebrisType, abovepos);"

# O diario e retirado SUBSTITUINDO a chamada, nunca apagando a linha: algumas moram
# dentro de  catch (...) { KabongLog.Tronco(...); kabongDeu = false; }  e apagar a linha
# mataria o catch. Preservar a contagem tambem mantem as travas validas.
RE_DIARIO = re.compile(r"KabongBrasil\.KabongLog\.(?:Tronco|Pedra)\([^;]*\);\s*")


def bloco_tronco(tempos_cs, fatia):
    return [
        "            // >>> KABONG: entrega automatica do tronco na mao de quem derrubou.",
        "            // A coleta manual depende da env var 'canPickup', calculada pelo CLIENTE",
        "            // vanilla, que mantem o limite antigo - por isso a entrega e feita aqui.",
        "            //",
        "            // VARIAS TENTATIVAS de proposito: a posicao do tronco vem da fisica do",
        "            // cliente durante a queda; antes dela chegar, a peca e descartada pelo",
        "            // filtro IsCollectedOrNotValid. Tentar cedo E tarde entrega o mais rapido",
        "            // possivel sem quebrar em arvore alta. Idempotente: PickupLog marca",
        "            // Collected e o filtro descarta nas tentativas seguintes.",
        "            //",
        "            // A PENULTIMA tentativa (5 s, arvore ja no chao) e a que FATIA: corta sob",
        "            // medida o que nao cabe na mao e NAO coleta nada - a coleta das pecas",
        "            // recem-cortadas fica para a ULTIMA tentativa, para o cliente ter tempo de",
        "            // processar os RPCs SliceTrunk antes dos DestroyLog. Cortar 23 vezes e",
        "            // coletar 20 pecas no mesmo instante deixava pecas-fantasma na tela",
        "            // (relato dos jogadores em 07/09/2026: arvore de 120, 100 na mao, e 24",
        "            // pecas desenhadas das quais so 4 existiam).",
        "            if (player != null && !isVehicleCut)",
        "            {",
        "                var kabongJogador = player;",
        "                // Ferramenta capturada FORA do adiamento, como o jogo faz no bloco do",
        "                // Logger a seguir: e para as leis filtradas por ferramenta casarem com a",
        "                // machadada que derrubou, nao com o que estiver na mao 5 s depois.",
        "                var kabongFerramenta = player.User.Inventory.Toolbar.SelectedItem as ToolItem;",
        "                var kabongTempos  = new[] { %s };" % tempos_cs,
        "                const float kabongFatia = %df;   // tamanho da fatia catavel com E (limite do cliente)" % fatia,
        "                for (var kabongI = 0; kabongI < kabongTempos.Length; kabongI++)",
        "                {",
        "                    // FATIAR SO NA PENULTIMA tentativa. Fatiar cedo corta uma geometria que",
        "                    // ainda nao assentou - foi o que produziu peca torta no teste de campo",
        "                    // (46 na mao com sobra de tronco, contra 75 esperando os 5 s).",
        "                    var kabongFatiar = kabongI == kabongTempos.Length - 2;",
        "                    var kabongT      = kabongTempos[kabongI];",
        "                    ThreadUtils.Delay(kabongT, () =>",
        "                    {",
        "                        try",
        "                        {",
        "                            // TOCO: o jogo so faz isso por sorte, via talento Logger Luck em",
        "                            // Logging 6. Aqui vale para todos. Idempotente pelo teste de",
        "                            // stumpHealth. NAO usar TryDestroyStump: ele passa giveResource=false e",
        "                            // JOGA FORA os TrunkResources (a polpa do toco) -- ver 07/09/2026 abaixo.",
        "                            //",
        "                            // SO DEPOIS DA QUEDA (5 s), e o motivo NAO e o mesmo do fatiar:",
        "                            // CheckDestroy destroi a arvore quando  Fallen && stumpHealth<=0",
        "                            // && todas as pecas coletadas. Com a mao vazia, destruir o toco em",
        "                            // t=1s fechava a condicao junto com a coleta, a arvore sumia ANTES",
        "                            // de bater no chao, e CollideWithTerrain -- que e RPC do cliente na",
        "                            // colisao -- nunca acontecia. Sem colisao, SEM RESIDUO: nem polpa,",
        "                            // nem semente, nem fibra. Observado em campo em 03/09/2026: com a",
        "                            // mao cheia vinha polpa, com a mao vazia nao vinha.",
        "                            if (kabongFatiar && this.stumpHealth > 0)",
        "                            {",
        "                                // 07/09/2026: com giveResource=true a polpa do toco (TrunkResources: cacto 4-6, joshua/abeto 8-10) vai para a mochila, como quando o jogador corta o toco a mao. Mochila cheia: o golpe falha limpo e o toco fica para cortar a mao.",
        "                                this.TryDamageStump(new GameActionPack(), kabongJogador, this.stumpHealth, kabongFerramenta, true).TryPerform(kabongJogador.User);",
        '                                KabongBrasil.KabongLog.Tronco("toco: tentou destruir, sobrou " + this.stumpHealth);',
        "                            }",
        "",
        "                            var kabongPecas = this.trunkPieces.Where(x => !x.IsCollectedOrNotValid).ToList();",
        '                            KabongBrasil.KabongLog.Tronco("t=" + kabongT + "s fatiar=" + kabongFatiar + " pecas=" + kabongPecas.Count + " mult=" + this.ResourceMultiplier);',
        "",
        "                            if (kabongFatiar)",
        "                            {",
        "                                // CORTE SOB MEDIDA. Para cada peca que nao cabe: uma fatia com o que",
        "                                // cabe na mao (menos 1, folga para o arredondamento do GetBasePickupSize)",
        "                                // e o resto em fatias de kabongFatia, cataveis com E. Nada e coletado",
        "                                // aqui - fica para a proxima tentativa.",
        "                                var kabongEspacoRestante = -1;",
        "                                foreach (var kabongPeca in kabongPecas)",
        "                                {",
        "                                    var (kabongRes, kabongNum) = this.CalculateTrunkResources(kabongJogador, kabongPeca);",
        "                                    if (kabongRes == null || kabongNum <= 0) continue;",
        "                                    if (kabongEspacoRestante < 0) kabongEspacoRestante = kabongJogador.User.Inventory.Carried.RoomFor(kabongRes);",
        "                                    // cabe inteira E passa no teto do PickupLog (base <= MaxTrunkPickupSize): nao cortar.",
        "                                    // Sem a 2a condicao, peca de 96-100 cabia na mao mas o PickupLog recusava (campo 08/09: 97 ficou no chao).",
        "                                    if (kabongNum <= kabongEspacoRestante && this.GetBasePickupSize(kabongPeca) <= MaxTrunkPickupSize) { kabongEspacoRestante -= kabongNum; continue; }",
        "",
        "                                    var kabongBonus  = kabongNum - this.GetBasePickupSize(kabongPeca);   // bonus de talento/yield, nao vem do comprimento",
        "                                    // teto: PickupLog recusa peca com base > MaxTrunkPickupSize (campo 07/09: 99 ficou no chao)",
        "                                    var kabongAlvo   = Math.Min(kabongEspacoRestante - kabongBonus - 1, MaxTrunkPickupSize);",
        "                                    var kabongIniRes = kabongPeca.SliceStart;                              // de onde comecam as fatias de 5",
        "                                    var kabongFim    = kabongPeca.SliceEnd;   // TrySliceTrunkStrict encurta ESTA peca ate o corte; o fim original e o do resto (campo 07/09: 'resto de 0,825 a 0,825')",
        "                                    if (kabongAlvo >= kabongFatia)",
        "                                    {",
        "                                        var kabongCorte = kabongPeca.SliceStart + kabongAlvo / this.ResourceMultiplier;",
        "                                        this.TrySliceTrunkStrict(null, kabongCorte);",
        '                                        KabongBrasil.KabongLog.Tronco("   corte sob medida em " + kabongCorte + " (" + kabongAlvo + " logs cabem de " + kabongNum + ")");',
        "                                        kabongEspacoRestante = 0;",
        "                                        kabongIniRes = kabongCorte;",
        "                                    }",
        "                                    else kabongEspacoRestante = 0;",
        "",
        "                                    // o resto em fatias de kabongFatia (como o AutoSliceTrunk faz, mas so nesta peca)",
        "                                    var kabongPasso = kabongFatia / this.ResourceMultiplier;",
        "                                    var kabongN = 0;",
        "                                    for (var kabongSp = kabongIniRes + kabongPasso; kabongSp < kabongFim - kabongPasso * 0.5f; kabongSp += kabongPasso)",
        "                                    {",
        "                                        this.TrySliceTrunkStrict(null, kabongSp);",
        "                                        kabongN++;",
        "                                    }",
        '                                    KabongBrasil.KabongLog.Tronco("   resto de " + kabongIniRes + " a " + kabongFim + " em " + (kabongN + 1) + " fatias de " + kabongFatia);',
        "                                }",
        "                                return;   // coleta so na proxima tentativa",
        "                            }",
        "",
        "                            foreach (var kabongPeca in kabongPecas)",
        "                            {",
        "                                var (kabongRes, kabongNum) = this.CalculateTrunkResources(kabongJogador, kabongPeca);",
        "                                var kabongEspaco = kabongRes == null ? 0 : kabongJogador.User.Inventory.Carried.RoomFor(kabongRes);",
        '                                KabongBrasil.KabongLog.Tronco("   peca " + kabongPeca.SliceStart + " a " + kabongPeca.SliceEnd + " rende " + kabongNum + ", espaco na mao " + kabongEspaco);',
        "                                if (kabongNum <= 0) continue;",
        '                                if (kabongEspaco < kabongNum) { KabongBrasil.KabongLog.Tronco("   -> nao cabe, fica no chao"); continue; }',
        "                                this.PickupLog(kabongJogador, kabongPeca.ID, kabongPeca.Position);",
        '                                KabongBrasil.KabongLog.Tronco(kabongPeca.Collected ? "   -> levou " + kabongNum : "   -> PickupLog RECUSOU (base " + this.GetBasePickupSize(kabongPeca) + " > " + MaxTrunkPickupSize + "?)");',
        "                            }",
        "                        }",
        '                        catch (Exception kabongEx) { KabongBrasil.KabongLog.Tronco("   EXCECAO: " + kabongEx.Message); }',
        "                    });",
        "                }",
        "            }",
        "            // <<< KABONG",
        "",
    ]

BLOCO_GALHO = [
    "                              // >>> KABONG GALHO: residuo direto para a mochila.",
    "                              // Se couber, nem cria o bloco no chao - o que tambem alivia",
    "                              // o servidor. Se nao couber, segue o comportamento original.",
    "                              {",
    "                                  var kabongDeu = false;",
    "                                  try",
    "                                  {",
    "                                      using (var kabongPack = new GameActionPack())",
    "                                      {",
    "                                          foreach (var kabongD in this.Species.DebrisResources)",
    "                                              kabongPack.AddToInventory(player.User.Inventory, Item.GetNonUniqueOrClone(kabongD.Key), kabongD.Value.RandIntInc, player.User);",
    "                                          kabongDeu = !kabongPack.TryPerform(player.User).Failed;",
    "                                      }",
    "                                  }",
    '                                  catch (Exception kabongExG) { KabongBrasil.KabongLog.Tronco("galho EXCECAO: " + kabongExG.Message); kabongDeu = false; }',
    '                                  KabongBrasil.KabongLog.Tronco("galho -> mochila: " + kabongDeu);',
    "                                  if (kabongDeu)",
    "                                  {",
    "                                      if (Interlocked.Increment(ref this.treeDebrisSpawned) >= MaxTreeDebris) return;",
    "                                      continue;   // nao cria o bloco de galho no chao",
    "                                  }",
    "                              }",
    "                              // <<< KABONG GALHO",
    "",
]


def acha_unico(linhas, texto, oque, exato=False):
    """Devolve o indice UNICO da linha. Exige exatidao: nunca gerar override errado
    em silencio -- se o arquivo do jogo mudou, tem de abortar alto."""
    achados = []
    for i, l in enumerate(linhas):
        if (l.strip() == texto) if exato else (texto in l):
            achados.append(i)
    if len(achados) != 1:
        print("  [XX] %s: apareceu %d vez(es), esperado exatamente 1" % (oque, len(achados)))
        for i in achados[:6]:
            print("       linha %d: %s" % (i + 1, linhas[i].strip()))
        if not achados:
            chave = texto.split("(")[0].split("=")[0].strip().split()[-1]
            print("       linhas parecidas (contendo %r):" % chave)
            for i, l in enumerate(linhas):
                if chave and chave in l:
                    print("         linha %d: %s" % (i + 1, l.strip()))
        sys.exit("ABORTANDO -- o arquivo do jogo mudou de forma. Revise antes de gerar.")
    return achados[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=95, help="MaxTrunkPickupSize (limite de coleta)")
    p.add_argument("--fatia", type=int, default=5, help="tamanho da fatia do AutoSliceTrunk")
    p.add_argument("--tentativas", default="1,2,3.5,5,6.5", help="segundos apos a queda")
    p.add_argument("--com-diario", action="store_true", help="liga as linhas de diagnostico")
    p.add_argument("--seco", action="store_true", help="gera em pasta temporaria, nao instala")
    a = p.parse_args()

    print("############ GERAR TreeObject.override.cs ############")
    print("origem     : %s" % ORIGEM)
    print("MaxTronco  : %d      fatia: %d" % (a.max, a.fatia))
    print("tentativas : %s" % a.tentativas)
    print("diario     : %s" % ("LIGADO" if a.com_diario else "desligado"))
    print("modo       : %s" % ("SECO -- nao instala" if a.seco else "INSTALAR"))
    print("")

    # valida o parametro ANTES de gerar C# com ele
    tempos = []
    for t in a.tentativas.split(","):
        t = t.strip()
        if not re.match(r"^\d+(\.\d+)?$", t):
            sys.exit("Tentativa invalida: <%s>. Numeros separados por virgula, ex.: 1,2,3.5,5" % t)
        tempos.append(t + "f")
    if not tempos:
        sys.exit("Nenhuma tentativa informada.")
    tempos_cs = ", ".join(tempos)

    # ---------------------------------------------------------------- 1. o arquivo do jogo
    print("=== 1. conferindo o arquivo do jogo ===")
    if not os.path.isfile(ORIGEM):
        sys.exit("[XX] nao achei %s" % ORIGEM)
    with open(ORIGEM, "rb") as f:
        cru = f.read()
    # ENCODING: a regra do projeto INVERTE aqui. Para .eco e script, gravar SEM BOM.
    # Para COPIA de arquivo do jogo, casar com o original -- e o TreeObject.cs TEM BOM,
    # com travessoes em comentarios. Gravar sem BOM fez o PowerShell reler como ANSI e
    # corromper 12 linhas (CLAUDE.md 19.6). No Linux o risco e outro, mas casar o
    # encoding continua sendo a regra certa.
    tem_bom = cru.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in cru
    texto = cru.decode("utf-8-sig")
    linhas = texto.split("\r\n" if crlf else "\n")
    # split deixa um elemento vazio no fim se o arquivo termina com newline
    fim_nl = linhas and linhas[-1] == ""
    if fim_nl:
        linhas = linhas[:-1]
    orig = list(linhas)
    n_orig = len(orig)
    print("  %d linhas   MD5 %s" % (n_orig, hashlib.md5(cru).hexdigest()))
    print("  BOM: %s   fim-de-linha: %s" % ("sim" if tem_bom else "nao", "CRLF" if crlf else "LF"))

    i_const = acha_unico(linhas, ALVO_CONST, "a constante MaxTrunkPickupSize", exato=True)
    print("  constante na linha %d" % (i_const + 1))
    i_fatia = acha_unico(linhas, ALVO_FATIA, "a linha do targetLength", exato=True)
    print("  targetLength na linha %d" % (i_fatia + 1))
    i_colet = acha_unico(linhas, ALVO_COLETADA, "a linha Rotation da peca nova", exato=True)
    print("  Rotation da peca nova na linha %d" % (i_colet + 1))
    i_tronco = acha_unico(linhas, ANCORA_TRONCO, "a ancora do bloco do TRONCO")
    print("  ancora do tronco na linha %d" % (i_tronco + 1))
    i_galho = acha_unico(linhas, ANCORA_GALHO, "a ancora do GALHO")
    print("  ancora do galho na linha %d" % (i_galho + 1))

    if not (i_const < i_galho < i_tronco):
        sys.exit("[XX] ordem inesperada (constante < galho < tronco). ABORTANDO.")
    print("  ordem conferida: constante < galho < tronco  [ok]")
    print("")

    # ---------------------------------------------------------------- 2. montar
    print("=== 2. montando ===")
    b_tronco = bloco_tronco(tempos_cs, a.fatia)
    b_galho = list(BLOCO_GALHO)
    if not a.com_diario:
        b_tronco = [RE_DIARIO.sub("", l) for l in b_tronco]
        b_galho = [RE_DIARIO.sub("", l) for l in b_galho]
        n = sum(len(RE_DIARIO.findall(l)) for l in bloco_tronco(tempos_cs, a.fatia) + BLOCO_GALHO)
        print("  diario desligado: %d chamadas retiradas SEM apagar linha" % n)

    ind = re.match(r"\s*", linhas[i_const]).group(0)
    linhas[i_const] = "%sprivate const int MaxTrunkPickupSize = %d;   // KABONG: era 5" % (ind, a.max)
    # A fatia herda o Collected da origem. Fica na MESMA linha do Rotation de
    # proposito: assim nao muda a contagem de linhas e a TRAVA 2 continua valendo.
    indc = re.match(r"\s*", linhas[i_colet]).group(0)
    linhas[i_colet] = ("%sRotation   = trunkPiece.Rotation, Collected  = trunkPiece.Collected,"
                       "   // KABONG: fatia de tronco JA COLETADO nasce coletada, senao duplica madeira"
                       % indc)

    indf = re.match(r"\s*", linhas[i_fatia]).group(0)
    linhas[i_fatia] = ("%svar targetLength = (float)%d / this.ResourceMultiplier;"
                       "   // KABONG: fatia de %d, era MaxTrunkPickupSize" % (indf, a.fatia, a.fatia))

    # INJECOES: da ULTIMA para a PRIMEIRA, senao a primeira desloca o indice da segunda.
    linhas = linhas[:i_tronco] + b_tronco + linhas[i_tronco:]
    linhas = linhas[:i_galho] + b_galho + linhas[i_galho:]
    print("  bloco do TRONCO: %d linhas, antes da linha %d" % (len(b_tronco), i_tronco + 1))
    print("  bloco do GALHO : %d linhas, antes da linha %d" % (len(b_galho), i_galho + 1))

    cab = [
        "// ============================================================================",
        "// TreeObject.override.cs  --  GERADO por gerar-tronco-override.py",
        "// Servidor Kabong Brasil",
        "//",
        "// NAO EDITE ESTE ARQUIVO A MAO. E uma copia do TreeObject.cs do jogo com as",
        "// mudancas abaixo, todas marcadas:",
        "//",
        "//   1. MaxTrunkPickupSize de 5 para %d, e a FATIA do AutoSliceTrunk em %d." % (a.max, a.fatia),
        "//      A constante servia a DOIS propositos: o limite de coleta e o tamanho da",
        "//      fatia. Com as duas em 95 o excedente caia cortado em pedacos de 95, e o",
        "//      cliente vanilla so oferece pegar ate 5 -- ficava INCATAVEL.",
        "//",
        "//   2. Entrega AUTOMATICA do tronco no FellTree (entre  >>> KABONG  e  <<< KABONG),",
        "//      com toco destruido. Necessaria porque a coleta manual depende da env var",
        "//      'canPickup', calculada pelo CLIENTE vanilla -- so a mudanca 1 nao produz",
        "//      efeito visivel. Verificado em campo.",
        "//",
        "//   3. Residuo de galho para a MOCHILA (entre  >>> KABONG GALHO  e  <<< KABONG GALHO).",
        "//      Se couber, o bloco de galho nem e criado no chao.",
        "//",
        "// Depois de ATUALIZAR O ECO, rode o gerador de novo para recopiar do arquivo novo.",
        "// Para reverter: apague este arquivo e reinicie.",
        "// ============================================================================",
        "",
    ]

    # --- TRAVA 1: todo elemento do cabecalho e comentario ou linha vazia ---
    # Sem ela, cabecalho corrompido so aparece no compilador, 20 min depois. Foi assim
    # que a armadilha da virgula do PowerShell custou 40 min (CLAUDE.md 19.5).
    for i, e in enumerate(cab):
        if not isinstance(e, str):
            sys.exit("[XX] cabecalho, elemento %d: tipo %s em vez de str" % (i + 1, type(e).__name__))
        if e.strip() and not e.strip().startswith("//"):
            sys.exit("[XX] cabecalho, elemento %d nao e comentario nem vazio: <%s>" % (i + 1, e))
    print("  TRAVA 1: cabecalho, %d elementos, todos comentario ou vazio  [ok]" % len(cab))

    saida = cab + linhas
    print("")

    # ---------------------------------------------------------------- 3. gravar
    destino = DIAG if a.seco else DESTINO
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    nl = "\r\n" if crlf else "\n"
    dados = nl.join(saida) + (nl if fim_nl else "")
    with open(destino, "wb") as f:
        if tem_bom:
            f.write(b"\xef\xbb\xbf")
        f.write(dados.encode("utf-8"))
    print("=== 3. gravado: %s (%d bytes) ===" % (destino, os.path.getsize(destino)))

    # --- TRAVA 2: relido do disco, tirando cabecalho e blocos marcados, o corpo tem de
    # ser IDENTICO ao original menos EXATAMENTE 2 linhas. Invariante forte e barato:
    # pega corrupcao de encoding, de contagem e injecao no lugar errado. Foi o que
    # pegou o bug do BOM.
    with open(destino, "rb") as f:
        conf_cru = f.read()
    conf = conf_cru.decode("utf-8-sig").split(nl)
    if conf and conf[-1] == "":
        conf = conf[:-1]
    esperado = len(cab) + n_orig + len(b_tronco) + len(b_galho)
    if len(conf) != esperado:
        sys.exit("[XX] contagem de linhas: %d, esperado %d" % (len(conf), esperado))

    corpo = conf[len(cab):]
    dentro, regioes, sem_bloco = False, 0, []
    i = 0
    while i < len(corpo):
        l = corpo[i]
        if not dentro and ">>> KABONG" in l:
            dentro = True
            regioes += 1
            i += 1
            continue
        if dentro:
            if "<<< KABONG" in l:
                dentro = False
                i += 1  # pula tambem a linha vazia do fim do bloco
            i += 1
            continue
        sem_bloco.append(l)
        i += 1
    if dentro:
        sys.exit("[XX] marcador >>> KABONG sem o <<< KABONG correspondente")
    if regioes != 2:
        sys.exit("[XX] %d regiao(oes) marcada(s); esperado 2 (tronco e galho)" % regioes)
    if len(sem_bloco) != n_orig:
        sys.exit("[XX] sem os blocos sobraram %d linhas, esperado %d" % (len(sem_bloco), n_orig))

    difs = [(i + 1, orig[i], sem_bloco[i]) for i in range(n_orig) if sem_bloco[i] != orig[i]]
    if len(difs) != 3:
        for n, o, d in difs[:6]:
            print("     ! linha %d:  <%s>  ->  <%s>" % (n, o.strip(), d.strip()))
        sys.exit("[XX] fora dos blocos o corpo difere em %d linha(s); esperado exatamente 3"
                 % len(difs))
    print("  TRAVA 2: 2 regioes marcadas, corpo difere do original em exatamente 3 linhas  [ok]")
    for n, o, d in difs:
        print("     linha %d:  <%s>" % (n, d.strip()))
    print("")

    if a.seco:
        print("=== MODO SECO CONCLUIDO -- as duas travas passaram ===")
        print("  primeiras 14 linhas geradas:")
        for l in conf[:14]:
            print("     | %s" % l)
        print("")
        print("  O servidor NAO foi tocado. Para instalar, rode sem --seco.")
        return

    print("############ INSTALADO ############")
    print("Reiniciar e conferir. Se o override NAO substituir o arquivo do jogo, o")
    print("compilador acusa CS0101 (TrunkPiece/TreeEntity definidos duas vezes) --")
    print("ou seja, COMPILAR SEM ERRO e a prova de que o override pegou.")


if __name__ == "__main__":
    main()
