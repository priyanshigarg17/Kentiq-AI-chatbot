# ============================================================
#  stt_module.py — Speech-to-Text (NO PyAudio, FREE Whisper)
#
#  ✔ No microphone dependency
#  ✔ No PyAudio
#  ✔ Uses Whisper locally (FREE)
#  ✔ Works with uploaded audio files
# ============================================================

import os
import tempfile
from typing import Optional


# Cache model globally (important for performance)
_whisper_model = None


def load_whisper_model(model_size: str = "base"):
    """
    Loads Whisper model only once (singleton pattern).
    
    Args:
        model_size: tiny | base | small | medium | large
    
    Returns:
        Loaded Whisper model
    """
    global _whisper_model

    if _whisper_model is None:
        try:
            import whisper
            print(f"[STT] Loading Whisper model: {model_size}...")
            _whisper_model = whisper.load_model(model_size)
            print("[STT] Whisper model loaded successfully.")
        except ImportError:
            raise RuntimeError(
                "Whisper not installed.\n"
                "Run: pip install openai-whisper\n"
                "Also install torch: pip install torch"
            )

    return _whisper_model


# ──────────────────────────────────────────
# MAIN FUNCTION — TRANSCRIBE FILE
# ──────────────────────────────────────────

def transcribe_audio_file(audio_path: str, model_size: str = "base") -> str:
    """
    Transcribes an audio file using local Whisper model.

    Args:
        audio_path: Path to audio file (wav/mp3/m4a)
        model_size: Whisper model size

    Returns:
        Transcribed text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = load_whisper_model(model_size)

    print(f"[STT] Transcribing file: {audio_path}")
    result = model.transcribe(audio_path)

    text = result.get("text", "").strip()
    print(f"[STT] Transcription: {text}")

    return text


# ──────────────────────────────────────────
# OPTIONAL — TRANSCRIBE FROM BYTES (API USE)
# ──────────────────────────────────────────

def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """
    Transcribes audio from raw bytes (used in FastAPI upload).

    Args:
        audio_bytes: Raw audio file bytes
        suffix: File extension (.wav, .mp3, etc.)

    Returns:
        Transcribed text
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        text = transcribe_audio_file(tmp_path)
    finally:
        os.remove(tmp_path)

    return text


# ──────────────────────────────────────────
# HELPER — SUPPORTED FORMATS
# ──────────────────────────────────────────

def is_supported_audio(filename: str) -> bool:
    """
    Checks if file format is supported.
    """
    allowed = (".wav", ".mp3", ".m4a", ".flac", ".ogg")
    return filename.lower().endswith(allowed)