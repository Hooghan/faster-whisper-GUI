from pathlib import Path
import json


CONFIG_TEXT = Path("faster_whisper_GUI/config.py").read_text(encoding="utf-8")
DEFAULT_GUI_CONFIG_TEXT = Path("fasterWhisperGUIConfig.json").read_text(
    encoding="utf-8"
)
DEFAULT_GUI_CONFIG = json.loads(DEFAULT_GUI_CONFIG_TEXT)
HUGGINGFACE_CONFIG_TEXT = Path("huggingface-config.json").read_text(encoding="utf-8")
HUGGINGFACE_CONFIG = json.loads(HUGGINGFACE_CONFIG_TEXT)
SETTING_PAGE_TEXT = Path("faster_whisper_GUI/settingPageNavigation.py").read_text(
    encoding="utf-8"
)


def test_source_config_has_no_hugging_face_access_token_literal():
    assert "hf_" not in CONFIG_TEXT


def test_default_gui_config_has_no_hugging_face_access_token_literal():
    assert "hf_" not in DEFAULT_GUI_CONFIG_TEXT


def test_default_gui_config_has_no_machine_specific_model_or_cache_paths():
    model_param = DEFAULT_GUI_CONFIG["model_param"]

    assert model_param["model_path"] == ""
    assert model_param["download_root"] == ""
    assert "C:/Users/" not in DEFAULT_GUI_CONFIG_TEXT
    assert "F:/WhisperModels/" not in DEFAULT_GUI_CONFIG_TEXT


def test_huggingface_config_is_a_machine_neutral_template():
    assert "hf_" not in HUGGINGFACE_CONFIG_TEXT
    assert "127.0.0.1" not in HUGGINGFACE_CONFIG_TEXT
    assert HUGGINGFACE_CONFIG["proxy"] == {"http": "", "https": ""}


def test_saved_settings_do_not_persist_hugging_face_token_to_portable_backups():
    main_windows_text = Path("faster_whisper_GUI/mainWindows.py").read_text(
        encoding="utf-8"
    )

    assert 'setting_param["huggingface_user_token"] = ""' in main_windows_text
    assert "is_local_private_config" in main_windows_text


def test_settings_page_explains_users_must_use_their_own_hugging_face_token():
    assert "你自己的 Hugging Face 用户令牌" in SETTING_PAGE_TEXT
    assert "账号需先同意 pyannote 模型授权" in SETTING_PAGE_TEXT
    assert "不会内置或分发他人的令牌" in SETTING_PAGE_TEXT
    assert 'param["huggingface_user_token"] = self.LineEdit_use_auth_token.text().strip()' in SETTING_PAGE_TEXT
