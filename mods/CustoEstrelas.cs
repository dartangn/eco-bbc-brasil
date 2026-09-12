// CustoEstrelas.cs -- Servidor Kabong Brasil
// Custo de estrela por arvore de profissao, conforme "Solicitacao de ajustes - BBC-Brasil".
//
// COMO FUNCIONA
//   Usa o gancho OFICIAL da Strange Loop, documentado em __core__\Skills\SkillMods.cs:
//       Skill.CalculateStarsNeededForSpecialty = (user, skillType) => ...
//   Devolver null faz o jogo usar a formula padrao. Nao ha Harmony, nao ha .override.cs,
//   nao ha copia congelada de arquivo do jogo -- ou seja, sobrevive a atualizacao do Eco.
//
//   A estrutura deste arquivo espelha o proprio SkillMods.cs (IModInit + Initialize
//   estatico), que e o exemplo oficial para exatamente este uso.
//
//   O caminho #2 da documentacao oficial (partial class com "override int SpecialtyCost")
//   NAO COMPILA: todo arquivo do AutoGen ja declara SpecialtyCost, e redeclarar da CS0102.
//
// REGRAS IMPLEMENTADAS
//   1. Primeira profissao de todas          -> custo base
//   2. Especialidade da arvore ja iniciada  -> custo base
//   3. Iniciar outra arvore                 -> custo base + 1
//   4. Profissao AVANCADA fora da arvore    -> custo base + 2
//
//   "Arvore" = a profissao raiz da especialidade (o RequiresSkill dela).
//   "Arvore iniciada" = o jogador ja tem alguma OUTRA ESPECIALIDADE naquela profissao.
//   "Avancada" = custo base ORIGINAL do jogo >= 4 (ver LimiteAvancada). Esse teste usa o
//   valor do jogo, nao o nosso, para nao virar circular quando subimos Cooking para 4.
//
// AVISO: enquanto este arquivo estiver ativo, o CostPerAdditionalSpecialty do Difficulty.eco
// e IGNORADO para as habilidades que passam por aqui. Hoje ele esta em 0.0, entao nao muda
// nada; se um dia for alterado, lembrar disto.
//
// TUDO O QUE SE AJUSTA ESTA NO BLOCO "AJUSTE AQUI".

namespace KabongCustoEstrelas
{
    using Eco.Core.Plugins;
    using Eco.Core.Plugins.Interfaces;
    using Eco.Core.Utils;
    using Eco.Gameplay.Aliases;
    using Eco.Gameplay.GameActions;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Property;
    using Eco.Gameplay.Skills;
    using Eco.Gameplay.Systems.Messaging.Chat.Commands;
    using Eco.Shared.Localization;
    using Eco.Shared.Logging;
    using Eco.Shared.Utils;
    using Eco.Simulation.Time;
    using System;
    using System.Collections.Generic;
    using System.Linq;

    // ============================================================ tabelas

    public static class Tabela
    {
        // ===================== AJUSTE AQUI =====================

        // Custo base novo. Quem nao esta nesta lista mantem o custo do jogo.
        public static readonly Dictionary<string, int> CustoBase = new Dictionary<string, int>
        {
            { "FarmingSkill",            1 },  // era 2
            { "CookingSkill",            4 },  // era 3
            { "BakingSkill",             4 },  // era 3
            { "AdvancedCookingSkill",    6 },  // era 4
            { "AdvancedBakingSkill",     6 },  // era 4
            { "CuttingEdgeCookingSkill", 6 },  // era 5
            { "AdvancedMixologySkill",   6 },  // era 4  (mod Mixology)
            { "IceCreamSkill",           4 },  // era 3  (mod IceCream)
            // CampfireCookingSkill ja custa 2 e MixologySkill ja custa 3 - nada a fazer.
        };

        public const int PenalidadeNovaArvore           = 1;  // regra 3
        public const int PenalidadeAvancadaForaDaArvore = 2;  // regra 4
        public const int LimiteAvancada                 = 4;  // custo original >= isto = avancada

