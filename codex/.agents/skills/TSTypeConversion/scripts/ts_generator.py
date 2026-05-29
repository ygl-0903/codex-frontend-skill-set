from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from .models import ApiTypeTask, ParsedTypeBundle, SharedSchemaUsage, TypeScriptRenderOptions
from .schema_resolver import TS_COMPOSITION_KEY, TS_REF_NAME_KEY


@dataclass(slots=True)
class _RenderContext:
    options: TypeScriptRenderOptions
    shared_schema_map: dict[str, SharedSchemaUsage]
    shared_name_map: dict[str, str]
    task_request_names: dict[tuple[str, str], str]
    task_response_names: dict[tuple[str, str], str]
    base_like_refs: set[str]
    shared_declarations: list[str] = field(default_factory=list)
    emitted_shared_names: set[str] = field(default_factory=set)


def generate_typescript(
    bundle: ParsedTypeBundle, options: TypeScriptRenderOptions | None = None
) -> str:
    """将解析后的 DTO 任务集合渲染为 TypeScript 类型定义。"""
    render_options = options or TypeScriptRenderOptions()
    context = _build_render_context(bundle, render_options)
    sections: list[str] = []

    for task in bundle.tasks:
        identity = _task_identity(task)
        if task.request_schema:
            sections.append(
                _render_named_schema(
                    context.task_request_names[identity],
                    task.request_schema,
                    render_options,
                    context=context,
                    comment_lines=_build_request_comment_lines(task),
                )
            )
        if task.response_schema:
            sections.append(_render_response_schema(task, context))

    ordered_sections = context.shared_declarations + [section for section in sections if section]
    return "\n\n".join(section for section in ordered_sections if section).strip() + "\n"


def _build_render_context(
    bundle: ParsedTypeBundle, options: TypeScriptRenderOptions
) -> _RenderContext:
    prefix = "I" if options.style == "interface" else "T"
    used_names: set[str] = set()

    shared_name_map: dict[str, str] = {}
    base_like_refs = {
        usage.source_name
        for usage in bundle.shared_schemas
        if _is_base_like(usage.resolved_schema, usage.source_name)
    }
    for usage in bundle.shared_schemas:
        core_name = _build_shared_core_name(usage.source_name, base_like_refs)
        shared_name_map[usage.source_name] = _ensure_unique_name(prefix + core_name, used_names)

    task_request_names: dict[tuple[str, str], str] = {}
    task_response_names: dict[tuple[str, str], str] = {}
    for task in bundle.tasks:
        identity = _task_identity(task)
        if task.request_schema:
            request_core = _build_request_core_name(task)
            task_request_names[identity] = _ensure_unique_name(prefix + request_core, used_names)
        if task.response_schema:
            response_core = _build_response_core_name(task)
            task_response_names[identity] = _ensure_unique_name(prefix + response_core, used_names)

    shared_schema_map = {usage.source_name: usage for usage in bundle.shared_schemas}
    return _RenderContext(
        options=options,
        shared_schema_map=shared_schema_map,
        shared_name_map=shared_name_map,
        task_request_names=task_request_names,
        task_response_names=task_response_names,
        base_like_refs=base_like_refs,
    )


def _render_response_schema(task: ApiTypeTask, context: _RenderContext) -> str:
    identity = _task_identity(task)
    name = context.task_response_names[identity]
    generic_base = _match_generic_base_response(task.response_schema)

    if not generic_base or not context.options.prefer_generic_base:
        return _render_named_schema(
            name,
            task.response_schema,
            context.options,
            context=context,
            comment_lines=_build_response_comment_lines(task),
        )

    base_ref_name, payload_schema, extension_schema = generic_base
    base_export_name = _ensure_ref_declaration_by_name(base_ref_name, context)
    if not base_export_name:
        return _render_named_schema(
            name,
            task.response_schema,
            context.options,
            context=context,
            comment_lines=_build_response_comment_lines(task),
        )

    payload_type = _render_schema(
        payload_schema,
        context.options,
        level=0,
        context=context,
        prefer_reference_names=True,
    )
    base_with_generic = f"{base_export_name}<{payload_type}>"
    export_prefix = "export " if context.options.export else ""
    comment = None
    if context.options.include_comments:
        comment = _build_jsdoc(_build_response_comment_lines(task))

    if context.options.style == "interface":
        body = _render_object_schema(extension_schema, context.options, 0, context=context)
        declaration = f"{export_prefix}interface {name} extends {base_with_generic} {body}"
    else:
        if _is_empty_object_schema(extension_schema):
            declaration = f"{export_prefix}type {name} = {base_with_generic};"
        else:
            body = _render_object_schema(extension_schema, context.options, 0, context=context)
            declaration = f"{export_prefix}type {name} = {base_with_generic} & {body};"
    return _prepend_comment(declaration, comment)


