# -*- coding: utf-8 -*-
import UnityPy, collections, os
env = UnityPy.load("MixologyMod.unity3d")
tipos = collections.Counter()
texturas = []
sprites = []
for obj in env.objects:
    tipos[obj.type.name] += 1
    if obj.type.name == "Texture2D":
        d = obj.read()
        texturas.append((d.m_Name, d.m_Width, d.m_Height, str(d.m_TextureFormat)))
    elif obj.type.name == "Sprite":
        d = obj.read()
        sprites.append(d.m_Name)
print("versao do bundle:", env.file.version if hasattr(env.file, "version") else "?")
print("objetos por tipo:", dict(tipos))
print()
print("=== Texture2D (%d)" % len(texturas))
for n, w, h, f in sorted(texturas):
    print("   %-34s %4dx%-4d  %s" % (n, w, h, f))
print()
print("=== Sprite (%d)" % len(sprites))
for n in sorted(sprites): print("   " + n)
