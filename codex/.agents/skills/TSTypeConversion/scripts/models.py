from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SchemaDict = dict[str, Any]
TypeStyle = Literal["interface", "type"]
SharedSchemaKind = Literal["base", "vo", "model"]


@dataclass(slots=True)
class ApiTypeTask:
    """描述一个接口最终需要生成的请求/响应类型。"""

    path: str
    method: str
    operation_id: str
    tags: list[str] = field(default_factory=list)
    summary: str | None = None
    description: str | None = None
    request_schema: SchemaDict = field(default_factory=dict)
    response_schema: SchemaDict = field(default_factory=dict)
    request_type_name: str | None = None
    response_type_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SharedSchemaUsage:
    """记录请求/响应中依赖到的共享 schema。"""

    source_name: str
    resolved_schema: SchemaDict = field(default_factory=dict)
    export_type_name: str | None = None
    kind: SharedSchemaKind = "model"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ParsedTypeBundle:
    """一次文档解析后的完整类型任务集合。"""

    tasks: list[ApiTypeTask] = field(default_factory=list)
    shared_schemas: list[SharedSchemaUsage] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tasks": [task.to_dict() for task in self.tasks],
            "shared_schemas": [schema.to_dict() for schema in self.shared_schemas],
            "warnings": list(self.warnings),
        }


@dataclass(slots=True)
class TypeScriptRenderOptions:
    style: TypeStyle = "interface"
    export: bool = True
    include_comments: bool = True
    prefer_generic_base: bool = True
