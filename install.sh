#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$HOME/.claude/skills}"

mkdir -p "$TARGET_DIR"

for skill in "$SCRIPT_DIR"/skills/*/; do
  name="$(basename "$skill")"
  dest="$TARGET_DIR/$name"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    rm -rf "$dest"
  fi
  ln -sfn "$skill" "$dest"
  echo "linked: $name -> $dest"
done
