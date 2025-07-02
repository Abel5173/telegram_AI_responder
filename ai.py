import requests
import os
from config import (
    OLLAMA_URL, OLLAMA_MODEL, logger, MAX_HISTORY,
    HUGGINGFACE_API_KEY,
    PROVIDER_ORDER
)
from db import get_last_n_messages
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import re

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HF_API_KEY")


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
        return result.get(
            "response",
            "Sorry, I'm having trouble thinking right now."
        ).strip()
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return None


def huggingface_generate(prompt: str) -> str:
    """Generate a concise response using Together provider and DeepSeek model."""
    try:
        client = InferenceClient(
            provider="together",
            api_key=HUGGINGFACE_TOKEN,
        )
        concise_prompt = "Answer concisely in 2-3 sentences. " + prompt
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-0528",
            messages=[
                {
                    "role": "user",
                    "content": concise_prompt
                }
            ],
        )
        response = completion.choices[0].message.content
        # Remove <think>...</think> sections if present
        response = re.sub(r'<think>[\s\S]*?</think>', '', response, flags=re.IGNORECASE).strip()
        return response
    except Exception as e:
        logger.error(f"Hugging Face InferenceClient error: {e}")
        return None


def get_context_for_ollama(user_id: int, chat_id: int, user_message: str) -> str:
    """Format the last n messages as context for Ollama."""
    context_pairs = get_last_n_messages(user_id, chat_id, MAX_HISTORY)
    context_parts = []
    for user_input, bot_response in context_pairs:
        context_parts.append(f"User: {user_input}")
        context_parts.append(f"Bot: {bot_response}")
    context_parts.append(f"User: {user_message}")
    return "\n".join(context_parts)


def generate_response(user_id: int, chat_id: int, user_message: str) -> str:
    """Generate a response using the available AI providers with fallback."""
    context = get_context_for_ollama(user_id, chat_id, user_message)
    logger.info(f"Sending context to AI providers for user {user_id}: '{context}'")
    provider_funcs = {
        "ollama": ollama_generate,
        "huggingface": huggingface_generate,
    }
    for provider in PROVIDER_ORDER:
        func = provider_funcs.get(provider)
        if not func:
            continue
        logger.info(f"Trying provider: {provider}")
        response = func(context)
        if response and isinstance(response, str) and response.strip():
            logger.info(f"{provider.capitalize()} response for user {user_id}: '{response}'")
            return f"[{provider}] {response.strip()}"
        else:
            logger.warning(f"Provider {provider} failed or returned empty response.")
    logger.error("All AI providers failed. Returning fallback message.")
    return "Sorry, I'm having trouble thinking right now."