def _render_named_schema(
    name: str,
    schema: dict[str, Any],
    options: TypeScriptRenderOptions,
    *,
    context: _RenderContext,
    comment_lines: list[str] | None = None,
) -> str:
    export_prefix = "export " if options.export else ""
    composition = schema.get(TS_COMPOSITION_KEY, {})

    if options.style == "interface" and composition.get("kind") == "extends":
        declaration = _render_extends_interface(name, schema, options, context=context)
    else:
        can_be_interface = _can_render_as_interface(schema)
        body = _render_schema(
            schema,
            options,
            level=0,
            context=context,
            prefer_reference_names=False,
        )
        if options.style == "interface" and can_be_interface and body.lstrip().startswith("{"):
            declaration = f"{export_prefix}interface {name} {body}"
        else:
            declaration = f"{export_prefix}type {name} = {body};"

    comment = None
    if options.include_comments:
        comment = _build_jsdoc(
            [line for line in (comment_lines or []) if line],
            deprecated=bool(schema.get("deprecated", False)),
        )
    return _prepend_comment(declaration, comment)


def _render_shared_schema(
    usage: SharedSchemaUsage, export_name: str, context: _RenderContext
) -> str:
    if usage.source_name in context.base_like_refs and context.options.prefer_generic_base:
        return _render_generic_base_declaration(export_name, usage.resolved_schema, context)
    return _render_named_schema(
        export_name,
        usage.resolved_schema,
        context.options,
        context=context,
        comment_lines=_build_shared_comment_lines(usage),
    )


def _render_generic_base_declaration(
    export_name: str,
    schema: dict[str, Any],
    context: _RenderContext,
) -> str:
    base_schema = _strip_data_property(schema)
    export_prefix = "export " if context.options.export else ""
    body = _render_object_schema(base_schema, context.options, 0, context=context)
    generic_body = _append_generic_data_property(body)
    comment = None
    if context.options.include_comments:
        comment = _build_jsdoc(_build_shared_comment_lines_from_schema(schema))

    if context.options.style == "interface":
        declaration = f"{export_prefix}interface {export_name}<T = any> {generic_body}"
    else:
        declaration = f"{export_prefix}type {export_name}<T = any> = {generic_body};"
    return _prepend_comment(declaration, comment)


def _append_generic_data_property(rendered_object: str) -> str:
    lines = rendered_object.splitlines()
    if len(lines) < 2:
        return "{\n  data?: T;\n}"
    lines.insert(-1, "  data?: T;")
    return "\n".join(lines)


def _strip_data_property(schema: dict[str, Any]) -> dict[str, Any]:
    base = {
        key: value
        for key, value in schema.items()
        if key not in {"properties", "required"}
    }
    properties = dict(schema.get("properties", {}))
    properties.pop("data", None)
    required = [item for item in schema.get("required", []) if item != "data"]
    if properties:
        base["properties"] = properties
    if required:
        base["required"] = required
    return base


def _render_schema(
    schema: dict[str, Any],
    options: TypeScriptRenderOptions,
    level: int = 0,
    *,
    context: _RenderContext,
    prefer_reference_names: bool = False,
) -> str:
    if not schema:
        return "unknown"

    composition = schema.get(TS_COMPOSITION_KEY, {})
    if composition:
        return _render_composition_schema(
            schema,
            options,
            level=level,
            context=context,
        )

    if prefer_reference_names and schema.get(TS_REF_NAME_KEY):
        export_name = _ensure_ref_declaration(schema, context)
        if export_name:
            return export_name

    if "enum" in schema:
        values = " | ".join(_literal(value) for value in schema["enum"])
        return values or "never"

    if "oneOf" in schema:
        return " | ".join(
            _render_schema(
                item,
                options,
                level,
                context=context,
                prefer_reference_names=True,
            )
            for item in schema["oneOf"]
        )

    if "anyOf" in schema:
        return " | ".join(
            _render_schema(
                item,
                options,
                level,
                context=context,
                prefer_reference_names=True,
            )
            for item in schema["anyOf"]
        )

    if schema.get("nullable"):
        non_null_schema = dict(schema)
        non_null_schema.pop("nullable", None)
        return (
            f"{_render_schema(non_null_schema, options, level, context=context, prefer_reference_names=prefer_reference_names)} | null"
        )

    schema_type = schema.get("type")
    if schema_type == "array":
        item_schema = schema.get("items", {})
        return (
            f"Array<{_render_schema(item_schema, options, level, context=context, prefer_reference_names=prefer_reference_names)}>"
        )

    if schema_type == "object" or "properties" in schema or "additionalProperties" in schema:
        return _render_object_schema(schema, options, level, context=context)

    return _render_scalar_schema(schema_type, schema)


