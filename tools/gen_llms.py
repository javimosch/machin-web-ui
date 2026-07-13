#!/usr/bin/env python3
"""Generate llms.txt (concise) + llms-full.txt (with the guide + SKILL.md)
from the built binary — the agent discovery layer. Written to both the repo
root and the exported gallery (docs/) so a deployed app advertises the trail.
Run after building ./machin-web-ui."""
import json, subprocess, pathlib

ROOT = pathlib.Path(__file__).parent.parent
BIN = ROOT / "machin-web-ui"

guide = json.loads(subprocess.run([str(BIN), "guide"], capture_output=True, text=True).stdout)
coverage = json.loads(subprocess.run([str(BIN), "coverage"], capture_output=True, text=True).stdout)
skill = (ROOT / ".agents/skills/machin-web-ui/SKILL.md").read_text()
version = guide["version"]

comp_lines = "\n".join(
    f"- **{c['name']}** — {c['description']} `{c.get('functions','')}`"
    for c in guide["components"])

LLMS = f"""# machin-web-ui

> {guide['tagline']}

Version {version}. The binary is the source of truth — everything here is
`machin-web-ui guide` / `coverage` / `list` output. Repo:
{guide['docs']['repo']} · live gallery: {guide['docs']['gallery']}

## Install

```
curl -L {guide['docs']['repo']}/releases/latest/download/machin-web-ui-linux-amd64 -o machin-web-ui
chmod +x machin-web-ui && sudo mv machin-web-ui /usr/local/bin/
```

Also needs `machin` and `zig` on PATH for `build.sh`. The shipped app binary
has zero runtime dependencies.

## Journey

{chr(10).join('- ' + s for s in guide['journey'])}

## Verbs

{chr(10).join(f"- `{v['verb']}` — {v['does']}" for v in guide['verbs'])}
- `guide` — this, as JSON (verbs, contracts, gotchas, full component catalog)
- `skill` — prints a SKILL.md for self-installation into an agent runtime

## Contracts

{chr(10).join(f"- **{k}**: {v}" for k, v in guide['contracts'].items())}

## Gotchas

{chr(10).join('- ' + g for g in guide['gotchas'])}

## Optional

- Using machin-web-ui: {guide['docs']['repo']}/blob/main/.agents/skills/machin-web-ui/SKILL.md\n- Maintaining the framework: {guide['docs']['repo']}/blob/main/AGENTS.md
- llms-full.txt (this + the complete component catalog + SKILL.md)
- Vision / north star: {guide['docs']['repo']}/blob/main/docs/VISION.md
- The language (machin/MFL): {guide['docs']['language']}
"""

FULL = LLMS + f"""

---

## Component catalog ({len(guide['components'])})

{comp_lines}

## Tailwind coverage

Implemented families: {', '.join(f['family'] for f in coverage['families'])}.
Not implemented: {', '.join(coverage['notImplemented'])}.
Verification: {coverage['verification']}

---

# SKILL.md — using machin-web-ui

{skill}
"""

targets = [ROOT, ROOT / "docs"]
for base in targets:
    if not base.exists():
        continue
    (base / "llms.txt").write_text(LLMS)
    (base / "llms-full.txt").write_text(FULL)
    print(f"wrote {base}/llms.txt ({len(LLMS)}B) + llms-full.txt ({len(FULL)}B)")
