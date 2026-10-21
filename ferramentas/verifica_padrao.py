#!/usr/bin/env python3
"""Verificador do Padrão RM (ver PADRAO_RM.md).

Uso:
  python3 ferramentas/verifica_padrao.py            # confere este repositório
  python3 ferramentas/verifica_padrao.py /pasta     # confere todos os repositórios dentro da pasta

Com vários repositórios, os blocos compartilhados são comparados entre si: a
versão que a maioria tem é a referência, e quem destoa aparece como erro.
Sai com código 1 se houver erro -- nenhuma publicação sai assim.
"""
import hashlib, os, re, sys
from collections import Counter

# Sistemas que não têm login próprio (a porta é a da Central, ou são públicos)
SEM_LOGIN = {'central_rm'}
# Sistemas fora de uso: não são conferidos
DESCARTADOS = {'controle_faltas', 'calculo_telha-t-rmica'}
# Sistemas com papelaria própria (já no padrão de timbrado/rodapé), sem o bloco "O IMPRESSO"
PAPELARIA_PROPRIA = {'recibos_rm', 'orcamento-rm', 'central_rm'}
# A Central tem a barra do alto dela (é a moldura dos outros)
BARRA_PROPRIA = {'central_rm'}

BLOCOS = {
    'impressão (rmImpressaoBloco)': r'<script id="rmImpressaoBloco">.*?</script>',
    'login – estilo (rmPortaEstilo)': r'<style id="rmPortaEstilo">.*?</style>',
    'login – script (rmPortaBloco)': r'<script id="rmPortaBloco">.*?</script>',
    'papel (O IMPRESSO)': r"O IMPRESSO — o mesmo pe.*?</script>",
    'barra do alto (52 px)': r"A BARRA DO ALTO TEM UMA ALTURA.*?</style>",
    'selo de versão (rmVersaoBloco)': r'<script id="rmVersaoBloco">.*?</script>',
    'nuvem (rmNuvemErro)': r'if\(window\.rmNuvemErro\) return;.*?\n\}\)\(\);',
}


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aplica_comum import acha_bloco, paginas_extras, OBRIG_EXTRA  # noqa: E402  (mesma pasta)


def acha_comum(repo):
    """A fonte única dos blocos: central_rm/comum ao lado do repositório (ou
    dentro dele, quando é a própria Central). None se não estiver à mão."""
    import json
    for d in (os.path.join(repo, 'comum'), os.path.join(os.path.dirname(os.path.normpath(repo)), 'central_rm', 'comum')):
        m = os.path.join(d, 'blocos.json')
        if os.path.exists(m):
            bl = json.loads(ler(m))
            return {'blocos': bl, 'texto': {b['arquivo']: ler(os.path.join(d, b['arquivo'])) for b in bl}}
    return None


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()[:10]


def ler(p):
    try:
        with open(p, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return None


def sw_de(repo):
    for nome in ('sw.js', 'service-worker.js'):
        s = ler(os.path.join(repo, nome))
        if s is not None:
            return nome, s
    return None, None


def corpo_sw(s):
    i = s.find("self.addEventListener('install'")
    return s[i:] if i >= 0 else ''


# blocos que precisam rodar antes da primeira pintura: no fim do <body> o
# navegador ja pintou a pagina clara quando o tema escuro chega (a Medicao
# da PU piscava o cartao de login branco ao abrir no escuro)
NO_HEAD = {'tema.html': 'a página pisca clara antes do escuro (o tema precisa rodar antes da primeira pintura)'}


# ---- CÓDIGO MORTO --------------------------------------------------------
# Limpeza de out/2026: funções que nada chamava, estilos de telas que já não
# existem (vinham junto quando um sistema nascia da cópia de outro) e o logo
# gravado duas ou três vezes no mesmo arquivo. Isto trava a volta. Os blocos
# comuns ficam de fora: valem para todos, e cada sistema usa uma parte.
SVG64 = r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]{3000,}'

