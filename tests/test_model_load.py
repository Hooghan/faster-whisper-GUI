import numpy as np

from faster_whisper_GUI import modelLoad


def test_cuda_model_load_prepares_torch_cuda_runtime(monkeypatch):
    imported_modules = []

    monkeypatch.setattr(
        modelLoad.importlib,
        "import_module",
        lambda name: imported_modules.append(name),
    )

    modelLoad.prepare_cuda_runtime("cuda")

    assert imported_modules == ["torch"]


def test_cpu_model_load_skips_torch_cuda_runtime(monkeypatch):
    imported_modules = []

    monkeypatch.setattr(
        modelLoad.importlib,
        "import_module",
        lambda name: imported_modules.append(name),
    )

    modelLoad.prepare_cuda_runtime("cpu")

    assert imported_modules == []


def test_v3_mel_filters_match_faster_whisper_float32_features():
    class FakeFeatureExtractor:
        sampling_rate = 16000
        n_fft = 400
        mel_filters = None

        def get_mel_filters(self, sampling_rate, n_fft, n_mels):
            assert sampling_rate == self.sampling_rate
            assert n_fft == self.n_fft
            assert n_mels == 128
            return np.ones((128, 201))

    class FakeModel:
        feature_extractor = FakeFeatureExtractor()

    modelLoad.set_v3_mel_filters(FakeModel())

    assert FakeModel.feature_extractor.mel_filters.dtype == np.float32
