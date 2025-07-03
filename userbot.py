from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from ai import generate_response
from db import get_last_n_messages, store_message, init_db, is_new_user
from config import MAX_HISTORY
import re
import requests
import logging

# Load environment variables from .env file
load_dotenv()
# Initialize the database and create tables if needed
init_db()
# Replace these with your own values from https://my.telegram.org
api_id = os.getenv("API_ID")         # <-- Enter your API ID here
api_hash = os.getenv("API_HASH")     # <-- Enter your API hash here

# This session file will be created on first run
tg_session = 'userbot_session'

client = TelegramClient(tg_session, api_id, api_hash)

TENOR_API_KEY = os.getenv("TENOR_API_KEY")

# Set up a logger if not already present
logger = logging.getLogger("userbot")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def fetch_gif_url(query):
    if not query or not TENOR_API_KEY:
        logger.warning("No GIF query provided or TENOR_API_KEY missing.")
        return None
    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={TENOR_API_KEY}&limit=1"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results")
        if not results:
            logger.info(f"No GIF results found for query: {query}")
            return None
        media_formats = results[0].get("media_formats")
        if not media_formats or "gif" not in media_formats:
            logger.error(f"No 'gif' format found in Tenor response for query: {query}")
            return None
        gif_url = media_formats["gif"].get("url")
        if not gif_url:
            logger.error(f"No GIF URL found in Tenor response for query: {query}")
            return None
        return gif_url
    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while fetching GIF for query: {query}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching GIF for query '{query}': {e}")
    except ValueError as e:
        logger.error(f"Invalid JSON response from Tenor for query '{query}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error in fetch_gif_url for query '{query}': {e}")
    return None

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Only reply to private messages (DMs) and not your own outgoing messages
    if event.is_private and not event.out:
        sender = await event.get_sender()
        name = sender.first_name or sender.username or "there"
        user_id = sender.id
        chat_id = event.chat_id
        user_message = event.text

        # Check if this is a new user
        new_user = is_new_user(user_id)

        # Store the incoming user message
        store_message(user_id, chat_id, user_message, "")

        # Retrieve last N message pairs for context
        context_pairs = get_last_n_messages(user_id, chat_id, MAX_HISTORY)
        context_parts = []
        for user_input, bot_response in context_pairs:
            context_parts.append(f"User: {user_input}")
            context_parts.append(f"Bot: {bot_response}")
        context_parts.append(f"User: {user_message}")
        context = "\n".join(context_parts)

        # Dynamic prompt for the AI
        if new_user:
            prompt = (
                f"Reply to {name} with greetings as Abel's AI assistant. If an emoji or GIF would enhance your reply (for humor, emotion, or emphasis), add [EMOJI: ...] or [GIF: ...] at the end. Otherwise, do not include these tags.\n"
                f"Context:\n{context}"
            )
        else:
            prompt = (
                f"Continue the conversation. If an emoji or GIF would enhance your reply, add [EMOJI: ...] or [GIF: ...] at the end. Otherwise, do not include these tags.\n"
                f"Context:\n{context}"
            )

        # Try Hugging Face first, then Ollama
        response = generate_response(user_id, chat_id, user_message=prompt)

        # Parse AI response for emoji and GIF
        def parse_ai_response(ai_response):
            emoji_match = re.search(r"\[EMOJI:\s*(.*?)\]", ai_response)
            gif_match = re.search(r"\[GIF:\s*(.*?)\]", ai_response)
            reply_text = re.split(r"\[EMOJI:|\[GIF:", ai_response)[0].strip()
            emoji = emoji_match.group(1).strip() if emoji_match else ""
            gif_topic = gif_match.group(1).strip() if gif_match else ""
            return reply_text, emoji, gif_topic

        reply_text, emoji, gif_topic = parse_ai_response(response)
        # Send the main reply with Markdown parsing
        try:
            await event.reply(reply_text, parse_mode='md')
        except Exception as e:
            logger.error(f"Error sending markdown reply: {e}")
            await event.reply(reply_text)  # Fallback to plain text if Markdown fails
        if emoji:
            try:
                await event.reply(emoji)
            except Exception as e:
                logger.error(f"Error sending emoji reply: {e}")
        if gif_topic:
            try:
                gif_url = fetch_gif_url(gif_topic)
                if gif_url:
                    await event.reply(file=gif_url)
                else:
                    logger.info(f"No GIF found for topic: {gif_topic}")
            except Exception as e:
                logger.error(f"Error sending GIF reply for topic '{gif_topic}': {e}")

        # Store the bot's response
        store_message(user_id, chat_id, user_message, reply_text)

if __name__ == "__main__":
    print("Starting userbot... If this is your first run, you'll be asked for your phone number and Telegram code.")
    client.start()
    print("Userbot is running. Press Ctrl+C to stop.")
    client.run_until_disconnected() 