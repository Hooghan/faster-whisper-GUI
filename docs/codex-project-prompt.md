# Prompt For Another Codex Account

Copy this prompt into another Codex account/session after opening the
`Hooghan/faster-whisper-GUI` repository.

```text
請用繁體中文協助我繼續維護這個專案。

這是 Hooghan/faster-whisper-GUI，也就是 CheshireCC/faster-whisper-GUI 0.8.5
的非官方續維護版本。目前主要分支是 codex-source-dev-run，版本標籤是
0.8.6-dev continuation build。

開始前請先讀：
1. AGENTS.md
2. docs/continuation-status.md
3. docs/codex-project-handoff.md
4. docs/release-notes-0.8.6-dev.md

重要規則：
- 不要提交 Hugging Face token 或 user/*.local.json。
- 不要提交 dist、build、cache、.venv、.venv-whisperx-next、log、temp。
- 一般 faster-whisper 轉寫目前以 faster-whisper==1.2.1 為驗證基線。
- WhisperX 預設使用 vendored backend；upstream backend 仍是實驗路徑。
- WhisperX 和 Demucs 的模型工作走 subprocess，避免 CUDA DLL 衝突。
- 修改前先看現有模式，修改後用對應測試驗證。

如果需要提交，先執行：
git grep --cached -n -E "hf_[A-Za-z0-9]{20,}"

如果 Codex 沙盒不能寫入 .git，請把需要執行的 Git 指令列給我，我會在
PowerShell 執行。
```
