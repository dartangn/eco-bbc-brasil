// ============================================================================
// PlantasCrescimento.cs  --  Servidor Kabong Brasil / BBC-Brasil
// GERADO por gerar-plantas-crescimento.py -- NAO EDITE A MAO.
//
// Aplica a TODAS as 53 plantas (PlantSpecies) os MESMOS fatores de crescimento
// que o ArvoresDensas.cs aplicou as 10 arvores, a pedido do Raul em 12/09/2026:
//
//     MaturityAgeDays x0.4      SeedingTime x0.4      SeedsCount x2      SpreadRate x3
//
// Numeros ABSOLUTOS, com o valor original do jogo ao lado em comentario -- regra
// deste projeto: nada de multiplicador escondido, da para conferir a olho.
//
// NAO entram aqui, e o gerador decide LENDO o servidor:
//   - as 10 arvores do ArvoresDensas.cs (duas implementacoes do mesmo metodo
//     parcial = CS0111, e o servidor nao sobe);
//   - a OldGrowthRedwood, que a Strange Loop declara nao-renovavel de proposito;
//   - qualquer especie a que falte um dos 4 campos;
//   - o CAPIM (CommonGrass, Bunchgrass, Switchgrass, BigBluestem), fora a pedido do
//     Raul: sao eles que invadem terreno arado.
//
// NAO precisa de mundo novo: estes campos valem no mundo existente. Densidade de
// GERACAO e outra coisa, exigiria wipe, e este arquivo nao toca nela.
//
// Reverter: apagar este arquivo.
// ============================================================================

namespace Eco.Mods.Organisms
{
    using System;

    /// <summary>Prova de vida: uma linha por especie a cada arranque. O `lock` nao e enfeite --
    /// em 03/09/2026 as especies foram construidas EM PARALELO dentro do mesmo segundo e o
    /// AppendAllText colidiu, perdendo duas linhas.</summary>
    public static class KabongPlantasDiario
    {
        private const string Diario = "/opt/eco/plantas-crescimento-vida.txt";
        private static readonly object Tranca = new object();

        public static void Anota(string texto)
        {
            try
            {
                lock (Tranca)
                {
                    System.IO.File.AppendAllText(Diario,
                        DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\n");
                }
            }
            catch { }
        }
    }

