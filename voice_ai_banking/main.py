# main.py
# Auto-generated file

# ============================================================
#  main.py — FastAPI Backend Server
#
#  PURPOSE:
#    REST API backend for the Kentiq AI Voice Banking Assistant.
#    Exposes endpoints for:
#      POST /api/welcome      → Get welcome message + audio
#      POST /api/chat         → Send text, get bot response
#      POST /api/transcribe   → Upload audio, get transcription
#      POST /api/speak        → Get TTS audio for any text
#      POST /api/cheque       → Upload cheque image for validation
#      POST /api/kyc          → Trigger KYC recording
#      GET  /api/balance      → Get account balance
#      GET  /api/transactions → Get recent transactions
#      GET  /api/health       → Health check
#
#  RUN:
#    uvicorn main:app --reload --host 0.0.0.0 --port 8000
#
#  DOCS:
#    http://localhost:8000/docs  (Swagger UI — auto-generated)
# ============================================================

import os
import uuid
import tempfile
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import Config
from conversation_manager import ConversationManager
from balance_module import BalanceModule
from tts_module import speak_to_bytes, speak_to_file, get_welcome_audio_bytes
from stt_module import transcribe_audio_bytes
from cheque_module import ChequeValidator
from kyc_module import KYCModule
from error_handler import ErrorHandler


# ──────────────────────────────────────────
# SESSION STORE (in-memory for demo)
# In production: use Redis or a database
# ──────────────────────────────────────────
sessions: dict[str, ConversationManager] = {}


def get_or_create_session(session_id: str) -> ConversationManager:
    """Gets existing session or creates a new one."""
    if session_id not in sessions:
        sessions[session_id] = ConversationManager()
    return sessions[session_id]


# ──────────────────────────────────────────
# APP SETUP
# ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # STARTUP
    print(f"\n{'='*60}")
    print(f"  {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"  Starting on http://{Config.APP_HOST}:{Config.APP_PORT}")
    print(f"  Docs: http://localhost:{Config.APP_PORT}/docs")
    print(f"  TTS Engine: {Config.TTS_ENGINE}")
    print(f"  STT Engine: {Config.STT_ENGINE}")
    print(f"  PDF: {Config.BANK_DATA_PDF}")
    print(f"{'='*60}\n")

    Config.validate()

    # Create required folders
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.KYC_RECORDINGS_DIR, exist_ok=True)

    yield

    # SHUTDOWN
    print("\n[SERVER] Shutting down Kentiq AI Voice Bot.")


app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="Voice AI Banking Assistant — Dubai Bank",
    lifespan=lifespan,
)

# Allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────
# REQUEST / RESPONSE MODELS (Pydantic)
# ──────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str
    return_audio: bool = False   # If True, also return TTS audio path


class ChatResponse(BaseModel):
    session_id: str
    speech: str
    text: str
    state: str
    action: str = ""
    data: dict = {}
    audio_url: Optional[str] = None


class TranscribeResponse(BaseModel):
    transcript: str
    session_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    tts_engine: str
    stt_engine: str
    pdf_loaded: bool


# ──────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────

# ── Health Check
@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check():
    """Returns server health and configuration status."""
    pdf_exists = os.path.exists(Config.BANK_DATA_PDF)
    return HealthResponse(
        status="ok",
        version=Config.APP_VERSION,
        tts_engine=Config.TTS_ENGINE,
        stt_engine=Config.STT_ENGINE,
        pdf_loaded=pdf_exists,
    )


# ── Welcome Message
@app.post(
    "/api/welcome",
    response_model=ChatResponse,
    summary="Get mandatory welcome message",
    tags=["Voice"],
)
async def get_welcome(session_id: str = Form(default=None)):
    """
    Returns the mandatory welcome message as text + audio.
    Must be called on the user's very first interaction.
    """
    sid = session_id or uuid.uuid4().hex
    manager = get_or_create_session(sid)
    response = manager.get_welcome()

    # Generate TTS audio and save temporarily
    audio_path = None
    try:
        audio_bytes = get_welcome_audio_bytes()
        audio_filename = f"welcome_{sid}.mp3"
        audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        audio_url = f"/api/audio/{audio_filename}"
    except Exception as e:
        ErrorHandler.log_event(f"TTS error in welcome: {e}", "error")
        audio_url = None

    return ChatResponse(
        session_id=sid,
        speech=response.speech,
        text=response.text,
        state=response.state,
        action="play_welcome",
        audio_url=audio_url,
    )


# ── Chat (Text Input → Bot Response)
from fastapi import Form

@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Send a text message to the bot",
    tags=["Voice"],
)
async def chat(
    session_id: str = Form(...),
    message: str = Form(...),
    return_audio: bool = Form(False)
):
    """
    Main chat endpoint. Accepts user text (transcribed or typed).
    """

    manager = get_or_create_session(session_id)
    bot_response = manager.process_input(message)

    audio_url = None
    if return_audio:
        try:
            audio_bytes = speak_to_bytes(bot_response.speech)
            audio_filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = os.path.join(tempfile.gettempdir(), audio_filename)

            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            audio_url = f"/api/audio/{audio_filename}"

        except Exception as e:
            ErrorHandler.log_event(f"TTS error in chat: {e}", "error")

    return ChatResponse(
        session_id=session_id,
        speech=bot_response.speech,
        text=bot_response.text,
        state=bot_response.state,
        action=bot_response.action,
        data=bot_response.data,
        audio_url=audio_url,
    )

