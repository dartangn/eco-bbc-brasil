// ============================================================================
// MoedasIniciais.cs  --  Servidor Kabong Brasil / BBC-Brasil
//
// O QUE FAZ
//   Jogador novo, no PRIMEIRO login, recebe alem do que o Starter Rewards ja da
//   (500 Real e 2 estrelas de especialidade):
//       10  de "Moeda para Papel de Propriedade"
//        3  de "Moeda para Estacas"
//   Pedido do Raul em 11/09/2026. Sao as moedas com que se compram papel de
//   reivindicacao e estaca nas lojas da federacao.
//
// POR QUE UM ARQUIVO NOSSO, E NAO MEXER NO STARTER REWARDS
//   1. O Starter Rewards so aceita UMA moeda: a config dele tem CurrencyName e
//      StartingAmount, no singular. Nao ha como pedir tres.
//   2. Editar mod de terceiro morre em silencio na proxima atualizacao dele.
//   3. E, o mais importante: foi o EnsureCurrency() do Starter Rewards que
//      CORROMPEU O MUNDO em 03/09/2026 -- ele CRIA a moeda quando nao encontra
//      pelo nome, e criou uma segunda com o mesmo nome, o que fez o servidor
//      parar de subir ("An item with the same key has already been added. Key:
//      <nome do primeiro admin>") por mais de uma hora, ate restaurarmos backup.
//
//   ESTE ARQUIVO NUNCA CRIA MOEDA. Se nao achar, nao faz nada e anota no diario.
//   E a diferenca que separa dar dinheiro de derrubar o servidor.
//
// POR QUE CASAR POR INICIO DO NOME, e nao por igualdade
//   O `/money currencies` pelo RCON devolve "Moeda para Papel de Propriedad" --
//   exatamente 30 caracteres, o que cheira a corte de largura de coluna. A tela
//   do jogo (print do Raul, 11/09/2026) tambem termina em "d". Ou o nome e mesmo
//   sem o "e" final, ou as duas telas cortam no mesmo ponto -- e nao da para
//   saber olhando. Casando por igualdade exata, um "e" a mais ou a menos faria o
//   mod NAO achar a moeda e NAO dar nada, sem erro nenhum. Por isso casa por
//   inicio (StartsWith), que acerta nos dois casos, e o diario grava o nome
//   COMPLETO que encontrou -- e ai ficamos sabendo qual e o de verdade.
//
// FORMAS COPIADAS do StarterRewardsPlugin.cs, que COMPILA neste servidor:
//   UserManager.OnUserLoggedIn.Add(metodo)
//   user.FirstLogin
//   CurrencyManager.Currencies.FirstOrDefault(c => c.Name == ...)
//   user.BankAccount.AddCurrency(moeda, valor)
//   user.Player?.MsgLocStr(texto)
//
// PRE-VOO: conferir-cs-novo.py antes de instalar.
// INSTALACAO: so com arranque VIGIADO (Regra 18 do ESTADO.md).
// REVERTER: apagar o arquivo.
// ============================================================================

namespace Eco.Mods.KabongBrasil
{
    using System;
    using System.Linq;
    using Eco.Core.Plugins.Interfaces;   // IModInit
    using Eco.Gameplay.Economy;          // CurrencyManager, Currency
    using Eco.Gameplay.Players;          // User, UserManager
    using Eco.Shared.Utils;

    public class MoedasIniciais : IModInit
    {
        // ---------------------------------------------------------------- AJUSTE AQUI
        /// <summary>Inicio do nome de cada moeda e quanto dar. O inicio basta: ver o cabecalho
        /// sobre o corte de 30 caracteres do RCON.</summary>
        private static readonly string[] moedas =
        {
            "Moeda para Papel de Propriedad",
            "Moeda para Estacas",
        };

        private static readonly float[] quantidades = { 10f, 3f };
        // ------------------------------------------------------------ FIM DO AJUSTE

        private const string Diario = "/opt/eco/moedas-iniciais-vida.txt";
        private static readonly object Tranca = new object();
        private static bool ativado;

        public static void Initialize()
        {
            lock (Tranca)
            {
                if (ativado) return;   // idempotente: o Eco pode chamar o gancho mais de uma vez
                try
                {
                    UserManager.OnUserLoggedIn.Add(AoEntrar);
                    ativado = true;
                    Anota("ATIVO - " + moedas.Length + " moeda(s) no primeiro login: "
                          + moedas[0] + "=" + quantidades[0] + ", " + moedas[1] + "=" + quantidades[1]);
                }
                catch (Exception e) { Anota("[XX] nao consegui registrar o ouvinte: " + e.Message); }
            }
        }

        private static void AoEntrar(User user)
        {
            try
            {
                if (user == null || !user.FirstLogin) return;   // so jogador NOVO
                if (user.BankAccount == null) { Anota("[!!] " + user.Name + " entrou sem conta bancaria"); return; }

                var deu = 0;
                for (var i = 0; i < moedas.Length && i < quantidades.Length; i++)
                {
                    var inicio = moedas[i];
                    var valor = quantidades[i];

                    // NUNCA cria: so procura entre as que ja existem.
                    var moeda = CurrencyManager.Currencies.FirstOrDefault(
                        c => c != null && c.Name != null &&
                             c.Name.StartsWith(inicio, StringComparison.OrdinalIgnoreCase));

                    if (moeda == null)
                    {
                        Anota("[!!] nenhuma moeda comeca com \"" + inicio + "\" -- " + user.Name
                              + " NAO recebeu esta. (Nao criei nenhuma, de proposito.)");
                        continue;
                    }

                    user.BankAccount.AddCurrency(moeda, valor);
                    deu++;
                    Anota("dei " + valor + " de \"" + moeda.Name + "\" para " + user.Name);
                }

                if (deu > 0)
                {
                    try
                    {
                        user.Player?.MsgLocStr(
                            "<color=green>Bem-vindo!</color> Voce tambem recebeu 10 de Moeda para Papel de "
                            + "Propriedade e 3 de Moeda para Estacas, para pegar seu terreno.");
                    }
                    catch { }
                }
            }
            catch (Exception e)
            {
                Anota("[XX] falhei com " + (user != null ? user.Name : "?") + ": " + e.Message);
            }
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
