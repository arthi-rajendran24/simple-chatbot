import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
# Chat model must support tool calling (gemma4:e2b does; gemma3:4b does not).
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma4:e2b")
MAX_UPLOAD_MB = 15
