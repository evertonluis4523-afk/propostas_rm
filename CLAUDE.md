# Sistema da RM Estruturas

Este repositório faz parte dos sistemas da RM Estruturas (publicados pelo
GitHub Pages e abertos dentro da Central RM).

**Antes de qualquer mudança, leia `PADRAO_RM.md`.** Ele é igual em todos os
repositórios e define layout, fonte, cores, marca, login, impressão/PDF,
selo de versão, service worker e publicação. Nada disso se reinventa por
sistema: o bloco que já existe é copiado igual.

Bloco comum (login, barra, selo, impressão, nuvem, fonte, tema...) **não se
edita aqui**: a fonte única é `central_rm/comum/`, aplicada em todos por
`python3 central_rm/ferramentas/aplica_comum.py /pasta-com-todos --sobe-versao`.

Ao terminar:

1. Suba `APP_VER` e o `CACHE` do service worker (mesmo `vNN`).
2. Rode `python3 ferramentas/verifica_padrao.py` (ou apontando para a pasta
   com todos os repositórios). Só publique com **0 erro**.
3. Rode `node ferramentas/testes/roda.js /pasta-com-todos`. Só publique com
   **0 falha**. Defeito corrigido ganha teste.
4. Commit, PR e merge no `main`.

Regra mudou? Ela muda no `PADRAO_RM.md` e nos blocos de **todos** os
sistemas no mesmo trabalho -- nunca em um só.
