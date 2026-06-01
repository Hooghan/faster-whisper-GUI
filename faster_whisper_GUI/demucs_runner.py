# coding:utf-8

import argparse
import gc
import json
import os
from pathlib import Path

import av
import numpy as np
import soundfile
import torch
from faster_whisper import decode_audio
from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS
from torchaudio.transforms import Fade
from torchaudio.utils import download_asset

from .config import STEMS


def get_runner_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def separate_sources(
    model,
    mix,
    segment=10.0,
    overlap=0.1,
    device=None,
    sample_rate=44100,
):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

    batch, channels, length = mix.shape

    chunk_len = int(sample_rate * segment * (1 + overlap))
    start = 0
    end = chunk_len
    overlap_frames = overlap * sample_rate
    fade = Fade(fade_in_len=0, fade_out_len=int(overlap_frames), fade_shape="linear")

    final = torch.zeros(batch, len(model.sources), channels, length, device=device)

    while start < length - overlap_frames:
        chunk = mix[:, :, start:end]
        chunk = torch.tensor(chunk, dtype=torch.float32).to(device)
        with torch.no_grad():
            out = model.forward(chunk)

        out = fade(out)
        final[:, :, :, start:end] += out
        if start == 0:
            fade.fade_in_len = int(overlap_frames)
            start += int(chunk_len - overlap_frames)
        else:
            start += chunk_len
        end += chunk_len
        if end >= length:
            fade.fade_out_len = 0

        del out
        del chunk
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    del fade
    del mix
    return final


def load_model(model_path: str, device=None):
    download_path = Path(model_path).resolve()
    print(f"download_path: {download_path}")

    if download_path.exists():
        print("found existed model file")
    else:
        print("download model")

    bundle = HDEMUCS_HIGH_MUSDB_PLUS
    sample_rate = bundle.sample_rate
    print(f"Sample rate: {sample_rate}")

    if not download_path.exists():
        download_path.parent.mkdir(parents=True, exist_ok=True)
        download_asset(bundle._model_path, path=download_path, progress=True)

    model = bundle._model_factory_func()
    state_dict = torch.load(download_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    model.to(device)
    return model


def resample_audio(audio, sample_rate) -> np.ndarray:
    file_path = os.path.abspath(audio)

    split_stereo = True
    with av.open(file_path) as av_file:
        stream = next(s for s in av_file.streams if s.codec_context.type == "audio")
        audio_channel_num = stream.channels
        if audio_channel_num < 2:
            print("single-channel audio")
            split_stereo = False
        else:
            print("multi-channel audio")

    print("resample audio data")
    return decode_audio(file_path, sample_rate, split_stereo)


def save_result(model, file_path: str, sources: torch.Tensor, stems: int, output_path: str, sample_rate=44100):
    sources_list = model.sources
    print(f"sources_list: {sources_list}")

    sources = list(sources[0])
    audios: dict = dict(zip(sources_list, sources))

    data_dir, file_name = os.path.split(file_path)
    file_output = ".".join(file_name.split(".")[:-1])

    if stems == 0:
        stems = STEMS[1:-1]
    elif stems != (len(STEMS) - 1):
        stems = [STEMS[stems]]
    else:
        stems = ["Vocals", "Others"]
        audios["others"] = audios["other"]
        audios.pop("other")
        audios["others"] = audios["others"] + audios["bass"]
        audios.pop("bass")
        audios["others"] = audios["others"] + audios["drums"]
        audios.pop("drums")

    print(f"output stems: {stems}")

    if not output_path:
        output_path = os.path.join(data_dir, file_output)
    else:
        output_path = os.path.join(output_path, file_output)

    if not os.path.exists(output_path):
        print(f"create output folder: {output_path}")
        os.makedirs(output_path, exist_ok=True)

    for stem in stems:
        spec = audios[stem.lower()][:, :].cpu()
        output_file_name = os.path.join(
            output_path,
            ".".join([file_output + f"_{stem.lower()}", "wav"]),
        )
        print(f"save file: {output_file_name}")
        soundfile.write(output_file_name, spec.numpy().T, sample_rate)


def run_demucs(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as input_file:
        payload = json.load(input_file)

    device = get_runner_device()
    print(f"Demucs subprocess device: {device}")

    model = load_model(payload["model_path"], device=device)
    for audio in payload["audio"]:
        print(f"current task: {audio}")
        print("resample audio...")
        samples = np.asarray(resample_audio(audio, payload["sample_rate"]))
        print("samples shape: ", samples.shape)

        print("separate sources...")
        sources = separate_sources(
            model,
            samples[None],
            payload["segment"],
            payload["overlap"],
            device,
            payload["sample_rate"],
        )

        print("save files...")
        save_result(
            model=model,
            file_path=audio,
            sources=sources,
            stems=payload["stems"],
            output_path=payload["output_path"],
            sample_rate=payload["sample_rate"],
        )

        del samples
        del sources
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump({"ok": True}, output_file, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run_demucs(args.input, args.output)


if __name__ == "__main__":
    main()
