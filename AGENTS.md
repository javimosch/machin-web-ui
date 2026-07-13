# AGENTS.md — working on machin-web-ui

> **Convention:** this file follows [agents.md](https://agents.md) — instructions
> for an agent **working on this repository** (i.e. maintaining/extending the
> framework itself). If instead you want to **build an app** *with* machin-web-ui,
> that's the [SKILL.md](.agents/skills/machin-web-ui/SKILL.md) (a portable capability) and the binary's own
> docs: `machin-web-ui guide` / `coverage` / `list`. `init` scaffolds a
> user-facing `AGENTS.md` into each app it creates — different file, different
> audience.

## The one rule: nothing ships without the oracle

Every change to the engine, the components, or the scanner is proven against
the real `tailwindcss` v3.4.17 standalone binary — the dev-only oracle — before
it lands. The harness lives in `oracle/`:

```sh
python3 oracle/check.py     # MUST print: PASS ... identical with tailwindcss v3.4.17
```

It runs five suites, all of which must stay green: the 3,600+-class **corpus**
(media-mode dark), the same corpus in **darkMode:class**, three **theme** suites
(default/brand/hostile — colors + radius + fonts), the **scanner** (both engines
scan `oracle/fixture/`), a **cascade-order** suite (relative rule order on
conflict pairs), and a **byte-identical preflight** check.

`oracle/check.py` needs `bin/tailwindcss` — the standalone binary, fetched once
from the tailwindcss GitHub releases (gitignored, never a dependency of a user
app). If it's missing, download `tailwindcss-linux-x64` there and `chmod +x`.

## The build

```sh
./build.sh          # gen_embed.py -> encode -> build -> gen_llms.py
```

`build.sh` regenerates two things first: `src/embed_gen.src` (the template +
component registry + SKILL.md, packed into the binary by `tools/gen_embed.py`)
and, after building, `llms.txt`/`llms-full.txt` via `tools/gen_llms.py`. Both
`src/embed_gen.src` and the generated tables below are **gitignored** — they are
rebuilt, never hand-edited.

> **Compiler caveat (2026-07):** the installed `~/.local/bin/machin` may be a
> divergent build with a broken `--target wasm` (emits an unconditional
> `mmap`). If the gallery's wasm build fails, build machin from source
> (`cd ~/ai/machin && go build -o /tmp/machin .`) and pass `MACHIN=/tmp/machin`.
> The native CLI builds fine either way.

## Generated-from-the-oracle tables (never hand-edit)

The finite parts of Tailwind are *extracted from the oracle's own output*, so
they are ground truth by construction. Regenerate with the `oracle/gen_*.py`
scripts:

| file | script | holds |
|---|---|---|
| `src/tw_palette.src` | `gen_palette.py` | the 244-color default palette (rgb + hex) |
| `src/tw_static_gen.src` | `gen_static.py` | ~600 finite utility classes + `@keyframes` + selector suffixes |
| `src/tw_preflight.src` | `gen_preflight.py` | `@tailwind base` verbatim |

The hand-written engine code (`src/tw.src`) only implements the **parametric**
surface: spacing families, negatives, color templates, opacity modifiers,
arbitrary values, and variant/selector composition. If you're about to type a
color hex or a shade value by hand — stop, and generate it instead.

## Adding a utility family

1. Add representative classes to `oracle/families.py` (`param_corpus()` for
   parametric, `static_gen()` for finite) so the harness will test them.
2. If finite: `python3 oracle/gen_static.py` (captures them from the oracle).
   If parametric: implement it in `src/tw.src` (`tw_decls` and friends).
3. `./build.sh && python3 oracle/check.py` until green. The diff output names
   every rule you got wrong, with the oracle's expected value — fix to match.
4. Update `cmd_coverage()` in `src/cli.src` (move it out of `notImplemented`).

Cascade order matters and set-diffing can't see it: if the new family conflicts
on a property with another (e.g. per-side vs all-side), add a pair to the
`pairs`/order list in `oracle/check.py` and make `tw_rank`/`tw_variant_depth`
(in `src/tw.src`) reproduce Tailwind's ordering.

## Adding a component

1. Write `components/<name>.src`. First line is `// <name>.src — <one-line
   description>` (the description is extracted for `list`/`guide`). Component
   functions are `func ui_<name>(...) (h) { ... }`.
2. Speak **semantic tokens** only (`bg-ink`, `text-muted`, `border-line`,
   `ring-accent-500/40`, `bg-surface`, `dark:bg-canvas-950`) — never `stone-*`
   or raw pastels. That's what makes theming work.
3. Include `dark:` variants (see the design rules below).
4. `./build.sh` (re-embeds the registry), then add it to a gallery tile and
   drive it with the E2E if it's interactive.

## Design rules (baked into every component)

- Flat minimalist: warm monochrome, hairline `border-line`, crisp radius, no
  heavy shadows; pale pastel accents only for status.
- **No-JS where possible**: `peer-checked:` for checkbox/radio/switch (the
  styled element must be a **sibling** of the `sr-only` input, never nested),
  `group-hover:` for tooltips, native `<details>` for accordion/dropdown.
- **Dynamic-class trap**: the scanner sees *literal* strings only. Never build
  a class name by interpolation. Data-driven geometry goes in SVG attributes or
  inline `style=` (see `chart.src`).
- **Dark brands**: don't invert the `ink`/`canvas` base tokens — components are
  light-first (`bg-ink text-white` is a dark chip). For a dark site, keep the
  tokens' normal meaning and force **class-mode dark** (`<html class=dark>` +
  `css --dark-class`); the `dark:` variants are internally consistent.

