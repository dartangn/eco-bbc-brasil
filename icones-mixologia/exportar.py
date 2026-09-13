# -*- coding: utf-8 -*-
import UnityPy, os
from PIL import Image

os.makedirs("originais", exist_ok=True)
env = UnityPy.load("MixologyMod.unity3d")
n = 0
for obj in env.objects:
    if obj.type.name != "Texture2D": continue
    d = obj.read()
    try: img = d.image
    except Exception as e:
        print("falhou", d.m_Name, e); continue
    nome = str(d.m_Name).strip().replace("/", "_") or ("sem-nome-%d" % obj.path_id)
    img.save(os.path.join("originais", "%s__%d.png" % (nome, obj.path_id)))
    n += 1
print("exportadas:", n)

# estatistica do fundo em 5 amostras
print()
for f in sorted(os.listdir("originais"))[:5]:
    im = Image.open(os.path.join("originais", f)).convert("RGB")
    w, h = im.size
    px = im.load()
    cantos = [px[0,0], px[w-1,0], px[0,h-1], px[w-1,h-1]]
    borda = [px[x,0] for x in range(0,w,16)] + [px[x,h-1] for x in range(0,w,16)]
    brancos = sum(1 for p in borda if min(p) > 240)
    print("%-28s %dx%d  cantos=%s  borda quase-branca: %d/%d"
          % (f, w, h, cantos[0], brancos, len(borda)))
