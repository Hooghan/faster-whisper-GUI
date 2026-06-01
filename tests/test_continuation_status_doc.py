from pathlib import Path


STATUS_TEXT = Path("docs/continuation-status.md").read_text(encoding="utf-8")
README_TEXT = Path("README.md").read_text(encoding="utf-8")


def test_continuation_status_documents_verified_ordinary_transcription_baseline():
    assert "Last updated: 2026-06-01" in STATUS_TEXT
    assert "ordinary faster-whisper transcription" in STATUS_TEXT
    assert "0.8.6-dev" in STATUS_TEXT
    assert "Startup model autoload is enabled by default" in STATUS_TEXT
    assert "autoload switch is kept independent" in STATUS_TEXT
    assert "faster-whisper==1.2.1" in STATUS_TEXT
    assert "PySide6>=6.10,<6.11" in STATUS_TEXT
    assert "requirements-dev-faster-whisper.txt" in STATUS_TEXT
    assert "requirements-dev-package.txt" in STATUS_TEXT
    assert "distil-large-v3.5" in STATUS_TEXT
    assert "`large-v3-turbo` at index `11`" in STATUS_TEXT


def test_continuation_status_documents_checked_core_dependency_limits():
    assert "onnxruntime 1.26.0" in STATUS_TEXT
    assert "huggingface-hub 1.16.1" in STATUS_TEXT
    assert "tokenizers 0.23.1" in STATUS_TEXT


def test_continuation_status_documents_unverified_feature_areas():
    assert "WhisperX alignment" in STATUS_TEXT
    assert "speaker diarization" in STATUS_TEXT
    assert "Windows executable packaging" in STATUS_TEXT


def test_continuation_status_documents_whisperx_addon_import_baseline():
    assert "requirements-dev-whisperx.txt" in STATUS_TEXT
    assert "transformers==5.9.0" in STATUS_TEXT
    assert "pyannote.audio==3.1.1" in STATUS_TEXT
    assert "WhisperX import" in STATUS_TEXT
    assert "WhisperX alignment runs in a subprocess" in STATUS_TEXT
    assert "speaker diarization runs in a subprocess" in STATUS_TEXT
    assert "defaults to CUDA" in STATUS_TEXT
    assert "GUI smoke-tested on 2026-05-26" in STATUS_TEXT
    assert "SPEAKER_00" in STATUS_TEXT
    assert "assigned speakers to .../... transcript segments" in STATUS_TEXT


def test_continuation_status_documents_whisperx_next_diarization_smoke():
    assert "whisperx==3.8.6" in STATUS_TEXT
    assert "pyannote/speaker-diarization-community-1" in STATUS_TEXT
    assert "diarization smoke passed on CPU" in STATUS_TEXT
    assert "assigned speakers to `1/1` transcript segments" in STATUS_TEXT
    assert "non-fatal warnings" in STATUS_TEXT
    assert "torchcodec DLL warning" in STATUS_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_BACKEND=upstream" in STATUS_TEXT
    assert ".venv-whisperx-next" in STATUS_TEXT
    assert "upstream backend runner path was smoke-tested on 2026-05-26" in STATUS_TEXT
    assert "faster_whisper_GUI.whisperx_alignment_runner" in STATUS_TEXT
    assert "faster_whisper_GUI.whisperx_diarization_runner" in STATUS_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL" in STATUS_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST=1" in STATUS_TEXT
    assert "model_name=None" in STATUS_TEXT
    assert "12/12" in STATUS_TEXT
    assert "短回应修正" in STATUS_TEXT
    assert "refined ... short response speaker assignments" in STATUS_TEXT
    assert "WhisperX 后端" in STATUS_TEXT
    assert "vendored" in STATUS_TEXT
    assert "upstream" in STATUS_TEXT
    assert "WhisperX backend: vendored" in STATUS_TEXT
    assert "WhisperX backend: upstream" in STATUS_TEXT
    assert "refine_short_responses=true" in STATUS_TEXT
    assert "refined `3` short response speaker assignments" in STATUS_TEXT
    assert "upstream backend alignment runner was verified" in STATUS_TEXT
    assert "aligned timestamps for all `12/12` transcript segments" in STATUS_TEXT


