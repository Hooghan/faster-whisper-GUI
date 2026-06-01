from pathlib import Path


PYTEST_INI_TEXT = Path("pytest.ini").read_text(encoding="utf-8")


def test_pytest_filters_known_vendored_whisperx_dependency_warning_noise():
    assert "filterwarnings" in PYTEST_INI_TEXT
    assert "SwigPyPacked" in PYTEST_INI_TEXT
    assert "torchaudio\\._backend\\.set_audio_backend" in PYTEST_INI_TEXT
    assert "speechbrain\\.pretrained" in PYTEST_INI_TEXT
    assert "AudioMetaData" in PYTEST_INI_TEXT
