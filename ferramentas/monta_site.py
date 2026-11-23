#!/usr/bin/env python3
"""Monta o site único dos sistemas (repositório rm-sistemas).

Uso:  python3 central_rm/ferramentas/monta_site.py /pasta-com-todos /caminho/rm-sistemas

Por que existe: o GitHub Pages monta o site de cada repositório numa fila
do próprio GitHub, e em 19/10/2026 essa fila parou por mais de uma hora --
a versão nova estava gravada e ninguém a recebia. O rm-sistemas é o mesmo
conjunto, num repositório só, servido pelo Cloudflare Pages, que publica a
cada envio sem passar por essa fila. O GitHub Pages de cada sistema continua
no ar, como reserva.

Cada sistema vai na sua pasta, com o nome do repositório (/recibos_rm/,
/central_rm/...), num endereço só: é isso que mantém tema, fundo e
preferências valendo em todos -- eles moram no mesmo endereço, como hoje
no github.io. Vai só o que o site serve: ficam de fora ferramentas,
testes, o programa instalado (electron/build/scripts) e a documentação.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

DESCARTADOS = {'controle_faltas', 'calculo_telha-t-rmica', 'rm-sistemas', 'minhas-contas'}
# pastas e arquivos da raiz de cada repositório que não são o site
# .claude e .impeccable: skills e notas de design do Claude não são o site
FORA_PASTAS = {'.git', '.github', '.claude', '.impeccable', 'ferramentas', 'node_modules', 'electron', 'build', 'scripts', 'dist', 'comum'}
FORA_ARQUIVOS = {'atualizar.bat', 'package.json', 'package-lock.json', '.gitignore', 'sync-info.js'}


def sistemas(raiz):
    return sorted(d for d in os.listdir(raiz)
                  if d not in DESCARTADOS and os.path.isfile(os.path.join(raiz, d, 'index.html')))


def commit_de(pasta):
    try:
        return subprocess.check_output(['git', '-C', pasta, 'rev-parse', '--short', 'HEAD'], text=True).strip()
    except Exception:
        return ''


def data_de(pasta):
    # data do commit publicado (a mesma a cada montagem do mesmo commit)
    try:
        return subprocess.check_output(['git', '-C', pasta, 'log', '-1', '--format=%cs'], text=True).strip()
    except Exception:
        return ''


def extensao_de(pasta):
    # versão da extensão do SketchUp que o Leitor DWG oferece para baixar
    try:
        with open(os.path.join(pasta, 'index.html'), encoding='utf-8') as f:
            html = f.read()
        i = html.find("TLH_EXT_VERSAO='")
        return html[i + 16:html.index("'", i + 16)] if i >= 0 else ''
    except Exception:
        return ''


# PLUGINS E ARQUIVOS PARA BAIXAR (a gaveta "Plugins e arquivos" da Central).
# A lista sai dos próprios arquivos a cada montagem: extensão do SketchUp
# (sketchup/*.rbz, nome e versão do .rb que a registra) e rotina do AutoCAD
# (*.lsp na raiz, versão no RM-VER). Mudou o plugin e publicou, a gaveta já
# mostra a versão nova e o link baixa o arquivo novo -- ninguém mantém lista.
# Aqui só o que o arquivo não diz: para que serve e como instalar.
PLUGINS_TEXTO = {
    'leitor_dwg/sketchup/RM_Coberturas.rbz': (
        'Cobertura e fechamento para o Leitor DWG (aba Telhas) e medidas e esquadrias da chave na mão (aba Chave na mão).',
        'SketchUp › Extensões › Gerenciador de extensões › Instalar extensão, e escolha o arquivo. Reinicie o SketchUp.'),
    'calculadora-pu/sketchup/RM_Estruturas_PU.rbz': (
        'Exporta as linhas de PU do modelo para o 3D do Cálculo PU.',
        'SketchUp › Extensões › Gerenciador de extensões › Instalar extensão, e escolha o arquivo. Reinicie o SketchUp.'),
    'propostas_rm/sketchup/RM_Cenas.rbz': (
        'Exporta as cenas do modelo como imagens para a proposta (Propostas e Contratos).',
        'SketchUp › Extensões › Gerenciador de extensões › Instalar extensão, e escolha o arquivo. Reinicie o SketchUp.'),
    'leitor_dwg/COTAR_BARRAS.lsp': (
        'Cota no AutoCAD cada barra selecionada (cota alinhada), sem os suportes de terça, com a letra no tamanho do desenho (comando COTARBARRAS; RMCBVER mostra a versão).',
        'AutoCAD › APPLOAD, carregue o arquivo e ponha em Conteúdo da inicialização (Startup Suite).'),
    'leitor_dwg/RM-TELHA.lsp': (
        'Desenha e cota no AutoCAD o esboço de telhas que o Leitor DWG lê (comandos TL, TLC, TLS; RMONDE mostra a versão carregada).',
        'AutoCAD › APPLOAD, carregue o arquivo e ponha em Conteúdo da inicialização (Startup Suite).'),
}


def _le(caminho):
    try:
        with open(caminho, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''


def _entre(txt, marca, fim="'"):
    i = txt.find(marca)
    if i < 0:
        return ''
    i += len(marca)
    j = txt.find(fim, i)
    return txt[i:j] if j > i else ''


def rbz_desatualizados(raiz_repo, repo):
    # o .rbz é o que se baixa: se o código da extensão mudou e ele não foi
    # refeito, o link entregaria a versão velha -- aí a montagem para
    import zipfile
    ruins = []
    skp = os.path.join(raiz_repo, 'sketchup')
    if not os.path.isdir(skp):
        return ruins
    for nome in os.listdir(skp):
        if not nome.endswith('.rbz'):
            continue
        try:
            z = zipfile.ZipFile(os.path.join(skp, nome))
            for m in z.namelist():
                f = os.path.join(skp, m)
                if not m.endswith('/') and (not os.path.isfile(f) or open(f, 'rb').read() != z.read(m)):
                    ruins.append(repo + '/sketchup/' + nome + ' (' + m + ')')
        except Exception as e:
            ruins.append(repo + '/sketchup/' + nome + ' (' + str(e) + ')')
    return ruins


def plugins_de(raiz_repo, repo):
    import re
    achados = []
    skp = os.path.join(raiz_repo, 'sketchup')
    if os.path.isdir(skp):
        for nome in sorted(os.listdir(skp)):
            if not nome.endswith('.rbz'):
                continue
            base = nome[:-4]
            reg = _le(os.path.join(skp, base + '.rb'))
            # o .rb que registra a extensão às vezes tem outro nome (RM_Estruturas.rb para RM_Estruturas_PU.rbz)
            if 'SketchupExtension.new' not in reg:
                for outro in sorted(os.listdir(skp)):
                    if outro.endswith('.rb') and 'SketchupExtension.new' in _le(os.path.join(skp, outro)):
                        reg = _le(os.path.join(skp, outro))
                        break
            m = re.search(r"SketchupExtension\.new\(\s*['\"]([^'\"]+)", reg)
            v = re.search(r"\.version\s*=\s*['\"]([^'\"]+)", reg)
            achados.append(('sketchup/' + nome, 'SketchUp', m.group(1) if m else base, v.group(1) if v else ''))
    for nome in sorted(os.listdir(raiz_repo)):
        if nome.lower().endswith('.lsp'):
            txt = _le(os.path.join(raiz_repo, nome))
            m = re.search(r'\(setq RM-(?:[A-Z]+-)?VER "([^"]+)"', txt)
            achados.append((nome, 'AutoCAD', nome[:-4], m.group(1) if m else ''))
    out = []
    for rel, tipo, nome, versao in achados:
        uso, instalar = PLUGINS_TEXTO.get(repo + '/' + rel, ('', ''))
        try:
            data = subprocess.check_output(['git', '-C', raiz_repo, 'log', '-1', '--format=%cs', '--', rel], text=True).strip()
        except Exception:
            data = ''
        out.append({'nome': nome, 'tipo': tipo, 'versao': versao, 'sistema': repo, 'arquivo': repo + '/' + rel,
                    'tamanho': os.path.getsize(os.path.join(raiz_repo, rel)), 'data': data, 'uso': uso, 'instalar': instalar})
    return out


def versao_de(pasta):
    try:
        with open(os.path.join(pasta, 'index.html'), encoding='utf-8') as f:
            html = f.read()
        i = html.find("const APP_VER='")
        return html[i + 15:html.index("'", i + 15)] if i >= 0 else ''
    except Exception:
        return ''


def copia(origem, destino):
    for nome in os.listdir(origem):
        if nome in FORA_PASTAS or nome in FORA_ARQUIVOS or nome.endswith('.md'):
            continue
        o = os.path.join(origem, nome)
        if os.path.isdir(o):
            shutil.copytree(o, os.path.join(destino, nome), ignore=shutil.ignore_patterns('.git', 'node_modules'))
        else:
            shutil.copy2(o, os.path.join(destino, nome))


def monta(raiz, destino):
    raiz = os.path.realpath(raiz)
    ruins = [r for s in sistemas(raiz) for r in rbz_desatualizados(os.path.realpath(os.path.join(raiz, s)), s)]
    if ruins:
        sys.exit('PARADO: extensão do SketchUp mudou e o .rbz não foi refeito -- refaça antes de publicar:\n  ' + '\n  '.join(ruins))
    # limpa tudo menos o .git: o site é sempre remontado do zero, então um
    # arquivo apagado num sistema também some daqui
    os.makedirs(destino, exist_ok=True)
    for nome in os.listdir(destino):
        if nome == '.git':
            continue
        p = os.path.join(destino, nome)
        shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)
    lista = {}
    plugins = []
    for s in sistemas(raiz):
        origem = os.path.realpath(os.path.join(raiz, s))
        os.makedirs(os.path.join(destino, s))
        copia(origem, os.path.join(destino, s))
        lista[s] = {'versao': versao_de(origem), 'commit': commit_de(origem), 'data': data_de(origem)}
        if extensao_de(origem):
            lista[s]['extensao'] = extensao_de(origem)
        plugins += plugins_de(origem, s)
    # página de instalação do programa num endereço curto (/instalar/), sem o
    # nome da conta do GitHub no link que se envia
    inst = os.path.join(raiz, 'central_rm', 'instalar.html')
    if os.path.isfile(inst):
        os.makedirs(os.path.join(destino, 'instalar'))
        shutil.copy2(inst, os.path.join(destino, 'instalar', 'index.html'))
    # a raiz abre a Central
    with open(os.path.join(destino, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
                '<meta http-equiv="refresh" content="0; url=central_rm/">'
                '<title>RM Estruturas</title></head><body>'
                '<script>location.replace("central_rm/"+location.search+location.hash)</script>'
                '<a href="central_rm/">Abrir a RM Central</a></body></html>')
    # o que está publicado aqui, para o programa e a Central saberem se a
    # cópia do Cloudflare está em dia (sem data/hora: o mesmo conteúdo dá o
    # mesmo arquivo, e nada é enviado quando nada mudou)
    with open(os.path.join(destino, 'versoes.json'), 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=1, sort_keys=True)
    # A aba Versões da Central lê o versoes.json também do programa instalado
    # e do endereço do GitHub (outra origem): o Cloudflare só deixa com este
    # cabeçalho. Sem cache, para a lista não ficar atrás da publicação.
    with open(os.path.join(destino, '_headers'), 'w', encoding='utf-8') as f:
        f.write('/versoes.json\n  Access-Control-Allow-Origin: *\n  Cache-Control: no-cache\n'
                '/plugins.json\n  Access-Control-Allow-Origin: *\n  Cache-Control: no-cache\n')
    with open(os.path.join(destino, 'plugins.json'), 'w', encoding='utf-8') as f:
        json.dump(plugins, f, ensure_ascii=False, indent=1, sort_keys=True)
    # O Cloudflare oferece dois caminhos para publicar um repositório: Pages
    # (não precisa de nada) e Workers, que pede este arquivo dizendo onde
    # estão os arquivos do site. Com ele, o mesmo repositório serve aos dois.
    with open(os.path.join(destino, 'wrangler.jsonc'), 'w', encoding='utf-8') as f:
        f.write('{\n  "name": "rm-estruturas",\n  "compatibility_date": "2025-10-01",\n'
                '  "assets": { "directory": "./", "not_found_handling": "404-page" }\n}\n')
    with open(os.path.join(destino, '.assetsignore'), 'w', encoding='utf-8') as f:
        f.write('.git\nwrangler.jsonc\n.assetsignore\nREADME.md\n')
    with open(os.path.join(destino, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('# RM Estruturas — site dos sistemas\n\n'
                'Gerado por `central_rm/ferramentas/monta_site.py` a cada publicação. '
                '**Não editar à mão**: a fonte de cada sistema é o repositório dele.\n')
    return lista


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    r = monta(sys.argv[1], sys.argv[2])
    print('%d sistema(s) montado(s) em %s' % (len(r), sys.argv[2]))
    for k, v in sorted(r.items()):
        print('  %-28s %-6s %s' % (k, v['versao'], v['commit']))
