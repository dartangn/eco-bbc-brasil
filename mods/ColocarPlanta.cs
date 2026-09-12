// ColocarPlanta.cs -- Servidor Kabong Brasil, 05/09/2026
//
// Coloca uma construcao pronta ("planta") no mundo, a partir de um arquivo de texto em
// /opt/eco/plantas/<nome>.txt, na posicao do jogador. Substitui o EcoWorldEdit, que derruba
// o Eco 0.14.1.0 por colisao do comando /export (CLAUDE.md 44.1).
//
// Formato do arquivo (gerado do .ecobp pelo mansao/LuckyMansion.compacto.json):
//   b x y z NomeDoBloco                  bloco, posicao relativa ao jogador
//   o x y z NomeDoObjeto qx qy qz qw     objeto do mundo, com rotacao (quaternion)
//   # comentario
//
// Toda chamada e API do jogo, com procedencia no proprio __core__ desta versao:
//   World.SetBlock(Type, Vector3i)                 PaintingCommands.cs:81
//   World.DeleteBlock(Vector3i)                    QACommands.cs:98
//   World.GetBlock(Vector3i)                       PaintingCommands.cs:162
//   user.Position.XYZi()                           PaintingCommands.cs:36
//   WorldObjectManager.ForceAdd(Type, User, Vector3i, Quaternion, bool)   StarterCampItem.cs:64
//   new Quaternion(x, y, z, w)                     StarterCampItem.cs:50
//   Log.WriteLine(Localizer.Do(...))               CustoEstrelas.cs
// Resolucao de tipo por nome: varre as assemblies carregadas procurando classes que herdam
// de Block / WorldObject (o mesmo que o GetTypeFromName do jogo faz para objetos).
//
// Regras do projeto: sem Harmony, sem override, sem editar __core__; prova de vida em arquivo.

