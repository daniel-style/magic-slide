from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SERVE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "serve.py"
SPEC = importlib.util.spec_from_file_location("magic_slide_serve", SERVE_PATH)
assert SPEC is not None and SPEC.loader is not None
serve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve)


class ServeArgumentsTest(unittest.TestCase):
    def test_explicit_managed_flags(self) -> None:
        args = serve.parse_args(
            [
                "deck/index.html",
                "--port",
                "12345",
                "--no-open",
                "--single-deck",
                "--managed-lifecycle",
            ]
        )

        self.assertEqual(args.port, 12345)
        self.assertTrue(args.no_open)
        self.assertTrue(args.single_deck)
        self.assertTrue(args.managed_lifecycle)

    def test_local_preview_keeps_idle_shutdown_enabled(self) -> None:
        args = serve.parse_args(["deck/index.html"])

        self.assertFalse(args.managed_lifecycle)

    def test_port_falls_back_to_managed_environment(self) -> None:
        with patch.dict(os.environ, {"CELHIVE_PREVIEW_PORT": "15432"}):
            args = serve.parse_args(["deck/index.html"])

        self.assertEqual(args.port, 15432)

    def test_single_deck_path_is_relative_to_the_browser_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            html_path = Path(directory) / "index.html"
            html_path.write_text("<html lang=\"en\"></html>", encoding="utf-8")
            deck = serve.build_deck(html_path, {})

            path = serve.deck_open_path(deck)

        self.assertTrue(path.startswith("deck/"))
        self.assertIn("#ms_token=", path)
        self.assertNotIn("127.0.0.1", path)


if __name__ == "__main__":
    unittest.main()
