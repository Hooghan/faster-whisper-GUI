# coding: utf-8
"""Command-line smoke test for the upstream WhisperX upgrade track.

Run this from an isolated virtual environment that installed
requirements-dev-whisperx-next.txt. The script deliberately avoids the
repository's vendored whisperx/ directory so the smoke test exercises the pip
package.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from time import perf_counter


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def configure_local_model_cache(repo_root: Path) -> Path:
    cache_root = repo_root / "cache" / "whisperx-next"
    hf_cache = cache_root / "huggingface"
    nltk_cache = cache_root / "nltk_data"
    pyannote_cache = cache_root / "pyannote"
    hf_cache.mkdir(parents=True, exist_ok=True)
    nltk_cache.mkdir(parents=True, exist_ok=True)
    pyannote_cache.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(hf_cache)
    os.environ["TRANSFORMERS_CACHE"] = str(hf_cache)
    os.environ["NLTK_DATA"] = str(nltk_cache)
    os.environ["PYANNOTE_CACHE"] = str(pyannote_cache)
    return cache_root


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


def import_upstream_whisperx(repo_root: Path):
    remove_repo_root_from_sys_path(repo_root)
    import whisperx

    module_file = Path(getattr(whisperx, "__file__", ""))
    if is_vendored_whisperx(module_file, repo_root):
        raise RuntimeError(
            "refusing to use vendored whisperx; run this script from an "
            "isolated environment so it imports the pip-installed package"
        )
    return whisperx


def get_device(requested_device: str):
    import torch

    if requested_device == "cuda" and torch.cuda.is_available():
        return "cuda"
    return "cpu"


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
    ffmpeg_dir = str(ffmpeg_path.parent)
    current_path = os.environ.get("PATH", "")
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
    return ffmpeg_path


def load_transcript(transcript_json: Path | None) -> dict:
    if transcript_json is None:
        return {
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "smoke test",
                    "words": [],
                }
            ]
        }
    return json.loads(transcript_json.read_text(encoding="utf-8"))


def run_alignment_smoke(whisperx, audio, transcript: dict, language: str, device: str) -> dict:
    print("starting alignment smoke")
    start = perf_counter()
    model, metadata = whisperx.load_align_model(language_code=language, device=device)
    result = whisperx.align(
        transcript["segments"],
        model,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )
    print(f"finished alignment smoke in {perf_counter() - start:.1f}s")
    return result


def get_diarization_pipeline_class(whisperx, diarize_module=None):
    pipeline_class = getattr(whisperx, "DiarizationPipeline", None)
    if pipeline_class is not None:
        return pipeline_class
    if diarize_module is None:
        from whisperx import diarize as diarize_module
    return diarize_module.DiarizationPipeline


def run_diarization_smoke(
    whisperx,
    audio,
    transcript: dict,
    device: str,
    hf_token: str | None,
    diarization_model: str | None,
    min_speakers: int | None,
    max_speakers: int | None,
) -> dict:
    print("starting diarization smoke")
    start = perf_counter()
    pipeline_class = get_diarization_pipeline_class(whisperx)
    try:
        diarize_model = pipeline_class(model_name=diarization_model, token=hf_token, device=device)
    except TypeError:
        diarize_model = pipeline_class(model_name=diarization_model, use_auth_token=hf_token, device=device)
    diarize_segments = diarize_model(
        audio,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
    )
    result = whisperx.assign_word_speakers(diarize_segments, transcript)
    assigned = sum(1 for segment in result.get("segments", []) if segment.get("speaker"))
    total = len(result.get("segments", []))
    print(f"finished diarization smoke in {perf_counter() - start:.1f}s")
    print(f"assigned speakers to {assigned}/{total} transcript segments")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test upstream whisperx==3.8.6")
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--transcript-json", type=Path)
    parser.add_argument("--language", default="zh")
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    parser.add_argument("--hf-token", default=os.environ.get("HUGGINGFACE_TOKEN"))
    parser.add_argument("--diarization-model")
    parser.add_argument("--min-speakers", type=int)
    parser.add_argument("--max-speakers", type=int)
    parser.add_argument("--check-audio", action="store_true")
    parser.add_argument("--skip-alignment", action="store_true")
    parser.add_argument("--skip-diarization", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    cache_root = configure_local_model_cache(repo_root)
    whisperx = import_upstream_whisperx(repo_root)
    device = get_device(args.device)

    print(f"using whisperx from {Path(whisperx.__file__).resolve()}")
    print(f"using device: {device}")
    print(f"using model cache at {cache_root}")
    ffmpeg_path = ensure_ffmpeg_on_path()
    if ffmpeg_path is None:
        print("ffmpeg not found; audio-loading smoke tests may fail")
    else:
        print(f"using ffmpeg from {ffmpeg_path}")

    transcript = load_transcript(args.transcript_json)
    result = transcript
    audio = None

    if args.check_audio:
        audio = whisperx.load_audio(str(args.audio))
        print(f"loaded audio samples: {len(audio)}")

    if not args.skip_alignment:
        if audio is None:
            audio = whisperx.load_audio(str(args.audio))
        result = run_alignment_smoke(whisperx, audio, result, args.language, device)

    if not args.skip_diarization:
        if audio is None:
            audio = whisperx.load_audio(str(args.audio))
        result = run_diarization_smoke(
            whisperx,
            audio,
            result,
            device,
            args.hf_token,
            args.diarization_model,
            args.min_speakers,
            args.max_speakers,
        )

    if args.output is not None:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("WhisperX next smoke completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
