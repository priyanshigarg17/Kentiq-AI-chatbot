# balance_module.py
# Auto-generated file

# ============================================================
#  balance_module.py — Account Balance Inquiry Module
#  (Milestone 2)
#
#  PURPOSE:
#    Handles all account balance related voice queries.
#    Pulls balance data from the bank PDF via pdf_reader.py.
#    Returns both text response and triggers TTS audio.
#
#  USAGE:
#    from balance_module import BalanceModule
#    response = BalanceModule.get_balance_response()
# ============================================================

from dataclasses import dataclass
from pdf_reader import pdf_reader


@dataclass
class BalanceResponse:
    """Structured response for balance inquiries."""
    text: str           # Text to display in UI
    speech: str         # Text to speak (may differ slightly from display)
    account_holder: str
    masked_account: str
    balance: str
    account_type: str
    status: str


class BalanceModule:
    """
    Handles all logic for account balance inquiries.
    Data is pulled from the PDF using pdf_reader.
    """

    @staticmethod
    def get_balance_response(account_type: str = "primary") -> BalanceResponse:
        """
        Returns balance info for the specified account.

        Args:
            account_type: "primary" or "savings"

        Returns:
            BalanceResponse with text, speech, and account details
        """
        # Pull account info from PDF
        info = pdf_reader.get_account_info(account_type)

        holder  = info.get("holder", "Valued Customer")
        balance = info.get("balance", "AED 48,250.75")
        masked  = info.get("masked", "****3456")
        acc_type = info.get("type", "Current Account")
        status   = info.get("status", "Active")

        # Speech text (more natural, spoken style)
        speech = (
            f"Your {acc_type}, account ending {masked}, "
            f"has an available balance of {balance}. "
            f"Account is {status}. "
            f"Is there anything else I can help you with?"
        )

        # Display text (clean and structured)
        text = (
            f"Account Holder: {holder}\n"
            f"Account: {acc_type} ({masked})\n"
            f"Balance: {balance}\n"
            f"Status: {status}"
        )

        return BalanceResponse(
            text=text,
            speech=speech,
            account_holder=holder,
            masked_account=masked,
            balance=balance,
            account_type=acc_type,
            status=status,
        )

    @staticmethod
    def get_transactions_response() -> dict:
        """
        Returns recent transactions from the PDF for display.
        """
        transactions = pdf_reader.get_recent_transactions()
        speech = f"Here are your last {len(transactions)} transactions. "
        for t in transactions[:3]:   # Speak only first 3 for brevity
            speech += f"{t['description']}, {t['type']}, {t['amount']} AED on {t['date']}. "
        speech += "Would you like more details?"
        return {
            "speech": speech,
            "transactions": transactions,
        }

    @staticmethod
    def detect_balance_intent_keywords() -> list[str]:
        """
        Returns the list of keywords that trigger this module.
        Used for documentation and testing.
        """
        return [
            "balance", "how much", "account", "funds",
            "money", "available", "check balance", "my balance"
        ]


# ── Self-test
if __name__ == "__main__":
    print("=== BALANCE MODULE TEST ===\n")
    response = BalanceModule.get_balance_response("primary")
    print("Display Text:")
    print(response.text)
    print("\nSpeech Text:")
    print(response.speech)
    print("\nSavings Account:")
    savings = BalanceModule.get_balance_response("savings")
    print(savings.text)
    print("\nRecent Transactions:")
    txns = BalanceModule.get_transactions_response()
    print(txns["speech"])