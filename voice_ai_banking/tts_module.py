# tts_module.py
# Auto-generated file

# ============================================================
#  tts_module.py — Text-to-Speech (TTS) Module
#
#  PURPOSE:
#    Converts bot text responses into audio speech.
#    Supports multiple TTS engines:
#      - gTTS   (Google TTS — requires internet, free)
#      - pyttsx3 (offline, no internet needed)
#      - Azure   (Microsoft Cognitive Services — best quality)
#
#  The engine is chosen from .env: TTS_ENGINE=gtts|pyttsx3|azure
#
#  USAGE:
#    from tts_module import speak, speak_to_file
#    speak("Hello, welcome to Dubai Bank.")
#    audio_path = speak_to_file("Your balance is AED 48,250.75")
# ============================================================

import os
import io
import uuid
import tempfile
from config import Config


# ──────────────────────────────────────────
# ENGINE: gTTS (Google Text-to-Speech)
# ──────────────────────────────────────────

def _speak_gtts(text: str, output_path: str) -> str:
    """
    Uses Google Text-to-Speech (gTTS) to generate MP3 audio.
    Requires: pip install gtts
    Requires: internet connection
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        return output_path
    except ImportError:
        raise RuntimeError("gTTS not installed. Run: pip install gtts")
    except Exception as e:
        raise RuntimeError(f"gTTS error: {e}")


# ──────────────────────────────────────────
# ENGINE: pyttsx3 (Offline TTS)
# ──────────────────────────────────────────

def _speak_pyttsx3(text: str, output_path: str) -> str:
    """
    Uses pyttsx3 for fully offline text-to-speech.
    Requires: pip install pyttsx3
    Note: Output format is WAV (not MP3).
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)      # Words per minute
        engine.setProperty("volume", 1.0)    # 0.0 to 1.0

        # Try to set a female voice if available
        voices = engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.id.lower():
                engine.setProperty("voice", voice.id)
                break

        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path
    except ImportError:
        raise RuntimeError("pyttsx3 not installed. Run: pip install pyttsx3")
    except Exception as e:
        raise RuntimeError(f"pyttsx3 error: {e}")


# ──────────────────────────────────────────
# ENGINE: Azure TTS (Best Quality)
# ──────────────────────────────────────────

def _speak_azure(text: str, output_path: str) -> str:
    """
    Uses Microsoft Azure Cognitive Services TTS.
    Requires: pip install azure-cognitiveservices-speech
    Requires: AZURE_TTS_KEY and AZURE_TTS_REGION in .env
    """
    try:
        import azure.cognitiveservices.speech as speechsdk

        if not Config.AZURE_TTS_KEY:
            raise RuntimeError("AZURE_TTS_KEY not set in .env")

        speech_config = speechsdk.SpeechConfig(
            subscription=Config.AZURE_TTS_KEY,
            region=Config.AZURE_TTS_REGION
        )
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.Canceled:
            raise RuntimeError(f"Azure TTS cancelled: {result.cancellation_details.reason}")

        return output_path
    except ImportError:
        raise RuntimeError("Azure SDK not installed. Run: pip install azure-cognitiveservices-speech")
    except Exception as e:
        raise RuntimeError(f"Azure TTS error: {e}")


# ──────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────

def speak_to_file(text: str, filename: str = None) -> str:
    """
    Converts text to speech and saves to an audio file.

    Args:
        text:     The text to speak
        filename: Optional filename. If None, a temp file is created.

    Returns:
        Path to the generated audio file.

    Example:
        path = speak_to_file("Your balance is AED 48,250.75")
        # → returns "/tmp/kentiq_abc123.mp3"
    """
    engine = Config.TTS_ENGINE.lower()

    # Determine file extension
    ext = ".mp3" if engine in ("gtts", "azure") else ".wav"

    if filename is None:
        uid = uuid.uuid4().hex[:8]
        filename = os.path.join(tempfile.gettempdir(), f"kentiq_{uid}{ext}")

    print(f"[TTS] Engine={engine} | Text='{text[:60]}...' | Output={filename}")

    if engine == "gtts":
        return _speak_gtts(text, filename)
    elif engine == "pyttsx3":
        return _speak_pyttsx3(text, filename)
    elif engine == "azure":
        return _speak_azure(text, filename)
    else:
        raise ValueError(f"Unknown TTS engine: '{engine}'. Use gtts, pyttsx3, or azure.")


def speak_to_bytes(text: str) -> bytes:
    """
    Converts text to speech and returns raw audio bytes.
    Used by the FastAPI endpoint to stream audio directly.

    Returns:
        Audio bytes (MP3 or WAV depending on engine)
    """
    path = speak_to_file(text)
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)  # Clean up temp file
    return data


def speak(text: str):
    """
    Speaks text aloud on the local machine (plays audio).
    Used in the standalone Python mode (not FastAPI).
    Requires: playsound or pygame
    """
    path = speak_to_file(text)
    try:
        import playsound
        playsound.playsound(path)
    except ImportError:
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except ImportError:
            # Last resort: use system command
            if os.name == "nt":         # Windows
                os.system(f"start {path}")
            elif os.uname().sysname == "Darwin":  # macOS
                os.system(f"afplay {path}")
            else:                       # Linux
                os.system(f"mpg123 {path} 2>/dev/null || aplay {path} 2>/dev/null")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


def get_welcome_audio_bytes() -> bytes:
    """
    Returns the mandatory welcome message as audio bytes.
    Called on the very first user interaction.
    """
    return speak_to_bytes(Config.WELCOME_MESSAGE)


# ── Self-test
if __name__ == "__main__":
    print(f"[TTS TEST] Engine: {Config.TTS_ENGINE}")
    print("[TTS TEST] Generating welcome message...")
    path = speak_to_file(Config.WELCOME_MESSAGE, "test_welcome.mp3")
    print(f"[TTS TEST] Saved to: {path}")
    print("[TTS TEST] Playing...")
    speak(Config.WELCOME_MESSAGE)