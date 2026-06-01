from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG = REPO_ROOT / "user" / "fasterWhisperGUIConfig.local.json"
DEFAULT_CONFIG = REPO_ROOT / "fasterWhisperGUIConfig.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)


def get_startup_config_path() -> Path:
    if LOCAL_CONFIG.exists():
        return LOCAL_CONFIG
    return DEFAULT_CONFIG


def get_model_target(config: dict) -> str:
    model_param = config.get("model_param", {})
    if model_param.get("localModel", True):
        return str(model_param.get("model_path", "")).strip()
    return str(model_param.get("modelName", "")).strip()


def is_model_target_accessible(config: dict, model_target: str) -> bool:
    if not model_target:
        return False
    model_param = config.get("model_param", {})
    if not model_param.get("localModel", True):
        return True
    try:
        return Path(model_target).is_dir()
    except OSError:
        return False


def check_source_run_rc() -> tuple[bool, list[str]]:
    messages = []
    config_path = get_startup_config_path()
    config = load_json(config_path)
    auto_load = bool(config.get("setting", {}).get("autoLoadModel", False))
    model_target = get_model_target(config)
    model_target_accessible = is_model_target_accessible(config, model_target)

    messages.append(f"startup_config={config_path.relative_to(REPO_ROOT)}")
    messages.append(f"autoLoadModel={auto_load}")
    messages.append(f"hasModelTarget={bool(model_target)}")
    messages.append(f"modelTargetAccessible={model_target_accessible}")

    ok = auto_load and bool(model_target) and model_target_accessible
    if not auto_load:
        messages.append("action=enable 自动加载模型 in settings")
    if not model_target:
        messages.append("action=select a model once in the GUI")
    elif not model_target_accessible:
        messages.append("action=select a readable local model path")
    return ok, messages


def main() -> int:
    try:
        ok, messages = check_source_run_rc()
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"config_check_error={error}")
        return 1

    for message in messages:
        print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
