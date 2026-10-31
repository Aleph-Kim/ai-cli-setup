import json
import os
import shlex
import stat
import sys
import tempfile
from pathlib import Path


if len(sys.argv) != 2:
    sys.exit("사용법: configure-codex-runcat.py <hook-script>")

config_path = Path.home() / ".codex" / "hooks.json"
config_path.parent.mkdir(parents=True, exist_ok=True)
try:
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
except json.JSONDecodeError:
    sys.exit(f"경고: {config_path}이 올바른 JSON이 아닙니다")

hooks = config.setdefault("hooks", {})
if not isinstance(hooks, dict):
    sys.exit(f"경고: {config_path}의 hooks 값을 확인해야 합니다")
stop_hooks = hooks.setdefault("Stop", [])
if not isinstance(stop_hooks, list):
    sys.exit(f"경고: {config_path}의 Stop hook 값을 확인해야 합니다")

script_path = str(Path(sys.argv[1]).expanduser())
command = shlex.quote(script_path)
registered = False
for group in stop_hooks:
    if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
        continue
    for item in group["hooks"]:
        if not isinstance(item, dict):
            continue
        existing = item.get("command")
        if existing in (command, script_path, str(Path.home() / ".codex" / "runcat-hook.py")):
            item["command"] = command
            registered = True

if not registered:
    stop_hooks.append({"hooks": [{"type": "command", "command": command, "timeout": 5}]})

mode = stat.S_IMODE(config_path.stat().st_mode) if config_path.exists() else 0o600
temporary = None
try:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=config_path.parent, delete=False) as file:
        temporary = Path(file.name)
        json.dump(config, file, ensure_ascii=False, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
        os.fchmod(file.fileno(), mode)
    os.replace(temporary, config_path)
finally:
    if temporary is not None:
        temporary.unlink(missing_ok=True)

print(f"Codex RunCat hook 설정 완료: {config_path}")
