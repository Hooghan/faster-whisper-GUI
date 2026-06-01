# coding:utf-8

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
import tempfile
import warnings


BACKEND_ENV = "FASTER_WHISPER_GUI_WHISPERX_BACKEND"
UPSTREAM_PYTHON_ENV = "FASTER_WHISPER_GUI_WHISPERX_UPSTREAM_PYTHON"


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_whisperx_backend(backend: str | None = None) -> str:
    if backend is None:
        backend = os.environ.get(BACKEND_ENV, "vendored")
    backend = str(backend).strip().lower()
    if backend == "upstream":
        return "upstream"
    return "vendored"


def whisperx_backend_display_name(backend: str | None = None) -> str:
    return normalize_whisperx_backend(backend)


def get_whisperx_backend() -> str:
    return normalize_whisperx_backend()


def get_whisperx_python_executable(repo_root: Path | None = None, backend: str | None = None) -> str:
    if normalize_whisperx_backend(backend) != "upstream":
        return sys.executable

    explicit_python = os.environ.get(UPSTREAM_PYTHON_ENV, "").strip()
    if explicit_python:
        return explicit_python

    if repo_root is None:
        repo_root = get_repo_root()

    windows_python = repo_root / ".venv-whisperx-next" / "Scripts" / "python.exe"
    if windows_python.exists():
        return str(windows_python)

    posix_python = repo_root / ".venv-whisperx-next" / "bin" / "python"
    if posix_python.exists():
        return str(posix_python)

    return sys.executable


def remove_repo_root_from_sys_path(repo_root: Path) -> None:
    resolved_repo_root = repo_root.resolve()
    filtered_paths = []
    for entry in sys.path:
        if entry == "":
            continue
        try:
            if Path(entry).resolve() == resolved_repo_root:
                continue
        except OSError:
            pass
        filtered_paths.append(entry)
    sys.path[:] = filtered_paths


def is_vendored_whisperx(module_file: Path, repo_root: Path) -> bool:
    try:
        return module_file.resolve().is_relative_to((repo_root / "whisperx").resolve())
    except OSError:
        return False


def configure_upstream_model_cache(repo_root: Path) -> Path:
    cache_root = repo_root / "cache" / "whisperx-next"
    hf_cache = cache_root / "huggingface"
    nltk_cache = cache_root / "nltk_data"
    pyannote_cache = cache_root / "pyannote"
    hf_cache.mkdir(parents=True, exist_ok=True)
    nltk_cache.mkdir(parents=True, exist_ok=True)
    pyannote_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(hf_cache))
    os.environ.setdefault("NLTK_DATA", str(nltk_cache))
    os.environ.setdefault("PYANNOTE_CACHE", str(pyannote_cache))
    return cache_root


def create_windows_ffmpeg_shim(ffmpeg_path: Path, shim_dir: Path | None = None) -> Path:
    if ffmpeg_path.name.lower() == "ffmpeg.exe":
        return ffmpeg_path

    if shim_dir is None:
        shim_dir = Path(tempfile.gettempdir()) / "faster-whisper-gui-whisperx-next"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim_path = shim_dir / "ffmpeg.exe"
    if not shim_path.exists() or shim_path.stat().st_size != ffmpeg_path.stat().st_size:
        shutil.copy2(ffmpeg_path, shim_path)
    return shim_path


def ensure_ffmpeg_on_path() -> Path | None:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return Path(system_ffmpeg)

    try:
        import imageio_ffmpeg
    except ImportError:
        return None

    ffmpeg_path = create_windows_ffmpeg_shim(Path(imageio_ffmpeg.get_ffmpeg_exe()))
    os.environ["PATH"] = str(ffmpeg_path.parent) + os.pathsep + os.environ.get("PATH", "")
    return ffmpeg_path


def configure_upstream_warning_filters() -> None:
    warnings.filterwarnings(
        "ignore",
        message=r".*torchcodec is not installed correctly.*",
        category=UserWarning,
    )


def import_whisperx_for_backend(backend: str | None = None, repo_root: Path | None = None):
    if backend is None:
        backend = get_whisperx_backend()
    if repo_root is None:
        repo_root = get_repo_root()

    if backend == "upstream":
        configure_upstream_model_cache(repo_root)
        configure_upstream_warning_filters()
        ensure_ffmpeg_on_path()
        remove_repo_root_from_sys_path(repo_root)

    import whisperx

    if backend == "upstream":
        module_file = Path(getattr(whisperx, "__file__", ""))
        if is_vendored_whisperx(module_file, repo_root):
            raise RuntimeError(
                "refusing to use vendored whisperx; upstream backend must import "
                "the pip-installed whisperx package from .venv-whisperx-next"
            )

    return whisperx