def _render_object_schema(
    schema: dict[str, Any],
    options: TypeScriptRenderOptions,
    level: int,
    *,
    context: _RenderContext,
) -> str:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    indent = "  " * (level + 1)
    closing_indent = "  " * level
    lines = ["{"]

    for name, child_schema in properties.items():
        optional_marker = "" if name in required else "?"
        rendered_child = _render_schema(
            child_schema,
            options,
            level + 1,
            context=context,
            prefer_reference_names=True,
        )
        if options.include_comments:
            # 字段注释直接读取字段 schema 自身的说明，便于保留 swagger 元信息。
            comment = _build_schema_comment(child_schema, indent=indent)
            if comment:
                lines.append(comment)
        lines.append(f"{indent}{_safe_property_name(name)}{optional_marker}: {rendered_child};")

    additional_properties = schema.get("additionalProperties")
    if additional_properties is True:
        lines.append(f"{indent}[key: string]: unknown;")
    elif isinstance(additional_properties, dict):
        rendered_value = _render_schema(
            additional_properties,
            options,
            level + 1,
            context=context,
            prefer_reference_names=True,
        )
        lines.append(f"{indent}[key: string]: {rendered_value};")

    lines.append(f"{closing_indent}}}")
    return "\n".join(lines)


def _render_scalar_schema(schema_type: str | None, schema: dict[str, Any]) -> str:
    schema_format = schema.get("format")
    if schema_type == "file":
        return "Blob"
    if schema_type == "string" and schema_format in {"binary", "base64"}:
        return "Blob"
    if schema_type in {"integer", "number"}:
        return "number"
    if schema_type == "boolean":
        return "boolean"
    if schema_type == "string":
        return "string"
    if schema_type == "null":
        return "null"
    if schema_type == "object":
        return "Record<string, unknown>"
    if "default" in schema:
        return _literal(schema["default"])
    return "unknown"


def _render_composition_schema(
    schema: dict[str, Any],
    options: TypeScriptRenderOptions,
    *,
    level: int,
    context: _RenderContext,
) -> str:
    composition = schema.get(TS_COMPOSITION_KEY, {})
    kind = composition.get("kind")
    if kind == "extends":
        members = [composition.get("base"), *composition.get("extensions", [])]
        return " & ".join(
            _render_schema(
                member,
                options,
                level,
                context=context,
                prefer_reference_names=True,
            )
            for member in members
            if member
        )
    if kind == "intersection":
        return " & ".join(
            _render_schema(
                member,
                options,
                level,
                context=context,
                prefer_reference_names=True,
            )
            for member in composition.get("members", [])
            if member
        )
    return "unknown"


def _render_extends_interface(
    name: str,
    schema: dict[str, Any],
    options: TypeScriptRenderOptions,
    *,
    context: _RenderContext,
) -> str:
    export_prefix = "export " if options.export else ""
    composition = schema.get(TS_COMPOSITION_KEY, {})
    base_schema = composition.get("base", {})
    base_name = _ensure_ref_declaration(base_schema, context) or _render_schema(
        base_schema,
        options,
        0,
        context=context,
        prefer_reference_names=True,
    )
    extension_schema = _merge_extension_members(composition.get("extensions", []))
    body = _render_object_schema(extension_schema, options, 0, context=context)
    return f"{export_prefix}interface {name} extends {base_name} {body}"


