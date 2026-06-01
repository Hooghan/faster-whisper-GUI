def test_vendored_whisperx_imports_with_addon_dependencies():
    import whisperx

    assert callable(whisperx.load_audio)
    assert callable(whisperx.load_align_model)
    assert callable(whisperx.align)


def test_gui_whisperx_worker_imports_with_addon_dependencies():
    from faster_whisper_GUI.whisper_x import WhisperXWorker

    assert WhisperXWorker.__name__ == "WhisperXWorker"


def test_whisperx_worker_uses_cpu_by_default_to_avoid_cuda_dll_conflict(monkeypatch):
    from faster_whisper_GUI import whisper_x

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_DEVICE", raising=False)
    monkeypatch.setattr(whisper_x.torch.cuda, "is_available", lambda: True)

    assert whisper_x.get_whisperx_device().type == "cpu"


def test_whisperx_worker_allows_explicit_cuda_override(monkeypatch):
    from faster_whisper_GUI import whisper_x

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cuda")
    monkeypatch.setattr(whisper_x.torch.cuda, "is_available", lambda: True)

    assert whisper_x.get_whisperx_device().type == "cuda"


def test_whisperx_backend_defaults_to_vendored(monkeypatch):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_backend

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", raising=False)

    assert get_whisperx_backend() == "vendored"


def test_whisperx_backend_allows_upstream_override(monkeypatch):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_backend

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", " upstream ")

    assert get_whisperx_backend() == "upstream"


def test_whisperx_backend_unknown_values_fall_back_to_vendored(monkeypatch):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_backend

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", "experimental")

    assert get_whisperx_backend() == "vendored"


def test_whisperx_backend_display_text_normalizes_backend_names():
    from faster_whisper_GUI.whisperx_backend import whisperx_backend_display_name

    assert whisperx_backend_display_name("upstream") == "upstream"
    assert whisperx_backend_display_name("vendored") == "vendored"
    assert whisperx_backend_display_name("unknown") == "vendored"


