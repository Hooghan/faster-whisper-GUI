from pathlib import Path


REQUIREMENTS_TEXT = Path("requirements-dev-faster-whisper.txt").read_text(encoding="utf-8")
CUDA_REQUIREMENTS_TEXT = Path("requirements-dev-cuda-cu124.txt").read_text(encoding="utf-8")
TEST_REQUIREMENTS_TEXT = Path("requirements-dev-test.txt").read_text(encoding="utf-8")
DEMUCS_REQUIREMENTS_TEXT = Path("requirements-dev-demucs.txt").read_text(encoding="utf-8")
WHISPERX_NEXT_REQUIREMENTS_TEXT = Path("requirements-dev-whisperx-next.txt").read_text(encoding="utf-8")
PACKAGE_REQUIREMENTS_TEXT = Path("requirements-dev-package.txt").read_text(encoding="utf-8")
LEGACY_REQUIREMENTS_TEXT = Path("requirements.txt").read_text(encoding="utf-8")
README_TEXT = Path("README.md").read_text(encoding="utf-8")


def test_ordinary_source_run_uses_forward_faster_whisper_pin():
    assert "faster-whisper==1.2.1" in REQUIREMENTS_TEXT.splitlines()


def test_readme_documents_current_model_selector_baseline():
    assert "faster-whisper==1.2.1" in README_TEXT
    assert "model selector" in README_TEXT
    assert "omits duplicate aliases" in README_TEXT
    assert "distil-large-v3.5" in README_TEXT


def test_ordinary_source_run_bounds_verified_faster_whisper_core_runtime():
    requirement_lines = REQUIREMENTS_TEXT.splitlines()

    assert "ctranslate2>=4.7.2,<4.8" in requirement_lines
    assert "huggingface-hub>=1.16,<1.17" in requirement_lines
    assert "tokenizers>=0.22,<0.24" in requirement_lines
    assert "onnxruntime>=1.26,<1.27" in requirement_lines
    assert "tqdm>=4.67,<5" in requirement_lines


def test_ordinary_source_run_uses_pyside6_610_batch():
    assert "PySide6>=6.10,<6.11" in REQUIREMENTS_TEXT.splitlines()


def test_cuda_124_addon_uses_forward_torch_baseline():
    cuda_requirement_lines = CUDA_REQUIREMENTS_TEXT.splitlines()

    assert "--index-url https://download.pytorch.org/whl/cu124" in cuda_requirement_lines
    assert "torch==2.6.0" in cuda_requirement_lines


def test_whisperx_addon_has_separate_dependency_entrypoint():
    whisperx_requirements = Path("requirements-dev-whisperx.txt").read_text(encoding="utf-8")
    requirement_lines = whisperx_requirements.splitlines()

    assert "--extra-index-url https://download.pytorch.org/whl/cu124" in requirement_lines
    assert "torchaudio==2.6.0" in requirement_lines
    assert "transformers==5.9.0" in requirement_lines
    assert "pyannote.audio==3.1.1" in requirement_lines
    assert "nltk==3.9.4" in requirement_lines
    assert "pandas>=3.0,<3.1" in requirement_lines
    assert "matplotlib>=3.10,<3.11" in requirement_lines


def test_whisperx_next_addon_is_isolated_from_verified_vendored_baseline():
    requirement_lines = WHISPERX_NEXT_REQUIREMENTS_TEXT.splitlines()

    assert "whisperx==3.8.6" in requirement_lines
    assert "hf_xet>=1.2,<1.3" in requirement_lines
    assert any("CUDA 12.8" in line for line in requirement_lines)
    assert "requirements-dev-whisperx-next.txt" in README_TEXT


def test_demucs_addon_has_separate_dependency_entrypoint():
    requirement_lines = DEMUCS_REQUIREMENTS_TEXT.splitlines()

    assert "--extra-index-url https://download.pytorch.org/whl/cu124" in requirement_lines
    assert "torchaudio==2.6.0" in requirement_lines
    assert "soundfile>=0.13,<0.14" in requirement_lines


def test_windows_package_build_has_separate_dependency_entrypoint():
    assert "pyinstaller==6.20.0" in PACKAGE_REQUIREMENTS_TEXT.splitlines()
    assert "requirements-dev-package.txt" in README_TEXT
    assert "package-windows-source.cmd" in README_TEXT


def test_ordinary_source_run_uses_verified_fluent_widgets_batch():
    assert "PySide6-Fluent-Widgets>=1.11,<1.12" in REQUIREMENTS_TEXT.splitlines()


