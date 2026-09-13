# -*- coding: utf-8 -*-
import UnityPy
from UnityPy.enums import TextureFormat

env = UnityPy.load("MixologyMod.unity3d")
# indexar texturas por path_id
tex = {}
for obj in env.objects:
    if obj.type.name == "Texture2D":
        d = obj.read()
        tex[obj.path_id] = (d.m_Name, d.m_Width, d.m_Height, d.m_TextureFormat)

print("=== Sprite -> Texture2D")
achou = 0
for obj in env.objects:
    if obj.type.name != "Sprite": continue
    d = obj.read()
    pid = None
    try: pid = d.m_RD.texture.m_PathID
    except Exception:
        try: pid = d.m_RD.texture.path_id
        except Exception: pass
    t = tex.get(pid)
    if t:
        achou += 1
        print("   %-32s -> tex '%s'  %dx%d  fmt %s" % (d.m_Name, t[0], t[1], t[2], t[3]))
    else:
        print("   %-32s -> (textura nao resolvida, pid=%s)" % (d.m_Name, pid))
print()
print("sprites resolvidos:", achou)
print()
fmts = {}
for _, (n, w, h, f) in tex.items(): fmts[str(f)] = fmts.get(str(f), 0) + 1
print("formatos das 68 texturas:", fmts)
