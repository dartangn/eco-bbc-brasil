# -*- coding: utf-8 -*-
"""
Troca a arte do icone da BOMBA DE COMBUSTIVEL (PumpGasMod) pela arte da LOJA do jogo.

POR QUE, e o que ja foi tentado
-------------------------------
Relato do Raul em 20/09: o icone da bomba sai grande demais no mapa. A primeira
tentativa foi o `pixelsPerUnit` (100 -> 150, igual ao da Loja) -- ver secao 64 do
CLAUDE.md. Aplicado no teste e conferido no bundle (os 3 sprites em ppu=150.0), e o
proprio Raul reportou em 21/09: "a correcao nao melhorou ele". Entao o ppu estava
inocente, e o pedido volta a ser o original dele: por a arte da Loja na bomba.

O QUE FOI MEDIDO ANTES DE ESCOLHER O CAMINHO
--------------------------------------------
  icon_pumpgas   128x128 DXT1  8192 bytes  mips=1   100,0% opaco  <- a bomba, COM fundo
  StoreItem      128x128 RGBA (do cliente)           78,2% opaco  <- a loja,  COM fundo
  StoreItem_FG   128x128 RGBA                        28,3% opaco  <- a loja,  RECORTADA
  GrayBackground NAO e textura -- e regiao do atlas UI_Icons 2048x2048 (rect y=1408)

O prefab do mod monta  GrayBackground (fundo)  +  icon_pumpgas (frente).
O da Loja monta        StoreItem (fundo)       +  StoreItem_FG (frente).

Como a `icon_pumpgas` JA TRAZ o fundo azul embutido, o papel dela e o do `StoreItem`,
nao o do `StoreItem_FG`. Logo:

  icon_pumpgas  <-  StoreItem        UMA textura, resultado igual a Loja de verdade
  icon_pumpgas  <-  StoreItem_FG     daria a lojinha recortada sobre o CINZA do mod

Por isso o padrao e `StoreItem`. O `--recortada` existe para o caso de ele preferir a
loja sobre o fundo cinza do mod -- mas nao e o que a Loja do jogo mostra.

O `icon_totem` NAO e tocado: e outro objeto do mod, e o pedido foi sobre a bomba.

CUSTO HERDADO (nao ha como evitar, e esta registrado na secao 64.4)
-------------------------------------------------------------------
E binario dentro de mod de terceiro: atualizacao do PumpGasMod desfaz, e nao da para
reaplicar por script como o OutputAmount do No More Books. Rodar de novo e o conserto.
E o nome da cena NAO e versionado (renomear quebraria o proprio mod), entao pela regra
60.13 o jogador precisa FECHAR o jogo e abrir -- reconectar nao basta.

USO
---
  python gerar-icone-bomba-loja.py --bundle pump-teste.unity3d
  python gerar-icone-bomba-loja.py --bundle pump-teste.unity3d --recortada
  python gerar-icone-bomba-loja.py --bundle pump-teste.unity3d --rgba32
"""
import argparse
import io
import os
import sys

try:
    import UnityPy
    from PIL import Image
except Exception as e:
    print("[XX] falta UnityPy/Pillow: %s" % e)
    sys.exit(1)

AQUI = os.path.dirname(os.path.abspath(__file__))
ARTE = os.path.join(AQUI, "icone-bomba")
ALVO = "icon_pumpgas"
NAO_TOCAR = "icon_totem"


def fmt_int(v):
    """m_TextureFormat vem as vezes como IntEnum, as vezes como int."""
    try:
        return int(v)
    except Exception:
        return int(getattr(v, "value", -1))


def carregar(env):
    """Indexa Texture2D e Sprite por nome, lendo do bundle."""
    texs, sprites = {}, {}
    for o in env.objects:
        if o.type.name == "Texture2D":
            d = o.read()
            texs.setdefault(d.m_Name, []).append((o, d))
        elif o.type.name == "Sprite":
            d = o.read()
            sprites.setdefault(d.m_Name, []).append((o, d))
    return texs, sprites


