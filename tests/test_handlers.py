import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock
from handlers import handle_afk_command, handle_back_command, handle_status_command


class TestHandlers(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.last_owner_reply = {}
        self.owner_id_int = 123
        self.OWNER_AFK = [True]

    def test_afk_command_owner(self):
        message = MagicMock()
        message.from_user.id = self.owner_id_int
        handle_afk_command(message, self.bot, self.OWNER_AFK, self.owner_id_int)
        self.assertTrue(self.OWNER_AFK[0])
        self.bot.reply_to.assert_called_with(
            message, "AFK mode enabled. I'll cover your DMs after 15 seconds if you don't reply."
        )

    def test_afk_command_non_owner(self):
        message = MagicMock()
        message.from_user.id = 999
        handle_afk_command(message, self.bot, self.OWNER_AFK, self.owner_id_int)
        self.assertTrue(self.OWNER_AFK[0])
        self.bot.reply_to.assert_called_with(
            message, "Only the owner can use this command."
        )

    def test_back_command_owner(self):
        message = MagicMock()
        message.from_user.id = self.owner_id_int
        handle_back_command(message, self.bot, self.OWNER_AFK, self.owner_id_int)
        self.assertFalse(self.OWNER_AFK[0])
        self.bot.reply_to.assert_called_with(
            message, "Welcome back! I won't auto-respond anymore."
        )

    def test_status_command(self):
        message = MagicMock()
        self.OWNER_AFK[0] = True
        handle_status_command(message, self.bot, self.OWNER_AFK)
        self.bot.reply_to.assert_called_with(
            message, "Owner is currently AFK."
        )
        self.OWNER_AFK[0] = False
        handle_status_command(message, self.bot, self.OWNER_AFK)
        self.bot.reply_to.assert_called_with(
            message, "Owner is currently online."
        )


if __name__ == '__main__':
    unittest.main() 