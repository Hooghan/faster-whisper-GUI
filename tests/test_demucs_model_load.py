from pathlib import Path

import torch


def test_demucs_downloads_official_asset_to_configured_cache(monkeypatch, tmp_path):
    from faster_whisper_GUI import demucs_runner

    calls = []

    class FakeModel(torch.nn.Module):
        def forward(self, chunk):
            return chunk

        def load_state_dict(self, state_dict):
            self.loaded_state_dict = state_dict

    class FakeBundle:
        _model_path = "models/hdemucs_high_trained.pt"
        sample_rate = 44100

        @staticmethod
        def _model_factory_func():
            return FakeModel()

    def fake_download_asset(key, path=None, **kwargs):
        assert path.exists() is False
        calls.append({"key": key, "path": Path(path), "kwargs": kwargs})
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({}, path)
        return str(path)

    monkeypatch.setattr(demucs_runner, "HDEMUCS_HIGH_MUSDB_PLUS", FakeBundle())
    monkeypatch.setattr(demucs_runner, "download_asset", fake_download_asset)

    model = demucs_runner.load_model(
        str(tmp_path / "hdemucs_high_trained.pt"),
        device=torch.device("cpu"),
    )

    assert calls == [
        {
            "key": "models/hdemucs_high_trained.pt",
            "path": tmp_path / "hdemucs_high_trained.pt",
            "kwargs": {"progress": True},
        }
    ]
    assert FakeBundle._model_path == "models/hdemucs_high_trained.pt"
    assert isinstance(model, FakeModel)


def test_demucs_gui_worker_uses_subprocess_without_importing_torch_at_module_level():
    source = Path("faster_whisper_GUI/de_mucs.py").read_text(encoding="utf-8")

    assert "import torch" not in source
    assert "torchaudio" not in source
    assert "import faster_whisper" not in source
    assert "faster_whisper_GUI.demucs_runner" in source


def test_demucs_subprocess_forces_utf8_output(monkeypatch, tmp_path):
    from faster_whisper_GUI.de_mucs import run_demucs_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), kwargs))
        output_path = command[command.index("--output") + 1]
        Path(output_path).write_text('{"ok": true}', encoding="utf-8")

    monkeypatch.setattr("subprocess.run", fake_run)

    result = run_demucs_in_subprocess(
        payload={"audio": []},
        input_path=str(tmp_path / "input.json"),
        output_path=str(tmp_path / "output.json"),
    )

    assert result == {"ok": True}
    assert calls[0][1]["PYTHONIOENCODING"] == "utf-8"
    assert calls[0][1]["PYTHONUTF8"] == "1"
    assert calls[0][1]["PYTHONUNBUFFERED"] == "1"


def test_demucs_save_result_creates_nested_output_directory(monkeypatch, tmp_path):
    from faster_whisper_GUI import demucs_runner

    writes = []

    class FakeModel:
        sources = ["drums", "bass", "other", "vocals"]

    def fake_write(path, data, sample_rate):
        writes.append(Path(path))

    monkeypatch.setattr(demucs_runner.soundfile, "write", fake_write)

    demucs_runner.save_result(
        model=FakeModel(),
        file_path=str(tmp_path / "audio" / "sample.mp3"),
        sources=torch.zeros(1, 4, 2, 10),
        stems=5,
        output_path=str(tmp_path / "nested" / "outputs"),
        sample_rate=44100,
    )

    assert (tmp_path / "nested" / "outputs" / "sample").is_dir()
    assert len(writes) == 2
