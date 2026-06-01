# coding:utf-8

import argparse
import json
import os
from time import perf_counter

import torch
from .whisperx_backend import get_whisperx_backend, import_whisperx_for_backend, whisperx_backend_display_name

WHISPERX_BACKEND = get_whisperx_backend()
whisperx = import_whisperx_for_backend(WHISPERX_BACKEND)


def get_runner_device():
    requested_device = os.environ.get("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cuda").strip().lower()
    if requested_device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def format_elapsed(seconds: float) -> str:
    return f"{seconds:.1f}s"


def remove_repetition(result):
    cleaned = {"segments": []}
    if "word_segments" in result:
        cleaned["word_segments"] = result["word_segments"]

    start = -1
    end = -1
    for segment in result["segments"]:
        segment_start = segment["start"]
        segment_end = segment["end"]
        if start == segment_start and end == segment_end:
            continue
        start = segment_start
        end = segment_end
        cleaned["segments"].append(segment)
        print(f"  [{start:.2f}s --> {end:.2f}s] {segment['text']}")

    return cleaned


def load_alignment_model(whisperx_module, language: str, device):
    try:
        return whisperx_module.load_align_model(
            language_code=language,
            device=device,
            model_dir=r"./cache",
            cache_dir=r"./cache",
        )
    except TypeError as error:
        if "cache_dir" not in str(error) and "model_dir" not in str(error):
            raise
        return whisperx_module.load_align_model(
            language_code=language,
            device=device,
        )


def run_alignment(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as input_file:
        payload = json.load(input_file)

    device = get_runner_device()
    audio_path = payload["audio_path"]
    language = payload["language"]
    segments = payload["segments"]

    print(f"WhisperX subprocess device: {device}")
    print(f"WhisperX backend: {whisperx_backend_display_name(WHISPERX_BACKEND)}")
    audio_start = perf_counter()
    audio = whisperx.load_audio(audio_path)
    print(f"WhisperX subprocess audio duration: {len(audio) / 16000:.1f}s")
    print(f"loaded audio in {format_elapsed(perf_counter() - audio_start)}")

    model_start = perf_counter()
    model, metadata = load_alignment_model(whisperx, language=language, device=device)
    print(f"loaded wav2vec2 model in {format_elapsed(perf_counter() - model_start)}")

    alignment_start = perf_counter()
    result = whisperx.align(segments, model, metadata, audio, device, return_char_alignments=False)
    print(f"finished alignment in {format_elapsed(perf_counter() - alignment_start)}")

    cleaned = remove_repetition(result)
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(cleaned, output_file, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run_alignment(args.input, args.output)


if __name__ == "__main__":
    main()
