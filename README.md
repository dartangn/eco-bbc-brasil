# Mods do servidor Eco — BBC-Brasil

Arquivos que **modificam o jogo** no servidor [BBC-Brasil 5X](http://186.215.73.175:27041)
(Eco 0.14.1.1, Linux). São mods próprios em C#, geradores que os produzem, e scripts que
ajustam a configuração do jogo.

Nada aqui é segredo: não há senha, chave, nem endereço interno. Os documentos de operação
do servidor (acesso, histórico, reconstrução) **não** estão neste repositório.

---

## Como o Eco carrega isto

O servidor **compila todo `.cs` de `Mods/UserCode` a cada arranque**. Se um único arquivo
não compilar, o servidor inteiro não sobe. Três regras que custaram caro para aprender:

1. **Nunca instalar um `.cs` novo e deixar para "o próximo reinício".** Instale e acompanhe
   o arranque. Em 08/09/2026 um arquivo esperando o reinício derrubou o servidor por 30 min,
   porque três arranques falhos seguidos travam a unidade do systemd.
2. **Copiar a forma de um código que compila inclui copiar os `using` dele.** Duas quedas em
   dois dias vieram de usar um tipo sem conferir em que namespace ele vive.
3. **Compilar não é funcionar.** Todo mod aqui escreve uma *prova de vida* em arquivo no
   arranque. Sem ela, não há como saber se o código rodou ou só compilou.

A ordem de decisão para escrever mod no Eco, da documentação oficial:
`partial class` + `ModsPreInitialize()` → gancho/delegate oficial → `partial class` acessando
privado da própria classe → `.override.cs` **gerado por script** → nunca Harmony
(o Harmony não aplica remendo neste servidor: `Could not locate clrjit library`).

---

## `mods/` — os arquivos C#

Vão para `Mods/UserCode/KabongBrasil/`.

| Arquivo | O que faz |
|---|---|
| `ArvoresDensas.cs` | 10 espécies de árvore: nascem em grupos maiores e mais próximos, amadurecem em 40% do tempo, espalham 3x mais rápido |
| `PlantasCrescimento.cs` ⚙ | as outras 53 plantas com os mesmos fatores. Capim de fora: é ele que invade terreno arado |
| `CustoEstrelas.cs` | preço em estrelas por profissão, com +1 para iniciar outra árvore e +2 para avançada fora da árvore. Usa o delegate oficial `Skill.CalculateStarsNeededForSpecialty` |
| `PergaminhosDosMods.cs` | 5 pergaminhos em vez do livro nas 3 receitas de mod que o No More Books não cobre |
| `LivroDaProfissao.cs` ⚙ | 31 receitas de livro no Laboratório a 10.000 pergaminhos. **Existe para a tela de habilidades voltar a abrir** — sem nenhuma receita que produza o livro, o cliente não deixa clicar em especialidade não descoberta |
| `CidadaniaFederacao.cs` | devolve a cidadania direta da federação a quem ficar sem assentamento nenhum, 2 s depois |
| `MoedasIniciais.cs` | jogador novo recebe moedas no primeiro login. **Nunca cria moeda** — só procura as que existem |
| `CouroDobrado.cs` | dobra o couro nas receitas de açougue |
| `ColocarPlanta.cs` | comando de admin para plantar |
| `GnomeNosMercados.cs` | integração do Eco Gnome com os mercados |
| `PlacasNoMenu.cs` | item no menu do painel web, via `IWebPlugin` |
| `KabongLog.cs` | diário de diagnóstico, usado pelos overrides quando ligados com `--com-diario` |
| `CargaMochilas.cs` | capacidade das mochilas ×5. **Não instalado** — substituído pelo `WeightMultiplier 0.25` |
| `PonteServidor.cs` | ponte de arquivo para mandar anúncio ao jogo. **Não instalado** |

⚙ = **gerado**. Depois de atualizar o Eco, rode o gerador de novo em vez de copiar o arquivo:
cópia velha de arquivo gerado é o defeito que degradou um mod famoso sem avisar.

---

## `geradores/` — produzem `.override.cs` a partir do arquivo do jogo instalado

`.override.cs` substitui um arquivo do `__core__` inteiro, então **mantê-lo à mão é cópia
congelada**: uma atualização do Eco deixa a sua versão velha e o mod degrada em silêncio.
Estes scripts leem o arquivo do jogo **que está instalado** e injetam só a mudança.

Cada um tem uma **trava**: relendo do disco, o corpo tem de diferir do original em um número
**exato** de linhas. Se a âncora não aparecer exatamente uma vez, o gerador aborta em vez de
produzir um override pela metade — que falharia em silêncio.

| Gerador | Produz | Entrega |
|---|---|---|
| `gerar-tronco-override.py` | `Objects/TreeObject.override.cs` | tronco direto para a mão ao derrubar; excedente no chão em peças catáveis; toco destruído **entregando a polpa**; resíduo de galho para a mochila |
| `gerar-pedra-override.py` | `Tools/PickaxeItem.override.cs` | bloco minerado vai direto para a mão, 4 por bloco, sem entulho |
| `gerar-pa-override.py` | `Tools/ShovelItem.override.cs` | cavar com E e mais blocos por slot (10/20/30/50) |
| `gerar-foice-override.py` | `Tools/BlockHarvestItem.override.cs` | colher com E na foice e na gadanha |
| `gerar-livros-profissao.py` | `LivroDaProfissao.cs` | lê os 31 livros e o destrave que **o próprio jogo** usa em cada um |
| `gerar-plantas-crescimento.py` | `PlantasCrescimento.cs` | lê as espécies e aplica os fatores; a lista `EXCLUIR` tira o capim |

Todos rodam no servidor, como o usuário dono dos arquivos, e têm `--seco` ou `--resumo` para
mostrar o que fariam sem tocar em nada. **Rode o modo seco antes do real, sempre.**

---

## `config/` — ajustam os `.eco` da pasta `Configs`

O Eco **regrava os `Configs` ao desligar**, então editar com o servidor no ar faz a mudança
desaparecer. Estes scripts rodam **com o servidor parado**, fazem backup datado, e conferem
**relendo do disco** — devolvendo o backup se a releitura não bater.

| Script | Mexe em |
|---|---|
| `ajustar-salas.py` | vão de até 2 blocos volta a contar como sala fechada (`EmptyBlocksCountAsWindows`) |
| `ajustar-influencia-cidade.py` | influência inicial da cidade |
| `ajustar-estacas.py` | estacas por cidadão e lotes por estaca |
| `ajustar-abandono.py` | cidadão abandonado gera o mesmo que ativo |
| `ajustar-exaustao.py` | limite diário de horas |
| `ajustar-itens-pagos.py` | itens do Marketplace em loja de jogador |
| `ajustar-remote-address.py` | endereço anunciado na lista pública |
| `ajustar-settlements.py` · `ajustar-nome.py` | requisitos de assentamento · nome na lista |

---

## `ferramentas/`

| Ferramenta | Para quê |
|---|---|
| `conferir-cs-novo.py` | **pré-voo**: confere ASCII puro, chaves e parênteses fora de comentário e string, e cada `using Eco.*` e cada tipo Eco usado contra os ~2.840 `.cs` que compilam no servidor. Não substitui acompanhar o arranque; só pega antes o que é barato pegar antes |
| `diff-configs.py` | compara cada `Configs/X.eco` com o `X.eco.template` de fábrica e lista **só o que difere** — responde "isto é padrão do jogo ou fomos nós?" sem depender de memória |

O pré-voo **não pega tudo**: ele deixou passar uma classe aninhada com o mesmo nome da externa,
que é erro de compilação em C#. Por isso todo gerador imprime uma amostra do que gerou, e ela
tem de ser lida antes de instalar.

---

## `ecopedia/`

| Arquivo | Para quê |
|---|---|
| `gerar-ecopedia-bbc.py` | gera as páginas do F1 (Ecopedia) documentando o servidor para o jogador. Valida cada link `[XItem]` contra a tabela de itens do servidor e **aborta** se um ícone repetir entre páginas |
| `extrair-icones.py` | monta a galeria dos 1824 ícones que a tag de placa aceita, com montador de texto |

A Ecopedia tem **três níveis** e essa é a armadilha dela: capítulo → categoria → página.
**Categoria sem nenhuma página não aparece** — foi o que fez um capítulo nosso surgir vazio
no menu por dois dias.

---

## Licença e crédito

Os mods são deste servidor e podem ser usados livremente. Os ícones e nomes do Eco são da
[Strange Loop Games](https://play.eco). Mods de terceiros citados (No More Books, GoodPrice,
Starter Rewards, Mixology, IceCream e outros) são de seus autores no [mod.io](https://mod.io/g/eco)
e **não** estão aqui — só o nosso código e o que ele altera.
