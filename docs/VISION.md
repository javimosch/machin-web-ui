# VISION — the machin-web-ui north star

> **An agent goes from intent to a deployed, styled, isomorphic machin app in
> minutes — with no human in the loop and no claim it cannot prove.**

machin-web-ui is the UI substrate of the [machin](https://github.com/javimosch/machin)
web ecosystem: one binary that scaffolds an app, vendors component source, and
generates its stylesheet with a pure-MFL Tailwind-compatible engine. This
document is the durable direction; the README tracks current state.

## Who it is for

Agents. In 2026 onward, frameworks are operated by agents: they read JSON, not
docs sites; they vendor and edit source, not configure black boxes; they trust
what is mechanically verified, not what is claimed. Humans review outcomes
(a PR, a live URL, a screenshot) — they are not the operators.

## Pillars (set in stone)

1. **Proof over promise.** Every compatibility claim is a green check against
   ground truth. The Tailwind engine is differential-tested rule-for-rule
   against the real `tailwindcss` binary (corpus, scanner, cascade order,
   preflight, both dark-mode strategies). New surface ships with its oracle
   suite or it does not ship. The same discipline applies beyond CSS: the
   isomorphic contract is proven by a headless-browser E2E, not described.
2. **The binary is the docs.** `list`, `coverage`, `check` answer in JSON;
   unknown classes are loud, never silently dropped; the honest gaps are
   enumerated machine-readably. There will never be a documentation website.
3. **Vendored ownership (the shadcn model).** `add` copies component source
   into the app. The agent that installs a component can read it, edit it, and
   diverge from it. No opaque runtime dependency, no versioned upgrade
   treadmill — the registry is a starting point, not a contract.
4. **One language, both sides of the wire.** A component is a plain MFL
   function: the server calls it for SSR first paint, the wasm client calls
   the same function inside `hydrate()` and binds to the same `data-s` slots.
   No flash, no drift, no second templating language.
5. **One coherent look that always works.** Flat minimalist (warm stone
   monochrome, hairline borders, pale pastel accents), dark mode included,
   both strategies. Agents benefit more from a default that is always right
   than from infinite configurability. Theming comes as verified capability
   (Tier 4), never as a prerequisite.
6. **Zero runtime dependencies.** The engine, scanner, registry, and template
   live in one static binary. Node, bundlers, and npm never enter a user's
   app — the real `tailwindcss` binary exists only as a dev-side oracle in
   THIS repo's harness.

## Non-goals

- Human-DX tooling: no LSP, no IDE plugin, no docs site (machin-wide policy).
- The Tailwind plugin/config JS ecosystem. Compatibility targets the core
  utility surface; `coverage` states the floor honestly.
- Pixel-parity with every Tailwind release. The target is a pinned, tested
  version (v3.4.17 today); moving it is a deliberate, oracle-verified event.
- Being a general-purpose CSS framework for non-machin stacks.

## Tiers

- **T1 — Engine parity (shipped, guarded).** Oracle-identical emission for the
  v3 core surface, both dark strategies, cascade-layer ordering. Open ends:
  a full canonical rule-order table generated from the oracle; the Tailwind
  v4 question (oklch/CSS-vars output) — decide when agent fluency shifts.
- **T2 — Component registry (shipped, demand-driven).** 60 components incl.
  charts (pure-MFL SVG), agent-era UI (chat/log/diff/command-palette), and
  no-JS controls. Growth is pulled by dogfood adoptions, not pushed:
  a component earns its place by being needed twice.
- **T3 — App archetypes.** `init` grows templates: `dashboard` (sidebar shell,
  stats, data tables, live logs), `saas` (machweb + SSO + Postgres + billing-
  shaped pages), `landing` (hero/pricing/FAQ, static-exportable). Each ships
  building, deployed, and E2E-verified — "app in minutes" made literal.
- **T4 — Verified theming.** A machine-readable theme (brand palette, radius,
  fonts) that the engine compiles like Tailwind config would — and proves by
  generating the equivalent `tailwind.config.js` and diffing against the
  oracle. Unlocks branded products without breaking pillar 5's default.
- **T5 — Server-driven live UI.** Components already render on the server;
  machweb already streams (SSE) and speaks WebSocket. Close the loop: the
  server pushes component re-renders into the page's slots/containers — the
  LiveView model with no Elixir and no client build for most apps. wasm
  remains for offline-capable or latency-sensitive interactivity.
- **T6 — The registry as protocol.** `machin-web-ui mcp` exposes
  list/coverage/check/add/init as MCP tools so any agent runtime can operate
  it natively; `add --from <url>` accepts third-party registries; a `verify`
  verb runs the headless-browser screenshot/E2E loop for the user's own app.

## What "winning" measures

- **Time-to-app**: intent → deployed URL for a fresh agent session, in
  minutes, without reading anything but the binary's JSON.
- **Dogfood adoption**: machin ecosystem apps on machin-web-ui
  (machin-vault ✓; next: hart, crmd, arm, grepapi surfaces).
- **Trust**: every oracle suite green on every commit; the E2E green against
  production; each adoption that surfaces a bug turns it into a permanent test
  (the vault adoption caught a scanner crash and a machin compiler bug —
  that loop is the product working).

## Ecosystem position

machin-web-ui is downstream of the machin web north star (machweb, reactive,
wasm) and upstream of every machin product surface. When a gap here reveals a
gap in machin itself (a builtin, a framework hook, a compiler bug), it is
filed and fixed upstream — the design system is the language's most demanding
web dogfood.
