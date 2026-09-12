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

cards = "\n".join('<figure data-n="%s"><img src="png/%s.png" loading="lazy" alt=""><figcaption>%s</figcaption></figure>'
                  % (html.escape(b.lower()), html.escape(b), html.escape(b)) for b in nomes)

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
.preview{background:var(--placa);border:6px solid #4a3220;border-radius:8px;padding:22px;min-height:110px;font-size:26px;line-height:1.35;color:#3b2a1a;font-family:Georgia,serif;word-break:break-word;box-shadow:inset 0 0 30px rgba(0,0,0,.25)}
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
footer{padding:16px 22px;font-size:14.5px;opacity:.8}
</style></head><body>
<div class="creditos"><b>Ícones do jogo Eco, © Strange Loop Games.</b> Os ícones dos mods são dos seus autores no mod.io: Market Mod e Gates (bushusuper / EcoPulse), Hot Wheels (zangdar1111 / CavRn), IceCream (Orflash-EcoSim, arte de PookieNoodlin), Mixology 14.0.3 (HolyTiti), StorageMore (Plex_). Imagens extraídas do mod Calculator &amp; Alert Price GP, o GoodPrice (Orflash-EcoSim). Galeria sem fins comerciais, para os jogadores do servidor BBC-Brasil usarem nas placas do jogo.</div>

<section class="montador">
  <h2>Montar texto da placa</h2>
  <div class="campo">
    <label for="txt">1. O que escrever (uma linha por linha da placa; pode deixar vazio para só o ícone)</label>
    <textarea id="txt" placeholder="Ex.: Carpintaria&#10;Lenhador"></textarea>
    <label>2. Cor do texto</label>
    <div class="paleta" id="paleta"></div>
    <div class="linha"><label>Outra cor: <input type="color" id="corlivre" value="#FFFFFF"></label><span id="corhex" style="font-family:Consolas,monospace;font-size:12.5px">#FFFFFF</span></div>
    <div class="linha"><label><input type="checkbox" id="porpalavra"> pintar palavra por palavra</label> <small id="dicapalavra" style="opacity:.7;display:none">clique numa palavra abaixo e depois numa cor da paleta; repita para cada palavra</small></div>
    <div id="palavras" class="linha" style="display:none"></div>
    <label>3. Ícones: clique nos ícones da galeria abaixo (pode escolher vários). Em cada um, escolha onde ele fica: antes do texto, depois do texto, ou numa linha só de ícones embaixo; e em qual linha.</label>
    <div class="icone-sel" id="iconesel"><small>nenhum ícone escolhido (o texto sai sem ícone)</small></div>
    <div class="linha">
      <label>Alinhar <select id="alinha"><option value="center">centro</option><option value="left">esquerda</option><option value="right">direita</option></select></label>
      <label>Tamanho <select id="tam"><option value="">normal</option><option value="80">80%</option><option value="125">125%</option><option value="150">150%</option><option value="200">200%</option><option value="300">300%</option></select></label>
      <label><input type="checkbox" id="nobg"> ícone sem fundo</label>
      <label><input type="checkbox" id="negrito"> negrito</label>
      <label><input type="checkbox" id="italico"> itálico</label>
      <label><input type="checkbox" id="sublinhado"> sublinhado</label>
    </div>
    <div class="linha" style="border-top:1px solid var(--borda);padding-top:10px">
      <label><input type="checkbox" id="halo" checked> prévia com o halo dourado da placa</label>
      <small style="opacity:.85;flex-basis:100%">
      <b>Três coisas da placa que o comando NÃO controla</b> — todas testadas em placa de verdade em
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
      completo; a <b>âmbar</b> no fim da paleta é a que mais se aproxima de deixar a palavra lisa.</small>
    </div>
  </div>
  <div class="campo">
    <label>Como deve ficar (aproximado)</label>
    <div class="preview" id="preview"></div>
    <label>Comando para colar na placa</label>
    <div class="saida"><textarea id="cmd" readonly></textarea><button id="copiar">Copiar comando</button></div>
    <div id="ok"></div>
    <button class="sec" id="limpar" style="align-self:flex-start">Limpar</button>
  </div>
</section>

<header><h1>BBC-Brasil · Ícones para placa (__N__)</h1><input id="f" placeholder="filtrar pelo nome (ex.: Store, Market, Sign, Log, Bar)..." autofocus>
<span id="n"></span><code>clique no ícone = escolhe para o montador e copia &lt;icon name="Nome" type=""&gt;&lt;/icon&gt;</code></header>
<main id="g">__CARDS__</main>
<footer>Tags do próprio jogo: &lt;align&gt;, &lt;color&gt;, &lt;size&gt;, &lt;b&gt; e &lt;icon&gt; (com fundo ou <code>type="nobg"</code>). O ícone funciona em qualquer placa com texto, inclusive em veículos.</footer>
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
  const vazio=n=>`<icon name="${n}"${nobg}></icon>`;
  // icones ANTES: o ultimo deles abre a tag e o texto vai dentro (forma provada em placa); os outros ficam vazios
  const antes=(lista,t)=>lista.length?lista.slice(0,-1).map(vazio).join('')+`<icon name="${lista[lista.length-1]}"${nobg}>${t}</icon>`:t;
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
  const imgs=(lista)=>lista.map(n=>`<img src="png/${n}.png" class="${cls}" alt="">`).join('');
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
function mostraIcones(){const s=$('iconesel'); if(!icones.length){s.innerHTML='<small>nenhum ícone escolhido (o texto sai sem ícone)</small>';return;}
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
function filtra(){const q=f.value.toLowerCase().trim(); let c=0; for(const el of figs){const ok=!q||el.dataset.n.includes(q); el.style.display=ok?'':'none'; if(ok)c++;} n.textContent=c+' de '+figs.length;}
f.oninput=filtra; filtra(); marca(); monta();
g.onclick=e=>{const fig=e.target.closest('figure'); if(!fig)return; const nome=fig.querySelector('figcaption').textContent;
  const tag='<icon name="'+nome+'" type=""></icon>'; copia(tag,'ícone copiado: '+tag);
  figs.forEach(x=>x.classList.remove('copiado')); fig.classList.add('copiado'); n.textContent='copiado: '+tag; escolhe(nome); window.scrollTo({top:0,behavior:'smooth'});};
</script></body></html>""".replace("__N__", str(len(nomes))).replace("__CARDS__", cards)
with open(os.path.join(AQUI, "icones.html"), "w", encoding="utf-8") as fh:
    fh.write(pagina)
print("icones.html com", len(nomes), "icones + montador")
