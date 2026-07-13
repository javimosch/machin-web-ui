# machin-web-ui — operator manual for agents

You are building or editing an **isomorphic machin app** styled by
machin-web-ui. This is the manual: the build, the contracts, and the gotchas
you will hit. The binary is the source of truth — run `machin-web-ui guide`
(full JSON) or `machin-web-ui coverage` (Tailwind surface) any time.

## The journey

```sh
machin-web-ui init my-app        # SSR server + wasm client + starter components + theme.json
cd my-app && ./build.sh          # css scan -> asset embed -> wasm -> native binary
./app                            # http://localhost:48100
machin-web-ui list               # more components -> machin-web-ui add <name...>
machin-web-ui check md:bg-ink    # does a class resolve? to what CSS?
machin-web-ui coverage           # what's implemented — and what is NOT
```

`build.sh` needs `machin`, `zig`, and `machin-web-ui` on `PATH` (or
`MACHIN=`/`MACHIN_WEB_UI=`). The shipped app binary has **zero runtime deps**.

## The five contracts

1. **Isomorphic component.** A component is one MFL function. The server calls
   it for SSR first paint; the wasm client calls the *same* function inside
   `hydrate()` and binds to matching `data-s` slots. One view, both sides, no
   flash, no drift.
2. **Clicks.** `<button data-action="bump" data-arg="0">` → the generic host
   calls `export func bump(arg)`. Add behavior = add an `export func` + a
   `data-action`. `data-input="x"` forwards input events to `export func x(v)`.
3. **Text slots.** `slot(name, fn)` emits `<span data-s="name">…</span>` and
   queues a reactive binding; `dom_patch` updates it. The SSR server renders
   the identical span so hydration reuses it.
4. **Markup re-render.** For non-text updates (rebuild a table, a calendar, a
   chip list), call `dom_mount(containerId, html)` directly from client code —
   the reactive runtime's extern is callable from your MFL.
5. **Theming.** Components speak semantic tokens — `canvas surface ink muted
   line accent` + `ok warn danger info` — each a full 50–950 ramp
   (`bg-ink`, `text-muted`, `ring-accent-500/40`, `dark:bg-canvas-950`). A
   `theme.json` remaps them (palette refs `@stone-900` or hexes `#0d9488`,
   plus `radius` and `fontSans`/`fontMono`); the default theme aliases the
   stone look. `css --theme theme.json`.

## Gotchas (these will bite)

- **Dynamic-class trap.** The scanner sees *literal* class strings only. Never
  build a class name by interpolation (`"h-[" + str(n) + "]"` is invisible to
  the scanner). For data-driven geometry use inline SVG attributes or `style=`.
- **`peer-checked:`** — the styled element must be a **sibling** of the
  `sr-only` input, never nested inside it.
- **`data-action` on a `<label>` fires twice** — a label click forwards a
  synthetic click to its wrapped input. Put the `data-action` on the input.
- **Unknown classes**: loud (`/* tw-unknown */` header) in an explicit list;
  silent in file-scan mode (Tailwind JIT semantics). `check` a class if unsure.
- **Dark mode**: media strategy by default; `css --dark-class` emits
  `:is(.dark *)` selectors so a `.dark` class on `<html>` drives a live toggle.

## Not implemented (see `coverage` for the current list)

Container queries, filters/backdrop-filters, aria/data variants, arbitrary
properties (`[color:red]`), `tailwind.config` plugins. The engine targets the
Tailwind v3.4 core surface and is differential-tested rule-for-rule against
the real `tailwindcss` binary.
