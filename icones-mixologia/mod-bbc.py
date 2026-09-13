# -*- coding: utf-8 -*-
"""Gera o bundle do NOSSO mod: os icones recortados, com os prefabs renomeados para
   <Nome>BBC, para conviver com o mod original sem conflito de nome.

POR QUE RENOMEAR, e nao so instalar o pacote corrigido por cima
    Substituir o arquivo da Mixologia MORRE na proxima atualizacao dela. Um pacote
    nosso, com nomes proprios, sobrevive -- e as placas apontam para os nossos nomes.

O QUE O CLIENTE USA PARA ACHAR O ICONE
    Um GameObject (prefab) com o nome EXATO da classe do item -- 'PinaColadaItem',
    com filhos Background / Icon / Foreground / FullImage / FullName. Por isso
    renomear o prefab cria um endereco novo e livre.
    ISSO AINDA NAO FOI PROVADO EM CAMPO: o teste e por na placa <icon name="PinaColadaBBC">.

TRAVAS
    - so renomeia GameObject cujo nome termina em Item / Skill / SkillBook / SkillScroll;
      os filhos estruturais (Background, Icon, ...) e nomes internos ficam intocados;
    - reabre o arquivo gerado e confere contagem de objetos e quantos nomes mudaram.
"""
import os, sys
import UnityPy

AQUI = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(AQUI, "MixologyMod.unity3d.novo")     # ja recortado
SAI = os.path.join(AQUI, "IconesMixologiaBBC.unity3d")
SUF = "BBC"

def renomeavel(n):
    # Tudo que o cliente pode procurar por nome. Inclui TalentGroup para que o nosso
    # pacote nao tenha NENHUM nome igual ao do mod original -- dois bundles com o
    # mesmo nome de prefab e a unica forma conhecida de os dois brigarem.
    return (n.endswith("Item") or n.endswith("Skill") or n.endswith("SkillBook")
            or n.endswith("SkillScroll") or n.endswith("TalentGroup"))

if not os.path.exists(ENT):
    sys.exit("[XX] rode antes: python regravar.py")

env = UnityPy.load(ENT)
mudados = []
for obj in env.objects:
    if obj.type.name == "GameObject":
        d = obj.read()
        n = str(d.m_Name)
        if renomeavel(n) and not n.endswith(SUF):
            d.m_Name = n + SUF
            d.save()
            mudados.append((n, n + SUF))
    elif obj.type.name == "AssetBundle":
        d = obj.read()
        d.m_Name = "iconesmixologiabbc"
        d.save()

with open(SAI, "wb") as fh:
    fh.write(env.file.save(packer="lz4"))

print("prefabs renomeados:", len(mudados))
for a, b in mudados[:8]: print("   %-32s -> %s" % (a, b))
print("   ...")
print("gravado:", SAI, os.path.getsize(SAI), "bytes")

# ---------------- conferencia ----------------
a = UnityPy.load(ENT); b = UnityPy.load(SAI)
na, nb = len(a.objects), len(b.objects)
comsuf = 0
for obj in b.objects:
    if obj.type.name == "GameObject" and str(obj.read().m_Name).endswith(SUF): comsuf += 1
print()
print("objetos: %d / %d  %s" % (na, nb, "OK" if na == nb else "DIFERENTE -- NAO USAR"))
print("prefabs terminando em %s no arquivo novo: %d" % (SUF, comsuf))
print("OK" if (na == nb and comsuf == len(mudados) and comsuf > 50) else "CONFERIR")

# lista para o gerador de placas
lst = os.path.join(AQUI, "nomes-bbc.txt")
with open(lst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join("%s|%s" % (a, b) for a, b in sorted(mudados)) + "\n")
print("mapa de nomes:", lst)
