# ============================================================
#  config.py — FINAL CLEAN CONFIG (FREE STACK)
# ============================================================

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()


class Config:
    """
    Central configuration class (clean version)
    Only includes what your project ACTUALLY uses
    """

    # ── App
    APP_NAME: str    = os.getenv("APP_NAME", "Kentiq AI Voice Banking Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_PORT: int    = int(os.getenv("APP_PORT", 8000))
    APP_HOST: str    = os.getenv("APP_HOST", "0.0.0.0")
    DEBUG: bool      = os.getenv("DEBUG", "True").lower() == "true"

    # ── Gemini (LLM)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ── PDF
    BANK_DATA_PDF: str = os.getenv("BANK_DATA_PDF", "data/bank_dummy_data.pdf")

    # ── File Storage
    UPLOAD_DIR: str         = os.getenv("UPLOAD_DIR", "uploads")
    KYC_RECORDINGS_DIR: str = os.getenv("KYC_RECORDINGS_DIR", "kyc_recordings")
    MAX_FILE_SIZE_MB: int   = int(os.getenv("MAX_FILE_SIZE_MB", 5))
    ALLOWED_IMAGE_TYPES     = os.getenv(
        "ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/webp"
    ).split(",")

    # ── Dummy Fallback (used if PDF missing)
    DUMMY_ACCOUNT_HOLDER: str = os.getenv("DUMMY_ACCOUNT_HOLDER", "Ahmed Al Mansouri")
    DUMMY_BALANCE_AED: float  = float(os.getenv("DUMMY_BALANCE_AED", 48250.75))
    DUMMY_ACCOUNT_MASKED: str = os.getenv("DUMMY_ACCOUNT_MASKED", "****3456")

    # ── Engines (FREE ONLY)
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "gtts")       # gtts | pyttsx3
    STT_ENGINE: str = os.getenv("STT_ENGINE", "whisper")    # whisper only

    # ── Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str  = os.getenv("LOG_FILE", "logs/kentiq.log")

    # ── Mandatory Welcome Message (SOW requirement)
    WELCOME_MESSAGE: str = (
        "Welcome to Kentiq AI Voice Bot from Dubai Bank Bank. How can I help you?"
    )

    # ─────────────────────────────
    # VALIDATION
    # ─────────────────────────────
    @classmethod
    def validate(cls):
        """
        Validates required configs at startup
        """
        warnings = []

        if not cls.GEMINI_API_KEY:
            warnings.append("GEMINI_API_KEY not set — LLM intent detection will fail.")

        if cls.TTS_ENGINE not in ["gtts", "pyttsx3"]:
            warnings.append(f"Invalid TTS_ENGINE: {cls.TTS_ENGINE}")

        if cls.STT_ENGINE != "whisper":
            warnings.append("Only 'whisper' STT is supported in this setup.")

        if not os.path.exists(cls.BANK_DATA_PDF):
            warnings.append(f"PDF not found at {cls.BANK_DATA_PDF} — using dummy data.")

        for w in warnings:
            print(f"[CONFIG WARNING] {w}")

        return len(warnings) == 0