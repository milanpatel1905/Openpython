import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from openpython.assistant import (
    OpenPythonError,
    _extract_code,
    delete_saved_api_key,
    generate_code,
    get_api_key,
    save_api_key,
)


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_openai_requires_key(self):
        with self.assertRaisesRegex(OpenPythonError, "No API key"):
            generate_code("make a list")

    def test_fenced_response_is_returned_as_plain_code(self):
        self.assertEqual(_extract_code("```python\nprint('hello')\n```"), "print('hello')")
        self.assertEqual(_extract_code("print('hello')"), "print('hello')")

    def test_empty_response_is_rejected(self):
        with self.assertRaisesRegex(OpenPythonError, "empty response"):
            _extract_code("```python\n```\n")

    @patch("openpython.assistant.urlopen")
    def test_request_uses_configured_key_and_model(self, urlopen):
        os.environ["OPENPYTHON_API_KEY"] = "test-key"
        os.environ["OPENPYTHON_MODEL"] = "test-model"
        response = Mock()
        response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "print(1 + 1)"}}]}
        ).encode()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        urlopen.return_value = response

        result = generate_code("add one and one")

        self.assertEqual(result, "print(1 + 1)")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data)
        self.assertEqual(body["model"], "test-model")
        self.assertEqual(body["messages"][1]["content"], "add one and one")

    @patch("openpython.assistant.urlopen")
    def test_custom_local_endpoint_does_not_need_key(self, urlopen):
        os.environ["OPENPYTHON_BASE_URL"] = "http://localhost:11434/v1/"
        response = Mock()
        response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "answer = 42"}}]}
        ).encode()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        urlopen.return_value = response

        self.assertEqual(generate_code("set answer"), "answer = 42")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:11434/v1/chat/completions")
        self.assertIsNone(request.get_header("Authorization"))

    def test_blank_prompt_is_rejected(self):
        with self.assertRaisesRegex(OpenPythonError, "Add a short task"):
            generate_code("  ")

    def test_saved_key_is_reused_and_can_be_removed(self):
        with tempfile.TemporaryDirectory() as config_dir:
            os.environ["OPENPYTHON_CONFIG_DIR"] = config_dir
            save_api_key("saved-test-key")
            self.assertEqual(get_api_key(), "saved-test-key")
            delete_saved_api_key()
            self.assertIsNone(get_api_key())

    def test_environment_key_takes_precedence_over_saved_key(self):
        with tempfile.TemporaryDirectory() as config_dir:
            os.environ["OPENPYTHON_CONFIG_DIR"] = config_dir
            save_api_key("saved-test-key")
            os.environ["OPENPYTHON_API_KEY"] = "environment-key"
            self.assertEqual(get_api_key(), "environment-key")


if __name__ == "__main__":
    unittest.main()
