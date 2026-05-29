from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.loader import load_openapi_document


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_FILE = ROOT / "assets" / "examples" / "demo-openapi.json"


class LoaderTests(unittest.TestCase):
    def test_load_local_json(self) -> None:
        document = load_openapi_document(str(EXAMPLE_FILE))
        self.assertEqual(document["openapi"], "3.0.3")

    def test_load_local_yaml(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "demo.yaml"
            payload = {
                "openapi": "3.0.3",
                "paths": {},
            }
            path.write_text("openapi: 3.0.3\npaths: {}\n", encoding="utf-8")
            document = load_openapi_document(str(path))
            self.assertEqual(document, payload)

    def test_load_remote_json(self) -> None:
        class DummyResponse(BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.close()
                return False

        with patch(
            "scripts.loader.urlopen",
            return_value=DummyResponse(EXAMPLE_FILE.read_bytes()),
        ):
            document = load_openapi_document("https://example.com/openapi.json")
            self.assertEqual(document["info"]["title"], "Demo API")

    def test_load_redoc_page_url_by_resolving_spec_parameter(self) -> None:
        class DummyResponse(BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.close()
                return False

        captured_urls: list[str] = []

        def fake_urlopen(request, timeout=30):
            captured_urls.append(request.full_url)
            return DummyResponse(EXAMPLE_FILE.read_bytes())

        with patch("scripts.loader.urlopen", side_effect=fake_urlopen):
            document = load_openapi_document(
                "https://example.com/docs/swagger/redoc.html?spec=/docs/swagger/user-api.swagger.json"
            )

        self.assertEqual(document["info"]["title"], "Demo API")
        self.assertEqual(
            captured_urls,
            ["https://example.com/docs/swagger/user-api.swagger.json"],
        )


if __name__ == "__main__":
    unittest.main()
