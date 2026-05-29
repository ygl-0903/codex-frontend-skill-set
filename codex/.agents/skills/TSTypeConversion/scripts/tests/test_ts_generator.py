from __future__ import annotations

import os
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.cli import main
from scripts.loader import load_openapi_document
from scripts.models import TypeScriptRenderOptions
from scripts.parser import parse_openapi_document
from scripts.ts_generator import generate_typescript


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_FILE = ROOT / "assets" / "examples" / "demo-openapi.json"
SWAGGER2_FILE = ROOT / "assets" / "examples" / "demo-swagger2.yaml"


LOGIN_DOCUMENT = {
    "swagger": "2.0",
    "info": {"title": "User API", "version": "1.0.0"},
    "paths": {
        "/user/login": {
            "post": {
                "tags": ["user"],
                "summary": "用户登录",
                "operationId": "login",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/LoginReq"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {"$ref": "#/definitions/LoginResp"},
                    }
                },
            }
        }
    },
    "definitions": {
        "Base": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "format": "int64"},
                "msg": {"type": "string"},
                "success": {"type": "boolean"},
            },
        },
        "LoginReq": {
            "type": "object",
            "required": ["password"],
            "properties": {
                "nickname": {"type": "string"},
                "workId": {"type": "string"},
                "domainId": {"type": "string"},
                "password": {"type": "string"},
            },
        },
        "UserInfo": {
            "type": "object",
            "description": "用户信息",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
            },
        },
        "LoginData": {
            "type": "object",
            "properties": {
                "userInfo": {"$ref": "#/definitions/UserInfo"},
                "accessToken": {"type": "string"},
            },
        },
        "LoginResp": {
            "type": "object",
            "allOf": [
                {"$ref": "#/definitions/Base"},
                {
                    "type": "object",
                    "properties": {
                        "data": {"$ref": "#/definitions/LoginData"},
                    },
                },
            ],
        },
    },
}


class TypeScriptGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        document = load_openapi_document(str(EXAMPLE_FILE))
        self.bundle = parse_openapi_document(document)

    def test_generate_interface_style_for_request_and_response_only(self) -> None:
        output = generate_typescript(
            self.bundle,
            TypeScriptRenderOptions(style="interface"),
        )
        self.assertIn("export interface ICreateUserReq {", output)
        self.assertIn("export interface IGetUserByIdResp {", output)
        self.assertNotIn("PathParams", output)
        self.assertNotIn("Response =", output)
        self.assertIn("role: \"admin\" | \"member\";", output)
        self.assertIn("Avatar url.", output)
        self.assertIn("@deprecated", output)

    def test_generate_type_style_with_nested_union_comments(self) -> None:
        output = generate_typescript(
            self.bundle,
            TypeScriptRenderOptions(style="type"),
        )
        self.assertIn("export type TCreateUserReq = {", output)
        self.assertIn("export type TGetUserByIdResp = {", output)
        self.assertIn("Allowed values: \"admin\", \"member\"", output)

    def test_generate_swagger2_request_with_body_and_params(self) -> None:
        document = load_openapi_document(str(SWAGGER2_FILE))
        bundle = parse_openapi_document(document)
        output = generate_typescript(
            bundle,
            TypeScriptRenderOptions(style="type"),
        )
        self.assertIn("export type TUpdatePetReq = {", output)
        self.assertIn("petId: string;", output)
        self.assertIn("expand?: boolean;", output)
        self.assertIn("name: string;", output)
        self.assertIn("age?: number;", output)
        self.assertIn("export type TUploadFileReq = {", output)
        self.assertIn("file: Blob;", output)

    def test_generate_generic_base_response_and_shared_vo(self) -> None:
        bundle = parse_openapi_document(LOGIN_DOCUMENT)
        output = generate_typescript(
            bundle,
            TypeScriptRenderOptions(style="interface"),
        )
        self.assertIn("export interface IBase<T = any> {", output)
        self.assertIn("data?: T;", output)
        self.assertIn("export interface IUserInfoVO {", output)
        self.assertIn("export interface ILoginDataVO {", output)
        self.assertIn("export interface IUserLoginResp extends IBase<ILoginDataVO>", output)
        self.assertIn("export interface ILoginReq {", output)

    def test_generate_intersection_and_union_from_composition(self) -> None:
        document = {
            "openapi": "3.0.3",
            "info": {"title": "Types", "version": "1.0.0"},
            "paths": {
                "/meta": {
                    "get": {
                        "operationId": "getMeta",
                        "responses": {
                            "200": {
                                "description": "Meta",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "allOf": [
                                                {"$ref": "#/components/schemas/AuditFields"},
                                                {"$ref": "#/components/schemas/PermissionFields"},
                                            ]
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/animal": {
                    "get": {
                        "operationId": "getAnimal",
                        "responses": {
                            "200": {
                                "description": "Animal",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "oneOf": [
                                                {"$ref": "#/components/schemas/Cat"},
                                                {"$ref": "#/components/schemas/Dog"},
                                            ]
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "AuditFields": {
                        "type": "object",
                        "properties": {"createdAt": {"type": "string"}},
                    },
                    "PermissionFields": {
                        "type": "object",
                        "properties": {"role": {"type": "string"}},
                    },
                    "Cat": {
                        "type": "object",
                        "properties": {"meow": {"type": "boolean"}},
                    },
                    "Dog": {
                        "type": "object",
                        "properties": {"bark": {"type": "boolean"}},
                    },
                }
            },
        }
        bundle = parse_openapi_document(document)
        output = generate_typescript(
            bundle,
            TypeScriptRenderOptions(style="type"),
        )
        self.assertIn("export type TAuditFieldsVO = {", output)
        self.assertIn("export type TPermissionFieldsVO = {", output)
        self.assertIn("export type TGetMetaResp = TAuditFieldsVO & TPermissionFieldsVO;", output)
        self.assertIn("export type TCatVO = {", output)
        self.assertIn("export type TDogVO = {", output)
        self.assertIn("export type TGetAnimalResp = TCatVO | TDogVO;", output)

    def test_cli_writes_output_and_supports_path_filter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "types.ts"
            exit_code = main(
                [
                    "--input",
                    str(EXAMPLE_FILE),
                    "--style",
                    "interface",
                    "--path",
                    "/users",
                    "--output",
                    str(output_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            output = output_path.read_text(encoding="utf-8")
            self.assertIn("export interface ICreateUserReq {", output)
            self.assertIn("export interface ICreateUserResp {", output)
            self.assertNotIn("IGetUserByIdResp", output)

    def test_cli_routes_outputs_by_config_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_path = temp_root / "openapi-ts.config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "default_output: outputs/common.types.ts",
                        "rules:",
                        "  - match:",
                        "      tags: [users]",
                        "    output: outputs/users.types.ts",
                    ]
                ),
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "--input",
                    str(EXAMPLE_FILE),
                    "--style",
                    "interface",
                    "--output-config",
                    str(config_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            users_output = (temp_root / "outputs" / "users.types.ts").read_text(encoding="utf-8")
            self.assertIn("export interface ICreateUserReq {", users_output)
            self.assertIn("export interface IGetUserByIdResp {", users_output)
            self.assertFalse((temp_root / "outputs" / "common.types.ts").exists())

    def test_cli_outputs_single_file_suggestion_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "types.ts"
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(EXAMPLE_FILE),
                        "--style",
                        "interface",
                        "--output",
                        str(output_path),
                        "--suggest-json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["generator"], "TSTypeConversion")
            self.assertEqual(payload["mode"], "suggest_json")
            self.assertEqual(len(payload["items"]), 1)
            item = payload["items"][0]
            self.assertEqual(item["file"], str(output_path.resolve()))
            self.assertIn("ICreateUserReq", item["symbols"])
            self.assertIn("IGetUserByIdResp", item["symbols"])
            self.assertIn("/users", item["source_paths"])
            self.assertEqual(item["style"], "interface")
            self.assertEqual(
                item["merge_hint"]["preferred_action"],
                "agent_inspect_and_patch",
            )
            self.assertFalse(output_path.exists())

    def test_cli_outputs_routed_suggestion_json(self) -> None:
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
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(EXAMPLE_FILE),
                        "--style",
                        "type",
                        "--output-config",
                        str(config_path),
                        "--suggest-json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(len(payload["items"]), 2)
            payload_by_file = {item["file"]: item for item in payload["items"]}
            create_user_file = str((temp_root / "outputs" / "create-user.types.ts").resolve())
            common_file = str((temp_root / "outputs" / "common.types.ts").resolve())
            self.assertIn(create_user_file, payload_by_file)
            self.assertIn(common_file, payload_by_file)
            self.assertIn("TCreateUserReq", payload_by_file[create_user_file]["symbols"])
            self.assertIn("createUser", payload_by_file[create_user_file]["operation_ids"])
            self.assertIn("TGetUserByIdResp", payload_by_file[common_file]["symbols"])
            self.assertFalse((temp_root / "outputs" / "create-user.types.ts").exists())
            self.assertFalse((temp_root / "outputs" / "common.types.ts").exists())

    def test_cli_auto_discovers_project_output_config(self) -> None:
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
            project_dir = temp_root / "project"
            project_dir.mkdir()

            previous_cwd = Path.cwd()
            try:
                os.chdir(project_dir)
                exit_code = main(
                    [
                        "--input",
                        str(EXAMPLE_FILE),
                        "--style",
                        "type",
                    ]
                )
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(exit_code, 0)
            create_user_output = (
                temp_root / "outputs" / "create-user.types.ts"
            ).read_text(encoding="utf-8")
            common_output = (temp_root / "outputs" / "common.types.ts").read_text(
                encoding="utf-8"
            )
            self.assertIn("export type TCreateUserReq = {", create_user_output)
            self.assertIn("export type TGetUserByIdResp = {", common_output)


if __name__ == "__main__":
    unittest.main()
