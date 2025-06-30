import requests
from config import OLLAMA_URL, OLLAMA_MODEL, logger, MAX_HISTORY
from db import get_last_n_messages


def ollama_generate(prompt: str) -> str:
    """Send a prompt to Ollama and return the response."""
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
        return result.get("response", "Sorry, I'm having trouble thinking right now.").strip()
    except Exception as e:
        logger.error(f"Ollama API error: {e}", exc_info=True)
        return "Sorry, I'm having trouble thinking right now."


def get_context_for_ollama(user_id, chat_id, user_message):
    """Format the last n messages as context for Ollama."""
    context_pairs = get_last_n_messages(user_id, chat_id, MAX_HISTORY)
    context_parts = []
    for user_input, bot_response in context_pairs:
        context_parts.append(f"User: {user_input}")
        context_parts.append(f"Bot: {bot_response}")
    context_parts.append(f"User: {user_message}")
    return "\n".join(context_parts)


def generate_response(user_id: int, chat_id: int, user_message: str) -> str:
    """Generate a response using Ollama with context."""
    context = get_context_for_ollama(user_id, chat_id, user_message)
    logger.info(f"Sending context to Ollama for user {user_id}: '{context}'")
    response = ollama_generate(context)
    logger.info(f"Ollama response for user {user_id}: '{response}'")
    return response 