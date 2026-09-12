# -*- coding: utf-8 -*-
"""Pre-voo de arquivo .cs novo antes de instalar em Mods/UserCode.
Roda NO SERVIDOR, como ecosrv (precisa ler /opt/eco/server/Mods):

    sudo -u ecosrv python3 /opt/eco/scripts-py/conferir-cs-novo.py /caminho/Arquivo.cs

Existe por causa de duas quedas em dois dias, as duas pelo mesmo motivo: eu copiei a FORMA de um codigo
que compila em outro lugar sem conferir em que namespace cada tipo vive.
  08/09  PonteServidor.cs  error CS0103  NotificationCategory
  10/09  PlacasNoMenu.cs   error CS0246  Singleton<>
Erro de compilacao em UserCode derruba o servidor inteiro, e tres arranques falhos travam o start por 30 min
(StartLimitBurst=3), o que exige root para destravar. Este script nao substitui o arranque vigiado (Regra 18);
ele so pega antes o que e barato pegar antes.

O que ele confere:
  1. ASCII puro (regra do projeto para .cs nosso)
  2. chaves e parenteses balanceados fora de comentario e de string
  3. para cada `using Eco.*`: se algum arquivo que JA COMPILA neste servidor usa o mesmo namespace
  4. para cada tipo Eco usado (identificador Maiusculo conhecido): em quantos arquivos do servidor aparece,
     e com quais usings esses arquivos aparecem -- tipo que nao aparece em NENHUM e o suspeito numero um
"""
import io, os, re, sys

MODS = "/opt/eco/server/Mods"

# tipos que nao vale conferir: sao do .NET ou palavra-chave
IGNORAR = set("""
System String Int32 Boolean Object Exception DateTime File Directory Path Math Convert
Console Enumerable List Dictionary IEnumerable Task Thread Guid TimeSpan Random StringBuilder
""".split())


def limpa(texto):
    """tira comentarios de linha, de bloco e literais de string"""
    texto = re.sub(r"/\*.*?\*/", " ", texto, flags=re.S)
    texto = re.sub(r"//[^\n]*", " ", texto)
    texto = re.sub(r'"(?:\\.|[^"\\])*"', '""', texto)
    return texto


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: conferir-cs-novo.py <arquivo.cs>")
    alvo = sys.argv[1]
    bruto = io.open(alvo, encoding="utf-8", errors="replace").read()
    problemas = []

    print("== 1. ASCII")
    fora = [(i + 1, l) for i, l in enumerate(bruto.splitlines())
            if any(ord(c) > 127 for c in l)]
    if fora:
        problemas.append("%d linha(s) com caractere fora do ASCII" % len(fora))
        for n, l in fora[:5]:
            print("   linha %d: %s" % (n, l.strip()[:90]))
    else:
        print("   ok, so ASCII")

    print("== 2. chaves e parenteses (fora de comentario e string)")
    corpo = limpa(bruto)
    for abre, fecha in (("{", "}"), ("(", ")")):
        a, f = corpo.count(abre), corpo.count(fecha)
        print("   %s %d   %s %d   %s" % (abre, a, fecha, f, "ok" if a == f else "DESBALANCEADO"))
        if a != f:
            problemas.append("%s%s desbalanceado (%d x %d)" % (abre, fecha, a, f))

    # indice do servidor: arquivo -> (texto, usings)
    print("== 3. lendo os .cs que ja compilam neste servidor")
    arquivos = []
    for pasta, _, arqs in os.walk(MODS):
        for a in arqs:
            if not a.endswith(".cs"):
                continue
            p = os.path.join(pasta, a)
            if os.path.abspath(p) == os.path.abspath(alvo):
                continue
            try:
                t = io.open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            arquivos.append((p.replace(MODS + "/", ""), t,
                             set(re.findall(r"^\s*using\s+([A-Za-z0-9_.]+)\s*;", t, re.M))))
    print("   %d arquivos" % len(arquivos))

    print("== 4. cada `using Eco.*` do arquivo novo aparece em quantos deles")
    meus_usings = re.findall(r"^\s*using\s+([A-Za-z0-9_.]+)\s*;", bruto, re.M)
    for u in meus_usings:
        if not u.startswith("Eco."):
            continue
        n = sum(1 for _, _, us in arquivos if u in us)
        print("   %-42s %d" % (u, n))
        if n == 0:
            problemas.append("using %s nao aparece em nenhum arquivo que compila aqui" % u)

    print("== 5. tipos Eco usados no arquivo novo")
    # identificadores em posicao de tipo: heranca, parametro, `new X`, generico, typeof, e os I*
    usados = set()
    for m in re.finditer(r"\bclass\s+\w+\s*:\s*([^\{]+)", corpo):
        usados |= set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)", m.group(1)))
    usados |= set(re.findall(r"\bnew\s+([A-Z][A-Za-z0-9_]*)", corpo))
    usados |= set(re.findall(r"\(\s*([A-Z][A-Za-z0-9_]*)\s+\w+\s*\)", corpo))   # parametro
    usados |= set(re.findall(r"^\s*public\s+([A-Z][A-Za-z0-9_]*)\s+\w+\s*\(", corpo, re.M))  # retorno
    usados |= set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\.[A-Z]", corpo))          # X.Membro estatico
    usados |= set(re.findall(r"\btypeof\s*\(\s*([A-Z][A-Za-z0-9_]*)", corpo))   # typeof(X)
    usados |= set(re.findall(r"<\s*([A-Z][A-Za-z0-9_]*)\s*>", corpo))           # generico <X>
    # Tipo NOVO declarado aqui (sem `partial`) nao tem de aparecer em outro arquivo -- senao classe
    # nossa nova sempre reprovaria, e falso alarme treina a ignorar aviso (licao da secao 39.1).
    # Mas classe `partial` declarada aqui TEM de existir em outro arquivo: e uma extensao de classe
    # do jogo, e se o nome estiver com erro de digitacao o C# compila uma classe NOVA e vazia, o
    # gancho nunca roda e o mod nao faz nada -- falha silenciosa. Essas ficam NA conferencia.
    novos = set(re.findall(r"\b(?:class|struct|interface|enum)\s+([A-Za-z0-9_]+)", corpo))
    parciais = set(re.findall(r"\bpartial\s+(?:class|struct|interface)\s+([A-Za-z0-9_]+)", corpo))
    novos -= parciais
    if novos:
        print("   (tipos NOVOS declarados aqui, fora da conferencia: %s)" % ", ".join(sorted(novos)))
    if parciais:
        print("   (classes `partial` daqui: %s -- estas TEM de existir em outro arquivo)"
              % ", ".join(sorted(parciais)))
    usados |= parciais
    usados -= novos
    usados -= IGNORAR
    for tipo in sorted(usados):
        casa = [(nome, us) for nome, t, us in arquivos
                if re.search(r"\b%s\b" % re.escape(tipo), t)]
        if not casa:
            print("   %-28s 0 arquivos  <<< NAO APARECE EM NENHUM QUE COMPILA AQUI" % tipo)
            problemas.append("tipo %s nao aparece em nenhum arquivo que compila aqui" % tipo)
        else:
            exemplo = casa[0][0]
            print("   %-28s %3d arquivos   ex.: %s" % (tipo, len(casa), exemplo[:60]))

    print()
    if problemas:
        print("[XX] %d ponto(s) a resolver antes de instalar:" % len(problemas))
        for p in problemas:
            print("   -", p)
        sys.exit(1)
    print("[ok] pre-voo passou. Isso NAO garante compilacao: instalar so com arranque vigiado (Regra 18).")


main()
