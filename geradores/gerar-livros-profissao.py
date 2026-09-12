# -*- coding: utf-8 -*-
"""
gerar-livros-profissao.py -- GERA o LivroDaProfissao.cs com uma receita por livro de profissao.

POR QUE EXISTE (Raul, 11/09/2026)
  No livro de habilidades (Z), especialidade NAO DESCOBERTA nao e selecionavel neste servidor --
  o clique nao muda a selecao nem o painel da direita, e o jogador nao ve o que a profissao faz
  antes de gastar estrela. Em servidor VANILLA e clicavel (comparado em video, dois servidores
  lado a lado). A diferenca candidata: o No More Books limpa os produtos das 28 receitas de livro
  do jogo, e o nosso PergaminhosDosMods.cs faz o mesmo nas 3 de mod -- entao NENHUMA receita deste
  servidor produz o item SkillBook.

  Hipotese do Raul: basta o livro ter receita em algum lugar, mesmo impossivel de fabricar.

O QUE O ARQUIVO GERADO FAZ
  Uma receita NOVA por livro (nao altera nenhuma existente), no LABORATORIO, custando
  10.000 pergaminhos da mesma profissao. Inalcancavel de proposito: o livro volta a ser produto
  de uma receita sem voltar a ser fabricavel, e o pergaminho continua sendo o que sai na pratica.

DE ONDE VEM CADA DADO -- tudo lido do servidor, nada inventado:
  class XSkillBook : SkillBook<XSkill, XSkillScroll>   -> livro, habilidade e pergaminho
  [LocDisplayName("...")] do livro                     -> nome que o jogador ve
  [RequiresSkill(typeof(YSkill), N)] da XSkillBookRecipe do JOGO
                                                       -> o MESMO destrave da receita original
  O destrave nao e o mesmo para todos: o livro de Assados e destravado por Milling 1, o de
  Cozimento por Butchery 1, o de Ferraria por Smelting 1. Espelhar isso mantem a logica do jogo.

USO (no servidor, como ecosrv -- /opt/eco e 750):
    sudo -u ecosrv python3 /opt/eco/scripts-py/gerar-livros-profissao.py > /tmp/LivroDaProfissao.cs
    sudo -u ecosrv python3 /opt/eco/scripts-py/gerar-livros-profissao.py --resumo

Depois de ATUALIZAR O ECO, rodar de novo: livros novos entram sozinhos.
PRE-VOO obrigatorio no arquivo gerado (conferir-cs-novo.py) e instalacao SO com arranque
vigiado (Regra 18 do ESTADO.md).
"""
import io, os, re, sys

RAIZ = "/opt/eco/server/Mods"
CUSTO = 10000          # pergaminhos por livro
MESA = "LaboratoryObject"

re_book = re.compile(r"class\s+(\w+)\s*:\s*SkillBook<\s*(\w+)\s*,\s*(\w+)\s*>")
re_gate = re.compile(
    r"\[RequiresSkill\s*\(\s*typeof\s*\(\s*(\w+)\s*\)\s*,\s*(-?\d+)\s*\)[^\]]*\]\s*"
    r"(?:\[[^\]]*\]\s*)*public\s+partial\s+class\s+(\w+SkillBookRecipe)\s*:", re.S)
re_locnome = re.compile(r'\[LocDisplayName\("([^"]+)"\)\]')

livros, gates = {}, {}
for base, _, arqs in os.walk(RAIZ):
    for a in arqs:
        if not a.endswith(".cs"):
            continue
        p = os.path.join(base, a)
        try:
            t = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in re_book.finditer(t):
            antes = t[max(0, m.start() - 600): m.start()]
            ln = re_locnome.findall(antes)
            livros[m.group(1)] = {"skill": m.group(2), "scroll": m.group(3),
                                  "nome": ln[-1] if ln else m.group(1)}
        for m in re_gate.finditer(t):
            gates[m.group(3)] = (m.group(1), int(m.group(2)))

itens = []
sem_gate = []
for b in sorted(livros):
    g = gates.get(b + "Recipe")
    if not g:
        sem_gate.append(b)
        continue
    d = livros[b]
    itens.append({"livro": b, "scroll": d["scroll"], "nome": d["nome"],
                  "gate": g[0], "nivel": g[1],
                  "classe": "Livro" + b[:-len("SkillBook")] + "KabongRecipe"})

if "--resumo" in sys.argv:
    print("livros: %d   com receita no jogo: %d   sem: %d" % (len(livros), len(itens), len(sem_gate)))
    for i in itens:
        print("  %-34s <- %-34s gate %s %d" % (i["livro"], i["scroll"], i["gate"], i["nivel"]))
    if sem_gate:
        print("  SEM RECEITA NO JOGO (nao gerados): %s" % ", ".join(sem_gate))
    sys.exit(0)

if not itens:
    sys.exit("[XX] nenhum livro encontrado -- a varredura falhou. Nada foi gerado.")

