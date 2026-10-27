# Padrão RM — regras para todos os sistemas

Este arquivo é **igual em todos os repositórios** da RM Estruturas. Ele vale
para os sistemas que já existem e para **qualquer sistema novo**. Antes de
mudar layout, fonte, impressão, login ou publicação, leia a seção correspondente.
Se uma regra precisar mudar, ela muda **aqui e em todos os sistemas juntos**,
nunca em um só.

Conferência automática: `python3 ferramentas/verifica_padrao.py` (roda num
repositório só ou na pasta com todos). Nenhuma publicação sai com erro nele.

Testes automáticos: `node ferramentas/testes/roda.js /pasta-com-todos` (abre
cada sistema num navegador de verdade, no computador e no celular). Nenhuma
publicação sai com teste falhando.

**Blocos comuns têm fonte única:** `central_rm/comum/`. Nenhum bloco comum é
editado dentro de um sistema -- muda o arquivo em `comum/` e roda
`python3 central_rm/ferramentas/aplica_comum.py /pasta-com-todos --sobe-versao`,
que leva o bloco (e este arquivo, o `CLAUDE.md`, as `ferramentas/` e o corpo do
service worker) para todos. O verificador acusa bloco diferente da fonte.

---

## 1. Princípios

- **Um jeito só de fazer cada coisa.** O que já foi resolvido em um sistema é
  copiado (bloco idêntico), não reescrito.
- **Um botão por ação.** Nada de duas saídas para a mesma coisa ("PDF" e
  "Imprimir" separados, "Carregar" depois de escolher, etc.).
- **Nada herdado sem pedir.** Campo abre vazio; sem nome sugerido, sem medida de
  exemplo, sem desenho pronto; `autocomplete="off"` em cadastro de peça/obra.
- **Português do Brasil** em tudo que aparece: datas `dd/mm/aaaa`, números
  `1.234,56`, textos sem jargão técnico.
- **Comentário explica o porquê**, com o caso real que motivou a regra.
- **Sem código morto.** Função que nada chama, estilo de classe que o sistema
  não usa (sobra de quando ele nasceu da cópia de outro) e o logo gravado mais
  de uma vez no mesmo arquivo saem. Uma cópia do logo por arquivo; os outros
  lugares apontam para ela (`RM_ASSINATURA`, ou o `src` da primeira imagem).
  O `verifica_padrao.py` acusa os três. Os blocos comuns ficam de fora: valem
  para todos, e cada sistema usa uma parte deles. Os comentários ficam: são o
  registro do porquê.

## 2. Marca

| Uso | Arquivo / cor |
|---|---|
| Logo completo (timbrado, login, tela) | versão **monocromática** oficial (símbolo + RM + nome) |
| Símbolo no rodapé do papel | símbolo **laranja** `#F24619` |
| Marca d'água | símbolo **escuro** `#141414` |
| Laranja da marca | `#F24619` (destaque, fio do timbrado, traço de seção) |
| Laranja texto/ação | `#D53309` |
| Preto da marca | `#141414` |
| Cinza de apoio | `#6E747C` · faixa de tabela `#F2F4F7` · fio `#eceef1` |

Logo sempre em vetor (SVG/data URI); nunca PNG ampliado. A escrita do logo é
o preto da marca (`#141414`): no escuro o tema a clareia sozinho -- no logo
embutido e no de arquivo (`rm-logo.svg`), teste `logo-em-arquivo-no-escuro`.

## 3. Tela

- **Aparência (Tema RM):** cor, canto, altura, letra e sombra moram UMA vez em
  `central_rm/comum/tema-rm.html` (variáveis `--rm-*`), junto com o botão, o
  campo, o cabeçalho de tabela e o cartão padrão. Vitrine com tudo, e um
  "Experimente" para testar mudança antes de pedir:
  https://evertonluis4523-afk.github.io/central_rm/comum/vitrine.html
  - CSS novo usa as variáveis (`var(--rm-marca)`, `var(--rm-raio)`...), nunca
    um número solto de cor ou canto.
  - Botão usa os nomes da casa: `.btn` (normal), `.btn.primary` (a ação que
    conclui -- um por tela), `.btn.ghost` (secundário), `.btn.danger`,
    `.btn.sm` (dentro de tabela/lista). Os nomes antigos de cada sistema
    (`.btn-act.save`, `.btn-red`, `.btn-sm.red`...) já seguem o mesmo visual.
  - O tema decide a APARÊNCIA; posição, largura e mostrar/esconder continuam
    com o sistema.
  - Status (pago, em aberto, atrasado, pedido) usa ok / aviso / perigo /
    informação, sempre com o fundo suave e o texto forte da mesma cor.
  - Tabela: linha sim, linha não, levemente cinza (`--rm-faixa`), a linha sob
    o mouse com um toque da marca e o fio entre linhas visível. Vem do tema;
    tabela que não quer faixa (grade, calendário) leva a classe `.sem-faixa`.
  - Lista de pessoas, empresas ou obras: a linha abre com a peça de registro,
    `rmRegistro(nome, dados)` (bloco comum `registro.html`): círculo com as
    iniciais (neutro: cinza claro com letra cinza -- colorido ficou gritante), nome
    forte e os dados menores e apagados embaixo. `{classe:'p'}` em lista
    densa. Onde a coluna é estreita demais (a grade do Almoços) fica só a
    faixa, sem iniciais -- nome cortado é pior que nome sem círculo.
