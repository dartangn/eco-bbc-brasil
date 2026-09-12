# -*- coding: utf-8 -*-
"""
gerar-plantas-crescimento.py -- GERA o PlantasCrescimento.cs, que aplica a TODAS as plantas os
mesmos fatores de crescimento que o ArvoresDensas.cs aplicou as 10 arvores.

PEDIDO DO RAUL, 12/09/2026: "coloca o crescimento de todas as plantas igual as arvores".

OS FATORES, identicos aos das arvores (secao 32 do CLAUDE.md):
    MaturityAgeDays x0.4      amadurece em 40% do tempo
    SeedingTime     x0.4      semeia com 40% do intervalo
    SeedsCount      x2        o dobro de sementes por evento
    SpreadRate      x3        espalha 3x mais rapido

QUEM ENTRA E QUEM FICA DE FORA -- e o gerador decide isso LENDO o servidor, nao por lista minha:
  ENTRAM   as 57 `PlantSpecies` (capim, musgo, cogumelo, alga, arbusto, fruta, legume, cereal...)
  FICAM DE FORA:
    - as 10 arvores que o ArvoresDensas.cs JA altera. Duas implementacoes do mesmo metodo parcial
      dao CS0111 e o servidor nao sobe -- o gerador le aquele arquivo e exclui o que achar la.
    - a OldGrowthRedwood, que a Strange Loop declara NAO-RENOVAVEL de proposito
      (MaturityAgeDays 30, SpreadRate 0, e sem SeedingTime/SeedsCount). Mexer apagaria uma
      decisao de jogo deliberada, e ela nem tem os campos.
    - qualquer especie a que falte um dos 4 campos -- nao da para multiplicar o que nao existe.

FORMA, copiada do ArvoresDensas.cs que JA COMPILA neste servidor:
    namespace Eco.Mods.Organisms
        public partial class Cotton            <- classe EXTERNA (no jogo: Cotton : PlantEntity)
            public partial class CottonSpecies  <- ANINHADA    (no jogo: CottonSpecies : PlantSpecies)
                partial void ModsPostInitialize() { ... }
O ModsPostInitialize() e a ULTIMA linha do construtor da especie, e os mods carregam ANTES da
geracao do mundo -- entao o valor novo ja vale para o mundo existente. NAO precisa de wipe.
(Densidade de geracao e outra coisa e exigiria mundo novo; este arquivo NAO mexe nisso.)

NUMEROS ABSOLUTOS, com o original ao lado em comentario -- regra deste projeto desde a pa: nada
de multiplicador escondido no codigo, para dar para conferir a olho o que cada especie ficou.

USO (no servidor, como ecosrv):
    sudo -u ecosrv python3 /opt/eco/scripts-py/gerar-plantas-crescimento.py --resumo
    sudo -u ecosrv python3 /opt/eco/scripts-py/gerar-plantas-crescimento.py > /tmp/PlantasCrescimento.cs

Depois de ATUALIZAR O ECO, rodar de novo. PRE-VOO no arquivo gerado (conferir-cs-novo.py) e
instalacao SO com arranque vigiado (Regra 18 do ESTADO.md).
"""
import io, os, re, sys

PLANTAS = "/opt/eco/server/Mods/__core__/AutoGen/Plant"
NOSSO_ARVORES = "/opt/eco/server/Mods/UserCode/KabongBrasil/ArvoresDensas.cs"

# ---------------------------------------------------------------- AJUSTE AQUI
# Especies que NAO entram, por decisao de jogo. Nome como aparece no arquivo, sem "Species".
# CAPIM fora a pedido do Raul (12/09/2026): sao eles que invadem terreno arado, e espalhar 3x
# mais rapido daria mais trabalho de capinar a quem planta -- o oposto do objetivo, que e a
# agricultura render mais. Tirar um nome desta lista o faz voltar a entrar.
EXCLUIR = {"CommonGrass", "Bunchgrass", "Switchgrass", "BigBluestem"}

FATOR_MATURIDADE = 0.4
FATOR_SEMEADURA = 0.4
FATOR_SEMENTES = 2
FATOR_ESPALHA = 3

re_especie = re.compile(r"public\s+partial\s+class\s+(\w+)Species\s*:\s*PlantSpecies")
re_externa = re.compile(r"public\s+partial\s+class\s+(\w+)\s*:\s*PlantEntity")
CAMPOS = ("MaturityAgeDays", "SeedingTime", "SeedsCount", "SpreadRate")


def valor(texto, campo):
    m = re.search(r"this\.%s\s*=\s*([0-9.]+)f?\s*;" % campo, texto)
    return m.group(1) if m else None


def num(s):
    return float(s)


def fmt(x, inteiro=False):
    """Numero em C#, sem depender de virgula/ponto de locale."""
    if inteiro:
        return str(int(round(x)))
    s = ("%.6f" % x).rstrip("0").rstrip(".")
    return (s if s else "0") + "f"


# --- quem o ArvoresDensas.cs ja trata: excluir, senao CS0111 (metodo parcial implementado 2x)
ja_tratadas = set()
if os.path.exists(NOSSO_ARVORES):
    ja_tratadas = set(re.findall(r"class\s+(\w+)Species",
                                 io.open(NOSSO_ARVORES, encoding="utf-8", errors="replace").read()))

