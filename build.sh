#!/usr/bin/env bash
# Build the tw engine spike CLI. Needs machin v0.107+.
set -euo pipefail
cd "$(dirname "$0")"
MACHIN="${MACHIN:-machin}"
"$MACHIN" encode src/tw_palette.src src/tw.src src/twgen.src > twgen.mfl
"$MACHIN" build twgen.mfl -o twgen
echo "built ./twgen"
