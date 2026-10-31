#!/usr/bin/env bash
set -euo pipefail

# 실행 위치와 무관하게 저장소 루트 절대 경로 참조
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AUTO_CONFIRM=false
INSTALL_RULES=true
INSTALL_STATUSLINE=true
INSTALL_SKILLS=true

show_help() {
  cat <<EOF
사용법: ./install.sh [옵션]

옵션:
  -y, --yes             확인 없이 기존 파일 백업 후 링크
  --rules-only          규칙(RULES.md)만 링크
  --statusline-only     상태표시줄 스크립트만 링크
  --skills-only         스킬만 링크
  -h, --help            도움말
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes)
      AUTO_CONFIRM=true
      shift
      ;;
    --rules-only)
      INSTALL_RULES=true
      INSTALL_STATUSLINE=false
      INSTALL_SKILLS=false
      shift
      ;;
    --statusline-only)
      INSTALL_RULES=false
      INSTALL_STATUSLINE=true
      INSTALL_SKILLS=false
      shift
      ;;
    --skills-only)
      INSTALL_RULES=false
      INSTALL_STATUSLINE=false
      INSTALL_SKILLS=true
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "알 수 없는 옵션입니다: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

backup_root() {
  # skills 하위 백업의 스킬 오인식 방지를 위한 CLI 홈별 백업 분리
  case "$1" in
    "$HOME/.claude/"*) echo "$HOME/.claude/backup" ;;
    "$HOME/.gemini/"*) echo "$HOME/.gemini/backup" ;;
    "$HOME/.codex/"*) echo "$HOME/.codex/backup" ;;
    *) echo "$(dirname "$1")/backup" ;;
  esac
}

needs_backup() {
  local src="$1"
  local dest="$2"

  if [ -L "$dest" ] && [ "$dest" -ef "$src" ]; then
    return 1
  fi

  [ -e "$dest" ] || [ -L "$dest" ]
}

confirm_overwrite() {
  if [ "$AUTO_CONFIRM" = true ]; then
    return 0
  fi

  local reply
  # 터미널 대화형 입력과 파이프라인(비대화형) 입력 모두 지원
  if [ -t 0 ]; then
    read -r -p "  기존 파일을 백업하고 덮어쓰시겠습니까? [y/n]: " reply || reply="n"
  else
    read -r reply || reply="n"
  fi

  [[ "$reply" =~ ^[yY]$ ]]
}

safe_link() {
  local src="$1"
  local dest="$2"
  local overwrite="$3"

  if [ ! -e "$src" ]; then
    echo "  원본 파일을 찾을 수 없습니다: $src" >&2
    return 1
  fi

  mkdir -p "$(dirname "$dest")"

  if [ -L "$dest" ] && [ "$dest" -ef "$src" ]; then
    echo "  이미 연결됨: $dest"
    return 0
  fi

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$overwrite" != true ]; then
      echo "  건너뜀: $dest"
      return 0
    fi

    local backup_dir
    backup_dir="$(backup_root "$dest")"
    mkdir -p "$backup_dir"
    local timestamp
    timestamp="$(date +%Y%m%d%H%M%S)"
    local backup_path="$backup_dir/$(basename "$dest").bak_${timestamp}"
    mv "$dest" "$backup_path"
    echo "  백업 완료: $dest -> $backup_path"
  fi

  ln -sfn "$src" "$dest"
  echo "  연결 완료: $dest -> $src"
}

link_group() {
  local label="$1"
  shift

  echo "==> $label 연결 중"

  local pair src dest
  local conflicts=()
  for pair in "$@"; do
    IFS=$'\t' read -r src dest <<<"$pair"
    if needs_backup "$src" "$dest"; then
      conflicts+=("$dest")
    fi
  done

  # 반복 승인 방지를 위한 카테고리별 덮어쓰기 일괄 확인
  local overwrite=true
  if [ "${#conflicts[@]}" -gt 0 ]; then
    echo "  기존 파일 ${#conflicts[@]}개:"
    printf '    %s\n' "${conflicts[@]}"
    if ! confirm_overwrite; then
      overwrite=false
    fi
  fi

  for pair in "$@"; do
    IFS=$'\t' read -r src dest <<<"$pair"
    safe_link "$src" "$dest" "$overwrite"
  done
}

