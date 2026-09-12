# -*- coding: utf-8 -*-
"""
Gera as páginas da Ecopedia (F1) do servidor BBC-Brasil, capítulo "Mods".

Regra de conteúdo (pedido do Raul, 08/09/2026): só o que o AUTOR do mod escreveu para o
usuário (mod.io / README, guardados em fontes-modio-bruto.txt e readmes-mods.txt) ou o que
foi CONFERIDO no código instalado neste servidor (receitas-servidor.txt) ou em campo.
Nada deduzido. fontes.md lista a fonte de cada página.

Saída: pasta ./saida/  com
  BBC-Brasil.xml, BBC-Brasil;<Mod>.xml   (página-mãe + subpáginas nossas)
  EcoPulse.xml, EcoPulse;Market.xml      (tradução PT-BR das páginas que o MarketMod instala)
Validação: XML bem formado, UTF-8 sem BOM, todo [XItem] existe em nomes-de-itens.txt,
todo [Nome de página] é uma subpágina gerada aqui, todo ícone é um item existente.

Uso:  python gerar-ecopedia-bbc.py
"""
import os, re, sys, xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
NOMES = os.path.join(AQUI, "nomes-de-itens.txt")

# ---------------------------------------------------------------- nomes de itens válidos
itens = set()
with open(NOMES, encoding="utf-8", errors="replace") as fh:
    for linha in fh:
        m = re.match(r"^(\w+)\s{2,}", linha)
        if m:
            itens.add(m.group(1))
if len(itens) < 1500:
    sys.exit("nomes-de-itens.txt incompleto: %d itens" % len(itens))

# ---------------------------------------------------------------- páginas
# Cada subpágina: (título, ícone, resumo, [(cabeçalho ou None, texto)])
# No texto: <b>, <i>, "•" e [XItem] / [Título de página].
PAGINAS = []

def pagina(titulo, icone, resumo, secoes, grupo="terceiro"):
    PAGINAS.append((titulo, icone, resumo, secoes, grupo))

# ------------------------------------------------------------------ PARÂMETROS (configuração, não código)
pagina("Configuracao do jogo", "StarterCampItem",
"Valores de configuração deste servidor: pilhas, peso, meteoro, assentamentos, minério, reinício diário.",
[
("Jogo (Difficulty.eco)", """
• <b>Pilhas 5x</b> (StackSizeMultiplier 5.0): cada pilha vale cinco vezes o normal. A tora comum empilha 100 na mão.
• <b>Peso 0,25x</b> (WeightMultiplier 0.25): todo item pesa um quarto do normal.
• <b>Alcance de conexão 2x</b> (ConnectionRangeMultiplier 2.0): estoque alcança mesas e outros estoques ao dobro da distância.
• <b>Exaustão desligada</b>: não há limite diário de horas de jogo.
• <b>Meteoro em 60 dias</b> (MeteorImpactInDays 60), contados da criação do mundo.
• <b>Animais só revidam</b> (AnimalBehavior DefensiveOnly): não atacam sem serem atacados.
• <b>5 papéis de terreno</b> por pergaminho de profissão consumido (ClaimPapersGrantedUponSkillscrollConsumed 5).
• Custo de XP por estrela no padrão do jogo (SkillCostMultiplier 1.0). O preço em estrelas de cada profissão é mudado por código, veja [Custo das estrelas].
"""),
("Assentamentos (Settlements.eco)", """
• Influência-base da fundação: cidade 45, país 150, <b>federação 2000</b>, para uma federação cobrir o mundo inteiro de 4 km².
• Cidadãos mínimos para fundar e para manter qualquer assentamento: <b>1</b>. Cultura mínima: <b>0</b>.
• Cada cidadão que entra na federação gera <b>5 estacas de terreno</b> (o jogo normal gera 1,5), e cada estaca deixa reivindicar <b>20 lotes</b> (normal 5). As estacas ficam com a federação, que as distribui aos cidadãos.
• Cidadão marcado como <b>abandonado</b> (que sumiu do jogo) gera o mesmo que um cidadão ativo, em cidade, país e federação: a federação não perde papéis nem estacas quando alguém para de jogar.
• <b>Cidade nova nasce com influência 65</b> (o padrão do jogo é 45). Influência se comporta como raio em blocos, então 65 cobre pouco mais que o dobro da área do padrão.
• A federação pode <b>proibir que uma cidade-filha se separe</b> dela, se a liderança desmarcar essa opção na política de imigração (é preciso uma Mesa de Imigração dentro da influência da federação).
"""),
("Salas e casas (Rooms.eco)", """
• Um vão de até <b>2 blocos de largura por 1 de altura</b> (ou 2 de altura por 1 de largura) na parede <b>continua contando como sala fechada</b>, servindo de janela ou porta. É o comportamento normal do Eco, que vinha desligado nesta versão.
• Vão maior que isso, ou buraco no teto aberto para o céu, continua invalidando a sala.
• O restante da configuração de sala está no padrão do jogo: uma janela sem penalidade a cada 10 blocos de parede, e bônus de 20% no valor da sala com as paredes pintadas.
"""),
("Itens comprados no Marketplace", """
• Item comprado com Eco Credits <b>pode ser vendido em loja de jogador</b>.
• E <b>qualquer um pode colocá-lo no mundo</b>, mesmo sem ter comprado o blueprint.
"""),
("Mundo (WorldGenerator.eco)", """
• Mapa de <b>2000 x 2000 blocos</b> (4 km²), semente 2052209397. O mesmo mapa volta a cada wipe.
• <b>Minério</b>: cada depósito tem o dobro da chance de aparecer e veios 1,5 vez maiores que o padrão. Vale para ferro, cobre, carvão e ouro, rasos e profundos. Exemplos (chance por bloco e tamanho do veio, padrão e aqui):
  ferro raso 0,02 e 8-15 blocos, aqui 0,04 e 12-22 · cobre 0,03 e 6-25, aqui 0,06 e 9-37 · carvão 0,0025 e 15-50, aqui 0,005 e 22-75 · ouro 0,005 e 5-25, aqui 0,01 e 7-37.
• Densidade das árvores: mudada por código, veja [Arvores densas].
"""),
("Servidor (Network.eco e outros)", """
• Servidor <b>público</b>, sem senha, vagas ilimitadas. Na lista de servidores aparece como <b>"BBC-BRASIL 5X, PT-BR, MODS, METEORO 60 DIAS"</b>.
• Imagem impressa (impressora, painéis) passa por <b>aprovação de administrador</b> antes de aparecer.
• Pedra de afiar faz <b>reparo completo</b> (WhetstonesPercent 100). Veja [Pedras de Afiar].
• Recompensa de primeiro login: veja [Recompensa inicial].
"""),
("Reinício diário", """
O servidor reinicia todo dia às <b>4h da manhã</b> (horário de Brasília). O mundo é salvo antes. Quem estiver conectado é desconectado e pode voltar em poucos minutos.
"""),
], grupo="param")

# ------------------------------------------------------------------ MODS DO SERVIDOR (código nosso)
pagina("Tronco na mão", "IronAxeItem",
"Ao derrubar a árvore, o tronco vem direto para a mão; o que não cabe fica no chão em peças de 5; o toco some e entrega a polpa.",
[
("O que muda", """
No Eco normal, a árvore cai inteira, você aperta E no tronco e só consegue pegar peça de até 5 toras; o resto precisa ser cortado com o machado, peça por peça, e o toco fica.

Neste servidor, ao derrubar:

• O <b>tronco vem direto para a mão</b>, até onde ela aguenta (100 toras com a mão vazia, pela pilha 5x).
• O que <b>não cabe fica no chão já cortado em peças de 5</b>, que se pegam com a tecla E, sem machado.
• Os <b>resíduos dos galhos</b> (polpa, sementes, fibra) vão para a mochila.
• O <b>toco desaparece</b> sozinho e entrega a polpa dele, como se você o tivesse cortado.
"""),
("Como usar bem", """
• Com a <b>mão vazia</b> você leva o máximo. Com outro item na mão, o tronco cai no chão como no jogo normal e você pega as peças de 5 com E.
• Espere a árvore terminar de cair: a entrega acontece nos primeiros segundos depois da queda.
"""),
], grupo="nosso")

