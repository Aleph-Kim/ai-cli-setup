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

# CLI 옵션 파싱
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
      echo "unknown option: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

# 백업은 각 CLI 홈 바로 아래로 모은다 (skills 하위에 남으면 스킬로 오인식됨)
backup_root() {
  case "$1" in
    "$HOME/.claude/"*) echo "$HOME/.claude/backup" ;;
    "$HOME/.gemini/"*) echo "$HOME/.gemini/backup" ;;
    *) echo "$(dirname "$1")/backup" ;;
  esac
}

# 이미 동일 원본을 가리키는 링크면 백업 대상에서 제외
needs_backup() {
  local src="$1"
  local dest="$2"

  if [ -L "$dest" ] && [ "$(readlink "$dest" || true)" = "$src" ]; then
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
    echo "  source not found: $src" >&2
    return 1
  fi

  mkdir -p "$(dirname "$dest")"

  if [ -L "$dest" ] && [ "$(readlink "$dest" || true)" = "$src" ]; then
    echo "  already linked: $dest"
    return 0
  fi

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$overwrite" != true ]; then
      echo "  skipped: $dest"
      return 0
    fi

    local backup_dir
    backup_dir="$(backup_root "$dest")"
    mkdir -p "$backup_dir"
    local timestamp
    timestamp="$(date +%Y%m%d%H%M%S)"
    local backup_path="$backup_dir/$(basename "$dest").bak_${timestamp}"
    mv "$dest" "$backup_path"
    echo "  backup: $dest -> $backup_path"
  fi

  ln -sfn "$src" "$dest"
  echo "  linked: $dest -> $src"
}

# 카테고리 단위로 덮어쓰기 여부를 한 번만 확인 (인자: 라벨, "원본<TAB>대상" 목록)
link_group() {
  local label="$1"
  shift

  echo "==> Linking $label"

  local pair src dest
  local conflicts=()
  for pair in "$@"; do
    IFS=$'\t' read -r src dest <<<"$pair"
    if needs_backup "$src" "$dest"; then
      conflicts+=("$dest")
    fi
  done

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

# 단일 원본 규칙 파일을 각 CLI(Claude, AGY) 기대 경로에 심볼릭 링크
if [ "$INSTALL_RULES" = true ]; then
  link_group "rules" \
    "$SCRIPT_DIR/rules/RULES.md"$'\t'"$HOME/.claude/CLAUDE.md" \
    "$SCRIPT_DIR/rules/RULES.md"$'\t'"$HOME/.gemini/GEMINI.md"
fi

# 상태표시줄 커스텀 스크립트 연결
if [ "$INSTALL_STATUSLINE" = true ]; then
  link_group "statusline" \
    "$SCRIPT_DIR/statusline/agy-statusline.js"$'\t'"$HOME/.gemini/antigravity-cli/statusline.js" \
    "$SCRIPT_DIR/statusline/claude-statusline.sh"$'\t'"$HOME/.claude/statusline.sh"
fi

# 각 CLI의 전역 스킬 디렉토리로 개별 스킬 폴더 심볼릭 링크
if [ "$INSTALL_SKILLS" = true ]; then
  TARGET_SKILL_DIRS=(
    "$HOME/.claude/skills"
    "$HOME/.gemini/config/skills"
  )

  skill_pairs=()
  for target_dir in "${TARGET_SKILL_DIRS[@]}"; do
    for skill_path in "$SCRIPT_DIR"/skills/*/; do
      [ -d "$skill_path" ] || continue
      skill_pairs+=("$skill_path"$'\t'"$target_dir/$(basename "$skill_path")")
    done
  done

  if [ "${#skill_pairs[@]}" -gt 0 ]; then
    link_group "skills" "${skill_pairs[@]}"
  fi
fi
