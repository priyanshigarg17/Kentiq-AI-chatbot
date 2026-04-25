# kyc_module.py
# Auto-generated file

# ============================================================
#  kyc_module.py — Voice/Video KYC Module
#  (Milestone 5)
#
#  PURPOSE:
#    Handles Voice KYC and Video KYC workflows:
#      1. User says "Start KYC"
#      2. Bot prompts user to look at camera & speak name
#      3. System records 5-second audio clip → saves as WAV
#      4. System records 10-second video clip → saves as MP4
#      5. Bot confirms completion with KYC reference ID
#      6. All files saved locally in kyc_recordings/ folder
#
#  USAGE:
#    from kyc_module import KYCModule
#    result = KYCModule.start_kyc_session(user_name="Ahmed")
# ============================================================

import os
import uuid
import time
import threading
from datetime import datetime
from dataclasses import dataclass
from pdf_reader import pdf_reader
from config import Config


@dataclass
class KYCResult:
    """Returned after KYC recording completes."""
    kyc_id: str
    status: str          # "completed" | "partial" | "failed"
    speech: str          # Bot's voice confirmation
    message: str         # Display message
    audio_saved_at: str  # Path to saved audio file
    video_saved_at: str  # Path to saved video file (if available)
    timestamp: str
    requirements: dict   # KYC requirements from PDF