# ── Speech-to-Text Transcription
@app.post(
    "/api/transcribe",
    response_model=TranscribeResponse,
    summary="Upload audio and get transcription",
    tags=["Voice"],
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (wav/mp3/ogg/webm)"),
    session_id: str = Form(default=None),
):
    sid = session_id or uuid.uuid4().hex

    # ✅ Validate file type
    allowed_audio = {"audio/wav", "audio/webm", "audio/ogg", "audio/mpeg"}
    if audio.content_type and audio.content_type not in allowed_audio:
        raise HTTPException(400, f"Unsupported audio type: {audio.content_type}")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio file received.")

    try:
        # ✅ FIX: use suffix instead of format
        ext = audio.filename.split(".")[-1] if audio.filename else "wav"
        suffix = f".{ext.lower()}"

        transcript = transcribe_audio_bytes(
            audio_bytes,
            suffix=suffix   # 🔥 THIS IS THE FIX
        )

    except Exception as e:
        ErrorHandler.log_event(f"Transcription failed: {e}", "error")
        raise HTTPException(500, f"Transcription failed: {e}")

    return TranscribeResponse(
        transcript=transcript,
        session_id=sid
    )


# ── Text-to-Speech — Return audio file
@app.post(
    "/api/speak",
    summary="Convert text to speech (returns audio)",
    tags=["Voice"],
)
async def text_to_speech(text: str = Form(...)):
    """
    Converts any text to speech and returns the audio file.
    Audio format depends on configured TTS engine (MP3 or WAV).
    """
    try:
        audio_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
        speak_to_file(text, audio_path)

        if not os.path.exists(audio_path):
            raise HTTPException(500, "TTS failed to generate audio.")

        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=audio_filename,
        )
    except Exception as e:
        raise HTTPException(500, f"TTS error: {e}")


# ── Serve audio files (generated by TTS)
@app.get(
    "/api/audio/{filename}",
    summary="Serve a generated audio file",
    tags=["System"],
)
async def serve_audio(filename: str):
    """Serves a previously generated TTS audio file."""
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Audio file not found or expired.")
    return FileResponse(path=path, media_type="audio/mpeg")


# ── Account Balance
@app.get(
    "/api/balance",
    summary="Get account balance from PDF",
    tags=["Banking"],
)
async def get_balance(account_type: str = "primary"):
    """
    Returns balance info pulled from bank data PDF.
    account_type: 'primary' or 'savings'
    """
    info = BalanceModule.get_balance_response(account_type)
    return {
        "account_holder": info.account_holder,
        "masked_account": info.masked_account,
        "balance": info.balance,
        "account_type": info.account_type,
        "status": info.status,
        "speech": info.speech,
        "display": info.text,
    }


# ── Recent Transactions
@app.get(
    "/api/transactions",
    summary="Get recent transactions from PDF",
    tags=["Banking"],
)
async def get_transactions():
    """Returns the list of recent transactions parsed from the bank data PDF."""
    result = BalanceModule.get_transactions_response()
    return {
        "speech": result["speech"],
        "transactions": result["transactions"],
        "count": len(result["transactions"]),
    }


# ── Cheque Validation
@app.post(
    "/api/cheque",
    summary="Upload and validate a cheque image",
    tags=["Banking"],
)
async def validate_cheque(
    session_id: str = Form(default=None),
    cheque_image: UploadFile = File(..., description="Cheque image (JPG/PNG)"),
):
    """
    Accepts a cheque image upload, validates it against PDF rules,
    and returns voice + text feedback.
    """
    sid = session_id or uuid.uuid4().hex

    # Save uploaded file temporarily
    ext = os.path.splitext(cheque_image.filename)[-1].lower() or ".jpg"
    tmp_path = os.path.join(tempfile.gettempdir(), f"cheque_{uuid.uuid4().hex}{ext}")
    try:
        content = await cheque_image.read()
        with open(tmp_path, "wb") as f:
            f.write(content)

        # Run validation
        manager = get_or_create_session(sid)
        bot_response = manager.process_cheque_upload(tmp_path)

        return {
            "session_id": sid,
            "valid": bot_response.data.get("valid", False),
            "speech": bot_response.speech,
            "message": bot_response.text,
            "checks_passed": bot_response.data.get("checks_passed", []),
            "checks_failed": bot_response.data.get("checks_failed", []),
            "saved_at": bot_response.data.get("saved_at", ""),
        }
    except Exception as e:
        raise HTTPException(500, f"Cheque validation error: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ── KYC
@app.post(
    "/api/kyc",
    summary="Start KYC recording session",
    tags=["Banking"],
)
async def start_kyc(
    session_id: str = Form(default=None),
    user_name: str = Form(default="Valued Customer"),
):
    """
    Triggers the KYC recording workflow.
    Records audio (and video if camera available) and saves locally.
    Returns KYC reference ID and voice confirmation.
    """
    sid = session_id or uuid.uuid4().hex
    try:
        result = KYCModule.start_kyc_session(user_name=user_name)
        return {
            "session_id": sid,
            "kyc_id": result.kyc_id,
            "status": result.status,
            "speech": result.speech,
            "message": result.message,
            "audio_saved_at": result.audio_saved_at,
            "video_saved_at": result.video_saved_at,
            "timestamp": result.timestamp,
        }
    except Exception as e:
        raise HTTPException(500, f"KYC error: {e}")


# ── List KYC Recordings
@app.get(
    "/api/kyc/recordings",
    summary="List all saved KYC recordings",
    tags=["Banking"],
)
async def list_kyc_recordings():
    """Returns list of all saved KYC audio/video files."""
    files = KYCModule.get_existing_kyc_files()
    return {"count": len(files), "files": files}


# ── Reset Session
@app.post(
    "/api/session/reset",
    summary="Reset a conversation session",
    tags=["System"],
)
async def reset_session(session_id: str = Form(...)):
    """Resets the conversation state for a given session."""
    if session_id in sessions:
        sessions[session_id].reset()
    return {"status": "reset", "session_id": session_id}


# ── Run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower(),
    )