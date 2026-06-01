# coding:utf-8

from importlib import metadata


def get_package_version(package_name: str) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return "unknown"


__version__ = "0.8.6-dev"
__FasterWhisper_version__ = get_package_version("faster-whisper")
__WhisperX_version__ = "vendored"
__Demucs_version__ = "v4.0"
