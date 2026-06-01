import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse(relative_path: str) -> ast.Module:
    return ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))


def module_level_imports(relative_path: str) -> set[str]:
    modules: set[str] = set()

    for node in parse(relative_path).body:
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)

    return modules


def test_package_init_does_not_import_whisperx_for_ordinary_flow():
    assert "whisperx" not in module_level_imports("faster_whisper_GUI/__init__.py")


def test_ui_main_window_does_not_import_demucs_page_at_module_import_time():
    assert (
        "demucsPageNavigationInterface"
        not in module_level_imports("faster_whisper_GUI/UI_MainWindows.py")
    )


def test_main_window_does_not_import_optional_workers_at_module_import_time():
    imports = module_level_imports("faster_whisper_GUI/mainWindows.py")

    assert "torch" not in imports
    assert "whisper_x" not in imports
    assert "de_mucs" not in imports


def test_transcribe_worker_does_not_import_torch_at_module_import_time():
    assert "torch" not in module_level_imports("faster_whisper_GUI/transcribe.py")


def test_transcribe_worker_does_not_import_pyaudio_at_module_import_time():
    assert "pyaudio" not in module_level_imports("faster_whisper_GUI/transcribe.py")
