#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
configurar.py -- escreve os .eco do servidor Eco a partir dos .template.

    RODAR ASSIM (como ecosrv, para os arquivos nascerem com o dono certo):
        sudo -u ecosrv python3 /opt/eco/scripts/configurar.py
        sudo -u ecosrv python3 /opt/eco/scripts/configurar.py --seco   # nao grava

POR QUE ANTES DO PRIMEIRO ARRANQUE
    O WorldGenerator.eco EXIGE WIPE para mudar. Subindo primeiro, o Eco geraria um
    mundo padrao e teriamos de gerar de novo -- cada geracao leva ~8 min neste
    hardware. Configurando antes, o mundo nasce com 4 km2 de primeira.

POR QUE PYTHON E NAO sed
    Os .eco sao JSON, e alguns campos sao ANINHADOS. No Windows, ler
    Difficulty.eco pelo primeiro nivel devolvia VAZIO -- falha silenciosa que
    gerou tres falsos alarmes de "o servidor reescreveu a config". Aqui os
    caminhos sao explicitos e o script CONFERE lendo de volta.

FONTE DOS VALORES
    RECONSTRUIR.md secao 4, que e a tabela do servidor Windows antigo.
    O WorldGenerator vem do EcoAtlas (wg.json), o mesmo mapa de antes:
    ecoatlas.dev/2000/2052209397/Balanced%20Water