def _sem(h, trechos):
    for a, b in sorted(trechos, reverse=True):
        h = h[:a] + ' ' * (b - a) + h[b:]
    return h

def _regras_css(css, base=0):
    """(ini, fim, seletor) das regras comuns de uma folha; desce em @media."""
    out, i, n = [], 0, len(css)
    while i < n:
        if css.startswith('/*', i):
            i = css.find('*/', i) + 2 or n; continue
        if css[i].isspace() or css[i] == '}':
            i += 1; continue
        j = i
        while j < n and css[j] not in '{;':
            if css.startswith('/*', j):
                j = css.find('*/', j) + 2; continue
            j += 1
        if j >= n:
            break
        if css[j] == ';':
            i = j + 1; continue
        d, k = 0, j
        while k < n:
            if css.startswith('/*', k):
                k = css.find('*/', k) + 2; continue
            if css[k] == '{':
                d += 1
            elif css[k] == '}':
                d -= 1
                if d == 0:
                    break
            k += 1
        cab = css[i:j].strip()
        if cab.startswith(('@media', '@supports', '@container')):
            out += _regras_css(css[j + 1:k], base + j + 1)
        elif not cab.startswith('@'):
            out.append((base + i, base + k + 1, cab))
        i = k + 1
    return out

def codigo_morto(h, comuns):
    """Erros de código sem uso em h, fora dos trechos `comuns` [(ini, fim)]."""
    erros = []
    rep = [x for x, n in Counter(re.findall(SVG64, h)).items() if n > 1]
    if rep:
        erros.append('logo gravado %d vezes no arquivo (deixe uma cópia e aponte as outras para ela)' % max(h.count(x) for x in rep))
    scripts = [(m.start(), m.end()) for m in re.finditer(r'(?is)<script\b[^>]*>.*?</script>', h)]
    masc = _sem(h, scripts)
    estilos = [(m.start(), m.end(), m.start(2), m.group(2)) for m in re.finditer(r'(?is)(<style\b[^>]*>)(.*?)</style>', masc)]
    estilos = [(a, b, c, h[c:c + len(g)]) for a, b, c, g in estilos]
    proprio = _sem(h, comuns)
    toks = Counter(re.findall(r'[A-Za-z_$][\w$]*', re.sub(SVG64, '', h)))
    decl = (re.findall(r'(?<![(!]\s)(?<![(!])\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', proprio)
            + re.findall(r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)', proprio))
    mortas = sorted(set(n for n in decl if toks[n] <= 1))
    if mortas:
        erros.append('função que nada chama: ' + ', '.join(mortas))
    # classes: usadas no HTML e no script (fora das <style>); "x-" + algo
    # montado no script conta como uso de todas as "x-..."
    uso = _sem(h, [(a, b) for a, b, c, g in estilos])
    utoks = set(re.findall(r'[A-Za-z_][\w-]*', uso))
    def usada(c):
        if c in utoks:
            return True
        return any(c[k - 1] in '-_' and re.search(r'(?<![\w-])' + re.escape(c[:k]) + r'(?:[\'"`+]|\$\{)', uso) for k in range(len(c) - 1, 0, -1))
    sobra = []
    for a, b, c, css in estilos:
        if any(x <= a < y for x, y in comuns):
            continue
        for _, _, cab in _regras_css(css):
            for sel in re.split(r',(?![^()]*\))', cab):
                sl = re.sub(r'\[[^\]]*\]', '', re.sub(r':not\([^()]*\)', '', sel))
                sobra += [k for k in re.findall(r'\.([A-Za-z_][\w-]*)', sl) if not usada(k)]
    if sobra:
        erros.append('estilo de classe que o sistema não usa: .' + ', .'.join(sorted(set(sobra))[:12]) + (' (+%d)' % (len(set(sobra)) - 12) if len(set(sobra)) > 12 else ''))
    return erros

def analisa(repo):
    nome = os.path.basename(os.path.normpath(repo))
    h = ler(os.path.join(repo, 'index.html')) or ''
    r = {'nome': nome, 'erros': [], 'avisos': [], 'hash': {}}
    if not h:
        r['erros'].append('index.html não encontrado')
        return r
    for rot, pat in BLOCOS.items():
        m = re.search(pat, h, re.S)
        r['hash'][rot] = md5(m.group(0)) if m else None
    precisa = {
        'impressão (rmImpressaoBloco)': True,
        'login – estilo (rmPortaEstilo)': nome not in SEM_LOGIN,
        'login – script (rmPortaBloco)': nome not in SEM_LOGIN,
        'papel (O IMPRESSO)': nome not in PAPELARIA_PROPRIA,
        'barra do alto (52 px)': nome not in BARRA_PROPRIA,
        'selo de versão (rmVersaoBloco)': True,
        'nuvem (rmNuvemErro)': True,
    }
    for rot, obrig in precisa.items():
        if obrig and not r['hash'][rot]:
            r['erros'].append('falta o bloco ' + rot)
    # fonte
    if "font-family:'Satoshi'" not in h and 'font-family:"Satoshi"' not in h and "font-family: 'Satoshi'" not in h:
        r['erros'].append('fonte Satoshi não embutida')
    if 'fonts.googleapis.com' in h:
        r['avisos'].append('carrega fonte de fora (fonts.googleapis.com)')
    # tema e celular
    if 'data-theme' not in h:
        r['erros'].append('sem tema claro/escuro (data-theme)')
    if 'touch-action' not in h:
        r['avisos'].append('sem touch-action:manipulation (zoom de toque duplo)')
    # sem "Sair" nos sistemas (a Central fecha tudo)
    if nome != 'central_rm' and ('onclick="doLogout()"' in h or re.search(r'<button[^>]*title="Sair"', h)
                                 or re.search(r'<button[^>]*>\s*(?:[⎋🚪⏻]\s*)?Sair(?: da conta)?\s*<', h)):
        r['erros'].append('botão "Sair" (os sistemas são fechados pela Central)')
    # sem "Tela cheia" nem "Instalar app" (o sistema roda na janela da Central)
    if nome != 'central_rm':
        if 'onclick="toggleFullscreen()"' in h or re.search(r'<button[^>]*>(?:\s|<[^>]+>)*(?:⛶\s*)?Tela cheia\s*<', h):
            r['erros'].append('botão "Tela cheia" (o sistema roda na janela da Central)')
        if re.search(r'<button[^>]*>[^<]*Instalar app', h):
            r['erros'].append('botão "Instalar app" (o sistema roda dentro da Central)')
    # impressão
    if '⬇ PDF' in h and 'injetarBotao' in h:
        r['erros'].append('botão "⬇ PDF" injetado ao lado do Imprimir')
    # timbrado: uma informação por linha (PADRAO_RM.md, Papel). Endereço e
    # cidade no mesmo texto viram uma linha só, tão comprida que encosta na logo.
    if re.search(r"""['"`]Rod[^'"`<]*Sala 2\s*[·•,]\s*Novo Paraíso""", h):
        r['erros'].append('timbrado: endereço e cidade juntos numa linha só (cada um na sua linha)')
    # timbrado em duas colunas: razão social e CNPJ | endereço e cidade. O
    # telefone saiu (está no rodapé) e o nome fantasia também (a logo já diz):
    # CNPJ colado no telefone é sinal do timbrado antigo que sobrou.
    for m in re.finditer(r"""CNPJ[^<\n]{0,50}?(?:99789|\.fone\b)""", h):
        n = h.count('\n', 0, m.start()) + 1
        r['erros'].append('timbrado antigo na linha %d: CNPJ com telefone (modelo de duas colunas, telefone só no rodapé)' % n)
    for m in re.finditer(r'''class=\\?["']nm\\?["']>RM Estruturas''', h):
        n = h.count('\n', 0, m.start()) + 1
        r['erros'].append('timbrado antigo na linha %d: nome fantasia no timbrado (a logo já diz; vai a razão social)' % n)
    # cor por NOME (white, black...): o tema escuro traduz #hex, rgb() e
    # variável -- o nome passa batido, e o "background:white" dos botões de
    # cotação do Orçamento ficava branco no escuro
    for m in re.finditer(r'(?:background(?:-color)?|(?<![-\w])color|border(?:-color)?)\s*:\s*(white|black|gray|grey|silver|whitesmoke|lightgray|lightgrey|gainsboro)\b', h, re.I):
        n = h.count('\n', 0, m.start()) + 1
        r['erros'].append('cor por nome (%s) na linha %d: use #hex ou variável (o tema escuro não traduz nome)' % (m.group(1), n))
    # data de hoje: toISOString() é o dia de Londres -- aqui vira amanhã às 21h
    for m in re.finditer(r"new Date\(\)\.toISOString\(\)\.(?:slice|substring)\(0,\s*10\)|new Date\(\)\.toISOString\(\)\.split\(", h):
        n = h.count('\n', 0, m.start()) + 1
        r['erros'].append('data de hoje em UTC na linha %d (use rmDiaISO(): às 21h vira o dia seguinte)' % n)
    # versão
    mv = re.search(r"const\s+APP_VER\s*=\s*['\"](v\d+)['\"]", h)
    r['ver'] = mv.group(1) if mv else None
    if not mv:
        r['erros'].append("sem const APP_VER='vNN'")
    # service worker
    swn, sw = sw_de(repo)
    r['sw'] = None
    if not sw:
        r['erros'].append('sem service worker')
    else:
        r['sw'] = md5(corpo_sw(sw))
        if 'RM · SERVICE WORKER PADRÃO' not in sw:
            r['erros'].append(swn + ' não é o service worker padrão')
        mc = re.search(r"const CACHE = '([^']+)'", sw)
        if mv and mc and not mc.group(1).endswith('-' + mv.group(1)):
            r['erros'].append('CACHE do %s (%s) não termina com APP_VER (%s)' % (swn, mc.group(1), mv.group(1)))
        if 'serviceWorker.register' not in h:
            r['erros'].append('service worker não é registrado no index.html')
    # blocos comuns: iguais à FONTE ÚNICA (central_rm/comum), não só entre si
    comum = acha_comum(repo)
    if comum:
        for bl in comum['blocos']:
            if nome in bl.get('exceto', []):
                continue
            try:
                ach = acha_bloco(h, bl['marca'])
            except ValueError as e:
                r['erros'].append('bloco %s: %s' % (bl['nome'], e)); continue
            if not ach:
                if bl.get('obrigatorio', True):
                    r['erros'].append('falta o bloco comum "%s"' % bl['nome'])
            elif h[ach[0]:ach[1]] != comum['texto'][bl['arquivo']]:
                r['erros'].append('bloco "%s" difere de central_rm/comum/%s (rode ferramentas/aplica_comum.py)' % (bl['nome'], bl['arquivo']))
            if ach and bl['arquivo'] in NO_HEAD and not (0 <= ach[0] < h.find('</head>')):
                r['erros'].append('bloco "%s" fora do <head>: %s' % (bl['nome'], NO_HEAD[bl['arquivo']]))
    if comum:
        spans = []
        for bl in comum['blocos']:
            try:
                ach = acha_bloco(h, bl['marca'])
            except ValueError:
                ach = None
            if ach:
                spans.append(ach)
        r['erros'] += codigo_morto(h, spans)
    # as outras páginas inteiras do sistema (ex.: medicao.html da PU) com os
    # mesmos blocos -- fonte e Tema RM obrigatórios
    if comum:
        for pag in paginas_extras(repo):
            hp = ler(os.path.join(repo, pag)) or ''
            for bl in comum['blocos']:
                if nome in bl.get('exceto', []):
                    continue
                try:
                    ach = acha_bloco(hp, bl['marca'])
                except ValueError as e:
                    r['erros'].append('%s: bloco %s: %s' % (pag, bl['nome'], e)); continue
                if not ach:
                    if bl['nome'] in OBRIG_EXTRA:
                        r['erros'].append('%s: falta o bloco comum "%s"' % (pag, bl['nome']))
                elif hp[ach[0]:ach[1]] != comum['texto'][bl['arquivo']]:
                    r['erros'].append('%s: bloco "%s" difere de central_rm/comum/%s (rode ferramentas/aplica_comum.py)' % (pag, bl['nome'], bl['arquivo']))
                if ach and bl['arquivo'] in NO_HEAD and not (0 <= ach[0] < hp.find('</head>')):
                    r['erros'].append('%s: bloco "%s" fora do <head>: %s' % (pag, bl['nome'], NO_HEAD[bl['arquivo']]))
    # a vitrine do padrão visual tem de ser a montagem do molde com os blocos atuais
    pasta = os.path.join(repo, 'comum')
    for nome in (sorted(os.listdir(pasta)) if os.path.isdir(pasta) else []):
        if not nome.endswith('.modelo.html'):
            continue
        v = re.sub(r'<!--COMUM:([\w.-]+)-->', lambda m: ler(os.path.join(pasta, m.group(1))) or '', ler(os.path.join(pasta, nome)))
        final = nome.replace('.modelo.html', '.html')
        if v != ler(os.path.join(pasta, final)):
            r['erros'].append('comum/%s desatualizada (rode ferramentas/aplica_comum.py)' % final)
    # documentos do padrão
    for doc in ('PADRAO_RM.md', 'CLAUDE.md', os.path.join('ferramentas', 'verifica_padrao.py'),
                os.path.join('ferramentas', 'aplica_comum.py'), os.path.join('ferramentas', 'testes', 'roda.js')):
        if not os.path.exists(os.path.join(repo, doc)):
            r['erros'].append('falta ' + doc)
    r['padrao'] = md5(ler(os.path.join(repo, 'PADRAO_RM.md')) or '')
    return r


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(raiz, 'index.html')):
        repos = [raiz]
    else:
        repos = sorted(os.path.join(raiz, d) for d in os.listdir(raiz)
                       if os.path.exists(os.path.join(raiz, d, 'index.html')) and d not in DESCARTADOS)
    res = [analisa(r) for r in repos]
    if len(res) > 1:
        chaves = list(BLOCOS) + ['sw', 'padrao']
        isento = {'barra do alto (52 px)': BARRA_PROPRIA, 'papel (O IMPRESSO)': PAPELARIA_PROPRIA,
                  'login – estilo (rmPortaEstilo)': SEM_LOGIN, 'login – script (rmPortaBloco)': SEM_LOGIN}
        for x in res:
            for k, conj in isento.items():
                if x['nome'] in conj:
                    x['hash'][k] = None
        for k in chaves:
            vals = [x['hash'].get(k) if k in BLOCOS else x.get(k) for x in res]
            vals = [v for v in vals if v]
            if not vals:
                continue
            ref = Counter(vals).most_common(1)[0][0]
            for x in res:
                v = x['hash'].get(k) if k in BLOCOS else x.get(k)
                if v and v != ref:
                    rot = {'sw': 'service worker', 'padrao': 'PADRAO_RM.md'}.get(k, k)
                    x['erros'].append(rot + ' diferente dos outros sistemas')
    total = 0
    for x in res:
        total += len(x['erros'])
        estado = 'OK' if not x['erros'] else '%d erro(s)' % len(x['erros'])
        print('%-27s %s' % (x['nome'], estado))
        for e in x['erros']:
            print('   ✗ ' + e)
        for a in x['avisos']:
            print('   · ' + a)
    print('\n%d sistema(s), %d erro(s).' % (len(res), total))
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
