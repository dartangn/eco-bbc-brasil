# -*- coding: utf-8 -*-
"""Nome em ingles de cada categoria da galeria.

A CHAVE continua sendo o nome em portugues -- e ele que esta no `data-cat` de cada
icone e no `categorias.txt`. So o RÓTULO muda de idioma. Assim trocar de lingua nao
mexe em filtro, em arquivo gerado nem em nada que ja esteja salvo.
"""
import io, os
EN = {
 "Móveis e decoração":"Furniture & decoration", "Comida":"Food",
 "Placas e letreiros":"Signs & banners", "Diversos":"Miscellaneous",
 "Outros objetos":"Other objects", "Grupos de item":"Item groups",
 "Roupas":"Clothing", "Melhorias":"Upgrades", "Mesas de fabricação":"Crafting tables",
 "Ferramentas":"Tools", "Sementes":"Seeds", "Armazenamento":"Storage",
 "Peças":"Parts", "Terra e rocha":"Dirt & rock", "Profissões":"Professions",
 "Blocos e construção":"Blocks & building", "Plantação":"Crops",
 "Combustível":"Fuel", "Veículos e barcos":"Vehicles & boats",
 "Pesquisa":"Research", "Governo":"Government", "Moeda":"Currency",
 "Plantas decorativas":"Decorative plants", "Madeira":"Wood", "Ração":"Animal feed",
 "Adubo":"Fertiliser", "Módulos":"Modules", "Lixo e sucata":"Garbage & scrap",
 "Peixes":"Fish", "Energia":"Power", "Mochilas":"Backpacks", "Fibra":"Fibre",
 "Lojas":"Shops", "Caça e carcaças":"Hunting & carcasses",
 "Comida crua":"Raw food", "Colheita":"Foraging",
}
AQUI = os.path.dirname(os.path.abspath(__file__))
usadas = {l.rstrip().split("|")[1] for l in io.open(os.path.join(AQUI, "categorias.txt"), encoding="utf-8") if "|" in l}
faltam = sorted(usadas - set(EN))
io.open(os.path.join(AQUI, "categorias-en.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join("%s|%s" % (k, v) for k, v in sorted(EN.items())) + "\n")
print("traducoes:", len(EN), " categorias em uso:", len(usadas))
print("SEM traducao:", faltam if faltam else "nenhuma")
