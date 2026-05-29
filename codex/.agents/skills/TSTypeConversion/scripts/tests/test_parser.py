from __future__ import annotations

from pathlib import Path
import unittest

from scripts.loader import load_openapi_document
from scripts.parser import parse_openapi_document


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_FILE = ROOT / "assets" / "examples" / "demo-openapi.json"
SWAGGER2_FILE = ROOT / "assets" / "examples" / "demo-swagger2.yaml"


class ParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load_openapi_document(str(EXAMPLE_FILE))

    def test_parse_tasks_from_openapi_document(self) -> None:
        bundle = parse_openapi_document(self.document)
        self.assertEqual(len(bundle.tasks), 2)
        self.assertEqual(bundle.shared_schemas, [])

        get_user = next(task for task in bundle.tasks if task.operation_id == "getUserById")
        self.assertEqual(get_user.method, "get")
        self.assertEqual(get_user.path, "/users/{id}")
        self.assertEqual(sorted(get_user.request_schema["properties"]), ["id", "includePosts"])
        self.assertEqual(get_user.request_schema["required"], ["id"])
        self.assertEqual(get_user.response_schema["properties"]["profile"]["type"], "object")

    def test_parse_request_body_from_openapi_document(self) -> None:
        bundle = parse_openapi_document(self.document)
        create_user = next(task for task in bundle.tasks if task.operation_id == "createUser")
        self.assertEqual(create_user.request_schema["required"], ["name", "role"])
        self.assertEqual(
            create_user.request_schema["properties"]["role"]["enum"],
            ["admin", "member"],
        )
        self.assertEqual(create_user.request_schema["__ts_ref_name"], "CreateUserRequest")

    def test_parse_swagger2_document(self) -> None:
        document = load_openapi_document(str(SWAGGER2_FILE))
        bundle = parse_openapi_document(document)

        update_pet = next(task for task in bundle.tasks if task.operation_id == "updatePet")
        self.assertEqual(sorted(update_pet.request_schema["properties"]), ["age", "expand", "name", "petId"])
        self.assertEqual(update_pet.response_schema["__ts_composition"]["kind"], "extends")
        self.assertEqual(
            update_pet.response_schema["__ts_composition"]["extensions"][0]["properties"]["status"]["enum"],
            ["active", "archived"],
        )

        upload_file = next(task for task in bundle.tasks if task.operation_id == "uploadFile")
        self.assertEqual(upload_file.request_schema["properties"]["file"]["type"], "file")
        self.assertEqual(upload_file.request_schema["properties"]["category"]["type"], "string")

    def test_collect_shared_schemas_from_nested_refs(self) -> None:
        document = {
            "swagger": "2.0",
            "info": {"title": "Demo", "version": "1.0.0"},
            "paths": {
                "/user/login": {
                    "post": {
                        "operationId": "login",
                        "parameters": [
                            {
                                "name": "body",
                                "in": "body",
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
                    "properties": {
                        "nickname": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
                "UserInfo": {
                    "type": "object",
                    "properties": {"id": {"type": "integer", "format": "int64"}},
                },
                "LoginData": {
                    "type": "object",
                    "properties": {"userInfo": {"$ref": "#/definitions/UserInfo"}},
                },
                "LoginResp": {
                    "allOf": [
                        {"$ref": "#/definitions/Base"},
                        {
                            "type": "object",
                            "properties": {"data": {"$ref": "#/definitions/LoginData"}},
                        },
                    ]
                },
            },
        }

        bundle = parse_openapi_document(document)
        shared_names = {schema.source_name for schema in bundle.shared_schemas}
        self.assertEqual(shared_names, {"Base", "LoginData", "UserInfo"})


if __name__ == "__main__":
    unittest.main()
