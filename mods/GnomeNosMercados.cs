// GnomeNosMercados.cs -- Servidor Kabong Brasil, 08/09/2026
//
// Poe as abas "Eco Gnome" E "GoodPrice" nos 8 mercados do MarketMod (EcoPulse).
//
// POR QUE: o Eco Gnome so anexa o seu componente a StoreObject e WoodShopCartObject
// (StoreObject.cs do mod, duas linhas [RequireComponent(typeof(EcoGnomeComponent))]).
// O Carpenter Market e os outros 7 mercados sao objetos do MarketMod, com StoreComponent
// (herdado de SimpleMarketObjectBase / FoodMarketObjectBase), mas sem a aba. Pedido do
// Raul: "na minha Carpenter Market nao tem essa aba do Gnome".
//
// COMO: as 8 classes sao 'public partial class XMarketObject' em Eco.Mods.TechTree, e
// atributo em UMA parte de classe partial vale para a classe inteira -- e exatamente o
// que o proprio Eco Gnome faz com StoreObject. Nenhum arquivo do MarketMod ou do Eco
// Gnome e tocado; apagar este arquivo desfaz.
//
// GOODPRICE, idem (08/09): GoodPrice_Store_Sync/GoodPriceStoreObject.cs so exige o
// GoodPriceSyncComponent em StoreObject e WoodShopCartObject; a classe do componente e
// public, em Eco.Mods.TechTree, compilada junto com este arquivo.
//
// DEPENDE de: MarketMod (as classes), Eco Gnome (EcoGnomeComponent, no StoreObject.cs) e
// GoodPrice (GoodPriceSyncComponent, no GoodPriceStoreObject.cs).
// Se um dos dois sair, isto nao compila -- quebra ALTO no arranque (o tipo bom de falha).
// Se o MarketMod passar a trazer a aba por conta propria, o atributo repetido e inofensivo
// (RequireComponent do mesmo componente duas vezes nao duplica o componente).
//
// A CONFERIR EM CAMPO: mercado JA colocado no mundo ganha a aba ao recarregar, ou so
// mercado novo? Se so novo: pegar e recolocar o mercado.

namespace Eco.Mods.TechTree
{
    using Eco.Gameplay.Objects;

    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class CarpenterMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class ChefMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class EngineerMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class FarmerMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class HunterMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class MasonMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class SmithMarketObject {}
    [RequireComponent(typeof(EcoGnomeComponent))] [RequireComponent(typeof(GoodPriceSyncComponent))] public partial class TailorMarketObject {}
}
