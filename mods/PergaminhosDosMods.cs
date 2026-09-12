// PergaminhosDosMods.cs -- Servidor Kabong Brasil
//
// O QUE FAZ
//   Estende o efeito do mod "No More Books" para as TRES profissoes de mod que ele nao
//   cobre: Mixology, Advanced Mixology e IceCream. A mesa de pesquisa passa a produzir
//   PERGAMINHOS em vez do livro, na mesma quantidade das outras.
//
// POR QUE ESTA AQUI E NAO DENTRO DO No More Books
//   Editar o arquivo de um mod de terceiro funciona, mas a mudanca MORRE na proxima
//   atualizacao do mod, e em silencio. Aqui ela sobrevive.
//   O risco oposto e conhecido e aceito: se um dia o autor do No More Books passar a
//   cobrir estas tres, havera DUAS implementacoes do mesmo metodo parcial e o servidor
//   nao compila (CS0111). Isso quebra ALTO, no arranque, que e o tipo bom de falha -
//   e apagar este arquivo resolve. Risco baixo: sao profissoes de mods de outros autores.
//
// COMO FUNCIONA
//   O Eco gera cada receita com um gancho vazio, `partial void ModsPreInitialize();`,
//   feito para isto - e o README do UserCode recomenda esta forma em vez de .override.cs.
//   Conferido antes de escrever: as tres classes DECLARAM o gancho e NENHUMA implementa,
//   entao nao ha colisao.
//
//   A quantidade vem de NMBSettings.OutputAmount, do proprio No More Books (classe
//   publica, mesmo namespace). Fica UM knob so para as 31 receitas, em vez de dois que
//   poderiam divergir. Se o mod for atualizado e a constante voltar a 1, estas tres
//   voltam a 1 junto - coerente, e o aviso esta na secao 16 do CLAUDE.md.
//
//   Nao mexemos nos ingredientes. As 28 receitas do No More Books usam modificador 1.0,
//   ou seja custo inalterado; e o dicionario IngredientModifiers dele NAO tem as nossas
//   tres, entao indexa-lo daria KeyNotFoundException.

namespace Eco.Mods.TechTree
{
    using Eco.Core.Items;
    using Eco.Gameplay.Items;
    using Eco.Gameplay.Items.Recipes;
    using System;

    /// <summary>Prova de vida: sem isto nao ha como saber se os ganchos rodaram.</summary>
    internal static class PergaminhosDosModsDiario
    {
        public const string Arquivo = @"/opt/eco/pergaminhos-mods-vida.txt";

        public static void Anota(string receita, int quantidade, string pergaminho)
        {
            try
            {
                System.IO.File.AppendAllText(Arquivo,
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + receita
                    + " -> " + quantidade + "x " + pergaminho + "\r\n");
            }
            catch { }
        }
    }

    public partial class MixologySkillBookRecipe
    {
        partial void ModsPreInitialize()
        {
            this.Recipes[0].Products.Clear();
            this.Recipes[0].Products.Add(new CraftingElement<MixologySkillScroll>(NMBSettings.OutputAmount));
            PergaminhosDosModsDiario.Anota("Mixology", NMBSettings.OutputAmount, "MixologySkillScroll");
        }
    }

    public partial class AdvancedMixologySkillBookRecipe
    {
        partial void ModsPreInitialize()
        {
            this.Recipes[0].Products.Clear();
            this.Recipes[0].Products.Add(new CraftingElement<AdvancedMixologySkillScroll>(NMBSettings.OutputAmount));
            PergaminhosDosModsDiario.Anota("Advanced Mixology", NMBSettings.OutputAmount, "AdvancedMixologySkillScroll");
        }
    }

    public partial class IceCreamSkillBookRecipe
    {
        partial void ModsPreInitialize()
        {
            this.Recipes[0].Products.Clear();
            this.Recipes[0].Products.Add(new CraftingElement<IceCreamSkillScroll>(NMBSettings.OutputAmount));
            PergaminhosDosModsDiario.Anota("IceCream", NMBSettings.OutputAmount, "IceCreamSkillScroll");
        }
    }
}
