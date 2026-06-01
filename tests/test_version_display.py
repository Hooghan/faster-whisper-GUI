from importlib import metadata

from faster_whisper_GUI.version import (
    __FasterWhisper_version__,
    __WhisperX_version__,
    __version__,
)


def test_faster_whisper_display_version_matches_installed_package():
    assert __FasterWhisper_version__ == metadata.version("faster-whisper")


def test_faster_whisper_display_version_is_not_stale_legacy_value():
    if metadata.version("faster-whisper") != "1.1.0":
        assert __FasterWhisper_version__ != "1.1.0"


def test_app_display_version_marks_continuation_build():
    assert __version__ == "0.8.6-dev"


def test_whisperx_display_version_marks_vendored_code():
    assert __WhisperX_version__ == "vendored"
