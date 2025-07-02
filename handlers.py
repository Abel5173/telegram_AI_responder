from config import logger, RESPONSE_DELAY_SECONDS
from db import store_message
from ai import generate_response
import threading
import time
import requests


def handle_afk_command(message, bot, OWNER_AFK_ref, owner_id_int):
    if message.from_user.id == owner_id_int:
        OWNER_AFK_ref[0] = True
        bot.reply_to(
            message,
            "AFK mode enabled. I'll cover your DMs after 15 seconds "
            "if you don't reply."
        )
        logger.info("Owner set AFK mode ON.")
    else:
        bot.reply_to(message, "Only the owner can use this command.")


def handle_back_command(message, bot, OWNER_AFK_ref, owner_id_int):
    if message.from_user.id == owner_id_int:
        OWNER_AFK_ref[0] = False
        bot.reply_to(
            message,
            "Welcome back! I won't auto-respond anymore."
        )
        logger.info("Owner set AFK mode OFF.")
    else:
        bot.reply_to(message, "Only the owner can use this command.")


def handle_status_command(message, bot, OWNER_AFK_ref):
    status = "AFK" if OWNER_AFK_ref[0] else "online"
    bot.reply_to(message, f"Owner is currently {status}.")


def handle_track_owner_reply(message, last_owner_reply, logger, owner_id_int):
    last_owner_reply[message.chat.id] = time.time()
    logger.info(
        f"Tracked owner reply in chat {message.chat.id} at "
        f"{last_owner_reply[message.chat.id]}"
    )


def owner_replied_recently(
    chat_id: int, since: float, last_owner_reply: dict
) -> bool:
    return last_owner_reply.get(chat_id, 0) > since


def handle_main_message(
    message, bot, last_owner_reply, owner_id_int, OWNER_AFK_ref
):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_message = message.text
    logger.info(
        f"handle_message triggered by user {user_id} in chat {chat_id}"
    )
    # Directly respond to every message for testing
    store_message(user_id, chat_id, 'user', user_message)
    bot.send_chat_action(chat_id, 'typing')
    response_text = generate_response(user_id, chat_id, user_message)
    bot.send_message(chat_id, response_text)
    logger.info(
        f"Sent AI response to user {user_id}: '{response_text}'"
    )
    store_message(user_id, chat_id, 'bot', response_text)


def register_handlers(bot, last_owner_reply, owner_id_int, OWNER_AFK_ref):
    @bot.message_handler(commands=['afk'])
    def set_afk(message):
        handle_afk_command(message, bot, OWNER_AFK_ref, owner_id_int)

    @bot.message_handler(commands=['back'])
    def set_back(message):
        handle_back_command(message, bot, OWNER_AFK_ref, owner_id_int)

    @bot.message_handler(commands=['status'])
    def status(message):
        handle_status_command(message, bot, OWNER_AFK_ref)

    @bot.message_handler(
        chat_types=['private'],
        func=lambda message: True
    )
    def handle_message(message):
        handle_main_message(
            message, bot, last_owner_reply, owner_id_int, OWNER_AFK_ref
        )
