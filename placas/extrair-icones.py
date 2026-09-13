# -*- coding: utf-8 -*-
"""
Galeria + montador de placa para os ícones que a tag de placa aceita:   <icon name="NomeDaClasse" type=""></icon>

Os PNG (32x32, um por item do jogo) vêm dos recursos .NET embutidos no GoodPrice.dll e nas GoodPrice.Images.*.dll dos
mods (Eco.Plugins.GoodPrice.Resources.<Classe>.png / GoodPriceItem.Resources.<Classe>.png). A EXTRAÇÃO é feita pelo
PowerShell com reflexão, que lê o nome exato de cada recurso (casar por ordem NÃO funciona — testado em 09/09, deu
ícone trocado):

    $asm = [System.Reflection.Assembly]::ReflectionOnlyLoadFrom("$dir\\GoodPrice.dll")
    foreach ($r in $asm.GetManifestResourceNames()) {
      if ($r -match '\\.([A-Za-z0-9_]+)\\.png$') {
        $s = $asm.GetManifestResourceStream($r); $b = New-Object byte[] $s.Length; [void]$s.Read($b,0,$b.Length); $s.Close()
        [System.IO.File]::WriteAllBytes("$dir\\png\\$($Matches[1]).png", $b) } }

Este script só monta icones.html a partir da pasta png/ (1824 ícones em 09/09/2026: 1689 do jogo + 135 dos mods
MarketMod, Gates, HotWheels, IceCream, Mixology, StorageMore). Sem ícone de skill (a tag aceita CarpentrySkill mesmo assim).

Tags usadas no montador, todas do próprio jogo (strings do binário; icon e nobg confirmados na wiki oficial Printing_Press):
  <align="center">…</align>  <color=#RRGGBB>…</color>  <size=NN%>…</size>  <icon name="X" type="">texto</icon>  type="nobg"
Publicação: copiar icones.html para ../../site-icones/index.html, commit, git push (GitHub Pages, dartangn/icones-eco-bbc).
"""
import os, html

AQUI = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(AQUI, "png")
nomes = sorted(f[:-4] for f in os.listdir(PNG_DIR) if f.endswith(".png"))

# Icones de BORDA SOLIDA: type="nobg" NAO tem efeito neles, porque a arte nao tem
# recorte -- o quadrado inteiro e opaco. Lista produzida por classificar-alfa.py e
# CONFIRMADA em campo em 12/09/2026 (a previsao acertou 5 de 5 numa placa de teste).
SOLIDOS = set()
_lst = os.path.join(AQUI, "solidos.txt")
if os.path.exists(_lst):
    SOLIDOS = {l.strip() for l in open(_lst, encoding="utf-8") if l.strip()}

# Categoria de cada icone, de categorizar.py (tags do item -> classe-mae -> sufixo).
# Icones do NOSSO mod (bundle com os prefabs renomeados para <Nome>BBC, com alfa).
# So valem se IconesMixologiaBBC.unity3d estiver instalado no servidor.
# Os icones da Mixologia saem SEMPRE com o nome do nosso mod. Nao ha caixa na
# interface: decisao do Raul em 12/09/2026 -- "vamos colocar so os icones bbc que
# criamos, substituindo os de mesmo nome".
#
# SE O TESTE DE 13/09 FALHAR (o cliente nao achar prefab de bundle de outro mod),
# ponha USAR_BBC = False aqui e rode este script de novo: as placas voltam a pedir
# os nomes originais. E uma linha, de proposito -- com a decisao num lugar so, em
# vez de espalhada pelo codigo.
USAR_BBC = True

# Nome que a tag <icon name="..."> aceita. O arquivo vem do GoodPrice e nem sempre
# bate com a classe do jogo: profissao la e "TailoringSkillItem", no jogo e
# "TailoringSkill" -- o Item no fim NAO EXISTE. Ver nomes-reais.py.
REAL = {}
_re = os.path.join(AQUI, "nomes-reais.txt")
if os.path.exists(_re):
    for _l in open(_re, encoding="utf-8"):
        _q = _l.rstrip().split("|")
        if len(_q) == 2: REAL[_q[0]] = _q[1]

# Nomes que nao correspondem a classe nenhuma do jogo: a galeria AVISA, nao esconde.
DUVIDOSO = set()
_dv = os.path.join(AQUI, "duvidosos.txt")
if os.path.exists(_dv):
    DUVIDOSO = {l.strip() for l in open(_dv, encoding="utf-8") if l.strip()}

BBC = {}
_bbc = os.path.join(AQUI, "nomes-bbc.txt")
if os.path.exists(_bbc):
    for _l in open(_bbc, encoding="utf-8"):
        _q = _l.rstrip().split("|")
        if len(_q) == 2: BBC[_q[0]] = _q[1]
if not USAR_BBC: BBC = {}

CAT = {}
_cat = os.path.join(AQUI, "categorias.txt")
if os.path.exists(_cat):
    for _l in open(_cat, encoding="utf-8"):
        _p = _l.rstrip().split("|")
        if len(_p) == 2: CAT[_p[0]] = _p[1]

cards = "\n".join('<figure data-n="%s" data-solido="%d" data-cat="%s" data-bbc="%s" data-real="%s"><img src="png/%s.png" loading="lazy" alt="">%s%s%s<figcaption>%s</figcaption></figure>'
                  % (html.escape(b.lower()), 1 if b in SOLIDOS else 0,
                     html.escape(CAT.get(b, "Diversos")), html.escape(BBC.get(b, "")),
                     html.escape(REAL.get(b, "")), html.escape(b),
                     '<b class="fundo" title="sem recorte: sai com quadrado na placa, mesmo com nobg">fundo</b>' if (b in SOLIDOS and b not in BBC) else '',
                     '<b class="bbc" title="temos versao recortada no nosso mod">BBC</b>' if b in BBC else '',
                     '<b class="duvida" title="este nome nao corresponde a nenhuma classe do jogo -- pode nao aparecer na placa">?</b>' if b in DUVIDOSO else '',
                     html.escape(b)) for b in nomes)

