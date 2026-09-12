// ArvoresDensas.cs -- Servidor Kabong Brasil
// Densidade de arvore na geracao do mundo + velocidade de crescimento e recomposicao.
//
// TECNICA: partial class + gancho ModsPostInitialize(), que e a PRIMEIRA opcao da ordem
// de decisao oficial (Mods/UserCode/README.md). Nao e .override.cs, nao e Harmony,
// nao toca no __core__. Verificado em compilacao: se a Strange Loop renomear qualquer
// propriedade, isto quebra ALTO no arranque, que e o tipo bom de falha.
//
// POR QUE O GANCHO FUNCIONA PARA GERACAO DE MUNDO (medido no log de 03/09/2026)
//   06:04:22  Loading mods            <- construtores das especies rodam aqui
//   06:04:57  Generating world 4km2   <- geracao le os valores JA alterados
//   06:11:19  Generating world ... Finished
// O ModsPostInitialize() e a ULTIMA linha do construtor de cada especie, entao o que
// setamos aqui sobrescreve tudo e chega a tempo da geracao.
//
// DUAS METADES, com custos MUITO diferentes:
//   GenerationDefinitions  -> so vale em mundo NOVO. Mudar depois exige regerar.
//   Maturidade / semeadura -> vale a partir do proximo restart, em mundo existente.
//
// OldGrowthRedwood NAO E TOCADA de proposito. A Strange Loop a declara nao-renovavel
// (o texto do jogo diz que ela nao volta a crescer se cortada), com MaturityAgeDays 30
// e SpreadRate 0. Mexer nela apagaria uma decisao de jogo deliberada.
//
// TETO NAO TESTADO -- ler antes de subir mais a densidade:
//   Cada especie tem CapacityConstraints com CanopySpace (ConsumedCapacityPerPop de 5 a
//   50 conforme a especie). Isso e o TETO de populacao que a simulacao permite. Se a
//   geracao plantar acima do teto, a simulacao mata o excedente e o mundo AFINA com o
//   tempo. Nao sabemos se os valores abaixo passam do teto -- e o que a medicao em campo
//   vai dizer. Se afinar, o proximo passo e baixar ConsumedCapacityPerPop, nao subir
//   mais a densidade.
//
// PARA AJUSTAR: os numeros sao ABSOLUTOS, um par por especie, com o valor original ao
// lado em comentario. Nao ha multiplicador escondido -- de proposito, para nao repetir
// o caso da pa (secao 10-C), onde nenhum multiplicador unico produzia a curva pedida.

namespace Eco.Mods.Organisms
{
    using Eco.Shared.Math;

    /// <summary>Diario de prova de vida. Compilar nao e funcionar -- este arquivo prova
    /// que os construtores rodaram e com quais valores.</summary>
    public static class KabongArvores
    {
        public const string Diario = "/opt/eco/arvores-vida.txt";

        // O lock e NECESSARIO aqui, e foi provado: na primeira rodada (03/09 06:37:52) as
        // 10 especies foram construidas EM PARALELO dentro do mesmo segundo, o
        // AppendAllText colidiu, e o diario saiu com 8 especies legiveis mais 2 linhas
        // em branco -- Birch e Joshua perdidas. As dez rodaram (senao a compilacao teria
        // acusado); so a ESCRITA se perdeu.
        //
        // Aqui o lock e de graca, ao contrario do caso da queda de arvore (secao 19.16),
        // onde ele foi recusado: la seriam 4 a 10 escritas por arvore derrubada, no
        // caminho de jogabilidade. Aqui sao 10 escritas uma vez por arranque.
        static readonly object trava = new object();

        public static void Anota(string especie, int grupoMin, int grupoMax,
                                 int distMin, int distMax, float maturidade)
        {
            try
            {
                lock (trava)
                {
                    System.IO.File.AppendAllText(Diario, string.Format(
                        "{0}  {1,-16} grupo={2}-{3}  dist={4}-{5}  maturidade={6}d\n",
                        System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                        especie, grupoMin, grupoMax, distMin, distMax, maturidade));
                }
            }
            catch { }   // diagnostico nunca pode derrubar o servidor
        }
    }

    // ---------------------------------------------------------------------------
    // AS QUATRO ESPARSAS -- o jogo planta 1 a 3 por grupo, isoladas. Sao as que mais
    // se notam ao dobrar, porque partem do minimo.
    // ---------------------------------------------------------------------------

