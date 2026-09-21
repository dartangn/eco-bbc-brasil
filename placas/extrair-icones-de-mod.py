# -*- coding: utf-8 -*-
"""
Extrai do BUNDLE DE CADA MOD os icones que a galeria nao tem.

POR QUE ISTO EXISTE
-------------------
A galeria foi montada dos PNG que o GoodPrice embute, e o GoodPrice NAO e a mesma
coisa que o cliente do Eco desenha:

  - ele tem 108 nomes que ninguem entrega (agrupamentos internos dele, e mods que
    nao estao instalados aqui) -> a tag sai na placa como ENGRENAGEM;
  - ele NAO tem 107 icones que os mods instalados entregam de verdade -- entre eles
    o icone da profissao IceCream, que foi o relato de campo.

A fonte que vale e a que o CLIENTE usa:
  item do jogo  -> sprite no atlas do cliente (icons_assets_all_*.bundle)
  item de mod   -> prefab <NomeDaClasse> no .unity3d do mod

Este script cobre a segunda metade: acha o prefab, desce
  <Classe> -> Icon -> FullImage | Foreground -> m_Sprite -> Texture2D
e grava o PNG.

Grava em pasta NOVA e so depois troca: regravar 100 arquivos por cima dispara o
falso positivo de ransomware do Acronis (licao de 12/09).
"""
import io, os, sys, shutil
import UnityPy
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))

# nome do mod -> bundle. O nome e o que aparece na etiqueta MOD da galeria.
BUNDLES = [
    ("IceCream",              "mixologia-icones/outros/IceCreamM.unity3d"),
    ("Gates",                 "mixologia-icones/outros/Assets_Gates.unity3d"),
    ("MarketMod",             "mixologia-icones/outros/Assets_MarketMod.unity3d"),
    ("Mixology",              "mixologia-icones/MixologyMod.unity3d"),
    ("Mixology",              "mixologia-icones/doador/MixologyTable.unity3d"),
    ("Mixology",              "bundles-mod/AdvancedMixologyTable.unity3d"),
    ("HotWheels",             "bundles-mod/HotWheels.unity3d"),
    ("StorageMore",           "bundles-mod/StorageMore.unity3d"),
    ("PumpGasMod",            "scratch-pump.unity3d"),
    ("Whetstones",            "mixologia-icones/doador/Whetstones.unity3d"),
    ("EcoPulse",              "mixologia-icones/doador/Assets_EcoPulse_Image.unity3d"),
]

SAIDA     = os.path.join(AQUI, "png-mod")
PROCED    = os.path.join(AQUI, "procedencia.txt")
SECO      = "--seco" in sys.argv


def af_de(x):
    """
    O arquivo interno a que um objeto pertence.

    Nesta versao do UnityPy o reader expoe `assets_file` e o PPtr expoe
    `assetsfile` -- sem underscore. Ler o atributo errado da AttributeError, e
    embrulhar isso num try/except daria "sem icone" em silencio.
    """
    return getattr(x, "assets_file", None) or getattr(x, "assetsfile", None)


def transform_filhos(go_ptr):
    """GameObject -> {nome do filho: ponteiro do GameObject}"""
    out = {}
    try:
        d = go_ptr.read() if hasattr(go_ptr, "read") else go_ptr
    except Exception:
        return out
    for c in getattr(d, "m_Component", []) or []:
        try:
            comp = c.component.read()
        except Exception:
            try:
                comp = c[1].read()
            except Exception:
                continue
        if type(comp).__name__ in ("Transform", "RectTransform"):
            for ch in getattr(comp, "m_Children", []) or []:
                try:
                    g = ch.read().m_GameObject
                    out[g.read().m_Name] = g
                except Exception:
                    pass
    return out


def sprite_da_camada(go_ptr):
    """Le o m_Sprite do componente Image de um GameObject de camada."""
    try:
        d = go_ptr.read() if hasattr(go_ptr, "read") else go_ptr
    except Exception:
        return None
    for c in getattr(d, "m_Component", []) or []:
        try:
            comp = c.component.read()
        except Exception:
            try:
                comp = c[1].read()
            except Exception:
                continue
        if type(comp).__name__ != "MonoBehaviour":
            continue
        try:
            tt = comp.object_reader.read_typetree()
        except Exception:
            continue
        sp = tt.get("m_Sprite")
        if isinstance(sp, dict) and sp.get("m_PathID"):
            return sp
    return None


