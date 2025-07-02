import sys
import os
import unittest
from db import init_db, store_message, get_last_n_messages
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))


class TestDB(unittest.TestCase):
    def setUp(self):
        # Use a test DB file
        self.test_db = 'test_chat_history.db'
        os.environ['DB_PATH'] = self.test_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        os.environ['DB_PATH'] = 'chat_history.db'

    def test_store_and_retrieve_message(self):
        store_message(1, 1, 'Hello', 'Hi there!')
        context = get_last_n_messages(1, 1, n=1)
        self.assertEqual(context, [('Hello', 'Hi there!')])

    def test_empty_history(self):
        context = get_last_n_messages(2, 2, n=1)
        self.assertEqual(context, [])

    def test_multiple_pairs(self):
        for i in range(3):
            store_message(1, 1, f'User {i}', f'Bot {i}')
        context = get_last_n_messages(1, 1, n=2)
        self.assertEqual(context, [('User 1', 'Bot 1'), ('User 2', 'Bot 2')])


if __name__ == '__main__':
    unittest.main()
