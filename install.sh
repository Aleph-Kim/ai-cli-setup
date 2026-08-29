#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -gt 0 ]; then
  TARGET_DIRS=("$@")
else
  TARGET_DIRS=(
    "$HOME/.claude/skills"
    "$HOME/.gemini/config/skills"
  )
fi

for target_dir in "${TARGET_DIRS[@]}"; do
  mkdir -p "$target_dir"
  echo "==> Linking skills to $target_dir"

  for skill in "$SCRIPT_DIR"/skills/*/; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    dest="$target_dir/$name"
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
      rm -rf "$dest"
    fi
    ln -sfn "$skill" "$dest"
    echo "  linked: $name -> $dest"
  done
done

