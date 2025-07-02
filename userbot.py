from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from ai import huggingface_generate, ollama_generate
from db import get_last_n_messages, store_message
from config import MAX_HISTORY

# Load environment variables from .env file
load_dotenv()
# Replace these with your own values from https://my.telegram.org
api_id = os.getenv("API_ID")         # <-- Enter your API ID here
api_hash = os.getenv("API_HASH")     # <-- Enter your API hash here

# This session file will be created on first run
tg_session = 'userbot_session'

client = TelegramClient(tg_session, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Only reply to private messages (DMs) and not your own outgoing messages
    if event.is_private and not event.out:
        sender = await event.get_sender()
        name = sender.first_name or sender.username or "there"
        user_id = sender.id
        chat_id = event.chat_id
        user_message = event.text

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
        prompt = (
            f"Greet {name} in a friendly and natural way, making it clear you are Abel's AI assistant while Abel is away. "
            f"Then continue the conversation based on the following context:\n{context}"
        )

        # Try Hugging Face first, then Ollama
        response = huggingface_generate(prompt)
        if not response:
            response = ollama_generate(prompt)
        if not response:
            response = f"Sorry {name}, I'm having trouble thinking right now."
        await event.reply(response)
        # Store the bot's response
        store_message(user_id, chat_id, user_message, response)

if __name__ == "__main__":
    print("Starting userbot... If this is your first run, you'll be asked for your phone number and Telegram code.")
    client.start()
    print("Userbot is running. Press Ctrl+C to stop.")
    client.run_until_disconnected() 