[![CI](https://github.com/Abel5173/telegram_AI_responder/actions/workflows/ci.yml/badge.svg)](https://github.com/Abel5173/telegram_AI_responder/actions/workflows/ci.yml)

# Personal Telegram Bot Responder

A modular, production-ready Telegram bot that uses [Ollama](https://ollama.com/) (Llama 3.1 8B) for AI-powered responses, with persistent chat history in SQLite, robust AFK/owner logic, and full Docker and test support.

---

## Features

- **Automatic AFK Responses:**
  - When the owner is AFK, the bot replies to DMs after a delay, using LLM-generated responses.
- **Context-Aware AI:**
  - Uses the last 3 user/bot message pairs for context, improving reply quality.
- **Persistent Chat History:**
  - All messages are stored in SQLite (`chat_history.db`).
- **Owner Commands:**
  - `/afk`, `/back`, `/status` for AFK mode and status control.
- **Robust Error Handling:**
  - Handles network, DB, and API errors gracefully, with exponential backoff for Telegram API issues.
- **Modular Codebase:**
  - Clean separation: `bot.py`, `handlers.py`, `ai.py`, `db.py`, `config.py`.
- **Comprehensive Unit Tests:**
  - For all core logic, using `pytest` and `unittest.mock`.
- **Dockerized:**
  - Easy to deploy anywhere with Docker.

---

## Architecture Overview

```
Telegram <-> bot.py <-> handlers.py <-> ai.py <-> Ollama
                                 |-> db.py <-> SQLite
                                 |-> config.py
```
- **bot.py:** Main entry, error handling, handler registration.
- **handlers.py:** All Telegram command and message logic.
- **ai.py:** Ollama (LLM) integration and context formatting.
- **db.py:** SQLite chat history management.
- **config.py:** Environment, constants, logging.

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
TELEGRAM_TOKEN=your_telegram_bot_token
OWNER_USER_ID=your_telegram_user_id
# Optional: override Ollama settings
# OLLAMA_URL=http://localhost:11434/api/generate
# OLLAMA_MODEL=llama3.1:8b
```
- Get your bot token from [@BotFather](https://t.me/BotFather).
- Get your user ID from [@userinfobot](https://t.me/userinfobot).

### 4. Start Ollama (Llama 3.1 8B)
- [Install Ollama](https://ollama.com/download) and pull the model:
  ```bash
  ollama pull llama3.1:8b
  ollama serve
  ```
- Ensure Ollama is running and accessible at the URL in your `.env` (default: `http://localhost:11434/api/generate`).

### 5. Run the Bot
```bash
python bot.py
```

---

## Docker Deployment

### 1. Build the Docker Image
```bash
docker build -t telegram-bot .
```

### 2. Run the Container
```bash
docker run --env-file .env -v $(pwd)/chat_history.db:/app/chat_history.db telegram-bot
```
- `--env-file .env`: Loads your environment variables.
- `-v $(pwd)/chat_history.db:/app/chat_history.db`: Persists chat history outside the container.

### 3. (Optional) Use Docker Compose
Create a `docker-compose.yml` for easier multi-service management (Ollama + bot).

---

## Testing

### 1. Run All Unit Tests
```bash
pytest tests/
```
- Tests cover all core logic: database, AI, and handler logic.
- No real Telegram or Ollama calls are made during unit tests.

### 2. Linting (Optional)
```bash
pip install flake8
flake8 .
```

---

## Troubleshooting

- **Bot does not reply:**
  - Check that your `.env` is correct and Ollama is running.
  - Check logs for errors (network, DB, or API issues).
- **Docker: DNS or network errors:**
  - Add `--dns=8.8.8.8` to your `docker run` command if needed.
- **Unit tests fail to import modules:**
  - Ensure you run `pytest` from the project root, or use the provided `sys.path` fix in test files.
- **Integration testing:**
  - Integration tests are not included by default due to Python 3.12 compatibility issues with `python-telegram-bot` v13.x. See README history for details.

---

## Contributing
- PRs and issues are welcome! Please add tests for new features.

---

## License
MIT 

## AI Provider Support and Fallback

The bot supports multiple AI providers with automatic fallback:
- Hugging Face (Together, DeepSeek, etc.)
- Ollama (local, as last fallback)

The provider order can be set via the `PROVIDER_ORDER` environment variable (default: `huggingface,ollama`).

### Required Environment Variables (.env)
Create a `.env` file in the project root or use `.env.example` as a template:
```dotenv
TELEGRAM_TOKEN=your_telegram_bot_token
OWNER_USER_ID=your_telegram_user_id
HUGGINGFACE_API_KEY=your_huggingface_or_together_api_key
# Optional overrides:
# OLLAMA_URL=http://localhost:11434/api/generate
# OLLAMA_MODEL=llama3.1:8b
# PROVIDER_ORDER=huggingface,ollama
```

- Get your API keys from the respective provider dashboards.
- Only the first available provider with a valid response will be used for each request.

## Code Quality & Testing

- Format code with [black](https://black.readthedocs.io/en/stable/):
  ```bash
  black .
  ```
- Run all tests and check coverage:
  ```bash
  pytest tests/
  coverage run -m pytest
  coverage report -m
  ```
- Aim for >90% test coverage for production deployments. 