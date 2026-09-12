# Fontes das páginas da Ecopedia BBC-Brasil (08/09/2026)

Regra (Raul): só orientação do autor do mod ou fato conferido no código instalado / em campo.
Nada deduzido. Textos brutos dos autores: `fontes-modio-bruto.txt` (páginas do mod.io, copiadas
pelo navegador) e `readmes-mods.txt` (READMEs dentro dos zips). Receitas: `receitas-servidor.txt`
(gerado por `extrair-receitas.py` em `/opt/eco/scripts-py/`, lendo `Mods/UserCode` do servidor).
Nomes de item para links `[XItem]`: `nomes-de-itens.txt` (1929, do servidor).

| Página | Fonte do texto | Receitas (profissão/nível/mesa) |
|---|---|---|
| **Parâmetros do servidor** (grupo Parametrizado) | `Configs/Difficulty.eco` (5.0 / 0.25 / 2.0 / ExhaustionEnabled false / MeteorImpactInDays 60 / DefensiveOnly / 5 papéis / SkillCostMultiplier 1.0), `Configs/Settlements.eco` (influência 45/150/2000; fundar/manter 1 cidadão, 0 cultura), `Configs/WorldGenerator.eco` (200x200, seed 2052209397; depósitos comparados com `WorldGenerator.eco.antes-minerio-2026-09-03_0645`: chance 2x, veio 1,5x — ferro/cobre/carvão/ouro), `Configs/Network.eco` (PublicServer true, senha vazia, DefaultSlots -1), `UserTextures.eco.template` (AutoApprovePrinterPictures false, sem .eco), `WhetstonesConfig.eco` 100, timer eco-reiniciar 03:55 SP | — |
| Tronco na mão (mod nosso) | `TreeObject.override.cs` gerado; campo 08/09 (carvalho 120: 100 na mão + 4x5 no chão; polpa do toco; resíduo na mochila) | — |
| Pedra na mão (mod nosso) | `PickaxeItem.override.cs`; campo 27/08 (4 por bloco, entulho se mão ocupada) | — |
| Pá com E (mod nosso) | `ShovelItem.override.cs` (KabongCapsPa 10/20/30/50, método CavarComE); jogo: MaxTake 1/3/5/10 nas 4 pás do `__core__` | — |
| Foice com E (mod nosso) | `BlockHarvestItem.override.cs`; SickleItem e ScytheItem herdam de BlockHarvestItem (`__core__/Tools`); campo 08/09 | — |
| Árvores densas (mod nosso) | `ArvoresDensas.cs` (md5 local = servidor), valores "era" nos comentários do próprio arquivo | — |
| Custo das estrelas (mod nosso) | `CustoEstrelas.cs` (Tabela.CustoBase, PenalidadeNovaArvore 1, PenalidadeAvancadaForaDaArvore 2); `/custoestrelas` no /help | — |
| Pergaminhos (mod nosso) | `NoMoreBooks.cs` OutputAmount=5, `PergaminhosDosMods.cs` (prova de vida), `Difficulty.eco` 5 papéis; campo 28/08 | — |
| Recompensa inicial (Starter Rewards) | `Configs/StarterRewards.eco` (OnlyOnFirstLogin true, 500 Real, 2 estrelas); campo 04-05/09 (`/starterrewards giveme`) | — |
| Eco Gnome | mod.io eco-gnome + campo 08/09 (Raul fez o fluxo inteiro) | — |
| GoodPrice | mod.io goodprice (descrição geral do autor); abas em campo. A página do mod.io já está na 5.5 e o servidor tem a 5.3 (catálogo §36.1), por isso a página NÃO cita recursos de versão (gráfico, avisos de preço) | — |
| Smart Storage | mod.io smart-storage + README.txt do zip 1.2.1 | — |
| Mercados | mod.io marketmod + `EcoPulse;Market.xml` do próprio mod; abas Eco Gnome/GoodPrice em campo (GnomeNosMercados.cs) | `EcoPulse/MarketMod/Objects/*.cs`: Workbench, skill 2 |
| Portões e Cercas | mod.io gates | `EcoPulse/Gates/**`: Carpentry 2 (portas), Blacksmith 2 Anvil (grades), Masonry 4/6 Masonry Table (pontes), Smelting 1 Anvil (cercas) |
| Hot Wheels | mod.io hot-wheels | `CavRnMods/HotWheels/**` (Jet Ski e Steam Paddle Craft: Shipwright **5** no código; o autor escreveu 2) |
| Molduras Grandes | mod.io bigger-frames | `CavRnMods/BiggerFrames/**`: Masonry 4 (Masonry Table), Carpentry 4/5, Blacksmith 4/6 |
| Mixology | mod.io mixology-140 | `Mixology 14.0.3/**` |
| Sorvetes | mod.io icecream | `IceCream/**`; mapa gerado com o mod (wipe 07/09 com mods carregados) |
| StorageMore | mod.io stockagemore-9 + Read-Me.txt | `StorageMore/StorageMore_English/StorageMore_English.cs` |
| Painéis de Anúncio | mod.io adsmod3 + Read-Me.txt (o autor diz Mesa de Mecânica; o código instalado usa Blacksmith Table 1/3/5 — usado o código); aprovação de imagem = `UserTextures.eco.template` AutoApprovePrinterPictures false (não há .eco, vale o template) | `adsmod/AdsMod_English/AdsMod_English.cs` |
| Posto de Gasolina | mod.io pumpgasmod-4 + Lisez-moi.txt | `pumpgasmod-brfm/**/PumpGas_English.cs` |
| Pedras de Afiar | mod.io whetstones + ChangeLog.txt; `Configs/WhetstonesConfig.eco` WhetstonesPercent 100 | `GadgetPaPa/Whetstones/Whetstones.cs` linhas 436-663 |
| Rejeitos | mod.io tailings-to-sand-clay-or-dirt + ChangeLog.txt | `GadgetPaPa/Tailings/*.cs` (Kiln Pottery 1 ×1; Incinerator Recycling 1 ×8) |
| Wolf Pack Utilities | mod.io wolf-pack-utilities + water-tower-eco-v13 | `WolfPackCustomMods/**` |
| Filtros de Poluição | mod.io air-pollution-filter-mod (texto completo do autor) | `PollutionFilterMod/FilterItems.cs` confere |
| Formas Extras | mod.io extrashapes | `ExtraShapes.cs` (6 Ashlar × Diagonal/ColumnQuarter) |
| Moinhos não industriais | mod.io waterwheel-windmill-not-industry | 4 `.override.cs` em `AutoGen/WorldObject` com receitas iguais ao jogo |
| Trator a Vapor minerador | mod.io early-skid-v11 | `Vehicles/SteamTractor.override.cs`, `AutoGen/Vehicle/SteamTractor.override.cs` |
| EcoPulse / EcoPulse;Market (tradução) | arquivos originais em `Mods/UserCode/Ecopedia/Mods/` | — |

## Fora, de propósito
- **Skills Requirements**: config ainda com os exemplos de fábrica → inerte; nada a explicar ao jogador.
- **Modular Storage Rack**: só `.unity3d`, sem código → nenhum item existe no jogo.
- **CivicsImportExport**: ferramenta de admin.
- **ColocarPlanta.cs, GnomeNosMercados.cs, KabongLog.cs**: ferramenta de admin / detalhe técnico (as abas dos mercados estão na página Mercados).
- Comandos do Eco Gnome além de `registeruser`/`join` (open, syncshop, createshop): listados pelo autor, não testados aqui → não entram.

## Divergências autor × código (usado o código instalado)
- Hot Wheels: Jet Ski e Steam Paddle Craft exigem Shipwright 5 (autor: 2).
- AdsMod: painéis na Blacksmith Table (autor: Mesa de Mecânica).
