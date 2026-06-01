# coding:utf-8

import argparse
import json
import os
import sys
from pathlib import Path
from time import perf_counter


def configure_local_model_cache():
    cache_root = Path("./cache").resolve()
    torch_home = cache_root / "torch"
    hf_home = cache_root / "huggingface"
    pyannote_cache = cache_root / "pyannote"
    torch_home.mkdir(parents=True, exist_ok=True)
    hf_home.mkdir(parents=True, exist_ok=True)
    pyannote_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TORCH_HOME", str(torch_home))
    os.environ.setdefault("HF_HOME", str(hf_home))
    os.environ.setdefault("PYANNOTE_CACHE", str(pyannote_cache))


configure_local_model_cache()


def disable_optional_speechbrain_k2_lazy_import():
    sys.modules.pop("speechbrain.integrations.k2_fsa", None)
    try:
        import speechbrain.inference as speechbrain_inference

        sys.modules["speechbrain.pretrained"] = speechbrain_inference
    except Exception:
        pass
    try:
        from speechbrain.utils.importutils import LazyModule
    except Exception:
        return

    if getattr(LazyModule.ensure_module, "_fwgui_windows_inspect_compatible", False):
        return

    original_ensure_module = LazyModule.ensure_module

    def compatible_ensure_module(self, stacklevel: int):
        try:
            import inspect

            importer_frame = inspect.getframeinfo(sys._getframe(stacklevel + 1))
            normalized_filename = importer_frame.filename.replace("\\", "/")
            if normalized_filename.endswith("/inspect.py") or importer_frame.filename.endswith("\\inspect.py"):
                raise AttributeError()
        except AttributeError:
            raise
        except Exception:
            pass
        return original_ensure_module(self, stacklevel)

    compatible_ensure_module._fwgui_windows_inspect_compatible = True
    LazyModule.ensure_module = compatible_ensure_module


disable_optional_speechbrain_k2_lazy_import()

import torch
from .whisperx_backend import get_whisperx_backend, import_whisperx_for_backend, whisperx_backend_display_name

WHISPERX_BACKEND = get_whisperx_backend()
whisperx = import_whisperx_for_backend(WHISPERX_BACKEND)


DIARIZATION_MODEL_ENV = "FASTER_WHISPER_GUI_WHISPERX_DIARIZATION_MODEL"
ASSIGN_FILL_NEAREST_ENV = "FASTER_WHISPER_GUI_WHISPERX_ASSIGN_FILL_NEAREST"
REFINE_SHORT_RESPONSES_ENV = "FASTER_WHISPER_GUI_WHISPERX_REFINE_SHORT_RESPONSES"


def patch_torch_load_for_pyannote_checkpoints():
    if getattr(torch.load, "_fwgui_pyannote_weights_only_compatible", False):
        return

    original_torch_load = torch.load

    def compatible_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False
        return original_torch_load(*args, **kwargs)

    compatible_torch_load._fwgui_pyannote_weights_only_compatible = True
    torch.load = compatible_torch_load


patch_torch_load_for_pyannote_checkpoints()


def get_runner_device():
    requested_device = os.environ.get("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cuda").strip().lower()
    if requested_device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def format_elapsed(seconds: float) -> str:
    return f"{seconds:.1f}s"


def summarize_diarization_segments(diarize_segments):
    if hasattr(diarize_segments, "to_dict"):
        rows = diarize_segments.to_dict("records")
    else:
        rows = list(diarize_segments or [])
    speakers = {
        row.get("speaker")
        for row in rows
        if isinstance(row, dict) and row.get("speaker")
    }
    return len(rows), len(speakers)


def summarize_speaker_assignment(result):
    transcript_segments = result.get("segments", [])
    assigned_segments = [
        segment for segment in transcript_segments if segment.get("speaker")
    ]
    return len(assigned_segments), len(transcript_segments)


def get_diarization_model_name():
    model_name = os.environ.get(DIARIZATION_MODEL_ENV, "").strip()
    if model_name:
        return model_name
    return None


