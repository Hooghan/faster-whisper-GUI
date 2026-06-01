from faster_whisper_GUI.transcribe import TranscribeWorker, normalize_vad_parameters


class FakeInfo:
    language = "zh"
    language_probability = 1.0
    duration = 1.0
    duration_after_vad = 1.0


class FakeModel:
    def __init__(self):
        self.transcribe_kwargs = None

    def transcribe(self, **kwargs):
        self.transcribe_kwargs = kwargs
        return iter(()), FakeInfo()


def default_parameters():
    return {
        "language": None,
        "task": False,
        "beam_size": 1,
        "best_of": 5,
        "patience": 1.0,
        "length_penalty": 1.0,
        "temperature": [0.0],
        "compression_ratio_threshold": 1.4,
        "log_prob_threshold": -10.0,
        "no_speech_threshold": 0.9,
        "condition_on_previous_text": False,
        "initial_prompt": None,
        "prefix": None,
        "suppress_blank": True,
        "suppress_tokens": [-1],
        "without_timestamps": False,
        "max_initial_timestamp": 1.0,
        "word_timestamps": True,
        "prepend_punctuations": "",
        "append_punctuations": "",
        "multilingual": False,
        "repetition_penalty": 1.0,
        "no_repeat_ngram_size": 0,
        "prompt_reset_on_temperature": 0.5,
        "max_new_tokens": None,
        "chunk_length": 30,
        "clip_timestamps": 0,
        "hallucination_silence_threshold": 0.5,
        "hotwords": "",
        "language_detection_threshold": 0.5,
        "language_detection_segments": 1,
    }


def legacy_vad_parameters():
    return {
        "onset": 0.2,
        "min_speech_duration_ms": 0,
        "max_speech_duration_s": float("inf"),
        "min_silence_duration_ms": 2000,
        "window_size_samples": 1024,
        "speech_pad_ms": 400,
    }


def test_legacy_vad_onset_maps_to_current_threshold():
    normalized = normalize_vad_parameters(legacy_vad_parameters())

    assert normalized["threshold"] == 0.2
    assert "onset" not in normalized
    assert "window_size_samples" not in normalized


def test_transcribe_worker_passes_compatible_vad_parameters_to_model():
    model = FakeModel()
    worker = TranscribeWorker(
        model=model,
        parameters=default_parameters(),
        vad_filter=True,
        vad_parameters=legacy_vad_parameters(),
    )
    worker.is_running = True

    info, segments = worker.transcribe_file("audio.wav")

    assert isinstance(info, FakeInfo)
    assert segments == []
    assert model.transcribe_kwargs["vad_parameters"]["threshold"] == 0.2
    assert "onset" not in model.transcribe_kwargs["vad_parameters"]
    assert "window_size_samples" not in model.transcribe_kwargs["vad_parameters"]
