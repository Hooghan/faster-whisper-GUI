"""Dependency-light model factory shared by the GUI loading thread and tests."""

from __future__ import annotations

from typing import Any, Callable


FASTER_WHISPER_BACKEND = "faster-whisper"
FUNASR_BACKEND = "funasr"


def _funasr_device(device: str, device_index: int | list[int]) -> str | None:
    if device == "auto":
        return None
    if device != "cuda":
        return device
    index = device_index[0] if isinstance(device_index, list) else device_index
    return f"cuda:{index}"


def recommended_num_workers(model: Any, configured_workers: int) -> int:
    if getattr(model, "asr_backend", FASTER_WHISPER_BACKEND) == FUNASR_BACKEND:
        return 1
    return configured_workers


def create_asr_model(
    *,
    backend: str,
    model_size_or_path: str,
    device: str,
    device_index: int | list[int],
    compute_type: str,
    cpu_threads: int,
    num_workers: int,
    download_root: str,
    local_files_only: bool,
    whisper_model_cls: Callable[..., Any] | None = None,
    funasr_model_cls: Callable[..., Any] | None = None,
) -> Any:
    if backend == FASTER_WHISPER_BACKEND:
        if whisper_model_cls is None:
            from faster_whisper import WhisperModel

            whisper_model_cls = WhisperModel
        return whisper_model_cls(
            model_size_or_path,
            device=device,
            device_index=device_index,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            num_workers=num_workers,
            download_root=download_root,
            local_files_only=local_files_only,
        )

    if backend == FUNASR_BACKEND:
        if funasr_model_cls is None:
            from .funasr_backend import FunASRWhisperCompatibleModel

            funasr_model_cls = FunASRWhisperCompatibleModel
        funasr_kwargs = {"model": model_size_or_path}
        if funasr_device := _funasr_device(device, device_index):
            funasr_kwargs["device"] = funasr_device
        model = funasr_model_cls(**funasr_kwargs)
        return model.load()

    raise ValueError(f"Unsupported ASR backend: {backend}")
