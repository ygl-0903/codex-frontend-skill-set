from __future__ import annotations

from langchain_core.tools import StructuredTool

from .loader import load_openapi_document
from .models import TypeScriptRenderOptions
from .output_config import resolve_output_config
from .parser import parse_openapi_document
from .suggestion_builder import (
    build_routed_suggestions,
    build_single_file_suggestion,
    render_suggestions_json,
)
from .ts_generator import generate_typescript


def convert_openapi_to_typescript(
    source: str,
    style: str = "interface",
    output_mode: str = "typescript",
    output_path: str | None = None,
    output_config_path: str | None = None,
    filter_tags: list[str] | None = None,
    filter_operation_ids: list[str] | None = None,
    filter_paths: list[str] | None = None,
) -> str:
    document = load_openapi_document(source)
    bundle = parse_openapi_document(document)

    bundle = _filter_bundle(
        bundle=bundle,
        include_tags=set(filter_tags or []),
        operation_ids=set(filter_operation_ids or []),
        paths=set(filter_paths or []),
    )
    render_options = TypeScriptRenderOptions(
        style=style if style in {"interface", "type"} else "interface",
    )

    if output_mode == "suggest_json":
        output_config = resolve_output_config(output_config_path)
        if output_config:
            suggestions = build_routed_suggestions(
                bundle,
                output_config,
                render_options,
                slice_bundle_fn=_slice_bundle,
            )
        else:
            if not output_path:
                raise ValueError(
                    "suggest_json 模式下需要 output_path 或可解析的 output_config_path"
                )
            suggestions = [build_single_file_suggestion(bundle, _to_path(output_path), render_options)]
        return render_suggestions_json(suggestions)

    return generate_typescript(bundle, render_options)


def _filter_bundle(bundle, include_tags: set[str], operation_ids: set[str], paths: set[str]):
    filtered_tasks = bundle.tasks
    if include_tags:
        filtered_tasks = [
            task for task in filtered_tasks if include_tags.intersection(set(task.tags))
        ]
    if operation_ids:
        filtered_tasks = [task for task in filtered_tasks if task.operation_id in operation_ids]
    if paths:
        filtered_tasks = [task for task in filtered_tasks if task.path in paths]

    reachable_shared_names = _collect_reachable_shared_names(filtered_tasks)
    filtered_shared = [
        shared
        for shared in bundle.shared_schemas
        if shared.source_name in reachable_shared_names
    ]
    bundle.tasks = filtered_tasks
    bundle.shared_schemas = filtered_shared
    return bundle


def _slice_bundle(bundle, tasks):
    reachable_shared_names = _collect_reachable_shared_names(tasks)
    filtered_shared = [
        shared
        for shared in bundle.shared_schemas
        if shared.source_name in reachable_shared_names
    ]
    bundle_type = type(bundle)
    return bundle_type(
        tasks=list(tasks),
        shared_schemas=filtered_shared,
        warnings=bundle.warnings,
    )


def _collect_reachable_shared_names(tasks) -> set[str]:
    reachable: set[str] = set()
    for task in tasks:
        _collect_ref_names(task.request_schema, reachable, include_current=False)
        _collect_ref_names(task.response_schema, reachable, include_current=False)
    return reachable


def _collect_ref_names(schema: object, reachable: set[str], *, include_current: bool) -> None:
    if isinstance(schema, list):
        for item in schema:
            _collect_ref_names(item, reachable, include_current=True)
        return
    if not isinstance(schema, dict):
        return

    ref_name = schema.get("__ts_ref_name")
    if include_current and ref_name:
        reachable.add(ref_name)

    for key, value in schema.items():
        if key == "__ts_composition" and isinstance(value, dict):
            for nested_key in ("base", "extensions", "members"):
                if nested_key in value:
                    _collect_ref_names(value[nested_key], reachable, include_current=True)
            continue
        if isinstance(value, dict):
            _collect_ref_names(value, reachable, include_current=True)
        elif isinstance(value, list):
            for item in value:
                _collect_ref_names(item, reachable, include_current=True)


def _to_path(raw_path: str):
    from pathlib import Path

    return Path(raw_path).resolve()


def build_langchain_tool() -> StructuredTool:
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as exc:
        raise RuntimeError("langchain_core is required to build the LangChain tool") from exc

    return StructuredTool.from_function(
        func=convert_openapi_to_typescript,
        name="convert_openapi_to_typescript",
        description=(
            "Load a local or remote Swagger/OpenAPI document, extract request and response DTOs, "
            "and generate TypeScript definitions or a structured suggestion package for downstream agents."
        ),
    )