pagina("Pedra na mão", "IronPickaxeItem",
"Minerar com a picareta entrega o bloco direto na mão, 4 por bloco, sem entulho no chão.",
[
(None, """
No Eco normal, cada bloco minerado vira <b>entulho</b> no chão, que você pega depois. Neste servidor o bloco vai <b>direto para a mão</b>: 4 unidades por bloco, a mesma quantidade que o entulho daria. A economia da mineração não muda; some só o passo de catar.

Se a mão estiver ocupada com outro item, ou cheia, o bloco vira entulho como no jogo normal. Vale para todas as picaretas ([StonePickaxeItem], [IronPickaxeItem], [SteelPickaxeItem], [ModernPickaxeItem]).
"""),
], grupo="nosso")

pagina("Pá com E", "IronShovelItem",
"A tecla E cava, e cada pá carrega mais por slot: madeira 10, ferro 20, aço 30, moderna 50.",
[
(None, """
Duas mudanças na pá, feitas por arquivo deste servidor (o mod Big fast shovel do mod.io <b>não</b> está instalado):

• <b>Cavar com E</b>: apontar para o bloco e apertar E cava, igual ao clique. Dá para segurar a tecla.
• <b>Mais por slot na mão</b>: no jogo normal cada slot da mão aceita 1 (madeira), 3 (ferro), 5 (aço) ou 10 (moderna) blocos ao cavar. Aqui: [WoodenShovelItem] <b>10</b>, [IronShovelItem] <b>20</b>, [SteelShovelItem] <b>30</b>, [ModernShovelItem] <b>50</b>.
"""),
], grupo="nosso")

pagina("Foice com E", "SteelSickleItem",
"Foices e gadanhas colhem com a tecla E, sem clicar.",
[
(None, """
Apontar para a planta e apertar <b>E</b> colhe, igual ao clique; dá para segurar a tecla. Vale para as foices e gadanhas ([StoneSickleItem], [SteelSickleItem], [ModernScytheItem]). A colheita em área das ferramentas de aço e modernas continua a mesma do jogo.
"""),
], grupo="nosso")

pagina("Plantas mais rapidas", "CornSeedItem",
"Todas as plantas cultivadas e silvestres amadurecem em 40% do tempo, dão o dobro de sementes e se espalham três vezes mais rápido. Capim de fora.",
[
("O que muda", """
As <b>53 espécies</b> de planta do jogo receberam os mesmos ajustes que as árvores já tinham:

• <b>Amadurecem em 40% do tempo.</b> A maioria passou de 0,8 para <b>0,32 dia</b>; algodão, abacaxi, mirtilo, tomate, mamão e figo-da-índia, de 1,2 para <b>0,48</b>.
• <b>Semeiam com 40% do intervalo</b> e produzem o <b>dobro de sementes</b> por vez.
• <b>Espalham-se 3 vezes mais rápido</b> pelo terreno ao redor (0,001 para 0,003).

Vale para o que se planta ([CornItem], [WheatItem], [CottonBollItem], [BeansItem], [RiceItem], [TomatoItem], [PumpkinItem], [FlaxStemItem], [BeetItem], [TaroRootItem], [SunflowerItem], [CamasBulbItem]) e também para o que se colhe no mundo: frutas, cogumelos, algas, arbustos, flores, samambaias e musgos.
"""),
("O que ficou de fora, e por quê", """
• <b>Os quatro capins</b> (grama comum, capim-touceira, capim-varre-vento e barba-de-bode) continuam no padrão do jogo. São eles que invadem terreno arado, e acelerá-los daria mais trabalho de capinar a quem planta.
• As <b>árvores</b> já tinham esses ajustes desde antes, veja [Arvores densas].
• A <b>sequoia antiga</b> continua não-renovável, como o jogo a desenhou: se for cortada, não volta a crescer.
"""),
], grupo="nosso")

pagina("Cidadania da federacao", "FederationFoundationItem",
"Se você ficar sem assentamento nenhum, o servidor devolve sua cidadania da federação sozinho, em 2 segundos.",
[
("O problema que isto resolve", """
No Eco, a <b>cidadania direta é exclusiva</b>: quando você planta uma pedra de fundação, ela cria um assentamento e a sua cidadania direta passa para ele — você continua na federação, mas por herança, como cidadão de um assentamento-filho.

Se depois você <b>recolher essa pedra</b> com o martelo, o assentamento deixa de existir e a herança morre junto: você fica <b>sem cidadania nenhuma</b>, e perde os direitos civis da federação.
"""),
("O que o servidor faz", """
Dois segundos depois, o servidor confere se você ficou sem assentamento e, se ficou, <b>devolve sua cidadania direta da federação</b> automaticamente. Não precisa pedir a ninguém.

Quem funda cidade e a mantém não é afetado: essa pessoa continua cidadã da federação por herança, e o servidor não mexe em nada.
"""),
], grupo="nosso")

pagina("Moedas para comecar", "CurrencyExchangeItem",
"Jogador novo recebe, no primeiro login, 10 de Moeda para Papel de Propriedade e 3 de Moeda para Estacas.",
[
(None, """
Quem entra no servidor pela <b>primeira vez</b> recebe, além dos 500 Real e das 2 estrelas de especialidade que a [Recompensa inicial] já dá:

• <b>10</b> de Moeda para Papel de Propriedade
• <b>3</b> de Moeda para Estacas

São as moedas com que se compram papel de reivindicação e estaca nas lojas da federação, para você conseguir marcar seu terreno logo ao chegar. Aparecem na sua carteira assim que você entra.

Vale <b>uma vez só</b>, no primeiro login. Quem já jogou aqui antes não recebe de novo.
"""),
], grupo="nosso")

pagina("Livro da profissao", "LaboratoryItem",
"Existe uma receita de livro para cada profissão no Laboratório. Ela não é para ser feita: serve para a tela de habilidades funcionar.",
[
("Por que ela existe", """
Neste servidor, a mesa de pesquisa entrega <b>pergaminhos</b> em vez de livros, veja [Pergaminhos]. Isso tem um efeito colateral no cliente do jogo: sem nenhuma receita que produza o <b>livro</b>, a tela de habilidades (tecla <b>Z</b>) não deixa clicar numa especialidade que ainda não foi descoberta, e você não consegue ver o que a profissão faz antes de gastar estrela.

A solução foi devolver a existência do livro sem devolver o livro na prática.
"""),
("Como ela é", """
No <b>Laboratório</b> há uma receita de livro para cada uma das 31 profissões, custando <b>10.000 pergaminhos</b> da mesma profissão. O preço é inalcançável de propósito.

Ela não muda nada do seu dia a dia: a mesa de pesquisa continua dando 5 pergaminhos, e é assim que se aprende profissão. A receita do livro está ali só para a tela de habilidades voltar a abrir.
"""),
], grupo="nosso")

pagina("Arvores densas", "CedarSeedItem",
"As dez espécies de árvore nascem em grupos maiores e mais próximos, amadurecem em menos da metade do tempo e se espalham três vezes mais rápido.",
[
("Densidade na geração do mundo", """
Quantas árvores nascem por grupo e a distância entre grupos, padrão do jogo e aqui:

• Cedar, Fir, Spruce, Oak: grupos de 1-3 para <b>2-6</b>; distância 10-20 para <b>7-13</b>.
• Birch: 30-60 para <b>45-90</b>; distância 30-60 para <b>20-39</b>.
• Redwood: 5-40 para <b>8-60</b>; distância 60-120 para <b>39-78</b>.
• Ceiba: 4-16 para <b>6-24</b>; distância 5-12 para <b>3-8</b>.
• Palm: 4-10 para <b>6-15</b>; distância 14-22 para <b>9-14</b>.
• Joshua: 3-5 para <b>5-8</b>; distância 30-50 para <b>20-33</b>.
• Saguaro Cactus: 3-5 para <b>5-8</b>; distância 30-60 para <b>20-39</b>.

Isso vale no nascimento do mundo. O mundo atual foi gerado com estes valores.
"""),
("Crescimento e recomposição", """
• <b>Maturidade</b> em 40% do tempo normal: Palm 1,8 dia (era 4,5); Cedar e Birch 2,0 (era 5); Fir e Spruce 2,2 (era 5,5); Ceiba, Redwood e Saguaro 2,4 (era 6); Oak e Joshua 2,8 (era 7).
• <b>Intervalo entre semeaduras</b> reduzido a 40% e <b>sementes por semeadura</b> dobradas, em todas.
• <b>Taxa de espalhamento</b> 0,0003 em todas (era 0,0001).

A Old Growth Redwood (sequoia antiga) <b>não</b> foi alterada: continua não renovável, como no jogo.
"""),
], grupo="param")

