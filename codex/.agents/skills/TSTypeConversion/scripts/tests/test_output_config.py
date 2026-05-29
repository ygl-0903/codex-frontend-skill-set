from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.output_config import (
    CONFIG_ENV_VAR,
    discover_output_config,
    load_output_config_file,
    resolve_output_config,
)
from scripts.parser import parse_openapi_document


DOCUMENT = {
    "openapi": "3.0.3",
    "info": {"title": "Routing", "version": "1.0.0"},
    "paths": {
        "/user/login": {
            "post": {
                "tags": ["auth"],
                "operationId": "login",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"ok": {"type": "boolean"}},
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


class OutputConfigTests(unittest.TestCase):
    def test_load_output_config_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openapi-ts.config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "default_output: src/api/common/types.ts",
                        "rules:",
                        "  - match:",
                        "      tags: [auth]",
                        "    output: src/api/auth/types.ts",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_output_config_file(str(config_path))
            self.assertEqual(config.default_output, "src/api/common/types.ts")
            self.assertEqual(len(config.rules), 1)
            self.assertEqual(config.rules[0].tags, {"auth"})

    def test_discover_output_config_by_walking_parent_directories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_dir = root / "apps" / "demo"
            project_dir.mkdir(parents=True)
            config_path = root / "openapi-ts.config.yaml"
            config_path.write_text("default_output: src/api/types.ts\n", encoding="utf-8")

            discovered = discover_output_config(project_dir)
            self.assertEqual(discovered, config_path.resolve())

    def test_resolve_output_config_from_environment(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openapi-ts.config.yaml"
            config_path.write_text("default_output: src/api/types.ts\n", encoding="utf-8")

            with patch.dict(os.environ, {CONFIG_ENV_VAR: str(config_path)}, clear=False):
                config = resolve_output_config(None, start_dir=Path(temp_dir))

            self.assertIsNotNone(config)
            assert config is not None
            self.assertEqual(config.config_path, config_path.resolve())

    def test_rule_priority_prefers_operation_id_over_tag(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openapi-ts.config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "default_output: src/api/common/types.ts",
                        "rules:",
                        "  - match:",
                        "      tags: [auth]",
                        "    output: src/api/tag-auth/types.ts",
                        "  - match:",
                        "      operation_ids: [login]",
                        "    output: src/api/op-auth/types.ts",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_output_config_file(str(config_path))
            bundle = parse_openapi_document(DOCUMENT)
            output_path = config.resolve_output_for_task(bundle.tasks[0])
            self.assertEqual(
                output_path,
                (Path(temp_dir) / "src" / "api" / "op-auth" / "types.ts").resolve(),
            )


if __name__ == "__main__":
    unittest.main()