        // Habilidades que NAO contam para dizer que uma arvore foi iniciada.
        // SelfImprovement ganha XP automatico de toda outra profissao (ver o OnLevelUp das
        // especialidades), entao se contasse, TODO jogador teria a arvore Survivalist
        // iniciada e a isencao da primeira profissao nunca valeria.
        public static readonly HashSet<string> NaoContamComoArvore = new HashSet<string>
        {
            "SelfImprovementSkill",
        };

        // =======================================================

        // Profissoes raiz do jogo (as que tem Tag("Profession")).
        public static readonly HashSet<string> Raizes = new HashSet<string>
        {
            "CarpenterSkill", "ChefSkill", "EngineerSkill", "FarmerSkill", "HunterSkill",
            "MasonSkill", "ScientistSkill", "SmithSkill", "SurvivalistSkill", "TailorSkill",
        };

        // Especialidade -> profissao raiz. Levantado do RequiresSkill de cada arquivo em
        // 27/08/2026, no Eco 14.0.3. Habilidade que nao estiver aqui cai na reflexao
        // (RaizPorReflexao); se nem isso resolver, fica sem penalidade.
        public static readonly Dictionary<string, string> Arvore = new Dictionary<string, string>
        {
            // --- Chef ---
            { "CampfireCookingSkill",    "ChefSkill" },
            { "CookingSkill",            "ChefSkill" },
            { "BakingSkill",             "ChefSkill" },
            { "AdvancedCookingSkill",    "ChefSkill" },
            { "AdvancedBakingSkill",     "ChefSkill" },
            { "CuttingEdgeCookingSkill", "ChefSkill" },
            { "MixologySkill",           "ChefSkill" },  // mod
            { "AdvancedMixologySkill",   "ChefSkill" },  // mod
            { "IceCreamSkill",           "ChefSkill" },  // mod
            // --- Carpenter ---
            { "LoggingSkill",            "CarpenterSkill" },
            { "CarpentrySkill",          "CarpenterSkill" },
            { "ShipwrightSkill",         "CarpenterSkill" },
            { "PaperMillingSkill",       "CarpenterSkill" },
            { "CompositesSkill",         "CarpenterSkill" },
            // --- Mason ---
            { "MiningSkill",             "MasonSkill" },
            { "MasonrySkill",            "MasonSkill" },
            { "PotterySkill",            "MasonSkill" },
            { "GlassworkingSkill",       "MasonSkill" },
            { "AdvancedMasonrySkill",    "MasonSkill" },
            // --- Smith ---
            { "SmeltingSkill",           "SmithSkill" },
            { "BlacksmithSkill",         "SmithSkill" },
            { "AdvancedSmeltingSkill",   "SmithSkill" },
            // --- Farmer ---
            { "GatheringSkill",          "FarmerSkill" },
            { "FarmingSkill",            "FarmerSkill" },
            { "MillingSkill",            "FarmerSkill" },
            { "FertilizersSkill",        "FarmerSkill" },
            // --- Hunter ---
            { "HuntingSkill",            "HunterSkill" },
            { "ButcherySkill",           "HunterSkill" },
            // --- Engineer ---
            { "BasicEngineeringSkill",   "EngineerSkill" },
            { "MechanicsSkill",          "EngineerSkill" },
            { "ElectronicsSkill",        "EngineerSkill" },
            { "IndustrySkill",           "EngineerSkill" },
            // --- Scientist ---
            { "PaintingSkill",           "ScientistSkill" },
            { "RecyclingSkill",          "ScientistSkill" },
            { "OilDrillingSkill",        "ScientistSkill" },
            // --- Tailor ---
            { "TailoringSkill",          "TailorSkill" },
            // --- Survivalist ---
            { "SelfImprovementSkill",    "SurvivalistSkill" },
        };
    }

    // ============================================================ a regra