pagina("Custo das estrelas", "ResearchTableItem",
"Preço em estrelas de algumas profissões mudou, e começar árvore nova ou pular para profissão avançada custa mais.",
[
("Veja o seu preço", """
No chat:

<b>/custoestrelas ver</b>

Lista as árvores de profissão que você já iniciou e o custo de cada profissão para você, marcando o que difere do jogo normal.
"""),
("Preços-base diferentes do jogo", """
• Farming: <b>1</b> (o jogo normal cobra 2)
• Cooking e Baking: <b>4</b> (normal 3)
• Advanced Cooking, Advanced Baking e Cutting Edge Cooking: <b>6</b> (normal 4, 4 e 5)
• Advanced Mixology: <b>6</b> (normal 4)
• IceCream: <b>4</b> (normal 3)

As demais profissões custam o preço normal do jogo.
"""),
("Duas regras que somam ao preço", """
• Começar uma <b>árvore de profissão nova</b> (por exemplo, quem só tem profissões de Carpenter aprende uma de Mason) custa <b>+1</b>.
• Aprender uma profissão <b>avançada</b> fora da sua árvore custa <b>+2</b>. Avançada é a que custa 4 ou mais no jogo normal.

A primeira profissão e a progressão dentro da mesma árvore pagam só o preço-base. Self Improvement não conta como árvore.
"""),
], grupo="nosso")

pagina("Pergaminhos", "CarpentrySkillScroll",
"Na mesa de pesquisa, todo livro de profissão vira 5 pergaminhos, e cada pergaminho consumido dá 5 papéis de terreno.",
[
(None, """
• Na [ResearchTableItem], toda receita de livro de profissão produz <b>5 pergaminhos</b> em vez de um livro (mod No More Books, ajustado para 5 neste servidor).
• Vale também para as três profissões de mod: Mixology, Advanced Mixology e IceCream (arquivo deste servidor).
• Cada pergaminho consumido dá <b>5 papéis de terreno</b> (configuração do servidor).

Livros não existem mais: o que se vende e se compra são pergaminhos.
"""),
], grupo="nosso")

pagina("Couro dobrado", "LeatherHideItem",
"Cortar bicho na mesa de açougue entrega o dobro de couro; carne, lã e pele continuam iguais ao jogo normal.",
[
("Quanto couro cada abate dá", """
Na [ButcheryTableItem], as receitas de abate entregam <b>o dobro</b> de [LeatherHideItem] deste servidor. Os outros produtos não mudaram.

• <b>Animal pequeno de couro</b> (peru, cão-da-pradaria, tartaruga): 1 carne crua e <b>2 couros</b> (o jogo normal dá 1).
• <b>Animal médio</b> (veado, alce, jacaré, jaguar): 5 carne crua e <b>2 couros</b> (normal 1).
• <b>Animal médio lanoso</b> (cabra da montanha, bighorn): 5 carne crua, 2 [ShornWoolItem] e <b>2 couros</b> (normal 1).
• <b>Bisão</b>: 10 carne crua, 3 [ShornWoolItem] e <b>4 couros</b> (normal 2).
"""),
("Bicho que não dá couro", """
Coiote, raposa, agouti, lontra, lebre e lobo <b>não dão couro em nenhum servidor</b>: eles dão [FurPeltItem]. Para virar couro, a pele passa pelo curtimento.

O <b>curtimento não foi alterado</b>: continua 2 [FurPeltItem] para 1 [LeatherHideItem] mais 1 [TallowItem], com Açougue nível 5. Só o abate dobrou.
"""),
], grupo="nosso")

pagina("Recompensa inicial", "MintItem",
"No primeiro login, cada jogador recebe 500 Real e 2 estrelas de especialidade.",
[
(None, """
Mod <b>Starter Rewards</b>, configurado neste servidor para dar, <b>uma vez, no primeiro login</b>: <b>500 Real</b> (a moeda da federação) e <b>2 estrelas de especialidade</b>. Uma mensagem de boas-vindas no chat confirma o que foi recebido. Quem já entrou antes não recebe de novo.
"""),
])


# ------------------------------------------------------------------ Eco Gnome
pagina("Eco Gnome", "CarpenterMarketItem",
"Calcule seus preços no site eco-gnome.com com as receitas deste servidor e mande as ofertas para a sua loja com um botão.",
[
("O que o Eco Gnome faz", """
Você diz no site <b>eco-gnome.com</b> quais profissões tem e quanto paga pelos ingredientes; ele calcula quanto custa fabricar cada item e sugere o preço de venda com a sua margem. Depois, na sua loja aqui no jogo, a aba <b>Eco Gnome</b> manda essas ofertas e preços para a loja de uma vez.

Ele <b>não olha o seu estoque</b>: entra na loja o que você listou no site. Nada se instala no seu PC. O servidor já está registrado no site com as receitas de todos os mods.
"""),
("Passo 1 - Sua conta no site", """
1. Abra <b>https://eco-gnome.com</b> no navegador do PC. O site cria uma conta anônima sozinho, com nome parecido com USER48453148. Não há senha.

2. Clique no <b>nome da conta</b>, no canto superior direito. Abre a janela <i>User settings</i>.

3. Em <b>Pseudo</b>, coloque o seu nome do jogo.

4. Copie o <b>Secret Id</b> com o botão ao lado dele. É esse código que liga a conta ao seu personagem.

5. Clique no botão de <b>exportar</b> e guarde o arquivo. A conta vive só nesse navegador; esse arquivo é a única forma de recuperá-la.
"""),
("Passo 2 - Ligar a conta ao seu personagem", """
No chat do jogo, colando o Secret Id no lugar indicado:

<b>/ecognome registeruser SEU-SECRET-ID</b>

Resposta esperada: <i>Success</i>. Faz uma vez só por jogador.
"""),
("Passo 3 - Abrir o site já dentro do servidor", """
<b>/ecognome join</b>

O navegador abre no eco-gnome.com com o servidor <b>BBC-BRASIL</b> selecionado em <i>My Servers</i>. As receitas que aparecem são as deste servidor, mods incluídos.

Se aparecer <i>"Unable to find server..."</i>, avise um admin: é o registro do servidor que falta, não o seu.
"""),
("Passo 4 - Suas profissões e seus custos (no site)", """
1. <b>Add your skills</b>: as profissões que você tem, com o nível.

2. <b>Crafting tables</b>: as mesas que usa, com o upgrade.

3. <b>Items to buy</b>: o preço pelo qual você compra cada ingrediente. O que você mesmo produz, deixe: o site usa o custo da receita.

4. Em <b>Options</b>, marque <b>Hide blueprints</b>. Itens pagos do Marketplace não podem ser vendidos em loja neste servidor; essa opção os tira da lista.

5. <b>Margins</b>: a margem padrão é 20%.

Sem preço de ingrediente não há custo, e o item vai para a loja com um preço absurdo. Preencha antes de sincronizar.
"""),
("Passo 5 - O que você vende (no site)", """
Em <b>Items to sell</b>, adicione <b>só os produtos que você realmente vende</b>. Essa lista é exatamente o que vai virar oferta na sua loja.

Se deixar a lista aberta, o botão do passo 6 cria uma oferta para tudo que você consegue fabricar: centenas de itens, a maioria sem preço calculado.
"""),
("Passo 6 - Mandar para a loja", """
1. Abra a sua loja, carrinho ou mercado. Ao lado das abas normais há a aba <b>Eco Gnome</b>.

2. <b>Context Name</b>: deixe vazio.

3. <b>Scope</b>: Sell, para mexer só nas suas vendas.

4. <b>Sync Tags</b>: No.

5. <b>Group By</b>: Skill separa por profissão; None põe tudo num grupo só.

6. Clique em <b>Sync Offers</b>.

A loja recebe as ofertas da sua lista, com os preços do site. Se aparecer <i>"Não foi possível adicionar todas as profissões: itens pagos não podem ser comprados ou vendidos..."</i>, está tudo certo: só os itens pagos ficaram de fora.
"""),
("Passo 7 - Manter os preços em dia", """
• Mudou preço no site: <b>Sync Prices</b> na aba Eco Gnome, ou <b>Shift + botão direito</b> na loja. Só atualiza preços.

• Mudou a lista do que vende: <b>Sync Offers</b> de novo. Acrescenta o que entrou e remove do grupo dele o que saiu.

• Ofertas feitas à mão que você não quer que ele toque: ponha as letras <b>NS</b> entre colchetes no nome do grupo. Grupos com essa marca são ignorados.

• <b>Sync For Sale Area</b> é outra coisa: ajusta o preço de objetos marcados como à venda perto da loja. Sem objeto assim, responde <i>"No authorized for-sale objects found"</i>. Normal.
"""),
("Onde a aba aparece", """
Na [StoreItem], no [WoodShopCartItem] e nos oito mercados do servidor: [CarpenterMarketItem], [MasonMarketItem], [SmithMarketItem], [EngineerMarketItem], [FarmerMarketItem], [ChefMarketItem], [HunterMarketItem] e [TailorMarketItem]. A aba <b>GoodPrice</b> aparece nos mesmos lugares (veja [GoodPrice]).
"""),
])

