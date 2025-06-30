# Personal Telegram Bot Responder

This is a simple Telegram bot that uses the Hugging Face Inference API to automatically respond to direct messages when you are offline. It's designed to act as a personal assistant, keeping conversations going until you're available to reply yourself.

The bot uses the `facebook/blenderbot-400M-distill` model for generating conversational responses.

## Features

-   **Automatic Responses:** Responds to DMs when the owner is detected as "offline."
-   **Context-Aware:** Keeps track of the last 3 messages in each conversation for more relevant replies.
-   **Delayed Replies:** Waits 15 seconds before replying to feel more natural.
-   **Error Handling:** Gracefully handles API failures with a fallback message.
-   **Configurable:** All API keys and personal IDs are configured via a `.env` file.

## Getting Started

Follow these instructions to get the bot up and running on your local machine for development and testing.

### 1. Prerequisites

-   Python 3.8 or newer.
-   A Telegram Bot Token from [BotFather](https://t.me/BotFather).
-   A Hugging Face User Access Token (API Key) with `read` permissions from your [Hugging Face account settings](https://huggingface.co/settings/tokens).
-   Your personal Telegram User ID. You can get this from a bot like [@userinfobot](https://t.me/userinfobot).

### 2. Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd personal_telegram_bot_responder
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add your API keys and User ID.

    ```dotenv
    # Telegram Bot API Token from BotFather
    TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN"

    # Hugging Face API Key from your Hugging Face account
    HF_API_KEY="YOUR_HUGGING_FACE_API_KEY"

    # Your personal Telegram User ID
    OWNER_USER_ID="YOUR_TELEGRAM_USER_ID"
    ```

### 3. Running the Bot Locally

To start the bot, simply run the `bot.py` script from your terminal:

```bash
python bot.py
```

The bot will start polling for new messages. You can stop it by pressing `Ctrl+C`.

## Deployment to Hugging Face Spaces

You can deploy this bot for free on [Hugging Face Spaces](https://huggingface.co/spaces).

1.  **Create a new Space:**
    -   Go to [huggingface.co/new-space](https://huggingface.co/new-space).
    -   Give it a name and select **Docker** > **Blank** as the Space SDK.
    -   Choose the free "CPU basic" hardware.
    -   Create the Space.

2.  **Upload your files:**
    -   Upload `bot.py`, `requirements.txt`, and `.gitignore`. You can do this via the web interface or by cloning the Space's Git repository.

3.  **Create a `Dockerfile`:**
    -   In your Hugging Face Space, create a new file named `Dockerfile` with the following content:

    ```dockerfile
    FROM python:3.9-slim

    WORKDIR /code

    COPY ./requirements.txt /code/requirements.txt

    RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

    COPY ./bot.py /code/bot.py

    CMD ["python", "/code/bot.py"]
    ```

4.  **Add your secrets:**
    -   In your Space's settings, navigate to the **Secrets** section.
    -   Add your `TELEGRAM_TOKEN`, `HF_API_KEY`, and `OWNER_USER_ID` as secrets. These will be securely injected as environment variables.

The Space will automatically build and run your bot. Check the logs on the Space's page to see the bot's status.

## Next Steps and Enhancements

This bot is a great starting point. Here are a few ideas for taking it to the next level:

-   **Improve Offline Detection:** The current `is_owner_online()` function always returns `False`. You could improve this by:
    -   Checking your Telegram presence using a user-bot library (can be complex).
    -   Creating commands like `/afk` and `/online` for you (the owner) to manually set your status.
    -   Connecting it to an external service like IFTTT or a calendar to know when you're busy.

-   **Add Commands:**
    -   Create a `/clear` command to wipe the conversation history for a user.
    -   Create a `/status` command to check if the bot is running and the owner's status.

-   **Use a Database:** The current chat history is stored in memory, so it will be lost if the bot restarts. You could use a simple database like `SQLite` or a cloud-based one to persist conversations.

-   **Try Different Models:** Experiment with other conversational models on the Hugging Face Hub. Simply change the `MODEL_ID` constant in `bot.py`. 