import json
from pathlib import Path

from faster_whisper_GUI.util import clear_temp_srt_files, ensure_directory, ensure_file


def test_default_settings_enable_startup_model_autoload():
    config = json.loads(Path("fasterWhisperGUIConfig.json").read_text(encoding="utf-8"))

    assert config["setting"]["autoLoadModel"] is True


def test_startup_model_autoload_setting_is_not_forced_off_by_save_config_switch():
    source = Path("faster_whisper_GUI/settingPageNavigation.py").read_text(encoding="utf-8")

    assert "self.switchButton_autoLoadModel.setChecked(False)" not in source
    assert "self.paramItemWidget_autoLoadModel.setEnabled(self.switchButton_saveConfig.isChecked())" not in source
    assert 'param["autoLoadModel"] = self.switchButton_autoLoadModel.isChecked()' in source


def test_tracked_qfluentwidgets_config_only_contains_shared_theme_settings():
    config = json.loads(Path("config/config.json").read_text(encoding="utf-8"))

    assert set(config["QFluentWidgets"]) == {"ThemeColor", "ThemeMode"}


def test_clear_temp_srt_files_only_removes_srt_files(tmp_path):
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "one.srt").write_text("subtitle", encoding="utf-8")
    (temp_dir / "two.SRT").write_text("subtitle", encoding="utf-8")
    (temp_dir / "keep.txt").write_text("keep", encoding="utf-8")

    assert clear_temp_srt_files(temp_dir) == 2
    assert not (temp_dir / "one.srt").exists()
    assert not (temp_dir / "two.SRT").exists()
    assert (temp_dir / "keep.txt").exists()


def test_clear_temp_srt_files_allows_missing_temp_dir(tmp_path):
    assert clear_temp_srt_files(tmp_path / "missing") == 0


def test_ensure_directory_creates_missing_directory(tmp_path):
    path = ensure_directory(tmp_path / "new-temp")

    assert path.exists()
    assert path.is_dir()


def test_ensure_file_creates_parent_directory_and_file(tmp_path):
    path = ensure_file(tmp_path / "logs" / "app.log")

    assert path.exists()
    assert path.is_file()


def test_transcribe_temp_directory_uses_shared_directory_helper():
    source = Path("faster_whisper_GUI/transcribe.py").read_text(encoding="utf-8")

    assert "ensure_directory" in source
    assert "os.mkdir" not in source


def test_split_audio_csv_writer_uses_context_manager_and_safe_makedirs():
    source = Path("faster_whisper_GUI/split_audio.py").read_text(encoding="utf-8")

    assert "with open(" in source
    assert "list_file.close()" not in source
    assert "exist_ok=True" in source