## Verify + gallery + deploy

- `machin-web-ui verify` drives headless Chrome over CDP **in pure MFL**
  (`src/verify.src` — a masked-client WebSocket over `framework/ws.src`). It
  uses a per-run `--user-data-dir` so parallel runs don't contend. Chrome is a
  dev dependency, never shipped.
- The **gallery** (`gallery/`) is the design system dogfooding itself and the
  screenshot/E2E target. `gallery/e2e.js` drives it over CDP (via the global
  `chrome-remote-interface` npm package) and must stay green; run it against
  localhost or `GALLERY_URL=<prod>`.
- Ship it: `gallery/export.sh` static-exports to `docs/` (the `--render` flag
  prints the SSR page; the wasm client hydrates it), served on GitHub Pages.

## machin (MFL) gotchas that bit this repo

The dogfood surfaced several compiler edge cases — all filed upstream. Until
they're fixed in machin, code around them:

- **`&&`/`||` don't short-circuit** (machin#437): `while j > 0 && f(out[j-1])`
  evaluates `out[-1]`. Split the bound check and the compare into separate
  statements.
- **loop + parsed struct + branch segfaults** (machin#449): iterating a
  `parse()`'d struct's fields through a generic getter with any branch in the
  loop body crashes. `src/theme.src` avoids `parse()` entirely with a hand-rolled
  flat-JSON extractor (`theme_field`).
- **`encode` miscounts braces in a string with `{}` AND escaped quotes**
  (machin#451): a JSON snippet like `{"id":1}` inside an MFL string breaks the
  encoder's brace balancer. Keep literal braces out of strings that also contain
  `\"` (rephrase the example, or build the JSON by concatenation).
- **Builtin shadowing**: a function named like a builtin (`log`, `flush`, `len`,
  `str`, `keys`, ...) is silently ignored at call sites. `check --json` reports
  it; heed it.
- **Piped stdout is buffered**: call `flush()` after `println` when debugging a
  program whose output goes to a pipe/file.

## Release

Push a `vX.Y.Z` tag. `.github/workflows/release.yml` builds machin from source,
cross-compiles linux/darwin × amd64/arm64 with `zig cc`, regenerates
`llms.txt`, and attaches the binaries + `SHA256SUMS.txt`. Bump `mwu_version()`
in `src/cli.src` first.
