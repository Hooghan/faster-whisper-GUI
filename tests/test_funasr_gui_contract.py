from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_model_page_exposes_and_persists_backend_selection():
    source = (ROOT / "faster_whisper_GUI" / "modelPageNavigationInterface.py").read_text()

    assert "backend_combox" in source
    assert "funasr_model_combox" in source
    assert 'param["backend"]' in source
    assert 'param["funasrModel"]' in source


def test_main_window_routes_selected_backend_to_model_loader():
    source = (ROOT / "faster_whisper_GUI" / "mainWindows.py").read_text()

    assert 'model_param["backend"]' in source
    assert '"backend":model_param["backend"]' in source
    assert "recommended_num_workers(self.FasterWhisperModel, num_worker)" in source
    assert "errorSignal.connect(self.setModelLoadError)" in source


def test_optional_dependency_and_user_docs_are_shipped():
    requirement = (ROOT / "requirements-funasr.txt").read_text().strip()
    docs = (ROOT / "docs" / "funasr_sensevoice_backend.md").read_text()

    assert requirement == "funasr>=1.3.29"
    assert "Suggested UI follow-up" not in docs
    assert "FunASR / SenseVoice" in docs


def test_transcription_errors_reach_the_gui_without_skipping_cleanup():
    worker_source = (ROOT / "faster_whisper_GUI" / "transcribe.py").read_text()
    window_source = (ROOT / "faster_whisper_GUI" / "mainWindows.py").read_text()

    assert "signal_error = Signal(str)" in worker_source
    assert "self.signal_error.emit(str(exc))" in worker_source
    assert "signal_error.connect(self.transcribeError)" in window_source


if __name__ == "__main__":
    test_model_page_exposes_and_persists_backend_selection()
    test_main_window_routes_selected_backend_to_model_loader()
    test_optional_dependency_and_user_docs_are_shipped()
    test_transcription_errors_reach_the_gui_without_skipping_cleanup()
    print("FunASR GUI contract tests passed")
