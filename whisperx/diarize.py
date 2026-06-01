import numpy as np
import pandas as pd
from pyannote.audio import Pipeline
from typing import Optional, Union
import torch

from .audio import load_audio, SAMPLE_RATE


def patch_numpy_legacy_nan_alias():
    if not hasattr(np, "NAN"):
        np.NAN = np.nan


def _wrap_hf_hub_download(download_function):
    if getattr(download_function, "_fwgui_accepts_use_auth_token", False):
        return download_function

    def compatible_hf_hub_download(*args, use_auth_token=None, token=None, **kwargs):
        if token is None and use_auth_token is not None:
            token = use_auth_token
        return download_function(*args, token=token, **kwargs)

    compatible_hf_hub_download._fwgui_accepts_use_auth_token = True
    return compatible_hf_hub_download


def patch_pyannote_hf_hub_download():
    module_names = [
        "pyannote.audio.core.pipeline",
        "pyannote.audio.core.model",
        "pyannote.audio.pipelines.speaker_verification",
    ]
    for module_name in module_names:
        try:
            module = __import__(module_name, fromlist=["hf_hub_download"])
            module.hf_hub_download = _wrap_hf_hub_download(module.hf_hub_download)
        except (ImportError, AttributeError):
            pass


def _wrap_speechbrain_from_hparams(from_hparams, default_device=None):
    original_from_hparams = getattr(
        from_hparams, "_fwgui_original_from_hparams", from_hparams
    )

    def compatible_from_hparams(*args, use_auth_token=None, revision=None, **kwargs):
        device = kwargs.pop("device", None) or default_device
        run_opts = dict(kwargs.pop("run_opts", None) or {})
        if "device" in run_opts:
            run_opts["device"] = str(run_opts["device"])
        elif device is not None:
            run_opts["device"] = str(device)
        if run_opts:
            kwargs["run_opts"] = run_opts
        return original_from_hparams(*args, **kwargs)

    compatible_from_hparams._fwgui_drops_legacy_kwargs = True
    compatible_from_hparams._fwgui_original_from_hparams = original_from_hparams
    return compatible_from_hparams


def patch_pyannote_speechbrain_from_hparams(default_device=None):
    try:
        import pyannote.audio.pipelines.speaker_verification as speaker_verification
    except ImportError:
        return

    try:
        encoder_classifier = speaker_verification.SpeechBrain_EncoderClassifier
    except AttributeError:
        return

    encoder_classifier.from_hparams = _wrap_speechbrain_from_hparams(
        encoder_classifier.from_hparams,
        default_device=default_device,
    )


patch_pyannote_hf_hub_download()
patch_pyannote_speechbrain_from_hparams()
patch_numpy_legacy_nan_alias()


class DiarizationPipeline:
    def __init__(
        self,
        model_name="pyannote/speaker-diarization@2.1",
        use_auth_token=None,
        device: Optional[Union[str, torch.device]] = "cpu",
        cache_dir = None
    ):
        if isinstance(device, str):
            device = torch.device(device)
        patch_numpy_legacy_nan_alias()
        patch_pyannote_hf_hub_download()
        patch_pyannote_speechbrain_from_hparams(default_device=device)
        self.model = Pipeline.from_pretrained(model_name, use_auth_token=use_auth_token, cache_dir=cache_dir)# .to(device)
        if self.model is None:
            raise RuntimeError(
                "Could not load the pyannote speaker diarization model. "
                "This usually means the model is private or gated; set a valid "
                "Hugging Face token and accept the pyannote model conditions."
            )
        if self.model:
            try:
                self.model = self.model.to(device)
            except Exception as e:
                print("Move Model To Device Error: \n",str(e))
                pass

    def __call__(self, audio: Union[str, np.ndarray], min_speakers=None, max_speakers=None):
        if isinstance(audio, str):
            audio = load_audio(audio)
        audio_data = {
            'waveform': torch.from_numpy(audio[None, :]),
            'sample_rate': SAMPLE_RATE
        }
        segments = self.model(audio_data, min_speakers=min_speakers, max_speakers=max_speakers)
        diarize_df = pd.DataFrame(segments.itertracks(yield_label=True))
        if diarize_df.empty:
            return pd.DataFrame(columns=["start", "end", "speaker"])
        diarize_df['start'] = diarize_df[0].apply(lambda x: x.start)
        diarize_df['end'] = diarize_df[0].apply(lambda x: x.end)
        diarize_df.rename(columns={2: "speaker"}, inplace=True)
        return diarize_df


def assign_word_speakers(diarize_df, transcript_result, fill_nearest=False):
    transcript_segments = transcript_result["segments"]
    for seg in transcript_segments:
        # assign speaker to segment (if any)
        diarize_df['intersection'] = np.minimum(diarize_df['end'], seg['end']) - np.maximum(diarize_df['start'], seg['start'])
        diarize_df['union'] = np.maximum(diarize_df['end'], seg['end']) - np.minimum(diarize_df['start'], seg['start'])
        # remove no hit, otherwise we look for closest (even negative intersection...)
        if not fill_nearest:
            dia_tmp = diarize_df[diarize_df['intersection'] > 0]
        else:
            dia_tmp = diarize_df
        if len(dia_tmp) > 0:
            # sum over speakers
            speaker = dia_tmp.groupby("speaker")["intersection"].sum().sort_values(ascending=False).index[0]
            seg["speaker"] = speaker
        
        # assign speaker to words
        if 'words' in seg:
            for word in seg['words']:
                if 'start' in word:
                    diarize_df['intersection'] = np.minimum(diarize_df['end'], word['end']) - np.maximum(diarize_df['start'], word['start'])
                    diarize_df['union'] = np.maximum(diarize_df['end'], word['end']) - np.minimum(diarize_df['start'], word['start'])
                    # remove no hit
                    if not fill_nearest:
                        dia_tmp = diarize_df[diarize_df['intersection'] > 0]
                    else:
                        dia_tmp = diarize_df
                    if len(dia_tmp) > 0:
                        # sum over speakers
                        speaker = dia_tmp.groupby("speaker")["intersection"].sum().sort_values(ascending=False).index[0]
                        word["speaker"] = speaker
        
    return transcript_result            


class Segment:
    def __init__(self, start, end, speaker=None):
        self.start = start
        self.end = end
        self.speaker = speaker
