// KabongLog.cs -- Servidor Kabong Brasil
//
// Diario de diagnostico compartilhado pelos nossos overrides.
//
// POR QUE EM ARQUIVO SEPARADO, E NAO DENTRO DO OVERRIDE
//   O bloco que injetamos no TreeObject.override.cs entra no CORPO de um metodo
//   (FellTree), e C# nao permite declarar metodo ali. Ter o logger aqui evita um segundo
//   ponto de injecao no arquivo mais volatil do jogo, e serve tambem para o PickaxeItem
//   quando chegarmos na pedra.
//
// POR QUE ARQUIVO E NAO Log.WriteLine
//   Nao depende do logger do Eco estar pronto, nao se mistura com as centenas de linhas
//   do log do servidor, e da para ler com um comando so. Mesma razao dos outros diarios
//   deste projeto (custo-estrelas-vida.txt e afins). Console.WriteLine NAO serve: o
//   compilador de mods do Eco nao referencia System.Console (CS0103, ja testado).

namespace Eco.Mods.KabongBrasil   // 07/09/2026: os overrides vivem em Eco.Mods.*, e la KabongBrasil.X resolve para Eco.Mods.KabongBrasil (CS0234 com o namespace raiz)
{
    using System;

    public static class KabongLog
    {
        public const string ArquivoTronco = @"/opt/eco/tronco-vida.txt";
        public const string ArquivoPedra  = @"/opt/eco/pedra-vida.txt";
        public const string ArquivoArvore = @"/opt/eco/arvores-vida.txt";

        /// <summary>Nunca lanca: diagnostico nao pode derrubar jogabilidade.</summary>
        public static void Tronco(string texto) { Escreve(ArquivoTronco, texto); }

        /// <summary>Idem, para a mineracao.</summary>
        public static void Pedra(string texto) { Escreve(ArquivoPedra, texto); }

        /// <summary>Densidade de arvore. Escreve so no ARRANQUE (uma linha por especie),
        /// nao por acao do jogador - por isso pode ficar ligado.</summary>
        public static void Arvore(string texto) { Escreve(ArquivoArvore, texto); }

        private static void Escreve(string arquivo, string texto)
        {
            try
            {
                System.IO.File.AppendAllText(arquivo,
                    DateTime.Now.ToString("HH:mm:ss.fff") + "  " + texto + "\r\n");
            }
            catch { }   // AppendAllText falha se o arquivo estiver travado por outra chamada.
                        // Consequencia conhecida: linha ausente NAO prova ausencia de execucao.
        }
    }
}