    public static class Regra
    {
        public static int? Calcular(User user, Type tipoSkill)
        {
            try
            {
                if (user == null || tipoSkill == null) return null;

                var nome = tipoSkill.Name;

                var custoJogo = CustoDoJogo(tipoSkill);
                var custoBase = Tabela.CustoBase.TryGetValue(nome, out var novo) ? novo : custoJogo;
                if (custoBase <= 0) return null;   // nao sei precificar - deixa o jogo decidir

                var raizAlvo = RaizDe(nome, tipoSkill);
                if (raizAlvo == null) return custoBase;   // sem arvore conhecida: so o custo base

                var iniciadas = ArvoresIniciadas(user);

                // regra 1: primeira profissao de todas -> custo base
                // regra 2: ja esta nessa arvore        -> custo base
                if (iniciadas.Count == 0 || iniciadas.Contains(raizAlvo)) return custoBase;

                // regra 4: avancada fora da arvore | regra 3: nova arvore
                var avancada = custoJogo >= Tabela.LimiteAvancada;
                return custoBase + (avancada ? Tabela.PenalidadeAvancadaForaDaArvore
                                             : Tabela.PenalidadeNovaArvore);
            }
            catch
            {
                return null;   // qualquer imprevisto: comportamento padrao do jogo
            }
        }

        /// <summary>Custo base ORIGINAL do jogo, lido da propria habilidade.</summary>
        public static int CustoDoJogo(Type tipoSkill)
        {
            try
            {
                var s = Skill.AllSkills.FirstOrDefault(x => x.GetType() == tipoSkill);
                return s != null ? s.SpecialtyCost : 0;
            }
            catch { return 0; }
        }

        /// <summary>Nome da profissao raiz. Se a propria habilidade for raiz, ela mesma.</summary>
        public static string RaizDe(string nome, Type tipoSkill)
        {
            if (Tabela.Raizes.Contains(nome)) return nome;
            if (Tabela.Arvore.TryGetValue(nome, out var r)) return r;
            return RaizPorReflexao(tipoSkill);
        }

        /// <summary>
        /// Reserva para habilidade de mod que nao esta na tabela: le o atributo RequiresSkill
        /// sem depender do nome das propriedades dele, para nao quebrar se a API mudar.
        /// </summary>
        private static string RaizPorReflexao(Type tipoSkill)
        {
            try
            {
                foreach (var attr in tipoSkill.GetCustomAttributes(true))
                {
                    var ta = attr.GetType();
                    if (ta.Name != "RequiresSkillAttribute") continue;

                    foreach (var p in ta.GetProperties())
                        if (p.PropertyType == typeof(Type) && p.GetValue(attr) is Type t1)
                            return t1.Name;

                    foreach (var f in ta.GetFields())
                        if (f.FieldType == typeof(Type) && f.GetValue(attr) is Type t2)
                            return t2.Name;
                }
            }
            catch { }
            return null;
        }

        /// <summary>Arvores em que o jogador ja tem alguma ESPECIALIDADE.</summary>
        public static HashSet<string> ArvoresIniciadas(User user)
        {
            var arvores = new HashSet<string>();
            try
            {
                foreach (var s in user.Skillset.Skills)
                {
                    if (s == null || s.Level < 1) continue;

                    var n = s.GetType().Name;
                    if (Tabela.Raizes.Contains(n)) continue;              // raiz nao marca por si
                    if (Tabela.NaoContamComoArvore.Contains(n)) continue;

                    var r = RaizDe(n, s.GetType());
                    if (r != null) arvores.Add(r);
                }
            }
            catch { }
            return arvores;
        }
    }

    // ============================================================ registro no jogo

    // PROVA DE VIDA - por que existe:
    //   Mod de codigo em UserCode nao aparece no "Loading mods" do log, e o Smart Storage
    //   ja ensinou aqui que compilar nao e funcionar. Pior: o Gates e o MarketMod logam do
    //   construtor do IModInit e essa mensagem NAO aparece em log nenhum deste servidor,
    //   ou seja o construtor pode nunca ser chamado. Por isso este arquivo:
    //     - instrumenta os TRES ganchos possiveis (Register, construtor, Initialize);
    //     - ativa por qualquer um deles, uma vez so (idempotente);
    //     - anota num ARQUIVO PROPRIO, que nao depende do logger do Eco estar pronto.
    //   Console.WriteLine NAO serve: o compilador de mods do Eco nao referencia
    //   System.Console (da CS0103). Isso foi testado.
    public class CustoEstrelasMod : IModInit
    {
        public const string Diario = @"/opt/eco/custo-estrelas-vida.txt";
        private static bool ativado;

