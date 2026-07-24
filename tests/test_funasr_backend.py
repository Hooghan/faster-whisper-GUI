import importlib.util
import builtins
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "faster_whisper_GUI" / "funasr_backend.py"
SPEC = importlib.util.spec_from_file_location("funasr_backend_test_module", MODULE_PATH)
funasr_backend = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = funasr_backend
SPEC.loader.exec_module(funasr_backend)

FunASRWhisperCompatibleModel = funasr_backend.FunASRWhisperCompatibleModel
funasr_results_to_segments = funasr_backend.funasr_results_to_segments
normalize_funasr_language = funasr_backend.normalize_funasr_language


def test_normalize_gui_language_values():
    assert normalize_funasr_language(None) == "auto"
    assert normalize_funasr_language("Auto") == "auto"
    assert normalize_funasr_language("zhs") == "zh"
    assert normalize_funasr_language("zht") == "zh"
    assert normalize_funasr_language("zh-CN") == "zh"
    assert normalize_funasr_language("yue") == "yue"


def test_convert_sentence_info_to_segments():
    segments = funasr_results_to_segments(
        [
            {
                "text": "ignored when sentence_info exists",
                "sentence_info": [
                    {"text": "hello", "start": 0, "end": 1200},
                    {"text": "world", "start": 1200, "end": 2500},
                ],
            }
        ]
    )

    assert [(s.start, s.end, s.text) for s in segments] == [
        (0.0, 1.2, "hello"),
        (1.2, 2.5, "world"),
    ]


def test_convert_flat_timestamp_result_to_segment():
    segments = funasr_results_to_segments(
        [{"text": "welcome", "timestamp": [[0, 800], [800, 1600]]}]
    )

    assert len(segments) == 1
    assert segments[0].start == 0.0
    assert segments[0].end == 1.6
    assert segments[0].text == "welcome"


def test_convert_subsecond_millisecond_timestamps():
    segments = funasr_results_to_segments(
        [{"text": "short", "sentence_info": [{"text": "short", "start": 120, "end": 800}]}]
    )

    assert [(s.start, s.end, s.text) for s in segments] == [(0.12, 0.8, "short")]


def test_single_untimed_result_uses_media_duration():
    segments = funasr_results_to_segments(
        [{"text": "SenseVoice result without timestamps"}],
        fallback_duration=5.25,
    )

    assert [(s.start, s.end, s.text) for s in segments] == [
        (0.0, 5.25, "SenseVoice result without timestamps")
    ]


def test_model_transcribe_uses_funasr_generate_contract():
    class FakeAutoModel:
        def __init__(self):
            self.calls = []

        def generate(self, **kwargs):
            self.calls.append(kwargs)
            return [{"text": "ok", "start": 0, "end": 1000}]

    fake = FakeAutoModel()
    model = FunASRWhisperCompatibleModel()
    model._model = fake

    segments, info = model.transcribe("sample.wav", language="zh-CN", hotwords="FunASR")

    assert fake.calls == [
        {
            "input": "sample.wav",
            "sentence_timestamp": True,
            "language": "zh",
            "hotword": "FunASR",
        }
    ]
    assert [(s.start, s.end, s.text) for s in segments] == [(0.0, 1.0, "ok")]
    assert info.language == "zh"
    assert info.duration == 1.0


def test_model_transcribe_cleans_sensevoice_tags_and_detects_language():
    class FakeAutoModel:
        def generate(self, **kwargs):
            return [
                {
                    "text": "<|en|><|NEUTRAL|><|Speech|><|woitn|>hello",
                    "start": 0,
                    "end": 800,
                }
            ]

    model = FunASRWhisperCompatibleModel()
    model._model = FakeAutoModel()

    segments, info = model.transcribe("sample.wav")

    assert [(s.start, s.end, s.text) for s in segments] == [(0.0, 0.8, "hello")]
    assert info.language == "en"


def test_model_transcribe_uses_media_duration_for_untimed_result():
    class FakeAutoModel:
        def generate(self, **kwargs):
            return [{"text": "untimed"}]

    original_duration_reader = getattr(funasr_backend, "_media_duration_seconds", None)
    funasr_backend._media_duration_seconds = lambda _: 4.75
    try:
        model = FunASRWhisperCompatibleModel()
        model._model = FakeAutoModel()

        segments, info = model.transcribe("sample.wav")

        assert [(s.start, s.end, s.text) for s in segments] == [(0.0, 4.75, "untimed")]
        assert info.duration == 4.75
    finally:
        if original_duration_reader is None:
            del funasr_backend._media_duration_seconds
        else:
            funasr_backend._media_duration_seconds = original_duration_reader


def test_model_transcribe_rejects_unsupported_translation_task():
    model = FunASRWhisperCompatibleModel()
    model._model = object()

    try:
        model.transcribe("sample.wav", task="translate")
    except ValueError as exc:
        assert "does not support translation" in str(exc)
    else:
        raise AssertionError("unsupported translation must not be silently transcribed")


def test_missing_optional_dependency_fails_during_load():
    real_import = builtins.__import__

    def import_without_funasr(name, *args, **kwargs):
        if name == "funasr":
            raise ImportError("missing in test")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = import_without_funasr
    try:
        model = FunASRWhisperCompatibleModel()
        try:
            model.load()
        except RuntimeError as exc:
            assert 'pip install "funasr>=1.3.29"' in str(exc)
        else:
            raise AssertionError("loading without FunASR should fail")
    finally:
        builtins.__import__ = real_import


if __name__ == "__main__":
    test_normalize_gui_language_values()
    test_convert_sentence_info_to_segments()
    test_convert_flat_timestamp_result_to_segment()
    test_convert_subsecond_millisecond_timestamps()
    test_single_untimed_result_uses_media_duration()
    test_model_transcribe_uses_funasr_generate_contract()
    test_model_transcribe_cleans_sensevoice_tags_and_detects_language()
    test_model_transcribe_uses_media_duration_for_untimed_result()
    test_model_transcribe_rejects_unsupported_translation_task()
    test_missing_optional_dependency_fails_during_load()
    print("FunASR backend adapter tests passed")
