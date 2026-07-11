#!/usr/bin/env python3
"""Regenerate src/tw_preflight.src from the oracle's `@tailwind base` output
(preflight reset + --tw-* variable defaults). MFL string escaping == JSON escaping."""
import json, subprocess, pathlib

HERE = pathlib.Path(__file__).parent
(HERE / "base.css").write_text("@tailwind base;\n")
(HERE / "content.html").write_text('<i class="flex"></i>')
subprocess.run([str(HERE.parent / "bin/tailwindcss"), "-c", "tailwind.preflight.config.js",
                "-i", "base.css", "-o", "preflight_full.css"], cwd=HERE, check=True, capture_output=True)
css = (HERE / "preflight_full.css").read_text()
out = ["// tw_preflight.src — GENERATED from tailwindcss v3.4.17 `@tailwind base` (oracle/gen_preflight.py). Do not hand-edit.",
       "func tw_preflight() (s) { s = " + json.dumps(css) + " }"]
(HERE.parent / "src/tw_preflight.src").write_text("\n".join(out) + "\n")
print(f"{len(css)} bytes -> src/tw_preflight.src")
