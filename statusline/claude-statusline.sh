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

runcat_reset() {
  [ -n "$1" ] || return 0
  if [ "$(date -r "$1" +%F)" = "$(date +%F)" ]; then
    date -r "$1" '+~%H:%M'
  else
    date -r "$1" '+~%-m/%-d %H:%M'
  fi
}

# RunCat Neo Custom Metrics 카드용 스냅샷, 임시 파일 경유 교체로 쓰는 도중의 파일 읽힘 방지
runcat_out="$HOME/.claude/runcat-usage.json"
if runcat_tmp=$(mktemp "$runcat_out.XXXXXX" 2>/dev/null); then
  if echo "$input" | jq -c \
    --arg model "$model" \
    --arg r5 "$(runcat_reset "$resets_at")" \
    --arg r7 "$(runcat_reset "$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')")" \
    --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
    def row($t; $v; $r):
      if $v == null then empty
      else {title: $t, formattedValue: "\($v | round)%\(if $r == "" then "" else " (\($r))" end)", normalizedValue: ($v / 100)}
      end;
    .rate_limits.five_hour.used_percentage as $five
    | {
        title: "Claude Code",
        symbol: "staroflife",
        metrics: [
          {title: "Model", formattedValue: $model},
          row("Context"; .context_window.used_percentage; ""),
          row("5h"; $five; $r5),
          row("7d"; .rate_limits.seven_day.used_percentage; $r7)
        ],
        lastUpdatedDate: $now
      }
      + (if $five == null then {} else {metricsBarValue: "\($five | round)%"} end)
  ' > "$runcat_tmp" 2>/dev/null; then
    mv "$runcat_tmp" "$runcat_out"
  else
    rm -f "$runcat_tmp"
  fi
fi

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