- **Nada de nome de pessoa no código.** Nem lista inicial, nem exemplo de
  campo, nem comentário: o arquivo é público. Nome de funcionário mora só na
  nuvem.
- **Fonte:** Satoshi, embutida no próprio HTML (`@font-face` com data URI).
  Nenhuma fonte de fora (Google Fonts etc.).
  Única exceção: a **folha** do Propostas e Contratos (proposta/contrato no
  papel) pode sair em Arial, a fonte dos documentos de orçamento e contrato,
  por escolha em Configurações (o padrão continua Satoshi). A Arial é a do
  computador, não se embute. O Word desses documentos é sempre Arial.
- **Barra do alto:** 52 px de altura em todos os sistemas (bloco "A BARRA DO
  ALTO TEM UMA ALTURA SO'"). Título do sistema à esquerda, selo de versão ao lado.
- **Selo de versão:** `const APP_VER='vNN'` no script + bloco idêntico
  `rmVersaoBloco`, que põe o número ao lado do nome do sistema na barra do
  alto. Sobe a cada publicação. O nome do cache do service worker termina com
  o mesmo `vNN`.
- **Marca na barra:** "RM ESTRUTURAS · NOME DO SISTEMA" montada pelo bloco da
  barra a partir do símbolo vetorial (`window.RM_SIMBOLO` ou equivalente) --
  nunca logo em imagem nem título em duas linhas.
- **Sem e-mail na barra:** o topo não mostra o e-mail de quem está logado --
  dentro da Central todos os sistemas entram com a mesma conta. O registro de
  quem fez cada coisa continua sendo gravado; só não aparece no topo.
- **Sem botão "Sair":** os sistemas não têm opção de sair da conta -- todos
  são usados dentro da Central, que é quem fecha tudo. (A Central mantém o
  dela.)
- **Sem "Tela cheia" nem "Instalar app":** o sistema roda na janela da
  Central; esses botões não fazem nada que ela já não faça.
- **Backup em arquivo fora da barra do alto:** a Central copia sozinha
  todos os dados da nuvem (lista `NOS_DADOS`). Baixar/restaurar em arquivo,
  quando existir, fica em Configurações ou num menu "Mais", nunca à vista.
  **Sistema que grava num nó novo da nuvem entra na `NOS_DADOS` da Central
  no mesmo trabalho** -- senão fica sem backup e ninguém percebe. (Exceção: nó
  que já é histórico, como `orcamentos_versoes`, e nó pessoal que só o dono
  lê, como `users` do app Minhas Contas; e todo nó novo entra também em
  `ferramentas/regras_firebase.json`. As regras são coladas INTEIRAS no
  console: nó de outro app no mesmo Firebase também fica nesse arquivo.)
  O que fica fora de propósito vai em `NOS_FORA_DO_BACKUP`, com o motivo: o
  teste `backup-cobre-todo-o-banco` recusa nó das regras que não esteja numa
  das listas. A cópia roda sozinha no programa do Windows: de 2 em 2 horas,
  ao voltar a internet ou a janela (se a última ficou velha) e ao fechar o
  programa -- ninguém precisa clicar.
  **Arquivo anexado (nota, PDF) não fica só no aparelho:** vai para a nuvem
  num nó à parte (`obras_rm_anexos`, `contas_pagar_anexos`), listado em
  `NOS_ANEXOS`; o IndexedDB é só a cópia local. Teste `contas-anexos-na-nuvem`.
  As imagens das obras do Propostas moram em `propostas_rm/imagens` (dentro
  da regra que já existia) e vão com os anexos; o resto do `propostas_rm` vai
  por partes na `NOS_DADOS`. Imagem é reduzida ao A4 e leva a marca d'água
  (o símbolo, 3,5%) gravada nela. Teste `propostas-imagens`.
- **Gravação na nuvem (Firebase):**
  - **nada grava antes da primeira leitura** do nó; a gravação junta com o
    que está na nuvem (por id) ou manda só o que mudou -- nunca a cópia
    inteira de um aparelho por cima da dos outros;
  - **cadastro com um carimbo de hora só é proibido**: cada aparelho guarda
    como a nuvem estava na última sincronização (por campo) e envia só o que
    mudou nele; campo que apagaria vários registros de uma vez fica segurado
    (freio) e avisa; antes de alterar, a versão anterior fica guardada na
    nuvem (histórico) -- é o que o Orçamento faz;
  - lista de itens com id (cheques, máquinas...) grava numa **transação que
    junta item por item** o que mudou aqui com o que está na nuvem -- nunca
    `set()` do banco inteiro; grade por dia (Almoços) manda só as células
    que mudaram;
  - toda gravação tem tratamento de erro que chega à tela
    (`.catch(e=>rmNuvemErro('o que era', e))`);
  - **nome de campo sem `. # $ / [ ]`** (chave composta junta as partes com
    `~`): o Firebase recusa o pacote INTEIRO, na hora, e nada mais sobe.
    O bloco `rmNuvemErro` (igual em todos) troca o que escapar só na cópia
    enviada e anota em `window.RM_NUVEM_AJUSTES` -- é rede de segurança,
    não desculpa para gravar chave proibida.
- **Data de hoje:** sempre `rmDiaISO()` (bloco comum "Data local"), e data
  `AAAA-MM-DD` vira objeto com `rmDataDe(iso)`. `new Date().toISOString()`
  é o dia de Londres -- aqui vira amanhã às 21h -- e `new Date('AAAA-MM-DD')`
  é o dia anterior aqui. O verificador recusa o primeiro.
- **Lista de sugestões** (escolher peça, obra, pessoa já cadastrada): sempre a
  do Recibos -- cartões claros presos embaixo do campo, o item em destaque no
  tom da marca, setas e Enter --, nunca a lista preta do navegador. Basta o
  `<input list="...">` com o `<datalist>`: o bloco comum
  `comum/lista-suspensa.html` troca o desenho sozinho em todos os sistemas
  (teste `lista-suspensa-padrao`).
- **Contraste e toque:** texto a 4,5:1 (3:1 no grande), botão com pelo menos
  24 px de área de toque, no claro e no escuro (teste `contraste-toque`).
- **Cor só pelo tema** (o escuro é derivado do claro, e só alcança o que está
  escrito numa folha de estilo):
  - campo, botão e caixa têm fundo **e** letra escritos -- o campo sem classe
    recebe os dois do Tema RM; o que fica com a cor do navegador (branco,
    cinza, letra preta) não muda no escuro;
  - cor na **folha de estilo**, não no atributo `style` nem numa variável
    escrita no elemento (`style="--c:..."`): o tema não alcança, e no escuro
    sobra o tom do claro (o "Em andamento" do Obras, o selo de nuvem);
  - situação (pago, em andamento, atrasado) só pela paleta de estado da casa
    (`--rm-ok`, `--rm-aviso`, `--rm-perigo`, `--rm-info`), nunca hex solto;
  - botão cheio com letra branca usa o tom de botão (`--rm-marca`, 4,9:1),
    não a laranja de texto, que clareia no escuro;
  - `@media print,screen` é só para o papel (o recibo branco na tela): o tema
    não traduz esse bloco, e regra da tela que cai ali fica clara no escuro;
  - o bloco do tema mora no `<head>` de toda página (a do sistema e as
    outras, como a Medição da PU): com o escuro gravado ele cobre a página
    na cor do fundo até a tradução ficar pronta. No fim do `<body>` o
    navegador já pintou claro antes -- a tela inteira piscava branca ao
    abrir no escuro (verificador e teste `abre-no-escuro-sem-clarao`, que reabre
    cada página num aparelho lento simulado -- é nele que o clarão aparece);
  - testes `cores-todas-as-telas` (toda tela, aba e janela, escondida ou
    não, no claro e nos três escuros) e `cores-depois-de-usar` (o que só
    nasce com uso: relatório, situação, troca de estado da nuvem).
- **Nome de pessoa na tela e no texto do documento:** "Nome Sobrenome"
  (`titlePt` no Recibos, `nomePt` no Almoços) -- funcionário, terceiro e
  cliente, em lista, título, aviso, busca e corpo do recibo. Formata na
  exibição; o cadastro fica como veio. A linha da assinatura do recibo é em
  caixa alta, em todos. Teste `recibos-nomes-terceiros-clientes`. Nos
  outros sistemas (cliente, fornecedor, emitente) vale a peça comum
  `rmNomePt`, que também mantém as siglas de empresa (LTDA, ME, S/A) e as
  iniciais. Teste `nomes-nome-sobrenome-em-todos`.
- **Ligação entre sistemas não quebra calada:** quem publica dado para outro
  publica junto a situação (o Almoços manda se o mês está fechado), e quem
  recebe avisa antes de fechar (a Folha confere os almoços antes de arquivar
  o pagamento) e mostra de quando é o que leu (a lista de funcionários no
  Almoços). Teste `ligacao-almocos-folha`.
- **Erro chega a quem administra:** o relato de erro dos sistemas vai para a
  nuvem (`central_erros`: só mensagem, onde, pilha e versão, nenhum dado de
  tela) e soma no selo do diagnóstico de quem administra, de todos os
  aparelhos. Teste `central-erros-de-todos-os-aparelhos`.
- **Botão que existe faz alguma coisa:** nada de botão escondido servindo de
  gatilho (quem precisa da ação chama a função), nem botão repetindo outro.
  Nada de informação da empresa escrita na página (inventário, valores):
  ela abre para quem tiver o endereço; o dado mora na nuvem.
- **Tema claro/escuro:** atributo `data-theme` no `<html>`, com o interruptor
  padrão. O escuro tem três intensidades, em `data-tom`: `forte` (quase
  preto), `suave` (grafite) e `nitido` (grafite escuro, com o texto
  principal quase branco e o de apoio um degrau abaixo -- no forte os dois
  saíam quase do mesmo cinza). As chaves comuns são `rm_tema` (claro/escuro)
  e `rm_tom` (forte/suave/nitido); o botão anda claro → suave → nítido →
  escuro, e a Central oferece as quatro em Aparência. Regra que vale para o
  escuro pergunta por `data-theme="escuro"` e vale nas três intensidades.
- **Fundo:** treliça + marca num desenho vetorial só, preso no canto, atrás do
  conteúdo, **fora da impressão**.
- **Celular:** `100dvh`, `env(safe-area-inset-*)`, `touch-action:manipulation`
  (sem zoom de toque duplo), campos com 16 px no iOS (sem zoom ao focar).
  Em 360 px de largura nada fica pela metade fora da tela (fora o que rola
  dentro de uma caixa com rolagem) e nenhum texto cortado com "…" fica sem
  outro jeito de ser lido: no celular ele quebra a linha. Varredura
  `AUD_MODO=celular`.
- Sem calculadora flutuante nem botões soltos por cima do conteúdo.
- **Cursor:** tabela que salva e se redesenha no `change` jogava fora a caixa
  de destino no meio do Tab, e o Tab seguinte ia para o alto da tabela. O
  bloco comum `comum/guarda-foco.html` termina o Tab, o clique e a digitação
  na caixa equivalente da tela nova. Para ele reencontrar a caixa, a linha
  redesenhada tem `data-lid` (ou `data-id`/`data-k`) ou o bloco tem `id`.
  Tela que se redesenha só devolve o cursor a uma caixa se ela **estava**
  com ele.

## 4. Login (porta de entrada)

Blocos idênticos `rmPortaEstilo` + `rmPortaBloco`:

- e-mail lembrado e **mostrado pela metade**, "Lembrar" marcado por padrão;
- foto grande e centralizada; "Não é você?" para trocar de conta;
- senha **nunca** preenchida automaticamente antes de a pessoa tocar no campo
  (Face ID/chaveiro liberados depois do toque).

## 5. Papel (impressão e PDF)

Tudo que imprime segue a mesma papelaria:

- **Timbrado:** logo mono à esquerda; à direita, **duas colunas** separadas
  por um fio fino: **razão social** (negrito) e `CNPJ` | **endereço** (rua) e
  **cidade · UF · CEP**. Fio laranja embaixo e, logo abaixo dele, o **tipo do
  documento em laranja** (maiúscula espaçada), acima do título.
  - Sem o nome fantasia: a logo já diz "RM Estruturas Pré-Fabricadas". Quem
    responde pelo papel é a razão social (Nunes e Kuhn Estruturas Metálicas
    Ltda), em todos os sistemas.
  - Sem telefone nem e-mail: o rodapé já traz telefone, Instagram e site.
  - Cada informação na sua linha (endereço e cidade nunca juntos).
  - No papel, na medida do relatório: texto de 9–9,5 px e logo de ~34–36 px
    de altura, para as duas colunas caberem ao lado da logo numa A4.
  - Marcação: `<div class="tb2"><div class="tb2-c"><div class="tb2-rz">razão</div><div>CNPJ …</div></div><div class="tb2-c"><div>rua</div><div>cidade</div></div></div>` e o tipo em `<div class="tb2-tipo">`.
  - Conferido pelo verificador (CNPJ colado no telefone, nome fantasia no
    timbrado) e pelos testes `timbrado`, `timbrado-recibos` e
    `recibos-pf-papel`.
- **PDF de jsPDF** (Almoços): a Satoshi embutida é recortada e não tem
  × º ª “ ” ‘ ’ • ² ³ ½; o jsPDF apaga o resto da linha quando acha um deles.
  Todo texto passa pela troca do `rmFontePDF` (× → x, º → o...).
  Teste `almocos-pdf-glifo`.
- **Rodapé:** `51 99789-7879 · @rm.estruturas` | `www.rmestruturas.com.br` |
  símbolo laranja; linha de nota abaixo. Fixo em todas as páginas, com
  `body{padding-bottom:16mm;box-decoration-break:clone}` para não cobrir texto.
- **Marca d'água:** símbolo escuro, **28% da largura, no máximo 190 px,
  opacidade 3,5%**, `mix-blend-mode:multiply`.
  Documento cujas imagens já trazem a marca gravada nelas (as imagens da
  obra, no Propostas) não leva a da página: o sistema põe
  `<html class="rm-sem-dagua">` enquanto mostra esse documento. Teste
  `propostas-imagens-pdf-limpo`.
- **Página:** `@page{size:A4;margin:12mm}`; tela, menus e botões fora do papel.
- **Tabelas:** faixa clara só no cabeçalho, fio fino entre linhas; sem moldura
  externa, sem zebra; totais não se repetem por página
  (`tfoot{display:table-row-group}`). Ficha para escrever à mão (ponto PF)
  mantém o fio vertical fino entre as casas; fim de semana em cinza bem
  claro, sem amarelo. Teste `recibos-pf-papel`.
- **Títulos de seção:** caixa alta pequena com traço laranja de 3 px.
- **Escala de letra (uma só):**

  | Onde | px | pt |
  |---|---|---|
  | rótulos e cabeçalho de coluna | 7,5 | 5,6 |
  | linha de apoio (grupo, espessura, observação) | 8 | 6 |
  | corpo da tabela e totais | 9,5 | 7,1 |
  | dados do cabeçalho (data, obra) | 10 | 7,5 |
  | total geral | 13 | 9,8 |

  Observação da linha sai como **texto de apoio** (pequeno, cinza, sem negrito,
  quebra linha), nunca como campo.
- Campo digitado vai para o papel como **texto**, não como `<input>`.

## 6. Botão de impressão

- **Um** botão: **"Imprimir / PDF"** (documentos específicos podem ter nome
  próprio, ex.: "Folha do fabricante (PDF)").
- A saída passa pelo bloco idêntico `rmImpressaoBloco`: no programa instalado e
  dentro da Central pergunta **Imprimir** (janela de impressão do Windows,
  direto na impressora) ou **Salvar PDF** (PDF vetorial, na pasta escolhida --
  abre na última usada -- e aberto no leitor); no navegador
  abre a janela de impressão.
- Proibido botão "⬇ PDF" injetado ao lado do Imprimir.
- Documento que alguém ainda ajusta fora do sistema (proposta e contrato, no
  Propostas e Contratos) tem também **"Baixar Word"**: o .docx sai dos mesmos
  blocos que desenham a folha, então o Word e o PDF nunca dizem coisas
  diferentes. O timbrado da folha montada fica fixo na página como `.head`
  -- assim o cabeçalho padrão não põe um segundo timbrado no papel. Teste
  `propostas-papel-e-word`.
- **Nome do arquivo:** o sistema que sabe o nome do documento define
  `window.rmNomePDF()` (tipo, de quem é e a data do documento -- ex.:
  "Orçamento REFRICOMP - PORTAS 28-09-2026"); o bloco usa esse nome no app,
  na Central e no "Salvar como PDF" do navegador. Sem ele: título da página
  + data de hoje. Teste `nome-pdf`.

## 7. Publicação e service worker

- Cada sistema tem o **service worker padrão** (arquivo idêntico; só mudam
  `CACHE`, `ASSETS` e `PAGINA`): sempre a rede com `cache:'no-cache'`, cache só
  sem internet. Com ele, a versão publicada aparece na próxima abertura.
- O service worker é registrado só em `http(s)`.
- A cada publicação: sobe `APP_VER` e o `CACHE`, confere com o verificador
  (0 erro) e com os testes (0 falha), commit, PR e merge no `main` (o GitHub
  Pages publica do `main`).
- O passo a passo de um pedido (entender, implementar, teste que falha na
  versão antiga, versão, prévia com dados fictícios, verificador, bateria e
  publicação até o Cloudflare) está na skill `rm-nova-funcao`, em
  `central_rm/.claude/skills/`, com os scripts de cada etapa.
- **Dois endereços, o mesmo conteúdo.** Principal: Cloudflare Pages,
  `https://rm-estruturas.pages.dev` -- o repositório `rm-sistemas`, montado
  por `ferramentas/monta_site.py` (todos os sistemas, cada um na sua pasta,
  sem ferramentas/testes/programa/documentação nem as pastas `.claude` e `.impeccable`) e
  enviado logo depois do merge, em toda publicação. Reserva: o GitHub Pages
  de cada repositório.
  Motivo: em 19/10/2026 a fila do GitHub Pages parou por mais de uma hora e
  ninguém recebia a versão nova. Não se edita o `rm-sistemas` à mão.
  - A Central abre os sistemas pelo endereço em que ela foi aberta (`SITE`);
    no programa instalado, o principal.
  - O programa baixa do principal e cai na reserva se ele falhar ou estiver
    com versão mais velha que a do computador (`electron/fontes.js`).
  - A Central se atualiza antes do programa. Por isso ela manda ao programa o
    endereço da **reserva** (o programa até 1.7.x só aceita esse e recusava o
    outro, abrindo a cópia velha); o programa novo usa só o caminho e busca
    no principal. Teste `programa-antigo-com-central-nova`.
  - No endereço novo, a Central traz uma vez as preferências do antigo
    (`central_rm/migra.html`): só aparência e organização da tela, nunca dado
    de sistema; a volta só vai para o site da RM.
  - Endereço gravado de um dos dois sites (o lápis da Central grava o
    endereço inteiro) vale pelo caminho: abre do mesmo site da Central.
  - **Instalar o programa:** o link que se manda é
    `https://rm-estruturas.pages.dev/instalar/` (fonte: `central_rm/instalar.html`,
    copiada pelo `monta_site.py`). O botão vai direto ao instalador mais novo,
    lido da lista de versões; sem ela, à página das versões. Teste `instalar-pagina`.
  - **Link que vai para outra pessoa** (Copiar, WhatsApp, link de instalação)
    sai **sempre** pelo principal, nunca montado de `location`: o endereço do
    GitHub leva o nome da conta (parecido com o e-mail) e aparece na prévia
    do WhatsApp. Hoje: Ficha de EPI e Instalar a RM Central (gaveta "Links
    úteis" do menu da Central) e Contas em aberto (Contas a Pagar). Link novo
    para enviar entra nessa gaveta (`TEL_LINKS`). Teste `central-links-uteis`.
  - Testes `site-unico-montagem`, `programa-duas-fontes`, `central-site-de-origem`,
    `contas-link-curto`.
- Os blocos comuns ficam **copiados dentro de cada index.html** (não num
  arquivo carregado de fora): a cópia offline do programa instalado baixa só o
  index.html, e um arquivo compartilhado com defeito derrubaria todos os
  sistemas ao mesmo tempo. A fonte é única na hora de editar; na hora de rodar,
  cada sistema é inteiro.

## 7a. Testes automáticos

- Ficam em `ferramentas/testes/roda.js` (Node + Playwright, o Firebase de
  verdade carregado do pacote local, sem internet e sem tocar na nuvem real).
- Cada incidente vira teste, para não voltar: sistema abre sem erro (computador
  e celular), chave proibida/undefined não derruba a gravação, o orçamento não
  sobe cadastro velho por cima da nuvem, o freio segura apagão, ninguém grava
  antes de ler a nuvem, a foto da conta chega aos logins, o Leitor abre sem
  internet.
- Correção de defeito novo: primeiro o teste que falha, depois a correção.
- Só roda um grupo: `node ferramentas/testes/roda.js /pasta nome-do-teste`.
- **Varredura de todas as telas** (não roda sozinha; leva de 30 a 60 min):
  `AUD_DIR=/pasta-de-saida AUD_MODO=cliques node ferramentas/testes/roda.js /pasta zz-auditoria`
  abre cada sistema e clica em tudo (abas, linhas, janelas), medindo as
  cores depois de cada clique. `AUD_MODO=efeitos` lista o botão cujo clique
  não faz nada (a tela não muda, nada grava, nada abre, nada baixa, nada
  pergunta); `AUD_MODO=nomes` procura nome em MAIÚSCULAS na tela;
  `AUD_MODO=celular` abre em 360 px e lista o que vaza ou fica cortado; `AUD_SO`
  limita a alguns sistemas. Rodar antes de mudar o tema ou o padrão visual.
- Roda em paralelo (até 4 ao mesmo tempo, um navegador por frente; o
  relatório sai na ordem de sempre, com o tempo de cada teste). Para caçar
  teste instável, um por vez: `RM_TESTES_PARALELO=1`.
- Na Central, o botão **"Atualizar"** descarta as cópias guardadas e recarrega
  as abas abertas.

## 8. Central RM

- Os sistemas abrem dentro da Central em `iframe`. A impressão fala com ela
  pela ponte (`ponte?` / `ponte:sim`, mensagem `rm:'pdf'`).
- Erro de JavaScript do sistema é enviado à Central pelo bloco comum
  `comum/relata-erro.html` (igual em todos), junto com a versão (`APP_VER`).
  O nome do sistema quem põe é a Central, pela aba que o abriu. O relatório
  de melhorias mostra a versão da primeira e da última ocorrência.
- Fundo: o escolhido na Central (padrão, cor da marca e intensidade) vale em
  todos os sistemas — blocos comuns `comum/fundo-estilo.html` (o desenho,
  igual na Central e nos sistemas) e `comum/fundo-central.html` (recebe
  `{rm:'fundo'}` e lê as chaves `rm_fundo*`). Sem escolha gravada fica o
  canto próprio do sistema. Dentro da Central, no tema claro, a margem do
  sistema é branca e a folha é marcada só pelo fio.
  Fundos: Treliça, Grade técnica, Planta industrial, Canto discreto, Trama
  completa, Arcos e Marca. Cores da marca: Laranja, Grafite e Vinho. Fundo
  novo é minimalista (traço fino, sem desenho de obra) e entra pelo chip nas
  Preferências + a regra em `fundo-estilo.html`; fundo ou cor que sai perde
  chip e regra juntos, e quem o tinha gravado cai no primeiro da lista
  (teste `central-fundos-arcos`).
- Movimento (bloco comum `comum/fundo-movimento.html`, igual em todos): nas
  Preferências da Central, "Fundo em movimento" (a obra se montando em 3D
  atrás da tela: estrutura metálica, pavilhão pré-moldado com as placas
  encaixando entre os pilares, ou os dois), "Cotas passando no fundo" (opção
  à parte, não vem mais junto com a montagem) e "Toque ao clicar" (snap de
  CAD). Vêm desligados; a escolha vale para o conjunto pelas chaves
  `rm_mov` (`metalica`/`premoldado`/`alterna`; a antiga `cotas` vale como
  metálica com as cotas), `rm_cotas`, `rm_toque` e pela mensagem
  `{rm:'movimento'}`. Teste `fundo-movimento`. Para com a janela escondida ou com um sistema
  aberto por cima da Central, some com "reduzir movimento", fica fora do
  celular e da impressão -- inclusive do PDF do programa: o bloco de
  impressão tira do clone todo canvas de enfeite (`aria-hidden`) e leva o
  `id` dos demais para a imagem (teste `pdf-sem-fundo-em-movimento`).
- **Desenho em canvas no papel sai em alta:** texto, tabela e logo já vão em
  vetor; o que é desenhado em canvas (vistas 3D do Corte) ia na resolução da
  tela (~96 ppp). Na hora de imprimir, o bloco de impressão dispara
  `rm:alta-resolucao` (escala 3, `window.rmImprimindoAlta`) e quem desenha em
  canvas se redesenha nele -- ~290 ppp no papel. É um aviso próprio, não um
  `resize`: redimensionar um quadro de assinatura apagaria o traço. Sistema
  novo com desenho em canvas escuta esse aviso. Teste `pdf-desenho-em-alta`.
  No celular, onde o PDF do Obras é uma imagem da página, ela sai a 3x e em
  PNG (teste `obras-pdf-celular`).
  O programa (1.7.0 em diante) usa o mesmo bloco como proteção de tela do
  Windows: o instalador deixa o `RM Central.scr` (ligação para o programa,
  `build/installer.nsh`) e `electron/protetor.js` abre a `protetor.html` (o
  papel de parede da RM em vetor) com o bloco tirado do `index.html`. A
  mesma tela com `?papel` (endereço curto `central_rm/papel-de-parede.html`)
  é o papel de parede com movimento, pelo Lively Wallpaper.
- Conta que usa só o próprio sistema (a arquiteta, no Propostas e Contratos)
  entra em `CENTRAL_ENXUTA`: a Central dela não tem o painel da empresa
  (números, gráficos, avisos), o Acompanhamento nem o sino -- só a saudação,
  a agenda e o sistema dela. E ao sair uma conta, o resumo do painel sai
  junto, e as abas de sistema abertas também fecham: a próxima pessoa no
  mesmo programa não vê nada da anterior. Testes `central-enxuta-arquiteta`
  e `central-troca-de-conta-fecha-abas`.
- Painel da Central: a tela inicial tem o "Resumo da semana" (o que entra
  e sai na semana e os pontos de atenção) e os Indicadores (período com
  comparação ao anterior, fluxo de caixa de 8 semanas, funil das propostas,
  recebimento das obras, a pagar, PU, compras por categoria); a gaveta
  lateral é "O que fazer hoje", só com o que pede ação. Cor com significado
  fixo: verde bom, laranja atenção, vermelho problema, azul informação.
  O que os sistemas fazem para isso:
  - o Propostas grava um resumo leve de cada proposta em
    `propostas_rm/resumo` (situação, valor, datas, cliente; a lixeira fica
    de fora) e a data em que fechou (`aprovadaEm`); a Central lê só isso;
  - o Compras exige a categoria da compra;
  - a Central abre um sistema já filtrado pela mensagem
    `{rm:'filtro', filtro:'...'}` (`vencidos` no Cheques, `sem-categoria` no
    Compras); sistema que não conhece o filtro só abre normal.
  Testes `central-indicadores` e `indicadores-sistemas`.
- "Meus resultados" (Central, só na conta do dono): horas e valores
  economizados com os sistemas, contados sozinhos do que cada um registrou.
  Cada atividade tem o tempo de antes (Word, Excel, papel) e o tempo no
  sistema; horas = vezes × (antes − no sistema); a hora vale salário ÷
  horas do mês, tudo editável em "Valores de referência". Mais a multa
  evitada (estimativa, pode desligar) e os cheques vencidos depositados.
  O período em curso aparece como parcial (sem comparação). Nós:
  `central_resultados` (só o dono lê e grava: a configuração e a contagem
  de cada mês fechado, que não diminui se algo for apagado depois) e
  `recibos_resultados` (o Recibos publica só a contagem do mês: recibos,
  terceiros, rescisões, cartões PF e fichas de EPI -- nenhum nome nem
  valor). O Propostas leva no resumo quando a proposta foi criada (`cr`) e
  as datas das revisões (`rv`); o Leitor DWG grava em
  `corte_estruturas/resumo` quantos detalhamentos houve por mês (cada obra
  uma vez); o Estoque de Máquinas grava em `maquinas_rm/resumo` as
  conferências, movimentos e termos do mês (e o Leitor, os projetos de
  planificação, em `corte_estruturas/resumo/pln`). O Recibos conta também
  ficha de admissão, entrevista, assiduidade e banco de horas, e marca em
  `recibos_resultados/_emitidos` cada documento do RH aberto para imprimir;
  o Pré-moldados marca cada cálculo impresso em `pre_moldados/resumo`; as
  Etiquetas, cada lote em `rm_documentos/etiquetas` (um por documento e
  dia, só a marca). A Central lê ainda a estrutura metálica, os documentos
  arquivados, os pedidos de esquadrias, as imagens das propostas e os
  lembretes do dono. A espera pela cotação dos
  fornecedores (antes do banco de preços) conta em dias de prazo, não em
  horas. Atividade nova entra na lista `ATIV` da Central, sempre com uma
  fonte que se conta sozinha. Testes `central-meus-resultados`,
  `central-meus-resultados-fontes`, `recibos-publica-resultados`,
  `corte-publica-resultados`, `maquinas-publica-resultados`,
  `central-meus-resultados-todas-as-fontes` e `fontes-publicam-resultados`.
- Salvos do Orçamento RM: a lista e, ao lado, a prévia do orçamento
  escolhido (cabeçalho, itens, fretes, desconto, total, chave na mão,
  esquadrias), sem trocar o orçamento aberto; "Editar orçamento" abre na
  tela principal e "Revisar" abre como nova revisão. Teste
  `orcamento-salvos-previa`.
- A cópia automática (backup) só roda com a conta que lê o banco inteiro
  (a do dono). Com outra conta no programa ela espera, sem marcar falha e
  sem gravar cópia pela metade. Teste `backup-pagina-ao-fechar-e-atrasado`.
- Trocar de sistema aberto: Ctrl+Tab / Ctrl+Shift+Tab, Alt+→ / Alt+← e
  Ctrl+1…9. Com o cursor dentro do sistema, o bloco comum
  `comum/atalhos-central.html` devolve a tecla à Central (`{rm:'atalho'}`).
  Nenhum sistema usa essas teclas para outra coisa.
- Programa instalado (Electron): versão em `package.json`; IPC novos exigem
  rodar `atualizar.bat` uma vez. Desde a 1.5.0 o programa tem: uma janela só
  (abrir de novo traz a aberta para a frente), botão direito com
  Recortar/Copiar/Colar e corretor pt-BR, Ctrl+F (barra própria por cima da
  janela), F5/Ctrl+R recarregando só o sistema aberto e tela que se recupera
  sozinha se cair. Antes do F5 a Central pergunta ao sistema `{rm:'sujo?'}`
  (bloco `atalhos-central.html`) e confirma se houver algo digitado sem
  gravar. Mudou `electron/` ou o Electron: rodar
  `xvfb-run -a node ferramentas/testes/programa.js` (abre o programa de
  verdade) e só publicar com 0 falha.
- O programa se atualiza sozinho (1.5+): `.github/workflows/instalador.yml`
  monta o instalador numa máquina Windows do GitHub quando `electron/` ou o
  `package.json` mudam, e publica no repositório público
  `rm-central-instalador` (só os .exe). O programa confere a cada 4 horas,
  baixa em segundo plano e a Central avisa "Reiniciar e atualizar"; fechar
  também instala. Versão = os dois primeiros números do `package.json` + o
  número da montagem (1.5.101, 1.5.102...). Segredo `RM_INSTALADOR_TOKEN` no
  `central_rm`. O `atualizar.bat` continua funcionando (monta sem publicar).
- Atalho "RM Central" na área de trabalho e no menu Iniciar: antes só a
  primeira instalação criava, e um PC ficou sem o ícone. Agora o instalador
  recria os atalhos ao ser rodado de novo (`createDesktopShortcut: "always"`
  no `package.json`), e o `build/installer.nsh` recria o da área de trabalho
  também nas atualizações automáticas, se tiver sumido. O atalho vai para o
  usuário do Windows que instalou: instale logado no usuário de quem vai usar
  (teste `instalador-atalho-sempre`).

## 9. Sistema novo — checklist

1. Colar uma vez os blocos de `central_rm/comum/` (fonte Satoshi, Tema RM,
   barra do alto, tema, `rmPortaEstilo`/`rmPortaBloco`, papelaria "O IMPRESSO",
   `rmImpressaoBloco`, selo, nuvem) e o relato de erro à Central; dali em
   diante quem os mantém é o `aplica_comum.py`.
2. Copiar o `sw.js` padrão e ajustar só `CACHE`, `ASSETS`, `PAGINA`.
3. `APP_VER` + bloco `rmVersaoBloco` (selo na barra do alto).
4. Um botão "Imprimir / PDF".
5. Rodar `aplica_comum.py` (leva este `PADRAO_RM.md`, o `CLAUDE.md` e as
   `ferramentas/`).
6. Rodar o verificador (0 erro) e os testes (0 falha). Só então publicar.
