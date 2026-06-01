# coding:utf-8

from PySide6.QtCore import (QThread, Signal)
import json
import os
import subprocess
import sys
import tempfile
from time import perf_counter
import torch

import whisperx
from .whisperx_backend import get_whisperx_backend, get_whisperx_python_executable, normalize_whisperx_backend, whisperx_backend_display_name
from .seg_ment import (
                        Removerepetition
                        , dictionaryListToSegmentList
                        , segmentListToDictionaryList
                    )
import gc


def get_whisperx_device():
    requested_device = os.environ.get("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cpu").strip().lower()
    if requested_device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def format_elapsed(seconds: float) -> str:
    return f"{seconds:.1f}s"


def _whisperx_subprocess_env(backend: str | None = None) -> dict:
    env = os.environ.copy()
    env["FASTER_WHISPER_GUI_WHISPERX_DEVICE"] = env.get("FASTER_WHISPER_GUI_WHISPERX_DEVICE", "cuda")
    env["FASTER_WHISPER_GUI_WHISPERX_BACKEND"] = normalize_whisperx_backend(backend)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env.setdefault("LOKY_MAX_CPU_COUNT", "1")
    return env


def normalize_huggingface_token(use_auth_token: str | None) -> str | None:
    if use_auth_token is None:
        return None
    token = use_auth_token.strip()
    if token:
        return token
    return None


