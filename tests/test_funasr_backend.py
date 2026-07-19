import importlib.util
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

    assert fake.calls == [{"input": "sample.wav", "language": "zh", "hotword": "FunASR"}]
    assert [(s.start, s.end, s.text) for s in segments] == [(0.0, 1.0, "ok")]
    assert info.language == "zh"
    assert info.duration == 1.0


if __name__ == "__main__":
    test_normalize_gui_language_values()
    test_convert_sentence_info_to_segments()
    test_convert_flat_timestamp_result_to_segment()
    test_model_transcribe_uses_funasr_generate_contract()
    print("FunASR backend adapter tests passed")
