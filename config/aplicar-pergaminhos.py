#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
aplicar-pergaminhos.py -- poe o No More Books para entregar 5 pergaminhos por livro fabricado.

    Mods/UserCode/No More Books/NoMoreBooks.cs:
        public const int OutputAmount = 1;   ->   = 5

POR QUE ESTE SCRIPT EXISTE
    Esta e a UNICA alteracao nossa dentro de um arquivo de mod de TERCEIRO. Todo o resto do
    servidor esta em arquivo nosso, justamente porque editar mod alheio morre em silencio na
    proxima atualizacao dele. Aqui nao houve escolha: o `OutputAmount` e `const` no `.cs` do
    mod, e `const` nao se alcanca por `partial class` nem por reflexao.

    **PENDENCIA PERMANENTE: toda atualizacao do No More Books zera isto para 1.** Ate
    12/09/2026 a reaplicacao dependia de alguem lembrar -- nao havia script no Linux, so um
    `.ps1` do servidor Windows antigo, que nao roda mais. Este arquivo fecha essa lacuna.

O QUE O MOD FAZ, e por que o numero importa
    Para cada receita de livro de profissao, o No More Books limpa os produtos e poe pergaminho
    no lugar: `Recipes[0].Products.Clear()` e depois `CraftingElement<XSkillScroll>(OutputAmount)`.
    Com 1, a mesa de pesquisa entrega 1 pergaminho; com 5, entrega 5.

    As 3 receitas de mod que o No More Books NAO cobre (Mixology, Advanced Mixology, IceCream)
    sao tratadas pelo nosso `PergaminhosDosMods.cs`, que LE este mesmo `OutputAmount` -- um
    unico numero para as 31 receitas, em vez de dois que poderiam divergir. Por isso mudar aqui
    basta.

    sudo -u ecosrv python3 aplicar-pergaminhos.py --seco      # so mostra
    sudo -u ecosrv python3 aplicar-pergaminhos.py             # grava
    sudo -u ecosrv python3 aplicar-pergaminhos.py --desfazer  # volta para 1

Vale no proximo arranque (o Eco compila os mods ao subir). Nao precisa parar o servidor para
editar -- isto e codigo, nao config; o Eco nao regrava `.cs` ao desligar.
"""
import io, os, re, shutil, sys, time

ARQ = "/opt/eco/server/Mods/UserCode/No More Books/NoMoreBooks.cs"
ALVO = 1 if "--desfazer" in sys.argv else 5
SECO = "--seco" in sys.argv
PADRAO = re.compile(r"(public\s+const\s+int\s+OutputAmount\s*=\s*)(\d+)(\s*;)")

print("=== No More Books: pergaminhos por livro fabricado ===")
if not os.path.exists(ARQ):
    sys.exit("[XX] nao achei %s -- o mod esta instalado? Nada foi tocado." % ARQ)

texto = io.open(ARQ, encoding="utf-8", errors="strict").read()
achados = PADRAO.findall(texto)
if len(achados) != 1:
    sys.exit("[XX] esperava encontrar OutputAmount exatamente 1 vez, achei %d. "
             "O mod mudou de forma. Nada foi tocado." % len(achados))

atual = int(achados[0][1])
print("  OutputAmount: %d -> %d" % (atual, ALVO))

if atual == ALVO:
    print("[ok] ja esta em %d -- nada a fazer." % ALVO)
    sys.exit(0)
if SECO:
    print("[seco] nada foi gravado.")
    sys.exit(0)

linhas_antes = texto.count("\n")
bak = ARQ + ".antes-pergaminhos-" + time.strftime("%Y-%m-%d_%H%M")
shutil.copy2(ARQ, bak)
print("  backup: %s" % bak)

novo = PADRAO.sub(lambda m: m.group(1) + str(ALVO) + m.group(3), texto, count=1)
io.open(ARQ, "w", encoding="utf-8").write(novo)

# confere RELENDO DO DISCO, que e o unico teste que vale
conferido = io.open(ARQ, encoding="utf-8", errors="strict").read()
depois = PADRAO.findall(conferido)
if len(depois) != 1 or int(depois[0][1]) != ALVO:
    shutil.copy2(bak, ARQ)
    sys.exit("[XX] a releitura nao bateu (%r). Backup devolvido." % (depois,))
if conferido.count("\n") != linhas_antes:
    shutil.copy2(bak, ARQ)
    sys.exit("[XX] o arquivo tinha %d linhas e ficou com %d. Backup devolvido."
             % (linhas_antes, conferido.count("\n")))

print("[ok] gravado e conferido relendo do disco: OutputAmount = %d, %d linhas preservadas"
      % (ALVO, linhas_antes))
print("     Vale no proximo arranque. Prova: fabricar um livro de profissao na Mesa de")
print("     Pesquisa deve sair %d pergaminhos." % ALVO)
