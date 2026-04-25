import os

# Base project directory (change if needed)
base_dir = "voice_ai_banking"

# List of files to create
files = [
    "config.py",
    "generate_pdf_data.py",
    "pdf_reader.py",
    "intent_detector.py",
    "tts_module.py",
    "stt_module.py",
    "balance_module.py",
    "transfer_module.py",
    "cheque_module.py",
    "kyc_module.py",
    "error_handler.py",
    "conversation_manager.py",
    "main.py"
]

# Create base directory if not exists
os.makedirs(base_dir, exist_ok=True)

# Create each file
for file in files:
    file_path = os.path.join(base_dir, file)
    
    with open(file_path, "w") as f:
        f.write(f"# {file}\n")
        f.write("# Auto-generated file\n\n")
    
    print(f"Created: {file_path}")

print("\n✅ All files created successfully!")