namespace Eco.Mods.KabongBrasil
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using Eco.Core.Plugins;
    using Eco.Core.Plugins.Interfaces;
    using Eco.Gameplay.Objects;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Systems.Messaging.Chat.Commands;
    using Eco.Shared.Localization;
    using Eco.Shared.Logging;
    using Eco.Shared.Math;
    using Eco.World;
    using Eco.World.Blocks;

    public class ColocarPlantaMod : IModInit
    {
        public const string Pasta = "/opt/eco/plantas";
        public const string Diario = "/opt/eco/planta-vida.txt";

        public static void Initialize()
        {
            try { Directory.CreateDirectory(Pasta); } catch { }
            Anota("Initialize: ColocarPlanta ativo. Pasta " + Pasta);
            Log.WriteLine(Localizer.Do($"[Kabong] ColocarPlanta ativo. Plantas em {Pasta}"));
        }

        public static ModRegistration Register() => new ModRegistration
        {
            ModName = "KabongBrasil.ColocarPlanta",
            ModDescription = "Coloca construcoes prontas a partir de arquivos em /opt/eco/plantas",
            ModDisplayName = "Kabong Brasil - Colocar Planta",
        };

        public static void Anota(string texto)
        {
            try { File.AppendAllText(Diario, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\n"); }
            catch { }
        }
    }

    // --- resolucao de tipos por nome simples -------------------------------------------
    public static class Tipos
    {
        static Dictionary<string, Type> blocos;
        static Dictionary<string, Type> objetos;
        static readonly object trava = new object();

        static void Carregar()
        {
            if (blocos != null) return;
            lock (trava)
            {
                if (blocos != null) return;
                var b = new Dictionary<string, Type>();
                var o = new Dictionary<string, Type>();
                foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
                {
                    Type[] tipos;
                    try { tipos = asm.GetTypes(); }
                    catch (System.Reflection.ReflectionTypeLoadException e) { tipos = e.Types.Where(t => t != null).ToArray(); }
                    catch { continue; }
                    foreach (var t in tipos)
                    {
                        if (t == null || t.IsAbstract) continue;
                        if (typeof(Block).IsAssignableFrom(t)) { if (!b.ContainsKey(t.Name)) b[t.Name] = t; }
                        else if (typeof(WorldObject).IsAssignableFrom(t)) { if (!o.ContainsKey(t.Name)) o[t.Name] = t; }
                    }
                }
                objetos = o;
                blocos = b;
            }
        }

        public static Type Bloco(string nome) { Carregar(); return blocos.TryGetValue(nome, out var t) ? t : null; }
        public static Type Objeto(string nome) { Carregar(); return objetos.TryGetValue(nome, out var t) ? t : null; }
        public static int QuantosBlocos { get { Carregar(); return blocos.Count; } }
        public static int QuantosObjetos { get { Carregar(); return objetos.Count; } }
    }

    // --- a planta lida do arquivo ----------------------------------------------------------
    public class Planta
    {
        public string Nome;
        public readonly List<(Vector3i pos, string tipo)> Blocos = new List<(Vector3i, string)>();
        public readonly List<(Vector3i pos, string tipo, Quaternion rot)> Objetos = new List<(Vector3i, string, Quaternion)>();
        public readonly List<string> Comentarios = new List<string>();

        public static Planta Ler(string nome)
        {
            var caminho = Path.Combine(ColocarPlantaMod.Pasta, nome + ".txt");
            if (!File.Exists(caminho)) return null;
            var p = new Planta { Nome = nome };
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            foreach (var linha in File.ReadLines(caminho))
            {
                if (linha.Length == 0) continue;
                if (linha[0] == '#') { p.Comentarios.Add(linha); continue; }
                var c = linha.Split(' ');
                if (c[0] == "b" && c.Length >= 5)
                    p.Blocos.Add((new Vector3i(int.Parse(c[1]), int.Parse(c[2]), int.Parse(c[3])), c[4]));
                else if (c[0] == "o" && c.Length >= 9)
                    p.Objetos.Add((new Vector3i(int.Parse(c[1]), int.Parse(c[2]), int.Parse(c[3])), c[4],
                        new Quaternion(float.Parse(c[5], inv), float.Parse(c[6], inv), float.Parse(c[7], inv), float.Parse(c[8], inv))));
            }
            return p;
        }
    }

    // --- o que a ultima colocacao mudou, para desfazer ------------------------------------
    public static class Desfazer
    {
        public static readonly List<(Vector3i pos, Type anterior)> BlocosAnteriores = new List<(Vector3i, Type)>();
        public static readonly List<WorldObject> ObjetosCriados = new List<WorldObject>();
        public static string Descricao = "";
    }

    [ChatCommandHandler]
    public static class PlantaComandos
    {
        [ChatCommand("Colocar construcao pronta - BBC-Brasil", ChatAuthorizationLevel.Admin)]
        public static void Planta() { }

        [ChatSubCommand("Planta", "Lista as plantas disponiveis em /opt/eco/plantas", ChatAuthorizationLevel.Admin)]
        public static void Listar(User user)
        {
            var arqs = Directory.Exists(ColocarPlantaMod.Pasta) ? Directory.GetFiles(ColocarPlantaMod.Pasta, "*.txt") : new string[0];
            if (arqs.Length == 0) { user.Player?.MsgLocStr("Nenhuma planta em " + ColocarPlantaMod.Pasta); return; }
            user.Player?.MsgLocStr("Plantas: " + string.Join(", ", arqs.Select(Path.GetFileNameWithoutExtension)));
        }

        [ChatSubCommand("Planta", "Mostra tamanho, blocos e objetos de uma planta, e o que o jogo nao conhece", ChatAuthorizationLevel.Admin)]
        public static void Info(User user, string nome)
        {
            var p = Eco.Mods.KabongBrasil.Planta.Ler(nome);
            if (p == null) { user.Player?.MsgLocStr("Nao achei /opt/eco/plantas/" + nome + ".txt"); return; }
            var faltamB = p.Blocos.Select(b => b.tipo).Distinct().Where(t => t != "EmptyBlock" && Tipos.Bloco(t) == null).ToList();
            var faltamO = p.Objetos.Select(o => o.tipo).Distinct().Where(t => Tipos.Objeto(t) == null).ToList();
            var construcao = p.Blocos.Count(b => b.pos.y >= 0 && b.tipo != "EmptyBlock");
            var terreno = p.Blocos.Count(b => b.pos.y < 0 && b.tipo != "EmptyBlock");
            var ar = p.Blocos.Count(b => b.tipo == "EmptyBlock");
            user.Player?.MsgLocStr(string.Format("{0}: {1} blocos de construcao, {2} de terreno (y<0), {3} de ar, {4} objetos. Tipos conhecidos pelo jogo: {5} blocos, {6} objetos.",
                nome, construcao, terreno, ar, p.Objetos.Count, Tipos.QuantosBlocos, Tipos.QuantosObjetos));
            if (faltamB.Count > 0) user.Player?.MsgLocStr("Blocos que o jogo NAO conhece (serao pulados): " + string.Join(", ", faltamB));
            if (faltamO.Count > 0) user.Player?.MsgLocStr("Objetos que o jogo NAO conhece (serao pulados): " + string.Join(", ", faltamO));
            foreach (var c in p.Comentarios.Take(3)) user.Player?.MsgLocStr(c);
        }

        [ChatSubCommand("Planta", "Coloca so a construcao (blocos com y>=0, sem ar e sem terreno) a partir da sua posicao", ChatAuthorizationLevel.Admin)]
        public static void Colocar(User user, string nome)
        {
            ColocarBlocos(user, nome, incluirTerreno: false, incluirAr: false);
        }

        [ChatSubCommand("Planta", "Coloca TUDO: construcao, terreno abaixo e ar (escava). Pode demorar", ChatAuthorizationLevel.Admin)]
        public static void ColocarTudo(User user, string nome)
        {
            ColocarBlocos(user, nome, incluirTerreno: true, incluirAr: true);
        }

        static void ColocarBlocos(User user, string nome, bool incluirTerreno, bool incluirAr)
        {
            var p = Eco.Mods.KabongBrasil.Planta.Ler(nome);
            if (p == null) { user.Player?.MsgLocStr("Nao achei /opt/eco/plantas/" + nome + ".txt"); return; }
            var origem = user.Position.XYZi();
            Desfazer.BlocosAnteriores.Clear();
            Desfazer.ObjetosCriados.Clear();
            Desfazer.Descricao = nome + " em " + origem;
            int feitos = 0, pulados = 0, desconhecidos = 0;
            var faltando = new HashSet<string>();
            foreach (var (rel, tipo) in p.Blocos)
            {
                if (!incluirTerreno && rel.y < 0) { pulados++; continue; }
                var ehAr = tipo == "EmptyBlock";
                if (ehAr && !incluirAr) { pulados++; continue; }
                var pos = origem + rel;
                Type t = null;
                if (!ehAr)
                {
                    t = Tipos.Bloco(tipo);
                    if (t == null) { desconhecidos++; faltando.Add(tipo); continue; }
                }
                try
                {
                    var atual = World.GetBlock(pos);
                    Desfazer.BlocosAnteriores.Add((pos, atual?.GetType()));
                    if (ehAr) World.DeleteBlock(pos); else World.SetBlock(t, pos);
                    feitos++;
                }
                catch (Exception e) { desconhecidos++; faltando.Add(tipo + ":" + e.GetType().Name); }
            }
            var msg = string.Format("Planta {0}: {1} blocos colocados, {2} pulados, {3} sem tipo. Origem {4}. Use /planta objetos {0} para a mobilia, /planta desfazer para voltar.",
                nome, feitos, pulados, desconhecidos, origem);
            user.Player?.MsgLocStr(msg);
            if (faltando.Count > 0) user.Player?.MsgLocStr("Sem tipo: " + string.Join(", ", faltando.Take(20)));
            ColocarPlantaMod.Anota(user.Name + " colocou " + msg + (faltando.Count > 0 ? " faltando=" + string.Join(",", faltando) : ""));
        }

        [ChatSubCommand("Planta", "Coloca os objetos (mobilia, portas, luzes) da planta a partir da sua posicao -- fique no MESMO lugar do /planta colocar", ChatAuthorizationLevel.Admin)]
        public static void Objetos(User user, string nome)
        {
            var p = Eco.Mods.KabongBrasil.Planta.Ler(nome);
            if (p == null) { user.Player?.MsgLocStr("Nao achei /opt/eco/plantas/" + nome + ".txt"); return; }
            var origem = user.Position.XYZi();
            int feitos = 0, falhas = 0;
            var faltando = new HashSet<string>();
            foreach (var (rel, tipo, rot) in p.Objetos)
            {
                var t = Tipos.Objeto(tipo);
                if (t == null) { falhas++; faltando.Add(tipo); continue; }
                try
                {
                    var obj = WorldObjectManager.ForceAdd(t, user, origem + rel, rot, false);
                    if (obj != null) { Desfazer.ObjetosCriados.Add(obj); feitos++; } else { falhas++; faltando.Add(tipo + ":null"); }
                }
                catch (Exception e) { falhas++; faltando.Add(tipo + ":" + e.GetType().Name); }
            }
            var msg = string.Format("Planta {0}: {1} objetos colocados, {2} falharam.", nome, feitos, falhas);
            user.Player?.MsgLocStr(msg);
            if (faltando.Count > 0) user.Player?.MsgLocStr("Falharam: " + string.Join(", ", faltando.Take(20)));
            ColocarPlantaMod.Anota(user.Name + " " + msg + (faltando.Count > 0 ? " faltando=" + string.Join(",", faltando) : ""));
        }

        [ChatSubCommand("Planta", "Desfaz a ultima colocacao: devolve os blocos anteriores e remove os objetos criados", ChatAuthorizationLevel.Admin)]
        public static void DesfazerUltima(User user)
        {
            int b = 0, o = 0;
            foreach (var obj in Desfazer.ObjetosCriados) { try { obj.Destroy(); o++; } catch { } }
            Desfazer.ObjetosCriados.Clear();
            for (int i = Desfazer.BlocosAnteriores.Count - 1; i >= 0; i--)
            {
                var (pos, anterior) = Desfazer.BlocosAnteriores[i];
                try
                {
                    if (anterior == null || anterior == typeof(EmptyBlock)) World.DeleteBlock(pos); else World.SetBlock(anterior, pos);
                    b++;
                }
                catch { }
            }
            Desfazer.BlocosAnteriores.Clear();
            var msg = string.Format("Desfeito ({0}): {1} blocos devolvidos, {2} objetos removidos.", Desfazer.Descricao, b, o);
            user.Player?.MsgLocStr(msg);
            ColocarPlantaMod.Anota(user.Name + " " + msg);
        }
    }
}
