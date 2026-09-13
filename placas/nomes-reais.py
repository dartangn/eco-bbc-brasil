# -*- coding: utf-8 -*-
"""Descobre o nome que a tag <icon name="..."> realmente aceita, para cada icone.

O PROBLEMA (relatado pelo Raul em 12/09/2026)
    A galeria emitia o nome do ARQUIVO, que vem do GoodPrice. Para profissao o
    GoodPrice chama de `TailoringSkillItem`, mas a classe do jogo e `TailoringSkill`
    -- **o `Item` no fim nao existe**. A placa do Raul que funciona usa
    `<icon name="CarpentrySkill">`, sem Item.

O CRITERIO
    Um nome so vale se for uma CLASSE do jogo. `classes.txt` traz as 10.804 classes
    declaradas em `__core__` e `UserCode`, colhidas do servidor.
      - nome e classe            -> usa como esta            (1658)
      - tirar "Item" vira classe -> usa sem o "Item"         (34, as profissoes)
      - nenhum dos dois          -> DUVIDOSO, marcado na galeria (132)

    Os 132 sao quase todos `*Group` (94), que sao agrupamentos do proprio GoodPrice.
    Nao afirmo que nao funcionam -- **afirmo que nao sao classe**, e por isso a
    galeria avisa em vez de esconder.
"""
import io, os
AQUI = os.path.dirname(os.path.abspath(__file__))
cls = {l.strip() for l in io.open(os.path.join(AQUI, "classes.txt"), encoding="utf-8") if l.strip()}
icones = sorted(f[:-4] for f in os.listdir(os.path.join(AQUI, "png")) if f.endswith(".png"))

reais, duvidosos = [], []
for n in icones:
    if n in cls: continue                                  # ja esta certo
    if n.endswith("Item") and n[:-4] in cls:
        reais.append((n, n[:-4]))                          # tirar o "Item"
    else:
        duvidosos.append(n)

io.open(os.path.join(AQUI, "nomes-reais.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join("%s|%s" % p for p in reais) + "\n")
io.open(os.path.join(AQUI, "duvidosos.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join(duvidosos) + "\n")
print("corrigidos (tirando 'Item'):", len(reais))
print("duvidosos (nao sao classe) :", len(duvidosos))
print("conferidos, usam o proprio nome:", len(icones) - len(reais) - len(duvidosos))
