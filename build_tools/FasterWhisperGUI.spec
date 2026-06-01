# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


repo_root = Path.cwd().resolve()

datas = [
    (str(repo_root / "fasterWhisperGUIConfig.json"), "."),
    (str(repo_root / "huggingface-config.json"), "."),
    (str(repo_root / "config" / "config.json"), "config"),
]

for optional_dir in ("ffmpeg", "bin"):
    path = repo_root / optional_dir
    if path.exists():
        datas.append((str(path), optional_dir))

datas += collect_data_files("qfluentwidgets", include_py_files=False)
datas += collect_data_files("faster_whisper", include_py_files=False)
datas += copy_metadata("faster-whisper")

hiddenimports = []
hiddenimports += collect_submodules("faster_whisper_GUI")
hiddenimports += collect_submodules("resource")
hiddenimports += collect_submodules("whisperx")
hiddenimports += [
    "faster_whisper",
    "ctranslate2",
    "tokenizers",
    "onnxruntime",
    "numpy",
]

block_cipher = None

a = Analysis(
    [str(repo_root / "FasterWhisperGUI.py")],
    pathex=[str(repo_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tests",
        "pytest",
        "jupyter",
        "IPython",
        "notebook",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FasterWhisperGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FasterWhisperGUI-0.8.6-dev-source",
)
