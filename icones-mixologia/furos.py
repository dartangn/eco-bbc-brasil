# -*- coding: utf-8 -*-
"""Acrescenta ao recorte a remocao de FUROS -- fundo cercado pelo desenho.

O PROBLEMA
    O preenchimento parte da BORDA, entao area de fundo que nao toca a borda nunca
    e alcancada: o vao da alca da caneca, o buraco de uma rosquinha, o meio de um
    aro. Ficava um pedaco do degrade la dentro.

A SOLUCAO, e ela precisa do degrade
    Comparar com uma cor unica nao serve: o fundo e um degrade, e a cor no vao da
    alca nao e a cor da borda. Entao:
      1. ajusta um PLANO por canal (c = a + b*x + c*y) usando so os pixels que o
         preenchimento ja marcou como fundo -- isso descreve o degrade;
      2. todo pixel que bate com o plano na SUA posicao vira candidato a furo;
      3. candidato so e aceito se formar uma ilha CERCADA e pequena (<8% da imagem),
         para nao comer area clara do proprio desenho.
"""
import collections
import numpy as np

def plano(a, mascara):
    """Ajusta c = k0 + k1*x + k2*y por canal, sobre os pixels de `mascara`."""
    h, w, _ = a.shape
    ys, xs = np.nonzero(mascara)
    if len(xs) < 50: return None
    A = np.stack([np.ones_like(xs), xs, ys], axis=1).astype(np.float64)
    gx, gy = np.meshgrid(np.arange(w), np.arange(h))
    pred = np.zeros_like(a, dtype=np.float64)
    for ch in range(3):
        k, *_ = np.linalg.lstsq(A, a[ys, xs, ch].astype(np.float64), rcond=None)
        pred[:, :, ch] = k[0] + k[1]*gx + k[2]*gy
    return pred

def ilhas(cand, limite):
    """Componentes conexas de `cand` que nao tocam a borda e cabem em `limite` pixels."""
    h, w = cand.shape
    visto = np.zeros((h, w), dtype=bool)
    aceitos = np.zeros((h, w), dtype=bool)
    # so percorre os CANDIDATOS. Varrer os 262144 pixels em Python era o gargalo.
    import numpy as _np
    for y0, x0 in zip(*_np.nonzero(cand)):
            y0, x0 = int(y0), int(x0)
            if visto[y0, x0]: continue
            fila = collections.deque([(y0, x0)]); visto[y0, x0] = True
            comp = []; toca = False
            while fila:
                y, x = fila.popleft(); comp.append((y, x))
                if y in (0, h-1) or x in (0, w-1): toca = True
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not visto[ny, nx]:
                        visto[ny, nx] = True; fila.append((ny, nx))
            if (not toca) and len(comp) <= limite:
                for y, x in comp: aceitos[y, x] = True
    return aceitos

def tira_furos(a, fundo, tol=20, frac_max=0.08):
    """Devolve (fundo_ampliado, predicao_do_degrade, quantos_pixels_de_furo)."""
    pred = plano(a, fundo)
    if pred is None: return fundo, None, 0
    dist = np.abs(a.astype(np.float64) - pred).max(axis=2)
    cand = (dist <= tol) & (~fundo)
    aceitos = ilhas(cand, int(frac_max * a.shape[0] * a.shape[1]))
    return (fundo | aceitos), pred, int(aceitos.sum())
