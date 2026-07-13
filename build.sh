#!/usr/bin/env bash
# Build the machin-web-ui CLI. Needs machin v0.107+.
set -euo pipefail
cd "$(dirname "$0")"
MACHIN="${MACHIN:-machin}"
python3 tools/gen_embed.py
"$MACHIN" encode src/tw_palette.src src/tw_preflight.src src/tw_static_gen.src src/embed_gen.src src/theme.src src/tw.src src/scan.src src/cli.src > machin-web-ui.mfl
"$MACHIN" build machin-web-ui.mfl -o machin-web-ui
python3 tools/gen_llms.py >/dev/null || true
echo "built ./machin-web-ui"
