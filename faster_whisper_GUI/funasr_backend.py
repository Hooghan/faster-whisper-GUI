"""FunASR/SenseVoice adapter for the FasterWhisperGUI transcription pipeline.

The GUI currently expects a model object with a ``transcribe(...)`` method that
returns ``(segments, info)`` in a faster-whisper-like shape. This adapter keeps
FunASR optional and converts common ``AutoModel.generate`` outputs to that small
contract so the UI can wire a SenseVoice backend without rewriting subtitle
export code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator


SENSEVOICE_TAG_RE = re.compile(r"<\|[^|>]+\|>")


@dataclass
class FunASRSegment:
    start: float
    end: float
    text: str
    words: list[Any] = field(default_factory=list)


@dataclass
class FunASRTranscriptionInfo:
    language: str = "auto"
    language_probability: float = 1.0
    duration: float = 0.0
    duration_after_vad: float = 0.0
    all_language_probs: list[Any] = field(default_factory=list)
    vad_options: dict[str, Any] = field(default_factory=dict)


def normalize_funasr_language(language: str | None) -> str:
    """Map GUI language values to the compact FunASR language hints."""
    if not language:
        return "auto"
    language = language.split("-")[0].strip().lower()
    if language in {"auto", ""}:
        return "auto"
    if language in {"zhs", "zht", "zh"}:
        return "zh"
    return language


def _timestamp_to_seconds(value: Any) -> float:
    # FunASR sentence and token timestamps are milliseconds, including values
    # below one second. Magnitude-based guessing turns 800 ms into 800 seconds.
    return float(value) / 1000.0


def _clean_sensevoice_text(value: Any) -> str:
    return SENSEVOICE_TAG_RE.sub("", str(value or "")).strip()


def _detect_result_language(results: Any) -> str | None:
    items = [results] if isinstance(results, dict) else results or []
    for item in items:
        if not isinstance(item, dict):
            continue
        explicit = item.get("language")
        if explicit:
            return normalize_funasr_language(str(explicit))
        match = re.search(r"<\|([a-z]{2,3})\|>", str(item.get("text") or ""), re.IGNORECASE)
        if match:
            return normalize_funasr_language(match.group(1))
    return None


def _media_duration_seconds(audio: str) -> float:
    try:
        import av

        with av.open(audio, metadata_errors="ignore") as container:
            if container.duration is not None:
                return max(float(container.duration) / 1_000_000.0, 0.0)

            durations = [
                float(stream.duration * stream.time_base)
                for stream in container.streams.audio
                if stream.duration is not None and stream.time_base is not None
            ]
            return max(durations, default=0.0)
    except (ImportError, OSError, ValueError):
        return 0.0


def _segment_from_item(item: dict[str, Any], default_start: float = 0.0) -> FunASRSegment:
    text = _clean_sensevoice_text(item.get("text") or item.get("sentence"))
    start = item.get("start", default_start)
    end = item.get("end", start)

    if "timestamp" in item and item["timestamp"]:
        timestamps = item["timestamp"]
        if isinstance(timestamps, list) and timestamps:
            first = timestamps[0]
            last = timestamps[-1]
            if isinstance(first, (list, tuple)) and len(first) >= 2:
                start = first[0]
                end = last[1] if isinstance(last, (list, tuple)) and len(last) >= 2 else first[1]

    start_s = _timestamp_to_seconds(start)
    end_s = _timestamp_to_seconds(end)
    if end_s < start_s:
        end_s = start_s
    return FunASRSegment(start=start_s, end=end_s, text=text)


def funasr_results_to_segments(
    results: Any, fallback_duration: float = 0.0
) -> list[FunASRSegment]:
    """Convert common FunASR result shapes to GUI-compatible segments."""
    if isinstance(results, dict):
        results = [results]

    segments: list[FunASRSegment] = []
    default_start = 0.0
    for item in results or []:
        if not isinstance(item, dict):
            continue

        sentence_info = item.get("sentence_info") or item.get("sentences")
        if isinstance(sentence_info, list) and sentence_info:
            for sentence in sentence_info:
                if isinstance(sentence, dict):
                    segment = _segment_from_item(sentence, default_start=default_start)
                    if segment.text:
                        segments.append(segment)
                        default_start = segment.end
            continue

        segment = _segment_from_item(item, default_start=default_start)
        if segment.text:
            segments.append(segment)
            default_start = segment.end

    if not segments:
        return [FunASRSegment(start=0.0, end=0.0, text="")]
    if len(segments) == 1 and segments[0].end <= segments[0].start and fallback_duration > 0:
        segments[0].end = fallback_duration
    return segments


class FunASRWhisperCompatibleModel:
    """Lazy FunASR model wrapper with a faster-whisper-like ``transcribe`` API."""

    asr_backend = "funasr"

    def __init__(
        self,
        model: str = "iic/SenseVoiceSmall",
        vad_model: str | None = "fsmn-vad",
        punc_model: str | None = None,
        device: str | None = None,
        **model_kwargs: Any,
    ) -> None:
        self.model_id = model
        self.vad_model = vad_model
        self.punc_model = punc_model
        self.device = device
        self.model_kwargs = model_kwargs
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from funasr import AutoModel
            except ImportError as exc:
                raise RuntimeError(
                    'FunASR backend requires the optional dependency: pip install "funasr>=1.3.29"'
                ) from exc

            kwargs = dict(self.model_kwargs)
            if self.vad_model:
                kwargs["vad_model"] = self.vad_model
            if self.punc_model:
                kwargs["punc_model"] = self.punc_model
            if self.device:
                kwargs["device"] = self.device
            self._model = AutoModel(model=self.model_id, **kwargs)
        return self._model

    def load(self) -> "FunASRWhisperCompatibleModel":
        """Load the optional runtime eagerly so GUI load errors are immediate."""
        self._load_model()
        return self

    def transcribe(
        self,
        audio: str,
        language: str | None = None,
        hotwords: str | None = None,
        task: str = "transcribe",
        **_: Any,
    ) -> tuple[Iterator[FunASRSegment], FunASRTranscriptionInfo]:
        if task != "transcribe":
            raise ValueError("The FunASR / SenseVoice backend does not support translation")

        language_hint = normalize_funasr_language(language)
        generate_kwargs: dict[str, Any] = {"input": audio, "sentence_timestamp": True}
        if language_hint != "auto":
            generate_kwargs["language"] = language_hint
        if hotwords:
            generate_kwargs["hotword"] = hotwords

        results = self._load_model().generate(**generate_kwargs)
        segments = funasr_results_to_segments(results)
        if len(segments) == 1 and segments[0].end <= segments[0].start:
            segments = funasr_results_to_segments(
                results, fallback_duration=_media_duration_seconds(audio)
            )
        duration = max((segment.end for segment in segments), default=0.0)
        detected_language = _detect_result_language(results)
        info = FunASRTranscriptionInfo(
            language=detected_language or language_hint,
            duration=duration,
            duration_after_vad=duration,
        )
        return iter(segments), info
