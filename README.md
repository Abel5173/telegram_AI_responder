# Abel's Personal Telegram Userbot AI Assistant

A modern, production-ready Telegram userbot that uses Hugging Face and Ollama for AI-powered, context-aware responses. The userbot replies to direct messages sent to your personal Telegram account, acting as your AI assistant when you're away. All conversations are stored in SQLite for context and continuity.

---

## Features

- **Personal AI Assistant:**
  - Replies to DMs as your personal account using Telethon.
  - Greets users by name and makes it clear it is your AI assistant.
- **Context-Aware AI:**
  - Uses the last N user/bot message pairs for context, improving reply quality.
- **Persistent Chat History:**
  - All messages are stored in SQLite (`chat_history.db`).
- **Provider Fallback:**
  - Uses Hugging Face (Together, DeepSeek, etc.) and Ollama (local) with automatic fallback.
- **Modern Python:**
  - Type hints, environment-based config, and robust error handling.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Abel5173/telegram_AI_responder.git
cd personal_telegram_bot_responder
```

### 2. Set Up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```dotenv
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
HUGGINGFACE_API_KEY=your_huggingface_or_together_api_key
# Optional: OLLAMA_URL, OLLAMA_MODEL, PROVIDER_ORDER
```
- Get your API ID and hash from [my.telegram.org](https://my.telegram.org).
- Get your Hugging Face API key from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

### 4. (Optional) Start Ollama (Llama 3.1 8B)
- [Install Ollama](https://ollama.com/download) and pull the model:
  ```bash
  ollama pull llama3.1:8b
  ollama serve
  ```
- Ensure Ollama is running and accessible at the URL in your `.env` (default: `http://localhost:11434/api/generate`).

### 5. Run the Userbot
```bash
python userbot.py
```
- On first run, you'll be prompted for your phone number and Telegram code.

---

## Docker Deployment

### 1. Build the Docker Image
```bash
docker build -t telegram-userbot .
```

### 2. Run the Container
You can provide environment variables using a file or directly:

**Using an env file:**
```bash
docker run --env-file .env telegram-userbot
```

**Or with inline variables:**
```bash
docker run -e API_ID=xxx -e API_HASH=xxx -e HUGGINGFACE_API_KEY=xxx telegram-userbot
```

- The database (`chat_history.db`) will be created inside the container. To persist it, mount a volume:
```bash
docker run --env-file .env -v $(pwd)/chat_history.db:/app/chat_history.db telegram-userbot
```

---

## File Overview
- `userbot.py`: Main userbot logic (Telethon, AI, chat history)
- `ai.py`: AI provider integration and fallback logic
- `db.py`: SQLite chat history management
- `config.py`: Environment, constants, logging
- `requirements.txt`: Python dependencies
- `chat_history.db`: SQLite database (auto-created)

---

## Environment Variables (.env)
```dotenv
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
HUGGINGFACE_API_KEY=your_huggingface_or_together_api_key
# Optional:
# OLLAMA_URL=http://localhost:11434/api/generate
# OLLAMA_MODEL=llama3.1:8b
# PROVIDER_ORDER=huggingface,ollama
```

---

## Maintenance & Upgrades
- Update dependencies with `pip install -U -r requirements.txt`.
- Review and rotate API keys regularly.
- Monitor Hugging Face and Ollama for new models and features.

---

## License
MIT 