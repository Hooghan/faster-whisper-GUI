import json

from tools import source_run_rc_check


def test_source_run_rc_check_prefers_local_config(monkeypatch, tmp_path):
    local_config = tmp_path / "user" / "fasterWhisperGUIConfig.local.json"
    default_config = tmp_path / "fasterWhisperGUIConfig.json"
    local_config.parent.mkdir()
    local_config.write_text("{}", encoding="utf-8")
    default_config.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(source_run_rc_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(source_run_rc_check, "LOCAL_CONFIG", local_config)
    monkeypatch.setattr(source_run_rc_check, "DEFAULT_CONFIG", default_config)

    assert source_run_rc_check.get_startup_config_path() == local_config


def test_source_run_rc_check_passes_with_autoload_and_model_target(monkeypatch, tmp_path):
    config_path = tmp_path / "fasterWhisperGUIConfig.json"
    model_path = tmp_path / "models" / "fw"
    model_path.mkdir(parents=True)
    config_path.write_text(
        json.dumps(
            {
                "setting": {"autoLoadModel": True},
                "model_param": {"localModel": True, "model_path": str(model_path)},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(source_run_rc_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(source_run_rc_check, "LOCAL_CONFIG", tmp_path / "missing.json")
    monkeypatch.setattr(source_run_rc_check, "DEFAULT_CONFIG", config_path)

    ok, messages = source_run_rc_check.check_source_run_rc()

    assert ok
    assert "autoLoadModel=True" in messages
    assert "hasModelTarget=True" in messages
    assert "modelTargetAccessible=True" in messages


def test_source_run_rc_check_fails_without_model_target(monkeypatch, tmp_path):
    config_path = tmp_path / "fasterWhisperGUIConfig.json"
    config_path.write_text(
        json.dumps(
            {
                "setting": {"autoLoadModel": True},
                "model_param": {"localModel": True, "model_path": "   "},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(source_run_rc_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(source_run_rc_check, "LOCAL_CONFIG", tmp_path / "missing.json")
    monkeypatch.setattr(source_run_rc_check, "DEFAULT_CONFIG", config_path)

    ok, messages = source_run_rc_check.check_source_run_rc()

    assert not ok
    assert "hasModelTarget=False" in messages


def test_source_run_rc_check_fails_when_local_model_target_is_not_accessible(monkeypatch, tmp_path):
    config_path = tmp_path / "fasterWhisperGUIConfig.json"
    config_path.write_text(
        json.dumps(
            {
                "setting": {"autoLoadModel": True},
                "model_param": {"localModel": True, "model_path": str(tmp_path / "missing-model")},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(source_run_rc_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(source_run_rc_check, "LOCAL_CONFIG", tmp_path / "missing.json")
    monkeypatch.setattr(source_run_rc_check, "DEFAULT_CONFIG", config_path)

    ok, messages = source_run_rc_check.check_source_run_rc()

    assert not ok
    assert "modelTargetAccessible=False" in messages
