// ============================================================================
// CidadaniaFederacao.cs  --  Servidor Kabong Brasil / BBC-Brasil
//
// O PROBLEMA (medido em campo por duas pessoas, 10 e 11/09/2026)
//   O pepsy e o raul.motta puseram a pedra de fundacao de cidade no chao e, ao
//   bater com o martelo para pega-la de volta, SAIRAM DA FEDERACAO. Nenhum dos
//   dois fundou a cidade -- basta plantar e recolher.
//
//   Por que: a cidadania DIRETA e exclusiva (o jogo avisa: "you will lose direct
//   citizenship of {0} and gain direct citizenship of {1}"). Plantar a pedra cria
//   um assentamento e move a cidadania direta para ele; recolher a pedra destroi
//   esse assentamento, e a pessoa fica sem nenhum -- nem o da cidade, nem o da
//   federacao, da qual so era cidadao por heranca.
//
// POR QUE ISTO E UM MOD, E NAO CONFIGURACAO
//   Nao ha o que ajustar. Conferidos UM A UM: os 56 campos do Settlements.eco e
//   os 14 da politica de imigracao. Nenhum impede a perda.
//
//   E o proprio Eco TEM o conceito certo -- os metodos abaixo existem:
//       RemoveAllDirectCitizens(bool joinParentUponLeaving, ...)
//       ForceRemoveMember(User user, UserRoster rosterToJoinUponLeaving = null)
//   "ao sair, entrar no pai". O caminho que recolhe a pedra nao usa isso, e esse
//   caminho esta dentro do binario: nao alcancamos. Entao o servidor devolve.
//
//   Isto e remediacao, nao prevencao -- e o Raul tem razao em chamar assim. A
//   diferenca e que ela e automatica e imediata, e nao depende de admin.
//
// O QUE ELE FAZ, E O QUE NAO FAZ
//   Ouve SettlementCitizenship.CitizenshipChanged. Quando alguem muda de
//   cidadania, espera 2 s (para a remocao do jogo terminar) e, SE a pessoa nao
//   for mais cidada da federacao de jeito nenhum, a poe de volta na lista de
//   cidadaos DIRETOS dela.
//
//   NAO interfere em quem funda cidade ou entra numa cidade: essa pessoa
//   continua cidada da federacao POR HERANCA, o HasCitizen devolve true, e o mod
//   nao faz nada. Ele so pega quem ficou orfao.
//
// ASSINATURAS -- todas da documentacao oficial (docs.play.eco, lida pelo
// navegador) ou de codigo que ja compila neste servidor. Nada foi adivinhado:
//   SettlementCitizenship.CitizenshipChanged : static ThreadSafeAction<User, Settlement, bool>
//   Settlement.Citizenship                   : SettlementCitizenship
//   SettlementCitizenship.HasCitizen(User)   : bool      (direto OU por filha)
//   SettlementCitizenship.DirectCitizenRoster: UserRoster
//   UserRoster.AddToRoster(User userAdding, User userToAdd, bool sendNotice, bool forceAdd = false)
//   Registrars.Get<Settlement>().GetByName(nome)   <- forma usada pelo proprio jogo
//   ThreadUtils.Delay(5f, () => ...)               <- forma usada em TreeObject.cs
//   .Add(handler) em ThreadSafeAction               <- forma usada em WorldLayerSettingsOilfield.cs
//
// O NOME DA FEDERACAO e montado por (char)231 e (char)227 para ficar ASCII PURO
// (regra do projeto): o nome real tem cedilha e til, montados por codigo de
// caractere. Se a federacao for renomeada, trocar aqui -- e o diario avisa quando
// nao a encontra.
//
// PRE-VOO: conferir-cs-novo.py antes de instalar.
// INSTALACAO: so com arranque VIGIADO (Regra 18 do ESTADO.md).
// REVERTER: apagar o arquivo.
// ============================================================================

