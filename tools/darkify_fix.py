#!/usr/bin/env python3
"""Cleanup for darkify.py's substring accidents: a variant-prefixed token
(hover:x, focus:x) also matched its bare form, appending an unconditional
dark token. Strip those exact malformed sequences."""
import pathlib, sys

FIXES = [
    ("hover:bg-stone-100 dark:bg-stone-800 dark:hover:bg-stone-800", "hover:bg-stone-100 dark:hover:bg-stone-800"),
    ("hover:bg-stone-100 dark:hover:bg-stone-800 dark:bg-stone-800", "hover:bg-stone-100 dark:hover:bg-stone-800"),
    ("hover:bg-stone-200 dark:bg-stone-700 dark:hover:bg-stone-700", "hover:bg-stone-200 dark:hover:bg-stone-700"),
    ("hover:bg-stone-200 dark:hover:bg-stone-700 dark:bg-stone-700", "hover:bg-stone-200 dark:hover:bg-stone-700"),
    ("hover:text-stone-900 dark:text-stone-100 dark:hover:text-stone-100", "hover:text-stone-900 dark:hover:text-stone-100"),
    ("hover:text-stone-900 dark:hover:text-stone-100 dark:text-stone-100", "hover:text-stone-900 dark:hover:text-stone-100"),
    ("dark:focus:border-stone-600 dark:border-stone-700", "dark:focus:border-stone-600"),
    ("dark:border-stone-700 dark:focus:border-stone-600", "dark:focus:border-stone-600"),
    ("focus:border-stone-300 dark:border-stone-700 dark:focus:border-stone-600", "focus:border-stone-300 dark:focus:border-stone-600"),
]
n = 0
for d in sys.argv[1:]:
    for p in sorted(pathlib.Path(d).glob("*.src")):
        t = orig = p.read_text()
        for f, r in FIXES: t = t.replace(f, r)
        if t != orig: p.write_text(t); n += 1
print(f"fixed {n} files")
