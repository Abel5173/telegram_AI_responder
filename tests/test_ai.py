import os
import sys
import unittest
from unittest.mock import patch

from ai import get_context_for_ollama, ollama_generate

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
))


class TestAI(unittest.TestCase):

    @patch("ai.requests.post")
    def test_ollama_generate_success(self, mock_post):
        mock_post.return_value.json.return_value = {"response": "Hi!"}
        mock_post.return_value.raise_for_status = lambda: None
        self.assertEqual(ollama_generate("Hello"), "Hi!")

    @patch("ai.requests.post", side_effect=Exception("API down"))
    def test_ollama_generate_failure(self, mock_post):
        self.assertIsNone(ollama_generate("Hello"))

    @patch(
        "ai.get_last_n_messages",
        return_value=[("Hi", "Hello!"), ("How are you?", "I'm good!")],
    )
    def test_get_context_for_ollama(self, mock_history):
        context = get_context_for_ollama(1, 1, "What's up?")
        self.assertIn("User: Hi", context)
        self.assertIn("Bot: Hello!", context)
        self.assertIn("User: How are you?", context)
        self.assertIn("Bot: I'm good!", context)
        self.assertIn("User: What's up?", context)

    @patch("ai.huggingface_generate", return_value=None)
    @patch("ai.ollama_generate", return_value=None)
    @patch(
        "ai.get_context_for_ollama",
        return_value="User: Hi\nBot: Hello!\nUser: What's up?",
    )
    @patch("ai.PROVIDER_ORDER", new=["ollama", "huggingface"])
    def test_generate_response_all_fail(
        self, mock_context, mock_ollama, mock_hf
    ):
        from ai import generate_response
        response = generate_response(1, 1, "What's up?")
        self.assertIn(
            "Sorry", response
        )


if __name__ == "__main__":
    unittest.main()
