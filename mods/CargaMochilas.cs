// CargaMochilas.cs -- Servidor Kabong Brasil
//
// O QUE FAZ
//   Multiplica por 5 a capacidade de peso das cinco mochilas do jogo, para a ultima
//   (Bearpack) ficar em 100 kg, mantendo a curva de progressao intacta.
//
//     Basic Backpack      5 kg  ->   25 kg    (Gathering 1)
//     Light Backpack      8 kg  ->   40 kg    (Tailoring 3)
//     Work Backpack       8 kg  ->   40 kg    (Tailoring 3)
//     Big Backpack       15 kg  ->   75 kg    (Tailoring 2)
//     Bearpack           20 kg  ->  100 kg    (Tailoring 4)
//
//   O fator 5 nao foi escolhido por acaso: e o mesmo do StackSizeMultiplier do servidor
//   e o "5X" do nome. Se um dia mudar, muda so o Fator aqui embaixo.
//
// O QUE ESTE ARQUIVO **NAO** MEXE
//   Bloco, tora, minerio, barra e madeira sao BlockItem<T>, ou seja itens CARREGADOS:
//   vao para as MAOS e nunca passam pelo peso da mochila. Quem governa aquilo e o
//   MaxTake / CarriedStackSizeCap da ferramenta - ver ShovelItem.override.cs e a secao
//   10-C do CLAUDE.md. Aqui so muda o que de fato vai na mochila: comida (125 a 200 g),
//   tabua (500 g), ferramenta (1000 g) e afins.
//
//   Tambem nao mexe nos outros bonus das mochilas, porque so a chave MaxCarryWeight e
//   reescrita: LightBackpack mantem MovementSpeed 1, WorkBackpack mantem CarriedSlots 1,
//   BigBackpack mantem BackpackSlots 4 e Bearpack mantem BackpackSlots 8.
//
// COMO FUNCIONA, E POR QUE NAO E .override.cs NEM REFLEXAO
//   O valor vive num `private static Dictionary<UserStatType, float> flatStats` de cada
//   classe, e o `GetFlatStats()` **ja e** `public override` - ou seja, partial class NAO
//   pode redeclarar o metodo (daria CS0111, a mesma armadilha do SpecialtyCost).
//
//   Mas partial class **acessa o proprio privado**: declarando aqui a mesma classe, este
//   codigo passa a fazer parte dela e mexe no `flatStats` direto. Vantagens sobre as
//   alternativas:
//     - contra .override.cs : nao cria copia congelada de arquivo do jogo (foi assim que
//       o Big fast shovel degradou sem avisar);
//     - contra reflexao     : e verificado em tempo de COMPILACAO. Se a Strange Loop
//       renomear o campo, quebra alto no arranque, que e o tipo bom de falha.
//
//   A capacidade total do jogador continua sendo uma SOMA: base do jogador + mochila +
//   calca (5 a 7,5 kg) + Self Improvement + talento Deeper Pockets. Mexemos numa parcela.
//
// A unidade interna e GRAMA. Provado no PlayerDefaults.cs, que divide por 1000 para
// exibir em kg: BonusUnitsDecoratorStrategy(..., "kg", (float val) => val/1000f).

namespace Eco.Mods.TechTree
{
    using Eco.Core.Plugins.Interfaces;
    using Eco.Gameplay.Items;
    using Eco.Gameplay.Players;
    using Eco.Shared.Localization;
    using Eco.Shared.Logging;
    using System;
    using System.Collections.Generic;

    // ===================== AJUSTE AQUI =====================
    internal static class CargaMochilasConfig
    {
        public const float Fator = 5f;                 // 20 kg x 5 = 100 kg na Bearpack
        public const string Diario = @"/opt/eco/carga-mochilas-vida.txt";
    }
    // =======================================================

    // Uma parcial por mochila, so para alcancar o flatStats privado dela.
    public partial class BasicBackpackItem
    {
        internal static float KabongCarga(float fator)
        {
            var novo = flatStats[UserStatType.MaxCarryWeight] * fator;
            flatStats[UserStatType.MaxCarryWeight] = novo;
            return novo;
        }
    }

    public partial class LightBackpackItem
    {
        internal static float KabongCarga(float fator)
        {
            var novo = flatStats[UserStatType.MaxCarryWeight] * fator;
            flatStats[UserStatType.MaxCarryWeight] = novo;
            return novo;
        }
    }

    public partial class WorkBackpackItem
    {
        internal static float KabongCarga(float fator)
        {
            var novo = flatStats[UserStatType.MaxCarryWeight] * fator;
            flatStats[UserStatType.MaxCarryWeight] = novo;
            return novo;
        }
    }

    public partial class BigBackpackItem
    {
        internal static float KabongCarga(float fator)
        {
            var novo = flatStats[UserStatType.MaxCarryWeight] * fator;
            flatStats[UserStatType.MaxCarryWeight] = novo;
            return novo;
        }
    }

    public partial class BearpackItem
    {
        internal static float KabongCarga(float fator)
        {
            var novo = flatStats[UserStatType.MaxCarryWeight] * fator;
            flatStats[UserStatType.MaxCarryWeight] = novo;
            return novo;
        }
    }

    public class CargaMochilasMod : IModInit
    {
        private static bool feito;

        public static ModRegistration Register()
        {
            Ativar("Register");
            return new ModRegistration
            {
                ModName        = "CargaMochilas",
                ModDescription = "Capacidade de peso das mochilas x5 - Servidor Kabong Brasil.",
                ModDisplayName = "Carga das Mochilas (Kabong)"
            };
        }

        // Initialize() estatico e o gancho que ESTE servidor comprovadamente chama - ver
        // secao 15.5 do CLAUDE.md. O construtor NAO e chamado, entao nem tento.
        public static void Initialize() { Ativar("Initialize"); }

        private static void Ativar(string origem)
        {
            if (feito) { Anota("  (ja estava aplicado; pedido de " + origem + " ignorado)"); return; }
            try
            {
                var f = CargaMochilasConfig.Fator;
                Anota("aplicando por " + origem + ", fator " + f);
                Anota("  Basic Backpack -> " + (BasicBackpackItem.KabongCarga(f) / 1000f) + " kg");
                Anota("  Light Backpack -> " + (LightBackpackItem.KabongCarga(f) / 1000f) + " kg");
                Anota("  Work Backpack  -> " + (WorkBackpackItem.KabongCarga(f)  / 1000f) + " kg");
                Anota("  Big Backpack   -> " + (BigBackpackItem.KabongCarga(f)   / 1000f) + " kg");
                Anota("  Bearpack       -> " + (BearpackItem.KabongCarga(f)      / 1000f) + " kg");
                feito = true;
                try { Log.WriteLine(Localizer.Do($"[Kabong] CargaMochilas aplicado por {origem}, fator {f}")); } catch { }
            }
            catch (Exception e)
            {
                Anota("  FALHOU: " + e.Message);
            }
        }

        private static void Anota(string texto)
        {
            try
            {
                System.IO.File.AppendAllText(CargaMochilasConfig.Diario,
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\r\n");
            }
            catch { }
        }
    }
}
