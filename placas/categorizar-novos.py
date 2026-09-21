# -*- coding: utf-8 -*-
"""
Categoria dos icones que vieram dos BUNDLES DE MOD (png-mod/).

O categorizar.py original classifica pelos [RequireComponent] que o jogo pendura no
objeto -- o que o objeto FAZ, que e o criterio certo (licao de 12/09: tag descreve
EFEITO, nao identidade). Aqueles dados foram coletados do servidor para os itens que
o GoodPrice tinha; os 84 icones novos nao estavam naquela coleta e cairiam todos em
"Diversos".

Aqui a classificacao e por NOME, e so para eles. E mais fraca de proposito -- nao
invento componente que nao medi -- mas resolve os casos que sao inequivocos pelo
sufixo (Skill, SkillBook, SkillScroll, TalentGroup) e deixa o resto em Diversos em
vez de chutar.

Escreve categorias-mod.txt; o extrair-icones.py le os dois arquivos, e este NAO
sobrescreve categoria que o original ja tenha decidido.
"""
import io, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))

# (teste, categoria) -- a ORDEM importa: o primeiro que casar decide, e os sufixos
# mais especificos vem antes. "IceCreamSkillBook" tem de cair em Pesquisa, nao em
# Profissoes, e sem a ordem certa o teste de "Skill" pegaria os dois.
REGRAS = [
    (lambda n: n.endswith("SkillBook") or n.endswith("SkillScroll"), "Pesquisa"),
    (lambda n: n.endswith("TalentGroup") or n.endswith("Group"),     "Grupos de item"),
    (lambda n: n.endswith("Skill"),                                  "Profissões"),
    (lambda n: "Whetstone" in n or "RepairTool" in n,                "Ferramentas"),
    (lambda n: "Gate" in n or "Door" in n or "DrawBridge" in n,      "Blocos e construção"),
    (lambda n: any(p in n for p in ("Coffee", "Tea", "Cocktail", "Juice",
                                   "Smoothie", "Mixology")),         "Comida"),
    (lambda n: "IceCream" in n or "Cornet" in n or "Popsicle" in n,  "Comida"),
    (lambda n: "Market" in n,                                        "Lojas"),
    (lambda n: n.endswith("Object"),                                 "Outros objetos"),
]


def main():
    pm = os.path.join(AQUI, "png-mod")
    if not os.path.isdir(pm):
        print("[XX] png-mod/ nao existe -- rode extrair-icones-de-mod.py antes")
        return 1
    novos = sorted(f[:-4] for f in os.listdir(pm)
                   if f.endswith(".png") and not f.startswith("_"))

    ja = set()
    _c = os.path.join(AQUI, "categorias.txt")
    if os.path.exists(_c):
        for l in io.open(_c, encoding="utf-8"):
            q = l.rstrip().split("|")
            if len(q) == 2:
                ja.add(q[0])

    linhas, cont = [], {}
    for n in novos:
        if n in ja:          # o categorizar.py, que mede componente, tem precedencia
            continue
        cat = "Diversos"
        for teste, c in REGRAS:
            if teste(n):
                cat = c; break
        cont[cat] = cont.get(cat, 0) + 1
        linhas.append("%s|%s" % (n, cat))

    io.open(os.path.join(AQUI, "categorias-mod.txt"), "w", encoding="utf-8").write("\n".join(linhas))
    print("categorias-mod.txt: %d icones" % len(linhas))
    for c, q in sorted(cont.items(), key=lambda x: -x[1]):
        print("  %-22s %3d" % (c, q))
    return 0


if __name__ == "__main__":
    sys.exit(main())