"""

import base64
import json
import os
import shutil
import sys

RAIZ = "/opt/eco/server"
CFG = os.path.join(RAIZ, "Configs")
WG_ORIGEM = "/opt/eco/scripts/wg.json"
SECO = "--seco" in sys.argv

# ---------------------------------------------------------------- valores

# ASCII puro nas tags de cor, entao nao precisa de truque. O nome antigo tinha
# "Sao" com acento e precisava de base64; este nao.
NOME = ("<color=#009C3B>BBC-BRASIL</color> <color=#FFDF00>5X</color>, "
        "<color=#00BFFF>PT-BR</color>, <color=#FFFFFF>MODS</color>, "
        "<color=#FFA500>METEORO 60 DIAS</color>")

# A descricao tem acento. Embutida em base64 para este arquivo ficar ASCII puro --
# mesma tecnica que usamos no Windows, onde .ps1 com acento corrompia.
DESC_B64 = (
    "U2Vydmlkb3IgYnJhc2lsZWlybyAoUFQtQlIpLCBhYmVydG8gZSBzZW0gc2VuaGEuCgpNdW5kbyBy"
    "ZWPDqW0tY3JpYWRvIOKAlCBkw6EgcGFyYSBlbnRyYXIgbmEgZWNvbm9taWEgZGVzZGUgbyBwcmlt"
    "ZWlybyBkaWEsIHNlbSBjaGVnYXIgYXRyYXNhZG8uCgpGb2NvIGVtIGNvbGFib3Jhw6fDo28sIGNv"
    "bnN0cnXDp8OjbyBkZSBsb25nbyBwcmF6byBlIGNsaW1hIHRyYW5xdWlsby4gVmFnYXMgbGl2cmVz"
    "LgoKVG9kb3Mgc8OjbyBiZW0tdmluZG9zIQ=="
)
DESC = base64.b64decode(DESC_B64).decode("utf-8")

# Os Steam64 dos admins do SEU servidor -- 17 digitos, comecando com 7656119.
# Vazio de proposito: este repositorio e publico. Sem ninguem aqui, o Users.eco nasce
# sem admin, e o /manage admin do chat NAO resolve (ele exige que quem digita ja seja
# admin). O primeiro admin tem de entrar pelo arquivo.
ADMINS = [
]

# O endereco PUBLICO do seu servidor, e as portas que ele usa.
#
# HOST_PUBLICO alimenta RemoteAddress e WebServerUrl. PROVADO EM CAMPO em
# 07/09/2026: sem esses dois campos o servidor APARECE na lista publica e entrar
# por ela nao baixa nada -- quando o UPnP falha (atras de NAT), a deteccao
# automatica do endereco nao acha o IP publico. Por IP direto sempre funcionou, e
# foi isso que escondeu o problema por semanas. Formato do jogo: host[:porta].
#
# Vazio de proposito, porque este repositorio e publico: deixando vazio o script
# NAO ENCOSTA nesses dois campos e avisa, em vez de gravar o endereco de outro
# servidor. Preencha com o IP ou o DNS do seu.
#
# As portas comecam nos PADROES do Eco. Troque se o seu servidor usa outras.
HOST_PUBLICO = ""
PORTA_JOGO = 3000     # UDP apenas
PORTA_WEB = 3001      # TCP apenas


def playtime():
    """168 caracteres, um por hora, comecando SEGUNDA 00h GMT.

    0 = raro, 1 = as vezes, 2 = normalmente. O campo e em GMT; os jogadores sao
    brasileiros (BRT = GMT-3), com pico observado entre 19h e 24h locais, o que
    cai entre 22h e 03h GMT. Fim de semana um pouco mais largo.
    """
    pico = {22, 23, 0, 1, 2}          # 19h-24h BRT
    medio = {19, 20, 21, 3, 4}
    s = []
    for dia in range(7):
        fds = dia >= 5                # sabado e domingo
        for h in range(24):
            if h in pico:
                s.append("2")
            elif h in medio or (fds and 14 <= h <= 21):
                s.append("1")
            else:
                s.append("0")
    return "".join(s)


PLAYTIME = playtime()

# ---------------------------------------------------------------- utilitarios

erros = []
avisos = []


def carregar(nome):
    """Le o .eco; se nao existir, cria a partir do .template."""
    alvo = os.path.join(CFG, nome)
    modelo = alvo + ".template"
    if not os.path.exists(alvo):
        if not os.path.exists(modelo):
            erros.append("nao achei nem %s nem o .template" % nome)
            return None, None
        if not SECO:
            shutil.copyfile(modelo, alvo)
        print("  %-22s criado do template" % nome)
        origem = modelo if SECO else alvo
    else:
        print("  %-22s ja existia" % nome)
        origem = alvo
    with open(origem, "r", encoding="utf-8") as f:
        return json.load(f), alvo


def gravar(dados, alvo):
    if SECO:
        return
    with open(alvo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
        f.write("\n")


def por(dados, caminho, valor):
    """Escreve num caminho aninhado, ex: GameSettings/AdvancedGameSettings/X.

    Caminho aninhado explicito de proposito: no Windows, ler o Difficulty.eco
    pelo primeiro nivel devolvia vazio, e isso gerou tres falsos alarmes.
    """
    partes = caminho.split("/")
    no = dados
    for p in partes[:-1]:
        if p not in no:
            avisos.append("caminho ausente: %s (parou em %s)" % (caminho, p))
            return False
        no = no[p]
    chave = partes[-1]
    if chave not in no:
        avisos.append("campo ausente: %s" % caminho)
        return False
    antes = no[chave]
    no[chave] = valor
    if isinstance(antes, str) and len(str(antes)) > 40:
        print("      %-46s (%d chars) -> (%d chars)"
              % (caminho, len(str(antes)), len(str(valor))))
    else:
        print("      %-46s %s -> %s" % (caminho, antes, valor))
    return True


def ler(dados, caminho):
    no = dados
    for p in caminho.split("/"):
        if not isinstance(no, dict) or p not in no:
            return "<ausente>"
        no = no[p]
    return no


print("#" * 70)
print("# CONFIGURANDO O SERVIDOR ECO" + ("   [MODO SECO - nao grava]" if SECO else ""))
print("#" * 70)
print()

# ---------------------------------------------------------------- Network.eco

print("=== Network.eco -- identidade e portas ===")
net, alvo = carregar("Network.eco")
if net is not None:
    por(net, "Name", NOME)
    por(net, "DetailedDescription", DESC)
    por(net, "GameServerPort", PORTA_JOGO)
    por(net, "WebServerPort", PORTA_WEB)
    por(net, "PublicServer", False)        # religar ao abrir de verdade
    # 07/09/2026, provado em campo: sem estes dois, o servidor aparece na lista publica
    # mas entrar por ela nao baixa nada (UPnP falha atras do MikroTik e a deteccao
    # automatica do endereco nao acha o IP publico). Por IP direto sempre funcionou.
    if HOST_PUBLICO:
        por(net, "RemoteAddress", "%s:%d" % (HOST_PUBLICO, PORTA_JOGO))
        por(net, "WebServerUrl", "http://%s:%d" % (HOST_PUBLICO, PORTA_WEB))
    else:
        print("    [!!] HOST_PUBLICO vazio -- RemoteAddress e WebServerUrl NAO")
        print("         foram tocados. Sem eles, entrar pela LISTA publica pode")
        print("         nao baixar nada (ver o comentario no topo). Por IP direto")
        print("         funciona de qualquer forma.")
    por(net, "Password", "")
    por(net, "DefaultSlots", -1)
    por(net, "ServerCategory", "Beginner")
    por(net, "Playtime", PLAYTIME)
    gravar(net, alvo)
print()

# ---------------------------------------------------------------- Difficulty.eco

print("=== Difficulty.eco -- os ajustes pedidos pelos jogadores ===")
print("    (campos ANINHADOS em GameSettings/AdvancedGameSettings)")
dif, alvo = carregar("Difficulty.eco")
if dif is not None:
    por(dif, "GameSettings/AnimalBehavior", "DefensiveOnly")
    A = "GameSettings/AdvancedGameSettings/"
    por(dif, A + "StackSizeMultiplier", 5.0)
    por(dif, A + "WeightMultiplier", 0.25)
    por(dif, A + "ConnectionRangeMultiplier", 2.0)
    por(dif, A + "ClaimPapersGrantedUponSkillscrollConsumed", 5.0)
    por(dif, A + "MeteorImpactInDays", 60.0)
    gravar(dif, alvo)
print()

# ---------------------------------------------------------------- Users.eco

print("=== Users.eco -- os tres admins ===")
usr, alvo = carregar("Users.eco")
if usr is not None:
    # A estrutura de Admins varia entre versoes: pode ser lista direta ou um
    # objeto com uma chave de lista. Detectamos em vez de supor -- supor a forma
    # do Users.eco no Windows me fez ler vazio e achar que os admins tinham sumido.
    if not ADMINS:
        # SOBRESCREVER com lista vazia tiraria o poder de todo mundo sem ninguem notar.
        # Com ADMINS vazio o certo e nao encostar no campo: use o adicionar-admin.py,
        # que faz uniao em vez de sobrescrever.
        avisos.append("ADMINS esta vazio neste script -- campo Admins do Users.eco NAO "
                      "foi tocado. Preencha ADMINS ou use o adicionar-admin.py")
        print("      Admins -> intocado (ADMINS vazio)")
    elif "Admins" not in usr:
        avisos.append("Users.eco sem campo Admins")
    elif isinstance(usr["Admins"], list):
        usr["Admins"] = ADMINS
        print("      Admins (lista direta) -> %d ids" % len(ADMINS))
    elif isinstance(usr["Admins"], dict):
        chave = None
        for k, v in usr["Admins"].items():
            if isinstance(v, list):
                chave = k
                break
        if chave:
            usr["Admins"][chave] = ADMINS
            print("      Admins/%s -> %d ids" % (chave, len(ADMINS)))
        else:
            avisos.append("Admins e objeto mas sem chave de lista; estrutura: %s"
                          % list(usr["Admins"].keys()))
    por(usr, "AdminCommandsLoggingLevel", "LogFileAndNotifyEveryone")
    gravar(usr, alvo)
print()

# ---------------------------------------------------------------- Settlements.eco

print("=== Settlements.eco -- influencia da federacao global ===")
print("    2000 porque o mundo tem 4 km2, acima do maximo suportado pela SLG")
print("    (2,56 km2). Meia-diagonal de 2000 blocos = 1414, entao 2000 da folga.")
st, alvo = carregar("Settlements.eco")
if st is not None:
    por(st, "SettlementFoundationBaseInfluence", [45.0, 150.0, 2000.0])
    gravar(st, alvo)
print()

# ---------------------------------------------------------------- WorldGenerator

print("=== WorldGenerator.eco -- o mapa do EcoAtlas ===")
print("    EXIGE WIPE para mudar depois. Por isso vem antes do primeiro arranque.")
if not os.path.exists(WG_ORIGEM):
    erros.append("nao achei %s" % WG_ORIGEM)
else:
    with open(WG_ORIGEM, "r", encoding="utf-8") as f:
        wg = json.load(f)
    d = wg.get("Dimensions", {})
    lado = d.get("WorldWidth", 0)
    km2 = round((lado * 10 / 1000.0) ** 2, 2)
    print("      MapSizePreset : %s" % wg.get("MapSizePreset"))
    print("      Dimensions    : %s x %s  ->  %s km2"
          % (lado, d.get("WorldLength"), km2))
    print("      WaterLevel    : %s" % wg.get("WaterLevel"))
    if lado != 200:
        erros.append("WorldWidth e %s, esperado 200" % lado)
    if not SECO:
        with open(os.path.join(CFG, "WorldGenerator.eco"), "w",
                  encoding="utf-8") as f:
            json.dump(wg, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("      gravado em Configs/WorldGenerator.eco")
print()

# ---------------------------------------------------------------- conferencia

print("=" * 70)
print("CONFERINDO -- lendo os arquivos DE VOLTA do disco")
print("=" * 70)
if SECO:
    print("  modo seco: nada foi gravado, nada a conferir")
else:
    checagens = [
        ("Network.eco", "GameServerPort", PORTA_JOGO),
        ("Network.eco", "WebServerPort", PORTA_WEB),
        ("Network.eco", "PublicServer", False),
    ]
    if HOST_PUBLICO:
        checagens += [
            ("Network.eco", "RemoteAddress",
             "%s:%d" % (HOST_PUBLICO, PORTA_JOGO)),
            ("Network.eco", "WebServerUrl",
             "http://%s:%d" % (HOST_PUBLICO, PORTA_WEB)),
        ]
    checagens += [
        ("Network.eco", "ServerCategory", "Beginner"),
        ("Difficulty.eco", "GameSettings/AnimalBehavior", "DefensiveOnly"),
        ("Difficulty.eco",
         "GameSettings/AdvancedGameSettings/StackSizeMultiplier", 5.0),
        ("Difficulty.eco",
         "GameSettings/AdvancedGameSettings/WeightMultiplier", 0.25),
        ("Difficulty.eco",
         "GameSettings/AdvancedGameSettings/MeteorImpactInDays", 60.0),
        ("WorldGenerator.eco", "Dimensions/WorldWidth", 200),
    ]
    ruim = 0
    for arq, caminho, esperado in checagens:
        p = os.path.join(CFG, arq)
        try:
            with open(p, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            print("  [XX] %s nao abre: %s" % (arq, e))
            ruim += 1
            continue
        lido = ler(dados, caminho)
        ok = (lido == esperado)
        if not ok:
            ruim += 1
        print("  %s %-18s %-46s = %s" % ("[ok]" if ok else "[XX]", arq, caminho, lido))

    print()
    n = len([x for x in os.listdir(CFG) if x.endswith(".eco")])
    print("  arquivos .eco em Configs: %d" % n)
    print("  Name : %d de 250 chars" % len(NOME))
    print("  Desc : %d de 500 chars" % len(DESC))
    print("  Playtime : %d de 168 chars" % len(PLAYTIME))
    if len(PLAYTIME) != 168:
        erros.append("Playtime com %d chars, esperado 168" % len(PLAYTIME))
    if ruim:
        erros.append("%d checagens falharam" % ruim)

print()
if avisos:
    print("AVISOS:")
    for a in avisos:
        print("  ! %s" % a)
if erros:
    print("ERROS:")
    for e in erros:
        print("  XX %s" % e)
    sys.exit(1)
print("OK -- configuracao aplicada e conferida.")
print()
print("Ainda NAO configurado de proposito:")
print("  Civics.eco     -> nao precisa: /admininterface faz o mesmo por chat")
print("  Backup.eco     -> o padrao do Eco ja faz backup a cada 30 min com rotacao")
print("  DiscordAddress -> vazio; decisao do Raul")
