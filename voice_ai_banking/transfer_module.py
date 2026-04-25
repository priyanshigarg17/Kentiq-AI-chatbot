# transfer_module.py
# Auto-generated file

# ============================================================
#  transfer_module.py — Money Transfer Workflow Module
#  (Milestone 3)
#
#  PURPOSE:
#    Manages the complete multi-step voice transfer workflow:
#      Step 1: Ask for beneficiary name
#      Step 2: Ask for bank name
#      Step 3: Ask for account number
#      Step 4: Ask for transfer amount
#      Step 5: Read summary, ask for voice confirmation
#      Step 6: Execute transfer, return success message
#
#    Uses a state machine pattern so the bot always knows
#    which step of the transfer it is currently on.
#
#  USAGE:
#    from transfer_module import TransferSession
#    session = TransferSession()
#    response = session.next_step(user_input)
# ============================================================

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
from pdf_reader import pdf_reader


# ── Transfer flow states
class TransferState(Enum):
    START             = auto()  # Initial state
    AWAITING_BENEFICIARY = auto()
    AWAITING_BANK        = auto()
    AWAITING_ACCOUNT     = auto()
    AWAITING_AMOUNT      = auto()
    AWAITING_CONFIRM     = auto()
    COMPLETED            = auto()
    CANCELLED            = auto()


@dataclass
class TransferData:
    """Holds all collected transfer details during the conversation."""
    beneficiary_name: str = ""
    bank_name: str = ""
    account_masked: str = ""
    amount: str = ""
    reference: str = ""
    timestamp: str = ""


@dataclass
class StepResponse:
    """Returned by TransferSession.next_step() for each turn."""
    speech: str         # What the bot should say
    text: str           # What to display
    state: str          # Current flow state name
    is_complete: bool = False
    is_cancelled: bool = False
    transfer_data: dict = field(default_factory=dict)


