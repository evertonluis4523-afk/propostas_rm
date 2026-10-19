#!/usr/bin/env python3
"""Blocos comuns do Padrão RM: FONTE ÚNICA em central_rm/comum/.

Os blocos que são iguais em todos os sistemas (login, barra, impressão, selo,
nuvem, fonte, tema...) moram UMA vez em central_rm/comum/, e esta ferramenta
os aplica em todos. Ninguém edita bloco comum dentro de um sistema: muda o
arquivo em comum/, roda isto, roda o verificador e os testes, publica.

Uso (na pasta que tem todos os repositórios):
  python3 central_rm/ferramentas/aplica_comum.py /pasta            # aplica
  python3 central_rm/ferramentas/aplica_comum.py /pasta --conferir # só diz o que mudaria
  python3 central_rm/ferramentas/aplica_comum.py /pasta --sobe-versao
      # aplica e sobe APP_VER + CACHE de quem mudou

Também leva de central_rm para os outros, iguais: PADRAO_RM.md, CLAUDE.md,
ferramentas/ (verificador, esta ferramenta e os testes) e o corpo do service
worker (as três linhas de configuração de cada um ficam como estão).

Cada bloco é achado por uma MARCA (texto que só existe nele) e recortado do
<script>/<style> que abre a linha até o fechamento -- nunca por uma busca
solta de "<script", que pegaria texto de dentro do JavaScript.
"""
import json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CENTRAL = os.path.dirname(AQUI)
COMUM = os.path.join(CENTRAL, 'comum')
DESCARTADOS = {'controle_faltas', 'calculo_telha-t-rmica'}
DOCS = ['PADRAO_RM.md', 'CLAUDE.md']


