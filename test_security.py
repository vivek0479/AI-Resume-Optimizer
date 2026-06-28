import os
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("backend", ROOT / "backend.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class SecurityStorageTests(unittest.TestCase):
    def test_save_api_key_writes_secret_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            backend._STREAMLIT_SECRETS_PATH = str(tmp_path / ".streamlit" / "secrets.toml")
            backend.save_api_key("secret-key")

            self.assertEqual(os.environ["GEMINI_API_KEY"], "secret-key")
            self.assertTrue((tmp_path / ".streamlit" / "secrets.toml").exists())

            content = (tmp_path / ".streamlit" / "secrets.toml").read_text(encoding="utf-8")
            self.assertIn("GEMINI_API_KEY", content)
            self.assertIn("secret-key", content)

    def test_clear_api_key_removes_secret_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            backend._STREAMLIT_SECRETS_PATH = str(tmp_path / ".streamlit" / "secrets.toml")
            backend.save_api_key("secret-key")
            backend.save_api_key("")

            self.assertNotIn("GEMINI_API_KEY", os.environ)
            self.assertFalse((tmp_path / ".streamlit" / "secrets.toml").exists())


if __name__ == "__main__":
    unittest.main()