# ------------------------------------------------------------------ GoodPrice
pagina("GoodPrice", "GoldBarItem",
"Calculadora de preços dentro do jogo: custo de produção, margem sugerida e preço médio do mercado, na aba GoodPrice da loja.",
[
("O que é", """
<b>GoodPrice</b> (Calculator e Alert Price GP, de Orflash-EcoSim) é uma calculadora de preços integrada ao jogo. Não precisa de conta, site nem sincronização: ela lê os dados direto deste servidor.

Segundo o autor, a margem de lucro é só uma <b>recomendação</b>: a calculadora mostra também o <b>preço médio</b> praticado pelos outros vendedores, e o preço final é decisão sua. A margem recomendada é dinâmica e muda com a quantidade fabricada.
"""),
("O que ela leva em conta", """
Ao calcular o custo de produção, o mod considera <b>talentos</b>, <b>custo das máquinas</b> e <b>calorias</b> gastas. Você pode importar de uma vez todos os itens da sua profissão para a loja.

Os administradores podem definir preço mínimo e/ou máximo, que a calculadora aplica sozinha.
"""),
("Onde usar", """
Abra a sua loja, carrinho ou um dos mercados e clique na aba <b>GoodPrice</b>. Ela aparece na [StoreItem], no [WoodShopCartItem] e nos oito mercados ([CarpenterMarketItem], [MasonMarketItem], [SmithMarketItem], [EngineerMarketItem], [FarmerMarketItem], [ChefMarketItem], [HunterMarketItem], [TailorMarketItem]).

A interface está disponível em inglês, francês, italiano, espanhol, alemão e russo. Não há português.
"""),
("Observação", """
O selo "premium" do mod só põe uma estrela ao lado do nome e está desligado neste servidor. Todos os dados do GoodPrice ficam neste servidor.
"""),
])

# ------------------------------------------------------------------ Smart Storage
pagina("Smart Storage", "StorageChestItem",
"O que sai da mesa de trabalho vai sozinho para o estoque que faz mais sentido, sem arrastar prioridades à mão.",
[
("O que faz", """
<b>Smart Storage</b> (StormVeil) reordena os estoques ligados a uma mesa de trabalho para que o item recém-fabricado caia no melhor lugar. A ordem que ele usa, segundo o autor:

1. <b>Estoque especializado</b> primeiro: geladeira ou silo para comida, lixeira ou composteira para lixo, porão de pesca para peixe, ou qualquer estoque em que você tenha definido uma lista de itens permitidos.
2. Dentro de uma categoria, estoque <b>elétrico ou com energia</b> antes do estoque simples.
3. Se nada for especializado, o de <b>maior capacidade</b>.
4. Material a granel escavado (terra, pedra) prefere <b>stockpile</b>; item comum prefere <b>baú</b>.
"""),
("O que ele nunca faz", """
• Não mexe no que um estoque aceita, só na ordem em que os estoques são tentados.
• Respeita dono, permissões e alcance de conexão: só reordena estoques que já estão ligados e autorizados.
• <b>Se você reordenar à mão</b> as prioridades de estoque de uma mesa, o mod deixa aquela mesa em paz daquele momento em diante.
"""),
("Veículos", """
O autor registra uma ação "Distribute" para veículos de carga, mas avisa que <b>ainda não há botão no jogo</b> para ela nesta versão.
"""),
])

# ------------------------------------------------------------------ MarketMod
pagina("Mercados", "SmithMarketItem",
"Oito mercados ao ar livre, um por profissão, com loja pública e estoque. Fabricados na bancada com nível 2 da profissão.",
[
("O que são", """
O <b>MarketMod</b> (EcoPulse) acrescenta oito bancas de mercado, uma para cada profissão, feitas para ficar ao ar livre no seu terreno. Cada uma funciona como <b>loja pública</b> com estoque, aparece no minimapa na categoria Economia e pode ser colocada dentro ou fora de casa. As bancas de comida (Chef, Farmer, Hunter) ganham animação quando estão em operação.
"""),
("Como fabricar", """
Todas se fabricam na [WorkbenchItem], com nível 2 da profissão correspondente:

• [CarpenterMarketItem] - Logging 2
• [MasonMarketItem] - Mining 2
• [SmithMarketItem] - Smelting 2
• [EngineerMarketItem] - Basic Engineering 2
• [FarmerMarketItem] - Gathering 2
• [ChefMarketItem] - Campfire Cooking 2
• [HunterMarketItem] - Hunting 2
• [TailorMarketItem] - Tailoring 2

Cada mercado ocupa 3 x 2 x 2 blocos.
"""),
("Abas extras", """
Neste servidor os oito mercados têm também as abas <b>Eco Gnome</b> e <b>GoodPrice</b>, como a loja normal. Veja [Eco Gnome] e [GoodPrice].
"""),
])

# ------------------------------------------------------------------ Gates
pagina("Portões e Cercas", "IronGrillItem",
"Portas duplas em 8 madeiras, grades de metal animadas, duas pontes levadiças e cercas decorativas.",
[
("Portas duplas", """
16 portas duplas de madeira, nas 8 madeiras do jogo (Birch, Cedar, Ceiba, Fir, Oak, Palm, Redwood, Spruce), em dois estilos:

• <b>Lumber Double Door</b> ([LumberDoubleDoorItem]) - nível 3 de material, fabricada na [SawmillItem].
• <b>Hewn Double Door</b> ([HewnDoubleDoorItem]) - nível 2 de material, fabricada na [CarpentryTableItem].

Ambas exigem <b>Carpentry 2</b>.
"""),
("Grades de metal", """
Três portões de grade animados, em ferro, cobre e ouro ([IronGrillItem], [CopperGrillItem], [GoldGrillItem]), fabricados na [AnvilItem] com <b>Blacksmith 2</b>. Abrem e fecham com animação e som. Ocupam 5 x 4 blocos: servem para entrada de veículos e portais grandes.
"""),
("Pontes levadiças", """
Fabricadas na [MasonryTableItem]:

• [WoodenDrawBridgeItem] - <b>Masonry 4</b>, nível 2 de material, 5 de largura por 5 de altura.
• [CastleDrawBridgeItem] - <b>Masonry 6</b>, nível 3 de material, 6 por 6, com arco de pedra e portas duplas acima do portão.

Pilares de pedra, correntes de ferro e um tablado de madeira que sobe e desce sob comando.
"""),
("Cercas decorativas", """
Blocos de cerca em ferro, cobre e ouro ([IronFenceItem], [CopperFenceItem], [GoldFenceItem]), fabricados na [AnvilItem] com <b>Smelting 1</b>. Empilháveis e giráveis, cada material tem 27 formas em 5 grupos: paredes retas, cantos de 90 graus, diagonais de 45 graus, paredes com borda e cantos com borda. Cada grupo traz variantes com barras, pontas, meias pontas, pontas baixas e pontas ascendentes.
"""),
])

