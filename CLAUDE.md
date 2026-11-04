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
3. Rode os testes no nível certo (PADRAO_RM 7a), todos em
   `central_rm/ferramentas/testes/roda.js`: mudança num sistema só ->
   `--sistema=<repo>` (nível 1, poucos minutos); bloco comum, padrão ou
   ferramentas -> bateria completa. Só publique com **0 falha**. Defeito
   corrigido ganha teste (só na central_rm).
4. Commit, PR e merge no `main`.
5. **Atualize o Cloudflare Pages** (sem este passo o app desktop não recebe
   a versão nova): rode `bash scripts/site.sh "o que mudou"` ou, se `gh`
   não estiver disponível, rode `python3 ferramentas/monta_site.py` na pasta
   de todos para `rm-sistemas/`, commit e push no main de `rm-sistemas`.
   Só diga que publicou quando o Cloudflare confirmar ou o push estiver feito.

Regra mudou? Ela muda no `PADRAO_RM.md` e nos blocos de **todos** os
sistemas no mesmo trabalho -- nunca em um só.
