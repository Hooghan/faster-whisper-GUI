import json
from pathlib import Path

from tools.seed_packaged_local_config import sanitize_config, seed_packaged_local_config


def test_packaged_local_config_seed_keeps_model_path_but_strips_token(tmp_path):
    source_config = tmp_path / "user" / "fasterWhisperGUIConfig.local.json"
    package_config = tmp_path / "dist" / "app" / "user" / "fasterWhisperGUIConfig.local.json"
    source_config.parent.mkdir()
    source_config.write_text(
        json.dumps(
            {
                "model_param": {"model_path": "C:/models/faster-whisper"},
                "setting": {"huggingface_user_token": "hf_secret"},
            }
        ),
        encoding="utf-8",
    )

    seed_packaged_local_config(
        source_config=source_config,
        default_config=tmp_path / "missing-default.json",
        package_config=package_config,
    )

    seeded = json.loads(package_config.read_text(encoding="utf-8"))
    assert seeded["model_param"]["model_path"] == "C:/models/faster-whisper"
    assert seeded["setting"]["huggingface_user_token"] == ""


def test_packaged_local_config_seed_falls_back_to_default_config(tmp_path):
    default_config = tmp_path / "fasterWhisperGUIConfig.json"
    package_config = tmp_path / "dist" / "app" / "user" / "fasterWhisperGUIConfig.local.json"
    default_config.write_text(
        json.dumps(
            {
                "model_param": {"model_path": ""},
                "setting": {"huggingface_user_token": "hf_secret"},
            }
        ),
        encoding="utf-8",
    )

    seed_packaged_local_config(
        source_config=tmp_path / "missing-local.json",
        default_config=default_config,
        package_config=package_config,
    )

    seeded = json.loads(package_config.read_text(encoding="utf-8"))
    assert seeded["model_param"]["model_path"] == ""
    assert seeded["setting"]["huggingface_user_token"] == ""


def test_sanitize_config_does_not_mutate_original():
    config = {"setting": {"huggingface_user_token": "hf_secret"}}

    sanitized = sanitize_config(config)

    assert sanitized["setting"]["huggingface_user_token"] == ""
    assert config["setting"]["huggingface_user_token"] == "hf_secret"
