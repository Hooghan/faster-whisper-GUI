# FasterWhisperGUI 0.8.6-dev continuation build

## 中文說明

這是基於 `CheshireCC/faster-whisper-GUI` `0.8.5` 繼續維護的非官方測試版。
程式名稱仍沿用 `FasterWhisperGUI`，但此版本標記為 fork 維護的
`0.8.6-dev continuation build`，不是原作者的官方穩定版。

### 主要更新

- 將一般 faster-whisper 轉寫流程更新到已驗證的
  `faster-whisper==1.2.1` source-run 基線。
- 模型清單保留 `large-v3`、`large-v3-turbo`，新增
  `distil-large-v3.5`，並移除重複別名 `large`、`turbo`。
- 啟動時若已有可讀取的本地模型路徑，會自動載入模型。
- 將本地私人設定與追蹤預設設定分離；打包測試設定會清空
  Hugging Face token。
- WhisperX 時間對齊與說話人辨識改由子程序執行，避免和主程式
  faster-whisper 的 CUDA DLL 發生衝突。
- 預設 WhisperX 仍使用已驗證的 vendored backend；另保留隔離的
  upstream WhisperX 實驗路徑供後續測試。
- Demucs 音訊分離改由子程序執行，並修正多層輸出資料夾處理。
- 新增 PyInstaller Windows onedir 打包流程，並補上 VAD 轉寫需要的
  faster-whisper Silero VAD ONNX 資產。
- 新增測試覆蓋依賴基線、token 安全、啟動自動載入、模型清單、
  WhisperX/Demucs runner、打包與 VAD。

### 驗證狀態

- 測試套件：`169 passed`。
- Source GUI：已手動測試一般 faster-whisper 轉寫。
- 打包版 GUI：已測試啟動、模型自動載入、啟用 VAD 的一般轉寫、
  WhisperX vendored 路徑與 Demucs smoke test。

### Windows 打包檔案

Windows 打包檔案較大，因此 release asset 拆成兩個分卷：

- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.sha256.txt`

下載兩個分卷後，在 PowerShell 執行以下命令合併 ZIP：

```powershell
cmd /c copy /b FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01+FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02 FasterWhisperGUI-0.8.6-dev-continuation-build.zip
```

合併後解壓縮 `FasterWhisperGUI-0.8.6-dev-continuation-build.zip`，執行
`FasterWhisperGUI.exe`。

### 注意事項

- 打包檔不包含使用者的 Hugging Face token。
- WhisperX 說話人辨識仍需要使用者到 Hugging Face 同意 pyannote 模型條款，
  並在設定中填入自己的 token。
- upstream WhisperX backend 仍屬實驗路徑；預設發佈路徑使用 vendored
  WhisperX backend。

---

This is an unofficial continuation build based on
`CheshireCC/faster-whisper-GUI` `0.8.5`. It keeps the original application name
while marking this release as a fork-maintained development build, not an
official upstream stable release.

## Highlights

- Updates ordinary faster-whisper transcription to the verified
  `faster-whisper==1.2.1` source-run baseline.
- Keeps `large-v3` and `large-v3-turbo`, adds `distil-large-v3.5`, and omits
  duplicate aliases such as `large` and `turbo` from the GUI model list.
- Enables startup model autoload when a saved local model path exists.
- Separates local private settings from tracked defaults and strips Hugging
  Face tokens from packaged seed configs.
- Runs WhisperX alignment and speaker diarization through subprocesses to avoid
  CUDA DLL conflicts with the main faster-whisper process.
- Keeps the default WhisperX route on the verified vendored backend, with an
  isolated upstream WhisperX experiment path available for testing.
- Runs Demucs audio separation through a subprocess and fixes nested output
  directory handling.
- Adds Windows onedir packaging with PyInstaller and includes the
  faster-whisper Silero VAD ONNX asset required for VAD-enabled transcription.
- Adds a focused test suite covering dependency baselines, token hygiene,
  startup autoload, model names, WhisperX/Demucs runners, packaging, and VAD.

## Verification

- Repository test suite: `169 passed`.
- Source GUI: ordinary faster-whisper transcription manually tested.
- Packaged GUI: startup, model autoload, VAD-enabled ordinary transcription,
  WhisperX vendored paths, and Demucs smoke tests were exercised during the
  continuation work.

## Windows Package Assets

The packaged Windows build is large, so the release asset is split into parts
for GitHub Releases:

- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02`
- `FasterWhisperGUI-0.8.6-dev-continuation-build.sha256.txt`

After downloading both parts, rebuild the ZIP from PowerShell:

```powershell
cmd /c copy /b FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part01+FasterWhisperGUI-0.8.6-dev-continuation-build.zip.part02 FasterWhisperGUI-0.8.6-dev-continuation-build.zip
```

Then extract `FasterWhisperGUI-0.8.6-dev-continuation-build.zip` and run
`FasterWhisperGUI.exe`.

## Notes

- The package does not include user Hugging Face tokens.
- WhisperX speaker diarization still requires the user to accept the relevant
  pyannote model terms on Hugging Face and enter their own token.
- The upstream WhisperX backend remains experimental; the default release path
  uses the vendored WhisperX backend.
