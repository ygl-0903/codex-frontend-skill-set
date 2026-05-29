from __future__ import annotations

from typing import Any

from .models import ApiTypeTask, ParsedTypeBundle
from .schema_resolver import SchemaResolver


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
PREFERRED_CONTENT_TYPES = (
    "application/json",
    "application/*+json",
    "multipart/form-data",
    "application/x-www-form-urlencoded",
)


def parse_openapi_document(document: dict[str, Any]) -> ParsedTypeBundle:
    """把 Swagger/OpenAPI 文档解析成请求/响应 DTO 任务集合。"""
    resolver = SchemaResolver(document)
    tasks: list[ApiTypeTask] = []
    warnings: list[str] = []
    paths = document.get("paths", {})

    for path, path_item in paths.items():
        shared_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            tasks.append(
                _parse_operation(
                    document=document,
                    resolver=resolver,
                    path=path,
                    method=method.lower(),
                    shared_parameters=shared_parameters,
                    operation=operation,
                    warnings=warnings,
                )
            )

    root_schemas: list[dict[str, Any]] = []
    for task in tasks:
        if task.request_schema:
            root_schemas.append(task.request_schema)
        if task.response_schema:
            root_schemas.append(task.response_schema)

    return ParsedTypeBundle(
        tasks=tasks,
        shared_schemas=resolver.collect_shared_schemas(root_schemas),
        warnings=warnings,
    )


def _parse_operation(
    document: dict[str, Any],
    resolver: SchemaResolver,
    path: str,
    method: str,
    shared_parameters: list[dict[str, Any]],
    operation: dict[str, Any],
    warnings: list[str],
) -> ApiTypeTask:
    merged_parameters = _merge_parameters(shared_parameters, operation.get("parameters", []))
    request_schema = _build_request_schema(document, resolver, operation, merged_parameters)
    response_schema = _extract_primary_response_schema(
        document=document,
        resolver=resolver,
        operation=operation,
        path=path,
        method=method,
        warnings=warnings,
    )

    return ApiTypeTask(
        path=path,
        method=method,
        operation_id=_build_operation_id(path, method, operation),
        tags=operation.get("tags", []),
        summary=operation.get("summary"),
        description=operation.get("description"),
        request_schema=request_schema,
        response_schema=response_schema,
    )