def test_ordinary_source_run_uses_verified_auxiliary_dependency_baseline():
    requirement_lines = REQUIREMENTS_TEXT.splitlines()

    assert "av>=17,<18" in requirement_lines
    assert "ffmpeg-python==0.2.0" in requirement_lines
    assert "requests>=2.34,<3" in requirement_lines
    assert "opencc-python-reimplemented==0.1.7" in requirement_lines
    assert "webvtt-py==0.5.1" in requirement_lines
    assert "numpy>=2,<3" in requirement_lines


def test_ordinary_source_run_does_not_install_test_runner():
    assert "pytest" not in REQUIREMENTS_TEXT.splitlines()


def test_test_runner_has_its_own_dependency_entrypoint():
    assert "pytest>=9,<10" in TEST_REQUIREMENTS_TEXT.splitlines()


def test_legacy_requirements_file_is_not_an_install_entrypoint():
    assert "Do not install this file for the continuation baseline." in LEGACY_REQUIREMENTS_TEXT
    assert "-r requirements-dev-faster-whisper.txt" not in LEGACY_REQUIREMENTS_TEXT
    assert "faster-whisper==" not in LEGACY_REQUIREMENTS_TEXT
    assert "torch==" not in LEGACY_REQUIREMENTS_TEXT
    assert "pyside6" not in LEGACY_REQUIREMENTS_TEXT.lower()


def test_readme_documents_current_ordinary_dependency_entrypoint():
    source_run_section = README_TEXT.split("## Windows source run for ordinary faster-whisper transcription", 1)[1]

    assert "Startup model autoload is enabled by default" in source_run_section
    assert "independent from automatic config saving" in source_run_section
    assert "finish-source-run-merge.cmd" in source_run_section
    assert "check-source-run-rc.cmd" in source_run_section
    assert "does not commit or merge" in source_run_section
    assert "requirements-dev-faster-whisper.txt" in source_run_section
    assert "requirements-dev-cuda-cu124.txt" in source_run_section
    assert "requirements-dev-whisperx.txt" in source_run_section
    assert "requirements-dev-whisperx-next.txt" in source_run_section
    assert "requirements-dev-demucs.txt" in source_run_section
    assert "requirements-dev-package.txt" in source_run_section
    assert "requirements-dev-test.txt" in source_run_section


def test_readme_documents_hugging_face_token_and_gated_model_access():
    assert "Hugging Face token and gated model access" in README_TEXT
    assert "Do not distribute the original author's Hugging Face token" in README_TEXT
    assert "user/*.local.json" in README_TEXT
    assert "Ordinary faster-whisper transcription with a local model path" in README_TEXT
    assert "WhisperX time alignment" in README_TEXT
    assert "WhisperX speaker diarization / speaker labels" in README_TEXT
    assert "pyannote/speaker-diarization@2.1" in README_TEXT
    assert "pyannote/speaker-diarization-community-1" in README_TEXT
    assert "Demucs audio separation" in README_TEXT
    assert "ordinary transcription and alignment still work" in README_TEXT


def test_readme_marks_legacy_requirements_as_unverified_full_feature_context():
    assert "`requirements.txt`" in README_TEXT
    assert "legacy full-feature" in README_TEXT
    assert "not the current ordinary source-run install path" in README_TEXT


def test_finish_script_verifies_without_committing_or_merging():
    finish_script = Path("finish-source-run-merge.cmd").read_text(encoding="utf-8")

    assert "git commit" not in finish_script
    assert "git merge" not in finish_script
    assert '-m pytest tests -q -p no:cacheprovider' in finish_script
    assert "requirements-dev-faster-whisper.txt" in finish_script
    assert "requirements-dev-cuda-cu124.txt" in finish_script
    assert "requirements-dev-whisperx.txt" in finish_script
    assert "requirements-dev-whisperx-next.txt" in finish_script
    assert "requirements-dev-demucs.txt" in finish_script
    assert "requirements-dev-package.txt" in finish_script
    assert "requirements-dev-test.txt" in finish_script
    assert "requirements.txt" in finish_script
    assert "Source-run release-candidate handoff" in finish_script
    assert "check-source-run-rc.cmd" in finish_script
    assert "launch-source-gui.cmd" in finish_script
    assert "saved model autoloads" in finish_script
    assert "package-windows-source.cmd" in finish_script


def test_launch_script_guides_missing_source_run_environment():
    launch_script = Path("launch-source-gui.cmd").read_text(encoding="utf-8")

    assert 'if not exist ".venv\\Scripts\\python.exe"' in launch_script
    assert "requirements-dev-faster-whisper.txt" in launch_script
    assert "FasterWhisperGUI.py" in launch_script
    assert "pause" in launch_script