namespace Eco.Mods.KabongBrasil
{
    using System;
    using Eco.Core.Plugins.Interfaces;   // IModInit
    using Eco.Core.Systems;              // Registrars
    using Eco.Core.Utils;                // ThreadUtils
    using Eco.Gameplay.Players;          // User
    using Eco.Gameplay.Settlements;      // Settlement, SettlementCitizenship
    using Eco.Shared.Utils;

    public class CidadaniaFederacao : IModInit
    {
        // ---------------------------------------------------------------- AJUSTE AQUI
        /// <summary>Nome exato da federacao, como aparece no jogo.</summary>
        public static readonly string NomeDaFederacao = "Federa" + (char)231 + (char)227 + "o";
        // 231 = c-cedilha, 227 = a-til. Montado por codigo de caractere para o arquivo
        // ficar ASCII PURO, que e regra deste projeto.

        /// <summary>Segundos de espera antes de devolver, para a remocao do jogo terminar
        /// primeiro. Se o teste em campo mostrar que a pessoa continua fora, subir este valor.</summary>
        public const float EsperaSegundos = 2f;
        // ------------------------------------------------------------ FIM DO AJUSTE

        private const string Diario = "/opt/eco/cidadania-federacao-vida.txt";
        private static readonly object Tranca = new object();
        private static bool ativado;

        public static void Initialize()
        {
            Ativar("Initialize");
        }

        /// <summary>Idempotente por seguranca: se o Eco chamar o gancho mais de uma vez, o
        /// ouvinte nao entra duas vezes.</summary>
        private static void Ativar(string origem)
        {
            lock (Tranca)
            {
                if (ativado) { Anota("  (ja estava ativo; pedido de " + origem + " ignorado)"); return; }
                try
                {
                    SettlementCitizenship.CitizenshipChanged.Add(AoMudarCidadania);
                    ativado = true;
                    Anota("ATIVO por " + origem + " - vigiando CitizenshipChanged, federacao \""
                          + NomeDaFederacao + "\", espera " + EsperaSegundos + "s");
                }
                catch (Exception e)
                {
                    Anota("[XX] NAO consegui registrar o ouvinte: " + e.Message);
                }
            }
        }

        private static Settlement AchaFederacao()
        {
            try { return Registrars.Get<Settlement>().GetByName(NomeDaFederacao) as Settlement; }
            catch (Exception e) { Anota("[XX] erro ao procurar a federacao: " + e.Message); return null; }
        }

        /// <summary>Chamado pelo jogo quando a cidadania de alguem muda, em qualquer assentamento.</summary>
        private static void AoMudarCidadania(User user, Settlement assentamento, bool entrou)
        {
            if (user == null || entrou) return;   // so interessa quem SAIU

            // O adiamento existe porque este evento dispara DURANTE a remocao. Devolver no
            // mesmo instante correria o risco de o proprio jogo desfazer logo em seguida.
            ThreadUtils.Delay(EsperaSegundos, () =>
            {
                try
                {
                    var fed = AchaFederacao();
                    if (fed == null)
                    {
                        Anota("[!!] nao achei assentamento chamado \"" + NomeDaFederacao
                              + "\" -- foi renomeado? " + user.Name + " ficou sem cidadania.");
                        return;
                    }

                    // HasCitizen cobre cidadania direta E por assentamento-filho. Quem fundou
                    // cidade continua cidadao por heranca, entao aqui nao entra -- de proposito.
                    if (fed.Citizenship.HasCitizen(user)) return;

                    fed.Citizenship.DirectCitizenRoster.AddToRoster(user, user, false, true);

                    var deu = fed.Citizenship.HasCitizen(user);
                    Anota((deu ? "devolvido: " : "[XX] TENTEI e NAO colou: ") + user.Name
                          + " -> cidadao direto de " + NomeDaFederacao
                          + " (saiu de " + (assentamento != null ? assentamento.Name : "?") + ")");
                }
                catch (Exception e)
                {
                    Anota("[XX] falhei ao devolver " + (user != null ? user.Name : "?") + ": " + e.Message);
                }
            });
        }

        /// <summary>Prova de vida em arquivo: compilar nao e funcionar, e carregar nao e funcionar.</summary>
        private static void Anota(string texto)
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
}