def _merge_extension_members(members: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    for member in members:
        if not member:
            continue
        member_composition = member.get(TS_COMPOSITION_KEY, {})
        if member_composition.get("kind") == "intersection":
            merged = _merge_extension_members([merged, *member_composition.get("members", [])])
            continue
        if member_composition.get("kind") == "extends":
            merged = _merge_extension_members([merged, *member_composition.get("extensions", [])])
            continue
        if "properties" in member:
            merged["properties"].update(member.get("properties", {}))
        if "required" in member:
            merged["required"] = sorted(set(merged["required"]) | set(member["required"]))
        additional_properties = member.get("additionalProperties")
        if additional_properties is not None:
            merged["additionalProperties"] = additional_properties
        for key in ("description", "deprecated"):
            if key in member and key not in merged:
                merged[key] = member[key]
    if not merged["required"]:
        merged.pop("required")
    if not merged["properties"]:
        merged.pop("properties")
    return merged


def _ensure_ref_declaration(schema: dict[str, Any], context: _RenderContext) -> str | None:
    raw_name = schema.get(TS_REF_NAME_KEY)
    if not raw_name:
        return None
    return _ensure_ref_declaration_by_name(raw_name, context)


def _ensure_ref_declaration_by_name(raw_name: str, context: _RenderContext) -> str | None:
    export_name = context.shared_name_map.get(raw_name)
    usage = context.shared_schema_map.get(raw_name)
    if not export_name or not usage:
        return None
    if export_name in context.emitted_shared_names:
        return export_name

    declaration = _render_shared_schema(usage, export_name, context)
    context.shared_declarations.append(declaration)
    context.emitted_shared_names.add(export_name)
    return export_name


def _can_render_as_interface(schema: dict[str, Any]) -> bool:
    composition = schema.get(TS_COMPOSITION_KEY, {})
    if composition.get("kind") == "extends":
        return True
    schema_type = schema.get("type")
    return schema_type == "object" or "properties" in schema


def _build_request_core_name(task: ApiTypeTask) -> str:
    ref_name = task.request_schema.get(TS_REF_NAME_KEY)
    if ref_name:
        return _normalize_request_name(ref_name)
    return f"{_derive_operation_name(task)}Req"


def _build_response_core_name(task: ApiTypeTask) -> str:
    return f"{_derive_operation_name(task)}Resp"


def _build_shared_core_name(raw_name: str, base_like_refs: set[str]) -> str:
    if raw_name in base_like_refs:
        return "Base"
    pascal = _to_pascal_case(raw_name)
    if pascal.endswith("VO"):
        return pascal
    if pascal.endswith(("Req", "Resp", "Base")):
        return pascal
    return f"{pascal}VO"


def _normalize_request_name(raw_name: str) -> str:
    pascal = _to_pascal_case(raw_name)
    if pascal.endswith("RequestBody"):
        pascal = f"{pascal[:-11]}Req"
    elif pascal.endswith("Request"):
        pascal = f"{pascal[:-7]}Req"
    elif not pascal.endswith("Req"):
        pascal = f"{pascal}Req"
    return pascal


def _derive_operation_name(task: ApiTypeTask) -> str:
    raw_operation_name = _to_pascal_case(task.operation_id)
    stripped_operation_name = _strip_http_verb_prefix(raw_operation_name)
    path_name = _build_path_name(task.path)
    if stripped_operation_name and path_name:
        if (
            path_name.lower().endswith(stripped_operation_name.lower())
            and path_name != stripped_operation_name
        ):
            return path_name
        return raw_operation_name
    return raw_operation_name or path_name or "AnonymousOperation"


def _build_path_name(path: str) -> str:
    tokens: list[str] = []
    for segment in path.strip("/").split("/"):
        if not segment:
            continue
        if segment.startswith("{") and segment.endswith("}"):
            tokens.append("By")
            tokens.append(_to_pascal_case(segment[1:-1]))
        else:
            tokens.append(_to_pascal_case(segment))
    return "".join(tokens) or "AnonymousOperation"


def _strip_http_verb_prefix(value: str) -> str:
    stripped = re.sub(
        r"^(Get|Post|Put|Patch|Delete|Create|Update|List|Fetch|Query|Remove)",
        "",
        value,
    )
    return stripped or value


def _ensure_unique_name(name: str, used_names: set[str]) -> str:
    if name not in used_names:
        used_names.add(name)
        return name
    index = 2
    while f"{name}{index}" in used_names:
        index += 1
    unique_name = f"{name}{index}"
    used_names.add(unique_name)
    return unique_name


def _task_identity(task: ApiTypeTask) -> tuple[str, str]:
    return task.method, task.path


def _build_request_comment_lines(task: ApiTypeTask) -> list[str]:
    lines: list[str] = []
    if task.summary:
        lines.append(f"{task.summary}请求参数")
    else:
        lines.append(f"{task.method.upper()} {task.path} 请求参数")
    lines.extend(_split_comment_text(task.request_schema.get("description")))
    return lines


def _build_response_comment_lines(task: ApiTypeTask) -> list[str]:
    lines: list[str] = []
    if task.summary:
        lines.append(f"{task.summary}响应参数")
    else:
        lines.append(f"{task.method.upper()} {task.path} 响应参数")
    lines.extend(_split_comment_text(task.response_schema.get("description")))
    return lines


def _build_shared_comment_lines(usage: SharedSchemaUsage) -> list[str]:
    return _build_shared_comment_lines_from_schema(usage.resolved_schema)


def _build_shared_comment_lines_from_schema(schema: dict[str, Any]) -> list[str]:
    return _split_comment_text(schema.get("description"))


def _match_generic_base_response(
    schema: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any]] | None:
    composition = schema.get(TS_COMPOSITION_KEY, {})
    if composition.get("kind") != "extends":
        return None

    base_schema = composition.get("base") or {}
    base_ref_name = base_schema.get(TS_REF_NAME_KEY)
    if not base_ref_name or not _is_base_like(base_schema, base_ref_name):
        return None

    extension_schema = _merge_extension_members(composition.get("extensions", []))
    properties = dict(extension_schema.get("properties", {}))
    payload_schema = properties.pop("data", None)
    if not payload_schema:
        return None

    remaining_required = [name for name in extension_schema.get("required", []) if name != "data"]
    remaining_extension = {
        key: value
        for key, value in extension_schema.items()
        if key not in {"properties", "required"}
    }
    if properties:
        remaining_extension["properties"] = properties
    if remaining_required:
        remaining_extension["required"] = remaining_required
    if "type" not in remaining_extension:
        remaining_extension["type"] = "object"
    return base_ref_name, payload_schema, remaining_extension


