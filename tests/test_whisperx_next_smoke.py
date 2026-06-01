from importlib import util
import os
from pathlib import Path
import sys
import shutil


SCRIPT_PATH = Path("tools/whisperx_next_smoke.py")


def load_smoke_module():
    spec = util.spec_from_file_location("whisperx_next_smoke", SCRIPT_PATH)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_whisperx_next_smoke_script_exists_and_targets_upstream_package():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    requirements = Path("requirements-dev-whisperx-next.txt").read_text(encoding="utf-8")

    assert "whisperx==3.8.6" in requirements
    assert "imageio-ffmpeg" in requirements
    assert "remove_repo_root_from_sys_path" in source
    assert "refusing to use vendored whisperx" in source
    assert "ensure_ffmpeg_on_path" in source
    assert "alignment smoke" in source
    assert "diarization smoke" in source


def test_whisperx_next_smoke_removes_repo_root_from_import_path(monkeypatch):
    smoke = load_smoke_module()
    repo_root = Path.cwd()
    original_path = list(sys.path)

    monkeypatch.setattr(sys, "path", [str(repo_root), "", "C:/external/site-packages"])

    smoke.remove_repo_root_from_sys_path(repo_root)

    assert str(repo_root) not in sys.path
    assert "" not in sys.path
    assert "C:/external/site-packages" in sys.path
    monkeypatch.setattr(sys, "path", original_path)


def test_whisperx_next_smoke_detects_vendored_whisperx_path():
    smoke = load_smoke_module()
    repo_root = Path.cwd()
    vendored_init = repo_root / "whisperx" / "__init__.py"

    assert smoke.is_vendored_whisperx(vendored_init, repo_root)
    assert not smoke.is_vendored_whisperx(Path("C:/external/site-packages/whisperx/__init__.py"), repo_root)


def test_whisperx_next_smoke_skips_audio_load_for_import_only(monkeypatch, tmp_path):
    smoke = load_smoke_module()
    calls = []

    class FakeWhisperX:
        __file__ = "C:/external/site-packages/whisperx/__init__.py"

        @staticmethod
        def load_audio(audio_path):
            calls.append(audio_path)
            raise AssertionError("import-only smoke should not load audio")

    monkeypatch.setattr(smoke, "parse_args", lambda: type("Args", (), {
        "audio": tmp_path / "sample.wav",
        "transcript_json": None,
        "language": "zh",
        "device": "cpu",
        "hf_token": None,
        "diarization_model": None,
        "min_speakers": None,
        "max_speakers": None,
        "check_audio": False,
        "skip_alignment": True,
        "skip_diarization": True,
        "output": None,
    })())
    monkeypatch.setattr(smoke, "import_upstream_whisperx", lambda repo_root: FakeWhisperX)
    monkeypatch.setattr(smoke, "get_device", lambda requested_device: "cpu")

    assert smoke.main() == 0
    assert calls == []


def test_whisperx_next_smoke_can_check_audio_without_model_downloads(monkeypatch, tmp_path):
    smoke = load_smoke_module()
    calls = []

    class FakeWhisperX:
        __file__ = "C:/external/site-packages/whisperx/__init__.py"

        @staticmethod
        def load_audio(audio_path):
            calls.append(audio_path)
            return [0.0, 0.1]

    monkeypatch.setattr(smoke, "parse_args", lambda: type("Args", (), {
        "audio": tmp_path / "sample.wav",
        "transcript_json": None,
        "language": "zh",
        "device": "cpu",
        "hf_token": None,
        "diarization_model": None,
        "min_speakers": None,
        "max_speakers": None,
        "check_audio": True,
        "skip_alignment": True,
        "skip_diarization": True,
        "output": None,
    })())
    monkeypatch.setattr(smoke, "import_upstream_whisperx", lambda repo_root: FakeWhisperX)
    monkeypatch.setattr(smoke, "get_device", lambda requested_device: "cpu")
    monkeypatch.setattr(smoke, "ensure_ffmpeg_on_path", lambda: Path("C:/ffmpeg/ffmpeg.exe"))

    assert smoke.main() == 0
    assert calls == [str(tmp_path / "sample.wav")]


def test_whisperx_next_smoke_finds_diarization_pipeline_in_diarize_module():
    smoke = load_smoke_module()

    class FakeWhisperX:
        pass

    class FakeDiarize:
        class DiarizationPipeline:
            pass

    assert smoke.get_diarization_pipeline_class(FakeWhisperX, FakeDiarize) is FakeDiarize.DiarizationPipeline


def test_whisperx_next_smoke_prefers_top_level_diarization_pipeline_when_available():
    smoke = load_smoke_module()

    class FakeWhisperX:
        class DiarizationPipeline:
            pass

    class FakeDiarize:
        class DiarizationPipeline:
            pass

    assert smoke.get_diarization_pipeline_class(FakeWhisperX, FakeDiarize) is FakeWhisperX.DiarizationPipeline


def test_whisperx_next_smoke_uses_imageio_ffmpeg_when_system_ffmpeg_is_missing(monkeypatch, tmp_path):
    smoke = load_smoke_module()
    fake_ffmpeg = tmp_path / "bin" / "ffmpeg.exe"
    fake_ffmpeg.parent.mkdir()
    fake_ffmpeg.write_text("", encoding="utf-8")

    class FakeImageioFfmpeg:
        @staticmethod
        def get_ffmpeg_exe():
            return str(fake_ffmpeg)

    monkeypatch.setattr(shutil, "which", lambda command: None)
    monkeypatch.setitem(sys.modules, "imageio_ffmpeg", FakeImageioFfmpeg)
    monkeypatch.setenv("PATH", "C:/original")

    resolved = smoke.ensure_ffmpeg_on_path()

    assert resolved == fake_ffmpeg
    assert str(fake_ffmpeg.parent) in os.environ["PATH"]


def test_whisperx_next_smoke_creates_windows_ffmpeg_exe_shim(monkeypatch, tmp_path):
    smoke = load_smoke_module()
    imageio_ffmpeg = tmp_path / "imageio" / "ffmpeg-win-x86_64-v7.1.exe"
    imageio_ffmpeg.parent.mkdir()
    imageio_ffmpeg.write_bytes(b"fake ffmpeg")

    shim = smoke.create_windows_ffmpeg_shim(imageio_ffmpeg, tmp_path / "shim")

    assert shim.name == "ffmpeg.exe"
    assert shim.read_bytes() == b"fake ffmpeg"


def test_whisperx_next_smoke_configures_local_model_cache(monkeypatch, tmp_path):
    smoke = load_smoke_module()
    monkeypatch.delenv("HF_HOME", raising=False)
    monkeypatch.delenv("TRANSFORMERS_CACHE", raising=False)
    monkeypatch.delenv("PYANNOTE_CACHE", raising=False)
    monkeypatch.delenv("NLTK_DATA", raising=False)

    cache_root = smoke.configure_local_model_cache(tmp_path)

    assert cache_root == tmp_path / "cache" / "whisperx-next"
    assert os.environ["HF_HOME"] == str(cache_root / "huggingface")
    assert os.environ["TRANSFORMERS_CACHE"] == str(cache_root / "huggingface")
    assert os.environ["PYANNOTE_CACHE"] == str(cache_root / "pyannote")
    assert os.environ["NLTK_DATA"] == str(cache_root / "nltk_data")
