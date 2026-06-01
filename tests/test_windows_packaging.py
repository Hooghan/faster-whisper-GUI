from pathlib import Path


SPEC_TEXT = Path("build_tools/FasterWhisperGUI.spec").read_text(encoding="utf-8")
SCRIPT_TEXT = Path("package-windows-source.cmd").read_text(encoding="utf-8")
PACKAGE_REQ_TEXT = Path("requirements-dev-package.txt").read_text(encoding="utf-8")


def test_package_requirements_pins_pyinstaller_for_python_312_source_build():
    assert "pyinstaller==6.20.0" in PACKAGE_REQ_TEXT


def test_pyinstaller_spec_builds_onedir_source_package_without_local_user_config():
    assert "repo_root = Path.cwd().resolve()" in SPEC_TEXT
    assert 'name="FasterWhisperGUI-0.8.6-dev-source"' in SPEC_TEXT
    assert "FasterWhisperGUI.py" in SPEC_TEXT
    assert "fasterWhisperGUIConfig.json" in SPEC_TEXT
    assert "huggingface-config.json" in SPEC_TEXT
    assert "user" not in SPEC_TEXT
    assert "cache" not in SPEC_TEXT
    assert ".venv" not in SPEC_TEXT


def test_gitignore_allows_tracking_the_packaging_spec():
    gitignore_text = Path(".gitignore").read_text(encoding="utf-8")

    assert "*.spec" in gitignore_text
    assert "!build_tools/*.spec" in gitignore_text


def test_pyinstaller_spec_collects_runtime_packages_and_resources():
    assert 'collect_submodules("faster_whisper_GUI")' in SPEC_TEXT
    assert 'collect_submodules("resource")' in SPEC_TEXT
    assert 'collect_submodules("whisperx")' in SPEC_TEXT
    assert 'collect_data_files("faster_whisper", include_py_files=False)' in SPEC_TEXT
    assert 'copy_metadata("faster-whisper")' in SPEC_TEXT
    assert '"faster_whisper"' in SPEC_TEXT
    assert '"ctranslate2"' in SPEC_TEXT
    assert '"qfluentwidgets"' in SPEC_TEXT


def test_windows_package_script_verifies_before_building_and_keeps_secrets_local():
    assert "-m pytest tests -q -p no:cacheprovider" in SCRIPT_TEXT
    assert "-m PyInstaller --noconfirm --clean" in SCRIPT_TEXT
    assert "-m tools.seed_packaged_local_config" in SCRIPT_TEXT
    assert "requirements-dev-package.txt" in SCRIPT_TEXT
    assert "strips" in SCRIPT_TEXT
    assert "private Hugging Face tokens" in SCRIPT_TEXT
    assert "Source user\\*.local.json files are not" in SCRIPT_TEXT
