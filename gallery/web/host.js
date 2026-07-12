// host.js — the GENERIC JS host (embedded into the server binary at build
// time). App-agnostic: instantiate the wasm, wire the reactive runtime's DOM
// ops, hydrate, and forward [data-action] clicks to same-named wasm exports.
// Adding components or behavior changes only the MFL — this file rarely changes.
const dec = new TextDecoder();
let mem;
const cstr = (p) => { const b = new Uint8Array(mem.buffer); let e = p; while (b[e]) e++; return dec.decode(b.subarray(p, e)); };

const env = {
  // reactive runtime → DOM
  dom_mount: (r, h) => { document.getElementById(cstr(r)).innerHTML = cstr(h); },
  dom_patch: (s, v) => { const el = document.querySelector('[data-s="' + cstr(s) + '"]'); if (el) el.textContent = cstr(v); },
  list_insert: (c, k, h) => { const li = document.createElement('li'); li.dataset.k = cstr(k); li.innerHTML = cstr(h); document.getElementById(cstr(c)).appendChild(li); },
  list_remove: (c, k) => { const el = document.querySelector('#' + cstr(c) + ' > [data-k="' + cstr(k) + '"]'); if (el) el.remove(); },
  list_order: (c, csv) => { const cont = document.getElementById(cstr(c)); for (const k of cstr(csv).split(',').filter(Boolean)) { const el = cont.querySelector('[data-k="' + k + '"]'); if (el) cont.appendChild(el); } },
  // app effects
  toast_show: (id) => { const el = document.getElementById(cstr(id)); if (!el) return; el.classList.remove('hidden'); clearTimeout(el._t); el._t = setTimeout(() => el.classList.add('hidden'), 2500); },
  dom_show: (id, on) => { document.getElementById(cstr(id))?.classList.toggle('hidden', !Number(on)); },
  set_theme: (name) => { const t = window.__THEMES?.[cstr(name)]; if (t) document.getElementById('tw-style').textContent = t; },
  toggle_dark: () => { const on = document.documentElement.classList.toggle('dark'); const sw = document.querySelector('input[name="dark"]'); if (sw) sw.checked = on; },
  after: (ms, key) => { setTimeout(() => instance.exports.timer_fired?.(BigInt(key)), Number(ms)); },
  tab_mark: (nav, idx, onCls, offCls) => { [...document.getElementById(cstr(nav)).children].forEach((el, i) => { el.className = i === Number(idx) ? cstr(onCls) : cstr(offCls); }); },
};
// no-op WASI shim (imported but never called)
const wasi = { fd_write: () => 0, fd_seek: () => 0, fd_close: () => 0, fd_fdstat_get: () => 0 };

const { instance } = await WebAssembly.instantiateStreaming(fetch('app.wasm'), { env, wasi_snapshot_preview1: wasi });
mem = instance.exports.memory;
instance.exports._initialize?.();
// darkMode 'class': boot from the OS preference; the Dark mode switch toggles it
const dk = matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.classList.toggle('dark', dk);
const dksw = document.querySelector('input[name="dark"]');
if (dksw) dksw.checked = dk;
instance.exports.start();

// delegate clicks: <button data-action="bump" data-arg="0"> calls exports.bump(0n);
// [data-copy] copies its payload to the clipboard.
document.body.addEventListener('click', (e) => {
  if (e.target.dataset?.comboInput !== undefined)
    e.target.closest('[data-combo]').querySelector('[data-combo-list]').classList.remove('hidden');
  const opt = e.target.closest('[data-combo-opt]');
  if (opt) {
    const combo = opt.closest('[data-combo]');
    combo.querySelector('[data-combo-input]').value = opt.textContent;
    combo.querySelector('[data-combo-list]').classList.add('hidden');
    return;
  }
  if (!e.target.closest('[data-combo]'))
    document.querySelectorAll('[data-combo-list]').forEach(el => el.classList.add('hidden'));
  const c = e.target.closest('[data-copy]');
  if (c) { navigator.clipboard?.writeText(c.dataset.copy); c.textContent = 'Copied'; setTimeout(() => c.textContent = 'Copy', 1200); return; }
  const b = e.target.closest('[data-action]');
  if (b) instance.exports[b.dataset.action]?.(BigInt(b.dataset.arg ?? 0));
});

// delegate input events: <input data-input="slider_set"> calls exports.slider_set(value)
document.body.addEventListener('input', (e) => {
  const t = e.target;
  if (t.dataset.input) instance.exports[t.dataset.input]?.(BigInt(t.value || 0));
  if (t.dataset.comboInput !== undefined) {
    const list = t.closest('[data-combo]').querySelector('[data-combo-list]');
    list.classList.remove('hidden');
    const q = t.value.toLowerCase();
    list.querySelectorAll('[data-combo-opt]').forEach(el =>
      el.classList.toggle('hidden', !el.textContent.toLowerCase().includes(q)));
  }
  if (t.dataset.paletteInput !== undefined) {
    const q = t.value.toLowerCase();
    t.closest('div').parentElement.querySelectorAll('[data-item]').forEach(el =>
      el.classList.toggle('hidden', !el.textContent.toLowerCase().includes(q)));
  }
});

// combobox: focusing the input opens its list
document.body.addEventListener('focusin', (e) => {
  if (e.target.dataset?.comboInput !== undefined)
    e.target.closest('[data-combo]').querySelector('[data-combo-list]').classList.remove('hidden');
});

// ctrl/cmd-K toggles the command palette; Escape closes it
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); instance.exports.palette?.(0n); }
  if (e.key === 'Escape') instance.exports.palette_close?.(0n);
});
