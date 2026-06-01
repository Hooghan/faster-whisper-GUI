from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_LOCAL_CONFIG = REPO_ROOT / "user" / "fasterWhisperGUIConfig.local.json"
DEFAULT_CONFIG = REPO_ROOT / "fasterWhisperGUIConfig.json"
PACKAGE_LOCAL_CONFIG = (
    REPO_ROOT
    / "dist"
    / "FasterWhisperGUI-0.8.6-dev-source"
    / "user"
    / "fasterWhisperGUIConfig.local.json"
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)


def sanitize_config(config: dict) -> dict:
    sanitized = dict(config)
    setting = dict(sanitized.get("setting", {}))
    setting["huggingface_user_token"] = ""
    sanitized["setting"] = setting
    return sanitized


def seed_packaged_local_config(
    source_config: Path = SOURCE_LOCAL_CONFIG,
    default_config: Path = DEFAULT_CONFIG,
    package_config: Path = PACKAGE_LOCAL_CONFIG,
) -> Path:
    config_path = source_config if source_config.exists() else default_config
    config = sanitize_config(load_json(config_path))

    package_config.parent.mkdir(parents=True, exist_ok=True)
    package_config.write_text(
        json.dumps(config, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    return package_config


def main() -> int:
    output_path = seed_packaged_local_config()
    print(f"seeded_package_config={output_path}")
    print("huggingface_user_token=")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