def test_whisperx_upstream_python_prefers_isolated_environment(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_python_executable

    upstream_python = tmp_path / ".venv-whisperx-next" / "Scripts" / "python.exe"
    upstream_python.parent.mkdir(parents=True)
    upstream_python.write_text("", encoding="utf-8")
    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", "upstream")

    assert get_whisperx_python_executable(repo_root=tmp_path) == str(upstream_python)


def test_whisperx_upstream_python_can_use_explicit_backend_without_parent_env(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_python_executable

    upstream_python = tmp_path / ".venv-whisperx-next" / "Scripts" / "python.exe"
    upstream_python.parent.mkdir(parents=True)
    upstream_python.write_text("", encoding="utf-8")
    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", raising=False)

    assert get_whisperx_python_executable(repo_root=tmp_path, backend="upstream") == str(upstream_python)


def test_whisperx_upstream_python_allows_explicit_executable(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisperx_backend import get_whisperx_python_executable

    explicit_python = tmp_path / "custom-python.exe"
    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", "upstream")
    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_UPSTREAM_PYTHON", str(explicit_python))

    assert get_whisperx_python_executable(repo_root=tmp_path) == str(explicit_python)


def test_whisperx_backend_detects_vendored_module_path(tmp_path):
    from faster_whisper_GUI.whisperx_backend import is_vendored_whisperx

    vendored_init = tmp_path / "whisperx" / "__init__.py"
    external_init = tmp_path / ".venv-whisperx-next" / "Lib" / "site-packages" / "whisperx" / "__init__.py"

    assert is_vendored_whisperx(vendored_init, tmp_path)
    assert not is_vendored_whisperx(external_init, tmp_path)


def test_whisperx_backend_removes_repo_root_from_import_path(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisperx_backend import remove_repo_root_from_sys_path

    monkeypatch.setattr("sys.path", ["", str(tmp_path), str(tmp_path / "external")])

    remove_repo_root_from_sys_path(tmp_path)

    assert "" not in __import__("sys").path
    assert str(tmp_path) not in __import__("sys").path
    assert str(tmp_path / "external") in __import__("sys").path


def test_whisperx_backend_refuses_vendored_import_in_upstream_mode(monkeypatch, tmp_path):
    import types

    from faster_whisper_GUI import whisperx_backend

    fake_module = types.SimpleNamespace(__file__=str(tmp_path / "whisperx" / "__init__.py"))

    monkeypatch.setattr(whisperx_backend, "remove_repo_root_from_sys_path", lambda repo_root: None)
    monkeypatch.setitem(__import__("sys").modules, "whisperx", fake_module)

    try:
        whisperx_backend.import_whisperx_for_backend("upstream", tmp_path)
    except RuntimeError as error:
        assert "refusing to use vendored whisperx" in str(error)
    else:
        raise AssertionError("upstream backend should refuse vendored whisperx")


def test_whisperx_backend_configures_upstream_warning_filters(monkeypatch):
    from faster_whisper_GUI import whisperx_backend

    calls = []

    def fake_filterwarnings(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr(whisperx_backend.warnings, "filterwarnings", fake_filterwarnings)

    whisperx_backend.configure_upstream_warning_filters()

    assert any(
        "torchcodec is not installed correctly" in kwargs.get("message", "")
        for _, kwargs in calls
    )


def test_whisperx_subprocess_prefers_cuda_without_changing_parent_env(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_DEVICE", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    assert calls[0][1]["FASTER_WHISPER_GUI_WHISPERX_DEVICE"] == "cuda"


def test_whisperx_subprocess_forces_utf8_output(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), kwargs))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    assert calls[0][1]["PYTHONIOENCODING"] == "utf-8"
    assert calls[0][1]["PYTHONUTF8"] == "1"


def test_whisperx_subprocess_sets_loky_cpu_count_to_reduce_upstream_noise(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.delenv("LOKY_MAX_CPU_COUNT", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    assert calls[0][1]["LOKY_MAX_CPU_COUNT"] == "1"


def test_whisperx_subprocess_respects_explicit_cpu_override(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cpu")
    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    assert calls[0][1]["FASTER_WHISPER_GUI_WHISPERX_DEVICE"] == "cpu"


def test_whisperx_subprocess_uses_upstream_python_when_backend_is_upstream(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    upstream_python = tmp_path / ".venv-whisperx-next" / "Scripts" / "python.exe"
    upstream_python.parent.mkdir(parents=True)
    upstream_python.write_text("", encoding="utf-8")
    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", "upstream")
    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_UPSTREAM_PYTHON", str(upstream_python))
    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    assert calls[0][0][0] == str(upstream_python)
    assert calls[0][1]["FASTER_WHISPER_GUI_WHISPERX_BACKEND"] == "upstream"


def test_whisperx_subprocess_uses_explicit_upstream_backend_without_parent_env(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    upstream_python = tmp_path / ".venv-whisperx-next" / "Scripts" / "python.exe"
    upstream_python.parent.mkdir(parents=True)
    upstream_python.write_text("", encoding="utf-8")
    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", raising=False)
    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_UPSTREAM_PYTHON", str(upstream_python))
    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        backend="upstream",
        working_dir=tmp_path,
    )

    assert calls[0][0][0] == str(upstream_python)
    assert calls[0][1]["FASTER_WHISPER_GUI_WHISPERX_BACKEND"] == "upstream"


def test_whisperx_subprocess_logs_child_output(monkeypatch, tmp_path, capsys):
    from types import SimpleNamespace

    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    def fake_run(command, env, check, capture_output, text, encoding, errors):
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')
        return SimpleNamespace(
            stdout="WhisperX subprocess device: cuda\nfinished alignment in 1.2s\n",
            stderr="runner warning\n",
        )

    monkeypatch.setattr("subprocess.run", fake_run)

    run_alignment_in_subprocess(
        segments=[],
        audio_path="sample.mp3",
        language="zh",
        working_dir=tmp_path,
    )

    captured = capsys.readouterr()

    assert "WhisperX subprocess device: cuda" in captured.out
    assert "runner warning" in captured.out


def test_whisperx_subprocess_logs_child_output_when_command_fails(monkeypatch, tmp_path, capsys):
    import subprocess

    from faster_whisper_GUI.whisper_x import run_alignment_in_subprocess

    def fake_run(command, env, check, capture_output, text, encoding, errors):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
            output="child stdout before failure\n",
            stderr="child stderr with root cause\n",
        )

    monkeypatch.setattr("subprocess.run", fake_run)

    try:
        run_alignment_in_subprocess(
            segments=[],
            audio_path="sample.mp3",
            language="zh",
            working_dir=tmp_path,
        )
    except subprocess.CalledProcessError:
        pass
    else:
        raise AssertionError("failed subprocess should re-raise CalledProcessError")

    captured = capsys.readouterr()

    assert "child stdout before failure" in captured.out
    assert "child stderr with root cause" in captured.out


def test_whisperx_diarization_subprocess_prefers_cuda(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_diarization_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append((command, env.copy(), check))
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_DEVICE", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)

    run_diarization_in_subprocess(
        transcript_result={"segments": []},
        audio_path="sample.mp3",
        use_auth_token=None,
        min_speaker=None,
        max_speaker=None,
        working_dir=tmp_path,
    )

    assert calls[0][1]["FASTER_WHISPER_GUI_WHISPERX_DEVICE"] == "cuda"
    assert "faster_whisper_GUI.whisperx_diarization_runner" in calls[0][0]


def test_whisperx_diarization_subprocess_normalizes_blank_token(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_diarization_in_subprocess

    payloads = []

    def fake_run(command, env, check, **kwargs):
        input_path = command[command.index("--input") + 1]
        output_path = command[command.index("--output") + 1]
        with open(input_path, "r", encoding="utf-8") as input_file:
            payloads.append(__import__("json").load(input_file))
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.setattr("subprocess.run", fake_run)

    run_diarization_in_subprocess(
        transcript_result={"segments": []},
        audio_path="sample.mp3",
        use_auth_token="   ",
        min_speaker=None,
        max_speaker=None,
        working_dir=tmp_path,
    )

    assert payloads[0]["use_auth_token"] is None


def test_whisperx_diarization_subprocess_passes_short_response_refinement(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_diarization_in_subprocess

    payloads = []

    def fake_run(command, env, check, **kwargs):
        input_path = command[command.index("--input") + 1]
        output_path = command[command.index("--output") + 1]
        with open(input_path, "r", encoding="utf-8") as input_file:
            payloads.append(__import__("json").load(input_file))
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.setattr("subprocess.run", fake_run)

    run_diarization_in_subprocess(
        transcript_result={"segments": []},
        audio_path="sample.mp3",
        use_auth_token=None,
        min_speaker=None,
        max_speaker=None,
        refine_short_responses=True,
        working_dir=tmp_path,
    )

    assert payloads[0]["refine_short_responses"] is True


def test_whisperx_diarization_subprocess_passes_backend(monkeypatch, tmp_path):
    from faster_whisper_GUI.whisper_x import run_diarization_in_subprocess

    calls = []

    def fake_run(command, env, check, **kwargs):
        calls.append(env.copy())
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_BACKEND", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)

    run_diarization_in_subprocess(
        transcript_result={"segments": []},
        audio_path="sample.mp3",
        use_auth_token=None,
        min_speaker=None,
        max_speaker=None,
        backend="upstream",
        working_dir=tmp_path,
    )

    assert calls[0]["FASTER_WHISPER_GUI_WHISPERX_BACKEND"] == "upstream"


def test_whisperx_diarization_subprocess_logs_child_output(monkeypatch, tmp_path, capsys):
    from types import SimpleNamespace

    from faster_whisper_GUI.whisper_x import run_diarization_in_subprocess

    def fake_run(command, env, check, capture_output, text, encoding, errors):
        output_path = command[command.index("--output") + 1]
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write('{"segments": []}')
        return SimpleNamespace(
            stdout="WhisperX diarization subprocess device: cuda\nfinished speaker diarize in 1.2s\n",
            stderr="diarize warning\n",
        )

    monkeypatch.setattr("subprocess.run", fake_run)

    run_diarization_in_subprocess(
        transcript_result={"segments": []},
        audio_path="sample.mp3",
        use_auth_token=None,
        min_speaker=None,
        max_speaker=None,
        working_dir=tmp_path,
    )

    captured = capsys.readouterr()

    assert "WhisperX diarization subprocess device: cuda" in captured.out
    assert "diarize warning" in captured.out


def test_whisperx_diarization_worker_leaves_audio_and_model_loading_to_subprocess(monkeypatch):
    from faster_whisper_GUI import whisper_x
    from faster_whisper_GUI.seg_ment import segment_Transcribe

    segment = segment_Transcribe(start=0, end=1, text="hello", words=[])
    info = type("Info", (), {"language": "zh"})()

    def fail_if_parent_loads_audio(path):
        raise AssertionError("parent process should not load audio for subprocess diarization")

    class ForbiddenDiarizationPipeline:
        def __init__(self, *args, **kwargs):
            raise AssertionError("parent process should not load diarization model")

    def fake_diarization_subprocess(
        transcript_result,
        audio_path,
        use_auth_token,
        min_speaker,
        max_speaker,
        refine_short_responses=False,
        backend=None,
        working_dir=None,
    ):
        assert transcript_result == {"segments": [{"start": 0.0, "end": 1.0, "text": "hello", "words": []}]}
        assert refine_short_responses is False
        assert backend is None
        return {"segments": [{"start": 0.0, "end": 1.0, "text": "hello", "words": [], "speaker": "SPEAKER_00"}]}

    monkeypatch.setattr(whisper_x.whisperx, "load_audio", fail_if_parent_loads_audio)
    monkeypatch.setattr(whisper_x.whisperx, "DiarizationPipeline", ForbiddenDiarizationPipeline)
    monkeypatch.setattr(whisper_x, "run_diarization_in_subprocess", fake_diarization_subprocess)

    worker = whisper_x.WhisperXWorker(
        segments_path_info=[([segment], "sample.mp3", info)],
        alignment=False,
        speaker_diarize=True,
        use_auth_token=None,
        min_speaker=None,
        max_speaker=None,
    )

    worker.run()

    result_segments = worker.result_segments_path_info[0][0]
    assert result_segments[0].speaker == "SPEAKER_00"


def test_whisperx_diarize_patches_pyannote_legacy_hf_token_argument(monkeypatch):
    import whisperx

    import pyannote.audio.core.model as model_module
    import pyannote.audio.core.pipeline as pipeline_module
    import pyannote.audio.pipelines.speaker_verification as speaker_verification_module
    from whisperx.diarize import patch_pyannote_hf_hub_download

    calls = []

    def fake_hf_hub_download(*args, token=None, **kwargs):
        calls.append({"token": token, "kwargs": kwargs})
        return "config.yaml"

    monkeypatch.setattr(pipeline_module, "hf_hub_download", fake_hf_hub_download)
    monkeypatch.setattr(model_module, "hf_hub_download", fake_hf_hub_download)
    monkeypatch.setattr(speaker_verification_module, "hf_hub_download", fake_hf_hub_download)

    patch_pyannote_hf_hub_download()

    pipeline_module.hf_hub_download("repo", "config.yaml", use_auth_token="token-value")
    model_module.hf_hub_download("repo", "model.bin", use_auth_token="token-value")
    speaker_verification_module.hf_hub_download("repo", "embedding.bin", use_auth_token="token-value")

    assert [call["token"] for call in calls] == ["token-value", "token-value", "token-value"]
    assert all("use_auth_token" not in call["kwargs"] for call in calls)


def test_whisperx_diarize_drops_legacy_speechbrain_arguments(monkeypatch):
    from whisperx.diarize import patch_pyannote_speechbrain_from_hparams
    import pyannote.audio.pipelines.speaker_verification as speaker_verification_module
    import torch

    calls = []

    class FakeEncoderClassifier:
        @staticmethod
        def from_hparams(*args, **kwargs):
            calls.append({"args": args, "kwargs": kwargs})
            return "classifier"

    monkeypatch.setattr(
        speaker_verification_module,
        "SpeechBrain_EncoderClassifier",
        FakeEncoderClassifier,
        raising=False,
    )

    patch_pyannote_speechbrain_from_hparams()
    patch_pyannote_speechbrain_from_hparams(default_device=torch.device("cuda"))

    classifier = speaker_verification_module.SpeechBrain_EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="./cache",
        use_auth_token="token-value",
        revision="main",
        run_opts={"jit": False},
    )

    assert classifier == "classifier"
    assert calls[0]["kwargs"]["source"] == "speechbrain/spkrec-ecapa-voxceleb"
    assert calls[0]["kwargs"]["savedir"] == "./cache"
    assert calls[0]["kwargs"]["run_opts"]["jit"] is False
    assert calls[0]["kwargs"]["run_opts"]["device"] == "cuda"
    assert "device" not in calls[0]["kwargs"]
    assert "use_auth_token" not in calls[0]["kwargs"]
    assert "revision" not in calls[0]["kwargs"]


def test_whisperx_diarize_restores_numpy_legacy_nan_alias(monkeypatch):
    import numpy as np
    from whisperx.diarize import patch_numpy_legacy_nan_alias

    monkeypatch.delattr(np, "NAN", raising=False)

    patch_numpy_legacy_nan_alias()

    assert np.NAN is np.nan


def test_whisperx_diarization_pipeline_reports_missing_pyannote_access(monkeypatch):
    from whisperx import diarize

    monkeypatch.setattr(diarize.Pipeline, "from_pretrained", lambda *args, **kwargs: None)

    try:
        diarize.DiarizationPipeline(use_auth_token=None)
    except RuntimeError as error:
        assert "pyannote speaker diarization model" in str(error)
        assert "Hugging Face" in str(error)
    else:
        raise AssertionError("missing pyannote access should raise RuntimeError")


def test_whisperx_diarization_runner_sets_local_cache_before_importing_torch_or_whisperx():
    from pathlib import Path

    source = Path("faster_whisper_GUI/whisperx_diarization_runner.py").read_text(encoding="utf-8")

    cache_index = source.index("configure_local_model_cache()")
    torch_index = source.index("import torch")
    whisperx_index = source.index("import_whisperx_for_backend(")

    assert cache_index < torch_index
    assert cache_index < whisperx_index
    assert 'TORCH_HOME' in source
    assert 'PYANNOTE_CACHE' in source


def test_whisperx_diarization_runner_patches_torch_load_for_pyannote_checkpoints():
    from pathlib import Path

    source = Path("faster_whisper_GUI/whisperx_diarization_runner.py").read_text(encoding="utf-8")

    assert "patch_torch_load_for_pyannote_checkpoints()" in source
    assert 'weights_only' in source
    assert 'False' in source


def test_whisperx_diarization_runner_disables_optional_speechbrain_k2_lazy_import():
    from pathlib import Path

    source = Path("faster_whisper_GUI/whisperx_diarization_runner.py").read_text(encoding="utf-8")

    disable_call_index = source.index("disable_optional_speechbrain_k2_lazy_import()")
    whisperx_import_index = source.index("import_whisperx_for_backend(")

    assert disable_call_index < whisperx_import_index
    assert "speechbrain.integrations.k2_fsa" in source
    assert "\\\\inspect.py" in source
    assert "speechbrain.pretrained" in source
    assert "speechbrain.inference" in source


def test_whisperx_diarization_runner_summarizes_speaker_assignment():
    from faster_whisper_GUI.whisperx_diarization_runner import (
        summarize_diarization_segments,
        summarize_speaker_assignment,
    )

    result = {
        "segments": [
            {"start": 0.0, "end": 1.0, "speaker": "SPEAKER_00"},
            {"start": 1.0, "end": 2.0},
            {"start": 2.0, "end": 3.0, "speaker": "SPEAKER_01"},
        ]
    }

    assert summarize_diarization_segments(
        [
            {"speaker": "SPEAKER_00"},
            {"speaker": "SPEAKER_00"},
            {"speaker": "SPEAKER_01"},
        ]
    ) == (3, 2)
    assert summarize_speaker_assignment(result) == (2, 3)


def test_whisperx_diarization_runner_finds_pipeline_in_diarize_module():
    from faster_whisper_GUI.whisperx_diarization_runner import get_diarization_pipeline_class

    class FakeWhisperX:
        pass

    class FakeDiarize:
        class DiarizationPipeline:
            pass

    assert get_diarization_pipeline_class(FakeWhisperX, FakeDiarize) is FakeDiarize.DiarizationPipeline


def test_whisperx_diarization_runner_prefers_top_level_pipeline_when_available():
    from faster_whisper_GUI.whisperx_diarization_runner import get_diarization_pipeline_class

    class FakeWhisperX:
        class DiarizationPipeline:
            pass

    class FakeDiarize:
        class DiarizationPipeline:
            pass

    assert get_diarization_pipeline_class(FakeWhisperX, FakeDiarize) is FakeWhisperX.DiarizationPipeline


def test_whisperx_diarization_runner_supports_upstream_token_constructor():
    from faster_whisper_GUI.whisperx_diarization_runner import create_diarization_pipeline

    calls = []

    class FakePipeline:
        def __init__(self, **kwargs):
            calls.append(kwargs)

    class FakeWhisperX:
        DiarizationPipeline = FakePipeline

    create_diarization_pipeline(
        FakeWhisperX,
        model_name="pyannote/speaker-diarization-community-1",
        use_auth_token="token-value",
        device="cpu",
        cache_dir="./cache",
    )

    assert calls[0]["model_name"] == "pyannote/speaker-diarization-community-1"
    assert calls[0]["token"] == "token-value"
    assert calls[0]["device"] == "cpu"
    assert calls[0]["cache_dir"] == "./cache"


def test_whisperx_diarization_runner_falls_back_to_legacy_use_auth_token_constructor():
    from faster_whisper_GUI.whisperx_diarization_runner import create_diarization_pipeline

    calls = []

    class FakePipeline:
        def __init__(self, **kwargs):
            if "token" in kwargs:
                raise TypeError("unexpected token")
            calls.append(kwargs)

    class FakeWhisperX:
        DiarizationPipeline = FakePipeline

    create_diarization_pipeline(
        FakeWhisperX,
        model_name="pyannote/speaker-diarization@2.1",
        use_auth_token="token-value",
        device="cpu",
        cache_dir="./cache",
    )

    assert calls[0]["model_name"] == "pyannote/speaker-diarization@2.1"
    assert calls[0]["use_auth_token"] == "token-value"
    assert calls[0]["device"] == "cpu"
    assert calls[0]["cache_dir"] == "./cache"


def test_whisperx_diarization_runner_does_not_override_vendored_default_model_with_none():
    from faster_whisper_GUI.whisperx_diarization_runner import create_diarization_pipeline

    calls = []

    class FakePipeline:
        def __init__(self, **kwargs):
            if "token" in kwargs:
                raise TypeError("unexpected token")
            calls.append(kwargs)

    class FakeWhisperX:
        DiarizationPipeline = FakePipeline

    create_diarization_pipeline(
        FakeWhisperX,
        model_name=None,
        use_auth_token="token-value",
        device="cpu",
        cache_dir="./cache",
    )

    assert "model_name" not in calls[0]
    assert calls[0]["use_auth_token"] == "token-value"


def test_whisperx_diarization_runner_reads_optional_model_override(monkeypatch):
    from faster_whisper_GUI.whisperx_diarization_runner import get_diarization_model_name

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL", raising=False)
    assert get_diarization_model_name() is None

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL", " pyannote/example ")
    assert get_diarization_model_name() == "pyannote/example"


def test_whisperx_diarization_runner_reads_fill_nearest_override(monkeypatch):
    from faster_whisper_GUI.whisperx_diarization_runner import get_assign_fill_nearest

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST", raising=False)
    assert get_assign_fill_nearest() is False

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST", "1")
    assert get_assign_fill_nearest() is True


def test_whisperx_diarization_runner_reads_short_response_refinement_override(monkeypatch):
    from faster_whisper_GUI.whisperx_diarization_runner import get_refine_short_responses

    monkeypatch.delenv("FASTER_WHISPER_GUI_WHISPERX_REFINE_SHORT_RESPONSES", raising=False)
    assert get_refine_short_responses() is False

    monkeypatch.setenv("FASTER_WHISPER_GUI_WHISPERX_REFINE_SHORT_RESPONSES", "1")
    assert get_refine_short_responses() is True


def test_whisperx_diarization_runner_passes_fill_nearest_when_supported():
    from faster_whisper_GUI.whisperx_diarization_runner import assign_speakers

    calls = []

    class FakeWhisperX:
        @staticmethod
        def assign_word_speakers(diarize_segments, transcript_result, fill_nearest=False):
            calls.append(fill_nearest)
            return transcript_result

    result = assign_speakers(FakeWhisperX, [], {"segments": []}, fill_nearest=True)

    assert result == {"segments": []}
    assert calls == [True]


def test_whisperx_diarization_runner_falls_back_when_fill_nearest_is_not_supported():
    from faster_whisper_GUI.whisperx_diarization_runner import assign_speakers

    calls = []

    class FakeWhisperX:
        @staticmethod
        def assign_word_speakers(diarize_segments, transcript_result, fill_nearest=False):
            if fill_nearest:
                raise TypeError("unexpected keyword argument 'fill_nearest'")
            calls.append("fallback")
            return transcript_result

    result = assign_speakers(FakeWhisperX, [], {"segments": []}, fill_nearest=True)

    assert result == {"segments": []}
    assert calls == ["fallback"]


def test_whisperx_diarization_runner_retries_with_fill_nearest_when_no_segments_are_assigned():
    from faster_whisper_GUI.whisperx_diarization_runner import assign_speakers_with_fallback

    calls = []

    class FakeWhisperX:
        @staticmethod
        def assign_word_speakers(diarize_segments, transcript_result, fill_nearest=False):
            calls.append(fill_nearest)
            result = {"segments": [dict(segment) for segment in transcript_result["segments"]]}
            if fill_nearest:
                result["segments"][0]["speaker"] = "SPEAKER_00"
            return result

    result, used_fallback = assign_speakers_with_fallback(
        FakeWhisperX,
        [{"speaker": "SPEAKER_00"}],
        {"segments": [{"start": 0.0, "end": 1.0, "text": "hello", "words": []}]},
        fill_nearest=False,
    )

    assert used_fallback is True
    assert calls == [False, True]
    assert result["segments"][0]["speaker"] == "SPEAKER_00"


def test_whisperx_diarization_runner_does_not_retry_when_assignment_succeeds():
    from faster_whisper_GUI.whisperx_diarization_runner import assign_speakers_with_fallback

    calls = []

    class FakeWhisperX:
        @staticmethod
        def assign_word_speakers(diarize_segments, transcript_result, fill_nearest=False):
            calls.append(fill_nearest)
            return {"segments": [{"speaker": "SPEAKER_00"}]}

    result, used_fallback = assign_speakers_with_fallback(
        FakeWhisperX,
        [{"speaker": "SPEAKER_00"}],
        {"segments": [{"start": 0.0, "end": 1.0, "text": "hello", "words": []}]},
        fill_nearest=False,
    )

    assert used_fallback is False
    assert calls == [False]
    assert result["segments"][0]["speaker"] == "SPEAKER_00"


def test_whisperx_diarization_runner_refines_short_response_between_same_speaker_turns():
    from faster_whisper_GUI.whisperx_diarization_runner import refine_short_response_speakers

    result = {
        "segments": [
            {"start": 0.11, "end": 1.93, "speaker": "SPEAKER_00", "text": "他的睡眠變好了耶"},
            {
                "start": 1.93,
                "end": 3.11,
                "speaker": "SPEAKER_00",
                "text": "真的假的",
                "words": [{"word": "真的", "speaker": "SPEAKER_00"}],
            },
            {"start": 3.11, "end": 5.43, "speaker": "SPEAKER_00", "text": "他的睡眠品質改善了耶"},
            {"start": 14.35, "end": 15.63, "speaker": "SPEAKER_01", "text": "打住 打住"},
        ]
    }

    changed = refine_short_response_speakers(result)

    assert changed == 1
    assert result["segments"][1]["speaker"] == "SPEAKER_01"
    assert result["segments"][1]["words"][0]["speaker"] == "SPEAKER_01"


def test_whisperx_diarization_runner_does_not_refine_long_segments():
    from faster_whisper_GUI.whisperx_diarization_runner import refine_short_response_speakers

    result = {
        "segments": [
            {"start": 0.0, "end": 1.0, "speaker": "SPEAKER_00", "text": "前一句"},
            {"start": 1.0, "end": 6.0, "speaker": "SPEAKER_00", "text": "這是一段比較長的內容"},
            {"start": 6.0, "end": 7.0, "speaker": "SPEAKER_00", "text": "後一句"},
            {"start": 8.0, "end": 9.0, "speaker": "SPEAKER_01", "text": "另一人"},
        ]
    }

    changed = refine_short_response_speakers(result)

    assert changed == 0
    assert result["segments"][1]["speaker"] == "SPEAKER_00"


def test_whisperx_alignment_runner_falls_back_when_cache_dir_is_not_supported():
    from faster_whisper_GUI.whisperx_alignment_runner import load_alignment_model

    calls = []

    class FakeWhisperX:
        @staticmethod
        def load_align_model(**kwargs):
            calls.append(kwargs)
            if "cache_dir" in kwargs:
                raise TypeError("unexpected keyword argument 'cache_dir'")
            return "model", "metadata"

    model, metadata = load_alignment_model(FakeWhisperX, language="zh", device="cpu")

    assert model == "model"
    assert metadata == "metadata"
    assert "cache_dir" in calls[0]
    assert "cache_dir" not in calls[1]
    assert "model_dir" not in calls[1]


def test_whisperx_diarization_pipeline_handles_empty_speaker_turns(monkeypatch):
    from whisperx import diarize

    class EmptyAnnotation:
        def itertracks(self, yield_label=True):
            return iter(())

    class EmptyPipeline:
        def __call__(self, audio_data, min_speakers=None, max_speakers=None):
            return EmptyAnnotation()

        def to(self, device):
            return self

    monkeypatch.setattr(diarize.Pipeline, "from_pretrained", lambda *args, **kwargs: EmptyPipeline())

    diarize_model = diarize.DiarizationPipeline(use_auth_token="token", device="cpu")
    diarize_df = diarize_model(__import__("numpy").zeros(16000, dtype="float32"))

    assert list(diarize_df.columns) == ["start", "end", "speaker"]
    assert diarize_df.empty


def test_whisperx_alignment_worker_leaves_audio_loading_to_subprocess(monkeypatch):
    from faster_whisper_GUI import whisper_x
    from faster_whisper_GUI.seg_ment import segment_Transcribe

    segment = segment_Transcribe(start=0, end=1, text="hello", words=[])
    info = type("Info", (), {"language": "zh"})()

    def fail_if_parent_loads_audio(path):
        raise AssertionError("parent process should not load audio for subprocess alignment")

    def fake_alignment_subprocess(segments, audio_path, language, backend=None, working_dir=None):
        assert backend is None
        return {"segments": segments}

    monkeypatch.setattr(whisper_x.whisperx, "load_audio", fail_if_parent_loads_audio)
    monkeypatch.setattr(whisper_x, "run_alignment_in_subprocess", fake_alignment_subprocess)

    worker = whisper_x.WhisperXWorker(
        segments_path_info=[([segment], "sample.mp3", info)],
        alignment=True,
        speaker_diarize=False,
    )

    worker.run()

    assert worker.result_segments_path_info[0][1] == "sample.mp3"


def test_whisperx_load_audio_falls_back_when_ffmpeg_cli_is_missing(monkeypatch):
    import subprocess

    import numpy as np
    import whisperx.audio as audio

    expected = np.array([0.1, -0.1], dtype=np.float32)

    def missing_ffmpeg(*args, **kwargs):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(audio.ffmpeg, "run", missing_ffmpeg)
    monkeypatch.setattr(audio, "decode_audio", lambda file, sampling_rate: expected)

    assert audio.load_audio("sample.mp3") is expected


def test_whisperx_audio_fallback_does_not_depend_on_faster_whisper():
    from pathlib import Path

    audio_source = Path("whisperx/audio.py").read_text(encoding="utf-8")

    assert "faster_whisper" not in audio_source
