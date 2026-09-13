# -*- coding: utf-8 -*-
"""Tira o fundo degrade dos icones da Mixologia, gerando PNG com canal alfa.

POR QUE
    A arte do mod e uma aquarela sobre um degrade pastel, e as texturas estao em
    DXT1 -- formato que NAO TEM canal alfa. Por isso o icone sai com um quadrado
    na placa e o type="nobg" nao faz nada: nao ha transparencia para respeitar.

COMO
    Crescimento de regiao a partir da BORDA. O fundo e liso, entao comparar cada
    pixel novo com o VIZINHO ja aceito (e nao com uma cor fixa) acompanha o
    degrade sem vazar para dentro do desenho.
    Duas travas contra vazamento:
      - passo local pequeno (--passo, padrao 10);
      - o pixel tambem precisa ficar dentro de --global da cor da borda mais
        proxima em luminancia, o que segura vazamento por dentro de aquarela clara.
    A borda ganha meio-tom (anti-serrilhado) pela distancia da cor de fundo.

USO
    python recortar.py              -> le originais/, escreve recortados/
    python recortar.py --passo 14   -> mais agressivo (tira mais fundo)
    python recortar.py --so 14__24  -> so um arquivo, para calibrar
"""
import os, sys, collections
import numpy as np
import furos
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(AQUI, "originais")
SAI = os.path.join(AQUI, "recortados")

PASSO = 10        # tolerancia entre pixel e vizinho ja aceito
FUROS = True      # remover fundo cercado pelo desenho (--sem-furos desliga)
TOLFURO = 20      # quanto o furo pode se afastar do degrade previsto
GLOBAL = 60       # tolerancia contra a cor da borda
SUAVE = 14        # largura do meio-tom na borda do recorte

args = sys.argv[1:]
so = None
for i, a in enumerate(args):
    if a == "--passo": PASSO = int(args[i+1])
    elif a == "--global": GLOBAL = int(args[i+1])
    elif a == "--so": so = args[i+1]
    elif a == "--sem-furos": FUROS = False
    elif a == "--tolfuro": TOLFURO = int(args[i+1])

def recorta(caminho):
    im = Image.open(caminho).convert("RGB")
    w, h = im.size
    a = np.asarray(im).astype(np.int16)
    fundo = np.zeros((h, w), dtype=bool)
    visto = np.zeros((h, w), dtype=bool)

    # cor de referencia: mediana da moldura de 1px
    moldura = np.concatenate([a[0, :], a[h-1, :], a[:, 0], a[:, w-1]])
    ref = np.median(moldura, axis=0)

    fila = collections.deque()
    for x in range(w):
        for y in (0, h-1):
            if not visto[y, x]: visto[y, x] = True; fundo[y, x] = True; fila.append((y, x))
    for y in range(h):
        for x in (0, w-1):
            if not visto[y, x]: visto[y, x] = True; fundo[y, x] = True; fila.append((y, x))

    while fila:
        y, x = fila.popleft()
        c0 = a[y, x]
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if ny < 0 or nx < 0 or ny >= h or nx >= w or visto[ny, nx]: continue
            c1 = a[ny, nx]
            if np.abs(c1-c0).max() <= PASSO and np.abs(c1-ref).max() <= GLOBAL:
                visto[ny, nx] = True; fundo[ny, nx] = True; fila.append((ny, nx))

    # FUROS: fundo cercado pelo desenho (o vao da alca da caneca) nao toca a borda,
    # entao o preenchimento acima nunca chega la. Ver furos.py.
    nfuro = 0
    if FUROS:
        fundo, pred, nfuro = furos.tira_furos(a, fundo, tol=TOLFURO)
    else:
        pred = None

    # alfa: 0 no fundo, 255 no desenho, meio-tom no limite.
    # A distancia sai da PREDICAO do degrade quando ela existe -- com uma cor unica,
    # o meio-tom fica errado do lado em que o degrade se afasta dela.
    base = pred if pred is not None else ref
    dist = np.abs(a.astype(np.float32) - base).max(axis=2)
    alfa = np.where(fundo, 0, np.clip(dist * (255.0 / max(SUAVE, 1)), 0, 255))

    saida = np.dstack([a.astype(np.uint8), alfa.astype(np.uint8)])
    return Image.fromarray(saida, "RGBA"), float(fundo.mean()), nfuro

os.makedirs(SAI, exist_ok=True)
arqs = sorted(f for f in os.listdir(ENT) if f.endswith(".png"))
if so: arqs = [f for f in arqs if so in f]
print("recortando %d arquivos  (passo=%d global=%d)" % (len(arqs), PASSO, GLOBAL))
ruins = []
for f in arqs:
    img, frac, nfuro = recorta(os.path.join(ENT, f))
    img.save(os.path.join(SAI, f))
    marca = "" if not nfuro else ("  furos: %d px" % nfuro)
    if frac < 0.05: marca = "  <-- quase nada virou fundo, CONFERIR"; ruins.append(f)
    if frac > 0.90: marca = "  <-- quase tudo virou fundo, CONFERIR"; ruins.append(f)
    print("   %-30s fundo removido: %5.1f%%%s" % (f, 100*frac, marca))
print()
print("suspeitos:", len(ruins))
for f in ruins: print("   " + f)
