# O que foi alterado no jogo, arquivo por arquivo

Para cada coisa que este servidor muda no Eco: **o que é, por que foi alterada, como foi
alterada** e **como refazer**. As armadilhas estão junto de cada item, porque quase todas
custaram servidor fora do ar.

Servidor: Eco **0.14.1.1** (release-1079), Linux. Caminho base: `/opt/eco/server`.

---

## Índice

1. [Como o Eco aceita modificação](#1-como-o-eco-aceita-modificação) — a ordem de decisão
2. [Arquivos C# nossos](#2-arquivos-c-nossos) — 12 instalados
3. [Overrides gerados](#3-overrides-gerados) — 4, e por que são gerados
4. [O arquivo de mod de terceiro que editamos](#4-o-arquivo-de-mod-de-terceiro-que-editamos) — 1
5. [Configuração do jogo](#5-configuração-do-jogo) — os `.eco`
6. [Ecopedia e painel web](#6-ecopedia-e-painel-web)

---

## 1. Como o Eco aceita modificação

O servidor **compila todo `.cs` de `Mods/UserCode` a cada arranque**. Um arquivo que não
compila derruba o servidor inteiro. A ordem de decisão, da documentação oficial em
`Mods/UserCode/README.md`, do mais seguro para o menos:

| # | Técnica | Quando serve | Sobrevive a atualização do Eco? |
|---|---|---|---|
| 1 | `partial class` + `ModsPreInitialize()` / `ModsPostInitialize()` | mudar valor de receita ou espécie | **sim** |
| 2 | gancho ou delegate oficial | quando o jogo oferece um | **sim** |
| 3 | `partial class` acessando privado da própria classe | campo privado, sem redeclarar membro | **sim**, e é verificado em compilação |
| 4 | `.override.cs` **gerado por script** | `const`, ou corpo de método já definido | só se o gerador rodar de novo |
| 5 | ~~Harmony~~ | **nunca aqui** | o `clrjit` não é localizável nesta máquina: remendo Harmony não aplica |

**`partial class` não pode redeclarar membro que a classe já declara** — dá `CS0111`/`CS0102`.
Foi o que reprovou o exemplo #2 da própria documentação da Strange Loop para custo de estrela.

---

## 2. Arquivos C# nossos

Todos em `Mods/UserCode/KabongBrasil/`. Todos escrevem **prova de vida** em `/opt/eco/*-vida.txt`
no arranque — porque *compilar não é funcionar*, lição que veio de um mod que compilou, carregou
e se declarou defeituoso depois.

### `ArvoresDensas.cs`
**O que muda:** 10 espécies de árvore nascem em grupos maiores e mais próximos, amadurecem em
40% do tempo, semeiam com 40% do intervalo, dão o dobro de sementes e espalham 3× mais rápido.

**Como:** técnica #1 — `partial class` + `ModsPostInitialize()`, que é a última linha do
construtor de cada espécie. Números **absolutos** com o valor original ao lado em comentário.

**Por que dá para mudar densidade sem wipe da geração:** os mods carregam **antes** da geração
do mundo (`Loading mods` às 06:04, `Generating world` às 06:57), então o gerador já lê os valores
alterados. Densidade só vale em mundo novo; maturidade e espalhamento valem no mundo existente.

> **Armadilha:** o gancho nas classes de planta é `ModsPostInitialize`, **não** `ModsPreInitialize`.
> Usar o nome errado dá `CS0759` e eu já concluí, erradamente, que densidade era inalcançável.

### `PlantasCrescimento.cs` ⚙ gerado
**O que muda:** as outras **53** espécies de planta com os mesmos quatro fatores das árvores.

**Como:** gerado por `geradores/gerar-plantas-crescimento.py`, que lê as espécies do servidor.
Fica de fora: as 10 árvores (já tratadas — duas implementações do mesmo método parcial dariam
`CS0111`), a sequoia antiga (a Strange Loop a declara não-renovável de propósito) e os **4 capins**,
por decisão de jogo: são eles que invadem terreno arado.

### `CustoEstrelas.cs`
**O que muda:** preço em estrelas por profissão. Cooking e Baking 4, avançadas 6, Farming 1,
mais **+1** para iniciar outra árvore e **+2** para avançada fora da árvore.

**Como:** técnica #2 — o delegate oficial `Skill.CalculateStarsNeededForSpecialty`, documentado
pela própria Strange Loop em `__core__/Skills/SkillMods.cs`. Devolver `null` deixa o jogo decidir.

**Detalhe de projeto que se pagou:** referencia as habilidades de mod por **nome em string**,
nunca por `typeof`. Por isso compila mesmo sem os mods instalados — nome que não existe não casa
em execução, em vez de derrubar a compilação.

> **Limite conhecido, medido em campo:** a tela de habilidades mostra o custo **do jogo**, não o
> nosso. O autor do mod Skills Requirements avisou disso no código dele: esse valor é *"a cached,
> client-displayed cost"*. O servidor cobra o nosso preço; o cliente desenha o dele.

### `PergaminhosDosMods.cs`
**O que muda:** as 3 receitas de livro de mod que o No More Books não cobre (Mixology, Advanced
Mixology, IceCream) passam a entregar pergaminho em vez de livro.

**Como:** técnica #1, `partial class` + `ModsPreInitialize()`, lendo o `NMBSettings.OutputAmount`
do próprio No More Books — **um único número** para as 31 receitas, em vez de dois que divergiriam.

> **Verificação obrigatória antes de instalar:** as três classes têm de **declarar** o método
> parcial e **nenhuma** implementá-lo. Método parcial admite uma implementação só; duas dão `CS0111`.

### `LivroDaProfissao.cs` ⚙ gerado
**O que muda:** 31 receitas novas no **Laboratório** — 1 livro de profissão a partir de 10.000
pergaminhos da mesma profissão.

**Por que existe, e não é para ser fabricado:** com os livros virando pergaminho, **nenhuma
receita do servidor produzia o item `SkillBook`** — e sem isso o cliente não deixa clicar numa
especialidade não descoberta na tela **Z**, então o jogador não vê o que a profissão faz antes de
gastar estrela. O preço é inalcançável de propósito: a receita existe só para a tela voltar a abrir.

**Como:** família de receita nova, sem tocar em nenhuma existente. O destrave de cada uma espelha
o que **o próprio jogo** usa na receita de livro dela — e não é o mesmo para todas: Assados por
Milling 1, Cozimento por Butchery 1, Ferraria por Smelting 1.

### `CidadaniaFederacao.cs`
**O que muda:** quem ficar sem assentamento nenhum recebe de volta a cidadania direta da
federação, 2 segundos depois, automaticamente.

**Por que:** a cidadania direta no Eco é **exclusiva**. Plantar uma pedra de fundação cria um
assentamento e move sua cidadania direta para ele; recolher a pedra destrói esse assentamento e
você fica **sem nenhuma** — nem da cidade, nem da federação, da qual só era cidadão por herança.
Aconteceu com dois jogadores em dois dias.

**Como:** ouve `SettlementCitizenship.CitizenshipChanged`, confere `HasCitizen` e, se estiver
órfão, chama `DirectCitizenRoster.AddToRoster(..., forceAdd: true)`. Relê o `HasCitizen` depois
para registrar **efeito**, não intenção.

> Não há configuração que evite a perda: conferidos um a um os 56 campos do `Settlements.eco` e
> os 14 da política de imigração. O jogo **tem** o conceito certo (`joinParentUponLeaving`), mas
> o caminho que recolhe a pedra não o usa, e esse caminho está dentro do binário.

### `MoedasIniciais.cs`
**O que muda:** jogador novo recebe, no primeiro login, 10 de Moeda para Papel de Propriedade e
3 de Moeda para Estacas.

**Como:** `UserManager.OnUserLoggedIn` + `user.FirstLogin` + `BankAccount.AddCurrency` — todas
formas copiadas do Starter Rewards, que compila neste servidor.

> **A linha que separa dar dinheiro de derrubar o servidor:** este arquivo **nunca cria moeda**.
> Se não achar, não faz nada e anota no diário. Foi o `EnsureCurrency()` do Starter Rewards, que
> **cria** quando não encontra, que gerou duas moedas com o mesmo nome e deixou o servidor sem
> subir por mais de uma hora, até restaurarmos backup.

> **E casa por INÍCIO do nome**, não por igualdade: o `/money currencies` devolve
> "Moeda para Papel de Propriedad" com exatamente 30 caracteres, o que cheira a corte de coluna.
> Um "e" a mais ou a menos faria o mod não achar a moeda e não dar nada, **sem erro nenhum**.

### `CouroDobrado.cs`
**O que muda:** dobra o couro das receitas de açougue.
**Como:** `partial class` + `ModsPreInitialize()`, trocando o `CraftingElement` do couro.
Confere quantos elementos de couro achou e avisa no diário se não for exatamente um.

### `PlacasNoMenu.cs`
**O que muda:** acrescenta um item no menu do painel web, apontando para a galeria de ícones.
**Como:** implementa `IWebPlugin` — funciona em `UserCode` apesar de a documentação dizer que
"não é recomendado fora de DLL". A rota é `/plugin/<NomeDaClasse>`, e o painel monta
`<iframe src="/plugins/" + GetPluginIndexUrl()>`, por isso a URL é relativa com `..`.

> O ícone é **Font Awesome 4.7.0**, que é o que o painel traz: classe `fa fa-<nome>`.
> `fa-solid` (FA5/6) não renderiza nada — e esse foi o meu erro na primeira tentativa.

### `ColocarPlanta.cs` · `GnomeNosMercados.cs` · `KabongLog.cs`
Comando de admin para plantar · integração do Eco Gnome com os mercados · diário de diagnóstico
usado pelos overrides quando ligados com `--com-diario`.

### Não instalados, mantidos como registro
`CargaMochilas.cs` (mochilas ×5, substituído pelo `WeightMultiplier 0.25`) e
`PonteServidor.cs` (ponte de arquivo para anúncio no jogo).

---

## 3. Overrides gerados

`.override.cs` substitui um arquivo do `__core__` **inteiro**. Isso o torna uma **cópia
congelada**: toda atualização do Eco que mexa naquele arquivo deixa a nossa versão velha, e o
mod degrada **sem avisar**. Foi exatamente assim que o mod Big fast shovel piorou a pá sem
ninguém notar.

**Por isso nenhum override está neste repositório — só os geradores.** Eles leem o arquivo do
jogo **que está instalado** e injetam apenas a mudança. Depois de atualizar o Eco: rode o gerador,
não copie o resultado.

Cada gerador tem uma **trava**: relendo do disco, o corpo tem de diferir do original em um número
**exato** de linhas, e a âncora tem de aparecer exatamente uma vez. Do contrário ele aborta, em vez
de produzir um override pela metade — que falharia em silêncio.

| Gerador | Produz | O que injeta |
|---|---|---|
| `gerar-tronco-override.py` | `Objects/TreeObject.override.cs` | tronco direto para a mão ao derrubar; excedente cortado em peças catáveis; toco destruído **entregando a polpa**; resíduo de galho para a mochila |
| `gerar-pedra-override.py` | `Tools/PickaxeItem.override.cs` | bloco minerado vai para a mão, 4 por bloco, sem entulho |
| `gerar-pa-override.py` | `Tools/ShovelItem.override.cs` | cavar com **E**, e 10/20/30/50 blocos por slot |
| `gerar-foice-override.py` | `Tools/BlockHarvestItem.override.cs` | colher com **E** na foice e na gadanha |

### As três lições que estão dentro desses geradores

**Uma constante servindo a dois propósitos esconde o efeito colateral.** `MaxTrunkPickupSize`
limitava a coleta *e* dimensionava a fatia. Subimos para 95 para entregar o tronco inteiro, e as
fatias passaram a sair com 95 — que o cliente recusa pegar. Hoje são dois valores separados.

**Se um `[Interaction]` exige uma variável que o servidor não produz, o gate é do cliente.** A
coleta manual do tronco depende de `canPickup`, que nenhum código do servidor envia: mexer no
servidor não tem efeito visível. A saída foi fazer o servidor entregar sozinho.

**Antes de destruir entidade por conveniência, pergunte que eventos ainda dependem dela.**
Destruir o toco cedo demais fechava a condição de `CheckDestroy` antes de a árvore bater no chão —
e sem colisão não nascia resíduo. O sintoma era "com a mão vazia a polpa some".

---

## 4. O arquivo de mod de terceiro que editamos

**É o único.** Todo o resto está em arquivo nosso, justamente porque editar mod alheio morre em
silêncio na próxima atualização dele.

### `Mods/UserCode/No More Books/NoMoreBooks.cs`

```csharp
public const int OutputAmount = 1;   ->   = 5
```

**O que muda:** a mesa de pesquisa entrega **5 pergaminhos** por livro fabricado, em vez de 1.

**Por que aqui e não em arquivo nosso:** `OutputAmount` é `const`, e `const` não se alcança por
`partial class` nem por reflexão — está embutida em compilação.

**Como refazer:** `config/aplicar-pergaminhos.py`. Ele exige achar o padrão **exatamente uma vez**,
faz backup datado e confere relendo do disco, inclusive a contagem de linhas.

> ⚠ **PENDÊNCIA PERMANENTE: toda atualização do No More Books zera isto para 1.** Reaplicar depois
> de cada atualização do mod. Até 12/09/2026 isso dependia de alguém lembrar — não havia script no
> Linux, só um do servidor Windows antigo, que não roda mais.

---

## 5. Configuração do jogo

Os `.eco` de `Configs/`. **O Eco regrava essa pasta ao desligar**, então editar com o servidor no
ar faz a mudança desaparecer: a sequência é **parar → editar → subir**. Os scripts de `config/`
rodam nessa janela, fazem backup datado e conferem **relendo do disco**, devolvendo o backup se a
releitura não bater.

`ferramentas/diff-configs.py` compara cada `X.eco` com o `X.eco.template` de fábrica e lista só o
que difere — responde "isto é padrão do jogo ou fomos nós?" sem depender de memória.

| Config | Valor | O que faz |
|---|---|---|
| `StackSizeMultiplier` | 5.0 | pilhas 5× |
| `WeightMultiplier` | 0.25 | tudo pesa um quarto |
| `ConnectionRangeMultiplier` | 2.0 | alcance entre estoques |
| `MeteorImpactInDays` | 60 | meteoro em 60 dias |
| `AnimalBehavior` | DefensiveOnly | bichos só revidam |
| `ExhaustionEnabled` | false | sem limite diário de horas |
| `ClaimPapersGrantedUponSkillscrollConsumed` | 5.0 | 5 papéis por pergaminho |
| `SettlementFoundationBaseInfluence` | [65, 150, 2000] | influência da cidade, país e federação |
| `BasePlotsOnClaimStake` | [5, 5, 20] | lotes por estaca — 20 na federação |
| `ClaimStakesPerCitizen` | [1.5, 1.5, 5.0] | estacas por cidadão — 5 na federação |
| `Min*ToFound/Maintain` | 1 / 0 / 0 | federação viável com poucos jogadores |
| `AllowOptionToPreventSettlementsFromSeceding` | true | **destrava** a opção de proibir secessão; sozinho não proíbe nada |
| `EmptyBlocksCountAsWindows` | true | vão de até 2 blocos conta como sala fechada |
| `AllowPaidItemsInPlayerStores` | true | item do Marketplace em loja de jogador |
| `AllowUsingPaidItemsWithoutBlueprint` | true | quem não comprou pode colocar o item |
| `RemoteAddress` / `WebServerUrl` | preenchidos | **sem isto, quem entra pela lista pública não baixa nada** |

> **Armadilhas de config, todas pagas:**
> **1.** `Difficulty.eco` é **aninhado** (`GameSettings.AdvancedGameSettings.X`); ler do primeiro
> nível devolve vazio, não erro — falha silenciosa.
> **2.** `WorldGenerator.eco` **exige wipe**. Os demais valem no mundo existente.
> **3.** `Rooms.eco` **não existia** — quando o arquivo não existe, valem os padrões do jogo.
> Criá-lo congela os outros campos no padrão de hoje.
> **4.** A wiki diz que `EmptyBlocksCountAsWindows` é `true` por padrão; o **template desta versão
> diz `false`**. A Strange Loop mudou e a wiki ficou para trás. É por isso que servidores
> diferentes se comportam de formas diferentes com um bloco aberto na parede.

---

## 6. Ecopedia e painel web

### Ecopedia (F1) — `Mods/UserCode/Ecopedia/`
39 páginas documentando o servidor para o jogador, em português. Geradas por
`ecopedia/gerar-ecopedia-bbc.py`, instaladas por `ecopedia/instalar-ecopedia-bbc.sh`.
Valem no próximo arranque.

> **São TRÊS níveis: capítulo → categoria → página.** E **categoria sem nenhuma página não
> aparece** — foi o que fez um capítulo nosso surgir como divisória vazia no menu por dois dias.
> O nome do capítulo vem do **nome do arquivo** `<ecopediachapter>`, não da pasta. A ordem do menu
> é por prioridade **crescente**.

O gerador barra três coisas que passariam para o jogo: ícone que não existe, ícone repetido entre
páginas, e link `[XItem]` com nome errado — que viraria texto morto, sem ícone e sem link.

> Uma das páginas **sobrescreve** dois XML que o MarketMod instala, para traduzi-los. Uma
> atualização do MarketMod os devolve em inglês: reaplicar.

### Galeria de ícones — `WebClient/WebBin/placas/`
Os 1824 ícones que a tag de placa aceita, com montador de texto. Gerada por
`placas/extrair-icones.py`, publicada por `placas/instalar-placas-web.sh`. **Não precisa
reiniciar:** é arquivo estático.

> **Ela mora em DOIS lugares** — o GitHub Pages (<https://dartangn.github.io/icones-eco-bbc/>) e a
> cópia-mestra `/opt/eco/placas-web` do painel. **Publicar num não publica no outro**, e isso já
> deixou o servidor dois dias com a versão velha enquanto o GitHub estava certo.

---

## Antes de instalar qualquer `.cs` novo

```bash
python3 ferramentas/conferir-cs-novo.py ARQUIVO.cs
```

Confere ASCII puro, chaves e parênteses fora de comentário e string, e cada `using Eco.*` e cada
tipo Eco usado contra os ~2.840 `.cs` que compilam no servidor.

**E ele não pega tudo.** Deixou passar uma classe aninhada com o mesmo nome da externa — erro de
compilação em C# que não é tipo, nem chave, nem `using`. Por isso **todo gerador imprime uma
amostra do que gerou, e ela tem de ser lida**.

**Nem o pré-voo substitui acompanhar o arranque.** Três arranques falhos seguidos travam a unidade
do systemd por 30 minutos, e destravar exige root.