class TransferSession:
    """
    Manages one complete money transfer conversation session.
    Each user turn calls next_step() which advances the state machine.

    Usage:
        session = TransferSession()
        r1 = session.start()            # "Please say beneficiary name"
        r2 = session.next_step("Ravi Kumar")
        r3 = session.next_step("HDFC Bank")
        r4 = session.next_step("1234 5678")
        r5 = session.next_step("500")   # Shows summary
        r6 = session.next_step("yes")   # Executes transfer
    """

    def __init__(self):
        self.state = TransferState.START
        self.data  = TransferData()
        self._limits = pdf_reader.get_transfer_limits()

    def start(self) -> StepResponse:
        """Called when user says 'transfer money'. Begins the flow."""
        self.state = TransferState.AWAITING_BENEFICIARY
        speech = "Sure, I will help you transfer money. Please say the name of the beneficiary."
        return StepResponse(speech=speech, text=speech, state=self.state.name)

    def next_step(self, user_input: str) -> StepResponse:
        """
        Advances the transfer state machine by one step.

        Args:
            user_input: Transcribed text from the user for this turn

        Returns:
            StepResponse with what the bot should say next
        """
        user_input = user_input.strip()

        # ── Check for cancel at any step
        cancel_words = ["cancel", "stop", "abort", "no", "quit", "exit"]
        if any(w in user_input.lower() for w in cancel_words):
            return self._handle_cancel()

        # ── Route based on current state
        if self.state == TransferState.AWAITING_BENEFICIARY:
            return self._collect_beneficiary(user_input)

        elif self.state == TransferState.AWAITING_BANK:
            return self._collect_bank(user_input)

        elif self.state == TransferState.AWAITING_ACCOUNT:
            return self._collect_account(user_input)

        elif self.state == TransferState.AWAITING_AMOUNT:
            return self._collect_amount(user_input)

        elif self.state == TransferState.AWAITING_CONFIRM:
            return self._handle_confirmation(user_input)

        else:
            speech = "An unexpected error occurred. Please say 'transfer' to start again."
            return StepResponse(speech=speech, text=speech, state=self.state.name)

    # ── Private step handlers

    def _collect_beneficiary(self, name: str) -> StepResponse:
        self.data.beneficiary_name = name.title()
        self.state = TransferState.AWAITING_BANK
        speech = f"Got it. Beneficiary name is {self.data.beneficiary_name}. Which bank should I transfer to?"
        return StepResponse(speech=speech, text=speech, state=self.state.name)

    def _collect_bank(self, bank: str) -> StepResponse:
        self.data.bank_name = bank.title()
        self.state = TransferState.AWAITING_ACCOUNT
        speech = f"Bank noted as {self.data.bank_name}. Please say the beneficiary's account number."
        return StepResponse(speech=speech, text=speech, state=self.state.name)

    def _collect_account(self, account: str) -> StepResponse:
        # Mask the account for privacy
        digits = "".join(c for c in account if c.isdigit())
        masked = f"****{digits[-4:]}" if len(digits) >= 4 else account
        self.data.account_masked = masked
        self.state = TransferState.AWAITING_AMOUNT
        speech = f"Account ending {masked} noted. How much would you like to transfer in AED?"
        return StepResponse(speech=speech, text=speech, state=self.state.name)

    def _collect_amount(self, amount_text: str) -> StepResponse:
        # Extract numeric amount from spoken text
        amount = self._parse_amount(amount_text)
        if not amount:
            speech = "I could not understand the amount. Please say the amount clearly, for example: five hundred or 500."
            return StepResponse(speech=speech, text=speech, state=self.state.name)

        self.data.amount = amount
        self.state = TransferState.AWAITING_CONFIRM

        # Build confirmation summary
        summary = (
            f"Please confirm the transfer details. "
            f"Beneficiary: {self.data.beneficiary_name}. "
            f"Bank: {self.data.bank_name}. "
            f"Account: {self.data.account_masked}. "
            f"Amount: AED {self.data.amount}. "
            f"Say Yes to confirm or No to cancel."
        )
        return StepResponse(
            speech=summary,
            text=summary,
            state=self.state.name,
            transfer_data=self._to_dict(),
        )

    def _handle_confirmation(self, response: str) -> StepResponse:
        confirm_words = ["yes", "yep", "confirm", "proceed", "okay", "ok", "sure", "go ahead", "do it"]
        if any(w in response.lower() for w in confirm_words):
            return self._execute_transfer()
        else:
            return self._handle_cancel()

    def _execute_transfer(self) -> StepResponse:
        """Simulates the transfer and returns a success message."""
        self.data.reference = f"TXN{uuid.uuid4().hex[:8].upper()}"
        self.data.timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.state = TransferState.COMPLETED

        speech = (
            f"Transfer successful! "
            f"AED {self.data.amount} has been sent to {self.data.beneficiary_name} "
            f"at {self.data.bank_name}, account {self.data.account_masked}. "
            f"Transaction reference number is {self.data.reference}. "
            f"Transaction completed on {self.data.timestamp}. "
            f"Is there anything else I can help you with?"
        )
        return StepResponse(
            speech=speech,
            text=speech,
            state=self.state.name,
            is_complete=True,
            transfer_data=self._to_dict(),
        )

    def _handle_cancel(self) -> StepResponse:
        self.state = TransferState.CANCELLED
        speech = "Transfer has been cancelled. Is there anything else I can help you with?"
        return StepResponse(
            speech=speech, text=speech,
            state=self.state.name, is_cancelled=True
        )

    def _to_dict(self) -> dict:
        return {
            "beneficiary": self.data.beneficiary_name,
            "bank": self.data.bank_name,
            "account": self.data.account_masked,
            "amount": self.data.amount,
            "reference": self.data.reference,
            "timestamp": self.data.timestamp,
        }

    @staticmethod
    def _parse_amount(text: str) -> str:
        """
        Parses spoken amount to a numeric string.
        Handles both: "500", "five hundred", "1,500", "1500"
        """
        import re

        # Direct number with optional commas
        match = re.search(r"\b(\d[\d,]*\.?\d*)\b", text)
        if match:
            return match.group(1).replace(",", "")

        # Word-to-number mapping (common banking amounts)
        word_numbers = {
            "one hundred": "100",
            "two hundred": "200",
            "five hundred": "500",
            "one thousand": "1000",
            "two thousand": "2000",
            "five thousand": "5000",
            "ten thousand": "10000",
            "twenty thousand": "20000",
            "fifty thousand": "50000",
            "one lakh": "100000",
        }
        lower = text.lower()
        for phrase, value in word_numbers.items():
            if phrase in lower:
                return value
        return None

    def get_current_state(self) -> str:
        return self.state.name

    def is_active(self) -> bool:
        return self.state not in (TransferState.COMPLETED, TransferState.CANCELLED, TransferState.START)


# ── Self-test
if __name__ == "__main__":
    print("=== TRANSFER MODULE TEST ===\n")
    session = TransferSession()
    steps = [
        session.start(),
        session.next_step("Ravi Kumar"),
        session.next_step("HDFC Bank"),
        session.next_step("1234 5678 9012"),
        session.next_step("five hundred"),
        session.next_step("yes"),
    ]
    for i, step in enumerate(steps, 1):
        print(f"Step {i} [{step.state}]: {step.speech}")
        print()