import sqlite3

from config import DB_PATH, logger


def init_db() -> None:
    """Initialize the SQLite database and create tables if they do not exist.
    Drops and recreates the messages table for a fresh schema.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS messages")
        cursor.execute(
            "CREATE TABLE messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER,"
            "chat_id INTEGER,"
            "message TEXT,"
            "response TEXT,"
            "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


def store_message(
    user_id: int,
    chat_id: int,
    message: str,
    response: str,
) -> None:
    """Store a user message and bot response in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, chat_id, message, response) "
            "VALUES (?, ?, ?, ?)",
            (user_id, chat_id, message, response),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error storing message: {e}")


def get_last_n_messages(
    user_id: int,
    chat_id: int,
    n: int,
) -> list[tuple[str, str]]:
    """Retrieve the last n user/bot message pairs for a given user and chat."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, response FROM messages "
            "WHERE user_id = ? AND chat_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, chat_id, n),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows[::-1]  # Return in chronological order
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return []


def is_new_user(user_id: int) -> bool:
    """Return True if the user has no messages in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM messages WHERE user_id = ? LIMIT 1", (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is None
    except Exception as e:
        logger.error(f"Error checking if user is new: {e}")
        return True  # Assume new if error
