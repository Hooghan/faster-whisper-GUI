from pathlib import Path

from faster_whisper_GUI import UI_MainWindows


def test_local_config_path_is_under_ignored_user_directory():
    assert UI_MainWindows.get_local_config_path().as_posix() == "user/fasterWhisperGUIConfig.local.json"


def test_qfluentwidgets_config_path_is_under_ignored_user_directory():
    assert UI_MainWindows.get_qfluentwidgets_local_config_path().as_posix() == "user/qfluentwidgets.local.json"


def test_packaged_default_config_path_reads_from_pyinstaller_internal(monkeypatch, tmp_path):
    packaged_exe = tmp_path / "dist" / "FasterWhisperGUI.exe"
    packaged_internal = tmp_path / "dist" / "_internal"

    monkeypatch.setattr(UI_MainWindows.sys, "frozen", True, raising=False)
    monkeypatch.setattr(UI_MainWindows.sys, "executable", str(packaged_exe))
    monkeypatch.setattr(UI_MainWindows.sys, "_MEIPASS", str(packaged_internal), raising=False)

    assert UI_MainWindows.get_default_config_path() == packaged_internal / "fasterWhisperGUIConfig.json"


def test_packaged_local_config_path_writes_next_to_executable(monkeypatch, tmp_path):
    packaged_exe = tmp_path / "dist" / "FasterWhisperGUI.exe"
    packaged_internal = tmp_path / "dist" / "_internal"

    monkeypatch.setattr(UI_MainWindows.sys, "frozen", True, raising=False)
    monkeypatch.setattr(UI_MainWindows.sys, "executable", str(packaged_exe))
    monkeypatch.setattr(UI_MainWindows.sys, "_MEIPASS", str(packaged_internal), raising=False)

    assert UI_MainWindows.get_local_config_path() == tmp_path / "dist" / "user" / "fasterWhisperGUIConfig.local.json"
    assert UI_MainWindows.get_qfluentwidgets_local_config_path() == tmp_path / "dist" / "user" / "qfluentwidgets.local.json"


def test_qfluentwidgets_config_is_routed_to_local_config(monkeypatch, tmp_path):
    original_qconfig_file = UI_MainWindows.qconfig.file
    local_config = tmp_path / "user" / "qfluentwidgets.local.json"
    monkeypatch.setattr(UI_MainWindows, "QFLUENTWIDGETS_LOCAL_CONFIG_PATH", local_config)
    monkeypatch.setattr(UI_MainWindows.qconfig, "file", original_qconfig_file)

    UI_MainWindows.configure_qfluentwidgets_local_config()

    assert UI_MainWindows.qconfig.file == local_config
    assert UI_MainWindows.qconfig._cfg.file == local_config


def test_qfluentwidgets_save_writes_to_local_config(monkeypatch, tmp_path):
    local_config = tmp_path / "user" / "qfluentwidgets.local.json"
    monkeypatch.setattr(UI_MainWindows, "QFLUENTWIDGETS_LOCAL_CONFIG_PATH", local_config)

    UI_MainWindows.configure_qfluentwidgets_local_config()
    UI_MainWindows.qconfig.save()

    assert local_config.exists()


def test_startup_config_prefers_local_config_when_present(tmp_path, monkeypatch):
    local_config = tmp_path / "user" / "fasterWhisperGUIConfig.local.json"
    default_config = tmp_path / "fasterWhisperGUIConfig.json"
    local_config.parent.mkdir()
    local_config.write_text("{}", encoding="utf-8")
    default_config.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(UI_MainWindows, "LOCAL_CONFIG_PATH", local_config)
    monkeypatch.setattr(UI_MainWindows, "DEFAULT_CONFIG_PATH", default_config)

    assert UI_MainWindows.get_startup_config_path() == local_config


def test_startup_config_falls_back_to_default_config(tmp_path, monkeypatch):
    local_config = tmp_path / "user" / "fasterWhisperGUIConfig.local.json"
    default_config = tmp_path / "fasterWhisperGUIConfig.json"
    default_config.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(UI_MainWindows, "LOCAL_CONFIG_PATH", local_config)
    monkeypatch.setattr(UI_MainWindows, "DEFAULT_CONFIG_PATH", default_config)

    assert UI_MainWindows.get_startup_config_path() == default_config


def test_close_event_saves_to_local_config_not_tracked_default():
    source = Path("faster_whisper_GUI/mainWindows.py").read_text(encoding="utf-8")

    close_event_source = source.split("def closeEvent", 1)[1]
    close_event_source = close_event_source.split("def saveConfig", 1)[0]

    assert "get_local_config_path()" in close_event_source
    assert "fasterWhisperGUIConfig.json" not in close_event_source


def test_gitignore_ignores_local_user_config_files():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "user/*.local.json" in gitignore


def test_gitignore_ignores_isolated_upstream_whisperx_environment():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert ".venv-whisperx-next/" in gitignore