def _run_whisperx_subprocess(module_name: str, payload: dict, input_path: str, output_path: str, backend: str | None = None):
    with open(input_path, "w", encoding="utf-8") as input_file:
        json.dump(payload, input_file, ensure_ascii=False)

    command = [
        get_whisperx_python_executable(backend=backend),
        "-m",
        module_name,
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]
    try:
        completed = subprocess.run(
            command,
            env=_whisperx_subprocess_env(backend=backend),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as error:
        if getattr(error, "stdout", None):
            print(error.stdout, end="")
        if getattr(error, "stderr", None):
            print(error.stderr, end="")
        raise
    if getattr(completed, "stdout", None):
        print(completed.stdout, end="")
    if getattr(completed, "stderr", None):
        print(completed.stderr, end="")

    with open(output_path, "r", encoding="utf-8") as output_file:
        return json.load(output_file)


def run_alignment_in_subprocess(segments, audio_path: str, language: str, backend: str | None = None, working_dir=None):
    def run_with_paths(input_path, output_path):
        return _run_whisperx_subprocess(
            module_name="faster_whisper_GUI.whisperx_alignment_runner",
            payload={"segments": segments, "audio_path": audio_path, "language": language},
            input_path=input_path,
            output_path=output_path,
            backend=backend,
        )

    if working_dir is not None:
        input_path = os.path.join(working_dir, "whisperx-alignment-input.json")
        output_path = os.path.join(working_dir, "whisperx-alignment-output.json")
        return run_with_paths(input_path, output_path)

    with tempfile.TemporaryDirectory(prefix="faster-whisper-gui-whisperx-") as temp_dir:
        input_path = os.path.join(temp_dir, "input.json")
        output_path = os.path.join(temp_dir, "output.json")
        return run_with_paths(input_path, output_path)


def run_diarization_in_subprocess(
    transcript_result,
    audio_path: str,
    use_auth_token: str = None,
    min_speaker: int = None,
    max_speaker: int = None,
    refine_short_responses: bool = False,
    backend: str | None = None,
    working_dir=None,
):
    payload = {
        "transcript_result": transcript_result,
        "audio_path": audio_path,
        "use_auth_token": normalize_huggingface_token(use_auth_token),
        "min_speaker": min_speaker,
        "max_speaker": max_speaker,
        "refine_short_responses": bool(refine_short_responses),
    }

    def run_with_paths(input_path, output_path):
        return _run_whisperx_subprocess(
            module_name="faster_whisper_GUI.whisperx_diarization_runner",
            payload=payload,
            input_path=input_path,
            output_path=output_path,
            backend=backend,
        )

    if working_dir is not None:
        input_path = os.path.join(working_dir, "whisperx-diarization-input.json")
        output_path = os.path.join(working_dir, "whisperx-diarization-output.json")
        return run_with_paths(input_path, output_path)

    with tempfile.TemporaryDirectory(prefix="faster-whisper-gui-whisperx-") as temp_dir:
        input_path = os.path.join(temp_dir, "input.json")
        output_path = os.path.join(temp_dir, "output.json")
        return run_with_paths(input_path, output_path)


class WhisperXWorker(QThread):
    signal_process_over = Signal(list)

    def __init__(
                self
                , segments_path_info:list
                , alignment:bool
                , speaker_diarize:bool
                , use_auth_token:str=None
                , min_speaker:int=None
                , max_speaker:int=None
                , refine_short_responses:bool=False
                , backend:str=None
                , parent=None
            ) -> None:
        
        super().__init__(parent)
        self.is_running = False

        self.alignment = alignment
        self.speaker_diarize = speaker_diarize

        self.use_auth_token = use_auth_token
        self.min_speaker = min_speaker
        self.max_speaker = max_speaker
        self.refine_short_responses = refine_short_responses
        self.backend = backend

        self.model_alignment = None
        self.metadata_alignment = None
        self.diarize_model = None

        self.segments_path_info = segments_path_info

    def stop(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        self.result_segments_path_info = []
        # audio = None
        for (segments, path, info) in self.segments_path_info:
            file_start = perf_counter()
            audio = None
            # wav2vec2 对齐
            if self.alignment:
                try:
                    # 重新获取当前系统支持的设备
                    print("\nTimeStample alignment")
                    print("WhisperX alignment runs in a subprocess")
                    print(f"WhisperX backend: {whisperx_backend_display_name(self.backend)}")

                    # 获取字典格式的转写结果
                    print("transform transcript result...")
                    segment_dict_list = segmentListToDictionaryList(segments)

                    print("process audio...")

                    print("start alignment subprocess...")
                    self.setStateTool(text="start alignment subprocess (cuda)...",status=False)
                    alignment_start = perf_counter()
                    result_a = run_alignment_in_subprocess(
                        segments=segment_dict_list,
                        audio_path=path,
                        language=info.language,
                        backend=self.backend,
                    )
                    print(f"finished alignment in {format_elapsed(perf_counter() - alignment_start)}")

                    # 清理结果
                    # print("after alignment: ")

                    # 清理可能存在的重复内容 时间戳完全一致的将会被合并 开启 faster-whisper 时间戳细分模式的情况下可能会出现此类结果
                    result_a_c = Removerepetition(result_a=result_a)

                except Exception as e:
                    print("alignment Error")
                    print(f"Error: {e}")
                    self.alignment = False
                    self.signal_process_over.emit(None)
                    result_a_c = segments
                    return
            else:
                del audio
                audio = None
                result_a_c = segments

            if self.speaker_diarize:
                try:
                    print("\nSpeaker diarize and alignment")
                    print("WhisperX speaker diarization runs in a subprocess")
                    print(f"WhisperX backend: {whisperx_backend_display_name(self.backend)}")
                    diarize_start = perf_counter()
                    if not self.alignment:
                        print("process transcription result...")
                        result_a_c = {"segments":segmentListToDictionaryList(result_a_c)}

                    print("start speaker diarization subprocess...")
                    self.setStateTool("start speaker diarization subprocess (cuda)...", False)
                    result_s = run_diarization_in_subprocess(
                        transcript_result=result_a_c,
                        audio_path=path,
                        use_auth_token=self.use_auth_token,
                        min_speaker=self.min_speaker,
                        max_speaker=self.max_speaker,
                        refine_short_responses=self.refine_short_responses,
                        backend=self.backend,
                    )
                    print(f"finished speaker diarize in {format_elapsed(perf_counter() - diarize_start)}")

                    # 检查结果
                    if result_s is None:
                        print("assign speakers to words failed...")
                        self.setStateTool("assign speakers to words failed", False)
                        self.signal_process_over.emit(None)
                        return
                    
                    # print("alignment result: ")
                    # for segment in result_s['segments']:
                    #     try:
                    #         print(f"  [{segment['start']:.2f}s -> {segment['end']:.2f}s] | {segment['speaker']}: {segment['text']}")
                    #     except Exception:
                    #         print(f"  [{segment['start']:.2f}s -> {segment['end']:.2f}s] | {segment['text']}")

                except Exception as e:
                    print("failed to diarize speaker!")
                    print(f"Error: {e}")
                    result_s = result_a_c
                    self.speaker_diarize = False
                    self.signal_process_over.emit(None)
                    return

            else:
                result_s = result_a_c

            if not(audio is None):
                del audio

            try:
                if self.alignment or self.speaker_diarize:
                    # 字典列表转换回对象列表
                    segments = dictionaryListToSegmentList(result_s['segments'])
            except Exception as e:
                print("failed to transform alignment result!")
                print(str(e))
                self.signal_process_over.emit(None)
                return

            self.result_segments_path_info.append((segments, path, info))
            print(f"finished WhisperX processing for {path} in {format_elapsed(perf_counter() - file_start)}")

        self.signal_process_over.emit(self.result_segments_path_info)

        try:
            del self.model_alignment
            self.model_alignment = None
        except:
            pass
        
        try:
            del self.metadata_alignment
            self.metadata_alignment = None
        except:
            pass

        try:
            del self.diarize_segments
            self.diarize_segments = None
        except:
            pass

        # 清除显存缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # gc强制回收，避免内存泄露
        gc.collect()


    def setStateTool(self, text:str , status:bool=False):
        try:
            self.parent().setStateTool(text=text,status=status)
        except Exception as e:
            print(f"To set StateTool Error: {e}")