CAB = '''// ============================================================================
// LivroDaProfissao.cs  --  Servidor Kabong Brasil / BBC-Brasil
// GERADO por gerar-livros-profissao.py -- NAO EDITE A MAO.
//
// UMA receita nova por livro de profissao, no LABORATORIO (a mesa de pesquisa
// avancada do jogo: exige Mechanics 1, sala nivel 2.8 e 24 m3), custando
// %(custo)d pergaminhos da mesma profissao.
//
// POR QUE: neste servidor nenhuma receita produz o item SkillBook -- o No More
// Books trocou o produto das 28 receitas de livro do jogo por pergaminhos, e o
// nosso PergaminhosDosMods.cs fez o mesmo nas 3 de mod. Sem livro como produto
// de receita, a tela de habilidades (Z) nao deixa clicar em especialidade nao
// descoberta, e o jogador nao ve o que a profissao faz antes de gastar estrela.
// Em servidor vanilla e clicavel (comparado em video pelo Raul, 11/09/2026).
//
// %(custo)d pergaminhos e inalcancavel DE PROPOSITO: o livro volta a existir como
// produto de receita sem voltar a ser fabricavel. O pergaminho continua sendo o
// que sai na pratica, e nenhuma receita existente foi alterada.
//
// O destrave de cada receita e o MESMO que o jogo usa na receita de livro dela
// (Assados por Milling 1, Cozimento por Butchery 1, e assim por diante).
//
// Classes SEM `partial`: sao novas e so existem aqui. `partial` num nome novo
// faria o compilador aceitar em silencio uma classe vazia se houvesse erro de
// digitacao -- foi o pre-voo que apontou isso em 11/09/2026.
//
// Reverter: apagar este arquivo.
// ============================================================================

namespace Eco.Mods.TechTree
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Linq;
    using Eco.Core.Items;
    using Eco.Core.Utils;
    using Eco.Core.Utils.AtomicAction;
    using Eco.Gameplay.Blocks;
    using Eco.Gameplay.Components;
    using Eco.Gameplay.DynamicValues;
    using Eco.Gameplay.Items;
    using Eco.Gameplay.Players;
    using Eco.Gameplay.Property;
    using Eco.Gameplay.Skills;
    using Eco.Gameplay.Systems;
    using Eco.Gameplay.Systems.TextLinks;
    using Eco.Shared.Localization;
    using Eco.Shared.Serialization;
    using Eco.Shared.Services;
    using Eco.Shared.Utils;
    using Eco.Gameplay.Systems.NewTooltip;
    using Eco.Core.Controller;
    using Eco.Gameplay.Items.Recipes;
    using Eco.Gameplay.Garbage;

    /// <summary>Prova de vida em arquivo: compilar nao e funcionar, e carregar nao e funcionar.</summary>
    public static class KabongLivroDiario
    {
        private const string Diario = "/opt/eco/livro-profissao-vida.txt";
        private static readonly object Tranca = new object();
        public static int Registradas;

        public static void Anota(string texto)
        {
            try
            {
                lock (Tranca)
                {
                    Registradas++;
                    System.IO.File.AppendAllText(Diario,
                        DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + texto + "\\n");
                }
            }
            catch { }
        }
    }
''' % {"custo": CUSTO}

MOLDE = '''
    [RequiresSkill(typeof(%(gate)s), %(nivel)d)]
    public class %(classe)s : RecipeFamily
    {
        public %(classe)s()
        {
            var recipe = new Recipe();
            recipe.Init(
                name: "%(classe)s",  //noloc
                displayName: Localizer.DoStr("%(nome)s"),
                ingredients: new List<IngredientElement>
                {
                    new IngredientElement(typeof(%(scroll)s), %(custo)d, true),
                },
                garbages: new List<GarbageOutput>
                {
                },
                items: new List<CraftingElement>
                {
                    new CraftingElement<%(livro)s>()
                });
            this.Recipes = new List<Recipe> { recipe };
            this.LaborInCalories = CreateLaborInCaloriesValue(2400, typeof(%(gate)s));
            this.CraftMinutes = CreateCraftTimeValue(beneficiary: typeof(%(classe)s), start: 15, skillType: typeof(%(gate)s));
            this.Initialize(displayText: Localizer.DoStr("%(nome)s"), recipeType: typeof(%(classe)s));
            CraftingComponent.AddRecipe(tableType: typeof(%(mesa)s), recipeFamily: this);
            KabongLivroDiario.Anota("%(livro)s <- %(custo)dx %(scroll)s");
        }
    }
'''

partes = [CAB]
for i in itens:
    d = dict(i)
    d["custo"] = CUSTO
    d["mesa"] = MESA
    partes.append(MOLDE % d)
partes.append("}\n")
texto = "".join(partes)

nao_ascii = [c for c in texto if ord(c) > 127]
if nao_ascii:
    sys.exit("[XX] o arquivo gerado tem caractere nao-ASCII: %r" % sorted(set(nao_ascii)))
if texto.count("{") != texto.count("}"):
    sys.exit("[XX] chaves desbalanceadas: %d abre, %d fecha" % (texto.count("{"), texto.count("}")))

sys.stdout.write(texto)
sys.stderr.write("[ok] %d receitas geradas, mesa %s, custo %d pergaminhos\n" % (len(itens), MESA, CUSTO))
if sem_gate:
    sys.stderr.write("[!!] livros sem receita no jogo, NAO gerados: %s\n" % ", ".join(sem_gate))
