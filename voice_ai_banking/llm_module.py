import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def detect_intent_llm(user_input: str) -> str:
    prompt = f"""
    Classify the user intent into ONE word:

    balance
    transfer
    cheque
    kyc
    help
    cancel

    Input: {user_input}

    Only return the word.
    """
    print("INPUT TO LLM:", user_input)
    try:
        response = model.generate_content(prompt)
        intent_raw = response.text.strip().lower()

        print("RAW LLM:", intent_raw)  # 🔥 DEBUG

        # ✅ robust matching
        if "balance" in intent_raw:
            return "balance"
        elif "transfer" in intent_raw:
            return "transfer"
        elif "cheque" in intent_raw:
            return "cheque"
        elif "kyc" in intent_raw:
            return "kyc"
        elif "help" in intent_raw:
            return "help"
        elif "cancel" in intent_raw:
            return "cancel"
        else:
            return "unknown"

    except Exception as e:
        print("LLM ERROR:", e)
        return "unknown"