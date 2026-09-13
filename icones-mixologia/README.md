# Ícones da Mixologia — recorte do fundo

**Estado: PRONTO, NÃO INSTALADO.** Para testar no servidor de teste em 13/09/2026, e só depois
na produção.

---

## 1. O problema, e a causa exata

Os ícones da Mixologia saem com um quadrado claro na placa, e marcar **"ícone sem fundo"**
(`type="nobg"`) não muda nada.

**Causa, medida — não deduzida:**

| | |
|---|---|
| Formato das 65 texturas do mod | **DXT1** |
| O que o DXT1 tem de canal alfa | **nenhum** |
| Fundo da arte | degradê pastel (amarelo → rosa), não branco |

**`nobg` não tem nada que respeitar.** Não existe transparência no arquivo: o quadrado inteiro é
imagem opaca, e em 32 px o degradê pastel lê como uma caixa branca.

## 2. Como isso foi estabelecido

1. **Medição de alfa** nos PNG extraídos do GoodPrice: Mixologia 100% opaca; jogo base ~70% opaco
   com 30% de meio-tom.
2. **Placa de teste em campo** (12/09/2026), 8 linhas. Resultado:
   - `nobg` na Mixologia → quadrado igual;
   - `TomatoItem` e `CeramicTeaCupItem` com `nobg` → limpos;
   - `BlackCoffeeItem` e `AgaveJuiceItem` → quadrado também. **(Eu os usei como "controle do jogo
     base" e estava ERRADO: são itens da própria Mixologia. O teste não discriminou nada.)**
   - `iconcolor='FFFFFF00'` → o ícone sumiu **inteiro, quadrado junto** — prova de que o claro é
     pixel da imagem, e não uma placa desenhada atrás.
   - `iconcolor='00FFFFFF'` → quadrado ciano, o que fixa a ordem em **`RRGGBBAA`**.
3. **Abertura do bundle** com UnityPy: 65 Texture2D 512×512, todas formato 10 (DXT1).

> **Existe ícone do jogo base no mesmo estado** — 64 dos 290, quase todos da família de lixo,
> reciclagem e filtros. Medido cruzando os 290 com as classes `*Item` de `__core__` e `UserCode`.
> *Mas os dois exemplos que usei na placa de teste eram da própria Mixologia, então o teste não
> provou isso — a medição depois é que provou.* É escolha de importação no Unity: arte sem canal
> alfa vira DXT1.

## 3. O que foi feito

Sem Unity. `UnityPy` abre e **regrava** AssetBundle direto do Python.

| Passo | Arquivo | O que faz |
|---|---|---|
| 1 | `inspecionar.py` · `mapear.py` | listam o conteúdo do bundle e ligam Sprite → Texture2D |
| 2 | `exportar.py` | despeja as 66 texturas em `originais/` |
| 3 | `recortar.py` | tira o fundo e grava PNG com alfa em `recortados/` |
| 4 | `regravar.py` | devolve as imagens ao bundle em **DXT5** e escreve `MixologyMod.unity3d.novo` |
| 5 | `instalar-icones-mixologia.sh` | troca no servidor, com backup e `--desfazer` |

**Como o recorte funciona.** O fundo é liso, então é crescimento de região a partir da borda,
comparando cada pixel novo com **o vizinho já aceito** — e não com uma cor fixa. É isso que
acompanha o degradê sem vazar para dentro do desenho. Duas travas contra vazamento: passo local
pequeno (`--passo`, padrão 10) e distância máxima da cor da moldura (`--global`, padrão 60). A borda
do recorte ganha meio-tom, senão fica serrilhada.

### As travas que já pegaram alguma coisa

- **`recortar.py` marca como suspeito** o que remove menos de 5% ou mais de 90%. Pegou o
  `LiberationSans SDF Atlas` — um atlas de fonte, que viraria 100% transparente e **quebraria o
  texto do mod**.
- **`regravar.py` só toca em textura referenciada por um `Sprite`**, e pula por nome qualquer
  `Font` / `SDF` / `Atlas`. Malha, material e fontes ficam intocados.
- **Ele reabre o arquivo que gerou e confere** contagem de objetos, formato e presença de pixel
  transparente. Só imprime `OK` se as três passarem.

### Resultado

```
texturas referenciadas por Sprite: 65
trocadas: 65  | pulados: 3   (Font Texture, LiberationSans SDF Atlas x2)
objetos: original 2021  novo 2021  OK
formatos no novo: DXT5 65, RGBA32 1, Alpha8 2
texturas COM pixel transparente: 65 | sem: 0
```

| | Bytes |
|---|---|
| original | 5.137.910 |
| novo | 5.225.609 (**+1,7%**) |

*DXT5 ocupa o dobro do DXT1 por textura, mas o LZ4 do bundle come quase toda a diferença. Foi por
isso que não usei RGBA32, que deixaria o pacote em dezenas de MB — e todo jogador baixa isso.*

**md5** — o instalador confere os dois:

```
1b549c38fb591411e96b7bb331a399d1  MixologyMod.unity3d        (original do autor)
b0cf7c1326caafd2dd70288789665a33  MixologyMod.unity3d.novo   (o nosso)
```

## 4. Como instalar, amanhã, no teste

```
.\eco-conectar.ps1 -Scp "mixologia-icones\MixologyMod.unity3d.novo"
.\eco-conectar.ps1 -Scp "mixologia-icones\instalar-icones-mixologia.sh"
```

No servidor, **com o servidor parado**:

```
bash ~/instalar-icones-mixologia.sh --seco      # mostra o plano
bash ~/instalar-icones-mixologia.sh             # instala
```

Subir, **entrar no jogo e olhar uma placa**. Voltar atrás é
`bash ~/instalar-icones-mixologia.sh --desfazer`.

### O que observar no teste, e é o único ponto que não está provado

**O cliente guarda o pacote em cache.** O arquivo mudou de tamanho e de hash, então o esperado é que
ele baixe de novo — mas isso **não foi verificado**. Se o quadrado continuar depois da troca:

1. é cache, não o arquivo — o md5 no servidor já foi conferido pelo instalador;
2. testar com um jogador que **nunca entrou** neste servidor, ou limpar o cache do cliente.

*Distinguir "não funcionou" de "não chegou" é o teste que importa. Sem isso, a conclusão sai errada.*

## 4-B. O caminho que NÃO morre na atualização — mod nosso, só de asset

Ideia do Raul: em vez de substituir o arquivo do autor, publicar **os mesmos ícones sob nomes
nossos** e apontar as placas para eles.

`mod-bbc.py` pega o pacote já recortado e **renomeia os 71 prefabs** para `<Nome>BBC`
(`PinaColadaItem` → `PinaColadaItemBBC`), gerando `IconesMixologiaBBC.unity3d`.

**Por que renomear prefab resolve.** O cliente acha o ícone por um **GameObject com o nome exato da
classe do item** — `PinaColadaItem`, com filhos `Background` / `Icon` / `Foreground` / `FullImage` /
`FullName`. Os sprites se chamam "1", "14", "60", então não é por eles. Renomear o prefab cria um
endereço novo e livre, e é trocar um campo de texto.

| | |
|---|---|
| prefabs renomeados | **71 de 71** |
| objetos antes / depois | 2021 / 2021 |
| nomes em comum com o mod original | **nenhum** — inclusive os `TalentGroup` |

*Renomeei os `TalentGroup` junto de propósito: dois bundles com o mesmo nome de prefab é a única
forma conhecida de os dois brigarem, e assim não sobra nenhum.*

**Sem C#, e isso é decisão, não preguiça.** Mod nosso que referencia **tipo** de outro mod derruba o
servidor quando aquele mod não está instalado — é a armadilha do `PergaminhosDosMods.cs`. Só asset:
o risco não existe, e os ícones continuam valendo mesmo se a Mixologia sair.

### O que ainda não está provado, e é o teste

**Que o cliente indexe prefab de bundle de outro mod.** É plausível — é assim que um mod adiciona
ícone — mas não verificado. O teste é uma placa:

```
<icon name="PinaColadaItemBBC" type="nobg"></icon>
```

- **aparece** → este é o caminho, e ele sobrevive a atualização;
- **não aparece** → volta a ser `instalar-icones-mixologia.sh`, que substitui o arquivo do autor.

Os dois estão prontos. Um teste decide, no mesmo arranque.

### A galeria de placas já está preparada

Caixa **"ícones BBC"**, ligada por padrão: os 40 ícones da Mixologia que existem na galeria saem com
o nome `...BBC` e ganham etiqueta verde **BBC**. **Desligar é um clique** — é o que fazer se o teste
falhar, e é por isso que a caixa existe em vez de a troca ser fixa no código.

### Instalar

```
.\eco-conectar.ps1 -Scp "mixologia-icones\IconesMixologiaBBC.unity3d"
.\eco-conectar.ps1 -Scp "mixologia-icones\instalar-mod-icones-bbc.sh"
```

```
bash ~/instalar-mod-icones-bbc.sh --seco
bash ~/instalar-mod-icones-bbc.sh
```

Vai para `Mods/UserCode/KabongBrasil/IconesBBC/`. Desinstalar é `--desfazer`.

---

## 4-C. Na fila do reinício de 13/09 — conferido por ensaio

`/opt/eco/pendentes/instalar-icones-bbc.py` + `payload/` (11 MB). Roda **com o servidor parado**.
Quatro passos: mod BBC → substituição com backup → cópia-mestra da galeria → republicação no painel
(`/opt/eco/server/WebClient/WebBin/placas`).

Ensaiar de novo a qualquer momento, sem escrever nada:

```
sudo -u ecosrv python3 /opt/eco/pendentes/instalar-icones-bbc.py --ensaio
```

**Não se anota em `instalados-neste-reinicio.txt`**, de propósito: aquela lista existe para desfazer
`.cs` que não compila, e asset não passa pelo compilador. Anotar faria um erro de compilação de
*outra* coisa remover estes arquivos sem motivo.

## 4-D. Os outros mods com o mesmo defeito

Dos 290 ícones sem recorte: **40 são da Mixologia** (feitos), **~83 de outros mods** — IceCream
(`RedCactusTubItem` e companhia), StorageMore, Gates, MarketMod, HotWheels — e **64 do jogo base**.

Os de mod se corrigem com **exatamente estes scripts**, trocando o arquivo de entrada: os bundles
estão todos no servidor. Os do jogo base não: a arte vive nos pacotes do **cliente**, e a única
cópia que temos é a de 32×32 do GoodPrice — dá para empacotar assim, mas em resolução menor que a
original, e isso precisa ser decisão consciente, não descuido.

> **A ordem importa mais que o volume.** Nada disto foi visto funcionando dentro do jogo ainda.
> Fazer os outros 83 antes do primeiro teste seria refazer tudo se o caminho estiver errado.

---

## 5. Quando a Mixologia for atualizada

A correção **morre** — é arquivo binário do mod, substituído pelo pacote novo. Foi decisão
consciente do Raul: *"não me importo que quebre na próxima atualização"*.

Refazer é a sequência inteira, e demora minutos:

```
# baixar o bundle novo do servidor para mixologia-icones/MixologyMod.unity3d
python exportar.py
python recortar.py
python regravar.py
# atualizar MD5_ORIGINAL e MD5_NOVO no topo de instalar-icones-mixologia.sh
```

O instalador avisa sozinho quando o md5 do alvo não é nenhum dos dois que ele conhece — que é
exatamente o sinal de que o mod foi atualizado.

## 6. Ferramentas instaradas nesta máquina

`UnityPy 1.25.3`, `Pillow 12.3.0`, `numpy 2.5.3` — via `pip`, em 12/09/2026.

**UnityPy lê e regrava AssetBundle sem o Unity.** Isso vale para qualquer mod, não só este: é a
ferramenta que faltava para mexer em asset de cliente neste projeto.

## 7. O que NÃO foi feito

- Nada foi instalado, nem no teste nem na produção.
- Os **64 ícones do jogo base** com o mesmo problema (lixo, sucata, filtros, upgrades) **não foram
  tocados** — mexer no `__core__` é regra quebrada. A galeria de placas marca os 290 sólidos com a
  etiqueta **FUNDO** para serem evitados.