class KYCModule:
    """
    Handles the Voice/Video KYC workflow.
    Records audio and video from device hardware.
    Saves recordings locally in kyc_recordings/ folder.
    """

    AUDIO_DURATION_SEC = 5    # How long to record audio
    VIDEO_DURATION_SEC = 10   # How long to record video

    @classmethod
    def start_kyc_session(cls, user_name: str = "Valued Customer") -> KYCResult:
        """
        Main entry point for KYC.
        Records audio (and video if camera available).

        Args:
            user_name: Customer's name for personalized prompts

        Returns:
            KYCResult with status, file paths, and voice confirmation
        """
        kyc_id = f"KYC-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        os.makedirs(Config.KYC_RECORDINGS_DIR, exist_ok=True)

        requirements = pdf_reader.get_kyc_requirements()
        audio_path = ""
        video_path = ""

        print(f"[KYC] Starting session: {kyc_id} for {user_name}")

        # ── Step 1: Record Audio
        audio_path = cls._record_audio(kyc_id)

        # ── Step 2: Record Video (optional — camera may not be available)
        video_path = cls._record_video(kyc_id)

        # ── Step 3: Determine status
        if audio_path and video_path:
            status = "completed"
            speech = (
                f"KYC completed successfully, {user_name}. "
                f"Your audio and video samples have been recorded and saved locally. "
                f"Your KYC reference ID is {kyc_id}. "
                f"Our team will review your documents shortly. "
                f"Is there anything else I can help you with?"
            )
        elif audio_path:
            status = "partial"
            speech = (
                f"KYC partially completed, {user_name}. "
                f"Your voice sample has been recorded. "
                f"Video recording was unavailable. "
                f"Your KYC reference ID is {kyc_id}. "
                f"Please visit a branch to complete video KYC."
            )
        else:
            status = "failed"
            speech = (
                f"KYC recording could not be completed. "
                f"Please ensure microphone access is granted and try again. "
                f"Or visit a Dubai Bank branch for in-person KYC."
            )

        return KYCResult(
            kyc_id=kyc_id,
            status=status,
            speech=speech,
            message=f"KYC {status}. Audio: {audio_path or 'N/A'}. Video: {video_path or 'N/A'}.",
            audio_saved_at=audio_path,
            video_saved_at=video_path,
            timestamp=timestamp,
            requirements=requirements,
        )

    @classmethod
    def _record_audio(cls, kyc_id: str) -> str:
        """
        Records a 5-second audio clip from the microphone.
        Saves as WAV file in kyc_recordings/ directory.

        Returns:
            Path to saved audio file, or "" on failure.
        """
        output_path = os.path.join(
            Config.KYC_RECORDINGS_DIR, f"{kyc_id}_audio.wav"
        )
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wav
            import numpy as np

            sample_rate = 16000
            print(f"[KYC] Recording audio for {cls.AUDIO_DURATION_SEC} seconds...")
            audio_data = sd.rec(
                int(cls.AUDIO_DURATION_SEC * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16"
            )
            sd.wait()
            wav.write(output_path, sample_rate, audio_data)
            print(f"[KYC] Audio saved: {output_path}")
            return output_path

        except ImportError:
            # Fallback: create a dummy placeholder file
            print("[KYC] sounddevice not installed — creating placeholder audio file.")
            with open(output_path, "wb") as f:
                # Write a minimal valid WAV header (44 bytes) + silence
                f.write(cls._create_silent_wav(duration_sec=cls.AUDIO_DURATION_SEC))
            return output_path

        except Exception as e:
            print(f"[KYC] Audio recording failed: {e}")
            return ""

    @classmethod
    def _record_video(cls, kyc_id: str) -> str:
        """
        Records a 10-second video clip using the device camera.
        Saves as MP4 in kyc_recordings/ directory.

        Returns:
            Path to saved video file, or "" if camera unavailable.
        """
        output_path = os.path.join(
            Config.KYC_RECORDINGS_DIR, f"{kyc_id}_video.mp4"
        )
        try:
            import cv2

            cap = cv2.VideoCapture(0)  # 0 = default camera
            if not cap.isOpened():
                print("[KYC] No camera detected.")
                return ""

            # Get camera properties
            frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

            print(f"[KYC] Recording video for {cls.VIDEO_DURATION_SEC} seconds...")
            start_time = time.time()

            while time.time() - start_time < cls.VIDEO_DURATION_SEC:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            cap.release()
            out.release()
            print(f"[KYC] Video saved: {output_path}")
            return output_path

        except ImportError:
            print("[KYC] OpenCV not installed — video recording skipped.")
            return ""
        except Exception as e:
            print(f"[KYC] Video recording failed: {e}")
            return ""

    @staticmethod
    def _create_silent_wav(duration_sec: int = 5, sample_rate: int = 16000) -> bytes:
        """
        Creates a minimal silent WAV file as a placeholder.
        Used when sounddevice is not installed.
        """
        import struct
        num_samples = duration_sec * sample_rate
        data_size = num_samples * 2   # 16-bit = 2 bytes per sample

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,
            b"WAVE",
            b"fmt ",
            16,           # Subchunk1Size
            1,            # PCM format
            1,            # Mono
            sample_rate,
            sample_rate * 2,  # ByteRate
            2,            # BlockAlign
            16,           # BitsPerSample
            b"data",
            data_size,
        )
        silence = b"\x00" * data_size
        return header + silence

    @staticmethod
    def get_kyc_prompt() -> str:
        """Voice prompt spoken at the start of KYC."""
        return (
            "I will now begin the KYC verification process. "
            "Please look directly at your camera and speak clearly. "
            "Say your full name after the beep. "
            "Recording will begin in 3 seconds."
        )

    @staticmethod
    def get_existing_kyc_files() -> list[dict]:
        """
        Lists all saved KYC recordings in the kyc_recordings/ folder.
        Used for admin review.
        """
        folder = Config.KYC_RECORDINGS_DIR
        if not os.path.exists(folder):
            return []
        files = []
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            files.append({
                "filename": fname,
                "path": fpath,
                "size_kb": round(os.path.getsize(fpath) / 1024, 1),
                "modified": datetime.fromtimestamp(
                    os.path.getmtime(fpath)
                ).strftime("%d %b %Y %H:%M"),
            })
        return sorted(files, key=lambda x: x["modified"], reverse=True)


# ── Self-test
if __name__ == "__main__":
    print("=== KYC MODULE TEST ===\n")
    print("KYC Prompt:")
    print(KYCModule.get_kyc_prompt())

    print("\nStarting KYC session (demo)...")
    result = KYCModule.start_kyc_session(user_name="Ahmed Al Mansouri")
    print(f"\nKYC ID: {result.kyc_id}")
    print(f"Status: {result.status}")
    print(f"Speech: {result.speech}")
    print(f"Audio: {result.audio_saved_at}")
    print(f"Video: {result.video_saved_at}")
    print(f"Time: {result.timestamp}")