def _merge_parameters(
    shared_parameters: list[dict[str, Any]], operation_parameters: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    merged: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for parameter in shared_parameters + operation_parameters:
        # path 级和 operation 级出现同名参数时，以 operation 级定义为准。
        identity = (parameter.get("name"), parameter.get("in"))
        merged[identity] = parameter
    return list(merged.values())


def _build_request_schema(
    document: dict[str, Any],
    resolver: SchemaResolver,
    operation: dict[str, Any],
    merged_parameters: list[dict[str, Any]],
) -> dict[str, Any]:
    body_schema = _extract_request_body_schema(document, resolver, operation, merged_parameters)
    parameter_schema = _build_parameter_schema(resolver, merged_parameters)

    if body_schema and not parameter_schema:
        return body_schema
    if parameter_schema and not body_schema:
        return parameter_schema
    if not body_schema and not parameter_schema:
        return {}

    # 既有 body 又有 query/path/header 时，尽量合并成一个请求对象，
    # 这样调用侧只需要消费一个请求 DTO。
    if _is_object_like(body_schema):
        return _merge_object_schemas(body_schema, parameter_schema)

    return {
        "type": "object",
        "properties": {
            **parameter_schema.get("properties", {}),
            "body": body_schema,
        },
        "required": sorted(
            set(parameter_schema.get("required", []))
            | ({"body"} if body_schema else set())
        ),
    }


def _build_parameter_schema(
    resolver: SchemaResolver, merged_parameters: list[dict[str, Any]]
) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []

    for raw_parameter in merged_parameters:
        parameter = resolver.resolve_node(raw_parameter)
        location = parameter.get("in")
        if location in {"body"}:
            continue

        schema = _extract_parameter_schema(resolver, parameter)
        properties[parameter["name"]] = schema
        if parameter.get("required", False):
            required.append(parameter["name"])

    if not properties:
        return {}

    result: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        result["required"] = sorted(set(required))
    return result


def _extract_parameter_schema(
    resolver: SchemaResolver, parameter: dict[str, Any]
) -> dict[str, Any]:
    if "schema" in parameter:
        schema = resolver.normalize_schema(parameter["schema"])
        if parameter.get("description") and not schema.get("description"):
            schema["description"] = parameter["description"]
        if parameter.get("deprecated") and "deprecated" not in schema:
            schema["deprecated"] = parameter["deprecated"]
        return schema

    schema: dict[str, Any] = {}
    for key in ("type", "format", "enum", "items", "default", "nullable", "deprecated"):
        if key in parameter:
            schema[key] = parameter[key]
    if "items" in schema and isinstance(schema["items"], dict):
        schema["items"] = resolver.normalize_schema(schema["items"])
    if "description" in parameter:
        schema["description"] = parameter["description"]
    return resolver.normalize_schema(schema)


def _extract_request_body_schema(
    document: dict[str, Any],
    resolver: SchemaResolver,
    operation: dict[str, Any],
    merged_parameters: list[dict[str, Any]],
) -> dict[str, Any]:
    request_body = operation.get("requestBody")
    if request_body:
        resolved = resolver.resolve_node(request_body)
        content_type, media_type = _select_media_type(resolved.get("content", {}))
        if content_type and media_type:
            schema = resolver.normalize_schema(media_type.get("schema"))
            if resolved.get("description") and not schema.get("description"):
                schema["description"] = resolved.get("description")
            return schema

    if document.get("swagger", "").startswith("2."):
        # Swagger 2.0 通过 in=body 参数表达请求体。
        for raw_parameter in merged_parameters:
            parameter = resolver.resolve_node(raw_parameter)
            if parameter.get("in") == "body":
                schema = resolver.normalize_schema(parameter.get("schema"))
                if parameter.get("description") and not schema.get("description"):
                    schema["description"] = parameter.get("description")
                return schema
    return {}


def _extract_primary_response_schema(
    document: dict[str, Any],
    resolver: SchemaResolver,
    operation: dict[str, Any],
    path: str,
    method: str,
    warnings: list[str],
) -> dict[str, Any]:
    raw_responses = operation.get("responses", {})
    produces = operation.get("produces") or document.get("produces") or ["application/json"]
    candidates: list[tuple[str, dict[str, Any]]] = []

    for status_code, raw_response in raw_responses.items():
        response = resolver.resolve_node(raw_response)
        if document.get("swagger", "").startswith("2."):
            schema = resolver.normalize_schema(response.get("schema"))
        else:
            _, media_type = _select_media_type(response.get("content", {}))
            schema = resolver.normalize_schema(media_type.get("schema")) if media_type else {}

        if schema:
            candidates.append((str(status_code), schema))

    if not candidates:
        return {}

    selected_status, selected_schema = sorted(
        candidates,
        key=lambda item: _response_sort_key(item[0]),
    )[0]

    ignored_statuses = [status for status, _ in candidates if status != selected_status]
    if ignored_statuses:
        warnings.append(
            (
                f"{method.upper()} {path} 命中了多个可转换响应状态码，"
                f"已优先选择 {selected_status}，忽略 {', '.join(sorted(ignored_statuses))}"
            )
        )

    if document.get("swagger", "").startswith("2.") and not produces:
        warnings.append(f"{method.upper()} {path} 缺少 produces，已按 application/json 处理")
    return selected_schema


def _select_media_type(content: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    if not content:
        return None, None
    for preferred in PREFERRED_CONTENT_TYPES:
        if preferred in content:
            return preferred, content[preferred]
    first_key = next(iter(content))
    return first_key, content[first_key]


def _merge_object_schemas(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "type": "object",
        "properties": {
            **primary.get("properties", {}),
            **secondary.get("properties", {}),
        },
    }
    required = sorted(set(primary.get("required", [])) | set(secondary.get("required", [])))
    if required:
        merged["required"] = required
    if primary.get("description"):
        merged["description"] = primary["description"]
    return merged


def _is_object_like(schema: dict[str, Any]) -> bool:
    schema_type = schema.get("type")
    return schema_type == "object" or "properties" in schema


def _response_sort_key(status_code: str) -> tuple[int, int, str]:
    if status_code == "200":
        return 0, 200, status_code
    if status_code.isdigit() and status_code.startswith("2"):
        return 1, int(status_code), status_code
    if status_code == "default":
        return 2, 0, status_code
    return 3, 999, status_code


def _build_operation_id(path: str, method: str, operation: dict[str, Any]) -> str:
    operation_id = operation.get("operationId")
    if operation_id:
        return operation_id

    tokens: list[str] = [method]
    for segment in path.strip("/").split("/"):
        if not segment:
            continue
        if segment.startswith("{") and segment.endswith("}"):
            tokens.append("by")
            tokens.append(segment[1:-1])
        else:
            tokens.append(segment)
    return "_".join(tokens) or method
