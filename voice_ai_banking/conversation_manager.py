# ============================================================
#  conversation_manager.py — FINAL (STATIC INTENT VERSION)
# ============================================================

from dataclasses import dataclass, field
from config import Config

# ✅ STATIC INTENT DETECTOR (RELIABLE)
from intent_detector import IntentDetector

from balance_module import BalanceModule
from transfer_module import TransferSession
from cheque_module import ChequeValidator
from kyc_module import KYCModule
from error_handler import ErrorHandler


# ── Bot States
class BotState:
    IDLE = "idle"
    TRANSFER = "transfer"
    CHEQUE = "cheque"
    KYC = "kyc"


# ── Unified Response Object
@dataclass
class BotResponse:
    speech: str
    text: str
    state: str
    action: str = ""
    data: dict = field(default_factory=dict)
    is_welcome: bool = False


# ── Main Manager
class ConversationManager:

    def __init__(self):
        self.bot_state = BotState.IDLE
        self.transfer_session = None
        self.turn_count = 0
        self.greeted = False

    # ─────────────────────────────
    # WELCOME
    # ─────────────────────────────
    def get_welcome(self) -> BotResponse:
        self.greeted = True
        return BotResponse(
            speech=Config.WELCOME_MESSAGE,
            text=Config.WELCOME_MESSAGE,
            state=BotState.IDLE,
            is_welcome=True,
        )

    # ─────────────────────────────
    # MAIN ENTRY
    # ─────────────────────────────
    def process_input(self, user_text: str) -> BotResponse:
        self.turn_count += 1

        ErrorHandler.log_event(
            f"Turn {self.turn_count} | State={self.bot_state} | Input='{user_text}'"
        )

        if not user_text or not user_text.strip():
            err = ErrorHandler.handle("no_speech")
            return BotResponse(err.speech, err.text, self.bot_state)

        # ── ACTIVE FLOWS
        if self.bot_state == BotState.TRANSFER and self.transfer_session:
            return self._handle_transfer_turn(user_text)

        if self.bot_state == BotState.KYC:
            return self._handle_kyc_turn(user_text)

        if self.bot_state == BotState.CHEQUE:
            self.bot_state = BotState.IDLE
            speech = "Cheque upload cancelled. How can I help you?"
            return BotResponse(speech, speech, BotState.IDLE)

        # ── NORMAL FLOW
        return self._handle_idle_input(user_text)

    # ─────────────────────────────
    # STATIC INTENT HANDLER
    # ─────────────────────────────
    def _handle_idle_input(self, user_text: str) -> BotResponse:
        result = IntentDetector.detect(user_text)
        intent = result.intent

        ErrorHandler.log_event(f"STATIC Intent={intent} | Input='{user_text}'")

        if intent == "balance":
            return self._handle_balance()

        elif intent == "transfer":
            return self._handle_transfer_start()

        elif intent == "cheque":
            return self._handle_cheque_start()

        elif intent == "kyc":
            return self._handle_kyc_start()

        elif intent == "help":
            speech = ErrorHandler.get_help_speech()
            return BotResponse(speech, speech, BotState.IDLE, action="show_help")

        elif intent == "cancel":
            speech = "Action cancelled. How can I help you next?"
            return BotResponse(speech, speech, BotState.IDLE)

        else:
            err = ErrorHandler.handle("unknown")
            return BotResponse(err.speech, err.text, BotState.IDLE)

    # ─────────────────────────────
    # BALANCE
    # ─────────────────────────────
    def _handle_balance(self) -> BotResponse:
        response = BalanceModule.get_balance_response("primary")

        return BotResponse(
            speech=response.speech,
            text=response.text,
            state=BotState.IDLE,
            action="show_balance",
            data={
                "holder": response.account_holder,
                "masked": response.masked_account,
                "balance": response.balance,
                "type": response.account_type,
                "status": response.status,
            },
        )

    # ─────────────────────────────
    # TRANSFER
    # ─────────────────────────────
    def _handle_transfer_start(self) -> BotResponse:
        self.transfer_session = TransferSession()
        self.bot_state = BotState.TRANSFER

        step = self.transfer_session.start()

        return BotResponse(
            speech=step.speech,
            text=step.text,
            state=BotState.TRANSFER,
            action="show_transfer_wizard",
        )

    def _handle_transfer_turn(self, user_text: str) -> BotResponse:
        step = self.transfer_session.next_step(user_text)

        if step.is_complete:
            self.bot_state = BotState.IDLE
            self.transfer_session = None

            return BotResponse(
                speech=step.speech,
                text=step.text,
                state=BotState.IDLE,
                action="show_transfer_success",
                data=step.transfer_data,
            )

        if step.is_cancelled:
            self.bot_state = BotState.IDLE
            self.transfer_session = None
            return BotResponse(step.speech, step.text, BotState.IDLE)

        action = "show_transfer_confirm" if step.state == "AWAITING_CONFIRM" else "transfer_step"

        return BotResponse(
            speech=step.speech,
            text=step.text,
            state=BotState.TRANSFER,
            action=action,
            data=step.transfer_data,
        )

    # ─────────────────────────────
    # CHEQUE
    # ─────────────────────────────
    def _handle_cheque_start(self) -> BotResponse:
        self.bot_state = BotState.CHEQUE

        prompt = "Please upload a cheque image for validation."

        return BotResponse(
            speech=prompt,
            text=prompt,
            state=BotState.CHEQUE,
            action="show_upload",
        )

    def process_cheque_upload(self, file_path: str) -> BotResponse:
        result = ChequeValidator.validate(file_path)

        self.bot_state = BotState.IDLE

        return BotResponse(
            speech=result.speech,
            text=result.message,
            state=BotState.IDLE,
            action="cheque_result",
            data={
                "valid": result.is_valid,
                "checks_passed": result.checks_passed,
                "checks_failed": result.checks_failed,
                "saved_at": result.file_saved_at,
            },
        )

    # ─────────────────────────────
    # KYC
    # ─────────────────────────────
    def _handle_kyc_start(self) -> BotResponse:
        self.bot_state = BotState.KYC

        prompt = "Starting KYC. Please look at the camera and say your name."

        return BotResponse(
            speech=prompt,
            text=prompt,
            state=BotState.KYC,
            action="start_kyc_recording",
        )

    def _handle_kyc_turn(self, user_text: str) -> BotResponse:
        result = KYCModule.start_kyc_session(user_name="Ahmed")

        self.bot_state = BotState.IDLE

        return BotResponse(
            speech=result.speech,
            text=result.message,
            state=BotState.IDLE,
            action="kyc_result",
            data={
                "kyc_id": result.kyc_id,
                "status": result.status,
                "audio": result.audio_saved_at,
                "video": result.video_saved_at,
                "timestamp": result.timestamp,
            },
        )

    # ─────────────────────────────
    # UTILS
    # ─────────────────────────────
    def reset(self):
        self.bot_state = BotState.IDLE
        self.transfer_session = None
        self.turn_count = 0
        self.greeted = False

    def get_state(self) -> str:
        return self.bot_state