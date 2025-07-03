import os
import re

import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from config import MAX_HISTORY, OLLAMA_MODEL, OLLAMA_URL, PROVIDER_ORDER, logger
from db import get_last_n_messages

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HF_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")


def ollama_generate(prompt: str) -> str:
    """Send a prompt to Ollama and return the response."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        return result.get(
            "response", "Sorry, I'm having trouble thinking right now."
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
        intro = (
            "Hi, I am Abel's personal AI assistant. "
            "Abel is not online at the moment, but you can talk to me about "
            "general things, knowledge, or ask me anything until he gets back online.\n\n"
        )
        concise_prompt = (
            intro + "Answer concisely in 2-3 sentences. " + prompt
        )
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-0528",
            messages=[
                {
                    "role": "user",
                    "content": concise_prompt,
                }
            ],
        )
        response = completion.choices[0].message.content
        # Remove <think>...</think> sections if present
        response = re.sub(
            r"<think>[\s\S]*?</think>",
            "",
            response,
            flags=re.IGNORECASE,
        ).strip()
        return response
    except Exception as e:
        logger.error(f"Hugging Face InferenceClient error: {e}")
        return None


def groq_generate(prompt: str) -> str:
    """Send a prompt to Groq API and return the response."""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        }
        system_message = (
            "You are Abel's personal AI assistant, acting as Abel when he is away. "
            "Your job is to keep users engaged in interesting, meaningful, and human-like conversations. "
            "Always use the provided conversation history to maintain context, remember details, and refer to previous messages. "
            "Be proactive: ask follow-up questions, show curiosity, and make the user feel heard. "
            "Be precise, avoid generic or vague answers, and tailor your responses to the user's interests and the ongoing topic. "
            "If an emoji or GIF would enhance your reply (for humor, emotion, or emphasis), add [EMOJI: ...] or [GIF: ...] at the end—otherwise, do not include these tags. "
            "Never mention that you are an AI or that Abel is away unless asked directly. "
            "Keep replies concise, friendly, and engaging."
        )
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        # Groq returns OpenAI-compatible response
        content = result["choices"][0]["message"]["content"]
        # Remove <think>...</think> sections if present
        content = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE).strip()
        return content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None


def get_context_for_ollama(
    user_id: int,
    chat_id: int,
    user_message: str,
) -> str:
    """Format the last n messages as context for Ollama."""
    context_pairs = get_last_n_messages(user_id, chat_id, MAX_HISTORY)
    context_parts = []
    for user_input, bot_response in context_pairs:
        context_parts.append(f"User: {user_input}")
        context_parts.append(f"Bot: {bot_response}")
    context_parts.append(f"User: {user_message}")
    return "\n".join(context_parts)


def generate_response(
    user_id: int,
    chat_id: int,
    user_message: str,
) -> str:
    """Generate a response using the available AI providers with fallback."""
    context = get_context_for_ollama(user_id, chat_id, user_message)
    logger.info(
        f"Sending context to AI providers for user {user_id}: '" f"{context}'")
    provider_funcs = {
        "groq": groq_generate,
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
            logger.info(
                f"{provider.capitalize()} response for user {user_id}: " f"'{response}'"
            )
            return response.strip()
        else:
            logger.warning(
                f"Provider {provider} failed or returned empty response.")
    logger.error("All AI providers failed. Returning fallback message.")
    return "Sorry, I'm having trouble thinking right now."