    public partial class Agave
    {
        public partial class AgaveSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.6f;   // jogo: 1.5
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Agave: maturidade 0.8->0.32f, semeia 1.5->0.6f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class AmanitaMushroom
    {
        public partial class AmanitaMushroomSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("AmanitaMushroom: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class ArcticWillow
    {
        public partial class ArcticWillowSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("ArcticWillow: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class BarrelCactus
    {
        public partial class BarrelCactusSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.6f;   // jogo: 1.5
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("BarrelCactus: maturidade 0.8->0.32f, semeia 1.5->0.6f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Beans
    {
        public partial class BeansSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Beans: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Beets
    {
        public partial class BeetsSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Beets: maturidade 0.8->0.32f, semeia 0.75->0.3f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class BoleteMushroom
    {
        public partial class BoleteMushroomSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("BoleteMushroom: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Bullrush
    {
        public partial class BullrushSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Bullrush: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Buttonbush
    {
        public partial class ButtonbushSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Buttonbush: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Camas
    {
        public partial class CamasSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Camas: maturidade 0.8->0.32f, semeia 0.75->0.3f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Clam
    {
        public partial class ClamSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Clam: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class CookeinaMushroom
    {
        public partial class CookeinaMushroomSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("CookeinaMushroom: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Corn
    {
        public partial class CornSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.4f;   // jogo: 1
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Corn: maturidade 0.8->0.32f, semeia 1->0.4f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Cotton
    {
        public partial class CottonSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Cotton: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class CreosoteBush
    {
        public partial class CreosoteBushSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.6f;   // jogo: 1.5
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("CreosoteBush: maturidade 0.8->0.32f, semeia 1.5->0.6f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class CriminiMushroom
    {
        public partial class CriminiMushroomSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("CriminiMushroom: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Daisy
    {
        public partial class DaisySpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Daisy: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class DeerLichen
    {
        public partial class DeerLichenSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("DeerLichen: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class DesertMoss
    {
        public partial class DesertMossSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.6f;   // jogo: 1.5
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("DesertMoss: maturidade 0.8->0.32f, semeia 1.5->0.6f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class DwarfWillow
    {
        public partial class DwarfWillowSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("DwarfWillow: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Fern
    {
        public partial class FernSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Fern: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class FilmyFern
    {
        public partial class FilmyFernSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("FilmyFern: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Fireweed
    {
        public partial class FireweedSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Fireweed: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Flax
    {
        public partial class FlaxSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.4f;   // jogo: 1
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Flax: maturidade 0.8->0.32f, semeia 1->0.4f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Heliconia
    {
        public partial class HeliconiaSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Heliconia: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Huckleberry
    {
        public partial class HuckleberrySpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Huckleberry: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Jointfir
    {
        public partial class JointfirSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.6f;   // jogo: 1.5
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Jointfir: maturidade 0.8->0.32f, semeia 1.5->0.6f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Kelp
    {
        public partial class KelpSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Kelp: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class KingFern
    {
        public partial class KingFernSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("KingFern: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class LatticeMushroom
    {
        public partial class LatticeMushroomSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("LatticeMushroom: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Lupine
    {
        public partial class LupineSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Lupine: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class OceanSpray
    {
        public partial class OceanSpraySpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("OceanSpray: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Orchid
    {
        public partial class OrchidSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Orchid: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Papaya
    {
        public partial class PapayaSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Papaya: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class PeatMoss
    {
        public partial class PeatMossSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("PeatMoss: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Pineapple
    {
        public partial class PineappleSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Pineapple: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class PitcherPlant
    {
        public partial class PitcherPlantSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("PitcherPlant: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class PricklyPear
    {
        public partial class PricklyPearSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("PricklyPear: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Pumpkin
    {
        public partial class PumpkinSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 6;   // jogo: 3
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Pumpkin: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 3->6, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Rice
    {
        public partial class RiceSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.4f;   // jogo: 1
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Rice: maturidade 0.8->0.32f, semeia 1->0.4f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class RoseBush
    {
        public partial class RoseBushSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("RoseBush: maturidade 0.8->0.32f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Salal
    {
        public partial class SalalSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Salal: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Saxifrage
    {
        public partial class SaxifrageSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Saxifrage: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Seagrass
    {
        public partial class SeagrassSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Seagrass: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Sunflower
    {
        public partial class SunflowerSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.4f;   // jogo: 1
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Sunflower: maturidade 0.8->0.32f, semeia 1->0.4f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Taro
    {
        public partial class TaroSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Taro: maturidade 0.8->0.32f, semeia 0.75->0.3f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Tomatoes
    {
        public partial class TomatoesSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.48f;   // jogo: 1.2
                this.SeedingTime     = 0.3f;   // jogo: 0.75
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Tomatoes: maturidade 1.2->0.48f, semeia 0.75->0.3f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Trillium
    {
        public partial class TrilliumSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Trillium: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Tulip
    {
        public partial class TulipSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.12f;   // jogo: 0.3
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Tulip: maturidade 0.8->0.32f, semeia 0.3->0.12f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Urchin
    {
        public partial class UrchinSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Urchin: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Waterweed
    {
        public partial class WaterweedSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Waterweed: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }

    public partial class Wheat
    {
        public partial class WheatSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.4f;   // jogo: 1
                this.SeedsCount      = 4;   // jogo: 2
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("Wheat: maturidade 0.8->0.32f, semeia 1->0.4f, sementes 2->4, espalha 0.001->0.003f");
            }
        }
    }

    public partial class WhiteBursage
    {
        public partial class WhiteBursageSpecies
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = 0.32f;   // jogo: 0.8
                this.SeedingTime     = 0.16f;   // jogo: 0.4
                this.SeedsCount      = 2;   // jogo: 1
                this.SpreadRate      = 0.003f;   // jogo: 0.001
                KabongPlantasDiario.Anota("WhiteBursage: maturidade 0.8->0.32f, semeia 0.4->0.16f, sementes 1->2, espalha 0.001->0.003f");
            }
        }
    }
}
