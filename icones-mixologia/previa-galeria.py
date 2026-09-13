# -*- coding: utf-8 -*-
"""Gera a previa 32x32 da galeria A PARTIR DO RECORTE GRANDE (512x512).

POR QUE, e este e o ponto
    A primeira versao recortava o proprio icone de 32x32. Com tao pouco pixel o
    recorte nao tem margem: sobrava fundo rosa no vao da alca das canecas e, pior,
    comeu metade do copo do matcha. Reduzir DEPOIS de recortar em 512 resolve os
    dois -- o recorte trabalha com 256x mais pixel, e a reducao ainda suaviza a borda.

    O casamento icone-nomeado <-> textura numerada vem de casar.py.

Escreve numa pasta NOVA e so entao substitui a antiga: regravar 40 arquivos por cima
e o que faz o antivirus da maquina do Raul acusar ransomware.
"""
import os, io, shutil
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
REC  = os.path.join(AQUI, "recortados")
GAL  = os.path.join(AQUI, "..", "ecopedia-bbc", "icones")
NOVO = os.path.join(GAL, "png-bbc.novo")
ALVO = os.path.join(GAL, "png-bbc")

pares = []
for l in io.open(os.path.join(AQUI, "casamento.txt"), encoding="utf-8"):
    p = l.rstrip().split("|")
    if len(p) == 3: pares.append((p[0], p[1], float(p[2])))

if os.path.isdir(NOVO): shutil.rmtree(NOVO)
os.makedirs(NOVO)
feitos, faltou = 0, []
for nome, tex, custo in pares:
    f = os.path.join(REC, tex)
    if not os.path.exists(f): faltou.append(nome); continue
    im = Image.open(f).convert("RGBA").resize((32, 32), Image.LANCZOS)
    im.save(os.path.join(NOVO, nome + ".png"))
    feitos += 1
print("previas geradas do recorte 512:", feitos, " faltaram:", len(faltou))
if faltou: print("   ", ", ".join(faltou))

if os.path.isdir(ALVO): shutil.rmtree(ALVO)
os.rename(NOVO, ALVO)
print("pasta trocada:", ALVO)
