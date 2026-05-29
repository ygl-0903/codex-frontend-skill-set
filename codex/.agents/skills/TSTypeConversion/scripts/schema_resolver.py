from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import SharedSchemaUsage


TS_REF_KEY = "__ts_ref"
TS_REF_NAME_KEY = "__ts_ref_name"
TS_COMPOSITION_KEY = "__ts_composition"


class SchemaResolver:
    def __init__(self, document: dict[str, Any]):
        self.document = document

    def resolve_node(self, node: Any) -> Any:
        if isinstance(node, list):
            return [self.resolve_node(item) for item in node]
        if not isinstance(node, dict):
            return node

        current = deepcopy(node)
        if "$ref" in current:
            # 先展开 $ref，再把当前节点上的额外字段覆盖回去，避免丢失局部元信息。
            ref = current["$ref"]
            target = self._resolve_ref(ref)
            merged = self._merge_dicts(target, {k: v for k, v in current.items() if k != "$ref"})
            merged[TS_REF_KEY] = ref
            merged[TS_REF_NAME_KEY] = ref.rsplit("/", 1)[-1]
            return self.resolve_node(merged)

        resolved: dict[str, Any] = {}
        for key, value in current.items():
            if key in {"properties", "definitions", "schemas"} and isinstance(value, dict):
                resolved[key] = {k: self.resolve_node(v) for k, v in value.items()}
            elif key in {"items", "additionalProperties", "schema"}:
                resolved[key] = self.resolve_node(value)
            elif key in {"allOf", "oneOf", "anyOf"} and isinstance(value, list):
                resolved[key] = [self.resolve_node(item) for item in value]
            elif isinstance(value, dict):
                resolved[key] = self.resolve_node(value)
            elif isinstance(value, list):
                resolved[key] = [self.resolve_node(item) for item in value]
            else:
                resolved[key] = value
        return resolved

    def normalize_schema(self, schema: dict[str, Any] | None) -> dict[str, Any]:
        if not schema:
            return {}

        resolved = self.resolve_node(schema)
        if "allOf" in resolved:
            # allOf 不能一律拍平，否则后续无法真实输出 extends / &。
            return self._normalize_all_of(resolved)

        if "properties" in resolved:
            resolved["properties"] = {
                name: self.normalize_schema(child)
                for name, child in resolved["properties"].items()
            }
        if "items" in resolved and isinstance(resolved["items"], dict):
            resolved["items"] = self.normalize_schema(resolved["items"])
        if "additionalProperties" in resolved and isinstance(resolved["additionalProperties"], dict):
            resolved["additionalProperties"] = self.normalize_schema(
                resolved["additionalProperties"]
            )
        if "oneOf" in resolved:
            resolved["oneOf"] = [self.normalize_schema(item) for item in resolved["oneOf"]]
        if "anyOf" in resolved:
            resolved["anyOf"] = [self.normalize_schema(item) for item in resolved["anyOf"]]
        return resolved

    def collect_shared_schemas(
        self, root_schemas: list[dict[str, Any]]
    ) -> list[SharedSchemaUsage]:
        """递归收集请求/响应内部引用到的共享 schema。"""
        collected: dict[str, dict[str, Any]] = {}

        for schema in root_schemas:
            self._collect_named_schemas(schema, collected, include_current=False)

        usages: list[SharedSchemaUsage] = []
        for source_name in sorted(collected):
            usages.append(
                SharedSchemaUsage(
                    source_name=source_name,
                    resolved_schema=deepcopy(collected[source_name]),
                )
            )
        return usages

    def _resolve_ref(self, ref: str) -> dict[str, Any]:
        if not ref.startswith("#/"):
            raise ValueError(f"Only local refs are supported: {ref}")
        current: Any = self.document
        for part in ref[2:].split("/"):
            current = current[part]
        if not isinstance(current, dict):
            raise ValueError(f"Ref does not resolve to an object: {ref}")
        return deepcopy(current)

    def _normalize_all_of(self, schema: dict[str, Any]) -> dict[str, Any]:
        parent_schema = {
            k: v
            for k, v in schema.items()
            if k not in {"allOf", TS_REF_KEY, TS_REF_NAME_KEY}
        }
        normalized_members = [self.normalize_schema(item) for item in schema.get("allOf", [])]
        normalized_parent = self.normalize_schema(parent_schema) if parent_schema else {}

        members = [member for member in normalized_members if member]
        if normalized_parent:
            members.append(normalized_parent)

        result = {
            k: deepcopy(v)
            for k, v in schema.items()
            if k
            not in {
                "allOf",
                "properties",
                "required",
                "type",
                "additionalProperties",
                TS_REF_KEY,
                TS_REF_NAME_KEY,
            }
        }
        result["type"] = "object"

        base_candidate = self._pick_extends_base(members)
        if base_candidate is not None:
            extensions = [member for member in members if member is not base_candidate]
            result[TS_COMPOSITION_KEY] = {
                "kind": "extends",
                "base": base_candidate,
                "extensions": extensions,
            }
        else:
            result[TS_COMPOSITION_KEY] = {
                "kind": "intersection",
                "members": members,
            }
        return result

    def strip_internal_metadata(self, schema: Any) -> Any:
        if isinstance(schema, list):
            return [self.strip_internal_metadata(item) for item in schema]
        if not isinstance(schema, dict):
            return schema

        cleaned: dict[str, Any] = {}
        for key, value in schema.items():
            if key in {TS_REF_KEY, TS_REF_NAME_KEY}:
                continue
            if key == TS_COMPOSITION_KEY and isinstance(value, dict):
                composition = dict(value)
                if "base" in composition:
                    composition["base"] = self.strip_internal_metadata(composition["base"])
                if "extensions" in composition:
                    composition["extensions"] = self.strip_internal_metadata(composition["extensions"])
                if "members" in composition:
                    composition["members"] = self.strip_internal_metadata(composition["members"])
                cleaned[key] = composition
                continue
            cleaned[key] = self.strip_internal_metadata(value)
        return cleaned

    def _pick_extends_base(self, members: list[dict[str, Any]]) -> dict[str, Any] | None:
        ref_members = [
            member
            for member in members
            if member.get(TS_REF_NAME_KEY) and self._is_object_like(member)
        ]
        if len(ref_members) != 1:
            return None
        if not all(self._is_object_like(member) for member in members):
            return None
        if any(member.get(TS_COMPOSITION_KEY, {}).get("kind") == "intersection" for member in members):
            return None
        return ref_members[0]

    def _is_object_like(self, schema: dict[str, Any]) -> bool:
        composition_kind = schema.get(TS_COMPOSITION_KEY, {}).get("kind")
        if composition_kind in {"extends", "intersection"}:
            return True
        schema_type = schema.get("type")
        return schema_type in {None, "object"} or "properties" in schema

    def _merge_dicts(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # 深度合并用于处理 $ref 展开后和局部覆盖字段同时存在的情况。
                merged[key] = self._merge_dicts(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged

    def _collect_named_schemas(
        self,
        schema: Any,
        collected: dict[str, dict[str, Any]],
        *,
        include_current: bool,
    ) -> None:
        if isinstance(schema, list):
            for item in schema:
                self._collect_named_schemas(item, collected, include_current=True)
            return
        if not isinstance(schema, dict):
            return

        ref_name = schema.get(TS_REF_NAME_KEY)
        if include_current and ref_name and ref_name not in collected:
            collected[ref_name] = schema

        for key, value in schema.items():
            if key == TS_COMPOSITION_KEY and isinstance(value, dict):
                for nested_key in ("base", "extensions", "members"):
                    if nested_key in value:
                        self._collect_named_schemas(
                            value[nested_key],
                            collected,
                            include_current=True,
                        )
                continue
            if isinstance(value, dict):
                self._collect_named_schemas(value, collected, include_current=True)
            elif isinstance(value, list):
                for item in value:
                    self._collect_named_schemas(item, collected, include_current=True)
