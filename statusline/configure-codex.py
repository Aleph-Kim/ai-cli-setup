import re
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ImportError:
    sys.exit("  경고: Codex 상태줄 설정에 Python 3.11 이상이 필요합니다")

path = Path.home() / ".codex" / "config.toml"
path = path.resolve()
content = path.read_text(encoding="utf-8") if path.exists() else ""
try:
    config = tomllib.loads(content)
except tomllib.TOMLDecodeError:
    sys.exit(f"  경고: {path}의 TOML이 올바르지 않아 설정을 건너뜁니다")

tui = config.get("tui", {})
if not isinstance(tui, dict):
    sys.exit("  경고: 기존 tui 설정을 확인해야 합니다")
items = tui.get("status_line", ["model-with-reasoning", "context-used", "five-hour-limit", "weekly-limit"])
if items is None:
    print(f"  기존 상태줄 설정 유지: {path}")
    sys.exit(0)
if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
    sys.exit("  경고: 기존 status_line 설정을 확인해야 합니다")
updated_items = [item for item in items if item != "access"]
for item in ("permissions", "approval-mode"):
    if item not in updated_items:
        updated_items.append(item)
if updated_items == items:
    print(f"  기존 상태줄 설정 유지: {path}")
    sys.exit(0)
items = updated_items

setting = "status_line = " + json.dumps(items) + "\n"
expected = dict(config)
expected["tui"] = {**tui, "status_line": items}
candidates = []
if "status_line" in tui:
    for match in re.finditer(r"(?ms)^[ \t]*status_line[ \t]*=[ \t]*\[.*?\]", content):
        candidates.append(content[:match.start()] + setting.rstrip("\n") + content[match.end():])
for header in re.finditer(r"(?m)^[ \t]*\[tui\][ \t]*(?:#.*)?$", content):
    position = header.end()
    candidates.append(content[:position] + "\n" + setting + content[position:].lstrip("\n"))
if "tui" not in config:
    candidates.append(content.rstrip() + "\n\n[tui]\n" + setting)
for updated in candidates:
    try:
        if tomllib.loads(updated) == expected:
            break
    except tomllib.TOMLDecodeError:
        pass
else:
    sys.exit(f"  경고: {path}에 상태줄을 안전하게 추가할 수 없습니다")

path.parent.mkdir(parents=True, exist_ok=True)
mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
temporary = None
try:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        file.write(updated)
        file.flush()
        os.fsync(file.fileno())
        os.fchmod(file.fileno(), mode)
    os.replace(temporary, path)
finally:
    if temporary is not None:
        temporary.unlink(missing_ok=True)
print(f"  Codex 상태줄 설정 완료: {path}")
