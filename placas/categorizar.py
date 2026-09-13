# -*- coding: utf-8 -*-
"""Da uma categoria a cada icone da galeria de placas.

POR QUE A PRIMEIRA VERSAO ERA RUIM
    Eu classifiquei por TAG, e as tags do Eco nao descrevem o que a coisa e.
    A tag `Mountable` parecia "veiculo": das 106 que a tem, 94 sao CADEIRAS e BANCOS
    (montavel porque voce senta) e 12 sao objetos de governo -- veiculo, nenhum.
    E "Objetos do mundo" virou um balde com movel dentro.

O CRITERIO AGORA
    O que o objeto FAZ, lido dos [RequireComponent] que o proprio jogo pendura nele.
    Item -> WorldObjectItem<XObject> -> componentes de XObject.
    A ORDEM importa: mesa de fabricacao tambem da moradia e tambem consome energia,
    entao a funcao especifica vem primeiro e HousingComponent fica por ultimo, que e
    o papel real dele -- "isto conta como mobilia".

    Quem nao e objeto (minerio, comida, ferramenta, semente, roupa) continua pelas
    tags, que ali descrevem bem.
"""
import io, os, re, collections

AQUI = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------- objetos: pelo que eles FAZEM
POR_COMPONENTE = [
    (("VehicleComponent", "BoatComponent"),                     "Veículos e barcos"),
    (("CraftingComponent",),                                    "Mesas de fabricação"),
    (("StoreComponent",),                                       "Lojas"),
    (("ModularStockpileComponent", "PublicStorageComponent"),   "Armazenamento"),
    (("PerformCivicActionComponent", "JurisdictionComponent"),  "Governo"),
    (("FakePlantComponent",),                                   "Plantas decorativas"),
    (("CustomTextComponent",),                                  "Placas e letreiros"),
    (("HousingComponent",),                                     "Móveis e decoração"),
    (("PowerGridComponent", "PowerConsumptionComponent",
      "FuelSupplyComponent"),                                   "Energia"),
]
# --------------------------------------------------- nao-objetos: pelas tags
POR_TAG = [
    ("Crop Seed", "Sementes"), ("Crop", "Plantação"), ("Raw Food", "Comida crua"),
    ("Fish", "Peixes"), ("Tool", "Ferramentas"), ("Clothes", "Roupas"),
    ("Currency", "Moeda"), ("Research", "Pesquisa"), ("Advanced Research", "Pesquisa"),
    ("Burnable Fuel", "Combustível"), ("Fuel", "Combustível"),
    ("Wood", "Madeira"), ("CompositeLumber", "Madeira"),
    ("Excavatable", "Terra e rocha"), ("CrushedRock", "Terra e rocha"),
    ("Garbage", "Lixo e sucata"), ("Fertilizer", "Adubo"),
    ("HerbivoreFeed", "Ração"), ("NaturalFiber", "Fibra"),
    ("Harvestable", "Colheita"), ("Upgrade", "Melhorias"),
    ("SpecialtyModule", "Módulos"), ("Constructable", "Blocos e construção"),
]
POR_MAE = {
    "FoodItem": "Comida", "SeedItem": "Sementes", "PartItem": "Peças",
    "ModuleItem": "Módulos", "ToolItem": "Ferramentas", "BlockItem": "Blocos e construção",
    "PaintToolItem": "Ferramentas", "ClothingItem": "Roupas",
    "SettlementFoundationItem": "Governo", "SettlementClaimStakeItem": "Governo",
    "UniqueSettlementCivicItem": "Governo",
}
REPRESENTANTE = {
    "Móveis e decoração": "WoodenChairItem", "Mesas de fabricação": "CarpentryTableItem",
    "Veículos e barcos": "WoodenCartItem", "Lojas": "StoreItem",
    "Armazenamento": "WoodenStorageChestItem", "Governo": "TownFoundationItem",
    "Energia": "SteamEngineItem", "Placas e letreiros": "WoodenSignItem",
    "Plantas decorativas": "FlowerPotItem", "Outros objetos": "StreetLampItem",
    "Comida": "CampfireStewItem", "Comida crua": "RawMeatItem", "Peixes": "SalmonItem",
    "Sementes": "CornSeedItem", "Plantação": "CornItem", "Colheita": "HuckleberriesItem",
    "Ferramentas": "IronHammerItem", "Roupas": "WorkBootsItem", "Peças": "IronGearItem",
    "Blocos e construção": "MortaredStoneItem", "Terra e rocha": "StoneItem",
    "Madeira": "LumberItem", "Combustível": "CoalItem", "Lixo e sucata": "WoodScrapItem",
    "Melhorias": "BasicUpgradeItem", "Módulos": "AdvancedUpgradeItem",
    "Pesquisa": "ResearchPaperBasicItem", "Moeda": "PaperItem", "Adubo": "CompostItem",
    "Ração": "WheatItem", "Fibra": "PlantFibersItem", "Profissões": "CarpentrySkillItem",
    "Grupos de item": "BlockGroup", "Caça e carcaças": "RawMeatItem", "Mochilas": "BackpackItem", "Diversos": "RockItem",
}

