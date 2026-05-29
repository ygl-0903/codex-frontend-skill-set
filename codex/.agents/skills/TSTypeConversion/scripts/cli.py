from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_openapi_document
from .models import ApiTypeTask, ParsedTypeBundle, TypeScriptRenderOptions
from .output_config import resolve_output_config
from .parser import parse_openapi_document
from .suggestion_builder import (
    build_routed_suggestions,
    build_single_file_suggestion,
    render_suggestions_json,
)
from .ts_generator import generate_typescript


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将 Swagger/OpenAPI 文档转换为 TypeScript 请求和响应类型。"
    )

    # 支持本地 JSON/YAML、远程 Swagger 地址，以及 Redoc/Swagger UI 页面地址。
    parser.add_argument("--input", required=True, help="输入文档路径或远程 URL")

    # 控制最终输出使用 interface 还是 type 两种 TypeScript 风格。
    parser.add_argument(
        "--style",
        default="interface",
        choices=("interface", "type"),
        help="TypeScript 输出风格：interface 或 type",
    )

    # 单文件输出模式下，将所有类型写入指定 ts 文件。
    parser.add_argument("--output", help="将生成的 TypeScript 写入指定文件")

    # 项目级规则配置，命中后会把不同接口路由到不同文件。
    parser.add_argument(
        "--output-config",
        help="项目级输出规则配置文件路径，支持 YAML",
    )

    # 输出结构化修改建议包，供 agent 读取后再做具体代码修改。
    parser.add_argument(
        "--suggest-json",
        action="store_true",
        help="输出结构化修改建议 JSON，不直接写入项目文件",
    )

    # 按 tag 过滤接口，多个 tag 使用英文逗号分隔。
    parser.add_argument(
        "--include-tags",
        help="按 tag 过滤接口，多个 tag 使用英文逗号分隔",
    )

    # 保持和 OpenAPI 原始语义一致，按真实 operationId 过滤。
    parser.add_argument(
        "--operation-id",
        action="append",
        default=[],
        help="按 operationId 过滤接口，可重复传入多个值",
    )

    # 按请求路径过滤接口，多个路径使用英文逗号分隔。
    parser.add_argument(
        "--path",
        help="按请求路径过滤接口，多个路径使用英文逗号分隔",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口，负责加载文档、过滤接口并输出 TS 类型文件。"""
    args = build_parser().parse_args(argv)
    if args.output and args.output_config:
        raise ValueError("--output 和 --output-config 不能同时使用")

    document = load_openapi_document(args.input)
    bundle = parse_openapi_document(document)
    bundle = _filter_bundle(
        bundle=bundle,
        include_tags=_split_csv(args.include_tags),
        operation_ids=set(args.operation_id),
        paths=_split_csv(args.path),
    )
    output_config = None
    if args.output_config:
        output_config = resolve_output_config(args.output_config)
    elif not args.output:
        output_config = resolve_output_config(None)

    render_options = TypeScriptRenderOptions(style=args.style)

    if args.suggest_json:
        suggestions = _build_suggestions(
            bundle=bundle,
            output_path=Path(args.output).resolve() if args.output else None,
            output_config=output_config,
            options=render_options,
        )
        print(render_suggestions_json(suggestions))
        return 0

    if output_config:
        _write_routed_outputs(bundle, output_config, render_options)
        return 0

    if not args.output:
        raise ValueError("需要通过 --output 指定单文件输出，或提供项目级输出配置")

    ts_output = generate_typescript(bundle, render_options)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ts_output, encoding="utf-8")
    return 0


def _filter_bundle(
    bundle: ParsedTypeBundle,
    include_tags: set[str],
    operation_ids: set[str],
    paths: set[str],
) -> ParsedTypeBundle:
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
    return ParsedTypeBundle(
        tasks=filtered_tasks,
        shared_schemas=filtered_shared,
        warnings=bundle.warnings,
    )


def _collect_reachable_shared_names(tasks: list[ApiTypeTask]) -> set[str]:
    reachable: set[str] = set()
    for task in tasks:
        _collect_ref_names(task.request_schema, reachable, include_current=False)
        _collect_ref_names(task.response_schema, reachable, include_current=False)
    return reachable


def _collect_ref_names(
    schema: object,
    reachable: set[str],
    *,
    include_current: bool,
) -> None:
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


def _split_csv(raw_value: str | None) -> set[str]:
    if not raw_value:
        return set()
    return {item.strip() for item in raw_value.split(",") if item.strip()}


def _write_routed_outputs(
    bundle: ParsedTypeBundle,
    output_config,
    options: TypeScriptRenderOptions,
) -> None:
    grouped_tasks: dict[Path, list[ApiTypeTask]] = {}
    for task in bundle.tasks:
        output_path = output_config.resolve_output_for_task(task)
        grouped_tasks.setdefault(output_path, []).append(task)

    for output_path, tasks in grouped_tasks.items():
        routed_bundle = _slice_bundle(bundle, tasks)
        ts_output = generate_typescript(routed_bundle, options)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ts_output, encoding="utf-8")


def _build_suggestions(
    *,
    bundle: ParsedTypeBundle,
    output_path: Path | None,
    output_config,
    options: TypeScriptRenderOptions,
):
    if output_config:
        return build_routed_suggestions(
            bundle,
            output_config,
            options,
            slice_bundle_fn=_slice_bundle,
        )
    if output_path is None:
        raise ValueError("需要通过 --output 或项目级输出配置生成建议包")
    return [build_single_file_suggestion(bundle, output_path, options)]


def _slice_bundle(bundle: ParsedTypeBundle, tasks: list[ApiTypeTask]) -> ParsedTypeBundle:
    reachable_shared_names = _collect_reachable_shared_names(tasks)
    filtered_shared = [
        shared
        for shared in bundle.shared_schemas
        if shared.source_name in reachable_shared_names
    ]
    return ParsedTypeBundle(
        tasks=list(tasks),
        shared_schemas=filtered_shared,
        warnings=bundle.warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
