# intent_detector.py
# Auto-generated file

# ============================================================
#  intent_detector.py — Voice Intent Detection Module
#
#  PURPOSE:
#    Converts transcribed text into a structured intent.
#    Uses regex pattern matching (NLP-lite approach).
#    No external NLP library needed — works offline.
#
#  USAGE:
#    from intent_detector import IntentDetector
#    intent, extras = IntentDetector.detect("I want to transfer money")
# ============================================================

import re
from dataclasses import dataclass, field
from typing import Optional


# ── All possible intents the bot understands
class Intent:
    BALANCE  = "balance"
    TRANSFER = "transfer"
    CHEQUE   = "cheque"
    KYC      = "kyc"
    CONFIRM  = "confirm"
    CANCEL   = "cancel"
    HELP     = "help"
    UNKNOWN  = "unknown"


@dataclass
class DetectionResult:
    """Returned by IntentDetector.detect()"""
    intent: str
    confidence: float          # 0.0 to 1.0
    extracted_amount: Optional[str] = None      # e.g. "500" from "transfer 500"
    extracted_name: Optional[str] = None        # e.g. "Ravi" from "send to Ravi"
    raw_text: str = ""
    matched_pattern: str = ""


class IntentDetector:
    """
    Detects user intent from transcribed speech text.
    Each intent has a list of regex patterns. First match wins.
    Patterns are ordered from most specific to least specific.
    """

    # ── Pattern registry: intent → list of regex patterns
    PATTERNS: dict[str, list[str]] = {
        Intent.BALANCE: [
            r"\bcheck\s+(?:my\s+)?(?:account\s+)?balance\b",
            r"\bhow\s+much\s+(?:money|funds|do\s+i\s+have)\b",
            r"\b(?:account|bank|my)\s+balance\b",
            r"\bbalance\s+(?:inquiry|check|info)\b",
            r"\bfunds\s+available\b",
            r"\bwhat(?:'s|\s+is)\s+(?:my\s+)?balance\b",
        ],
        Intent.TRANSFER: [
            r"\b(?:transfer|send|wire|remit|pay)\s+(?:money|funds|cash|amount)?\b",
            r"\bsend\s+(?:to|money\s+to)\b",
            r"\bi\s+want\s+to\s+(?:transfer|send|pay)\b",
            r"\b(?:make\s+a\s+)?(?:bank\s+)?transfer\b",
            r"\btransfer\b",
        ],
        Intent.CHEQUE: [
            r"\b(?:upload|scan|verify|submit|check)\s+(?:a\s+)?chequ?e\b",
            r"\bchequ?e\s+(?:verification|upload|scan)\b",
            r"\bchequ?e\b",
        ],
        Intent.KYC: [
            r"\bstart\s+kyc\b",
            r"\bbegin\s+(?:kyc|verification)\b",
            r"\bkyc\s+(?:verification|process|check)?\b",
            r"\bidentity\s+(?:verification|check)\b",
            r"\bknow\s+your\s+customer\b",
        ],
        Intent.CONFIRM: [
            r"\b(?:yes|yep|yup|yeah|sure|okay|ok|correct|right|proceed|confirm|go\s+ahead|do\s+it)\b",
        ],
        Intent.CANCEL: [
            r"\b(?:no|nope|nah|cancel|stop|abort|quit|exit|back|end|never\s+mind)\b",
        ],
        Intent.HELP: [
            r"\b(?:help|assist|support)\b",
            r"\bwhat\s+can\s+you\s+do\b",
            r"\b(?:show\s+)?(?:options|menu|services|features)\b",
            r"\bhow\s+(?:do\s+i|can\s+i)\b",
        ],
    }

    # ── Confidence weights per intent (higher = more reliable patterns)
    CONFIDENCE: dict[str, float] = {
        Intent.BALANCE:  0.95,
        Intent.TRANSFER: 0.90,
        Intent.CHEQUE:   0.95,
        Intent.KYC:      0.95,
        Intent.CONFIRM:  0.85,
        Intent.CANCEL:   0.85,
        Intent.HELP:     0.90,
        Intent.UNKNOWN:  0.10,
    }

    @classmethod
    def detect(cls, text: str) -> DetectionResult:
        """
        Main method. Detects intent from text string.

        Args:
            text: Transcribed speech or typed user input

        Returns:
            DetectionResult with intent, confidence, and extracted info
        """
        if not text or not text.strip():
            return DetectionResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
                raw_text=text or "",
            )

        clean = text.lower().strip()

        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, clean):
                    return DetectionResult(
                        intent=intent,
                        confidence=cls.CONFIDENCE[intent],
                        extracted_amount=cls._extract_amount(clean),
                        extracted_name=cls._extract_name(text),
                        raw_text=text,
                        matched_pattern=pattern,
                    )

        return DetectionResult(
            intent=Intent.UNKNOWN,
            confidence=0.1,
            raw_text=text,
        )

    @staticmethod
    def _extract_amount(text: str) -> Optional[str]:
        """
        Extracts a numeric or word-number amount from text.
        Examples:
          "transfer 500 AED"   → "500"
          "send five hundred"  → "500"
          "pay 1,500"          → "1500"
        """
        # Direct numeric (with optional comma and decimal)
        numeric = re.search(r"\b(\d[\d,]*\.?\d*)\b", text)
        if numeric:
            return numeric.group(1).replace(",", "")

        # Written numbers (common banking amounts)
        word_map = {
            "hundred": "100",   "five hundred": "500",
            "thousand": "1000", "one thousand": "1000",
            "two thousand": "2000", "five thousand": "5000",
            "ten thousand": "10000",
        }
        for phrase, value in word_map.items():
            if phrase in text.lower():
                return value

        return None

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """
        Attempts to extract a person's name from the text.
        Simple heuristic: capitalized word(s) after 'to', 'for', 'named'.
        """
        # "transfer to Ravi Kumar"
        match = re.search(r"\b(?:to|for|named|beneficiary)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
        if match:
            return match.group(1)
        return None

    @classmethod
    def get_all_intents(cls) -> list[str]:
        """Returns list of all supported intent names."""
        return [
            Intent.BALANCE, Intent.TRANSFER, Intent.CHEQUE,
            Intent.KYC, Intent.CONFIRM, Intent.CANCEL, Intent.HELP, Intent.UNKNOWN
        ]


# ── Run quick self-test when executed directly
if __name__ == "__main__":
    tests = [
        ("check my account balance", Intent.BALANCE),
        ("I want to transfer money",  Intent.TRANSFER),
        ("upload cheque please",       Intent.CHEQUE),
        ("start KYC",                  Intent.KYC),
        ("yes, confirm",               Intent.CONFIRM),
        ("no, cancel",                 Intent.CANCEL),
        ("help me",                    Intent.HELP),
        ("blah blah",                  Intent.UNKNOWN),
        ("send 500 AED to Ravi Kumar", Intent.TRANSFER),
    ]

    print("=" * 60)
    print("INTENT DETECTOR SELF-TEST")
    print("=" * 60)
    for text, expected in tests:
        result = IntentDetector.detect(text)
        status = "✅ PASS" if result.intent == expected else "❌ FAIL"
        print(f"{status} | '{text}'")
        print(f"       → intent={result.intent}, confidence={result.confidence}")
        if result.extracted_amount:
            print(f"       → amount={result.extracted_amount}")
        if result.extracted_name:
            print(f"       → name={result.extracted_name}")