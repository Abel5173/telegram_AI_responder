import os
import logging
import time
from collections import defaultdict
from typing import Dict, List

import telebot
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
OWNER_USER_ID = os.getenv("OWNER_USER_ID")

# --- Constants ---
MODEL_ID = "facebook/blenderbot-400M-distill"
MAX_HISTORY = 3  # Number of past messages to keep for context
RESPONSE_DELAY_SECONDS = 15

# --- Setup ---
# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the Telegram bot
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Convert Owner ID to integer for comparison
owner_id_int = 0
if OWNER_USER_ID and OWNER_USER_ID.isdigit():
    owner_id_int = int(OWNER_USER_ID)
else:
    logger.warning("OWNER_USER_ID is not set or invalid. Bot will respond to all users.")

# Initialize the Hugging Face Inference Client
if not HF_API_KEY:
    raise ValueError("HF_API_KEY environment variable not set!")
hf_client = InferenceClient(token=HF_API_KEY)

# In-memory chat history storage
# defaultdict allows us to create a new list for a user if they don't exist yet
chat_history: Dict[int, Dict[str, List[str]]] = defaultdict(
    lambda: {"past_user_inputs": [], "generated_responses": []}
)


# --- Helper Functions ---
def is_owner_online() -> bool:
    """
    Placeholder function to check if the bot owner is online.
    For this example, we assume the owner is always offline.
    In a real-world scenario, you might check Telegram's presence,
    a status from another API, or a flag in a database.
    """
    return False


def generate_response(user_id: int, user_message: str) -> str:
    """
    Generates a response using the Hugging Face Inference API.
    """
    # Retrieve conversation history for the user
    history = chat_history.get(user_id)
    if not history:
        past_user_inputs = []
        generated_responses = []
    else:
        past_user_inputs = history["past_user_inputs"]
        generated_responses = history["generated_responses"]

    try:
        # Use the conversational task
        response_text = hf_client.conversational(
            user_message,
            past_user_inputs=past_user_inputs,
            generated_responses=generated_responses,
            model=MODEL_ID,
        )
        return response_text['generated_text']

    except Exception as e:
        logger.error(f"Hugging Face API error: {e}")
        return "I'm sorry, I'm having a little trouble thinking right now. Please try again later."


def update_chat_history(user_id: int, user_message: str, bot_response: str):
    """
    Updates the chat history for a given user, keeping it within the MAX_HISTORY limit.
    """
    history = chat_history[user_id]
    history["past_user_inputs"].append(user_message)
    history["generated_responses"].append(bot_response)

    # Trim history to the maximum length
    history["past_user_inputs"] = history["past_user_inputs"][-MAX_HISTORY:]
    history["generated_responses"] = history["generated_responses"][-MAX_HISTORY:]


# --- Telegram Bot Handlers ---
@bot.message_handler(chat_types=['private'], func=lambda message: True)
def handle_message(message: telebot.types.Message):
    """
    Main handler for all incoming private text messages.
    """
    user_id = message.from_user.id
    user_message = message.text

    # Log the incoming message
    logger.info(f"Received message from user {user_id}: '{user_message}'")
    
    # Do not respond to the owner of the bot
    if user_id == owner_id_int:
        logger.info("Message is from the owner. Ignoring.")
        return

    # Check if the owner is offline
    if is_owner_online():
        logger.info(f"Owner is online. Bot will not respond to user {user_id}.")
        return

    # Don't respond to own messages if the bot is in a group
    if user_id == bot.get_me().id:
        return

    # Add a delay to simulate typing or thinking
    logger.info(f"Waiting for {RESPONSE_DELAY_SECONDS} seconds before responding.")
    time.sleep(RESPONSE_DELAY_SECONDS)

    # Generate a response
    bot.send_chat_action(message.chat.id, 'typing')
    response_text = generate_response(user_id, user_message)

    # Send the response
    bot.reply_to(message, response_text)
    logger.info(f"Sent response to user {user_id}: '{response_text}'")
    
    # Update chat history after sending the response
    update_chat_history(user_id, user_message, response_text)


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Bot starting up...")
    if not owner_id_int:
        logger.warning("OWNER_USER_ID is not set. The bot will respond to all users.")
    
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logger.critical(f"Bot crashed with error: {e}") 