# ------------------------------------------------------------------ Hot Wheels
pagina("Hot Wheels", "BicycleItem",
"Bicicleta, patinete, moto, ônibus escolar, jetski a vapor, jetski elétrico e Tesla Model 3, além dos carregadores elétricos.",
[
("Os veículos", """
• [ScooterItem] - Patinete. Basic Engineering 2, na [WainwrightTableItem].
• [BicycleItem] - Bicicleta. Basic Engineering 3, na [WainwrightTableItem].
• [MotoItem] - Moto. Mechanics 2, na [AssemblyLineItem].
• [SteamPaddleCraftItem] - Jetski a vapor, movido a carvão. Shipwright 5, no [MediumShipyardItem].
• [JetSkiItem] - Jetski elétrico. Shipwright 5, no [MediumShipyardItem].
• [SchoolBusItem] - Ônibus escolar com 29 lugares, contando o motorista. Industry 2, na [RoboticAssemblyLineItem].
• [TeslaModel3Item] - Tesla Model 3, elétrico. Electronics 2, na [RoboticAssemblyLineItem].

Os veículos podem ser pintados como os do jogo.
"""),
("Peças e carregadores", """
Bicicleta e moto precisam de peças novas, feitas na [BlacksmithTableItem] com <b>Blacksmith 2</b>: [IronChainItem] e [BicycleFrameItem].

O Jet Ski e o Tesla Model 3 são elétricos e precisam ser recarregados no [WallChargerItem] ou no [TeslaSuperchargerItem], ambos fabricados na [ElectricMachinistTableItem] com <b>Electronics 1</b>.
"""),
])

# ------------------------------------------------------------------ Bigger Frames
pagina("Molduras Grandes", "BorderlessFrameLargeWideItem",
"Molduras 2x2, 3x2 e 2x3 para todo tipo de moldura do jogo, e seis molduras sem borda.",
[
("O que acrescenta", """
<b>Bigger Frames</b> (CavRn) acrescenta, para cada tipo de moldura existente no jogo, três tamanhos grandes: <b>Large Square</b> (2 x 2), <b>Large Wide</b> (3 x 2) e <b>Large Tall</b> (2 x 3). Existem para as molduras de madeira, ferro, cobre, ouro e para as versões ornamentadas.

Acrescenta também seis molduras <b>sem borda</b>, da profissão Masonry: [BorderlessFrameSquareItem], [BorderlessFrameTallItem], [BorderlessFrameWideItem], [BorderlessFrameLargeSquareItem], [BorderlessFrameLargeTallItem] e [BorderlessFrameLargeWideItem].
"""),
("Como fabricar", """
• Sem borda: [MasonryTableItem], <b>Masonry 4</b>.
• Molduras de madeira grandes: <b>Carpentry 4</b> (comuns) e <b>Carpentry 5</b> (ornamentadas).
• Molduras de metal grandes: <b>Blacksmith 4</b> (ferro, cobre e ouro) e <b>Blacksmith 6</b> (ferro e ouro ornamentados).
"""),
])

# ------------------------------------------------------------------ Mixology
pagina("Mixology", "MixologyTableItem",
"Duas profissões de bebidas: sucos e smoothies (Mixology) e coquetéis, cafés e chás (Advanced Mixology).",
[
("As duas profissões", """
<b>Mixology</b> está no mesmo patamar de Cooking e Baking e traz <b>6 sucos e 5 smoothies</b>. Ela também fabrica o <b>Tomato Sauce</b>, usado em receitas de Advanced Baking e Advanced Cooking, e torra café e seca folhas de chá para a profissão seguinte. Usa só plantações do jogo normal.

<b>Advanced Mixology</b> é a continuação natural, no patamar de Advanced Cooking e Advanced Baking: <b>5 coquetéis, 4 cafés e 5 chás</b>.

Segundo o autor, o mod ainda não é compatível com os jantares (Dinner Parties), porque as bebidas não têm modelo de comida no jogo. Neste servidor, Mixology custa 3 estrelas e Advanced Mixology custa 6 (veja [Custo das estrelas]).
"""),
("Mesas e utensílios", """
• [MixologyTableItem] - fabricada na [BloomeryItem] com <b>Smelting 3</b>. Usa energia mecânica.
• [AdvancedMixologyTableItem] - fabricada na [MachinistTableItem] com <b>Mechanics 5</b>.
• [WoodenBarrelItem] - [CarpentryTableItem], Logging 2.
• [CocktailShakerItem] - [BlastFurnaceItem], Advanced Smelting 2.
"""),
("O que se faz em cada nível", """
Na [MixologyTableItem]:
• Sucos ([AgaveJuiceItem], [HuckleberriesJuiceItem], [PapayaJuiceItem], [PineappleJuiceItem], [PricklyPearFruitJuiceItem], [TomatoJuiceItem]) - Mixology 1
• [TomatoSauceItem] e [MixologyUpgradeItem] - Mixology 2
• Smoothies ([DesertSmoothieItem], [FieldSmoothieItem], [ForestSmoothieItem], [ProteinSmoothieItem], [TropicalSmoothieItem]) - Mixology 3
• [AlchoholItem] - Mixology 5

Na [AdvancedMixologyTableItem]:
• Cafés ([BlackCoffeeItem], [CappuccinoItem], [CoffeeLatteItem], [IcedCoffeeItem]) - Advanced Mixology 1
• [EnglishBreakfastTeaItem] e [AdvancedMixologyUpgradeItem] - Advanced Mixology 2
• [MatchaTeaLatteItem], [OrchidTeaItem], [TrilliumTeaItem] - Advanced Mixology 3
• [BerryBubbleTeaItem] - Advanced Mixology 4
• Coquetéis ([BloodyMarryItem], [EspressoMartiniItem], [PinaColadaItem], [PurpleRainItem], [TheGrasshopperItem]) - Advanced Mixology 5
"""),
])

# ------------------------------------------------------------------ IceCream
pagina("Sorvetes", "IceCreamMachinItem",
"A profissão IceCream: máquina de sorvete, cones, picolés e potes, a partir das frutas do jogo.",
[
("A profissão", """
<b>IceCream</b> é uma especialidade de Chef que custa <b>4 estrelas</b> neste servidor (veja [Custo das estrelas]). Todas as receitas de sorvete são feitas na [IceCreamMachinItem], que se fabrica na [CarpentryTableItem] com <b>Basic Engineering 3</b>.

O mapa deste servidor foi gerado com o mod instalado, como o autor exige: a neve ([SnowItem]) funciona ao ser cavada.
"""),
("O que se faz", """
• [IceCubeItem] - Cooking 2, na máquina de sorvete.
• Cones de fruta (huckleberries, giant cactus fruit, papaya, pineapple) - IceCream 3; prickly pear e pumpkin - IceCream 4. Cada receita dá 2.
• Potes de sorvete (Tropical Duo, Red Cactus, Autumn Berries, Desert Multivitamin e outros) - a partir de IceCream 5. Cada receita dá 3.
• As receitas mais altas vão até IceCream 7.
"""),
])

