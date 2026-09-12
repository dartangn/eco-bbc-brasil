// ============================================================================
// LivroDaProfissao.cs  --  Servidor Kabong Brasil / BBC-Brasil
// GERADO por gerar-livros-profissao.py -- NAO EDITE A MAO.
//
// UMA receita nova por livro de profissao, no LABORATORIO (a mesa de pesquisa
// avancada do jogo: exige Mechanics 1, sala nivel 2.8 e 24 m3), custando
// 10000 pergaminhos da mesma profissao.
//
// POR QUE: neste servidor nenhuma receita produz o item SkillBook -- o No More
// Books trocou o produto das 28 receitas de livro do jogo por pergaminhos, e o
// nosso PergaminhosDosMods.cs fez o mesmo nas 3 de mod. Sem livro como produto
// de receita, a tela de habilidades (Z) nao deixa clicar em especialidade nao
// descoberta, e o jogador nao ve o que a profissao faz antes de gastar estrela.
// Em servidor vanilla e clicavel (comparado em video pelo Raul, 11/09/2026).
//
// 10000 pergaminhos e inalcancavel DE PROPOSITO: o livro volta a existir como
// produto de receita sem voltar a ser fabricavel. O pergaminho continua sendo o
// que sai na pratica, e nenhuma receita existente foi alterada.
//
// O destrave de cada receita e o MESMO que o jogo usa na receita de livro dela
// (Assados por Milling 1, Cozimento por Butchery 1, e assim por diante).
//
// Classes SEM `partial`: sao novas e so existem aqui. `partial` num nome novo
// faria o compilador aceitar em silencio uma classe vazia se houvesse erro de
// digitacao -- foi o pre-voo que apontou isso em 11/09/2026.
//
// Reverter: apagar este arquivo.
// ============================================================================

