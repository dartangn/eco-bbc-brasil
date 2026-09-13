# -*- coding: utf-8 -*-
"""PENDENTE do reinicio diario: instala os icones recortados da Mixologia.

RODA COM O SERVIDOR PARADO, que e o que asset de cliente precisa -- trocar com
gente conectada deixaria metade dos jogadores com cada versao.

INSTALA OS DOIS CAMINHOS, de proposito:
  1. MOD NOSSO (IconesMixologiaBBC.unity3d) -- 71 prefabs renomeados para <Nome>BBC.
     E ADITIVO: nao toca no mod do autor. Se o cliente nao souber achar prefab em
     bundle de outro mod, ele simplesmente nao aparece e nada quebra.
     >>> E ELE que o teste de amanha responde: <icon name="PinaColadaItemBBC" type="nobg">
  2. SUBSTITUICAO do MixologyMod.unity3d -- garante que os icones fiquem certos
     mesmo se o caminho 1 falhar. Com backup datado.

POR QUE NAO SE ANOTA EM instalados-neste-reinicio.txt
  Aquela lista existe para desfazer .cs que nao compila. Isto aqui e ASSET: nao passa
  pelo compilador, entao nao pode causar 'error CS'. Se eu anotasse, um erro de
  compilacao de OUTRA coisa removeria estes arquivos sem motivo.

DESFAZER
  bash ~/instalar-mod-icones-bbc.sh --desfazer     (mod nosso)
  bash ~/instalar-icones-mixologia.sh --desfazer   (volta o bundle do autor)
"""
import hashlib, os, shutil, sys, datetime

PAYLOAD = "/opt/eco/pendentes/payload"
MOD_BBC_SRC = os.path.join(PAYLOAD, "IconesMixologiaBBC.unity3d")
MIX_SRC     = os.path.join(PAYLOAD, "MixologyMod.unity3d.novo")
MOD_BBC_DIR = "/opt/eco/server/Mods/UserCode/KabongBrasil/IconesBBC"
MOD_BBC_DST = os.path.join(MOD_BBC_DIR, "IconesMixologiaBBC.unity3d")
MIX_DST     = "/opt/eco/server/Mods/UserCode/Mixology 14.0.3/Mixology/Unity/MixologyMod.unity3d"
BKDIR       = "/opt/eco/backups"

MD5_BBC = "270ed583507f6c347ec2b82838b56102"
MD5_MIX = "b0cf7c1326caafd2dd70288789665a33"
MD5_MIX_ORIGINAL = "1b549c38fb591411e96b7bb331a399d1"

# galeria de placas no painel web
GAL_SRC = os.path.join(PAYLOAD, "placas-web")
GAL_MESTRE = "/opt/eco/placas-web"
GAL_WEB = "/opt/eco/server/WebClient/WebBin/placas"   # caminho real, conferido em 12/09

def md5(c):
    h = hashlib.md5()
    with open(c, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def erro(m):
    print("[XX] " + m)
    sys.exit(1)

ENSAIO = "--ensaio" in sys.argv   # confere tudo e NAO escreve nada

quando = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
feito = []

def copiar(a, b):
    if ENSAIO:
        print("   (ensaio) copiaria %s -> %s" % (os.path.basename(a), b)); return
    shutil.copy2(a, b)

# ---------------------------------------------------------------- 1. mod nosso
if not os.path.exists(MOD_BBC_SRC): erro("nao achei " + MOD_BBC_SRC)
if md5(MOD_BBC_SRC) != MD5_BBC: erro("md5 do mod BBC nao confere (esperado %s)" % MD5_BBC)
if not ENSAIO: os.makedirs(MOD_BBC_DIR, exist_ok=True)
copiar(MOD_BBC_SRC, MOD_BBC_DST)
if not ENSAIO and md5(MOD_BBC_DST) != MD5_BBC: erro("md5 nao bateu depois de copiar o mod BBC")
feito.append("mod BBC em %s" % MOD_BBC_DST)

# ---------------------------------------------------- 2. substituicao (plano B)
if not os.path.exists(MIX_SRC): erro("nao achei " + MIX_SRC)
if md5(MIX_SRC) != MD5_MIX: erro("md5 do pacote recortado nao confere")
if not os.path.exists(MIX_DST):
    print("   [..] Mixologia nao instalada; pulei a substituicao")
else:
    atual = md5(MIX_DST)
    if atual == MD5_MIX:
        print("   [..] o bundle da Mixologia ja e o nosso; nada a fazer")
    else:
        if atual != MD5_MIX_ORIGINAL:
            print("   [!!] o bundle atual NAO e o original conhecido (%s)." % atual)
            print("        A Mixologia pode ter sido atualizada -- faco backup e sigo.")
        if not ENSAIO: os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "MixologyMod.unity3d.original-%s" % quando)
        copiar(MIX_DST, bk)
        copiar(MIX_SRC, MIX_DST)
        if not ENSAIO and md5(MIX_DST) != MD5_MIX:
            shutil.copy2(bk, MIX_DST)
            erro("md5 nao bateu depois da troca; voltei o original")
        feito.append("bundle da Mixologia trocado (backup em %s)" % bk)

# ------------------------------------------------- 3. galeria de placas no painel
if os.path.isdir(GAL_SRC):
    destino_bbc = os.path.join(GAL_MESTRE, "png-bbc")
    n = len(os.listdir(os.path.join(GAL_SRC, "png-bbc")))
    if not ENSAIO:
        os.makedirs(GAL_MESTRE, exist_ok=True)
        shutil.copy2(os.path.join(GAL_SRC, "index.html"), os.path.join(GAL_MESTRE, "index.html"))
        if os.path.isdir(destino_bbc): shutil.rmtree(destino_bbc)
        shutil.copytree(os.path.join(GAL_SRC, "png-bbc"), destino_bbc)
    feito.append("galeria: index.html + %d icones recortados na copia-mestra" % n)
    # republica no painel, se a pasta do painel existir
    # republica a copia-mestra inteira no painel, igual ao instalar-placas-web.sh
    if os.path.isdir(os.path.dirname(GAL_WEB)):
        if not ENSAIO:
            if os.path.isdir(GAL_WEB): shutil.rmtree(GAL_WEB)
            shutil.copytree(GAL_MESTRE, GAL_WEB)
        feito.append("galeria republicada em %s" % GAL_WEB)
    else:
        print("   [..] %s nao existe; a copia-mestra ficou pronta." % os.path.dirname(GAL_WEB))
else:
    print("   [..] sem payload de galeria; pulei")

for f in feito: print("   " + f)
if ENSAIO:
    print("[ensaio] tudo conferido; NADA foi escrito. Tire o --ensaio para valer.")
else:
    print("[ok] icones da Mixologia instalados (%d passos)" % len(feito))
