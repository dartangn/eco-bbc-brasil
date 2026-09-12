// PonteServidor.cs -- Servidor Kabong Brasil, 08/09/2026
//
// PONTE ENTRE OS SCRIPTS DO SERVIDOR E O JOGO, sem depender de jogador logado.
//
// POR QUE: dois comandos que o eco-reiniciar.sh mandava pelo RCON nao funcionam de fora:
//   - "/world clearallrubble" responde "Cannot call function clearallrubble from RCON, it
//     requires a in-game user" (visto em 08/09 10:04);
//   - "/manage announce ..." responde vazio e os jogadores NAO viram o aviso (Raul, 08/09).
// A API web (/api/v1/chat/sendChat, /command/exec) exige authtoken de usuario, que nao temos.
//
// COMO: este mod vigia a pasta /opt/eco/ponte a cada 5 s:
//   - arquivo  anuncio.txt      -> manda o texto a todos NO CHAT (NotificationManager.ServerMessageToAll,
//                                 a MESMA chamada que o __core__/Commands/SimCommands.cs usa) e apaga
//   - arquivo  alerta.txt       -> CAIXA COM OK para cada jogador online (Player.OkBoxLocStr por reflexao;
//                                 se nao existir, Player.InfoBoxLocStr, que o UserCode ja chama) e apaga.
//                                 Campo 08/09: o announce "pisca rapido demais para ler"; o alert "ficou na
//                                 tela ate darem OK" -- o reinicio diario usa este.
//   - arquivo  limpar-entulho   -> chama RubbleObject.ClearAllRubble (o que o /world clearallrubble
//                                 chama; achado por REFLEXAO porque a classe vive na DLL do jogo e
//                                 nao ha fonte para conferir a assinatura) e apaga
// Tudo o que faz vai para /opt/eco/ponte-vida.txt (prova de vida + resultado de cada pedido).
// Quem escreve na pasta: o usuario ecosrv (os scripts fazem sudo -u ecosrv). Nunca lanca excecao
// para fora: diagnostico nao derruba servidor.
//
// PARA DESATIVAR: apagar este arquivo e reiniciar.

namespace Eco.Mods.KabongBrasil
{
    using Eco.Core.Plugins;
    using Eco.Core.Plugins.Interfaces;
    using Eco.Gameplay.Objects;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Systems.Messaging.Notifications;
    using Eco.Shared.Localization;
    using Eco.Shared.Logging;
    using System;
    using System.IO;
    using System.Linq;
    using System.Reflection;
    using System.Threading;

    public class PonteServidorMod : IModInit
    {
        const string Pasta   = "/opt/eco/ponte";
        const string Diario  = "/opt/eco/ponte-vida.txt";
        const string Anuncio = Pasta + "/anuncio.txt";
        const string Alerta  = Pasta + "/alerta.txt";
        const string Entulho = Pasta + "/limpar-entulho";

        static Timer vigia;
        static int ocupado;

        public static void Initialize()
        {
            try
            {
                Directory.CreateDirectory(Pasta);
                // primeira varredura 30 s depois do Initialize (o mundo ainda esta carregando), depois a cada 5 s
                vigia = new Timer(_ => Varrer(), null, 30000, 5000);
                Escreve("ATIVO por Initialize -- vigiando " + Pasta);
            }
            catch (Exception ex) { Escreve("ERRO no Initialize: " + ex.Message); }
        }

        public static ModRegistration Register() => new ModRegistration
        {
            ModName        = "KabongPonte",
            ModDescription = "Ponte entre os scripts do servidor e o jogo: anuncios e limpeza de entulho por arquivo.",
            ModDisplayName = "Kabong Ponte",
        };

        static void Varrer()
        {
            if (Interlocked.Exchange(ref ocupado, 1) == 1) return;   // nunca duas varreduras ao mesmo tempo
            try
            {
                if (File.Exists(Anuncio))
                {
                    var texto = File.ReadAllText(Anuncio).Trim();
                    File.Delete(Anuncio);
                    if (texto.Length > 0)
                    {
                        NotificationManager.ServerMessageToAll(Localizer.DoStr(texto));   // 1 argumento: a forma do __core__/Commands/SimCommands.cs:446 (a forma com category: deu CS0103 NotificationCategory em 08/09 e DERRUBOU o servidor)
                        Escreve("anuncio enviado a todos: " + texto);
                    }
                }
                if (File.Exists(Alerta))
                {
                    var texto = File.ReadAllText(Alerta).Trim();
                    File.Delete(Alerta);
                    if (texto.Length > 0) AlertarTodos(texto);
                }
                if (File.Exists(Entulho))
                {
                    File.Delete(Entulho);
                    LimparEntulho();
                }
            }
            catch (Exception ex) { Escreve("ERRO na varredura: " + ex.Message); }
            finally { Interlocked.Exchange(ref ocupado, 0); }
        }

        static void AlertarTodos(string texto)
        {
            var enviados = 0; var modo = "";
            foreach (var u in Eco.Gameplay.Players.UserManager.Users)
            {
                var pl = u?.Player;
                if (pl == null) continue;   // offline
                try
                {
                    var m = pl.GetType().GetMethod("OkBoxLocStr", new[] { typeof(string) });
                    if (m != null) { m.Invoke(pl, new object[] { texto }); modo = "OkBoxLocStr"; }
                    else           { pl.InfoBoxLocStr(texto);              modo = "InfoBoxLocStr (OkBoxLocStr nao achado)"; }
                    enviados++;
                }
                catch (Exception ex) { Escreve("alerta: falhou para " + u.Name + ": " + (ex.InnerException ?? ex).Message); }
            }
            Escreve("alerta enviado a " + enviados + " jogador(es) via " + modo + ": " + texto);
        }

        static void LimparEntulho()
        {
            var tipo = typeof(RubbleObject);
            var metodos = tipo.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance)
                              .Where(m => m.Name == "ClearAllRubble").ToList();
            if (metodos.Count == 0)
            {
                Escreve("entulho: RubbleObject.ClearAllRubble NAO encontrado por reflexao -- nada feito. Metodos com 'Rubble': "
                        + string.Join(", ", tipo.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static).Select(m => m.Name).Where(n => n.Contains("Rubble")).Distinct()));
                return;
            }
            foreach (var m in metodos)
            {
                var ps = m.GetParameters();
                Escreve("entulho: achei " + (m.IsStatic ? "static " : "instancia ") + m.Name + "(" + string.Join(", ", ps.Select(p => p.ParameterType.Name + " " + p.Name)) + ")");
                if (!m.IsStatic) continue;
                try
                {
                    // argumentos: null para referencia (ex.: User), default para valor
                    var args = ps.Select(p => p.ParameterType.IsValueType ? Activator.CreateInstance(p.ParameterType) : null).ToArray();
                    var r = m.Invoke(null, args);
                    Escreve("entulho: ClearAllRubble chamado, retorno = " + (r == null ? "(void/null)" : r.ToString()));
                    return;
                }
                catch (Exception ex) { Escreve("entulho: falhou ao chamar: " + (ex.InnerException ?? ex).Message); }
            }
        }

        static readonly object trava = new object();
        static void Escreve(string texto)
        {
            try { lock (trava) { File.AppendAllText(Diario, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\n"); } } catch { }
            try { Log.WriteLine(Localizer.Do($"[KabongPonte] {texto}")); } catch { }
        }
    }
}
