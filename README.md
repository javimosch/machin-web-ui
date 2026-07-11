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
corpus (1465 classes): oracle rules: 1465 | ours: 1465
scanner (oracle/fixture): oracle rules: 41 | ours: 41
preflight: byte-identical with @tailwind base
PASS: corpus + scanner + preflight identical with tailwindcss v3.4.17
```

## The CLI

```sh
machin-web-ui css [paths...] [-o out.css] [--no-preflight]
    # scan .src/.mfl/.html/.js (dirs recurse) for classes -> stylesheet
machin-web-ui css -              # explicit class list on stdin (strict:
                                 # unknown classes reported loudly)
machin-web-ui coverage           # JSON: exactly which Tailwind surface is
                                 # implemented — and which is NOT — so an
                                 # agent can query compat before writing a class
machin-web-ui check <class...>   # JSON per class: resolves? to which rule?
```

Scanning the whole isomorphic boilerplate repo end-to-end: **44 ms**.

Every generated rule — selector escaping (`.md\:px-6`, `.\32xl\:flex`),
declarations, `--tw-*-opacity` variables, `-moz-` autoprefixes, the `:visited`
alpha-stripping quirk, media-query nesting — is set-identical to Tailwind's
output for the whole corpus.

|                    | twgen (this repo) | tailwindcss standalone |
|--------------------|-------------------|------------------------|
| corpus (1,465 cls) | **71 ms**         | 958 ms                 |
| binary size        | **55 kB**         | 43 MB                  |
| runtime deps       | none              | none (bundled Node)    |

### Spike scope (all oracle-verified)

- **Utilities**: display, padding/margin, width/height (scale + fractions +
  min/max/fit), bg/text/border colors (full 244-color default palette,
  extracted from the oracle — `oracle/` regenerates `src/tw_palette.src`),
  border widths/sides, rounded, font-size/weight, tracking, leading, flex
  (direction/wrap/grow/shrink/items/justify), grid-cols/col-span, gap,
  text-align, shadows.
- **Variants**, stacking included (`2xl:dark:hover:bg-stone-700`):
  hover/focus/active/disabled/visited/focus-within/focus-visible, `dark:`
  (media strategy), responsive `sm: md: lg: xl: 2xl:`.
- Unknown classes are **loud**: emitted in a `/* tw-unknown: ... */` header,
  never silently dropped.

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
src/tw.src             the engine core: class -> CSS rule
src/scan.src           content scanner (walk dirs, extract candidates)
src/cli.src            the CLI: css / coverage / check
src/tw_palette.src     GENERATED from the oracle -- do not hand-edit
src/tw_preflight.src   GENERATED from the oracle -- do not hand-edit
oracle/check.py        differential harness: corpus + scanner + preflight
oracle/gen_palette.py  regenerate the palette table from ground truth
oracle/gen_preflight.py  regenerate the preflight embed from ground truth
bin/tailwindcss        dev-only oracle binary (not committed)
```

## Roadmap

- [x] **M0 spike — tw engine core**, oracle-verified
- [x] preflight + `.mfl`/`.src` file scanner (`machin-web-ui css`), oracle-verified
- [x] `machin-web-ui coverage` + `check` — honest, queryable compat surface
- [ ] arbitrary values (`w-[13px]`), `group-hover:`, remaining utility families
- [ ] `init` — isomorphic app template (from boilerplate-cli-ui-machin-isomorphic)
- [ ] `add <component>` — vendor MFL component source (button, card, dialog, ...)
      styled to the minimalist design language
- [ ] component gallery app, deployed (screenshot-verify target)
