import os
import logging
import time
import requests
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv
from telebot import TeleBot
from config import logger
from db import init_db
from handlers import register_handlers
import traceback

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_USER_ID = os.getenv("OWNER_USER_ID")

# --- Constants ---
MAX_HISTORY = 3  # Number of past messages to keep for context
RESPONSE_DELAY_SECONDS = 15  # 15-second delay
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"
DB_PATH = "chat_history.db"

# --- Setup ---
# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize the Telegram bot
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")
bot = TeleBot(TELEGRAM_TOKEN)

# Convert Owner ID to integer for comparison
owner_id_int = 0
if OWNER_USER_ID and OWNER_USER_ID.isdigit():
    owner_id_int = int(OWNER_USER_ID)
else:
    logger.warning(
        "OWNER_USER_ID is not set or invalid. "
        "Bot will respond to all users."
    )


# --- SQLite Chat History ---
def store_message(user_id, chat_id, sender, message_text, timestamp=None):
    try:
        if timestamp is None:
            # Use timezone-aware UTC datetime
            timestamp = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (user_id, chat_id, sender, message_text, "
            "timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, chat_id, sender, message_text, timestamp)
        )
        conn.commit()
        conn.close()
        logger.info(
            f"Stored message for user {user_id} in chat {chat_id} as {sender}."
        )
    except Exception as e:
        logger.error(f"Failed to store message: {e}", exc_info=True)


def get_last_n_messages(user_id, chat_id, n=MAX_HISTORY):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            SELECT sender, message_text FROM messages
            WHERE user_id = ? AND chat_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
            """,
            (user_id, chat_id, n * 2)  # Fetch more for alternating user/bot
        )
        rows = c.fetchall()
        conn.close()
        # Reverse to chronological order
        rows = rows[::-1]
        # Only keep the last n user/bot pairs
        context = []
        user_msgs = []
        bot_msgs = []
        for sender, msg in rows:
            if sender == 'user':
                user_msgs.append(msg)
            elif sender == 'bot':
                bot_msgs.append(msg)
        # Interleave user/bot pairs, but keep only the last n
        # Reconstruct pairs from the end
        i = len(user_msgs) - 1
        j = len(bot_msgs) - 1
        pairs = []
        while i >= 0 and j >= 0 and len(pairs) < n:
            pairs.append((user_msgs[i], bot_msgs[j]))
            i -= 1
            j -= 1
        pairs = pairs[::-1]
        for user_msg, bot_msg in pairs:
            context.append((user_msg, bot_msg))
        return context
    except Exception as e:
        logger.error(f"Failed to fetch chat history: {e}", exc_info=True)
        return []


def get_context_for_ollama(user_id, chat_id, user_message):
    context_pairs = get_last_n_messages(user_id, chat_id, MAX_HISTORY)
    context_parts = []
    for user_input, bot_response in context_pairs:
        context_parts.append(f"User: {user_input}")
        context_parts.append(f"Bot: {bot_response}")
    context_parts.append(f"User: {user_message}")
    return "\n".join(context_parts)


# --- AFK Status and Owner Reply Tracking ---
OWNER_AFK = [True]  # Use list for mutability in handlers
# Track last message time from owner per chat
last_owner_reply = {}

# Register all handlers
register_handlers(bot, last_owner_reply, owner_id_int, OWNER_AFK)


# --- Ollama Integration ---
def ollama_generate(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result.get(
            "response",
            "Sorry, I'm having trouble thinking right now."
        ).strip()
    except Exception as e:
        logger.error(f"Ollama API error: {e}", exc_info=True)
        return "Sorry, I'm having trouble thinking right now."


# --- Generate Response ---
def generate_response(user_id: int, chat_id: int, user_message: str) -> str:
    context = get_context_for_ollama(user_id, chat_id, user_message)
    logger.info(
        f"Sending context to Ollama for user {user_id}: '{context}'"
    )
    response = ollama_generate(context)
    logger.info(f"Ollama response for user {user_id}: '{response}'")
    return response


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Bot starting up...")
    if not owner_id_int:
        logger.warning(
            "OWNER_USER_ID is not set. The bot will respond to all users."
        )
    init_db()
    max_backoff = 300  # 5 minutes
    backoff = 5
    try:
        while True:
            try:
                logger.info("Starting the bot with infinity polling...")
                bot.infinity_polling(timeout=60, long_polling_timeout=60)
            except (requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError) as e:
                logger.error(
                    f"Network error during polling: {e}. "
                    f"Retrying in {backoff} seconds.",
                    exc_info=True
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
            except Exception as e:
                logger.critical(f"Unexpected error in polling: {e}", exc_info=True)
                traceback.print_exc()
                print("\n[CRITICAL] The bot failed to start or crashed. Check the logs above for details.\n")
                time.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
            else:
                backoff = 5
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt). Exiting gracefully.")
