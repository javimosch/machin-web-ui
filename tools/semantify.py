#!/usr/bin/env python3
"""Migrate component class strings from stone/pastel literals to semantic
tokens. Ordered: variant-prefixed mappings first (protected via placeholders),
then bare tokens — so dark:bg-stone-900 (a SURFACE) maps differently than bare
bg-stone-900 (INK). Default theme aliases make the result pixel-identical."""
import pathlib, sys

ORDERED = [
    # dark-mode variants first (different semantics than their bare forms)
    ("dark:bg-stone-950", "dark:bg-canvas-950"),
    ("dark:bg-stone-900", "dark:bg-surface-900"),
    ("dark:hover:bg-stone-800", "dark:hover:bg-surface-800"),
    ("dark:hover:bg-stone-700", "dark:hover:bg-surface-700"),
    ("dark:hover:bg-stone-300", "dark:hover:bg-ink-300"),
    ("dark:bg-stone-800", "dark:bg-surface-800"),
    ("dark:bg-stone-700", "dark:bg-surface-700"),
    ("dark:bg-stone-600", "dark:bg-muted-600"),
    ("dark:bg-stone-100", "dark:bg-ink-100"),
    ("dark:peer-checked:bg-stone-100", "dark:peer-checked:bg-ink-100"),
    ("dark:peer-checked:border-stone-100", "dark:peer-checked:border-ink-100"),
    ("dark:text-stone-900", "dark:text-ink-900"),
    ("dark:text-stone-100", "dark:text-ink-100"),
    ("dark:hover:text-stone-100", "dark:hover:text-ink-100"),
    ("dark:text-stone-400", "dark:text-muted-400"),
    ("dark:text-stone-500", "dark:text-muted-500"),
    ("dark:placeholder:text-stone-500", "dark:placeholder:text-muted-500"),
    ("dark:border-stone-800", "dark:border-line-800"),
    ("dark:border-stone-700", "dark:border-line-700"),
    ("dark:border-stone-900", "dark:border-surface-900"),
    ("dark:hover:border-stone-600", "dark:hover:border-line-600"),
    ("dark:focus:ring-stone-600", "dark:focus:ring-line-600"),
    ("dark:focus:border-stone-600", "dark:focus:border-line-600"),
    ("dark:divide-stone-800", "dark:divide-line-800"),
    ("dark:border-l-stone-400", "dark:border-l-muted-400"),
    # bare / light-mode
    ("hover:bg-stone-100", "hover:bg-surface-100"),
    ("hover:bg-stone-200", "hover:bg-line"),
    ("hover:bg-stone-700", "hover:bg-ink-700"),
    ("hover:text-stone-900", "hover:text-ink"),
    ("hover:border-stone-400", "hover:border-line-400"),
    ("peer-checked:border-stone-900", "peer-checked:border-ink"),
    ("peer-checked:bg-stone-900", "peer-checked:bg-ink"),
    ("placeholder:text-stone-400", "placeholder:text-muted-400"),
    ("focus:ring-stone-300", "focus:ring-line-300"),
    ("focus:border-stone-300", "focus:border-line-300"),
    ("divide-stone-200", "divide-line"),
    ("bg-stone-900/40", "bg-ink/40"),
    ("bg-stone-900/50", "bg-ink/50"),
    ("bg-stone-950", "bg-canvas-950"),
    ("bg-stone-900", "bg-ink"),
    ("bg-stone-300", "bg-muted-300"),
    ("bg-stone-200", "bg-line"),
    ("bg-stone-100", "bg-surface-100"),
    ("bg-stone-50", "bg-canvas"),
    ("bg-white", "bg-surface"),
    ("border-stone-200", "border-line"),
    ("border-stone-300", "border-line-300"),
    ("border-t-stone-900", "border-t-ink"),
    ("border-l-stone-400", "border-l-muted-400"),
    ("border-white", "border-surface"),
    ("text-stone-950", "text-ink-950"),
    ("text-stone-900", "text-ink"),
    ("text-stone-700", "text-ink-700"),
    ("text-stone-600", "text-muted-600"),
    ("text-stone-500", "text-muted"),
    ("text-stone-400", "text-muted-400"),
    ("text-stone-300", "text-muted-300"),
    ("text-stone-200", "text-ink-200"),
    ("text-stone-100", "text-ink-100"),
    ("ring-stone-950/10", "ring-ink-950/10"),
    # status hues
    ("green-", "ok-"), ("red-", "danger-"), ("amber-", "warn-"), ("sky-", "info-"),
]

def migrate(text):
    marks = {}
    for i, (find, repl) in enumerate(ORDERED):
        if find.endswith("-"):  # hue prefix rename (green- -> ok-)
            text = text.replace(find, repl)
            continue
        token = f"\x00M{i}\x00"
        if find in text:
            text = text.replace(find, token)
            marks[token] = repl
    for token, repl in marks.items():
        text = text.replace(token, repl)
    return text

changed = 0
for d in sys.argv[1:]:
    p = pathlib.Path(d)
    files = [p] if p.is_file() else sorted(p.glob("*.src"))
    for f in files:
        t = f.read_text()
        nt = migrate(t)
        if nt != t: f.write_text(nt); changed += 1
print(f"semantified {changed} files")