def _is_base_like(schema: dict[str, Any], raw_name: str) -> bool:
    if _to_pascal_case(raw_name) == "Base":
        return True
    properties = schema.get("properties", {})
    if not properties:
        return False
    stable_fields = {"code", "msg", "success"}
    return stable_fields.issubset(set(properties))


def _is_empty_object_schema(schema: dict[str, Any]) -> bool:
    return not schema.get("properties") and "additionalProperties" not in schema


def _literal(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def _safe_property_name(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return f'"{name}"'


def _to_pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    normalized = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return normalized or "AnonymousOperation"


def _build_schema_comment(schema: dict[str, Any], *, indent: str) -> str | None:
    lines = _split_comment_text(schema.get("description"))
    schema_format = schema.get("format")
    if schema_format:
        lines.append(f"Format: {schema_format}")
    if "default" in schema:
        lines.append(f"Default: {_literal_for_comment(schema['default'])}")
    if schema.get("enum"):
        allowed_values = ", ".join(_literal_for_comment(value) for value in schema["enum"])
        lines.append(f"Allowed values: {allowed_values}")
    return _build_jsdoc(
        lines,
        deprecated=bool(schema.get("deprecated", False)),
        indent=indent,
    )


def _build_jsdoc(
    lines: list[str],
    *,
    deprecated: bool = False,
    indent: str = "",
) -> str | None:
    normalized_lines = [line for raw in lines for line in _split_comment_text(raw) if line]
    if deprecated:
        normalized_lines.append("@deprecated")
    if not normalized_lines:
        return None
    if len(normalized_lines) == 1 and normalized_lines[0] != "@deprecated":
        return f"{indent}/** {_escape_comment_text(normalized_lines[0])} */"

    block = [f"{indent}/**"]
    for line in normalized_lines:
        block.append(f"{indent} * {_escape_comment_text(line)}")
    block.append(f"{indent} */")
    return "\n".join(block)


def _prepend_comment(declaration: str, comment: str | None) -> str:
    if not comment:
        return declaration
    return f"{comment}\n{declaration}"


def _split_comment_text(text: str | None) -> list[str]:
    if not text:
        return []
    return [line.strip() for line in str(text).splitlines() if line.strip()]


def _escape_comment_text(text: str) -> str:
    return text.replace("*/", "*\\/")


def _literal_for_comment(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)
