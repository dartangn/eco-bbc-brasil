# -*- coding: utf-8 -*-
"""Compara cada Configs/X.eco com o X.eco.template de fabrica e lista SO o que difere.
Responde "isto e padrao do jogo ou nos configuramos?" para qualquer campo. So leitura."""
import io, json, os

CFG = "/opt/eco/server/Configs"

def carrega(p):
    try:
        return json.load(io.open(p, encoding="utf-8-sig"))
    except Exception as e:
        return {"__erro__": str(e)}

def achata(o, pre=""):
    saida = {}
    if isinstance(o, dict):
        for k, v in o.items():
            saida.update(achata(v, pre + "." + k if pre else k))
    else:
        saida[pre] = o
    return saida

arquivos = sorted(a for a in os.listdir(CFG) if a.endswith(".eco"))
print("=" * 92)
print("CONFIGS: o que difere do template de fabrica")
print("=" * 92)
for a in arquivos:
    p = os.path.join(CFG, a)
    t = p + ".template"
    if not os.path.exists(t):
        print("\n## %-28s (SEM template de fabrica para comparar)" % a)
        continue
    atual, base = achata(carregaible := carrega(p)), achata(carrega(t))
    dif = [k for k in sorted(set(atual) | set(base)) if atual.get(k) != base.get(k)]
    if not dif:
        print("\n## %-28s  IGUAL ao template -- tudo padrao do jogo" % a)
        continue
    print("\n## %-28s  %d campo(s) diferente(s) do padrao" % (a, len(dif)))
    for k in dif:
        va, vb = base.get(k, "(nao existe)"), atual.get(k, "(nao existe)")
        sa, sb = repr(va), repr(vb)
        if len(sa) > 34: sa = sa[:31] + "..."
        if len(sb) > 34: sb = sb[:31] + "..."
        print("   %-52s padrao %-34s -> %s" % (k, sa, sb))