configure_statusline_setting() {
  local target_json="$1"
  local cmd_type="$2"
  local cmd_val="$3"

  mkdir -p "$(dirname "$target_json")"
  if [ ! -f "$target_json" ]; then
    echo "{}" > "$target_json"
  fi

  if command -v jq >/dev/null 2>&1; then
    local current_type current_cmd
    current_type="$(jq -r '.statusLine.type // empty' "$target_json" 2>/dev/null || true)"
    current_cmd="$(jq -r '.statusLine.command // empty' "$target_json" 2>/dev/null || true)"
    if [ "$current_type" = "$cmd_type" ] && [ "$current_cmd" = "$cmd_val" ]; then
      echo "  이미 설정됨: $target_json"
      return 0
    fi

    local tmp
    tmp="$(mktemp)"
    if ! jq --arg type "$cmd_type" --arg cmd "$cmd_val" \
      '.statusLine = {type: $type, command: $cmd}' "$target_json" > "$tmp"; then
      rm -f "$tmp"
      echo "  경고: $target_json 이 올바른 JSON이 아니어서 statusLine 설정을 건너뜁니다" >&2
      return 0
    fi
    mv "$tmp" "$target_json"
  elif command -v node >/dev/null 2>&1; then
    if ! node -e '
      const fs = require("fs");
      const p = process.argv[1];
      const d = JSON.parse(fs.readFileSync(p, "utf-8"));
      d.statusLine = { type: process.argv[2], command: process.argv[3] };
      fs.writeFileSync(p, JSON.stringify(d, null, 2) + "\n", "utf-8");
    ' "$target_json" "$cmd_type" "$cmd_val" 2>/dev/null; then
      echo "  경고: $target_json 이 올바른 JSON이 아니어서 statusLine 설정을 건너뜁니다" >&2
      return 0
    fi
  else
    echo "  경고: jq 또는 node를 찾을 수 없어 $target_json 의 statusLine 설정을 건너뜁니다" >&2
    return 0
  fi
  echo "  statusLine 설정 완료: $target_json"
}

if [ "$INSTALL_RULES" = true ]; then
  link_group "규칙" \
    "$SCRIPT_DIR/rules/RULES.md"$'\t'"$HOME/.claude/CLAUDE.md" \
    "$SCRIPT_DIR/rules/RULES.md"$'\t'"$HOME/.gemini/GEMINI.md" \
    "$SCRIPT_DIR/rules/RULES.md"$'\t'"$HOME/.codex/AGENTS.md"
fi

if [ "$INSTALL_STATUSLINE" = true ]; then
  link_group "상태표시줄" \
    "$SCRIPT_DIR/statusline/agy-statusline.js"$'\t'"$HOME/.gemini/antigravity-cli/statusline.js" \
    "$SCRIPT_DIR/statusline/claude-statusline.sh"$'\t'"$HOME/.claude/statusline.sh" \
    "$SCRIPT_DIR/statusline/codex-runcat-hook.py"$'\t'"$HOME/.codex/runcat-hook.py"

  echo "==> settings.json에 상태표시줄 설정 등록 중"
  configure_statusline_setting "$HOME/.gemini/antigravity-cli/settings.json" "command" "node $HOME/.gemini/antigravity-cli/statusline.js"
  configure_statusline_setting "$HOME/.claude/settings.json" "command" "bash $HOME/.claude/statusline.sh"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/statusline/configure-codex.py" || echo "  Codex 상태줄 설정을 건너뜁니다" >&2
    if [ "$HOME/.codex/runcat-hook.py" -ef "$SCRIPT_DIR/statusline/codex-runcat-hook.py" ]; then
      python3 "$SCRIPT_DIR/statusline/configure-codex-runcat.py" "$HOME/.codex/runcat-hook.py" || echo "  Codex RunCat hook 설정을 건너뜁니다" >&2
    else
      echo "  RunCat hook 원본이 연결되지 않아 등록을 건너뜁니다" >&2
    fi
  else
    echo "  경고: python3을 찾을 수 없어 Codex 상태줄 설정을 건너뜁니다" >&2
  fi
fi

if [ "$INSTALL_SKILLS" = true ]; then
  TARGET_SKILL_DIRS=(
    "$HOME/.claude/skills"
    "$HOME/.gemini/config/skills"
    "$HOME/.codex/skills"
  )

  # 외부 스킬 보존을 위한 저장소 소유 끊어진 링크만 제거
  for target_dir in "${TARGET_SKILL_DIRS[@]}"; do
    for link in "$target_dir"/*; do
      [ -L "$link" ] && [ ! -e "$link" ] && [ "$(dirname "$(readlink "$link")")" -ef "$SCRIPT_DIR/skills" ] || continue
      rm "$link"
      echo "  삭제된 스킬 링크 제거: $link"
    done
  done

  skill_pairs=()
  for target_dir in "${TARGET_SKILL_DIRS[@]}"; do
    for skill_path in "$SCRIPT_DIR"/skills/*/; do
      [ -d "$skill_path" ] || continue
      skill_pairs+=("$skill_path"$'\t'"$target_dir/$(basename "$skill_path")")
    done
  done

  if [ "${#skill_pairs[@]}" -gt 0 ]; then
    link_group "스킬" "${skill_pairs[@]}"
  fi
fi