# ------------------------------------------------------------------ StorageMore
pagina("StorageMore", "Shipping_01Item",
"Mais de 20 estoques novos: containers, paletes, big bag, estoques de madeira, estantes, rack de ferramentas e outros.",
[
("Na Mesa de Carpintaria (Carpentry)", """
• [PaletteItem] - Pallet: itens de construção e lingotes, 8 slots. Carpentry 1.
• [StockageOutilsItem] - Wall Tool Rack: ferramentas em slots dedicados, 32 slots. Carpentry 1.
• [PetitStockageWoodItem] - Small Wood Storage, 18 slots. Carpentry 1.
• [MoyenStockageWoodItem] - Medium Wood Storage, 24 slots. Carpentry 2.
• [GrandStockageWoodItem] - Large Wood Storage, 32 slots. Carpentry 3.
• [DressingItem] - Dressing. Carpentry 1.
• [SeedbarrelItem] - Seed Barrel. Carpentry 1.
"""),
("Na Mesa de Maquinista (Mechanics)", """
• [Petite_Simple_EtagereItem] - Small Single Shelf, 8 slots. Mechanics 1.
• [Petite_Double_EtagereItem] - Small Double Shelf, 16 slots. Mechanics 2.
• [Grande_Simple_EtagereItem] - Large Single Shelf, 32 slots. Mechanics 3.
• [Grande_Double_EtagereItem] - Large Double Shelf, 64 slots. Mechanics 4.
• [Shipping_01Item] - Blue Container, 32 slots. Mechanics 5.
• [Shipping_02Item] - Green Container, 64 slots. Mechanics 6.
• [Shipping_03Item] - Red Container, 128 slots. Mechanics 7.
• [CaisseOutilsItem] - Toolbox. Mechanics 1.
• [SiloPetroleItem] - Oil Refinery Silo. Mechanics 1.
• [BenneGravatItem] - Dumping Bin. Mechanics 5.
• [Shipping_dechetItem] - Polluting Waste Container. Mechanics 5.

As estantes guardam qualquer item do jogo.
"""),
("Outros", """
• [BigBagItem] - Big Bag: terra, areia, pedra e material triturado, 10 slots. [TailoringTableItem], Tailoring 2.
• [PoubelleItem] - Green Trash Bin. [WorkbenchItem], sem profissão.

Os tamanhos de pilha indicados pelo autor (40, 60 ou 80 por slot) são os do mod, antes do multiplicador de pilha deste servidor.
"""),
])

# ------------------------------------------------------------------ AdsMod
pagina("Painéis de Anúncio", "affiche_pub01Item",
"Três painéis que mostram a imagem que você quiser, pelo sistema de impressora do jogo.",
[
(None, """
<b>AdsMod</b> (Plex_) acrescenta três painéis publicitários em que o jogador exibe qualquer imagem usando o sistema de <b>impressora</b> do jogo. Neste servidor a imagem impressa passa por aprovação de um administrador antes de aparecer.

Fabricados na [BlacksmithTableItem]:

• [affiche_pub04Item] - Mobile Poster. Blacksmith 1.
• [affiche_pub02Item] - Urban Sign. Blacksmith 3.
• [affiche_pub01Item] - Large Format Panel. Blacksmith 5.
"""),
])

# ------------------------------------------------------------------ PumpGasMod
pagina("Posto de Gasolina", "PumpgasItem",
"Uma bomba de combustível que também é loja, e um totem com texto, para montar um posto de gasolina.",
[
(None, """
<b>PumpGasMod</b> (Plex_) traz dois objetos para quem quer ter um posto de gasolina:

• [PumpgasItem] - Fuel Pump: bomba de combustível que <b>também funciona como loja</b>. [MachinistTableItem], Mechanics 1.
• [Totem_EnglishItem] - Gas Station Totem: totem em que se escreve um texto. [WainwrightTableItem], Basic Engineering 2.
"""),
])

# ------------------------------------------------------------------ Whetstones
pagina("Pedras de Afiar", "IronWhetstoneItem",
"Repare ferramentas em qualquer lugar: botão direito com a pedra de afiar certa, sem precisar da bancada.",
[
("Como usar", """
Com a pedra de afiar na mão, <b>botão direito</b> repara a ferramenta correspondente, onde você estiver. Neste servidor uma pedra faz o <b>reparo completo</b> (100%).
"""),
("As seis pedras", """
• [WoodWhetstoneItem] - ferramentas de madeira. [ToolBenchItem], Basic Engineering (qualquer nível).
• [StoneWhetstoneItem] - ferramentas de pedra. [ToolBenchItem], Basic Engineering 1.
• [IronWhetstoneItem] - ferramentas de ferro. [GrindstoneItem], Blacksmith 2.
• [SteelWhetstoneItem] - ferramentas de aço e modernas. [PowerHammerItem], Blacksmith 4.
• [TractorWhetstoneItem] - os 5 implementos do trator: [SteamTractorScoopItem], [SteamTractorPlowItem], [SteamTractorSowerItem], [SteamTractorHarvesterItem] e [SteamTractorTreeCutterItem]. [AssemblyLineItem], Mechanics 3.
• [GasolineWhetstoneItem] - [ModernRockDrillItem] e [ChainsawItem]. [PowerHammerItem], Blacksmith 6.

Segundo o autor, também reparam os arcos ([WoodenBowItem], Recurve e [CompositeBowItem]) e os três pulverizadores de tinta.
"""),
])

# ------------------------------------------------------------------ Tailings
pagina("Rejeitos", "TailingsItem",
"Transforme rejeitos úmidos em rejeitos secos e estes em areia, argila ou terra; e escória em enxofre.",
[
(None, """
<b>Tailings to Sand, Clay or Dirt</b> (GadgetPaPa) acrescenta receitas para se livrar dos rejeitos da mineração em vez de estocá-los:

• [WetTailingsItem] vira [TailingsItem] (rejeito seco).
• [TailingsItem] vira [SandItem], [ClayItem] ou [DirtItem].
• [SlagItem] vira [SulfurItem].

Duas mesas fazem as mesmas receitas, em escalas diferentes:

• [KilnItem] - <b>Pottery 1</b>, 1 por receita.
• [IncineratorItem] - <b>Recycling 1</b>, 8 por receita.
"""),
])

# ------------------------------------------------------------------ Wolf Pack + Water Tower
pagina("Wolf Pack Utilities", "SolarPanelItem",
"Moinho avançado, painel solar, poste de transmissão mecânica e torre de água, com alumínio e silício como materiais novos.",
[
("Objetos", """
• [AdvancedWindmillItem] - Advanced Windmill. [MachinistTableItem], Mechanics 5.
• [SolarPanelItem] - Solar Panel. [MachinistTableItem], Mechanics 5.
• [MechanicalTransmissionPoleItem] - Mechanical Transmission Pole. [WainwrightTableItem], Basic Engineering 2.
• [WaterTowerItem] - Water Tower: segundo o autor, <b>bombeia água do solo</b>. [SawmillItem], Carpentry 3. (Mod Water Tower, do mesmo autor.)
"""),
("Materiais novos", """
• [AluminaItem] - [OilRefineryItem], Oil Drilling 1.
• [AluminumBarItem] - [BlastFurnaceItem], Advanced Smelting 1.
• [AluminumSheetItem] - [ScrewPressItem], Mechanics 1.
• [CokeItem], [SiliconItem] e [SiliconPlateItem] - [BlastFurnaceItem], Smelting 7.
"""),
])

# ------------------------------------------------------------------ Air Pollution Filter
pagina("Filtros de Poluição", "BasicPollutionFilterItem",
"Módulos que reduzem em 20, 40 ou 60 por cento a poluição de máquinas e veículos, ocupando um slot de módulo.",
[
("O que fazem", """
Três níveis de filtro, instalados no slot de módulo de máquinas e veículos, reduzem a emissão de CO2 deles. O autor lembra a escolha: o slot ocupado pelo filtro não recebe módulo de eficiência ou velocidade.

• [BasicPollutionFilterItem] - reduz <b>20%</b>. [MachinistTableItem], Mechanics 2.
• [AdvancedPollutionFilterItem] - reduz <b>40%</b>. [RoboticAssemblyLineItem], Mechanics 4.
• [IndustrialPollutionFilterItem] - reduz <b>60%</b>. [ElectronicsAssemblyItem], Industry 6.

Cada filtro superior usa o inferior como ingrediente. A poluição nova é a poluição-base multiplicada por (1 menos a redução), e a dica do objeto se atualiza na hora.
"""),
("Onde cabem", """
Máquinas: [CombustionGeneratorItem], [IndustrialGeneratorItem], [BlastFurnaceItem], [CementKilnItem], [OilRefineryItem] e [StoveItem]. As que já têm módulos próprios (alto-forno, forno de cimento, refinaria, fogão) aceitam o filtro ao lado deles.

Veículos: [ExcavatorItem], [IndustrialBargeItem], [TruckItem], [TrailerTruckItem], [SkidSteerItem], [MediumFishingTrawlerItem], [CraneItem], [SteamTruckItem], [PoweredCartItem] e [SteamTractorItem].
"""),
])