        public static ModRegistration Register()
        {
            Anota("Register() chamado");
            Ativar("Register");
            return new ModRegistration
            {
                ModName        = "CustoEstrelas",
                ModDescription = "Custo de estrela por arvore de profissao - Servidor Kabong Brasil.",
                ModDisplayName = "Custo de Estrelas (Kabong)"
            };
        }

        // Forma usada pelo Gates e pelo MarketMod.
        public CustoEstrelasMod()
        {
            Anota("construtor chamado");
            Ativar("construtor");
        }

        // Forma usada pelo SkillMods.cs do proprio jogo.
        public static void Initialize()
        {
            Anota("Initialize() chamado");
            Ativar("Initialize");
        }

        private static void Ativar(string origem)
        {
            if (ativado) { Anota("  (ja estava ativo; pedido de " + origem + " ignorado)"); return; }

            // O delegate vem PRIMEIRO e sozinho: se o listener falhar, o preco continua valendo.
            try
            {
                Skill.CalculateStarsNeededForSpecialty = (user, tipoSkill) => Regra.Calcular(user, tipoSkill);
                ativado = true;
                Anota("  ATIVO por " + origem + " - " + Tabela.CustoBase.Count + " precos alterados, "
                      + Tabela.Arvore.Count + " especialidades mapeadas, penalidades +"
                      + Tabela.PenalidadeNovaArvore + "/+" + Tabela.PenalidadeAvancadaForaDaArvore);
            }
            catch (Exception e) { Anota("  FALHOU ao instalar o delegate: " + e.Message); return; }

            try { ActionUtil.AddListener(new AvisoDePreco()); Anota("  listener de GainSpecialty registrado"); }
            catch (Exception e) { Anota("  listener NAO registrado (preco exibido pode ficar velho): " + e.Message); }

            try { Log.WriteLine(Localizer.Do($"[Kabong] CustoEstrelas ATIVO por {origem}")); } catch { }
        }

        private static void Anota(string texto)
        {
            try
            {
                System.IO.File.AppendAllText(Diario,
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\r\n");
            }
            catch { }
        }
    }

    /// <summary>
    /// O custo e um valor em CACHE mostrado ao cliente. Sem avisar, a interface segue
    /// exibindo o preco velho depois que o jogador entra numa arvore nova. O proprio
    /// SkillMods.cs da Strange Loop avisa disso.
    /// </summary>
    public class AvisoDePreco : IGameActionAware
    {
        public Result CanPerformAction(GameAction action) => Result.Succeeded;

        public void ActionPerformed(GameAction action)
        {
            try
            {
                if (action is GainSpecialty g && g.Citizen != null)
                    g.Citizen.Skillset.NotifyEffectiveSpecialtyCostChanged();
            }
            catch { }
        }

        public LazyResult ShouldOverrideAuth(IAlias alias, IOwned property, GameAction action)
            => LazyResult.FailedNoMessage;
    }

    // ============================================================ comando de conferencia

    [ChatCommandHandler]
    public static class CustoEstrelasComandos
    {
        [ChatCommand("Custo de estrelas - BBC-Brasil")]
        public static void CustoEstrelas() { }

        [ChatSubCommand("CustoEstrelas", "Lista o custo de cada profissao para voce", ChatAuthorizationLevel.Admin)]
        public static void Ver(User user)
        {
            var arvores = Regra.ArvoresIniciadas(user);
            var linhas  = new List<string>();
            linhas.Add("Arvores ja iniciadas: " + (arvores.Count == 0 ? "nenhuma" : string.Join(", ", arvores.OrderBy(x => x))));
            linhas.Add("");

            foreach (var s in Skill.AllSkills.OrderBy(x => x.GetType().Name))
            {
                var tipo = s.GetType();
                if (Tabela.Raizes.Contains(tipo.Name)) continue;

                var jogo  = s.SpecialtyCost;
                var nosso = Regra.Calcular(user, tipo) ?? jogo;
                var marca = nosso != jogo ? "   <-- alterado" : "";
                linhas.Add(tipo.Name.Replace("Skill", "") + ": " + nosso + " (jogo: " + jogo + ")" + marca);
            }

            user.MsgLocStr(string.Join("\n", linhas));
        }
    }
}