def imagem_do_sprite(idx, arq_origem, af_origem, sp):
    """
    PPtr de sprite -> PIL.Image, ou None.

    Um bundle de cena tem DOIS arquivos internos: 'BuildPlayer-<cena>' com os
    prefabs e 'BuildPlayer-<cena>.sharedAssets' com os Sprite/Texture2D. O
    m_FileID do ponteiro diz em qual deles olhar -- 0 e o proprio arquivo, n e o
    n-esimo external. Ignorar isso encontra o path_id no arquivo ERRADO (onde ele
    e outro objeto qualquer) e conclui "nao tem icone". Foi o que aconteceu na
    primeira versao deste script: 0 de 107.
    """
    fid = sp.get("m_FileID", 0)
    if fid == 0:
        arq = arq_origem
    else:
        ex = getattr(af_origem, "externals", []) or []
        if fid - 1 >= len(ex):
            return None
        arq = getattr(ex[fid - 1], "name", None)
    o = idx.get((arq, sp["m_PathID"]))
    if o is None or o.type.name != "Sprite":
        return None
    try:
        return o.read().image
    except Exception:
        return None


def main():
    idx = {}   # path_id -> reader, por bundle
    achados = {}   # nome -> (mod, PIL.Image)
    for mod, rel in BUNDLES:
        cam = os.path.join(RAIZ, rel)
        if not os.path.isfile(cam):
            print("  (falta) %-22s %s" % (mod, rel)); continue
        try:
            env = UnityPy.load(cam)
        except Exception as e:
            print("  [XX] %-22s nao abriu: %s" % (mod, e)); continue
        # indice por (arquivo interno, path_id) -- ver imagem_do_sprite
        idx = {(getattr(af_de(o), "name", "?"), o.path_id): o for o in env.objects}
        prefabs = {}
        for o in env.objects:
            if o.type.name == "GameObject":
                try:
                    n = o.read().m_Name
                except Exception:
                    continue
                if n and n not in prefabs:
                    prefabs[n] = o
        n_ok = 0
        for nome, ptr in prefabs.items():
            if nome in achados:
                continue
            icon = transform_filhos(ptr).get("Icon")
            if icon is None:
                continue
            camadas = transform_filhos(icon)
            sp = None
            for pref in ("FullImage", "Foreground", "Background"):
                if pref in camadas:
                    sp = sprite_da_camada(camadas[pref])
                    if sp:
                        break
            if not sp:
                continue
            af = af_de(camadas[pref])
            img = imagem_do_sprite(idx, getattr(af, "name", "?"), af, sp)
            if img is None:
                continue
            achados[nome] = (mod, img)
            n_ok += 1
        print("  %-22s %4d prefabs, %4d com icone" % (mod, len(prefabs), n_ok))

    print()
    print("TOTAL de icones lidos dos bundles de mod: %d" % len(achados))

    if SECO:
        print("(modo seco: nada gravado)")
        return 0

    tmp = SAIDA + ".novo"
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    linhas = []
    for nome, (mod, img) in sorted(achados.items()):
        try:
            im = img.convert("RGBA")
            if im.size != (64, 64):
                im = im.resize((64, 64), Image.LANCZOS)
            im.save(os.path.join(tmp, nome + ".png"))
            linhas.append("%s|%s" % (nome, mod))
        except Exception as e:
            print("  [XX] %s: %s" % (nome, e))
    # trava: nao aceitar se gravou muito menos do que achou
    # trava: zero e FALHA, nao sucesso. A primeira versao comparava com
    # len(achados)*0.9 e, com achados=0, 0 < 0 e falso -- a trava passava.
    if len(linhas) < 50:
        print("[XX] so %d icones -- esperado ~100. NAO vou trocar a pasta." % len(linhas))
        return 1
    if len(linhas) < len(achados) * 0.9:
        print("[XX] gravou so %d de %d -- NAO vou trocar a pasta" % (len(linhas), len(achados)))
        return 1
    if os.path.isdir(SAIDA):
        shutil.rmtree(SAIDA)
    os.rename(tmp, SAIDA)
    io.open(os.path.join(SAIDA, "_procedencia.txt"), "w", encoding="utf-8").write("\n".join(linhas))
    print("[ok] %d PNG em %s" % (len(linhas), SAIDA))
    return 0


if __name__ == "__main__":
    sys.exit(main())
