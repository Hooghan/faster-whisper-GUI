# coding:utf-8

import json
import os
import subprocess
import sys
import tempfile

from PySide6.QtCore import QThread, Signal


def _demucs_subprocess_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def run_demucs_in_subprocess(payload: dict, input_path: str, output_path: str):
    with open(input_path, "w", encoding="utf-8") as input_file:
        json.dump(payload, input_file, ensure_ascii=False)

    command = [
        sys.executable,
        "-m",
        "faster_whisper_GUI.demucs_runner",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]

    try:
        completed = subprocess.run(
            command,
            env=_demucs_subprocess_env(),
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


class DemucsWorker(QThread):
    signal_vr_over = Signal(bool)
    file_process_status = Signal(dict)

    def __init__(
        self,
        parent,
        audio: list[str],
        stems: int,
        model_path: str,
        *,
        segment: float = 10,
        overlap: float = 0.1,
        sample_rate: int = 44100,
        output_path: str = "",
    ) -> None:
        super().__init__(parent)
        self.is_running = False
        self.model_path = model_path
        self.model = None
        self.audio = audio
        self.sampleRate = sample_rate
        self.segment = segment
        self.overlap = overlap
        self.stems = stems
        self.output_path = output_path

    def run(self) -> None:
        self.is_running = True
        payload = {
            "audio": self.audio,
            "stems": self.stems,
            "model_path": self.model_path,
            "segment": self.segment,
            "overlap": self.overlap,
            "sample_rate": self.sampleRate,
            "output_path": self.output_path,
        }

        try:
            self.file_process_status.emit({"file": "", "status": False, "task": "load model"})
            with tempfile.TemporaryDirectory(prefix="faster-whisper-gui-demucs-") as temp_dir:
                input_path = os.path.join(temp_dir, "input.json")
                output_path = os.path.join(temp_dir, "output.json")
                result = run_demucs_in_subprocess(payload, input_path, output_path)
        except Exception as error:
            print(f"demucs subprocess error:\n{error}")
            self.signal_vr_over.emit(False)
            self.stop()
            return

        self.signal_vr_over.emit(bool(result.get("ok")))
        self.stop()

    def stop(self):
        self.is_running = False
