// e2e.js — drive the gallery in headless Chrome (CDP): hydration, counter,
// tabs, dialog, toast. GALLERY_URL overrides the target (e.g. the live site).
const CDP = require('/home/jarancibia/.nvm/versions/node/v24.3.0/lib/node_modules/chrome-remote-interface');
const { spawn } = require('child_process');
const chrome = spawn('/usr/bin/google-chrome', ['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9781','about:blank'], { stdio:'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await sleep(1200);
  const c = await CDP({ port: 9781 });
  const { Page, Runtime } = c;
  await Page.enable(); await Runtime.enable();
  const errs = [];
  Runtime.exceptionThrown(e => errs.push(e.exceptionDetails.text + ' ' + (e.exceptionDetails.exception?.description || '').slice(0,200)));
  const URL = process.env.GALLERY_URL || 'http://localhost:48124/';
  await Page.navigate({ url: URL }); await Page.loadEventFired(); await sleep(600);
  const ev = async (x) => (await Runtime.evaluate({ expression: x, returnByValue: true })).result.value;

  const r = {};
  r.count0 = await ev(`document.querySelector('[data-s="count"]').textContent`);
  await ev(`document.querySelector('[data-action="bump"]').click()`); await ev(`document.querySelector('[data-action="bump"]').click()`); await ev(`document.querySelector('[data-action="bump"]').click()`);
  await sleep(120);
  r.count3 = await ev(`document.querySelector('[data-s="count"]').textContent`);
  await ev(`document.querySelector('[data-action="reset"]').click()`); await sleep(100);
  r.countReset = await ev(`document.querySelector('[data-s="count"]').textContent`);

  r.panel0 = (await ev(`document.querySelector('[data-s="panel"]').textContent`)).slice(0, 30);
  await ev(`document.querySelectorAll('#tabs [data-action="tab"]')[1].click()`); await sleep(120);
  r.panel1 = (await ev(`document.querySelector('[data-s="panel"]').textContent`)).slice(0, 30);
  r.tab1Active = await ev(`document.querySelectorAll('#tabs button')[1].className.includes('border-stone-900')`);
  r.tab0Idle = await ev(`document.querySelectorAll('#tabs button')[0].className.includes('border-transparent')`);

  r.dlgHidden = await ev(`document.getElementById('dlg').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="dlg_open"]').click()`); await sleep(100);
  r.dlgOpen = await ev(`!document.getElementById('dlg').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="dlg_close"]').click()`); await sleep(100);
  r.dlgClosed = await ev(`document.getElementById('dlg').classList.contains('hidden')`);

  r.drwHidden = await ev(`document.getElementById('drw').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="drw_open"]').click()`); await sleep(100);
  r.drwOpen = await ev(`!document.getElementById('drw').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="drw_close"]').click()`); await sleep(100);
  r.drwClosed = await ev(`document.getElementById('drw').classList.contains('hidden')`);

  r.calMonth0 = await ev(`document.querySelector('#cal span.font-semibold').textContent`);
  await ev(`document.querySelector('[data-action="cal_next"]').click()`); await sleep(100);
  r.calMonth1 = await ev(`document.querySelector('#cal span.font-semibold').textContent`);
  await ev(`document.querySelector('#cal [data-action="cal_pick"][data-arg="20260803"]').click()`); await sleep(80);
  await ev(`document.querySelector('#cal [data-action="cal_pick"][data-arg="20260812"]').click()`); await sleep(80);
  r.calRange = await ev(`document.querySelector('#cal p').textContent`);
  r.calInked = await ev(`document.querySelector('#cal [data-arg="20260812"]').className.includes('bg-stone-900')`);
  r.calWashed = await ev(`document.querySelector('#cal [data-arg="20260807"]').className.includes('bg-stone-100')`);

  // command palette: button toggle, filter, action, escape
  r.palHidden = await ev(`document.getElementById('pal').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="palette"]').click()`); await sleep(100);
  r.palOpen = await ev(`!document.getElementById('pal').classList.contains('hidden')`);
  await ev(`const inp = document.querySelector('[data-palette-input]'); inp.value = 'drawer'; inp.dispatchEvent(new Event('input', {bubbles: true}))`); await sleep(100);
  r.palFiltered = await ev(`[...document.querySelectorAll('#pal [data-item]')].filter(el => !el.classList.contains('hidden')).length`);
  await ev(`[...document.querySelectorAll('#pal [data-item]')].find(el => !el.classList.contains('hidden')).click()`); await sleep(100);
  r.palOpenedDrawer = await ev(`!document.getElementById('drw').classList.contains('hidden')`);
  await ev(`document.querySelector('[data-action="drw_close"]').click()`); await sleep(80);
  await ev(`document.querySelector('[data-action="palette_close"]')?.click(); document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}))`); await sleep(100);
  r.palClosed = await ev(`document.getElementById('pal').classList.contains('hidden')`);

  // slider live readout via data-input delegation
  await ev(`const sl = document.querySelector('[data-input="slider_set"]'); sl.value = 72; sl.dispatchEvent(new Event('input', {bubbles: true}))`); await sleep(100);
  r.sliderVal = await ev(`document.querySelector('[data-s="slider_val"]').textContent`);

  // rating re-render
  await ev(`document.querySelector('#rating [data-arg="5"]').click()`); await sleep(100);
  r.stars5 = await ev(`[...document.querySelectorAll('#rating [data-action="rate"]')].filter(el => el.className.includes('text-amber-500')).length`);

  // chips removal
  r.chips0 = await ev(`document.querySelectorAll('#chips [data-action="chip_del"]').length`);
  await ev(`document.querySelector('#chips [data-action="chip_del"]').click()`); await sleep(100);
  r.chips1 = await ev(`document.querySelectorAll('#chips [data-action="chip_del"]').length`);

  // banner dismiss
  await ev(`document.querySelector('[data-action="banner_close"]').click()`); await sleep(80);
  r.bannerGone = await ev(`document.getElementById('top-banner').classList.contains('hidden')`);

  // toast stack: three notifies -> three stacked toasts; dismiss one; auto-expire
  await ev(`document.querySelector('[data-action="notify"]').click()`); await sleep(60);
  await ev(`document.querySelector('[data-action="notify"]').click()`); await sleep(60);
  await ev(`document.querySelector('[data-action="notify"]').click()`); await sleep(100);
  r.toasts3 = await ev(`document.querySelectorAll('#toasts [data-action="toast_dismiss"]').length`);
  await ev(`document.querySelector('#toasts [data-action="toast_dismiss"]').click()`); await sleep(100);
  r.toasts2 = await ev(`document.querySelectorAll('#toasts [data-action="toast_dismiss"]').length`);
  await sleep(2700);
  r.toasts0 = await ev(`document.querySelectorAll('#toasts [data-action="toast_dismiss"]').length`);

  // combobox: focus opens, typing filters, click picks
  await ev(`document.querySelector('[data-combo-input]').click()`); await sleep(80);
  r.comboOpen = await ev(`!document.querySelector('[data-combo-list]').classList.contains('hidden')`);
  await ev(`const ci = document.querySelector('[data-combo-input]'); ci.value = 'frank'; ci.dispatchEvent(new Event('input', {bubbles: true}))`); await sleep(80);
  r.comboFiltered = await ev(`[...document.querySelectorAll('[data-combo-opt]')].filter(el => !el.classList.contains('hidden')).length`);
  await ev(`[...document.querySelectorAll('[data-combo-opt]')].find(el => !el.classList.contains('hidden')).click()`); await sleep(80);
  r.comboValue = await ev(`document.querySelector('[data-combo-input]').value`);
  r.comboClosed = await ev(`document.querySelector('[data-combo-list]').classList.contains('hidden')`);

  // sortable data table: initial asc by app; click reqs -> numeric asc; again -> desc
  r.sortFirst0 = await ev(`document.querySelector('#dtable tbody tr td').textContent`);
  await ev(`document.querySelector('#dtable [data-action="sort_by"][data-arg="2"]').click()`); await sleep(100);
  r.sortNumAsc = await ev(`document.querySelector('#dtable tbody tr td').textContent`);
  await ev(`document.querySelector('#dtable [data-action="sort_by"][data-arg="2"]').click()`); await sleep(100);
  r.sortNumDesc = await ev(`document.querySelector('#dtable tbody tr td').textContent`);
  r.errors = errs;
  // dark mode: emulate prefers-color-scheme dark, reload, check computed colors
  await c.Emulation.setEmulatedMedia({ features: [{ name: 'prefers-color-scheme', value: 'dark' }] });
  await Page.navigate({ url: URL }); await Page.loadEventFired(); await sleep(500);
  r.darkBody = await ev(`getComputedStyle(document.body).backgroundColor`);
  r.darkCard = await ev(`getComputedStyle(document.querySelector('#sec-buttons section')).backgroundColor`);

  console.log(JSON.stringify(r, null, 1));
  await c.close(); chrome.kill();
  const pass = r.count0==='0' && r.count3==='3' && r.countReset==='0' && r.panel0!==r.panel1 &&
    r.tab1Active && r.tab0Idle && r.dlgHidden && r.dlgOpen && r.dlgClosed && r.drwHidden && r.drwOpen && r.drwClosed &&
    r.calMonth0 === 'July 2026' && r.calMonth1 === 'August 2026' &&
    r.calRange.includes('2026-08-03') && r.calRange.includes('2026-08-12') && r.calInked && r.calWashed &&
    r.palHidden && r.palOpen && r.palFiltered === 1 && r.palOpenedDrawer && r.palClosed &&
    r.sliderVal === '72%' && r.stars5 === 5 && r.chips0 === 4 && r.chips1 === 3 && r.bannerGone &&
    r.toasts3 === 3 && r.toasts2 === 2 && r.toasts0 === 0 &&
    r.comboOpen && r.comboFiltered === 1 && r.comboValue.includes('Frankfurt') && r.comboClosed &&
    r.sortFirst0 === 'crmd' && r.sortNumAsc === 'hart' && r.sortNumDesc === 'grepapi' &&
    r.darkBody === 'rgb(12, 10, 9)' && r.darkCard === 'rgb(28, 25, 23)' && errs.length===0;
  console.log(pass ? 'GALLERY E2E PASS' : 'GALLERY E2E FAIL'); process.exit(pass?0:1);
})().catch(e=>{console.error(e);chrome.kill();process.exit(1)});