# ------------------------------------------------------------------ ExtraShapes
pagina("Formas Extras", "AshlarGraniteItem",
"Parede diagonal a 45 graus e coluna de um quarto para os seis tipos de pedra lavrada (Ashlar).",
[
(None, """
<b>ExtraShapes</b> (McMiller) acrescenta duas formas de bloco, com as texturas do próprio jogo, para todas as pedras lavradas: [AshlarGraniteItem], [AshlarLimestoneItem], [AshlarBasaltItem], [AshlarGneissItem], [AshlarSandstoneItem] e [AshlarShaleItem].

• <b>Diagonal</b>: parede a 45 graus, com a textura de tijolo lavrado em todas as faces.
• <b>Quarter Column</b>: coluna de um quarto, com forma dinâmica e textura bruta nas faces que não são da coluna.

As formas aparecem no <b>seletor de forma</b> ao construir com pedra lavrada. Não existem para outros materiais (Mortared, Brick, Lumber, Concrete).
"""),
])

# ------------------------------------------------------------------ Waterwheel Windmill not Industrial
pagina("Moinhos não industriais", "WaterwheelItem",
"Roda d'água e moinho de vento não transformam o ambiente externo em industrial.",
[
(None, """
<b>Waterwheel Windmill not Industrial</b> (Orflash-EcoSim): segundo o autor, com este mod o seu moinho <b>não transforma o exterior em industrial</b>. O mod substitui os arquivos da [WaterwheelItem], do [WindmillItem], do [SteamEngineItem] e do [CombustionGeneratorItem]; as receitas continuam as do jogo normal.
"""),
])

# ------------------------------------------------------------------ Early Skid
pagina("Trator a Vapor minerador", "SteamTractorItem",
"O Trator a Vapor pode minerar com a pá (Steam Scoop).",
[
(None, """
<b>Early Skid</b> (Stellion): segundo o autor, o mod habilita a <b>mineração com o Trator a Vapor</b> ([SteamTractorItem]) usando o implemento de pá ([SteamTractorScoopItem]). O trator continua sendo fabricado na [AssemblyLineItem] com Mechanics 2.
"""),
])

# ------------------------------------------------------------------ índice (página-mãe)
# HIERARQUIA DA ECOPEDIA — três níveis, não dois. Fonte: docs.play.eco, classes de Eco.Gameplay.EcopediaRoot
# (lidas em 10/09/2026), mais o exemplo oficial StrangeLoopGames/EcoModKit Examples/EcopediaPage:
#   CAPÍTULO   EcopediaChapter  → tem  List<EcopediaCategory> Categories   arquivo "Nome.xml" com <ecopediachapter/>
#   CATEGORIA  EcopediaCategory → tem  Dictionary<string,EcopediaPage> Pages   arquivo "Nome.xml" com chapter="..."
#   PÁGINA     EcopediaPage     → tem  Sections e SubPages                 arquivo "Categoria;Pagina.xml"
# No menu da esquerda, embaixo do título do capítulo aparecem as CATEGORIAS (ícone + nome); as PÁGINAS da
# categoria selecionada aparecem na tira de ícones do alto. É o que Mods faz: capítulo Mods → categoria
# BBC-Brasil → 26 páginas.
# POR QUE O CAPÍTULO SAIU VAZIO em 09 e 10/09: os dois arquivos com chapter= ("Configuracao do jogo" e
# "Arvores densas") eram CATEGORIAS, e categoria sem nenhuma página dentro não aparece no menu. Não era
# acento (as páginas "Painéis de Anúncio" e "Pá com E" têm acento e funcionam) nem espaço no nome do
# capítulo (o mod Elixr Mods usa <ecopediachapter/> no arquivo "Elixr Mods.xml", com espaço, e funciona).
CAPITULO_PARAM = "Parametros do Servidor"   # ASCII mantido: é o que já aparece no menu e não há motivo para mexer
CAPITULO_PARAM_PRIORIDADE = "-11"
CATEGORIA_PARAM = "Ajustes do servidor"     # o item com ícone que aparece EMBAIXO do título do capítulo
CATEGORIA_PARAM_ICONE = "ContractBoardItem"
CATEGORIA_PARAM_RESUMO = "O que este servidor mudou na configuração do jogo, em relação ao Eco normal."
INDICE_ICONE = "StoreItem"                  # ícone da CATEGORIA "BBC-Brasil" no menu da esquerda
PAGINA_INDICE = "Sobre o servidor"          # o índice é uma PÁGINA; priority -10 o deixa PRIMEIRO na tira
PAGINA_INDICE_ICONE = "PaperItem"
INDICE_RESUMO = "Manuais do servidor BBC-Brasil: o que muda em relação ao Eco normal e como usar cada mod instalado."

# ---------------------------------------------------------------- tradução das páginas do MarketMod
ECOPULSE_XML = """<ecopedia icon="Ecopulse" chapter="Mods" priority="-1">
  <summary>Mods criados pela EcoPulse.</summary>

  <section type="header">Mods EcoPulse</section>
  <section>
    <b>EcoPulse</b> é uma coleção de mods que acrescentam ao Eco itens decorativos e mecânicas de jogo novas. Neste servidor estão instalados o <b>MarketMod</b> (mercados por profissão) e o <b>Gates</b> (portas duplas, grades, pontes levadiças e cercas). Veja também [Mercados] e [Portões e Cercas].
  </section>
</ecopedia>
"""

ECOPULSE_MARKET_XML = """<ecopedia icon="SmithMarketItem">
	<section type="banner" image="MarketModEcopedia" />
  <summary>Oito bancas de mercado, uma por profissão, para comércio e estoque.</summary>

  <section type="header">Market Mod</section>
  <section>
    O <b>Market Mod</b> acrescenta ao Eco oito bancas de mercado, uma por profissão, feitas para melhorar o comércio e o estoque de cada setor da economia. Cada mercado é um ponto de venda dedicado à sua profissão e traz elementos visuais e funcionais próprios para o seu assentamento.
  </section>

  <section type="header">As bancas</section>
  <section>
    <b>Oito mercados de profissão:</b>

    • [CarpenterMarketItem] - Mercado do Carpinteiro: madeira e produtos de carpintaria
    • [ChefMarketItem] - Mercado do Chef: comida e culinária, com vitrine animada
    • [EngineerMarketItem] - Mercado do Engenheiro: máquinas e equipamentos técnicos
    • [FarmerMarketItem] - Mercado do Fazendeiro: produtos agrícolas, com vitrine animada
    • [HunterMarketItem] - Mercado do Caçador: suprimentos de caça e materiais de animais
    • [MasonMarketItem] - Mercado do Pedreiro: pedra e materiais de alvenaria
    • [SmithMarketItem] - Mercado do Ferreiro: metais e produtos de forja
    • [TailorMarketItem] - Mercado do Alfaiate: tecidos e roupas

    Todos ocupam 3 x 2 x 2 blocos, com estoque e acesso público. Os mercados de comida (Chef, Farmer, Hunter) ganham animação quando estão em operação. Como fabricar cada um: veja [Mercados].
  </section>

  <section type="header">Recursos</section>
  <section>
    Cada banca inclui:

    • Loja pública para negociar com outros jogadores
    • Aparece no minimapa, na categoria Economia
    • Aparência profissional, de acordo com a especialidade
    • Pode ser colocada dentro ou fora de casa

    Os mercados de comida mostram o estado animado quando estão operando, dando retorno visual do comércio ativo.
  </section>
</ecopedia>
"""

# ---------------------------------------------------------------- montagem
def esc(t):
    return t.replace("&", "&amp;")

def monta_subpagina(titulo, icone, resumo, secoes, capitulo=None, prioridade=-1, prio_pagina=None):
    # Com `capitulo`: sai um arquivo de CATEGORIA (chapter= + priority), como Mods/BBC-Brasil.xml.
    # Sem `capitulo`: sai uma PÁGINA (só icon), como Mods/BBC-Brasil;Custo das estrelas.xml.
    # `prio_pagina` ordena as páginas na tira de ícones; sem ele, o jogo ordena por nome.
    if capitulo:
        abre = '<ecopedia icon="%s" chapter="%s" priority="%d">' % (icone, capitulo, prioridade)
    elif prio_pagina is not None:
        abre = '<ecopedia icon="%s" priority="%d">' % (icone, prio_pagina)
    else:
        abre = '<ecopedia icon="%s">' % icone
    partes = [abre, "  <summary>%s</summary>" % esc(resumo), ""]
    for cab, texto in secoes:
        if cab:
            partes.append('  <section type="header">%s</section>' % esc(cab))
        partes.append("  <section>")
        partes.append(esc(texto.strip("\n")))
        partes.append("  </section>")
        partes.append("")
    partes.append("</ecopedia>")
    return "\n".join(partes) + "\n"