itens, pulados = [], []
for a in sorted(os.listdir(PLANTAS)):
    if not a.endswith(".cs"):
        continue
    t = io.open(os.path.join(PLANTAS, a), encoding="utf-8", errors="replace").read()
    me, mx = re_especie.search(t), re_externa.search(t)
    if not me:
        continue                      # e TreeSpecies ou nao e especie
    # ATENCAO: o grupo do regex traz o nome SEM o sufixo -- "Cotton", nao "CottonSpecies".
    # Usar o grupo cru batizava a classe aninhada com o mesmo nome da externa, o que e erro de
    # compilacao em C# (nome de membro igual ao do tipo que o contem). Pego em 12/09/2026 olhando
    # a amostra do arquivo gerado: o pre-voo NAO acusa isso, porque nao e tipo nem chave.
    nome = me.group(1)
    especie, externa = nome + "Species", (mx.group(1) if mx else None)
    if externa is None:
        pulados.append((nome, "nao achei a classe externa : PlantEntity"))
        continue
    if nome in ja_tratadas:
        pulados.append((nome, "ja alterada pelo ArvoresDensas.cs"))
        continue
    if nome in EXCLUIR:
        pulados.append((nome, "na lista EXCLUIR (decisao de jogo)"))
        continue
    if "partial void ModsPostInitialize();" not in t:
        pulados.append((nome, "sem o gancho ModsPostInitialize"))
        continue
    v = dict((c, valor(t, c)) for c in CAMPOS)
    falta = [c for c in CAMPOS if v[c] is None]
    if falta:
        pulados.append((nome, "faltam campos: " + ", ".join(falta)))
        continue
    itens.append({
        "externa": externa, "especie": especie, "nome": nome,
        "mat0": v["MaturityAgeDays"], "sem0": v["SeedingTime"],
        "cnt0": v["SeedsCount"], "esp0": v["SpreadRate"],
        "mat1": num(v["MaturityAgeDays"]) * FATOR_MATURIDADE,
        "sem1": num(v["SeedingTime"]) * FATOR_SEMEADURA,
        "cnt1": num(v["SeedsCount"]) * FATOR_SEMENTES,
        "esp1": num(v["SpreadRate"]) * FATOR_ESPALHA,
    })

if "--resumo" in sys.argv:
    print("especies que ENTRAM: %d" % len(itens))
    for i in itens:
        print("  %-20s maturidade %-7s -> %-7s  semeia %-6s -> %-6s  sementes %s -> %s  espalha %-7s -> %s"
              % (i["nome"], i["mat0"], fmt(i["mat1"]), i["sem0"], fmt(i["sem1"]),
                 i["cnt0"], fmt(i["cnt1"], True), i["esp0"], fmt(i["esp1"])))
    print()
    print("FICAM DE FORA: %d" % len(pulados))
    for nome, por in pulados:
        print("  %-20s %s" % (nome, por))
    sys.exit(0)

if not itens:
    sys.exit("[XX] nenhuma especie encontrada -- a varredura falhou. Nada foi gerado.")

CAB = '''// ============================================================================
// PlantasCrescimento.cs  --  Servidor Kabong Brasil / BBC-Brasil
// GERADO por gerar-plantas-crescimento.py -- NAO EDITE A MAO.
//
// Aplica a TODAS as %(n)d plantas (PlantSpecies) os MESMOS fatores de crescimento
// que o ArvoresDensas.cs aplicou as 10 arvores, a pedido do Raul em 12/09/2026:
//
//     MaturityAgeDays x%(fm)s      SeedingTime x%(fs)s      SeedsCount x%(fc)d      SpreadRate x%(fe)d
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
                        DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\\n");
                }
            }
            catch { }
        }
    }
''' % {"n": len(itens), "fm": FATOR_MATURIDADE, "fs": FATOR_SEMEADURA,
       "fc": FATOR_SEMENTES, "fe": FATOR_ESPALHA}

MOLDE = '''
    public partial class %(externa)s
    {
        public partial class %(especie)s
        {
            partial void ModsPostInitialize()
            {
                this.MaturityAgeDays = %(mat1)s;   // jogo: %(mat0)s
                this.SeedingTime     = %(sem1)s;   // jogo: %(sem0)s
                this.SeedsCount      = %(cnt1)s;   // jogo: %(cnt0)s
                this.SpreadRate      = %(esp1)s;   // jogo: %(esp0)s
                KabongPlantasDiario.Anota("%(nome)s: maturidade %(mat0)s->%(mat1)s, semeia %(sem0)s->%(sem1)s, sementes %(cnt0)s->%(cnt1)s, espalha %(esp0)s->%(esp1)s");
            }
        }
    }
'''

partes = [CAB]
for i in itens:
    d = dict(i)
    d["mat1"] = fmt(i["mat1"])
    d["sem1"] = fmt(i["sem1"])
    d["cnt1"] = fmt(i["cnt1"], True)
    d["esp1"] = fmt(i["esp1"])
    partes.append(MOLDE % d)
partes.append("}\n")
texto = "".join(partes)

nao_ascii = sorted(set(c for c in texto if ord(c) > 127))
if nao_ascii:
    sys.exit("[XX] o arquivo gerado tem caractere nao-ASCII: %r" % nao_ascii)
if texto.count("{") != texto.count("}"):
    sys.exit("[XX] chaves desbalanceadas: %d abre, %d fecha" % (texto.count("{"), texto.count("}")))

sys.stdout.write(texto)
sys.stderr.write("[ok] %d especies geradas; %d ficaram de fora\n" % (len(itens), len(pulados)))
for nome, por in pulados:
    sys.stderr.write("     fora: %-20s %s\n" % (nome, por))