    public partial class Cedar
    {
        public partial class CedarSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(2, 6);    // era 1, 3
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(7, 13);   // era 10, 20
                this.MaturityAgeDays = 2.0f;      // era 5
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 4;         // era 2
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Cedar", 2, 6, 7, 13, 2.0f);
            }
        }
    }

    public partial class Fir
    {
        public partial class FirSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(2, 6);    // era 1, 3
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(7, 13);   // era 10, 20
                this.MaturityAgeDays = 2.2f;      // era 5.5
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 4;         // era 2
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Fir", 2, 6, 7, 13, 2.2f);
            }
        }
    }

    public partial class Spruce
    {
        public partial class SpruceSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(2, 6);    // era 1, 3
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(7, 13);   // era 10, 20
                this.MaturityAgeDays = 2.2f;      // era 5.5
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 4;         // era 2
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Spruce", 2, 6, 7, 13, 2.2f);
            }
        }
    }

    public partial class Oak
    {
        public partial class OakSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(2, 6);    // era 1, 3
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(7, 13);   // era 10, 20
                this.MaturityAgeDays = 2.8f;      // era 7
                this.SeedingTime     = 2.4f;      // era 6
                this.SeedsCount      = 2;         // era 1
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Oak", 2, 6, 7, 13, 2.8f);
            }
        }
    }

    // ---------------------------------------------------------------------------
    // AS JA AGRUPADAS -- aqui o fator e 1,5 e nao 2. Elas ja plantam de 3 a 60 por
    // grupo; dobrar carregaria a simulacao sem ganho visual proporcional.
    // ---------------------------------------------------------------------------

    public partial class Birch
    {
        public partial class BirchSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(45, 90);  // era 30, 60
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(20, 39);  // era 30, 60
                this.MaturityAgeDays = 2.0f;      // era 5
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 4;         // era 2
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Birch", 45, 90, 20, 39, 2.0f);
            }
        }
    }

    public partial class Redwood
    {
        public partial class RedwoodSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(8, 60);   // era 5, 40
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(39, 78);  // era 60, 120
                this.MaturityAgeDays = 2.4f;      // era 6
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 4;         // era 2
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Redwood", 8, 60, 39, 78, 2.4f);
            }
        }
    }

    public partial class Ceiba
    {
        public partial class CeibaSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(6, 24);   // era 4, 16
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(3, 8);    // era 5, 12
                this.MaturityAgeDays = 2.4f;      // era 6
                this.SeedingTime     = 2.4f;      // era 6
                this.SeedsCount      = 2;         // era 1
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Ceiba", 6, 24, 3, 8, 2.4f);
            }
        }
    }

    public partial class Palm
    {
        public partial class PalmSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(6, 15);   // era 4, 10
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(9, 14);   // era 14, 22
                this.MaturityAgeDays = 1.8f;      // era 4.5
                this.SeedingTime     = 0.85f;     // era 2.1
                this.SeedsCount      = 6;         // era 3
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Palm", 6, 15, 9, 14, 1.8f);
            }
        }
    }

    // ---------------------------------------------------------------------------
    // AS DE DESERTO -- o mapa Balanced Water tem deserto (o /info do mundo anterior
    // listou White Bursage, Creosote, Jointfir, Joshua). Sao fonte de madeira onde
    // nao ha floresta.
    // ---------------------------------------------------------------------------

    public partial class Joshua
    {
        public partial class JoshuaSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(5, 8);    // era 3, 5
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(20, 33);  // era 30, 50
                this.MaturityAgeDays = 2.8f;      // era 7
                this.SeedingTime     = 1.0f;      // era 2.5
                this.SeedsCount      = 6;         // era 3
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("Joshua", 5, 8, 20, 33, 2.8f);
            }
        }
    }

    public partial class SaguaroCactus
    {
        public partial class SaguaroCactusSpecies
        {
            partial void ModsPostInitialize()
            {
                this.GenerationDefinitions.PlantsInGroup            = new Range(5, 8);    // era 3, 5
                this.GenerationDefinitions.MinDistanceBetweenGroups = new Range(20, 39);  // era 30, 60
                this.MaturityAgeDays = 2.4f;      // era 6
                this.SeedingTime     = 0.6f;      // era 1.5
                this.SeedsCount      = 6;         // era 3
                this.SpreadRate      = 0.0003f;   // era 0.0001
                KabongArvores.Anota("SaguaroCactus", 5, 8, 20, 39, 2.4f);
            }
        }
    }
}