def test_continuation_status_documents_demucs_cuda_subprocess_smoke_test():
    assert "requirements-dev-demucs.txt" in STATUS_TEXT
    assert "Demucs audio separation runs in a subprocess" in STATUS_TEXT
    assert "cache/hdemucs_high_trained.pt" in STATUS_TEXT
    assert "GUI smoke test" in STATUS_TEXT
    assert "2026-05-25" in STATUS_TEXT
    assert "nested custom output directories" in STATUS_TEXT


def test_continuation_status_documents_verification_command():
    assert '.\\.venv\\Scripts\\python.exe -m pytest tests -q -p no:cacheprovider' in STATUS_TEXT
    assert "The current verified result is `168 passed`." in STATUS_TEXT


def test_continuation_status_documents_source_run_release_candidate_scope():
    assert "Source-Run Release Candidate" in STATUS_TEXT
    assert "release candidate for Windows source" in STATUS_TEXT
    assert "finish-source-run-merge.cmd" in STATUS_TEXT
    assert "check-source-run-rc.cmd" in STATUS_TEXT
    assert "readable saved model target" in STATUS_TEXT
    assert "launch-source-gui.cmd" in STATUS_TEXT
    assert "saved model autoloads" in STATUS_TEXT
    assert "choose the verified model path once" in STATUS_TEXT
    assert "modelTargetAccessible=True" in STATUS_TEXT
    assert "Load over" in STATUS_TEXT
    assert "temp/source-run-smoke.wav" in STATUS_TEXT
    assert "one English transcript segment" in STATUS_TEXT
    assert "package-windows-source.cmd" in STATUS_TEXT
    assert "packaged executable" in STATUS_TEXT
    assert "0.8.6-dev` startup line" in STATUS_TEXT
    assert "FileNotFoundError" in STATUS_TEXT
    assert "PyInstaller's" in STATUS_TEXT
    assert "seeds the packaged `user/` config" in STATUS_TEXT
    assert "huggingface_user_token` is stripped" in STATUS_TEXT
    assert "Silero VAD ONNX asset" in STATUS_TEXT
    assert "silero_vad_v6.onnx" in STATUS_TEXT
    assert "use their own Hugging Face token" in STATUS_TEXT
    assert "accept pyannote model access terms" in STATUS_TEXT
    assert "saved only in local private config files" in STATUS_TEXT
    assert "which features need Hugging Face credentials" in STATUS_TEXT
    assert "Ordinary local faster-whisper transcription and Demucs do not require a token" in STATUS_TEXT
    assert "packaged ordinary transcription initially failed" in STATUS_TEXT
    assert "smoke test" in STATUS_TEXT


def test_continuation_status_documents_safe_temp_cleanup():
    assert "clear_temp_srt_files()" in STATUS_TEXT
    assert "only removes `.srt` files" in STATUS_TEXT
    assert "Transcription and audio-capture temp directory creation" in STATUS_TEXT
    assert "create the temp directory or log files" in STATUS_TEXT
    assert "load_language_config()" in STATUS_TEXT
    assert "Speaker audio splitting now writes `00_list.csv` with a context manager" in STATUS_TEXT


def test_readme_links_to_continuation_status():
    assert "docs/continuation-status.md" in README_TEXT
    assert "speaker column" in README_TEXT
    assert "SPEAKER_00" in README_TEXT
    assert "CPU diarization smoke tests passed" in README_TEXT
    assert "pyannote/speaker-diarization-community-1" in README_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_BACKEND" in README_TEXT
    assert "verified vendored WhisperX" in README_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL" in README_TEXT
    assert "FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST" in README_TEXT
    assert "短回应修正" in README_TEXT
    assert "WhisperX 后端" in README_TEXT
    assert "Hugging Face token and gated model access" in README_TEXT
    assert "Do not distribute the original author's Hugging Face token" in README_TEXT
    assert "WhisperX speaker diarization / speaker labels" in README_TEXT
