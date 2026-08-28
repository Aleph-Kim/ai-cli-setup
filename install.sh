#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$HOME/.claude/skills}"

mkdir -p "$TARGET_DIR"

for skill in "$SCRIPT_DIR"/skills/*/; do
  name="$(basename "$skill")"
  ln -sfn "$skill" "$TARGET_DIR/$name"
  echo "linked: $name -> $TARGET_DIR/$name"
done
