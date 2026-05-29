from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.langchain_tool import convert_openapi_to_typescript


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_FILE = ROOT / "assets" / "examples" / "demo-openapi.json"


class LangChainToolTests(unittest.TestCase):
    def test_convert_openapi_to_typescript_returns_plain_ts_by_default(self) -> None:
        output = convert_openapi_to_typescript(str(EXAMPLE_FILE), style="interface")
        self.assertIn("export interface ICreateUserReq {", output)
        self.assertIn("export interface IGetUserByIdResp {", output)

    def test_convert_openapi_to_typescript_returns_single_file_suggestion_package(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "types.ts"
            output = convert_openapi_to_typescript(
                str(EXAMPLE_FILE),
                style="type",
                output_mode="suggest_json",
                output_path=str(output_path),
            )

            payload = json.loads(output)
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["generator"], "TSTypeConversion")
            self.assertEqual(len(payload["items"]), 1)
            item = payload["items"][0]
            self.assertEqual(item["file"], str(output_path.resolve()))
            self.assertIn("TCreateUserReq", item["symbols"])
            self.assertIn("/users", item["source_paths"])

    def test_convert_openapi_to_typescript_returns_routed_suggestion_package(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_path = temp_root / "openapi-ts.config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "default_output: outputs/common.types.ts",
                        "rules:",
                        "  - match:",
                        "      operation_ids: [createUser]",
                        "    output: outputs/create-user.types.ts",
                    ]
                ),
                encoding="utf-8",
            )

            output = convert_openapi_to_typescript(
                str(EXAMPLE_FILE),
                style="interface",
                output_mode="suggest_json",
                output_config_path=str(config_path),
            )

            payload = json.loads(output)
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(len(payload["items"]), 2)
            payload_by_file = {item["file"]: item for item in payload["items"]}
            create_user_file = str((temp_root / "outputs" / "create-user.types.ts").resolve())
            common_file = str((temp_root / "outputs" / "common.types.ts").resolve())
            self.assertIn(create_user_file, payload_by_file)
            self.assertIn(common_file, payload_by_file)
            self.assertIn("ICreateUserReq", payload_by_file[create_user_file]["symbols"])
            self.assertIn("IGetUserByIdResp", payload_by_file[common_file]["symbols"])


if __name__ == "__main__":
    unittest.main()