def ler(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def iguais(a, b):
    # por bytes: as fixtures do leitor (DXF) estão em latin-1, não em UTF-8
    with open(a, 'rb') as fa, open(b, 'rb') as fb:
        return fa.read() == fb.read()


def grava(p, s):
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


def manifesto():
    return json.loads(ler(os.path.join(COMUM, 'blocos.json')))


def acha_bloco(html, marca):
    """(ini, fim) do elemento <script>/<style> que contém a marca, ou None.
    Erro se a marca aparecer mais de uma vez."""
    pos = [m.start() for m in re.finditer(re.escape(marca), html)]
    if not pos:
        return None
    if len(pos) > 1:
        raise ValueError('marca aparece %d vezes: %r' % (len(pos), marca))
    p = pos[0]
    abre = None
    for m in re.finditer(r'(?m)^<(script|style)\b[^>]*>', html[:p]):
        abre = m
    if not abre:
        raise ValueError('sem <script>/<style> no começo de linha antes da marca %r' % marca)
    tag = abre.group(1)
    fecha = html.find('</%s>' % tag, p)
    if fecha < 0:
        raise ValueError('sem </%s> depois da marca %r' % (tag, marca))
    fim = fecha + len('</%s>' % tag)
    miolo = html[abre.end():p]
    if re.search(r'(?m)^<(script|style)\b', miolo):
        raise ValueError('bloco ambíguo para a marca %r' % marca)
    return abre.start(), fim


# Outras páginas inteiras de um sistema (ex.: a medicao.html da PU): as que
# já usam a fonte comum. Recebem os mesmos blocos que tiverem; a fonte e o
# Tema RM são obrigatórios nelas. Sem isto a tela de trabalho da PU ficou
# meses com fonte, tema e impressão antigos -- só o index.html era aplicado.
OBRIG_EXTRA = {'Fonte Satoshi', 'Tema RM (aparência)'}


def paginas_extras(repo_dir):
    out = []
    for n in sorted(os.listdir(repo_dir)):
        if n.endswith('.html') and n != 'index.html':
            if 'var RM_FONTE="@font-face' in ler(os.path.join(repo_dir, n)):
                out.append(n)
    return out


def aplica_blocos(html, blocos, mestres, repo, problemas, obrig=None, rotulo=''):
    trocados = []
    for b in blocos:
        if repo in b.get('exceto', []):
            continue
        try:
            achado = acha_bloco(html, b['marca'])
        except ValueError as e:
            problemas.append('%s%s: %s' % (repo, rotulo, e)); continue
        if not achado:
            if (b.get('obrigatorio', True) if obrig is None else b['nome'] in obrig):
                problemas.append('%s%s: falta o bloco %s (inserir uma vez à mão, depois a ferramenta mantém)' % (repo, rotulo, b['nome']))
            continue
        i, f = achado
        if html[i:f] != mestres[b['arquivo']]:
            html = html[:i] + mestres[b['arquivo']] + html[f:]
            trocados.append(b['nome'])
    return html, trocados


def repos_da(raiz):
    return sorted(d for d in os.listdir(raiz)
                  if os.path.isfile(os.path.join(raiz, d, 'index.html')) and d not in DESCARTADOS)


def sobe_versao(repo_dir):
    p = os.path.join(repo_dir, 'index.html'); s = ler(p)
    m = re.search(r"const\s+APP_VER\s*=\s*['\"]v(\d+)['\"]", s)
    if not m:
        return None
    novo = int(m.group(1)) + 1
    s = s[:m.start()] + m.group(0).replace('v%s' % m.group(1), 'v%d' % novo) + s[m.end():]
    grava(p, s)
    for nome in ('sw.js', 'service-worker.js'):
        sp = os.path.join(repo_dir, nome)
        if os.path.exists(sp):
            t = ler(sp)
            t2 = re.sub(r"(const CACHE = '[^']*-)v%s'" % m.group(1), r"\g<1>v%d'" % novo, t)
            grava(sp, t2)
    return 'v%d' % novo


def corpo_sw(s):
    i = s.find("self.addEventListener('install'")
    return (s[:i], s[i:]) if i >= 0 else (s, '')


def aplica(raiz, conferir=False, subir=False):
    blocos = manifesto()
    mestres = {b['arquivo']: ler(os.path.join(COMUM, b['arquivo'])) for b in blocos}
    central = os.path.basename(CENTRAL)
    problemas, mudou = [], {}
    for repo in repos_da(raiz):
        d = os.path.join(raiz, repo)
        p = os.path.join(d, 'index.html'); html = ler(p); orig = html
        html, trocados = aplica_blocos(html, blocos, mestres, repo, problemas)
        arquivos = []
        if html != orig:
            arquivos.append('index.html')
            if not conferir:
                grava(p, html)
        for pag in paginas_extras(d):
            pp = os.path.join(d, pag); h0 = ler(pp)
            h1, tr = aplica_blocos(h0, blocos, mestres, repo, problemas, OBRIG_EXTRA, ' (' + pag + ')')
            if h1 != h0:
                arquivos.append(pag); trocados += [t + ' (' + pag + ')' for t in tr]
                if not conferir:
                    grava(pp, h1)
        if repo != central:
            for doc in DOCS:
                o, dst = os.path.join(CENTRAL, doc), os.path.join(d, doc)
                if os.path.exists(o) and (not os.path.exists(dst) or ler(o) != ler(dst)):
                    arquivos.append(doc)
                    if not conferir: shutil.copyfile(o, dst)
            for raizf, _, nomes in os.walk(AQUI):
                if '__pycache__' in raizf or os.sep + '.libs' in raizf or os.sep + 'node_modules' in raizf:
                    continue
                for n in nomes:
                    if n == 'regras_firebase.json' or n.endswith('.pyc'):
                        continue
                    o = os.path.join(raizf, n)
                    rel = os.path.relpath(o, CENTRAL)
                    dst = os.path.join(d, rel)
                    if not os.path.exists(dst) or not iguais(o, dst):
                        arquivos.append(rel)
                        if not conferir:
                            os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copyfile(o, dst)
            _, corpo_ref = corpo_sw(ler(os.path.join(CENTRAL, 'sw.js')))
            for nome in ('sw.js', 'service-worker.js'):
                sp = os.path.join(d, nome)
                if os.path.exists(sp):
                    cab, corpo = corpo_sw(ler(sp))
                    if corpo and corpo != corpo_ref:
                        arquivos.append(nome)
                        if not conferir: grava(sp, cab + corpo_ref)
        if arquivos:
            mudou[repo] = (trocados, arquivos)
    # páginas montadas de molde (vitrine, proposta...): o molde com os MESMOS
    # blocos colados, para mostrar exatamente o que os sistemas usam
    for nome in sorted(os.listdir(COMUM)):
        if not nome.endswith('.modelo.html'):
            continue
        v = re.sub(r'<!--COMUM:([\w.-]+)-->', lambda m: ler(os.path.join(COMUM, m.group(1))), ler(os.path.join(COMUM, nome)))
        final = nome.replace('.modelo.html', '.html')
        dst = os.path.join(COMUM, final)
        if not os.path.exists(dst) or ler(dst) != v:
            mudou.setdefault(central, ([], []))[1].append('comum/' + final)
            if not conferir: grava(dst, v)
    for repo, (tr, arqs) in mudou.items():
        ver = ''
        if subir and not conferir and any(x.endswith('.html') and '/' not in x for x in arqs):
            ver = ' -> ' + (sobe_versao(os.path.join(raiz, repo)) or '?')
        print('%-27s %s%s' % (repo, ', '.join(arqs), ver))
        if tr:
            print('   blocos: ' + ', '.join(tr))
    if not mudou:
        print('Nada a aplicar: todos os sistemas já estão iguais à fonte (central_rm/comum).')
    for x in problemas:
        print('   ✗ ' + x)
    return 1 if problemas else 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    raiz = args[0] if args else os.path.dirname(CENTRAL)
    sys.exit(aplica(raiz, conferir='--conferir' in sys.argv, subir='--sobe-versao' in sys.argv))
