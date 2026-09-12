// Servidor BBC-Brasil -- DOBRA o couro (Leather Hide) que o acougue entrega ao cortar os bichos.
// Autorizado pelo Raul em 10/09/2026: "pode mexer e dobrar a quantidade de couro por receita".
//
// ===================== O QUE MUDA =====================
//   ButcherTinyLeatherAnimalRecipe   couro 1 -> 2    peru, cao-da-pradaria, tartaruga
//   ButcherMediumAnimalRecipe        couro 1 -> 2    veado, alce, jacare, jaguar
//   ButcherMediumWoolyAnimalRecipe   couro 1 -> 2    cabra da montanha, bighorn
//   ButcherBisonRecipe               couro 2 -> 4    bisao
// Carne, la e pele NAO sao tocadas: o codigo troca so o elemento cujo Item.Type e LeatherHideItem.
// O CURTIMENTO (TanningLeatherRecipe, 2 peles -> 1 couro + 1 sebo, Butchery 5) ficou INTOCADO de
// proposito: ele nao e cortar bicho, e dobrar ali dobraria tambem o caminho da pele. Se um dia se
// quiser, e acrescentar uma quinta classe parcial aqui.
// Bicho que nao da couro nenhum, so pele, e portanto nao e afetado: coiote e raposa (SmallCarcass),
// agouti e lontra (TinyFurCarcass), lebre e lobo.
//
// ===================== POR QUE ASSIM =====================
// E o primeiro caminho da ordem de decisao oficial, e esta escrito no README que a Strange Loop
// distribui com o servidor (Mods/UserCode/README.md): "you want to change the Computer Lab recipe"
// -> criar arquivo, "copy namespace, using part and partial class name from the original file",
// e por as mudancas dentro de ModsPreInitialize(). O proprio arquivo gerado da receita reforca:
// "This is an auto-generated class. Don't modify it! ... Use Mods* partial methods instead".
// Os `using` abaixo sao COPIADOS INTEIROS do ButcherMediumAnimal.cs do jogo, como o README manda --
// e por nao ter feito isso que o servidor caiu duas vezes nesta semana (NotificationCategory em
// 08/09, Singleton<> em 10/09).
//
// Conferido antes de escrever:
//   - as 8 receitas Butcher* DECLARAM `partial void ModsPreInitialize();` e NINGUEM implementa em
//     __core__ nem em UserCode -- gancho livre, sem risco de CS0111 hoje;
//   - o gancho e chamado no construtor ANTES de Initialize(), entao mexer em Recipes[0].Products vale;
//   - `Recipe.Products` e `public List<CraftingElement>` (docs.play.eco): o `protected set` so impede
//     trocar a lista inteira; Clear/Add/[i]= funcionam;
//   - `CraftingElement` e abstrata, quem se instancia e `CraftingElement<T>`;
//   - ler `Item.Type` de um produto e o que o proprio jogo faz em
//     __core__/Commands/TechTreeSimCommands.cs:238 (`recipe.Products.Select(x => x.Item.Type)`);
//   - mesma tecnica que ja roda aqui em PergaminhosDosMods.cs e no mod No More Books.
//
// Nao existe caminho de config: varredura em todos os .eco e .template achou so
// CraftResourceMultiplier, que mexe no CUSTO em ingredientes, nao na producao.
// O jogo tem um sistema de bonus de rendimento (BonusAction.Yield) e ja o usa no acougue -- o talento
// Local Fauna, Butchery 3, da +1 em quatro receitas de abate -- mas bonus vem de TALENTO, e por
// jogador e opcional, nao serve para valer para todos. Quem tiver Local Fauna soma as duas coisas.
//
// Valor ABSOLUTO, nunca multiplicando o que estiver la: rodar duas vezes da o mesmo resultado, e a
// licao da pa (nenhum multiplicador escondido; o original fica escrito ao lado).
// Prova de vida: /opt/eco/couro-vida.txt, uma linha por receita a cada arranque.
// REGRA 18: instalar SO imediatamente antes de um reinicio que alguem vai VIGIAR.
namespace Eco.Mods.TechTree
{
    using System;
    using System.Collections.Generic;
    using Eco.Gameplay.Components;
    using Eco.Gameplay.DynamicValues;
    using Eco.Gameplay.Items;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Skills;
    using Eco.Shared.Utils;
    using Eco.World;
    using Eco.World.Blocks;
    using Gameplay.Systems.TextLinks;
    using Eco.Shared.Localization;
    using Eco.Core.Controller;
    using Eco.Gameplay.Settlements.ClaimStakes;
    using Eco.Gameplay.Items.Recipes;
    using Eco.Gameplay.Garbage;

    /// <summary>Servidor BBC-Brasil: troca a quantidade de couro nas receitas de acougue.</summary>
    public static class CouroBBC
    {
        /// <summary>Quantas vezes o couro do jogo. AJUSTE AQUI.</summary>
        public const int Fator = 2;

        static readonly object trava = new object();

        /// <summary>
        /// Troca o elemento de couro da lista de produtos por um de (couroDoJogo * Fator).
        /// Nao toca em nenhum outro produto. Anota no diario o que fez, ou reclama se nao achou couro.
        /// </summary>
        public static void Dobra(List<CraftingElement> produtos, string receita, int couroDoJogo)
        {
            var achou = 0;
            for (var i = 0; i < produtos.Count; i++)
            {
                if (produtos[i].Item == null || produtos[i].Item.Type != typeof(LeatherHideItem)) continue;
                produtos[i] = new CraftingElement<LeatherHideItem>(couroDoJogo * Fator);
                achou++;
            }
            if (achou == 1)
                Anota(receita + ": couro " + couroDoJogo + " -> " + (couroDoJogo * Fator));
            else
                Anota(receita + ": [!!] achei " + achou + " elemento(s) de couro, esperava 1 -- nada garantido");
        }

        static void Anota(string texto)
        {
            try
            {
                lock (trava)
                {
                    System.IO.File.AppendAllText("/opt/eco/couro-vida.txt",
                        System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\n");
                }
            }
            catch { }
        }
    }

    public partial class ButcherTinyLeatherAnimalRecipe
    {
        partial void ModsPreInitialize()
        {
            // jogo: 1 carne crua + 1 couro
            CouroBBC.Dobra(this.Recipes[0].Products, "ButcherTinyLeatherAnimal", 1);
        }
    }

    public partial class ButcherMediumAnimalRecipe
    {
        partial void ModsPreInitialize()
        {
            // jogo: 5 carne crua + 1 couro
            CouroBBC.Dobra(this.Recipes[0].Products, "ButcherMediumAnimal", 1);
        }
    }

    public partial class ButcherMediumWoolyAnimalRecipe
    {
        partial void ModsPreInitialize()
        {
            // jogo: 5 carne crua + 1 couro + 2 la
            CouroBBC.Dobra(this.Recipes[0].Products, "ButcherMediumWoolyAnimal", 1);
        }
    }

    public partial class ButcherBisonRecipe
    {
        partial void ModsPreInitialize()
        {
            // jogo: 10 carne crua + 2 couro + 3 la
            CouroBBC.Dobra(this.Recipes[0].Products, "ButcherBison", 2);
        }
    }
}
