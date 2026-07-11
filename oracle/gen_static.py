#!/usr/bin/env python3
"""Regenerate src/tw_static_gen.src from the oracle: every finite-set utility
class is probed against the real tailwindcss binary and its (selector suffix,
declarations) captured verbatim. Classes the oracle does not resolve are simply
absent from the table — so our engine drops them too, matching by construction.

Emits three functions:
  tw_static_gen()  class -> declarations (verbatim oracle text)
  tw_suffix_gen()  class -> selector suffix (divide-*/space-*: "> :not(...) ~ ...")
  tw_keyframes()   animation name -> full @keyframes block (for animate-*)
"""
import json, re, subprocess, pathlib
from families import static_gen

HERE = pathlib.Path(__file__).parent

classes = static_gen()
(HERE / "content.html").write_text('<i class="' + " ".join(classes) + '"></i>')
subprocess.run([str(HERE.parent / "bin/tailwindcss"), "-c", "tailwind.config.js",
                "-i", "input.css", "-o", "static_gen.css"], cwd=HERE, check=True, capture_output=True)
css = (HERE / "static_gen.css").read_text()

# keyframes blocks (indented bodies; the closing brace is at column 0)
keyframes = {}
for m in re.finditer(r"(@keyframes ([\w-]+) \{.*?\n\})", css, flags=re.S):
    keyframes[m.group(2)] = m.group(1)
css = re.sub(r"@keyframes [\w-]+ \{.*?\n\}", "", css, flags=re.S)

# top-level rules: selector { decls } (no @media in this probe)
decls_map, suffix_map = {}, {}
for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
    sel, body = m.group(1).strip(), m.group(2).strip()
    cm = re.match(r"^\.((?:\\.|[\w-])+)(.*)$", sel)
    assert cm, f"unparsable selector: {sel}"
    cls = cm.group(1).replace("\\", "")
    suffix = cm.group(2).strip()
    assert cls in classes, f"unexpected class from oracle: {cls}"
    decls_map[cls] = body
    if suffix:
        suffix_map[cls] = suffix

unresolved = [c for c in classes if c not in decls_map]
if unresolved:
    print(f"note: {len(unresolved)} probed classes not resolved by oracle (dropped, matching): {' '.join(unresolved)}")

lines = ["// tw_static_gen.src — GENERATED from tailwindcss v3.4.17 (oracle/gen_static.py). Do not hand-edit.",
         "func tw_static_gen() (m) {", "    m = make(map[string]string)"]
for cls in classes:
    if cls in decls_map:
        lines.append(f"    m[{json.dumps(cls)}] = {json.dumps(decls_map[cls])}")
lines.append("}")
lines += ["func tw_suffix_gen() (m) {", "    m = make(map[string]string)"]
for cls, sfx in suffix_map.items():
    lines.append(f"    m[{json.dumps(cls)}] = {json.dumps(' ' + sfx)}")
lines.append("}")
lines += ["func tw_keyframes() (m) {", "    m = make(map[string]string)"]
for name, block in sorted(keyframes.items()):
    lines.append(f"    m[{json.dumps(name)}] = {json.dumps(block)}")
lines.append("}")

(HERE.parent / "src/tw_static_gen.src").write_text("\n".join(lines) + "\n")
print(f"{len(decls_map)} static classes, {len(suffix_map)} with selector suffix, "
      f"{len(keyframes)} keyframes -> src/tw_static_gen.src")