objc = {}
for l in io.open(os.path.join(AQUI, "objcomp.txt"), encoding="utf-8"):
    p = l.rstrip().split("|")
    if len(p) == 2: objc[p[0]] = set(p[1].split(";"))

itens = {}
for l in io.open(os.path.join(AQUI, "itens2.txt"), encoding="utf-8"):
    p = l.rstrip().split("|")
    if len(p) < 4: continue
    itens[p[0]] = {"mae": p[2], "tags": set(t for t in p[3].split(";") if t)}

rx_obj = re.compile(r'WorldObjectItem<\s*([A-Za-z0-9_]+)')
nomes = sorted(f[:-4] for f in os.listdir(os.path.join(AQUI, "png")) if f.endswith(".png"))

def categoria(n):
    d = itens.get(n)
    if d:
        m = rx_obj.search(d["mae"])
        if m:                                   # e um OBJETO do mundo
            comps = objc.get(m.group(1), set())
            for chaves, cat in POR_COMPONENTE:
                if comps & set(chaves): return cat
            return "Outros objetos"
        for tag, cat in POR_TAG:                # nao e objeto: vale a tag
            if tag in d["tags"]: return cat
        mae = d["mae"].split("<")[0].strip()
        if mae in POR_MAE: return POR_MAE[mae]
    # Ultima camada, pelo NOME. Existe porque 157 icones caiam em "Diversos" so por
    # nao terem tag: carcaca de caca e boa parte das roupas de mod nao declaram nenhuma.
    if n.endswith("CarcassItem"): return "Caça e carcaças"
    if any(k in n for k in ("Hat", "Shirt", "Pants", "Boots", "Shoes", "Glasses",
                            "Cloak", "Flipflops", "Gloves", "Skirt", "Dress",
                            "Jacket", "Coat", "Shorts", "Helmet")): return "Roupas"
    if n.endswith("Group"): return "Grupos de item"
    if n.endswith("SkillItem") or n.endswith("Skill"): return "Profissões"
    if "Backpack" in n or "Bag" in n: return "Mochilas"
    return "Diversos"

linhas = ["%s|%s" % (n, categoria(n)) for n in nomes]
io.open(os.path.join(AQUI, "categorias.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(linhas) + "\n")
io.open(os.path.join(AQUI, "representantes.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join("%s|%s" % (a, b) for a, b in sorted(REPRESENTANTE.items())) + "\n")

c = collections.Counter(l.split("|")[1] for l in linhas)
print("icones:", len(linhas), " categorias:", len(c))
for cat, q in c.most_common(): print("   %-24s %4d" % (cat, q))
