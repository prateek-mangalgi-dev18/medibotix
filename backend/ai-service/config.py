import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as config.py, and from cwd as fallback
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_CHAT_MODEL = os.getenv("MISTRAL_CHAT_MODEL", "open-mistral-7b")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in .env")
