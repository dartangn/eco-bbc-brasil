# -*- coding: utf-8 -*-
"""Descobre QUAL textura 512x512 do bundle corresponde a cada icone nomeado.

POR QUE PRECISA
    As texturas do bundle se chamam "1", "14", "60" -- o nome do item esta no PREFAB,
    e seguir prefab -> Image -> Sprite -> Texture pelo typetree e caro e fragil.
    Mas nos TEMOS o icone 32x32 com o nome certo (extraido do GoodPrice). Entao:
    reduzir cada textura 512 para 32x32 e ver de qual icone nomeado ela mais se
    parece resolve o mesmo problema, com dado que ja esta na mao.

    Isso vale para gerar a previa da galeria a partir da arte GRANDE, em vez de
    recortar 32x32 -- que e onde o recorte estraga o desenho, por falta de pixel.
"""
import os, io
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
GAL = os.path.join(AQUI, "..", "ecopedia-bbc", "icones")
ORIG = os.path.join(AQUI, "originais")

bbc = [l.rstrip().split("|")[0] for l in io.open(os.path.join(AQUI, "nomes-bbc.txt"), encoding="utf-8") if l.strip()]
nomes = [n for n in bbc if os.path.exists(os.path.join(GAL, "png", n + ".png"))]

def mini(img):
    a = np.asarray(img.convert("RGB").resize((24, 24), Image.LANCZOS)).astype(np.float32)
    return a - a.mean()

alvos = {n: mini(Image.open(os.path.join(GAL, "png", n + ".png"))) for n in nomes}
texs = {}
for f in sorted(os.listdir(ORIG)):
    if not f.endswith(".png"): continue
    if "Font" in f or "SDF" in f: continue
    texs[f] = mini(Image.open(os.path.join(ORIG, f)))

pares, usados = [], set()
custos = []
for n, av in alvos.items():
    for f, tv in texs.items():
        custos.append((float(np.abs(av - tv).mean()), n, f))
custos.sort()
feito = set()
for c, n, f in custos:
    if n in feito or f in usados: continue
    feito.add(n); usados.add(f); pares.append((n, f, c))

pares.sort(key=lambda p: p[2])
io.open(os.path.join(AQUI, "casamento.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join("%s|%s|%.2f" % p for p in sorted(pares)) + "\n")
print("casados: %d de %d icones nomeados" % (len(pares), len(nomes)))
print()
print("--- 5 melhores")
for n, f, c in pares[:5]: print("   %-28s -> %-24s custo %.2f" % (n, f, c))
print("--- 5 piores (conferir)")
for n, f, c in pares[-5:]: print("   %-28s -> %-24s custo %.2f" % (n, f, c))
