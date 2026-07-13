---
name: machin-web-ui
description: Build or edit an isomorphic machin (MFL) web app styled by machin-web-ui — an agent-first design system with a pure-MFL Tailwind engine, 60 vendored components, and verified theming. Use when scaffolding a machin web app, adding UI components, generating the stylesheet, or debugging the SSR+wasm hydration contract. The binary is the docs: `machin-web-ui guide` (full JSON), `coverage` (Tailwind surface), `list` (components).
---

# machin-web-ui

Agent-first design system for isomorphic machin apps: one static binary that
scaffolds an app, vendors component source into your repo (shadcn-style), and
generates the stylesheet with a pure-MFL Tailwind-compatible engine — no Node.

## Install

Grab the binary from GitHub releases (or `MACHIN_WEB_UI=/path` if built from
source):

```sh
curl -L https://github.com/javimosch/machin-web-ui/releases/latest/download/machin-web-ui-linux-amd64 -o machin-web-ui
chmod +x machin-web-ui && sudo mv machin-web-ui /usr/local/bin/
```

Also needs `machin` (v0.107+) and `zig` on PATH for `build.sh`.

## Do this first

Ask the binary — it is version-exact and self-describing:

```sh
machin-web-ui guide        # full JSON: verbs, contracts, gotchas, component catalog with signatures
machin-web-ui coverage     # the implemented Tailwind surface + honest notImplemented
machin-web-ui list         # the component registry
machin-web-ui check <cls>  # does a class resolve? to what CSS?
```

## The journey

```sh
machin-web-ui init my-app          # isomorphic app (SSR + wasm) + theme.json, builds out of the box
cd my-app && ./build.sh && ./app   # http://localhost:48100
machin-web-ui add dialog table     # vendor component source into ./components/ (you own it)
```

## The contracts (memorize these)

- **Component = one MFL function**, called by the server (SSR) and the wasm
  client (inside `hydrate()`) — one view, both sides.
- **Clicks**: `data-action="x"` → `export func x(arg)`. `data-input="x"` →
  `export func x(value)`.
- **Text**: `slot(name, fn)` → `<span data-s=name>`, patched by `dom_patch`.
- **Markup re-render**: `dom_mount(id, html)` from client code.
- **Theming**: components speak semantic tokens (`canvas surface ink muted line
  accent` + `ok warn danger info`); `theme.json` remaps them; `css --theme`.

## Gotchas

- **Dynamic-class trap**: the scanner sees literal strings only. Never
  interpolate class names; use SVG attributes or `style=` for data-driven
  geometry.
- `peer-checked:` target must be a **sibling** of the `sr-only` input.
- `data-action` on a `<label>` fires **twice** — put it on the input.
- Unknown classes: loud in explicit lists, silent in file scan. `check` if
  unsure.

Full manual: `AGENTS.md` in the repo. Vision: `docs/VISION.md`. The language:
https://github.com/javimosch/machin
