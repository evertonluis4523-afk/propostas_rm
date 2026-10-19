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
FORA_PASTAS = {'.git', '.github', 'ferramentas', 'node_modules', 'electron', 'build', 'scripts', 'dist', 'comum'}
FORA_ARQUIVOS = {'atualizar.bat', 'package.json', 'package-lock.json', '.gitignore', 'sync-info.js'}


def sistemas(raiz):
    return sorted(d for d in os.listdir(raiz)
                  if d not in DESCARTADOS and os.path.isfile(os.path.join(raiz, d, 'index.html')))


def commit_de(pasta):
    try:
        return subprocess.check_output(['git', '-C', pasta, 'rev-parse', '--short', 'HEAD'], text=True).strip()
    except Exception:
        return ''


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
    # limpa tudo menos o .git: o site é sempre remontado do zero, então um
    # arquivo apagado num sistema também some daqui
    os.makedirs(destino, exist_ok=True)
    for nome in os.listdir(destino):
        if nome == '.git':
            continue
        p = os.path.join(destino, nome)
        shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)
    lista = {}
    for s in sistemas(raiz):
        origem = os.path.realpath(os.path.join(raiz, s))
        os.makedirs(os.path.join(destino, s))
        copia(origem, os.path.join(destino, s))
        lista[s] = {'versao': versao_de(origem), 'commit': commit_de(origem)}
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