def get_assign_fill_nearest():
    value = os.environ.get(ASSIGN_FILL_NEAREST_ENV, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_refine_short_responses():
    value = os.environ.get(REFINE_SHORT_RESPONSES_ENV, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def resolve_refine_short_responses(payload):
    if "refine_short_responses" in payload:
        return bool(payload.get("refine_short_responses"))
    return get_refine_short_responses()


def get_diarization_pipeline_class(whisperx_module, diarize_module=None):
    pipeline_class = getattr(whisperx_module, "DiarizationPipeline", None)
    if pipeline_class is not None:
        return pipeline_class
    if diarize_module is None:
        from whisperx import diarize as diarize_module
    return diarize_module.DiarizationPipeline


def create_diarization_pipeline(whisperx_module, model_name, use_auth_token, device, cache_dir):
    pipeline_class = get_diarization_pipeline_class(whisperx_module)
    common_kwargs = {
        "device": device,
        "cache_dir": cache_dir,
    }
    if model_name is not None:
        common_kwargs["model_name"] = model_name
    try:
        return pipeline_class(
            token=use_auth_token,
            **common_kwargs,
        )
    except TypeError:
        return pipeline_class(
            use_auth_token=use_auth_token,
            **common_kwargs,
        )


def assign_speakers(whisperx_module, diarize_segments, transcript_result, fill_nearest=False):
    try:
        return whisperx_module.assign_word_speakers(
            diarize_segments,
            transcript_result,
            fill_nearest=fill_nearest,
        )
    except TypeError as error:
        if "fill_nearest" not in str(error):
            raise
        return whisperx_module.assign_word_speakers(diarize_segments, transcript_result)


def assign_speakers_with_fallback(
    whisperx_module,
    diarize_segments,
    transcript_result,
    fill_nearest=False,
):
    result = assign_speakers(
        whisperx_module,
        diarize_segments,
        transcript_result,
        fill_nearest=fill_nearest,
    )
    assigned_count, total_count = summarize_speaker_assignment(result)
    if fill_nearest or assigned_count > 0 or total_count == 0:
        return result, False

    diarize_count, _ = summarize_diarization_segments(diarize_segments)
    if diarize_count == 0:
        return result, False

    fallback_result = assign_speakers(
        whisperx_module,
        diarize_segments,
        transcript_result,
        fill_nearest=True,
    )
    fallback_assigned_count, _ = summarize_speaker_assignment(fallback_result)
    if fallback_assigned_count > assigned_count:
        return fallback_result, True
    return result, False


def segment_duration(segment):
    return float(segment.get("end", 0.0)) - float(segment.get("start", 0.0))


def normalized_text_length(segment):
    return len(str(segment.get("text", "")).strip().replace(" ", ""))


def update_segment_speaker(segment, speaker):
    segment["speaker"] = speaker
    for word in segment.get("words", []) or []:
        if isinstance(word, dict):
            word["speaker"] = speaker


def refine_short_response_speakers(
    result,
    max_duration_seconds=1.6,
    max_text_chars=8,
):
    segments = result.get("segments", [])
    speakers = [
        segment.get("speaker")
        for segment in segments
        if segment.get("speaker")
    ]
    unique_speakers = sorted(set(speakers))
    if len(unique_speakers) != 2:
        return 0

    changed = 0
    for index in range(1, len(segments) - 1):
        previous_segment = segments[index - 1]
        segment = segments[index]
        next_segment = segments[index + 1]
        speaker = segment.get("speaker")
        neighbor_speaker = previous_segment.get("speaker")
        if not speaker or not neighbor_speaker:
            continue
        if speaker != neighbor_speaker or next_segment.get("speaker") != neighbor_speaker:
            continue
        if segment_duration(segment) > max_duration_seconds:
            continue
        if normalized_text_length(segment) > max_text_chars:
            continue

        alternate_speakers = [name for name in unique_speakers if name != neighbor_speaker]
        if not alternate_speakers:
            continue
        update_segment_speaker(segment, alternate_speakers[0])
        changed += 1
    return changed


def run_diarization(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as input_file:
        payload = json.load(input_file)

    device = get_runner_device()
    audio_path = payload["audio_path"]
    transcript_result = payload["transcript_result"]
    use_auth_token = payload.get("use_auth_token")
    min_speaker = payload.get("min_speaker")
    max_speaker = payload.get("max_speaker")
    model_name = get_diarization_model_name()
    fill_nearest = get_assign_fill_nearest()
    refine_short_responses = resolve_refine_short_responses(payload)

    print(f"WhisperX diarization subprocess device: {device}")
    print(f"WhisperX backend: {whisperx_backend_display_name(WHISPERX_BACKEND)}")
    print(f"speaker diarization model: {model_name or 'default'}")
    print(f"speaker count limits: min={min_speaker}, max={max_speaker}")
    print(f"speaker assignment fill nearest: {fill_nearest}")
    print(f"speaker short response refinement: {refine_short_responses}")

    audio_start = perf_counter()
    audio = whisperx.load_audio(audio_path)
    print(f"WhisperX diarization audio duration: {len(audio) / 16000:.1f}s")
    print(f"loaded audio in {format_elapsed(perf_counter() - audio_start)}")

    model_start = perf_counter()
    diarize_model = create_diarization_pipeline(
        whisperx,
        model_name=model_name,
        use_auth_token=use_auth_token,
        device=device,
        cache_dir=r"./cache",
    )
    print(f"loaded speaker diarize model in {format_elapsed(perf_counter() - model_start)}")

    diarize_start = perf_counter()
    diarize_segments = diarize_model(
        audio,
        min_speakers=min_speaker,
        max_speakers=max_speaker,
    )
    diarize_count, diarize_speaker_count = summarize_diarization_segments(diarize_segments)
    print(
        "speaker diarization produced "
        f"{diarize_count} speaker turns across {diarize_speaker_count} speakers"
    )
    print(f"finished speaker diarize in {format_elapsed(perf_counter() - diarize_start)}")

    assign_start = perf_counter()
    result, used_assignment_fallback = assign_speakers_with_fallback(
        whisperx,
        diarize_segments,
        transcript_result,
        fill_nearest=fill_nearest,
    )
    assigned_count, total_count = summarize_speaker_assignment(result)
    print(f"assigned speakers to {assigned_count}/{total_count} transcript segments")
    if used_assignment_fallback:
        print("speaker assignment retried with nearest diarization turn because direct overlap assigned 0 segments")
    print(f"assigned speakers to words in {format_elapsed(perf_counter() - assign_start)}")
    if refine_short_responses:
        refined_count = refine_short_response_speakers(result)
        print(f"refined {refined_count} short response speaker assignments")

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run_diarization(args.input, args.output)


if __name__ == "__main__":
    main()
