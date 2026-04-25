# error_handler.py
# Auto-generated file

# ============================================================
#  error_handler.py — Voice Error Handling Module
#  (Milestone 6)
#
#  PURPOSE:
#    Handles all error scenarios in the voice bot:
#      - Unclear speech / no input detected
#      - Background noise
#      - Unknown/invalid commands
#      - Microphone access errors
#      - Network failures
#      - Timeout (user not responding)
#      - Invalid file uploads
#
#    Error scripts are pulled from the PDF (Section 6).
#    Falls back to hardcoded scripts if PDF unavailable.
#
#  USAGE:
#    from error_handler import ErrorHandler
#    response = ErrorHandler.handle("no_speech")
# ============================================================

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from config import Config
from pdf_reader import pdf_reader


# ── Set up module-level logger
os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True) if os.path.dirname(Config.LOG_FILE) else None

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        # Uncomment to log to file:
        # logging.FileHandler(Config.LOG_FILE),
    ]
)
logger = logging.getLogger("KentiqErrorHandler")


@dataclass
class ErrorResponse:
    """Returned by ErrorHandler.handle()"""
    error_type: str
    speech: str          # Voice response to play
    text: str            # Text to display
    should_retry: bool   # Should the bot prompt the user to try again?
    log_message: str     # What gets logged


class ErrorHandler:
    """
    Centralised error handling for the voice bot.
    All errors go through here so responses are consistent.
    """

    # ── Error scripts (fallback if PDF unavailable)
    FALLBACK_SCRIPTS: dict[str, str] = {
        "no_speech":    "I did not hear anything. Please speak clearly and try again.",
        "unclear":      "Sorry, I could not understand that. Please repeat slowly.",
        "noise":        "There seems to be background noise. Please move to a quieter area and try again.",
        "unknown":      "I am not sure what you mean. You can say: Balance, Transfer, Cheque, KYC, or Help.",
        "mic_error":    "I am having trouble accessing your microphone. Please check that microphone access is allowed.",
        "network":      "I am unable to process your request right now. Please check your connection and try again.",
        "timeout":      "You have not responded for a while. Returning to the main menu. How can I help you?",
        "invalid_file": "The file you uploaded is not valid. Please upload a JPG or PNG image under 5 megabytes.",
        "transfer_limit": "Transfer amount exceeds your daily limit. Please try a lower amount.",
        "generic":      "Something went wrong. Please try again or say Help for options.",
    }

    @classmethod
    def handle(cls, error_type: str, context: str = "") -> ErrorResponse:
        """
        Main method. Returns structured error response for a given error type.

        Args:
            error_type: One of the keys in FALLBACK_SCRIPTS
            context:    Optional extra info for logging

        Returns:
            ErrorResponse with speech text and retry flag

        Example:
            response = ErrorHandler.handle("no_speech")
            tts.speak(response.speech)
        """
        # Try to get script from PDF first
        speech = pdf_reader.get_error_script(error_type)

        # Fallback to hardcoded if PDF returned empty
        if not speech:
            speech = cls.FALLBACK_SCRIPTS.get(error_type, cls.FALLBACK_SCRIPTS["generic"])

        # Log the error
        log_msg = f"Error: {error_type}" + (f" | Context: {context}" if context else "")
        logger.warning(log_msg)

        # Determine if user should retry
        retry_errors = {"no_speech", "unclear", "noise", "timeout"}
        should_retry = error_type in retry_errors

        return ErrorResponse(
            error_type=error_type,
            speech=speech,
            text=speech,
            should_retry=should_retry,
            log_message=log_msg,
        )

    @classmethod
    def handle_stt_error(cls, exception: Exception) -> ErrorResponse:
        """
        Maps a Speech Recognition exception to an appropriate error response.

        Args:
            exception: The caught exception from the STT engine

        Returns:
            ErrorResponse
        """
        error_map = {
            "UnknownValueError": "unclear",
            "RequestError":      "network",
            "WaitTimeoutError":  "timeout",
            "OSError":           "mic_error",
        }

        exc_name = type(exception).__name__
        error_type = error_map.get(exc_name, "unclear")

        logger.error(f"STT Exception [{exc_name}]: {exception}")
        return cls.handle(error_type, context=str(exception))

    @classmethod
    def handle_file_error(cls, file_path: str, reason: str) -> ErrorResponse:
        """
        Handles file validation errors (cheque uploads, etc.).

        Args:
            file_path: Path of the file that failed
            reason:    Human-readable reason for failure
        """
        context = f"File: {os.path.basename(file_path)} — {reason}"
        logger.warning(f"File error: {context}")
        return cls.handle("invalid_file", context=context)

    @classmethod
    def handle_unknown_intent(cls, transcript: str) -> ErrorResponse:
        """
        Called when user speech is understood but no intent matches.

        Args:
            transcript: What the user said
        """
        context = f"Unmatched transcript: '{transcript}'"
        logger.info(context)
        return cls.handle("unknown", context=context)

    @staticmethod
    def log_event(message: str, level: str = "info"):
        """
        Generic event logger for the voice bot.

        Args:
            message: What happened
            level:   "info" | "warning" | "error" | "debug"
        """
        log_fn = getattr(logger, level.lower(), logger.info)
        log_fn(message)

    @staticmethod
    def get_help_speech() -> str:
        """Returns the help/menu voice script."""
        return (
            "Here is what I can help you with. "
            "Say Balance to check your account balance. "
            "Say Transfer to send money to someone. "
            "Say Cheque to upload and verify a cheque. "
            "Say KYC to start identity verification. "
            "Say Cancel at any time to stop the current action."
        )

    @staticmethod
    def get_retry_prompt() -> str:
        """Short retry prompt after an error."""
        return "Please try again. What would you like to do?"


# ── Self-test
if __name__ == "__main__":
    print("=== ERROR HANDLER TEST ===\n")
    errors = ["no_speech", "unclear", "noise", "unknown", "mic_error", "timeout", "invalid_file"]
    for err in errors:
        result = ErrorHandler.handle(err)
        print(f"[{err}] retry={result.should_retry}")
        print(f"  Speech: {result.speech}\n")

    print("Help Script:")
    print(ErrorHandler.get_help_speech())