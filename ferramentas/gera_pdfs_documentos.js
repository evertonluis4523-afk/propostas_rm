/* PDFs PRONTOS DA APRESENTAÇÃO E DA FICHA CADASTRAL

   No celular não há como gerar PDF pela janela de imprimir -- o iPhone com o
   sistema instalado na tela de início ignora o imprimir. Então cada
   publicação leva os dois PDFs já prontos em apresentacao/, e no celular o
   "Enviar" compartilha esses arquivos.

   Gera do mesmo jeito que o programa: a página montada pela própria Central,
   copiada sem scripts e impressa sem javascript (o @page de cada documento
   manda: A4 deitado na apresentação, A4 em pé na ficha).

   Uso:  node central_rm/ferramentas/gera_pdfs_documentos.js
   Rode sempre que mudar texto, foto ou logo da apresentação ou da ficha, e
   antes de publicar (a ficha sai com a data do dia em que foi gerada). */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const RAIZ = path.resolve(__dirname, '..');
const SAIDA = path.join(RAIZ, 'apresentacao');
const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.jpg': 'image/jpeg', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.json': 'application/json', '.woff2': 'font/woff2', '.pdf': 'application/pdf' };

const DOCS = [
  { abre: 'rmApresentacao', fecha: 'rmApresFechar', arq: 'Apresentacao-RM-Estruturas.pdf', folhas: '#apx-doc .pg', esperadas: 12 },
  { abre: 'rmFichaCadastral', fecha: 'rmFichaFechar', arq: 'Ficha-cadastral-RM-Estruturas.pdf', folhas: '#ap-doc .folha', esperadas: 2 }
];

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const pg = await ctx.newPage();
  await pg.route('**/*', rq => {
    const u = new URL(rq.request().url());
    if (u.hostname !== 'central.local') return rq.abort();
    const f = path.join(RAIZ, decodeURIComponent(u.pathname.slice(1)) || 'index.html');
    if (!f.startsWith(RAIZ) || !fs.existsSync(f) || !fs.statSync(f).isFile()) return rq.fulfill({ status: 404, body: '' });
    rq.fulfill({ status: 200, contentType: TIPOS[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f) });
  });
  await pg.goto('http://central.local/index.html', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await pg.waitForTimeout(2500);
  const imp = await b.newContext({ javaScriptEnabled: false });
  const folha = await imp.newPage();
  let falhou = false;
  for (const d of DOCS) {
    const n = await pg.evaluate(async (d) => {
      await window[d.abre]();
      await new Promise(r => setTimeout(r, 300));
      const imgs = [...document.querySelectorAll(d.folhas + ' img')];
      if (imgs.some(i => !/^data:/.test(i.getAttribute('src') || ''))) return -1;   // foto fora do documento
      return document.querySelectorAll(d.folhas).length;
    }, d);
    if (n !== d.esperadas) { console.error('ERRO ' + d.arq + ': ' + (n < 0 ? 'foto sem carregar' : n + ' folhas, esperadas ' + d.esperadas)); falhou = true; continue; }
    const html = await pg.evaluate(() => { const c = document.documentElement.cloneNode(true); c.querySelectorAll('script').forEach(s => s.remove()); return '<!DOCTYPE html>' + c.outerHTML; });
    await folha.setContent(html, { waitUntil: 'load' });
    await folha.emulateMedia({ media: 'print' });
    const destino = path.join(SAIDA, d.arq);
    await folha.pdf({ path: destino, preferCSSPageSize: true, printBackground: true });
    await pg.evaluate((d) => window[d.fecha](), d);
    console.log(d.arq + '  ' + d.esperadas + ' folhas  ' + (fs.statSync(destino).size / 1e6).toFixed(1) + ' MB');
  }
  await b.close();
  process.exit(falhou ? 1 : 0);
})();
