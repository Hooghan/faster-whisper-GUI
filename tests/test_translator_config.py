import json

from faster_whisper_GUI import translator


def test_translator_loads_language_config_from_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"setting": {"language": 1}}),
        encoding="utf-8",
    )

    assert translator.load_language_config(config_path) == 1


def test_translator_falls_back_to_auto_language_for_invalid_config(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{not-json", encoding="utf-8")

    assert translator.load_language_config(config_path) == 2


def test_translator_falls_back_to_auto_language_for_missing_config(tmp_path):
    assert translator.load_language_config(tmp_path / "missing.json") == 2
