# machin-web-ui

An **agent-first design system for isomorphic machin apps** — think shadcn, but
for [machin](https://github.com/javimosch/machin) (MFL), operated by agents, not
humans. One binary that scaffolds an isomorphic app (SSR + reactive wasm),
vendors component source into your repo, and generates its stylesheet with a
built-in **Tailwind-compatible CSS engine in pure MFL** — no Node, no bundler.

> In 2026 onwards, frameworks are operated by agents. Everything here is
> queryable (`--json`), self-describing, and copy-source-into-your-repo, so an
> agent never needs a docs website — it asks the binary.

## Status: engine + scanner + preflight, all oracle-verified

The risky part was the CSS engine: is "100% Tailwind-compatible without Node"
real? Verified by **differential testing against the real thing** — the
`tailwindcss` v3.4.17 standalone binary (a dev-only oracle, never a dependency
of user apps):

```
corpus (3613 classes): oracle rules: 3618 | ours: 3618
scanner (oracle/fixture): oracle rules: 66 | ours: 66
cascade order: 9 conflict pairs match the oracle
preflight: byte-identical with @tailwind base
PASS: corpus + scanner + preflight identical with tailwindcss v3.4.17
```

And the whole loop is proven end-to-end: `init` an app, build it (native
server + wasm client), drive it in a real headless Chrome — SSR first paint,
wasm hydration, reactive click patches, toast, computed styles from the
generated stylesheet — all asserted.

## For agents

The binary is the documentation. No docs site.

```sh
machin-web-ui guide        # verbs, contracts, gotchas, full component catalog (JSON)
machin-web-ui help-json    # verbs + version
machin-web-ui skill        # a SKILL.md you can self-install
machin-web-ui coverage     # the implemented Tailwind surface (and what's NOT)
```

Discovery: [`llms.txt`](llms.txt) (concise) and [`llms-full.txt`](llms-full.txt)
sit at the repo root and on the [live site](https://javimosch.github.io/machin-web-ui/llms.txt);
the full operator manual is [AGENTS.md](AGENTS.md). Install via a GitHub
release binary (`releases/latest`) — no build-from-source required.

## The CLI

```sh
machin-web-ui init [dir]         # scaffold an isomorphic app: SSR + reactive
                                 # wasm client + starter components, builds
                                 # out of the box
machin-web-ui add dialog table   # vendor component source into ./components/
                                 # (shadcn-style: you own it, edit it)
machin-web-ui list               # component registry (JSON)
machin-web-ui css [paths...] [-o out.css] [--no-preflight]
    # scan .src/.mfl/.html/.js (dirs recurse) for classes -> stylesheet
machin-web-ui css -              # explicit class list on stdin (strict:
                                 # unknown classes reported loudly)
machin-web-ui coverage           # JSON: exactly which Tailwind surface is
                                 # implemented — and which is NOT — so an
                                 # agent can query compat before writing a class
machin-web-ui check <class...>   # JSON per class: resolves? to which rule?
```

## Components

Flat minimalist design (warm stone monochrome, hairline borders, pale pastel
accents, no heavy shadows) — **59 components**: accordion, alert, avatar,
badge, banner, breadcrumb, button, calendar (custom month grid with range
selection, pure-MFL date math), card, chart (sparkline/bars/donut as pure-MFL
inline SVG), chat (agent transcript), checkbox, chips, code_block,
command_palette (ctrl-K), copy_field, date_picker (native date/datetime/time
+ ranges), desc_list, dialog, diff_view, drawer, dropdown, empty_state,
file_upload, footer, form_field, heatmap, hero, input, kbd, layout
(shell/grid/split), list_group, log_view, navbar, otp_input, pagination,
popover, progress, radio_group, rating, section_header, combobox (autocomplete: the picked option IS the form value),
data_table (sortable headers), select, separator, sidebar, skeleton, slider,
spinner, stat, steps, switch, table, tabs, textarea, timeline, toast
(single + STACKED with queueing and auto-expiry), tooltip, tree (+ `ui` base
helpers).

**Dark mode**: every component carries `dark:` classes. Two strategies, both
oracle-verified: the default media strategy (follows the OS), or
`css --dark-class` for **darkMode: 'class'** — `dark:` variants become
`:is(.dark *)` selectors so a `.dark` class on `<html>` drives the theme.
The gallery uses class mode: its Dark mode switch flips the theme live
(boot syncs from the OS preference), asserted in the E2E with computed
colors both ways. The layout
family (ui_shell + sidebar + content grid) powers the gallery's own
full-wide docs layout. Interactive controls
are no-JS where possible: checkbox/radio/switch are sr-only native inputs
driving styled siblings via `peer-checked:`, tooltips use `group-hover:`,
accordion/dropdown are native `<details>`. Each is a plain MFL
function usable on both sides — the server calls it for SSR, the wasm client
calls it inside `hydrate()`. The starter template's `app_view()` in
`models.src` shows the isomorphic pattern: one view function, dynamic parts
passed as fragments (SSR spans on the server, reactive `slot()`s on the
client, same `data-s` names).

Every generated rule — selector escaping (`.md\:px-6`, `.\32xl\:flex`),
declarations, `--tw-*-opacity` variables, `-moz-` autoprefixes, the `:visited`
alpha-stripping quirk, media-query nesting — is set-identical to Tailwind's
output for the whole corpus.

|                    | machin-web-ui | tailwindcss standalone |
|--------------------|---------------|------------------------|
| corpus (3,471 cls) | **16 ms**     | 1,342 ms               |
| binary size        | **172 kB**    | 43 MB                  |
| runtime deps       | none          | none (bundled Node)    |

### Implemented surface (all oracle-verified — `coverage` has the full JSON)

- **Utilities**: layout (display/position/visibility/overflow/object/aspect/
  z/order), spacing (+ negative margins, `space-x/y` with reverse), sizing
  (+ min/max variants), inset (+ negatives), the full 244-color default
  palette for bg/text/border **with opacity modifiers** (`bg-red-500/50`,
  also ring/divide), borders (widths/styles/radius/divide/ring/outline),
  typography (sizes/weights/families/decoration/whitespace/truncate),
  flexbox + grid (incl. rows/flow/place-*), gradients (`from/via/to-*`),
  shadows, opacity, transitions + `animate-*` (with `@keyframes`), transforms
  (translate/rotate/scale/skew, negatable), interactivity (cursor/select/…).
- **Arbitrary values**: `w-[13px]`, `top-[117px]`, `text-[15px]`,
  `bg-[#f7f6f3]`, `border-[rgb(1,2,3)]`, `w-[calc(100%_-_2rem)]` — with
  Tailwind's exact selector escaping (`\2c ` commas, `\3` leading digits).
- **Variants**, stacking included (`2xl:dark:hover:bg-stone-700`):
  hover/focus/active/disabled/visited/focus-within/focus-visible,
  **group-hover/focus, peer-hover/focus/checked/disabled**, `dark:` (media
  strategy), responsive `sm: md: lg: xl: 2xl:`.
- Unknown classes are **loud** in explicit-list mode: emitted in a
  `/* tw-unknown: ... */` header, never silently dropped.

Every finite utility set is **generated from the oracle itself**
(`oracle/gen_static.py` → `src/tw_static_gen.src`, 526 classes + keyframes;
same for the palette and preflight) — the tables are ground truth by
construction, and what the oracle doesn't resolve, this engine doesn't either.
The hand-written engine code only implements the genuinely parametric surface:
spacing families, negatives, color templates, opacity modifiers, arbitrary
values, and variant/selector composition.

## Try it

```sh
./build.sh                                  # needs machin v0.107+
echo "flex items-center gap-2 rounded-lg bg-stone-900 text-white hover:bg-stone-700 md:px-6" | ./machin-web-ui css --no-preflight -
./machin-web-ui css path/to/app -o tw.css   # scan a real project
./machin-web-ui coverage | jq .notImplemented
```

Re-run the differential test (needs `bin/tailwindcss`, the standalone oracle
binary — fetched once from the tailwindcss GitHub releases, not committed):

```sh
python3 oracle/check.py
```

## Layout

```
src/tw.src             the engine core: class -> CSS rule (+ cascade ranking)
src/scan.src           content scanner (walk dirs, extract candidates)
src/cli.src            the CLI: init / add / list / css / coverage / check
src/tw_palette.src     GENERATED from the oracle -- do not hand-edit
src/tw_preflight.src   GENERATED from the oracle -- do not hand-edit
src/tw_static_gen.src  GENERATED from the oracle -- do not hand-edit
src/embed_gen.src      GENERATED from template/ + components/ (tools/gen_embed.py)
template/              the `init` scaffold (isomorphic starter app)
components/            the component registry (vendored by `add`)
oracle/check.py        differential harness: corpus + scanner + order + preflight
oracle/gen_*.py        regenerate the generated tables from ground truth
bin/tailwindcss        dev-only oracle binary (not committed)
```

## Roadmap

The durable direction lives in [docs/VISION.md](docs/VISION.md). Working on the
framework itself? [AGENTS.md](AGENTS.md) is the maintainer guide (the oracle
discipline, adding components/engine surface, the machin gotchas). Building an
app *with* it? [SKILL.md](.agents/skills/machin-web-ui/SKILL.md) or `machin-web-ui guide`.

- [x] **M0 spike — tw engine core**, oracle-verified
- [x] preflight + `.mfl`/`.src` file scanner (`machin-web-ui css`), oracle-verified
- [x] `machin-web-ui coverage` + `check` — honest, queryable compat surface
- [x] arbitrary values, `group-*`/`peer-*`, opacity modifiers, negatives, and
      ~all remaining v3 core families (see `coverage` for the exact list)
- [x] `init` — isomorphic app template (SSR + wasm hydration), E2E-proven in
      headless Chrome
- [x] `add <component>` + `list` — 10 components + base helpers, minimalist
      design language, vendored source (you own it)
- [x] component gallery **live at
      [javimosch.github.io/machin-web-ui](https://javimosch.github.io/machin-web-ui/)**
      — every component SSR'd + hydrated; statically exported to GitHub Pages
      (`gallery/export.sh` -> `docs/`: the `--render` flag prints the SSR page,
      the wasm client hydrates it — no server in production at all);
      `gallery/e2e.js` drives it in headless Chrome (GALLERY_URL picks the target)
- [ ] full canonical rule ordering generated from the oracle (today: structural
      shorthand→axis→side ranking, oracle-checked on conflict pairs)
