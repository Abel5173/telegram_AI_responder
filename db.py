import sqlite3
from datetime import datetime, timezone
from config import DB_PATH, logger, MAX_HISTORY


def init_db():
    """Initialize the SQLite database and create the messages table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                sender TEXT,
                message_text TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("SQLite database initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        raise


def store_message(user_id, chat_id, sender, message_text, timestamp=None):
    """Store a message in the database."""
    try:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (user_id, chat_id, sender, message_text, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, chat_id, sender, message_text, timestamp)
        )
        conn.commit()
        conn.close()
        logger.info(f"Stored message for user {user_id} in chat {chat_id} as {sender}.")
    except Exception as e:
        logger.error(f"Failed to store message: {e}", exc_info=True)


def get_last_n_messages(user_id, chat_id, n=MAX_HISTORY):
    """Retrieve the last n user/bot message pairs for context."""
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
            (user_id, chat_id, n * 2)
        )
        rows = c.fetchall()
        conn.close()
        rows = rows[::-1]
        user_msgs = []
        bot_msgs = []
        for sender, msg in rows:
            if sender == 'user':
                user_msgs.append(msg)
            elif sender == 'bot':
                bot_msgs.append(msg)
        context = []
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