namespace Eco.Mods.TechTree
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Linq;
    using Eco.Core.Items;
    using Eco.Core.Utils;
    using Eco.Core.Utils.AtomicAction;
    using Eco.Gameplay.Blocks;
    using Eco.Gameplay.Components;
    using Eco.Gameplay.DynamicValues;
    using Eco.Gameplay.Items;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Property;
    using Eco.Gameplay.Skills;
    using Eco.Gameplay.Systems;
    using Eco.Gameplay.Systems.TextLinks;
    using Eco.Shared.Localization;
    using Eco.Shared.Serialization;
    using Eco.Shared.Services;
    using Eco.Shared.Utils;
    using Eco.Gameplay.Systems.NewTooltip;
    using Eco.Core.Controller;
    using Eco.Gameplay.Items.Recipes;
    using Eco.Gameplay.Garbage;

    /// <summary>Prova de vida em arquivo: compilar nao e funcionar, e carregar nao e funcionar.</summary>
    public static class KabongLivroDiario
    {
        private const string Diario = "/opt/eco/livro-profissao-vida.txt";
        private static readonly object Tranca = new object();
        public static int Registradas;

        public static void Anota(string texto)
        {
            try
            {
                lock (Tranca)
                {
                    Registradas++;
                    System.IO.File.AppendAllText(Diario,
                        DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\n");
                }
            }
            catch { }
        }
    }

    [RequiresSkill(typeof(BakingSkill), 1)]
    public class LivroAdvancedBakingKabongRecipe : RecipeFamily
    {
        public LivroAdvancedBakingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroAdvancedBakingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Advanced Baking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(AdvancedBakingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<AdvancedBakingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(BakingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroAdvancedBakingKabongRecipe), start: 15, skillType: typeof(BakingSkill));
            this.Initialize(displayText: Localizer.DoStr("Advanced Baking Skill Book"), recipeType: typeof(LivroAdvancedBakingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("AdvancedBakingSkillBook <- 10000x AdvancedBakingSkillScroll");
        }
    }

    [RequiresSkill(typeof(CookingSkill), 1)]
    public class LivroAdvancedCookingKabongRecipe : RecipeFamily
    {
        public LivroAdvancedCookingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroAdvancedCookingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Advanced Cooking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(AdvancedCookingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<AdvancedCookingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(CookingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroAdvancedCookingKabongRecipe), start: 15, skillType: typeof(CookingSkill));
            this.Initialize(displayText: Localizer.DoStr("Advanced Cooking Skill Book"), recipeType: typeof(LivroAdvancedCookingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("AdvancedCookingSkillBook <- 10000x AdvancedCookingSkillScroll");
        }
    }

    [RequiresSkill(typeof(PotterySkill), 1)]
    public class LivroAdvancedMasonryKabongRecipe : RecipeFamily
    {
        public LivroAdvancedMasonryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroAdvancedMasonryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Advanced Masonry Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(AdvancedMasonrySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<AdvancedMasonrySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(PotterySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroAdvancedMasonryKabongRecipe), start: 15, skillType: typeof(PotterySkill));
            this.Initialize(displayText: Localizer.DoStr("Advanced Masonry Skill Book"), recipeType: typeof(LivroAdvancedMasonryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("AdvancedMasonrySkillBook <- 10000x AdvancedMasonrySkillScroll");
        }
    }

    [RequiresSkill(typeof(MixologySkill), 1)]
    public class LivroAdvancedMixologyKabongRecipe : RecipeFamily
    {
        public LivroAdvancedMixologyKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroAdvancedMixologyKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Advanced Mixology Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(AdvancedMixologySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<AdvancedMixologySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MixologySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroAdvancedMixologyKabongRecipe), start: 15, skillType: typeof(MixologySkill));
            this.Initialize(displayText: Localizer.DoStr("Advanced Mixology Skill Book"), recipeType: typeof(LivroAdvancedMixologyKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("AdvancedMixologySkillBook <- 10000x AdvancedMixologySkillScroll");
        }
    }

    [RequiresSkill(typeof(SmeltingSkill), 1)]
    public class LivroAdvancedSmeltingKabongRecipe : RecipeFamily
    {
        public LivroAdvancedSmeltingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroAdvancedSmeltingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Advanced Smelting Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(AdvancedSmeltingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<AdvancedSmeltingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(SmeltingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroAdvancedSmeltingKabongRecipe), start: 15, skillType: typeof(SmeltingSkill));
            this.Initialize(displayText: Localizer.DoStr("Advanced Smelting Skill Book"), recipeType: typeof(LivroAdvancedSmeltingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("AdvancedSmeltingSkillBook <- 10000x AdvancedSmeltingSkillScroll");
        }
    }

    [RequiresSkill(typeof(MillingSkill), 1)]
    public class LivroBakingKabongRecipe : RecipeFamily
    {
        public LivroBakingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroBakingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Baking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(BakingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<BakingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MillingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroBakingKabongRecipe), start: 15, skillType: typeof(MillingSkill));
            this.Initialize(displayText: Localizer.DoStr("Baking Skill Book"), recipeType: typeof(LivroBakingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("BakingSkillBook <- 10000x BakingSkillScroll");
        }
    }

    [RequiresSkill(typeof(LoggingSkill), 1)]
    public class LivroBasicEngineeringKabongRecipe : RecipeFamily
    {
        public LivroBasicEngineeringKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroBasicEngineeringKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Basic Engineering Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(BasicEngineeringSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<BasicEngineeringSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(LoggingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroBasicEngineeringKabongRecipe), start: 15, skillType: typeof(LoggingSkill));
            this.Initialize(displayText: Localizer.DoStr("Basic Engineering Skill Book"), recipeType: typeof(LivroBasicEngineeringKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("BasicEngineeringSkillBook <- 10000x BasicEngineeringSkillScroll");
        }
    }

    [RequiresSkill(typeof(SmeltingSkill), 1)]
    public class LivroBlacksmithKabongRecipe : RecipeFamily
    {
        public LivroBlacksmithKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroBlacksmithKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Blacksmith Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(BlacksmithSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<BlacksmithSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(SmeltingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroBlacksmithKabongRecipe), start: 15, skillType: typeof(SmeltingSkill));
            this.Initialize(displayText: Localizer.DoStr("Blacksmith Skill Book"), recipeType: typeof(LivroBlacksmithKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("BlacksmithSkillBook <- 10000x BlacksmithSkillScroll");
        }
    }

    [RequiresSkill(typeof(HuntingSkill), 1)]
    public class LivroButcheryKabongRecipe : RecipeFamily
    {
        public LivroButcheryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroButcheryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Butchery Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(ButcherySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<ButcherySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(HuntingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroButcheryKabongRecipe), start: 15, skillType: typeof(HuntingSkill));
            this.Initialize(displayText: Localizer.DoStr("Butchery Skill Book"), recipeType: typeof(LivroButcheryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("ButcherySkillBook <- 10000x ButcherySkillScroll");
        }
    }

    [RequiresSkill(typeof(LoggingSkill), 1)]
    public class LivroCarpentryKabongRecipe : RecipeFamily
    {
        public LivroCarpentryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroCarpentryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Carpentry Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(CarpentrySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<CarpentrySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(LoggingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroCarpentryKabongRecipe), start: 15, skillType: typeof(LoggingSkill));
            this.Initialize(displayText: Localizer.DoStr("Carpentry Skill Book"), recipeType: typeof(LivroCarpentryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("CarpentrySkillBook <- 10000x CarpentrySkillScroll");
        }
    }

    [RequiresSkill(typeof(CarpentrySkill), 1)]
    public class LivroCompositesKabongRecipe : RecipeFamily
    {
        public LivroCompositesKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroCompositesKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Composites Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(CompositesSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<CompositesSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(CarpentrySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroCompositesKabongRecipe), start: 15, skillType: typeof(CarpentrySkill));
            this.Initialize(displayText: Localizer.DoStr("Composites Skill Book"), recipeType: typeof(LivroCompositesKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("CompositesSkillBook <- 10000x CompositesSkillScroll");
        }
    }

    [RequiresSkill(typeof(ButcherySkill), 1)]
    public class LivroCookingKabongRecipe : RecipeFamily
    {
        public LivroCookingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroCookingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Cooking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(CookingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<CookingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(ButcherySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroCookingKabongRecipe), start: 15, skillType: typeof(ButcherySkill));
            this.Initialize(displayText: Localizer.DoStr("Cooking Skill Book"), recipeType: typeof(LivroCookingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("CookingSkillBook <- 10000x CookingSkillScroll");
        }
    }

    [RequiresSkill(typeof(AdvancedCookingSkill), 1)]
    public class LivroCuttingEdgeCookingKabongRecipe : RecipeFamily
    {
        public LivroCuttingEdgeCookingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroCuttingEdgeCookingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Cutting Edge Cooking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(CuttingEdgeCookingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<CuttingEdgeCookingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(AdvancedCookingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroCuttingEdgeCookingKabongRecipe), start: 15, skillType: typeof(AdvancedCookingSkill));
            this.Initialize(displayText: Localizer.DoStr("Cutting Edge Cooking Skill Book"), recipeType: typeof(LivroCuttingEdgeCookingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("CuttingEdgeCookingSkillBook <- 10000x CuttingEdgeCookingSkillScroll");
        }
    }

    [RequiresSkill(typeof(MechanicsSkill), 1)]
    public class LivroElectronicsKabongRecipe : RecipeFamily
    {
        public LivroElectronicsKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroElectronicsKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Electronics Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(ElectronicsSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<ElectronicsSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MechanicsSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroElectronicsKabongRecipe), start: 15, skillType: typeof(MechanicsSkill));
            this.Initialize(displayText: Localizer.DoStr("Electronics Skill Book"), recipeType: typeof(LivroElectronicsKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("ElectronicsSkillBook <- 10000x ElectronicsSkillScroll");
        }
    }

    [RequiresSkill(typeof(GatheringSkill), 1)]
    public class LivroFarmingKabongRecipe : RecipeFamily
    {
        public LivroFarmingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroFarmingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Farming Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(FarmingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<FarmingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(GatheringSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroFarmingKabongRecipe), start: 15, skillType: typeof(GatheringSkill));
            this.Initialize(displayText: Localizer.DoStr("Farming Skill Book"), recipeType: typeof(LivroFarmingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("FarmingSkillBook <- 10000x FarmingSkillScroll");
        }
    }

    [RequiresSkill(typeof(FarmingSkill), 1)]
    public class LivroFertilizersKabongRecipe : RecipeFamily
    {
        public LivroFertilizersKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroFertilizersKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Fertilizers Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(FertilizersSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<FertilizersSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(FarmingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroFertilizersKabongRecipe), start: 15, skillType: typeof(FarmingSkill));
            this.Initialize(displayText: Localizer.DoStr("Fertilizers Skill Book"), recipeType: typeof(LivroFertilizersKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("FertilizersSkillBook <- 10000x FertilizersSkillScroll");
        }
    }

    [RequiresSkill(typeof(MasonrySkill), 1)]
    public class LivroGlassworkingKabongRecipe : RecipeFamily
    {
        public LivroGlassworkingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroGlassworkingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Glassworking Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(GlassworkingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<GlassworkingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MasonrySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroGlassworkingKabongRecipe), start: 15, skillType: typeof(MasonrySkill));
            this.Initialize(displayText: Localizer.DoStr("Glassworking Skill Book"), recipeType: typeof(LivroGlassworkingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("GlassworkingSkillBook <- 10000x GlassworkingSkillScroll");
        }
    }

    [RequiresSkill(typeof(BasicEngineeringSkill), 1)]
    public class LivroIceCreamKabongRecipe : RecipeFamily
    {
        public LivroIceCreamKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroIceCreamKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Ice Cream Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(IceCreamSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<IceCreamSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(BasicEngineeringSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroIceCreamKabongRecipe), start: 15, skillType: typeof(BasicEngineeringSkill));
            this.Initialize(displayText: Localizer.DoStr("Ice Cream Skill Book"), recipeType: typeof(LivroIceCreamKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("IceCreamSkillBook <- 10000x IceCreamSkillScroll");
        }
    }

    [RequiresSkill(typeof(MechanicsSkill), 1)]
    public class LivroIndustryKabongRecipe : RecipeFamily
    {
        public LivroIndustryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroIndustryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Industry Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(IndustrySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<IndustrySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MechanicsSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroIndustryKabongRecipe), start: 15, skillType: typeof(MechanicsSkill));
            this.Initialize(displayText: Localizer.DoStr("Industry Skill Book"), recipeType: typeof(LivroIndustryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("IndustrySkillBook <- 10000x IndustrySkillScroll");
        }
    }

    [RequiresSkill(typeof(MiningSkill), 1)]
    public class LivroMasonryKabongRecipe : RecipeFamily
    {
        public LivroMasonryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroMasonryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Masonry Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(MasonrySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<MasonrySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MiningSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroMasonryKabongRecipe), start: 15, skillType: typeof(MiningSkill));
            this.Initialize(displayText: Localizer.DoStr("Masonry Skill Book"), recipeType: typeof(LivroMasonryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("MasonrySkillBook <- 10000x MasonrySkillScroll");
        }
    }

    [RequiresSkill(typeof(BasicEngineeringSkill), 1)]
    public class LivroMechanicsKabongRecipe : RecipeFamily
    {
        public LivroMechanicsKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroMechanicsKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Mechanics Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(MechanicsSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<MechanicsSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(BasicEngineeringSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroMechanicsKabongRecipe), start: 15, skillType: typeof(BasicEngineeringSkill));
            this.Initialize(displayText: Localizer.DoStr("Mechanics Skill Book"), recipeType: typeof(LivroMechanicsKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("MechanicsSkillBook <- 10000x MechanicsSkillScroll");
        }
    }

    [RequiresSkill(typeof(FarmingSkill), 1)]
    public class LivroMillingKabongRecipe : RecipeFamily
    {
        public LivroMillingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroMillingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Milling Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(MillingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<MillingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(FarmingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroMillingKabongRecipe), start: 15, skillType: typeof(FarmingSkill));
            this.Initialize(displayText: Localizer.DoStr("Milling Skill Book"), recipeType: typeof(LivroMillingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("MillingSkillBook <- 10000x MillingSkillScroll");
        }
    }

    [RequiresSkill(typeof(CampfireCookingSkill), 1)]
    public class LivroMixologyKabongRecipe : RecipeFamily
    {
        public LivroMixologyKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroMixologyKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Mixology Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(MixologySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<MixologySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(CampfireCookingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroMixologyKabongRecipe), start: 15, skillType: typeof(CampfireCookingSkill));
            this.Initialize(displayText: Localizer.DoStr("Mixology Skill Book"), recipeType: typeof(LivroMixologyKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("MixologySkillBook <- 10000x MixologySkillScroll");
        }
    }

    [RequiresSkill(typeof(ElectronicsSkill), 1)]
    public class LivroOilDrillingKabongRecipe : RecipeFamily
    {
        public LivroOilDrillingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroOilDrillingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Oil Drilling Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(OilDrillingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<OilDrillingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(ElectronicsSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroOilDrillingKabongRecipe), start: 15, skillType: typeof(ElectronicsSkill));
            this.Initialize(displayText: Localizer.DoStr("Oil Drilling Skill Book"), recipeType: typeof(LivroOilDrillingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("OilDrillingSkillBook <- 10000x OilDrillingSkillScroll");
        }
    }

    [RequiresSkill(typeof(TailoringSkill), 1)]
    public class LivroPaintingKabongRecipe : RecipeFamily
    {
        public LivroPaintingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroPaintingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Painting Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(PaintingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<PaintingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(TailoringSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroPaintingKabongRecipe), start: 15, skillType: typeof(TailoringSkill));
            this.Initialize(displayText: Localizer.DoStr("Painting Skill Book"), recipeType: typeof(LivroPaintingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("PaintingSkillBook <- 10000x PaintingSkillScroll");
        }
    }

    [RequiresSkill(typeof(BlacksmithSkill), 1)]
    public class LivroPaperMillingKabongRecipe : RecipeFamily
    {
        public LivroPaperMillingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroPaperMillingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Paper Milling Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(PaperMillingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<PaperMillingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(BlacksmithSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroPaperMillingKabongRecipe), start: 15, skillType: typeof(BlacksmithSkill));
            this.Initialize(displayText: Localizer.DoStr("Paper Milling Skill Book"), recipeType: typeof(LivroPaperMillingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("PaperMillingSkillBook <- 10000x PaperMillingSkillScroll");
        }
    }

    [RequiresSkill(typeof(MasonrySkill), 1)]
    public class LivroPotteryKabongRecipe : RecipeFamily
    {
        public LivroPotteryKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroPotteryKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Pottery Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(PotterySkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<PotterySkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MasonrySkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroPotteryKabongRecipe), start: 15, skillType: typeof(MasonrySkill));
            this.Initialize(displayText: Localizer.DoStr("Pottery Skill Book"), recipeType: typeof(LivroPotteryKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("PotterySkillBook <- 10000x PotterySkillScroll");
        }
    }

    [RequiresSkill(typeof(MechanicsSkill), 1)]
    public class LivroRecyclingKabongRecipe : RecipeFamily
    {
        public LivroRecyclingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroRecyclingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Recycling Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(RecyclingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<RecyclingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MechanicsSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroRecyclingKabongRecipe), start: 15, skillType: typeof(MechanicsSkill));
            this.Initialize(displayText: Localizer.DoStr("Recycling Skill Book"), recipeType: typeof(LivroRecyclingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("RecyclingSkillBook <- 10000x RecyclingSkillScroll");
        }
    }

    [RequiresSkill(typeof(LoggingSkill), 1)]
    public class LivroShipwrightKabongRecipe : RecipeFamily
    {
        public LivroShipwrightKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroShipwrightKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Shipwright Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(ShipwrightSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<ShipwrightSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(LoggingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroShipwrightKabongRecipe), start: 15, skillType: typeof(LoggingSkill));
            this.Initialize(displayText: Localizer.DoStr("Shipwright Skill Book"), recipeType: typeof(LivroShipwrightKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("ShipwrightSkillBook <- 10000x ShipwrightSkillScroll");
        }
    }

    [RequiresSkill(typeof(MiningSkill), 1)]
    public class LivroSmeltingKabongRecipe : RecipeFamily
    {
        public LivroSmeltingKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroSmeltingKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Smelting Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(SmeltingSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<SmeltingSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(MiningSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroSmeltingKabongRecipe), start: 15, skillType: typeof(MiningSkill));
            this.Initialize(displayText: Localizer.DoStr("Smelting Skill Book"), recipeType: typeof(LivroSmeltingKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("SmeltingSkillBook <- 10000x SmeltingSkillScroll");
        }
    }

    [RequiresSkill(typeof(FarmingSkill), 1)]
    public class LivroTailoringKabongRecipe : RecipeFamily
    {
        public LivroTailoringKabongRecipe()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "LivroTailoringKabongRecipe",  //noloc
                displayName: Localizer.DoStr("Tailoring Skill Book"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(TailoringSkillScroll), 10000, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<TailoringSkillBook>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(FarmingSkill));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(LivroTailoringKabongRecipe), start: 15, skillType: typeof(FarmingSkill));
            this.Initialize(displayText: Localizer.DoStr("Tailoring Skill Book"), recipeType: typeof(LivroTailoringKabongRecipe));
            CraftingComponent.AddRecipe(tableType: typeof(LaboratoryObject), recipeFamily: this);
            KabongLivroDiario.Anota("TailoringSkillBook <- 10000x TailoringSkillScroll");
        }
    }
}
