# -*- coding: utf-8 -*-
"""Separa os icones em BORDA SOLIDA (nao aceitam nobg) e BORDA MACIA.

POR QUE ISTO EXISTE
    O atributo type="nobg" da tag <icon> tira o fundo do icone -- mas so funciona
    se a arte TIVER recorte. Icone cujo quadrado inteiro e opaco sai com fundo
    branco na placa, e nenhuma tag conserta.
    Medido em campo em 12/09/2026: a previsao desta varredura acertou 5 de 5
    (FieldSmoothie, BlackCoffee e AgaveJuice saem com quadrado; Tomato e
    CeramicTeaCup saem limpos).

COMO
    Le SO a primeira linha de cada PNG -- o filtro da linha 0 nao depende da
    linha anterior, entao da para decodificar sem descompactar a imagem inteira.
    Sem PIL, que nao existe nesta maquina.
"""
import os, struct, zlib, io

PNG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "png")

def alfa_linha0(caminho):
    b = open(caminho, "rb").read()
    if len(b) < 26 or b[1:4] != b"PNG": return None
    larg, alt = struct.unpack(">II", b[16:24])
    prof, cor = b[24], b[25]
    if cor != 6 or prof != 8: return None
    dados = b""; i = 8
    while i < len(b) and len(dados) < 65536:
        tam = struct.unpack(">I", b[i:i+4])[0]
        if b[i+4:i+8] == b"IDAT": dados += b[i+8:i+8+tam]
        i += 12 + tam
    try: cru = zlib.decompressobj().decompress(dados, 4 + larg*4 + 8)
    except Exception: return None
    passo = larg*4
    if len(cru) < passo + 1: return None
    f = cru[0]; lin = bytearray(cru[1:1+passo])
    if f == 1 or f == 4:                       # Sub, e Paeth com linha anterior zerada
        for x in range(4, passo): lin[x] = (lin[x] + lin[x-4]) & 255
    elif f == 3:                               # Average
        for x in range(4, passo): lin[x] = (lin[x] + lin[x-4]//2) & 255
    return [lin[x*4+3] for x in range(larg)]

solidos, macios, outros = [], [], []
for f in sorted(os.listdir(PNG_DIR)):
    if not f.endswith(".png"): continue
    a = alfa_linha0(os.path.join(PNG_DIR, f))
    nome = f[:-4]
    if a is None: outros.append(nome)
    else: (solidos if min(a) == 255 else macios).append(nome)

saida = os.path.join(os.path.dirname(PNG_DIR), "solidos.txt")
io.open(saida, "w", encoding="utf-8", newline="\n").write("\n".join(solidos) + "\n")
print("solidos (nao aceitam nobg): %d   macios: %d   nao lidos: %d"
      % (len(solidos), len(macios), len(outros)))
print("gravado em", saida)
