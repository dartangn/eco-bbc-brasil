# -*- coding: utf-8 -*-
"""Regrava o MixologyMod.unity3d com os icones recortados (com canal alfa).

TRAVAS
  1. So mexe em Texture2D REFERENCIADA POR UM SPRITE -- malha, material e atlas
     de fonte ficam intocados.
  2. Pula por nome qualquer coisa com Font / SDF / Atlas.
  3. Exige que o PNG recortado exista e tenha o mesmo tamanho da textura.
  4. No fim REABRE o arquivo gerado e confere: formato mudou, alfa existe, e a
     contagem de objetos e a mesma do original.
  Nao sobrescreve o original: escreve MixologyMod.unity3d.novo
"""
import os, sys
import UnityPy
from UnityPy.enums import TextureFormat
from PIL import Image
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(AQUI, "MixologyMod.unity3d")
NOVO = os.path.join(AQUI, "MixologyMod.unity3d.novo")
REC  = os.path.join(AQUI, "recortados")
FORMATO = TextureFormat.DXT5
if "--rgba" in sys.argv: FORMATO = TextureFormat.RGBA32

def proibido(nome):
    n = str(nome).lower()
    return ("font" in n) or ("sdf" in n) or ("atlas" in n)

env = UnityPy.load(ORIG)

usadas = set()
for obj in env.objects:
    if obj.type.name != "Sprite": continue
    d = obj.read()
    try: usadas.add(d.m_RD.texture.m_PathID)
    except Exception: pass
print("texturas referenciadas por Sprite:", len(usadas))

trocadas, pulados = 0, []
for obj in env.objects:
    if obj.type.name != "Texture2D": continue
    d = obj.read()
    nome = str(d.m_Name).strip()
    if obj.path_id not in usadas: pulados.append((nome, "nao e sprite")); continue
    if proibido(nome):            pulados.append((nome, "fonte/atlas")); continue
    png = os.path.join(REC, "%s__%d.png" % (nome.replace("/", "_"), obj.path_id))
    if not os.path.exists(png):   pulados.append((nome, "sem PNG recortado")); continue
    img = Image.open(png).convert("RGBA")
    if img.size != (d.m_Width, d.m_Height):
        pulados.append((nome, "tamanho diferente")); continue
    d.set_image(img, target_format=FORMATO)
    d.save()
    trocadas += 1

print("trocadas:", trocadas, " | pulados:", len(pulados))
for n, p in pulados: print("   pulado: %-28s (%s)" % (n, p))

with open(NOVO, "wb") as fh:
    fh.write(env.file.save(packer="lz4"))
print()
print("gravado:", NOVO, os.path.getsize(NOVO), "bytes  (original %d)" % os.path.getsize(ORIG))

# ---------------- conferencia: reabre o que foi gravado ----------------
print()
print("=== CONFERINDO o arquivo gerado")
a = UnityPy.load(ORIG); b = UnityPy.load(NOVO)
na, nb = len(a.objects), len(b.objects)
print("objetos: original %d  novo %d  %s" % (na, nb, "OK" if na == nb else "DIFERENTE -- NAO USAR"))

comalfa, semalfa, fmts = 0, 0, {}
for obj in b.objects:
    if obj.type.name != "Texture2D": continue
    d = obj.read()
    fmts[str(d.m_TextureFormat)] = fmts.get(str(d.m_TextureFormat), 0) + 1
    if proibido(str(d.m_Name)): continue
    try:
        arr = np.asarray(d.image.convert("RGBA"))
        (comalfa if (arr[:, :, 3] == 0).any() else semalfa).__int__
        if (arr[:, :, 3] == 0).any(): comalfa += 1
        else: semalfa += 1
    except Exception: pass
print("formatos no novo:", fmts)
print("texturas COM pixel transparente:", comalfa, " | sem:", semalfa)
print()
print("OK" if (na == nb and comalfa >= 60) else "CONFERIR ANTES DE USAR")
