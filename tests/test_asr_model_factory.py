import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "faster_whisper_GUI" / "asr_model_factory.py"
SPEC = importlib.util.spec_from_file_location("asr_model_factory_test_module", MODULE_PATH)
asr_model_factory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = asr_model_factory
SPEC.loader.exec_module(asr_model_factory)

create_asr_model = asr_model_factory.create_asr_model
recommended_num_workers = asr_model_factory.recommended_num_workers


def test_factory_preserves_faster_whisper_arguments():
    calls = []

    class FakeWhisperModel:
        def __init__(self, model, **kwargs):
            calls.append((model, kwargs))

    model = create_asr_model(
        backend="faster-whisper",
        model_size_or_path="large-v3",
        device="cuda",
        device_index=1,
        compute_type="float16",
        cpu_threads=4,
        num_workers=2,
        download_root="/models",
        local_files_only=True,
        whisper_model_cls=FakeWhisperModel,
    )

    assert isinstance(model, FakeWhisperModel)
    assert calls == [
        (
            "large-v3",
            {
                "device": "cuda",
                "device_index": 1,
                "compute_type": "float16",
                "cpu_threads": 4,
                "num_workers": 2,
                "download_root": "/models",
                "local_files_only": True,
            },
        )
    ]


def test_factory_loads_funasr_with_selected_device_and_model():
    calls = []

    class FakeFunASRModel:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.loaded = False

        def load(self):
            self.loaded = True
            return self

    model = create_asr_model(
        backend="funasr",
        model_size_or_path="iic/SenseVoiceSmall",
        device="cuda",
        device_index=[2, 3],
        compute_type="float16",
        cpu_threads=4,
        num_workers=1,
        download_root="",
        local_files_only=False,
        funasr_model_cls=FakeFunASRModel,
    )

    assert model.loaded is True
    assert calls == [{"model": "iic/SenseVoiceSmall", "device": "cuda:2"}]


def test_factory_leaves_auto_device_selection_to_funasr():
    calls = []

    class FakeFunASRModel:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def load(self):
            return self

    create_asr_model(
        backend="funasr",
        model_size_or_path="iic/SenseVoiceSmall",
        device="auto",
        device_index=0,
        compute_type="float16",
        cpu_threads=4,
        num_workers=1,
        download_root="",
        local_files_only=False,
        funasr_model_cls=FakeFunASRModel,
    )

    assert calls == [{"model": "iic/SenseVoiceSmall"}]


def test_worker_count_follows_loaded_model_not_current_selector():
    class LoadedFunASRModel:
        asr_backend = "funasr"

    assert recommended_num_workers(LoadedFunASRModel(), configured_workers=4) == 1
    assert recommended_num_workers(object(), configured_workers=4) == 4


def test_factory_rejects_unknown_backend():
    try:
        create_asr_model(
            backend="other",
            model_size_or_path="model",
            device="cpu",
            device_index=0,
            compute_type="float32",
            cpu_threads=4,
            num_workers=1,
            download_root="",
            local_files_only=False,
        )
    except ValueError as exc:
        assert "Unsupported ASR backend" in str(exc)
    else:
        raise AssertionError("unknown backend should be rejected")


if __name__ == "__main__":
    test_factory_preserves_faster_whisper_arguments()
    test_factory_loads_funasr_with_selected_device_and_model()
    test_factory_leaves_auto_device_selection_to_funasr()
    test_worker_count_follows_loaded_model_not_current_selector()
    test_factory_rejects_unknown_backend()
    print("ASR model factory tests passed")
