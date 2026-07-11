#!/usr/bin/env python3
"""Regenerate src/tw_palette.src from the oracle (the tailwindcss binary).

The default color palette is never hand-typed: it is extracted from the real
Tailwind's output, so the table is ground truth by construction.
"""
import subprocess, re, pathlib

HERE = pathlib.Path(__file__).parent
hues = "slate gray zinc neutral stone red orange amber yellow lime green emerald teal cyan sky blue indigo violet purple fuchsia pink rose".split()
shades = "50 100 200 300 400 500 600 700 800 900 950".split()
names = [f"{h}-{s}" for h in hues for s in shades] + ["black", "white"]

(HERE / "content.html").write_text(
    '<i class="' + " ".join(f"bg-{n} from-{n}" for n in names) + '"></i>')
subprocess.run([str(HERE.parent / "bin/tailwindcss"), "-c", "tailwind.config.js",
                "-i", "input.css", "-o", "out.css"], cwd=HERE, check=True, capture_output=True)
css = (HERE / "out.css").read_text()
pal = dict(re.findall(r"\.bg-([\w-]+) \{\n  --tw-bg-opacity: 1;\n  background-color: rgb\(([\d ]+) / var", css))
hexes = dict(re.findall(r"\.from-([\w-]+) \{\n  --tw-gradient-from: (\S+) var", css))
missing = [n for n in names if n not in pal or n not in hexes]
assert not missing, missing

lines = ["// tw_palette.src — GENERATED from tailwindcss v3.4.17 (oracle/gen_palette.py). Do not hand-edit.",
         "func tw_palette() (m) {", "    m = make(map[string]string)"]
lines += [f'    m["{n}"] = "{pal[n]}"' for n in names]
lines.append("}")
lines += ["// hex form (gradients, outline-color, ring-offset-color use hex, not rgb triplets)",
          "func tw_palette_hex() (m) {", "    m = make(map[string]string)"]
lines += [f'    m["{n}"] = "{hexes[n]}"' for n in names]
lines.append("}")
(HERE.parent / "src/tw_palette.src").write_text("\n".join(lines) + "\n")
print(f"{len(pal)} colors (+hex) -> src/tw_palette.src")
