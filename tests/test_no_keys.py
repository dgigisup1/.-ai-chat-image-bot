import unittest
import os
from src.ai_chatbot import AIChatBot


class NoKeysTests(unittest.TestCase):
    def setUp(self):
        # Ensure tests run deterministically regardless of local env vars
        self._saved_openai = os.environ.pop("OPENAI_API_KEY", None)

    def tearDown(self):
        if self._saved_openai is not None:
            os.environ["OPENAI_API_KEY"] = self._saved_openai
    def test_chat_raises_without_key(self):
        bot = AIChatBot(openai_api_key=None)
        with self.assertRaises(RuntimeError) as cm:
            bot.chat("hello")
        self.assertIn("OPENAI_API_KEY not set", str(cm.exception))

    def test_generate_image_stub_raises(self):
        bot = AIChatBot()
        with self.assertRaises(RuntimeError):
            bot.generate_image("a test prompt")

    def test_generate_video_stub_raises(self):
        bot = AIChatBot()
        with self.assertRaises(RuntimeError):
            bot.generate_video("a test prompt")


if __name__ == '__main__':
    unittest.main()
