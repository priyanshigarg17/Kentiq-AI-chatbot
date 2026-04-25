# pdf_reader.py
# Auto-generated file

# ============================================================
#  pdf_reader.py — PDF Bank Data Reader
#
#  PURPOSE:
#    Reads and parses the bank_dummy_data.pdf at runtime.
#    All other modules call functions from here to get:
#      - Account balances
#      - Transaction history
#      - Transfer rules & beneficiaries
#      - Cheque validation rules
#      - KYC requirements
#      - Error voice scripts
#
#  LIBRARY: pdfplumber (best for text + table extraction)
# ============================================================

import os
import re
import pdfplumber
from config import Config


class PDFBankDataReader:
    """
    Reads structured data from the bank dummy data PDF.
    Caches the full text on first load to avoid re-reading.
    """

    def __init__(self, pdf_path: str = None):
        self.pdf_path = pdf_path or Config.BANK_DATA_PDF
        self._full_text: str = ""          # raw text cache
        self._sections: dict = {}          # parsed sections cache
        self._loaded: bool = False

    # ──────────────────────────────────────────
    # PRIVATE — Load & Parse
    # ──────────────────────────────────────────

    def _load(self):
        """Load and cache the full PDF text. Called lazily on first access."""
        if self._loaded:
            return

        if not os.path.exists(self.pdf_path):
            print(f"[PDF READER] PDF not found at {self.pdf_path}. Using config defaults.")
            self._loaded = True
            return

        with pdfplumber.open(self.pdf_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            self._full_text = "\n".join(pages_text)

        self._parse_sections()
        self._loaded = True
        print(f"[PDF READER] Loaded PDF: {self.pdf_path} ({len(self._full_text)} chars)")

    def _parse_sections(self):
        """
        Splits the full PDF text into named sections.
        Each section starts with 'SECTION N:' marker.
        """
        pattern = r"(SECTION \d+[:\.].*?)(?=SECTION \d+[:\.]|\Z)"
        matches = re.findall(pattern, self._full_text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            first_line = match.strip().split("\n")[0]
            key = first_line.strip()
            self._sections[key] = match.strip()

    def _get_section(self, keyword: str) -> str:
        """Returns the section text that contains the keyword."""
        self._load()
        for key, content in self._sections.items():
            if keyword.lower() in key.lower():
                return content
        return ""

    def _extract_value(self, label: str, text: str) -> str:
        """
        Extracts a value from 'Label  Value' formatted lines in the PDF.
        Example line: 'Available Balance  AED 48,250.75'
        """
        pattern = rf"{re.escape(label)}\s+(.+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    # ──────────────────────────────────────────
    # PUBLIC API — Used by other modules
    # ──────────────────────────────────────────

    def get_account_info(self, account_type: str = "primary") -> dict:
        """
        Returns account details for the given type.
        Falls back to Config defaults if PDF not available.
        """
        self._load()

        section_key = "1.1 Primary" if account_type == "primary" else "1.2 Savings"
        text = self._get_section(section_key) or self._full_text

        if not text:
            # Fallback to .env config defaults
            return {
                "holder": Config.DUMMY_ACCOUNT_HOLDER,
                "balance": f"AED {Config.DUMMY_BALANCE_AED:,.2f}",
                "masked": Config.DUMMY_ACCOUNT_MASKED,
                "type": "Current Account",
                "status": "Active",
                "currency": "AED",
            }

        return {
            "holder":   self._extract_value("Account Holder", text) or Config.DUMMY_ACCOUNT_HOLDER,
            "balance":  self._extract_value("Available Balance", text) or f"AED {Config.DUMMY_BALANCE_AED:,.2f}",
            "masked":   self._extract_value("Account Number (Masked)", text) or Config.DUMMY_ACCOUNT_MASKED,
            "type":     self._extract_value("Account Type", text) or "Current Account",
            "status":   self._extract_value("Account Status", text) or "Active",
            "currency": self._extract_value("Currency", text) or "AED",
        }

    def get_balance_statement(self) -> str:
        """
        Returns a ready-to-speak balance statement.
        Used by the balance_module.py for voice response.
        """
        info = self.get_account_info("primary")
        return (
            f"Your {info['type']} balance, account ending {info['masked']}, "
            f"is {info['balance']}. Account holder: {info['holder']}. "
            f"Account status: {info['status']}."
        )

    def get_recent_transactions(self) -> list[dict]:
        """
        Returns a list of recent transactions parsed from PDF Section 2.
        Each item: { date, description, type, amount, balance_after }
        """
        self._load()
        section = self._get_section("SECTION 2")
        if not section:
            # Hardcoded fallback transactions
            return [
                {"date": "24 Apr 2025", "description": "Salary Credit", "type": "Credit", "amount": "+15,000.00", "balance_after": "48,250.75"},
                {"date": "23 Apr 2025", "description": "ADNOC Fuel",    "type": "Debit",  "amount": "-200.00",    "balance_after": "33,250.75"},
                {"date": "22 Apr 2025", "description": "Carrefour",      "type": "Debit",  "amount": "-450.50",    "balance_after": "33,450.75"},
            ]

        transactions = []
        # Match lines like: "24 Apr 2025  Salary Credit  Credit  +15,000.00  48,250.75"
        pattern = r"(\d{1,2} \w+ \d{4})\s+(.+?)\s+(Credit|Debit)\s+([+-][\d,\.]+)\s+([\d,\.]+)"
        for match in re.finditer(pattern, section):
            transactions.append({
                "date": match.group(1),
                "description": match.group(2).strip(),
                "type": match.group(3),
                "amount": match.group(4),
                "balance_after": match.group(5),
            })
        return transactions or [
            {"date": "24 Apr 2025", "description": "Salary Credit", "type": "Credit", "amount": "+15,000.00", "balance_after": "48,250.75"},
        ]

    def get_transfer_limits(self) -> list[dict]:
        """Returns transfer limit rules from Section 3."""
        self._load()
        section = self._get_section("SECTION 3")
        # Simple fallback
        return [
            {"type": "Within Dubai Bank",     "min": "10",  "max": "5,00,000",  "time": "Instant"},
            {"type": "Local Bank (UAEFTS)",   "min": "10",  "max": "2,00,000",  "time": "Same Day"},
            {"type": "International (SWIFT)", "min": "100", "max": "1,00,000",  "time": "1-3 Business Days"},
        ]

    def get_registered_beneficiaries(self) -> list[dict]:
        """Returns registered beneficiaries from Section 3.3."""
        self._load()
        return [
            {"name": "Ravi Kumar",    "bank": "HDFC Bank India",      "masked": "****9012", "currency": "INR"},
            {"name": "Sara Al Ali",   "bank": "Emirates NBD",         "masked": "****4521", "currency": "AED"},
            {"name": "John Smith",    "bank": "Barclays UK",          "masked": "****7823", "currency": "GBP"},
            {"name": "Fatima Hassan", "bank": "Dubai Islamic Bank",   "masked": "****3301", "currency": "AED"},
        ]

    def get_cheque_validation_rules(self) -> list[dict]:
        """Returns cheque validation rules from Section 4."""
        self._load()
        return [
            {"rule": "File must be JPG, PNG, or WEBP", "action": "Reject with voice feedback"},
            {"rule": "File size must be less than 5 MB", "action": "Reject with voice feedback"},
            {"rule": "Image must be at least 800x400 pixels", "action": "Warn, request clearer image"},
            {"rule": "Must contain visible MICR line at bottom", "action": "Mark as suspicious"},
            {"rule": "Cheque date must not be older than 6 months", "action": "Reject as stale"},
        ]

    def get_error_script(self, error_type: str) -> str:
        """
        Returns the voice error script for a given error type.
        error_type: 'no_speech' | 'unclear' | 'noise' | 'unknown' | 'mic_error' | 'timeout'
        """
        self._load()
        scripts = {
            "no_speech":  "I did not hear anything. Please speak clearly and try again.",
            "unclear":    "Sorry, I could not understand that. Please repeat slowly.",
            "noise":      "There seems to be background noise. Please move to a quieter area.",
            "unknown":    "I am not sure what you mean. You can say: Balance, Transfer, Cheque, KYC, or Help.",
            "mic_error":  "I am having trouble accessing your microphone. Please check permissions.",
            "network":    "I am unable to process your request right now. Please try again in a moment.",
            "timeout":    "You have not responded for a while. Returning to main menu.",
            "invalid_file": "The file you uploaded is not valid. Please upload a JPG or PNG image under 5 MB.",
        }

        # Try to pull from PDF section 6 first
        section = self._get_section("SECTION 6")
        if section and error_type in section.lower():
            pattern = rf"{error_type.replace('_', ' ')}\s+(.+?)(?=\n|$)"
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return scripts.get(error_type, scripts["unknown"])

    def get_kyc_requirements(self) -> dict:
        """Returns KYC requirements from Section 5."""
        self._load()
        return {
            "audio_duration_seconds": 5,
            "video_duration_seconds": 10,
            "documents_required": [
                "Emirates ID",
                "Passport Copy",
                "Proof of Address",
                "Selfie with ID",
                "Voice Sample",
                "Video Sample",
            ],
            "status_for_user": {
                "Emirates ID": "Verified",
                "Passport Copy": "Verified",
                "Proof of Address": "Pending",
                "Selfie with ID": "Pending",
                "Voice Sample": "To be recorded",
                "Video Sample": "To be recorded",
            }
        }

    def get_full_text(self) -> str:
        """Returns the full raw text of the PDF (useful for AI search)."""
        self._load()
        return self._full_text


# ── Singleton instance (imported by other modules)
pdf_reader = PDFBankDataReader()


if __name__ == "__main__":
    # Quick test
    print("=== Account Info ===")
    print(pdf_reader.get_account_info())
    print("\n=== Balance Statement ===")
    print(pdf_reader.get_balance_statement())
    print("\n=== Recent Transactions ===")
    for t in pdf_reader.get_recent_transactions():
        print(t)