# cartoes da vista por categoria: icone representativo + nome + contagem
_porcat = {}
for _b in nomes: _porcat.setdefault(CAT.get(_b, "Diversos"), []).append(_b)
_ordem = sorted(_porcat.items(), key=lambda kv: (-len(kv[1]), kv[0]))
_REP = {}
_rp = os.path.join(AQUI, "representantes.txt")
if os.path.exists(_rp):
    for _l in open(_rp, encoding="utf-8"):
        _q = _l.rstrip().split("|")
        if len(_q) == 2: _REP[_q[0]] = _q[1]
def _rep(c, v):
    r = _REP.get(c)
    return r if (r and r in nomes) else sorted(v)[len(v)//2]
catcards = chr(10).join(
    '<button class="catcard" data-cat="%s"><img src="png/%s.png" loading="lazy" alt=""><span class="cnome">%s</span><span class="cqtd">%d</span></button>'
    % (html.escape(c), html.escape(_rep(c, v)), html.escape(c), len(v))
    for c, v in _ordem)

pagina = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Ícones do Eco para placas · BBC-Brasil</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--fundo:#2b2118;--painel:#3a2c20;--escuro:#241b13;--borda:#6b4c2a;--ouro:#e8c47a;--texto:#e9dcc4;--placa:#7a5233;--halo:#d4962b}
html{font-size:17px}
body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:var(--fundo);color:var(--texto);font-size:1rem}
.creditos{background:var(--escuro);padding:12px 22px;font-size:15px;line-height:1.55;border-bottom:1px solid var(--borda)}
.creditos b{color:var(--ouro)}
/* montador */
.montador{background:var(--painel);border-bottom:1px solid var(--borda);padding:18px 22px;display:grid;grid-template-columns:1fr 1fr;gap:16px 32px}
@media (max-width:900px){.montador{grid-template-columns:1fr}}
.montador h2{grid-column:1/-1;margin:0;font-size:19px;color:var(--ouro);letter-spacing:.06em;text-transform:uppercase}
.campo{display:flex;flex-direction:column;gap:8px;font-size:16px}
.campo label{opacity:.85}
textarea,input[type=text],select{background:var(--escuro);color:#f3e6c9;border:1px solid var(--borda);border-radius:6px;padding:10px 12px;font-size:16px;font-family:inherit}
textarea{min-height:80px;resize:vertical}
.linha{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.linha label{display:flex;align-items:center;gap:6px;font-size:15px}
.linha input[type=checkbox]{width:18px;height:18px}
.paleta{display:flex;flex-wrap:wrap;gap:6px}
.cor{width:34px;height:34px;border-radius:6px;border:2px solid transparent;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(0,0,0,.35)}
.cor.sel{border-color:#fff;box-shadow:0 0 0 2px var(--ouro)}
/* a ficha de cada palavra usa o MESMO fundo da placa e a borda na cor da palavra: antes o fundo era
   escuro e a borda marrom fixa, o que fazia cor clara e cor preta parecerem erradas (Raul, 10/09) */
.palavra{background:var(--placa);border:2px solid #4a3220;border-radius:6px;padding:6px 11px;cursor:pointer;font-size:16px;font-weight:600}
.palavra.sel{outline:2px solid var(--ouro)}
.icone-sel{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:var(--escuro);border:1px solid var(--borda);border-radius:6px;padding:8px 12px;min-height:50px;font-size:15px}
.icone-sel img{width:40px;height:40px;background:#c9a56b;border-radius:6px;padding:3px;box-sizing:content-box}
.icone-sel small{opacity:.7}
/* A previa imita a PLACA DO JOGO: tabuas horizontais em madeira quente, moldura
   escura e sombra interna. Nao e enfeite -- a decisao que a previa existe para
   ajudar e a COR do texto sobre a madeira, e julgar isso sobre um retangulo liso
   engana. Cores tiradas dos prints de campo de 09 e 12/09/2026. */
.preview{
  background:
    repeating-linear-gradient(180deg,
      rgba(0,0,0,.13) 0px, rgba(0,0,0,.13) 1px,
      rgba(255,255,255,.045) 2px, rgba(255,255,255,.045) 4px,
      rgba(0,0,0,0) 5px, rgba(0,0,0,0) 38px,
      rgba(0,0,0,.16) 39px, rgba(0,0,0,.16) 40px),
    linear-gradient(180deg,#8a6038,#7a5233 55%,#6d4829);
  border:7px solid #5a3c22; border-radius:6px; padding:24px 22px; min-height:120px;
  font-size:26px; line-height:1.4; color:#3b2a1a;
  font-family:"Trebuchet MS","Segoe UI",Verdana,sans-serif; font-weight:600;
  letter-spacing:.01em; word-break:break-word;
  box-shadow:inset 0 0 34px rgba(0,0,0,.30), inset 0 2px 0 rgba(255,255,255,.06);}
.previa-nota{font-size:12px;opacity:.7;margin-top:7px;line-height:1.45}
.preview img{height:1.2em;vertical-align:-0.25em;margin-right:.15em;border-radius:4px}
.preview img.bg{background:#c9a56b;padding:2px;box-sizing:content-box}
/* HALO DOURADO -- a placa do jogo desenha um halo quente em volta de cada letra. Ele vem do material
   do texto no cliente (TextMeshPro), nao do comando: nao existe tag de contorno. Medido em campo em
   10/09/2026: letra preta ganha halo dourado forte, letra branca ganha halo palido, letra ambar mostra
   um halo fino e mais claro que ela. A forca dele muda com a hora do dia no jogo, entao nao existe cor
   que o esconda por completo. A previa imita isso para nao mentir sobre a cor escolhida. */
.comhalo{text-shadow:0 0 2px var(--halo),1px 0 1px var(--halo),-1px 0 1px var(--halo),0 1px 1px var(--halo),0 -1px 1px var(--halo),1px 1px 1px var(--halo),-1px -1px 1px var(--halo)}
.saida{display:flex;gap:8px;align-items:stretch}
.saida textarea{flex:1;min-height:90px;font-family:Consolas,monospace;font-size:14.5px;line-height:1.4}
button{background:var(--ouro);color:#2b2118;border:0;border-radius:6px;padding:10px 18px;font-weight:700;cursor:pointer;font-size:16px}
button.sec{background:var(--escuro);color:var(--texto);border:1px solid var(--borda)}
button:hover{filter:brightness(1.08)}
#ok{font-size:14px;color:var(--ouro);min-height:16px}
/* galeria */
header{position:sticky;top:0;background:var(--painel);padding:14px 22px;border-bottom:1px solid var(--borda);display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:2}
header h1{font-size:19px;margin:0;color:var(--ouro);letter-spacing:.06em;text-transform:uppercase}
header input{flex:1;min-width:260px;padding:11px 13px;border-radius:6px;border:1px solid var(--borda);background:var(--escuro);color:#f3e6c9;font-size:17px}
header code{background:var(--escuro);padding:6px 10px;border-radius:5px;color:#f3e6c9;font-size:14.5px}
#n{font-size:15px;opacity:.85}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;padding:18px 22px}
figure{margin:0;background:var(--painel);border:1px solid #5a4430;border-radius:8px;padding:14px 8px;text-align:center;cursor:pointer}
figure:hover{background:#4a382a}
figure img{width:64px;height:64px;background:#c9a56b;border-radius:6px;padding:4px;box-sizing:content-box}
figcaption{font-size:15.5px;margin-top:8px;line-height:1.3;overflow-wrap:anywhere;color:var(--texto)}
figure.copiado{outline:2px solid var(--ouro)}
#cats{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px;padding:22px}
.catcard{display:flex;align-items:center;gap:12px;background:var(--painel);border:1px solid #5a4430;
  border-radius:10px;padding:12px 14px;cursor:pointer;text-align:left;color:inherit;font:inherit}
.catcard:hover{background:#4a382a;border-color:var(--ouro)}
.catcard img{width:44px;height:44px;background:#c9a56b;border-radius:6px;padding:3px;flex:none}
.catcard .cnome{flex:1;font-weight:700;font-size:14px}
.catcard .cqtd{font-size:12px;opacity:.75;font-variant-numeric:tabular-nums}
#volta{display:none;align-items:center;gap:10px;padding:14px 22px 0}
#volta button{padding:5px 12px}
#volta b{font-size:15px}
figure{position:relative}
figure .fundo{position:absolute;top:6px;right:6px;background:#8a2f2f;color:#ffe9e9;font-size:10px;
  font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1px 5px;border-radius:3px}
figure[data-solido="1"] img{outline:2px dashed #8a2f2f;outline-offset:-2px}
figure .bbc{position:absolute;top:6px;left:6px;background:#2f6b4f;color:#e7f0ea;font-size:10px;
  font-weight:700;letter-spacing:.04em;padding:1px 5px;border-radius:3px}
/* com os icones BBC ligados, o aviso de "sai com fundo" nao vale: a nossa versao tem alfa */
figure[data-bbc]:not([data-bbc=""]) img{outline:none}
figure .duvida{position:absolute;bottom:34px;right:6px;background:#7a5a12;color:#ffeec2;font-size:11px;
  font-weight:700;padding:0 6px;border-radius:3px}
footer{padding:16px 22px;font-size:14.5px;opacity:.8}
/* DOIS IDIOMAS DENTRO DA PAGINA. Nao ha traducao por arquivo separado de proposito:
   um arquivo so nunca fica com metade traduzida, e a bandeira troca na hora. */
body:not(.en) .en{display:none}
body.en .pt{display:none}
#lingua{display:flex;gap:4px;margin-left:auto}
#lingua button{font-size:19px;line-height:1;padding:3px 8px;background:var(--escuro);
  border:2px solid transparent;border-radius:6px;cursor:pointer}
#lingua button.on{border-color:var(--ouro);background:var(--painel)}
</style></head><body>
<div class="creditos"><span class="pt"><b>Ícones do jogo Eco, © Strange Loop Games.</b> Os ícones dos mods são dos seus autores no mod.io: Market Mod e Gates (bushusuper / EcoPulse), Hot Wheels (zangdar1111 / CavRn), IceCream (Orflash-EcoSim, arte de PookieNoodlin), Mixology 14.0.3 (HolyTiti), StorageMore (Plex_). Imagens extraídas do mod Calculator &amp; Alert Price GP, o GoodPrice (Orflash-EcoSim). Galeria sem fins comerciais, para os jogadores do servidor BBC-Brasil usarem nas placas do jogo.</span>
<span class="en"><b>Eco game icons, © Strange Loop Games.</b> Mod icons belong to their authors on mod.io:
Market Mod and Gates (bushusuper / EcoPulse), Hot Wheels (zangdar1111 / CavRn), IceCream (Orflash-EcoSim,
art by PookieNoodlin), Mixology 14.0.3 (HolyTiti), StorageMore (Plex_). Images extracted from the mod
Calculator &amp; Alert Price GP, aka GoodPrice (Orflash-EcoSim). A non-commercial gallery, for the players
of the BBC-Brasil server to use on in-game signs.</span></div>

<section class="montador">
  <h2><span class="pt">Montar texto da placa</span><span class="en">Build your sign text</span></h2>
  <div class="campo">
    <label for="txt"><span class="pt">1. O que escrever (uma linha por linha da placa; pode deixar vazio para só o ícone)</span><span class="en">1. What to write (one line per sign line; leave empty for icons only)</span></label>
    <textarea id="txt" placeholder="Ex.: Carpintaria&#10;Lenhador"></textarea>
    <label><span class="pt">2. Cor do texto</span><span class="en">2. Text colour</span></label>
    <div class="paleta" id="paleta"></div>
    <div class="linha"><label><span class="pt">Outra cor:</span><span class="en">Other colour:</span> <input type="color" id="corlivre" value="#FFFFFF"></label><span id="corhex" style="font-family:Consolas,monospace;font-size:12.5px">#FFFFFF</span></div>
    <div class="linha"><label><input type="checkbox" id="porpalavra"> <span class="pt">pintar palavra por palavra</span><span class="en">colour word by word</span></label> <small id="dicapalavra" style="opacity:.7;display:none"><span class="pt">clique numa palavra abaixo e depois numa cor da paleta; repita para cada palavra</span><span class="en">click a word below, then a colour; repeat for each word</span></small></div>
    <div id="palavras" class="linha" style="display:none"></div>
    <label><span class="pt">3. Ícones: clique nos ícones da galeria abaixo (pode escolher vários). Em cada um, escolha onde ele fica: antes do texto, depois do texto, ou numa linha só de ícones embaixo; e em qual linha.</span><span class="en">3. Icons: click icons in the gallery below (as many as you like). For each one choose where it goes: before the text, after it, or on a row of icons underneath; and on which line.</span></label>
    <div class="icone-sel" id="iconesel"><small><span class="pt">nenhum ícone escolhido (o texto sai sem ícone)</span><span class="en">no icon chosen (the text comes out without icons)</span></small></div>
    <div class="linha">
      <label><span class="pt">Alinhar</span><span class="en">Align</span> <select id="alinha"><option value="center">centro</option><option value="left">esquerda</option><option value="right">direita</option></select></label>
      <label><span class="pt">Tamanho</span><span class="en">Size</span> <select id="tam"><option value="">normal</option><option value="80">80%</option><option value="125">125%</option><option value="150">150%</option><option value="200">200%</option><option value="300">300%</option></select></label>
      <label><input type="checkbox" id="nobg"> <span class="pt">ícone sem fundo</span><span class="en">icon without background</span></label>
      <label><input type="checkbox" id="negrito"> <span class="pt">negrito</span><span class="en">bold</span></label>
      <label><input type="checkbox" id="italico"> <span class="pt">itálico</span><span class="en">italic</span></label>
      <label><input type="checkbox" id="sublinhado"> <span class="pt">sublinhado</span><span class="en">underline</span></label>
    </div>
    <div class="linha" style="border-top:1px solid var(--borda);padding-top:10px">
      <label><input type="checkbox" id="halo" checked> <span class="pt">prévia com o halo dourado da placa</span><span class="en">preview with the sign's golden halo</span></label>
      <small style="opacity:.85;flex-basis:100%">
<span class="pt">      <b>Três coisas da placa que o comando NÃO controla</b> — todas testadas em placa de verdade em
      10/09/2026, não são suposição:
      <br>1. <b>O halo dourado em volta de cada letra não sai.</b> Ele vem do material do texto dentro do
      jogo, e não existe tag de contorno para ligar, desligar ou pintar — o texto da placa é
      TextMeshPro, que não tem essa tag. A prévia acima desenha o halo justamente para a cor que você
      escolhe aqui ser a cor que vai aparecer na placa.
      <br>2. <b>Não há realce atrás da letra.</b> O <code>&lt;mark&gt;</code> foi colado numa placa e a placa
      ignorou: nenhuma tarja apareceu. Por isso a opção saiu daqui.
      <br>3. <b>Maiúsculas:</b> a placa grande de madeira escreve tudo em maiúscula, e o
      <code>&lt;lowercase&gt;</code> não vence isso. A placa pequena escreve em caixa mista —
      <b>depende do modelo da placa</b>.
      <br><b>O que dá para fazer, então:</b> use <b>cor escura e forte</b> (preto, verde, azul escuro,
      vinho). O halo é claro e quente, então ele contorna a letra escura e ela salta da madeira — é a
      combinação que ficou melhor em todos os testes. Cor clara na madeira clara some.
      A força do halo <b>muda com a hora do dia</b> no jogo, então não existe cor que o esconda por
      completo; a <b>âmbar</b> no fim da paleta é a que mais se aproxima de deixar a palavra lisa.</span><span class="en"><b>Three things about the sign the command does NOT control</b> — all tested on a
      real sign on 10/09/2026, not guesswork:
      <br>1. <b>The golden halo around each letter cannot be removed.</b> It comes from the text material
      inside the game, and there is no outline tag to turn it on, off or recolour — the sign text is
      TextMeshPro, which has no such tag. The preview above draws the halo precisely so that the colour you
      pick here is the colour you will see on the sign.
      <br>2. <b>There is no highlight behind the letter.</b> <code>&lt;mark&gt;</code> was pasted on a real
      sign and the sign ignored it: no band appeared. That is why the option is gone from here.
      <br>3. <b>Uppercase:</b> the large wooden sign writes everything in capitals, and
      <code>&lt;lowercase&gt;</code> does not beat it. The small sign writes mixed case —
      <b>it depends on the sign model</b>.
      <br><b>So what can you do:</b> use a <b>dark, strong colour</b> (black, green, dark blue, wine).
      The halo is light and warm, so it outlines a dark letter and the letter pops off the wood — that was
      the best combination in every test. A light colour on light wood disappears. The halo's strength
      <b>changes with the time of day</b> in game, so no colour hides it completely; the <b>amber</b> at
      the end of the palette comes closest to leaving the word flat.</span></small>
    </div>
  </div>
  <div class="campo">
    <label><span class="pt">Como deve ficar (aproximado)</span><span class="en">How it should look (approximate)</span></label>
    <div class="preview" id="preview"></div>
    <div class="previa-nota"><span class="pt">Aproximação: a madeira, o halo e o tamanho vieram dos prints
      de campo. A <b>fonte</b> é a do navegador, não a do jogo, e a força do halo <b>muda com a hora do
      dia</b>. O que a prévia acerta é <b>cor sobre a madeira</b> e <b>qual ícone sai com quadrado</b>.</span>
      <span class="en">Approximate: the wood, the halo and the size came from in-game screenshots. The
      <b>font</b> is the browser's, not the game's, and the halo's strength <b>changes with the time of
      day</b>. What the preview gets right is <b>colour on wood</b> and <b>which icon comes out with a
      square</b>.</span></div>
    <label><span class="pt">Comando para colar na placa</span><span class="en">Command to paste into the sign</span></label>
    <div class="saida"><textarea id="cmd" readonly></textarea><button id="copiar"><span class="pt">Copiar comando</span><span class="en">Copy command</span></button></div>
    <div id="ok"></div>
    <button class="sec" id="limpar" style="align-self:flex-start"><span class="pt">Limpar</span><span class="en">Clear</span></button>
  </div>
</section>

<header><h1>BBC-Brasil · <span class="pt">Ícones para placa</span><span class="en">Sign icons</span> (__N__)</h1><input id="f" placeholder="filtrar pelo nome (ex.: Store, Market, Sign, Log, Bar)..." autofocus>
<span id="n"></span><label style="font-size:13px"><input type="checkbox" id="porCat" checked> <span class="pt">por categoria</span><span class="en">by category</span></label>
<code><span class="pt">clique no ícone = escolhe para o montador e copia a tag</span><span class="en">click an icon = adds it to the builder and copies the tag</span></code>
<div id="lingua"><button id="lpt" class="on" title="Português">🇧🇷</button><button id="len" title="English">🇺🇸</button></div></header>
<div id="volta"><button class="sec" id="btVolta">&#8592; <span class="pt">todas as categorias</span><span class="en">all categories</span></button><b id="catAtual"></b></div>
<div id="cats">__CATCARDS__</div>
<main id="g">__CARDS__</main>
<footer><span class="pt">Tags do próprio jogo: &lt;align&gt;, &lt;color&gt;, &lt;size&gt;, &lt;b&gt; e &lt;icon&gt; (com fundo ou <code>type="nobg"</code>). O ícone funciona em qualquer placa com texto, inclusive em veículos.<br>
Os <b style="background:#8a2f2f;color:#ffe9e9;padding:1px 5px;border-radius:3px;font-size:10px">FUNDO</b> são __S__ ícones cuja arte não tem recorte: saem com quadrado na placa <b>mesmo com <code>type="nobg"</code></b> — medido em campo em 12/09/2026. A saída não é escondê-los, é <b>corrigi-los</b>: os que já têm versão nossa aparecem com a etiqueta BBC. <b>64 deles são do jogo base</b> (lixo, sucata, filtros, upgrades) e 123 de mods — então não é
problema de um mod só. Os que temos versão recortada aparecem com a etiqueta
<b style="background:#2f6b4f;color:#e7f0ea;padding:1px 5px;border-radius:3px;font-size:10px">BBC</b>:
com a caixa <b>ícones BBC</b> ligada, a placa sai com o nome do nosso mod.<br>
O <b style="background:#7a5a12;color:#ffeec2;padding:0 6px;border-radius:3px;font-size:11px">?</b> marca
__D__ nomes que <b>não correspondem a nenhuma classe do jogo</b> (quase todos <code>*Group</code>, que são
agrupamentos do GoodPrice): podem não aparecer na placa. E __R__ ícones de profissão saíam com um
<code>Item</code> no fim que não existe — agora saem certos (<code>TailoringSkill</code>, não
<code>TailoringSkillItem</code>).<br>
Também do binário, ainda pouco usados: <code>iconcolor='RRGGBBAA'</code> (tinge o ícone, com canal alfa) e <code>overlayimg='X' overlaycolor='RRGGBBAA'</code>. Aspas <b>simples</b> nesses dois.</span>
<span class="en">Tags from the game itself: &lt;align&gt;, &lt;color&gt;, &lt;size&gt;, &lt;b&gt; and &lt;icon&gt;
(with background or <code>type="nobg"</code>). Icons work on any sign with text, vehicles included.<br>
The <b style="background:#8a2f2f;color:#ffe9e9;padding:1px 5px;border-radius:3px;font-size:10px">FUNDO</b>
badge marks __S__ icons whose artwork has no cut-out: they come out with a square on the sign
<b>even with <code>type="nobg"</code></b> — measured in game on 12/09/2026. <b>64 of them are from the
base game</b> (garbage, scrap, filters, upgrades) and 123 from mods, so it is not one mod's fault.
Icons we have re-cut show the
<b style="background:#2f6b4f;color:#e7f0ea;padding:1px 5px;border-radius:3px;font-size:10px">BBC</b>
badge: the sign command then uses our mod's name.<br>
The <b style="background:#7a5a12;color:#ffeec2;padding:0 6px;border-radius:3px;font-size:11px">?</b>
badge marks __D__ names that <b>match no class in the game</b> (nearly all <code>*Group</code>, which are
GoodPrice groupings): they may not show up. And __R__ profession icons used to come out with an
<code>Item</code> suffix that does not exist — they are correct now (<code>TailoringSkill</code>, not
<code>TailoringSkillItem</code>).<br>
Also from the binary, still little used: <code>iconcolor='RRGGBBAA'</code> (tints the icon, with an alpha
channel) and <code>overlayimg='X' overlaycolor='RRGGBBAA'</code>. <b>Single</b> quotes on those two.</span></footer>
<script>
const PALETA=[["#FFFFFF","branco"],["#000000","preto"],["#FFDF00","amarelo"],["#009C3B","verde"],["#00BFFF","azul claro"],["#1E3A8A","azul escuro"],["#FFA500","laranja"],["#E53935","vermelho"],["#FF69B4","rosa"],["#8E44AD","roxo"],["#8B4513","marrom"],["#BDBDBD","cinza"],["#D4AF37","dourado"],["#00E5A0","verde água"],["#D98C00","âmbar: o mais perto de liso"]];
const $=id=>document.getElementById(id);
let cor="#FFFFFF", icones=[];
const pal=$('paleta');
// cor por palavra: chave "linha:palavra" -> #HEX ; palavraSel = chave da palavra escolhida para receber a proxima cor
let coresPalavra={}, palavraSel=null;
function aplicaCor(hex){ if($('porpalavra').checked && palavraSel!==null){coresPalavra[palavraSel]=hex; palavras();} else {cor=hex;$('corlivre').value=hex;marca();} monta(); }
for(const [hex,nome] of PALETA){const d=document.createElement('div');d.className='cor';d.style.background=hex;d.title=nome+' '+hex;d.dataset.hex=hex;d.onclick=()=>aplicaCor(hex);pal.appendChild(d);}
function marca(){$('corhex').textContent=cor.toUpperCase();[...pal.children].forEach(c=>c.classList.toggle('sel',c.dataset.hex.toUpperCase()===cor.toUpperCase()));}
$('corlivre').oninput=e=>aplicaCor(e.target.value.toUpperCase());
function palavras(){ const box=$('palavras'); const on=$('porpalavra').checked; box.style.display=on?'':'none'; $('dicapalavra').style.display=on?'':'none'; if(!on) return;
  box.innerHTML=''; $('txt').value.split('\\n').forEach((l,li)=>{ l.split(/(\\s+)/).forEach((w,wi)=>{ if(!w.trim()) return; const k=li+':'+wi; const s=document.createElement('span'); s.className='palavra'+(palavraSel===k?' sel':'')+($('halo').checked?' comhalo':''); s.textContent=w; const cw=coresPalavra[k]||cor; s.style.color=cw; s.style.borderColor=cw; s.onclick=()=>{palavraSel=k;palavras();}; box.appendChild(s); }); const br=document.createElement('span'); br.style.flexBasis='100%'; box.appendChild(br); });
  const lim=document.createElement('button'); lim.className='sec'; lim.style.padding='3px 8px'; lim.textContent='limpar cores das palavras'; lim.onclick=()=>{coresPalavra={};palavraSel=null;palavras();monta();}; box.appendChild(lim); }
$('porpalavra').addEventListener('change',()=>{palavras();monta();});
function pinta(l,li){ if(!$('porpalavra').checked) return l; return l.split(/(\\s+)/).map((w,wi)=>{const c=coresPalavra[li+':'+wi]; return (w.trim()&&c)?`<color=${c}>${w}</color>`:w;}).join(''); }
function pintaHtml(l,li){ if(!$('porpalavra').checked) return esc(l); return l.split(/(\\s+)/).map((w,wi)=>{const c=coresPalavra[li+':'+wi]; return (w.trim()&&c)?`<span style="color:${c}">${esc(w)}</span>`:esc(w);}).join(''); }
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function monta(){
  const linhas=$('txt').value.split('\\n'); const nobg=$('nobg').checked?' type="nobg"':' type=""';
  const tam=$('tam').value, ali=$('alinha').value;
  const neg=$('negrito').checked, ita=$('italico').checked, sub=$('sublinhado').checked;
  const vazio=n=>`<icon name="${nomePara(n)}"${nobg}></icon>`;
  // icones ANTES: o ultimo deles abre a tag e o texto vai dentro (forma provada em placa); os outros ficam vazios
  const antes=(lista,t)=>lista.length?lista.slice(0,-1).map(vazio).join('')+`<icon name="${nomePara(lista[lista.length-1])}"${nobg}>${t}</icon>`:t;
  const L=linhas.map((l,i)=>pinta(l,i));
  const porLinha=L.map((t,i)=>antes(icones.filter(o=>o.pos==='antes'&&o.linha===i+1).map(o=>o.n),t)+icones.filter(o=>o.pos==='depois'&&o.linha===i+1).map(o=>vazio(o.n)).join(''));
  const abaixo=icones.filter(o=>o.pos==='abaixo').map(o=>vazio(o.n)).join('');
  let corpo=porLinha.join('\\n')+(abaixo?'\\n'+abaixo:'');
  if(neg) corpo='<b>'+corpo+'</b>';
  if(ita) corpo='<i>'+corpo+'</i>';
  if(sub) corpo='<u>'+corpo+'</u>';
  if(tam) corpo=`<size=${tam}%>`+corpo+'</size>';
  corpo=`<color=${cor}>`+corpo+'</color>';
  // NAO existe realce: <mark=#000000BF> foi testado em placa em 10/09/2026 e a placa ignorou --
  // nenhuma tarja atras das letras. A tag esta no binario, mas o material do texto da placa nao a
  // desenha. Nao reintroduzir sem novo teste em campo.
  corpo=`<align="${ali}">`+corpo+'</align>';
  $('cmd').value=corpo;
  // preview
  const cls=$('nobg').checked?'':'bg';
  // Com "icones BBC" ligado, a previa desenha a versao RECORTADA -- senao ela mostraria
  // o quadrado que o nosso mod justamente tira, e mentiria sobre o resultado na placa.
  const src=n=>BBC[n] ? `png-bbc/${n}.png` : `png/${n}.png`;
  const imgs=(lista)=>lista.map(n=>`<img src="${src(n)}" class="${BBC[n]?'':cls}" alt="">`).join('');
  const H=linhas.map((l,i)=>pintaHtml(l,i));
  const pvLinhas=H.map((t,i)=>imgs(icones.filter(o=>o.pos==='antes'&&o.linha===i+1).map(o=>o.n))+t+imgs(icones.filter(o=>o.pos==='depois'&&o.linha===i+1).map(o=>o.n)));
  const pvAbaixo=imgs(icones.filter(o=>o.pos==='abaixo').map(o=>o.n));
  const pv=pvLinhas.join('<br>')+(pvAbaixo?'<br>'+pvAbaixo:'');
  const p=$('preview'); p.innerHTML=pv||'&nbsp;'; p.style.textAlign=ali; p.style.color=cor; p.style.fontWeight=neg?'700':'400';
  p.classList.toggle('comhalo',$('halo').checked);
  p.style.fontStyle=ita?'italic':'normal'; p.style.textDecoration=sub?'underline':'none'; p.style.fontSize=(tam?22*tam/100:22)+'px';
}
['txt','alinha','tam','nobg','negrito','italico','sublinhado','halo'].forEach(id=>{$(id).addEventListener('input',monta);$(id).addEventListener('change',monta);});
$('halo').addEventListener('change',palavras);   // as fichas de palavra tambem ganham/perdem o halo
$('txt').addEventListener('input',()=>{palavras();mostraIcones();});
/* COPIAR -- por que nao e so navigator.clipboard: essa API so existe em pagina SEGURA (https ou
   localhost). Dentro do painel do servidor a pagina e http://ENDERECO-DO-SERVIDOR:27041/placas/, entao
   navigator.clipboard vem UNDEFINED, a linha estourava e o botao nao fazia nada nem avisava
   (defeito relatado pelo Raul em 10/09). Agora: tenta a API, cai para o execCommand antigo, que
   funciona em http, e se nem isso der, seleciona o texto e pede Ctrl+C. Sempre avisa. */
function copia(t,msg){
  const aviso=m=>{ if($('ok')) $('ok').textContent=m; };
  /* O plano B copia de um campo VISIVEL (o Chrome recusa copiar de elemento fora da tela). Fica
     dentro da janela, com 2em e opacidade 0, que e a forma que funciona em http. */
  const antigo=()=>{ const ta=document.createElement('textarea'); ta.value=t;
    ta.style.cssText='position:fixed;left:0;top:0;width:2em;height:2em;padding:0;border:none;outline:none;box-shadow:none;background:transparent;opacity:0';
    document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0,t.length);
    let ok=false; try{ ok=document.execCommand('copy'); }catch(e){ ok=false; }
    document.body.removeChild(ta); return ok; };
  try{
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(()=>aviso(msg)).catch(()=>{
        aviso(antigo()?msg:'nao consegui copiar sozinho; o texto esta selecionado, aperte Ctrl+C');
        if(!navigator.clipboard) return; });
      return;
    }
  }catch(e){}
  if(antigo()) aviso(msg);
  else { const c=$('cmd'); if(c){ c.focus(); c.select(); } aviso('nao consegui copiar sozinho; o texto esta selecionado, aperte Ctrl+C'); }
}
$('copiar').onclick=()=>copia($('cmd').value,'comando copiado; cole no texto da placa (tecla E na placa).');
function mostraIcones(){const s=$('iconesel'); if(!icones.length){s.innerHTML='<small>'+(document.body.classList.contains('en')?'no icon chosen (the text comes out without icons)':'nenhum ícone escolhido (o texto sai sem ícone)')+'</small>';return;}
  const nl=Math.max(1,$('txt').value.split('\\n').length); icones.forEach(o=>{if(o.linha>nl)o.linha=nl;});
  const optL=(o)=>Array.from({length:nl},(_,k)=>`<option value="${k+1}"${o.linha===k+1?' selected':''}>linha ${k+1}</option>`).join('');
  s.innerHTML=icones.map((o,i)=>`<span style="display:inline-flex;align-items:center;gap:6px;background:#3a2c20;border:1px solid #6b4c2a;border-radius:6px;padding:3px 6px"><img src="png/${o.n}.png" alt=""><span>${o.n}</span>
    <select data-pos="${i}" style="padding:3px 6px"><option value="antes"${o.pos==='antes'?' selected':''}>antes do texto</option><option value="depois"${o.pos==='depois'?' selected':''}>depois do texto</option><option value="abaixo"${o.pos==='abaixo'?' selected':''}>linha de ícones embaixo</option></select>
    <select data-lin="${i}" style="padding:3px 6px"${o.pos==='abaixo'?' disabled':''}>${optL(o)}</select>
    <button class="sec" data-i="${i}" style="padding:2px 7px">x</button></span>`).join(' ')
    +` <button class="sec" id="tiratodos" style="padding:3px 8px">tirar todos</button>`;
  s.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{icones.splice(+b.dataset.i,1);mostraIcones();monta();});
  s.querySelectorAll('select[data-pos]').forEach(x=>x.onchange=()=>{icones[+x.dataset.pos].pos=x.value;mostraIcones();monta();});
  s.querySelectorAll('select[data-lin]').forEach(x=>x.onchange=()=>{icones[+x.dataset.lin].linha=+x.value;monta();});
  $('tiratodos').onclick=()=>{icones=[];mostraIcones();monta();};}
$('limpar').onclick=()=>{$('txt').value='';icones=[];coresPalavra={};palavraSel=null;palavras();mostraIcones();monta();};
function escolhe(nome){icones.push({n:nome,pos:'antes',linha:1});mostraIcones();monta();}
const g=$('g'), f=$('f'), n=$('n'); const figs=[...g.children];
const BBC=__BBCJSON__;
// IDIOMA. Os textos visiveis existem nos DOIS idiomas dentro da pagina (classes .pt/.en),
// e o CSS esconde um. Aqui ficam so os que sao ATRIBUTO, que o CSS nao alcanca.
// Por que dois idiomas no mesmo arquivo, e nao um arquivo por lingua: arquivo separado
// envelhece pela metade -- um dos dois acaba desatualizado sem ninguem notar.
const ATTR = {
  txt: ["Ex.: Carpintaria\\nLenhador", "e.g. Carpentry\\nLumberjack"],
  f:   ["filtrar pelo nome (ex.: Store, Market, Sign, Log, Bar)...",
        "filter by name (e.g. Store, Market, Sign, Log, Bar)..."]
};
const OPC = { alinha: [["centro","esquerda","direita"], ["center","left","right"]] };
function lingua(x){
  const en = (x === "en");
  document.body.classList.toggle("en", en);
  const i = en ? 1 : 0;
  for (const id in ATTR){ const el = document.getElementById(id); if (el) el.placeholder = ATTR[id][i]; }
  for (const id in OPC){ const el = document.getElementById(id); if (!el) continue;
    OPC[id][i].forEach((txt,k) => { if (el.options[k]) el.options[k].textContent = txt; }); }
  document.getElementById("lpt").classList.toggle("on", !en);
  document.getElementById("len").classList.toggle("on", en);
  document.documentElement.lang = en ? "en" : "pt-BR";
  try { localStorage.setItem("bbc-lingua", x); } catch(e){}
  if (typeof mostraIcones === "function") mostraIcones();
}
let catAberta=null;
// Nome que vai para a placa: o do nosso mod quando existir e a caixa estiver ligada.
// Ordem: icone do nosso mod > nome corrigido (sem o 'Item' que nao existe) > o do arquivo.
function nomeReal(fig){ return fig.dataset.bbc || fig.dataset.real || fig.querySelector('figcaption').textContent; }
function nomePara(n){ const fig=figs.find(x=>x.querySelector('figcaption').textContent===n); return fig?nomeReal(fig):n; }
function filtra(){const q=f.value.toLowerCase().trim();
  const modo=$('porCat').checked; const cats=$('cats'), volta=$('volta');
  // busca por texto sempre vence: mostra a grade inteira
  const vendoCats = modo && !q && !catAberta;
  cats.style.display = vendoCats ? 'grid' : 'none';
  g.style.display    = vendoCats ? 'none' : 'grid';
  volta.style.display= (modo && !q && catAberta) ? 'flex' : 'none';
  $('catAtual').textContent = catAberta || '';
  if(vendoCats){ n.textContent = cats.children.length+' categorias'; return; }
  let c=0;
  for(const el of figs){
    const ok=(!q||el.dataset.n.includes(q))
           &&(!modo||q||!catAberta||el.dataset.cat===catAberta);
    el.style.display=ok?'':'none'; if(ok)c++;}
  n.textContent=c+' de '+figs.length;}
$('cats').onclick=e=>{const b=e.target.closest('.catcard'); if(!b)return;
  catAberta=b.dataset.cat; filtra(); window.scrollTo({top:document.querySelector('header').offsetTop,behavior:'smooth'});};
$('btVolta').onclick=()=>{catAberta=null; filtra();};
$('porCat').onchange=()=>{catAberta=null; filtra();};
document.getElementById("lpt").onclick = () => lingua("pt");
document.getElementById("len").onclick = () => lingua("en");
let _lg = "pt";
try { _lg = localStorage.getItem("bbc-lingua")
      || ((navigator.language||"").toLowerCase().startsWith("pt") ? "pt" : "en"); } catch(e){}
lingua(_lg);
f.oninput=filtra; filtra(); trocaImagens(); marca(); monta();
function trocaImagens(){
  for(const el of figs){ const n=el.querySelector('figcaption').textContent;
    if(BBC[n]) el.querySelector('img').src='png-bbc/'+n+'.png'; } }
g.onclick=e=>{const fig=e.target.closest('figure'); if(!fig)return; const nome=fig.querySelector('figcaption').textContent;
  const real=nomeReal(fig); const tag='<icon name="'+real+'"'+($('nobg').checked?' type="nobg"':' type=""')+'></icon>'; copia(tag,'ícone copiado: '+tag);
  figs.forEach(x=>x.classList.remove('copiado')); fig.classList.add('copiado'); n.textContent='copiado: '+tag; escolhe(nome); window.scrollTo({top:0,behavior:'smooth'});};
</script></body></html>""".replace("__N__", str(len(nomes))).replace("__S__", str(len(SOLIDOS))).replace("__CATCARDS__", catcards).replace("__D__", str(len(DUVIDOSO))).replace("__R__", str(len(REAL))).replace("__BBCJSON__", __import__("json").dumps(BBC, ensure_ascii=False)).replace("__CARDS__", cards)
with open(os.path.join(AQUI, "icones.html"), "w", encoding="utf-8") as fh:
    fh.write(pagina)
print("icones.html com", len(nomes), "icones + montador")
