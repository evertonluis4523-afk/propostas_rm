/* TESTE DO PROGRAMA INSTALADO (Electron de verdade, não o navegador).
   Abre a Central pelo electron/main.js, numa tela virtual, e confere o que
   só existe no programa: uma janela só, botão direito, Ctrl+F, F5 e a tela
   que se recupera sozinha depois de cair.

   Uso (Linux, precisa do Electron instalado em central_rm/node_modules):
     npm install --no-save electron@<versão do package.json>
     xvfb-run -a node ferramentas/testes/programa.js
   Fora da bateria comum de propósito: baixar o Electron (~100 MB) a cada
   publicação não vale; roda quando o main.js/preload.js mudam. */
const path = require('path');
const fs = require('fs');
const os = require('os');
const cp = require('child_process');
const { _electron } = require('playwright');

const RAIZ = path.resolve(__dirname, '..', '..');
const EXE = require(path.join(RAIZ, 'node_modules', 'electron'));
let ok = 0, falha = 0;
const confere = (nome, cond, det) => { if (cond) { ok++; console.log('  ✓ ' + nome); } else { falha++; console.log('  ✗ ' + nome + (det ? '  — ' + det : '')); } };
const esp = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const dados = fs.mkdtempSync(path.join(os.tmpdir(), 'rm-programa-'));
  const args = ['--no-sandbox', '--user-data-dir=' + dados, RAIZ];
  const app = await _electron.launch({ executablePath: EXE, args, cwd: RAIZ, timeout: 60000 });
  const pg = await app.firstWindow();
  await pg.waitForLoadState('domcontentloaded'); await esp(2500);
  /* sem internet aqui: o Firebase vem do pacote local (o mesmo da bateria) */
  const FB = path.join(__dirname, '.libs', 'firebase', 'package');
  await app.evaluate(({ protocol, net, BrowserWindow }, FB) => {
    const fs = process.mainModule.require('fs'), path = process.mainModule.require('path');
    protocol.handle('https', (req) => {
      const m = new URL(req.url).pathname.match(/firebasejs\/[^/]+\/(firebase-[a-z-]+\.js)$/);
      if (m && fs.existsSync(path.join(FB, m[1]))) return new Response(fs.readFileSync(path.join(FB, m[1])), { headers: { 'content-type': 'text/javascript' } });
      return net.fetch(req, { bypassCustomProtocolHandlers: true });
    });
    BrowserWindow.getAllWindows()[0].webContents.reload();
  }, FB);
  await esp(3500);
  const erros = []; pg.on('pageerror', e => erros.push(e.message));
  console.log('\n== programa (Electron ' + await app.evaluate(() => process.versions.electron) + ')');

  // a tela de login some para os testes (não há nuvem aqui)
  /* tecla pelo caminho do Electron (sendInputEvent), que passa pelo
     before-input-event como uma tecla de verdade -- a do Playwright não passa */
  const tecla = (k, mods) => app.evaluate(({ BrowserWindow }, [k, mods]) => {
    const wc = BrowserWindow.getAllWindows()[0].webContents;
    wc.sendInputEvent({ type: 'keyDown', keyCode: k, modifiers: mods || [] });
    wc.sendInputEvent({ type: 'keyUp', keyCode: k, modifiers: mods || [] });
  }, [k, mods]);
  const semPorta = () => pg.evaluate(() => { document.querySelectorAll('#lock-screen').forEach(e => e.style.setProperty('display', 'none', 'important')); });
  await semPorta();

  // 1) uma janela só: a segunda abertura sai na hora e não cria janela
  const t0 = Date.now();
  const seg = cp.spawn(EXE, args, { stdio: 'ignore' });
  const saiu = await new Promise(r => { const t = setTimeout(() => r(null), 15000); seg.on('exit', c => { clearTimeout(t); r(c); }); });
  const janelas = await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows().length);
  confere('abrir de novo não cria um segundo programa', saiu === 0 && janelas === 1, JSON.stringify({ saiu, janelas, ms: Date.now() - t0 }));

  // 2) botão direito: guarda o menu que seria mostrado
  await app.evaluate(({ Menu }) => { const orig = Menu.buildFromTemplate; global.__menus = []; Menu.buildFromTemplate = (t) => { global.__menus.push(t.map(i => i.label || i.type)); const m = orig(t); m.popup = () => {}; return m; }; });
  await pg.evaluate(() => { const i = document.createElement('input'); i.id = 'zzCampo'; i.value = 'texto de teste'; i.style.cssText = 'position:fixed;left:300px;top:300px;width:200px;z-index:99999'; document.body.appendChild(i); i.focus(); i.select(); });
  await pg.click('#zzCampo', { button: 'right' }); await esp(400);
  const menus = await app.evaluate(() => global.__menus);
  const m = menus[menus.length - 1] || [];
  confere('botão direito numa caixa: Recortar, Copiar, Colar, Selecionar tudo', ['Recortar', 'Copiar', 'Colar', 'Selecionar tudo'].every(x => m.includes(x)), JSON.stringify(menus));
  const linguas = await app.evaluate(({ session }) => session.defaultSession.getSpellCheckerLanguages());
  confere('corretor ortográfico ligado em português', linguas.includes('pt-BR'), JSON.stringify(linguas));

  // 3) Ctrl+F: abre a barra por cima, acha e conta, Esc fecha
  await pg.evaluate(() => { const d = document.createElement('div'); d.id = 'zzTexto'; d.textContent = 'parafuso autobrocante · parafuso sextavado · parafuso'; d.style.cssText = 'position:fixed;left:300px;top:360px;z-index:99999;background:#fff'; document.body.appendChild(d); });
  await pg.click('#zzTexto'); await tecla('f', ['control']); await esp(800);
  const aberta = await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].contentView.children.length);
  const barraWc = async (js) => app.evaluate(({ webContents }, js) => { const b = webContents.getAllWebContents().find(w => w.getURL().startsWith('data:')); return b ? b.executeJavaScript(js) : 'sem barra'; }, js);
  await barraWc("var t=document.getElementById('t');t.value='parafuso';t.dispatchEvent(new Event('input'));1");
  await esp(900);
  const conta = await barraWc("document.getElementById('n').textContent");
  await barraWc("document.getElementById('t').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));1"); await esp(600);
  const conta2 = await barraWc("document.getElementById('n').textContent");
  await barraWc("document.getElementById('t').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));1"); await esp(500);
  const fechada = await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].contentView.children.length);
  confere('Ctrl+F abre a barra de procurar por cima da tela', aberta === 1, 'filhos: ' + aberta);
  // começa de onde está o cursor (como no Chrome) e o Enter anda um, dando a volta
  const ord = s => { const x = /^(\d+) de 3$/.exec(s || ''); return x ? +x[1] : 0; };
  confere('acha e conta ("x de 3"), Enter vai ao próximo', ord(conta) > 0 && ord(conta2) === ord(conta) % 3 + 1, JSON.stringify({ conta, conta2 }));
  confere('Esc fecha a barra', fechada === 0, 'filhos: ' + fechada);

  // 4) F5 com um sistema aberto: recarrega só ele; com algo digitado, pergunta antes
  const bloco = fs.readFileSync(path.join(RAIZ, 'comum', 'atalhos-central.html'), 'utf8');
  await pg.evaluate((bloco) => {
    const lay = document.createElement('div'); lay.className = 'iframe-layer'; lay.id = 'layer-zzsis';
    const f = document.createElement('iframe'); f.src = 'data:text/html;charset=utf-8,' + encodeURIComponent(bloco + '<input id="c"><script>window.__vivo=Math.random()<\/script>');
    lay.appendChild(f); document.querySelector('.content, main, body').appendChild(lay);
    openTabs.push({ id: 'zzsis', name: 'Sistema Teste', cat: 'OUTROS', icon: 'ext' }); activateTab('zzsis');
  }, bloco);
  await esp(800);
  const quadro = () => pg.frames().find(fr => fr.url().startsWith('data:'));
  await quadro().evaluate(() => { window.__marca = 1; document.getElementById('c').focus(); });
  await tecla('F5'); await esp(900);
  const semPergunta = await pg.evaluate(() => !document.querySelector('.dlg-fundo'));
  const recarregou = await quadro().evaluate(() => !window.__marca).catch(() => 'erro');
  confere('F5 sem nada digitado recarrega só o sistema, sem perguntar', semPergunta && recarregou === true, JSON.stringify({ semPergunta, recarregou }));
  await quadro().evaluate(() => { window.__marca = 2; const c = document.getElementById('c'); c.focus(); });
  await pg.keyboard.type('meio digitado');
  await tecla('F5'); await esp(900);
  const pergunta = await pg.evaluate(() => { const d = document.querySelector('.dlg-fundo'); return d ? d.textContent : ''; });
  const aindaLa = await quadro().evaluate(() => window.__marca === 2 && document.getElementById('c').value);
  confere('com algo digitado, o F5 pergunta antes e não perde nada', /Recarregar Sistema Teste\?/.test(pergunta) && aindaLa === 'meio digitado', JSON.stringify({ pergunta: pergunta.slice(0, 80), aindaLa }));
  await pg.click('.dlg-fundo [data-ok]'); await esp(900);
  const depois = await quadro().evaluate(() => window.__marca == null && document.getElementById('c').value === '');
  confere('confirmando, recarrega', depois === true, String(depois));

  // 5) o PDF vetorial (o que o programa já fazia) continua saindo no Electron novo
  const pdf = path.join(dados, 'teste.pdf');
  await app.evaluate(({ dialog }, pdf) => { dialog.showSaveDialog = async () => ({ canceled: false, filePath: pdf }); }, pdf);
  const rPdf = await pg.evaluate(() => window.rmDesktop.salvarPDF('<!doctype html><html><head><style>@page{size:A4;margin:12mm}</style></head><body><h1>Relatório de teste</h1><p>Texto vetorial.</p></body></html>', 'teste')).catch(e => ({ erro: e.message }));
  await esp(500);
  const cab = fs.existsSync(pdf) ? fs.readFileSync(pdf).slice(0, 5).toString() : '';
  confere('PDF vetorial do relatório continua saindo', cab === '%PDF-' && fs.statSync(pdf).size > 1000, JSON.stringify({ rPdf, cab }));

  // 6) programa novo baixado pelo atualizador: aviso com "Reiniciar e atualizar"
  const est = await pg.evaluate(() => window.rmDesktop.programaEstado());
  await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].webContents.send('rm:programa-novo', { versao: '1.5.103' }));
  await esp(500);
  const avisoNovo = await pg.evaluate(() => { const d = document.getElementById('aviso-programa-novo'); return d ? d.textContent : ''; });
  confere('versão nova do programa: aviso "Reiniciar e atualizar"', /1\.5\.103/.test(avisoNovo) && /Reiniciar e atualizar/.test(avisoNovo) && est && est.automatico === false, JSON.stringify({ est, avisoNovo }));
  await pg.evaluate(() => { const d = document.getElementById('aviso-programa-novo'); if (d) d.remove(); });

  // 7) a tela cai: o programa recarrega sozinho e avisa
  await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].webContents.forcefullyCrashRenderer());
  await esp(5000);
  // a página de antes morreu com o processo: lê pela janela, no Electron
  const aviso = String(await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].webContents
    .executeJavaScript("(document.getElementById('rm-toasts')||{}).textContent||''")).catch(e => 'erro ' + e.message));
  confere('tela que cai volta sozinha, com aviso', /travado e foi recarregada/.test(aviso), aviso.slice(0, 120));

  confere('sem erro na página', !erros.length, erros.join(' | '));
  await app.close();
  try { fs.rmSync(dados, { recursive: true, force: true }); } catch (e) {}
  console.log('\n' + ok + ' ok, ' + falha + ' falha(s).' + (falha ? ' NÃO publique.' : ''));
  process.exit(falha ? 1 : 0);
})().catch(e => { console.log('  ✗ quebrou: ' + (e && e.stack || e)); process.exit(1); });
