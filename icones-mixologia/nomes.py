# -*- coding: utf-8 -*-
import UnityPy, collections
env = UnityPy.load("MixologyMod.unity3d")
gos = []
for obj in env.objects:
    if obj.type.name == "GameObject":
        d = obj.read()
        gos.append(str(d.m_Name))
print("GameObjects:", len(gos))
c = collections.Counter(gos)
print()
print("=== nomes que parecem item/bebida")
alvo = [n for n in sorted(set(gos)) if any(k in n.lower() for k in
        ("colada","martini","grasshopper","matcha","smoothie","tea","juice","rain","bloody","item","scroll","book"))]
for n in alvo[:40]: print("   %-40s x%d" % (n, c[n]))
print()
print("=== 25 nomes mais comuns")
for n, q in c.most_common(25): print("   %-40s x%d" % (n, q))
print()
print("=== nome do AssetBundle e lista de assets")
for obj in env.objects:
    if obj.type.name == "AssetBundle":
        d = obj.read()
        print("   bundle:", d.m_Name)
        try:
            nomes = list(d.m_Container.keys()) if hasattr(d.m_Container, "keys") else [k for k, _ in d.m_Container]
            print("   assets no container:", len(nomes))
            for k in nomes[:25]: print("      " + str(k))
        except Exception as e:
            print("   container:", e)
