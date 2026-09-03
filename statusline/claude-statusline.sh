#!/usr/bin/env bash
# Claude Code Custom Statusline Script
# Format: {model} | {5h_used}% current (reset {time}) | {weekly_used}% week   {email}

set -u

input=$(cat)
cfg="${CLAUDE_CONFIG_DIR:+$CLAUDE_CONFIG_DIR/.claude.json}"
cfg="${cfg:-$HOME/.claude.json}"

email=$(jq -r '.oauthAccount.emailAddress // empty' "$cfg" 2>/dev/null)
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
current=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
resets_at=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')

[ -n "$current" ] && current=$(printf '%.0f' "$current") || current="n/a"
[ -n "$week" ] && week=$(printf '%.0f' "$week") || week="n/a"

reset_str=""
[ -n "$resets_at" ] && reset_str=$(date -r "$resets_at" '+%H:%M' 2>/dev/null)

if [ -n "$reset_str" ]; then
  left=$(printf '%s | %s%% current (reset %s) | %s%% week' "$model" "$current" "$reset_str" "$week")
else
  left=$(printf '%s | %s%% current | %s%% week' "$model" "$current" "$week")
fi

if [ -n "$email" ] && [ -n "${COLUMNS-}" ]; then
  margin=4
  usable=$((COLUMNS - margin))
  gap=$((usable - ${#left} - ${#email}))
  [ "$gap" -lt 2 ] && gap=2
  printf '%s%*s%s' "$left" "$gap" "" "$email"
else
  printf '%s%s' "$left" "${email:+  $email}"
fi
