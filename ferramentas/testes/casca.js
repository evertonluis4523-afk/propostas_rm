/* CASCA DO PROGRAMA: confere as regras de segurança (electron/regras.js)
   sem abrir o Electron. Roda na montagem do instalador, antes de publicar,
   e dentro da bateria (roda.js). Sai com código 1 se alguma falhar. */
const path = require('path');
const { pathToFileURL } = require('url');
const r = require(path.join(__dirname, '..', '..', 'electron', 'regras.js'));

const falhas = [];
const confere = (ok, msg) => { if (!ok) falhas.push(msg); };

/* 1. o "olho" dos documentos só abre documento */
for (const n of ['nota.pdf', 'FOTO.JPG', 'IMG_0001.HEIC', 'scan.tiff', 'foto.jfif', 'planilha.xlsx', 'contrato.docx', 'planta.dwg', 'nfe.xml', 'pacote.zip'])
  confere(r.podeAbrir(n), 'deveria abrir ' + n);
for (const n of ['nota.exe', 'nota.pdf.exe', 'x.bat', 'x.cmd', 'atalho.lnk', 'x.hta', 'x.js', 'x.vbs', 'x.scr', 'x.ps1', 'x.msi', 'x.html', 'semtipo', ''])
  confere(!r.podeAbrir(n), 'não deveria abrir "' + n + '"');

/* 2. link para o Windows: só site, e-mail e telefone */
for (const u of ['https://rmestruturas.com.br', 'http://x.com/a', 'mailto:a@b.com', 'tel:+5511999999999'])
  confere(r.linkExterno(u), 'deveria abrir fora: ' + u);
for (const u of ['file:///C:/Windows/System32/calc.exe', 'search-ms:query=x', 'ms-msdt:/id', 'javascript:alert(1)', 'smb://x/y', '', null])
  confere(!r.linkExterno(u), 'não deveria abrir fora: ' + u);

/* 3. a janela principal só mostra a própria Central */
const index = path.resolve(__dirname, '..', '..', 'index.html');
const urlIndex = pathToFileURL(index).href;
confere(r.navegacaoInterna(urlIndex, index), 'a Central deveria navegar para ela mesma');
confere(r.navegacaoInterna(urlIndex + '?v=2#sis', index), 'a Central com ?/# deveria valer');
confere(!r.navegacaoInterna(pathToFileURL(path.resolve(__dirname, 'solto.pdf')).href, index), 'arquivo solto não deveria tomar a janela');
confere(!r.navegacaoInterna(pathToFileURL(path.resolve(__dirname, 'pagina.html')).href, index), 'outra página local não deveria tomar a janela');
confere(!r.navegacaoInterna('https://evertonluis4523-afk.github.io/central_rm/', index), 'site de fora não é navegação interna');

/* 4. permissões da janela principal */
for (const p of ['media', 'geolocation', 'midi', 'hid', 'serial', 'usb', 'display-capture'])
  confere(!r.permitePrincipal(p, {}), 'deveria negar ' + p);
for (const p of ['notifications', 'clipboard-read', 'clipboard-sanitized-write', 'fullscreen'])
  confere(r.permitePrincipal(p, {}), 'deveria liberar ' + p);
confere(r.permitePrincipal('openExternal', { externalURL: 'mailto:a@b.com' }), 'mailto deveria abrir');
confere(!r.permitePrincipal('openExternal', { externalURL: 'search-ms:query=x' }), 'search-ms não deveria abrir');

if (falhas.length) { console.log('CASCA: ' + falhas.length + ' falha(s)\n  ' + falhas.join('\n  ')); process.exit(1); }
console.log('CASCA: regras de segurança ok');