def assinatura(caminho):
    """Retrato do bundle: para comparar antes x depois sem depender de md5."""
    env = UnityPy.load(caminho)
    arqs = sorted(env.file.files.keys())
    n = 0
    texs = {}
    ppus = {}
    for o in env.objects:
        n += 1
        if o.type.name == "Texture2D":
            d = o.read()
            dados = bytes(d.image_data) if hasattr(d, "image_data") else b""
            texs[d.m_Name] = (d.m_Width, d.m_Height, fmt_int(d.m_TextureFormat),
                              len(dados), hash(dados))
        elif o.type.name == "Sprite":
            d = o.read()
            ppus[d.m_Name] = getattr(d, "m_PixelsToUnits", None)
    return {"arquivos": arqs, "objetos": n, "texturas": texs, "ppu": ppus}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--recortada", action="store_true",
                    help="usa StoreItem_FG (loja recortada sobre o cinza do mod)")
    ap.add_argument("--rgba32", action="store_true",
                    help="grava sem compressao, se o DXT1 degradar a arte")
    a = ap.parse_args()

    origem = os.path.join(ARTE, "StoreItem_FG.png" if a.recortada else "StoreItem.png")
    if not os.path.isfile(origem):
        print("[XX] nao achei a arte da loja: %s" % origem)
        print("     ela e extraida do bundle de icones do CLIENTE (ver 64.3)")
        return 1
    if not os.path.isfile(a.bundle):
        print("[XX] nao achei o bundle: %s" % a.bundle)
        return 1

    saida = a.saida or (a.bundle + ".novo")

    print("=== ANTES ===")
    antes = assinatura(a.bundle)
    print("  arquivos internos : %s" % antes["arquivos"])
    print("  objetos           : %d" % antes["objetos"])
    alvo_antes = antes["texturas"].get(ALVO)
    if not alvo_antes:
        print("[XX] o bundle nao tem a textura %s. ABORTEI." % ALVO)
        return 1
    print("  %s     : %dx%d fmt=%d %d bytes" % ((ALVO,) + alvo_antes[:4]))
    print("  ppu               : %s" % antes["ppu"])

    # ---- a troca ----
    env = UnityPy.load(a.bundle)
    texs, _ = carregar(env)
    if len(texs.get(ALVO, [])) != 1:
        print("[XX] esperava %s exatamente 1 vez, achei %d. ABORTEI."
              % (ALVO, len(texs.get(ALVO, []))))
        return 1

    img = Image.open(origem).convert("RGBA")
    o, d = texs[ALVO][0]
    if (d.m_Width, d.m_Height) != img.size:
        print("[XX] dimensao diferente: textura %sx%s, arte %sx%s. ABORTEI."
              % (d.m_Width, d.m_Height, img.size[0], img.size[1]))
        return 1

    if a.rgba32:
        from UnityPy.enums import TextureFormat
        d.m_TextureFormat = TextureFormat.RGBA32
    d.image = img
    d.save()

    with open(saida, "wb") as fh:
        fh.write(env.file.save(packer="lz4"))
    print("\n[ok] gravado %s  (%d bytes)" % (saida, os.path.getsize(saida)))

    # ---- TRAVAS: reler do disco, nunca confiar no objeto em memoria ----
    print("\n=== DEPOIS (relido do arquivo gravado) ===")
    dep = assinatura(saida)
    falhas = []

    if dep["arquivos"] != antes["arquivos"]:
        falhas.append("nomes de arquivo INTERNO mudaram %s -> %s   (colisao de cena, regra 60.12)"
                      % (antes["arquivos"], dep["arquivos"]))
    else:
        print("  [ok] arquivos internos inalterados: %s" % dep["arquivos"])

    if dep["objetos"] != antes["objetos"]:
        falhas.append("contagem de objetos %d -> %d" % (antes["objetos"], dep["objetos"]))
    else:
        print("  [ok] objetos: %d" % dep["objetos"])

    al = dep["texturas"].get(ALVO)
    if not al:
        falhas.append("a textura %s desapareceu" % ALVO)
    elif al[:2] != alvo_antes[:2]:
        falhas.append("%s mudou de dimensao %s -> %s" % (ALVO, alvo_antes[:2], al[:2]))
    elif al[4] == alvo_antes[4]:
        falhas.append("%s NAO mudou -- a troca nao pegou" % ALVO)
    else:
        print("  [ok] %s trocada: %dx%d fmt=%d %d bytes (era fmt=%d %d bytes)"
              % (ALVO, al[0], al[1], al[2], al[3], alvo_antes[2], alvo_antes[3]))

    # nenhuma OUTRA textura pode ter mudado
    for nome, v in antes["texturas"].items():
        if nome == ALVO:
            continue
        if dep["texturas"].get(nome) != v:
            falhas.append("textura %s mudou e NAO devia (%s -> %s)"
                          % (nome, v[:4], (dep["texturas"].get(nome) or ("?",))[:4]))
    if not falhas:
        print("  [ok] as outras %d texturas intactas (inclusive %s)"
              % (len(antes["texturas"]) - 1, NAO_TOCAR))

    if dep["ppu"] != antes["ppu"]:
        falhas.append("ppu mudou %s -> %s" % (antes["ppu"], dep["ppu"]))
    else:
        print("  [ok] ppu preservado: %s" % dep["ppu"])

    # previa para OLHAR antes de instalar -- a licao de 64.2
    try:
        env2 = UnityPy.load(saida)
        for o2 in env2.objects:
            if o2.type.name == "Texture2D":
                d2 = o2.read()
                if d2.m_Name == ALVO:
                    d2.image.save(os.path.join(ARTE, "pump-DEPOIS.png"))
                    print("  [ok] previa em icone-bomba/pump-DEPOIS.png -- OLHAR antes de instalar")
                    break
    except Exception as e:
        print("  [!!] nao consegui gerar a previa: %s" % e)

    if falhas:
        print("\n[XX] %d TRAVA(S) REPROVARAM:" % len(falhas))
        for f in falhas:
            print("     - %s" % f)
        os.remove(saida)
        print("  saida apagada. Nada a instalar.")
        return 1

    print("\n[ok] todas as travas passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
