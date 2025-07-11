import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
OWNER_USER_ID: str = os.getenv("OWNER_USER_ID", "")
DB_PATH: str = "chat_history.db"
OLLAMA_URL: str = "http://localhost:11434/api/generate"
OLLAMA_MODEL: str = "llama3.1:8b"
MAX_HISTORY: int = 3
RESPONSE_DELAY_SECONDS: int = 1

# AI Provider Configurations
HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
PROVIDER_ORDER: list[str] = os.getenv(
    "PROVIDER_ORDER", "groq,huggingface,ollama").split(",")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