def monta_categoria_mods():
    # CATEGORIA "BBC-Brasil" do capítulo Mods: só ícone e resumo. O texto do índice NÃO vem aqui —
    # EcopediaCategory tem Summary e NÃO tem Sections (docs.play.eco), e em campo clicar na categoria
    # abre a primeira PÁGINA da tira, nunca um texto da categoria. Índice em arquivo de página, abaixo.
    return '<ecopedia icon="%s" chapter="Mods" priority="-5">\n  <summary>%s</summary>\n</ecopedia>\n' % (
        INDICE_ICONE, esc(INDICE_RESUMO))

def monta_indice():
    def lista(grupo):
        return "\n\n".join("• <b>%s</b> - %s" % (t, r) for t, _, r, _, g in PAGINAS if g == grupo)
    return """<ecopedia icon="%s" priority="-10">
  <summary>%s</summary>

  <section type="header">Servidor BBC-Brasil</section>
  <section>
Estas páginas foram escritas pela administração do servidor <b>BBC-Brasil</b> (na lista de servidores: "BBC-BRASIL 5X, PT-BR, MODS, METEORO 60 DIAS"). Elas separam três coisas: o que foi <b>parametrizado</b> (valores de configuração do jogo), os <b>mods do servidor</b> (código nosso que muda o comportamento padrão do Eco) e os <b>mods de terceiros</b> instalados. O texto vem das instruções publicadas pelo autor de cada mod e do que foi conferido no código instalado aqui: profissão, nível e mesa de cada receita foram lidos deste servidor.
  </section>

  <section type="header">Parametros do Servidor</section>
  <section>
No menu da esquerda, em <b>Parametros do Servidor</b>, item <b>Ajustes do servidor</b>:

%s
  </section>

  <section type="header">Mods do servidor BBC-Brasil</section>
  <section>
%s
  </section>

  <section type="header">Mods de terceiros</section>
  <section>
%s
  </section>

  <section type="header">Comandos</section>
  <section>
• Escreva o comando por extenso, como está na página, e cole no chat do jogo.

• Quando um comando recebe mais de um valor, os valores são separados por vírgula.

• Comandos que começam com <b>/ecognome</b> são do mod Eco Gnome; <b>/custoestrelas</b> é deste servidor.
  </section>

  <section type="header">Ícones e cores nas placas</section>
  <section>
Toda placa com texto aceita ícones do jogo, cores, tamanho e alinhamento. A galeria com todos os ícones e um montador que gera o texto pronto para colar na placa está em <b>dartangn.github.io/icones-eco-bbc</b>. Abra no navegador do PC, monte, copie e cole no texto da placa.
  </section>
</ecopedia>
""" % (PAGINA_INDICE_ICONE, esc(INDICE_RESUMO), esc(lista("param")), esc(lista("nosso")), esc(lista("terceiro")))

# ---------------------------------------------------------------- validação
def valida_links(nome_arquivo, xml, titulos):
    erros = []
    for link in re.findall(r"\[([^\]\n]+)\]", xml):
        if link.endswith("Item"):
            if link not in itens:
                erros.append("%s: item desconhecido [%s]" % (nome_arquivo, link))
        else:
            if link not in titulos:
                erros.append("%s: página desconhecida [%s]" % (nome_arquivo, link))
    return erros

def valida_xml(nome_arquivo, xml):
    try:
        ET.fromstring(xml.encode("utf-8"))
    except ET.ParseError as e:
        return ["%s: XML inválido: %s" % (nome_arquivo, e)]
    if "<" in re.sub(r"</?(ecopediachapter|ecopedia|summary|section|b|i)\b[^>]*>", "", xml):
        return ["%s: '<' solto no texto" % nome_arquivo]
    return []

def main():
    os.makedirs(SAIDA, exist_ok=True)
    titulos = set(t for t, _, _, _, _ in PAGINAS) | {"BBC-Brasil", PAGINA_INDICE}
    if CATEGORIA_PARAM_ICONE not in itens:
        sys.exit("ícone desconhecido para a categoria %s: %s" % (CATEGORIA_PARAM, CATEGORIA_PARAM_ICONE))
    if PAGINA_INDICE_ICONE not in itens:
        sys.exit("ícone desconhecido para a página %s: %s" % (PAGINA_INDICE, PAGINA_INDICE_ICONE))
    arquivos = {"Mods/BBC-Brasil.xml": monta_categoria_mods(),
                "Mods/BBC-Brasil;%s.xml" % PAGINA_INDICE: monta_indice(),
                "Mods/EcoPulse.xml": ECOPULSE_XML,
                "Mods/EcoPulse;Market.xml": ECOPULSE_MARKET_XML,
                # capítulo (só o título/divisória no menu)
                "%s/%s.xml" % (CAPITULO_PARAM, CAPITULO_PARAM): '<ecopediachapter priority="%s" />\n' % CAPITULO_PARAM_PRIORIDADE,
                # categoria (o item com ícone embaixo da divisória) — sem ela as páginas não aparecem
                "%s/%s.xml" % (CAPITULO_PARAM, CATEGORIA_PARAM): monta_subpagina(
                    CATEGORIA_PARAM, CATEGORIA_PARAM_ICONE, CATEGORIA_PARAM_RESUMO, [],
                    capitulo=CAPITULO_PARAM, prioridade=-5)}
    icones = {INDICE_ICONE: "BBC-Brasil", CATEGORIA_PARAM_ICONE: CATEGORIA_PARAM,
              PAGINA_INDICE_ICONE: PAGINA_INDICE}
    n_param = 0
    for titulo, icone, resumo, secoes, grupo in PAGINAS:
        if icone not in itens:
            sys.exit("ícone desconhecido para %s: %s" % (titulo, icone))
        if icone in icones:
            sys.exit("ícone repetido: %s em '%s' e '%s' (confunde o jogador)" % (icone, icones[icone], titulo))
        icones[icone] = titulo
        if grupo == "param":
            # páginas da categoria: arquivo "Categoria;Pagina.xml", igual ao que o Mods faz
            arquivos["%s/%s;%s.xml" % (CAPITULO_PARAM, CATEGORIA_PARAM, titulo)] = monta_subpagina(
                titulo, icone, resumo, secoes, prio_pagina=-5 + n_param)
            n_param += 1
        else:
            arquivos["Mods/BBC-Brasil;%s.xml" % titulo] = monta_subpagina(titulo, icone, resumo, secoes)
    erros = []
    for nome, xml in arquivos.items():
        erros += valida_xml(nome, xml)
        erros += valida_links(nome, xml, titulos)
        if "﻿" in xml:
            erros.append("%s: BOM" % nome)
    if erros:
        print("\n".join(erros)); sys.exit(1)
    for pasta in os.listdir(SAIDA):          # arquivo obsoleto não pode sobreviver ao tar
        cheio = os.path.join(SAIDA, pasta)
        if os.path.isfile(cheio) and cheio.endswith(".xml"):
            os.remove(cheio); print("  removido obsoleto (raiz): %s" % pasta); continue
        if os.path.isdir(cheio):
            for velho in os.listdir(cheio):
                if velho.endswith(".xml") and "%s/%s" % (pasta, velho) not in arquivos:
                    os.remove(os.path.join(cheio, velho)); print("  removido obsoleto: %s/%s" % (pasta, velho))
    for nome, xml in arquivos.items():
        destino = os.path.join(SAIDA, *nome.split("/"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(xml)
    print("gerados %d arquivos em %s" % (len(arquivos), SAIDA))
    for nome in sorted(arquivos):
        print("  %-58s %6d bytes" % (nome, len(arquivos[nome].encode("utf-8"))))

if __name__ == "__main__":
    main()
