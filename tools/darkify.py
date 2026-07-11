#!/usr/bin/env python3
"""Dark-mode pass: append dark: counterparts to light-mode utility tokens in
component class strings. Ordered: inverted-ink surfaces first (so their
sub-tokens don't get the generic treatment), then generic token appends.
Idempotent: skips files that already contain "dark:"."""
import pathlib, sys

# (find, append) — find must include its own context to stay unambiguous
SURFACES = [
    # primary button / user chat bubble / banner: ink surface inverts
    ("bg-stone-900 text-white hover:bg-stone-700",
     "dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-300"),
    ("bg-stone-900 px-3.5 py-2 text-sm text-white",
     "dark:bg-stone-100 dark:text-stone-900"),
    ("bg-stone-900 px-4 py-2.5 text-sm text-white",
     "dark:bg-stone-100 dark:text-stone-900"),
    ("hover:bg-stone-700 hover:text-white",
     "dark:hover:bg-stone-300 dark:hover:text-stone-900"),
    # tabs / pagination active ink
    ("border-stone-900 text-stone-900", "dark:border-stone-100 dark:text-stone-100"),
    ("border-stone-900 bg-stone-900 text-white", "dark:border-stone-100 dark:bg-stone-100 dark:text-stone-900"),
    ("bg-stone-900 text-white", "dark:bg-stone-100 dark:text-stone-900"),          # steps dot, calendar sel, tooltip bubble
    ("bg-stone-900 font-medium text-white", "dark:bg-stone-100 dark:text-stone-900"),
    ("border-2 border-stone-900", "dark:border-stone-100"),
    ("peer-checked:border-stone-900 peer-checked:bg-stone-900", "dark:peer-checked:border-stone-100 dark:peer-checked:bg-stone-100"),
    ("peer-checked:border-4 peer-checked:border-stone-900", "dark:peer-checked:border-stone-100"),
    ("peer-checked:bg-stone-900", "dark:peer-checked:bg-stone-100"),
    ("bg-stone-900 transition", "dark:bg-stone-100"),                              # progress fill
    ("bg-stone-900 p-4", None),  # log_view panel: stays dark — no append
    # pastel washes
    ("bg-red-50 text-red-800", "dark:bg-red-950 dark:text-red-300"),
    ("bg-sky-50 text-sky-800", "dark:bg-sky-950 dark:text-sky-300"),
    ("bg-green-50 text-green-800", "dark:bg-green-950 dark:text-green-300"),
    ("bg-amber-50 text-amber-800", "dark:bg-amber-950 dark:text-amber-300"),
    ("bg-red-50 text-red-800".replace("red", "green"), None),  # placeholder no-op guard
    # canvas
    ("bg-stone-50 text-stone-900", "dark:bg-stone-950 dark:text-stone-100"),
]
GENERIC = [
    ("bg-white", "dark:bg-stone-900"),
    ("border-stone-200", "dark:border-stone-800"),
    ("divide-stone-200", "dark:divide-stone-800"),
    ("border-stone-300", "dark:border-stone-700"),
    ("border-white", "dark:border-stone-900"),
    ("text-stone-900", "dark:text-stone-100"),
    ("text-stone-700", "dark:text-stone-300"),
    ("text-stone-600", "dark:text-stone-400"),
    ("text-stone-500", "dark:text-stone-400"),
    ("hover:bg-stone-100", "dark:hover:bg-stone-800"),
    ("hover:bg-stone-200", "dark:hover:bg-stone-700"),
    ("hover:text-stone-900", "dark:hover:text-stone-100"),
    ("hover:border-stone-400", "dark:hover:border-stone-600"),
    ("bg-stone-100", "dark:bg-stone-800"),
    ("bg-stone-200", "dark:bg-stone-700"),
    ("bg-stone-300", "dark:bg-stone-600"),
    ("focus:ring-stone-300", "dark:focus:ring-stone-600"),
    ("focus:border-stone-300", "dark:focus:border-stone-600"),
    ("placeholder:text-stone-400", "dark:placeholder:text-stone-500"),
    ("bg-green-50", "dark:bg-green-950"), ("text-green-800", "dark:text-green-300"),
    ("bg-red-50", "dark:bg-red-950"), ("text-red-800", "dark:text-red-300"),
]

def darkify(text):
    # protect surface patterns with placeholders, transform generics, then restore
    marks = {}
    for i, (find, add) in enumerate(SURFACES):
        if add is None:
            token = f"\x00KEEP{i}\x00"
            text = text.replace(find, token)
            marks[token] = find
            continue
        token = f"\x00S{i}\x00"
        if find in text:
            text = text.replace(find, token)
            marks[token] = find + " " + add
    for find, add in GENERIC:
        # avoid re-matching inside already-added dark: tokens or variant forms
        text = text.replace("dark:" + find, f"\x00D{find}\x00")
        text = text.replace(find, find + " " + add)
        text = text.replace(f"\x00D{find}\x00", "dark:" + find)
    for token, orig in marks.items():
        text = text.replace(token, orig)
    return text

changed = 0
for d in sys.argv[1:]:
    for p in sorted(pathlib.Path(d).glob("*.src")):
        t = p.read_text()
        if "dark:" in t and p.name not in ("ui.src",):
            print(f"skip (has dark:): {p}")
            continue
        nt = darkify(t)
        if nt != t:
            p.write_text(nt)
            changed += 1
print(f"darkified {changed} files")
