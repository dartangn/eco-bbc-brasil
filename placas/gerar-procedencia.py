# -*- coding: utf-8 -*-
"""
De onde vem cada icone da galeria -- e quais NAO existem para o cliente.

O PROBLEMA QUE ISTO RESOLVE
---------------------------
A galeria foi montada dos PNG que o GoodPrice embute. O GoodPrice NAO e a fonte que
o cliente do Eco usa para desenhar icone, e as duas listas nao batem:

  - ele tem nomes que NINGUEM entrega (agrupamentos internos dele, e mods que nao
    estao instalados aqui). Copiar esses da ENGRENAGEM na placa. Aconteceu duas
    vezes em campo: a placa DRINKS da Kris em 15/09, e a da netcrazy em 21/09.
  - ele NAO tem icones que os mods instalados entregam de verdade -- entre eles o
    da profissao IceCream, que foi o relato de 21/09.

A FONTE QUE VALE e a que o cliente consulta:

  item do jogo base -> Sprite no atlas do cliente
                       Eco_Data/StreamingAssets/aa/StandaloneWindows64/icons_assets_all_*.bundle
  item de mod       -> prefab com o nome EXATO da classe, no .unity3d do mod

Saida: procedencia.txt, uma linha por icone, `arquivo|nome-emitido|procedencia`, com
procedencia em JOGO / MOD:<nome do mod> / ORFAO.

Regra que sai daqui: a galeria confere contra o que o CLIENTE tem, nunca contra o
nome do arquivo que veio do GoodPrice.
"""
import io, os, sys, glob
import UnityPy

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))

# O atlas do cliente. Procurado em TODAS as bibliotecas da Steam: em 20/09 eu olhei
# so o C: e concluí que o cliente nao estava nesta maquina -- ele estava no D:.
ATLAS_GLOBS = [
    r"C:/Program Files (x86)/Steam/steamapps/common/Eco/Eco_Data/StreamingAssets/aa/StandaloneWindows64/icons_assets_all_*.bundle",
    r"D:/SteamLibrary/steamapps/common/Eco/Eco_Data/StreamingAssets/aa/StandaloneWindows64/icons_assets_all_*.bundle",
    r"E:/SteamLibrary/steamapps/common/Eco/Eco_Data/StreamingAssets/aa/StandaloneWindows64/icons_assets_all_*.bundle",
]

BUNDLES = [
    ("IceCream",    "mixologia-icones/outros/IceCreamM.unity3d"),
    ("Gates",       "mixologia-icones/outros/Assets_Gates.unity3d"),
    ("MarketMod",   "mixologia-icones/outros/Assets_MarketMod.unity3d"),
    ("Mixology",    "mixologia-icones/MixologyMod.unity3d"),
    ("Mixology",    "mixologia-icones/doador/MixologyTable.unity3d"),
    ("Mixology",    "bundles-mod/AdvancedMixologyTable.unity3d"),
    ("HotWheels",   "bundles-mod/HotWheels.unity3d"),
    ("StorageMore", "bundles-mod/StorageMore.unity3d"),
    ("PumpGasMod",  "scratch-pump.unity3d"),
    ("Whetstones",  "mixologia-icones/doador/Whetstones.unity3d"),
    ("EcoPulse",    "mixologia-icones/doador/Assets_EcoPulse_Image.unity3d"),
]


def sprites_do_atlas():
    cam = None
    for g in ATLAS_GLOBS:
        hit = glob.glob(g)
        if hit:
            cam = hit[0]; break
    if not cam:
        print("[XX] atlas de icones do CLIENTE nao encontrado.")
        print("     Sem ele nao da para dizer o que e do jogo base -- abortando em vez")
        print("     de marcar 1581 icones do jogo como orfaos.")
        return None
    print("atlas do cliente: %s" % os.path.basename(cam))
    s = set()
    for o in UnityPy.load(cam).objects:
        if o.type.name == "Sprite":
            try:
                n = o.read().m_Name
            except Exception:
                continue
            if n:
                s.add(n)
    return s


def main():
    cliente = sprites_do_atlas()
    if cliente is None:
        return 1
    print("  %d sprites" % len(cliente))

    dono = {}
    for mod, rel in BUNDLES:
        cam = os.path.join(RAIZ, rel)
        if not os.path.isfile(cam):
            print("  (falta) %-14s %s" % (mod, rel)); continue
        n = 0
        for o in UnityPy.load(cam).objects:
            if o.type.name == "GameObject":
                try:
                    nm = o.read().m_Name
                except Exception:
                    continue
                if nm and nm not in dono:
                    dono[nm] = mod; n += 1
        print("  %-14s %4d prefabs novos" % (mod, n))

    corr = {}
    _re = os.path.join(AQUI, "nomes-reais.txt")
    if os.path.exists(_re):
        for l in io.open(_re, encoding="utf-8"):
            q = l.rstrip().split("|")
            if len(q) == 2:
                corr[q[0]] = q[1]

    arquivos = set()
    for d in ("png", "png-mod"):
        p = os.path.join(AQUI, d)
        if os.path.isdir(p):
            arquivos |= {f[:-4] for f in os.listdir(p) if f.endswith(".png") and not f.startswith("_")}

    linhas, cont = [], {}
    for arq in sorted(arquivos):
        nome = corr.get(arq, arq)
        if nome in cliente:
            proc = "JOGO"
        elif nome in dono:
            proc = "MOD:" + dono[nome]
        else:
            proc = "ORFAO"
        cont[proc.split(":")[0]] = cont.get(proc.split(":")[0], 0) + 1
        linhas.append("%s|%s|%s" % (arq, nome, proc))

    # trava: se quase tudo virou orfao, a fonte falhou -- nao gravar um arquivo que
    # faria a galeria marcar o jogo inteiro como quebrado.
    if cont.get("ORFAO", 0) > len(arquivos) * 0.25:
        print("[XX] %d de %d marcados ORFAO -- fonte suspeita, nao gravei nada."
              % (cont["ORFAO"], len(arquivos)))
        return 1

    io.open(os.path.join(AQUI, "procedencia.txt"), "w", encoding="utf-8").write("\n".join(linhas))
    print()
    for k in ("JOGO", "MOD", "ORFAO"):
        print("  %-6s %5d" % (k, cont.get(k, 0)))
    print("[ok] procedencia.txt  (%d linhas)" % len(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
