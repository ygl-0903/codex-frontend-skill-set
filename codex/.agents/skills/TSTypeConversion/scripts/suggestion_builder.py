from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .models import ApiTypeTask, ParsedTypeBundle, TypeScriptRenderOptions
from .ts_generator import generate_typescript


DECLARATION_PATTERN = re.compile(
    r"^\s*(?:export\s+)?(?:declare\s+)?(?:default\s+)?"
    r"(interface|type|class|enum|function|const|let|var)\s+([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)
IMPORT_DEFAULT_PATTERN = re.compile(
    r"^\s*import\s+([A-Za-z_$][\w$]*)\s*(?:,|\s+from)",
    re.MULTILINE,
)
IMPORT_NAMESPACE_PATTERN = re.compile(
    r"^\s*import\s+\*\s+as\s+([A-Za-z_$][\w$]*)\s+from",
    re.MULTILINE,
)
IMPORT_NAMED_PATTERN = re.compile(r"^\s*import\s*{([^}]*)}\s*from", re.MULTILINE)


@dataclass(slots=True)
class FileSuggestion:
    file: Path
    content: str
    symbols: list[str]
    source_paths: list[str]
    operation_ids: list[str]
    tags: list[str]
    style: str
    warnings: list[str]
    merge_hint: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "file": str(self.file),
            "content": self.content,
            "symbols": list(self.symbols),
            "source_paths": list(self.source_paths),
            "operation_ids": list(self.operation_ids),
            "tags": list(self.tags),
            "style": self.style,
            "warnings": list(self.warnings),
            "merge_hint": dict(self.merge_hint),
        }


def build_routed_suggestions(
    bundle: ParsedTypeBundle,
    output_config,
    options: TypeScriptRenderOptions,
    *,
    slice_bundle_fn,
) -> list[FileSuggestion]:
    grouped_tasks: dict[Path, list[ApiTypeTask]] = {}
    for task in bundle.tasks:
        output_path = output_config.resolve_output_for_task(task)
        grouped_tasks.setdefault(output_path, []).append(task)

    suggestions: list[FileSuggestion] = []
    for output_path in sorted(grouped_tasks, key=lambda item: str(item)):
        tasks = grouped_tasks[output_path]
        routed_bundle = slice_bundle_fn(bundle, tasks)
        suggestions.append(
            _build_file_suggestion(
                output_path=output_path,
                bundle=routed_bundle,
                tasks=tasks,
                options=options,
            )
        )
    return suggestions


def build_single_file_suggestion(
    bundle: ParsedTypeBundle,
    output_path: Path,
    options: TypeScriptRenderOptions,
) -> FileSuggestion:
    return _build_file_suggestion(
        output_path=output_path,
        bundle=bundle,
        tasks=bundle.tasks,
        options=options,
    )


def render_suggestions_json(suggestions: list[FileSuggestion]) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "generator": "TSTypeConversion",
            "mode": "suggest_json",
            "items": [suggestion.to_dict() for suggestion in suggestions],
        },
        ensure_ascii=False,
        indent=2,
    )


def _build_file_suggestion(
    *,
    output_path: Path,
    bundle: ParsedTypeBundle,
    tasks: list[ApiTypeTask],
    options: TypeScriptRenderOptions,
) -> FileSuggestion:
    content = generate_typescript(bundle, options)
    symbols = sorted(scan_typescript_symbols(content))
    source_paths = sorted({task.path for task in tasks})
    operation_ids = sorted({task.operation_id for task in tasks})
    tags = sorted({tag for task in tasks for tag in task.tags})
    return FileSuggestion(
        file=output_path.resolve(),
        content=content,
        symbols=symbols,
        source_paths=source_paths,
        operation_ids=operation_ids,
        tags=tags,
        style=options.style,
        warnings=list(bundle.warnings),
        merge_hint={
            "preferred_action": "agent_inspect_and_patch",
            "conflict_policy": "agent_reads_target_file_before_edit",
        },
    )


def scan_typescript_symbols(source: str) -> dict[str, str]:
    """扫描 TS 内容中的顶层声明与导入，供建议包输出 symbol 列表。"""
    symbols: dict[str, str] = {}
    for kind, name in DECLARATION_PATTERN.findall(source):
        symbols.setdefault(name, kind)

    for name in IMPORT_DEFAULT_PATTERN.findall(source):
        symbols.setdefault(name, "import")
    for name in IMPORT_NAMESPACE_PATTERN.findall(source):
        symbols.setdefault(name, "import")
    for block in IMPORT_NAMED_PATTERN.findall(source):
        for raw_item in block.split(","):
            item = raw_item.strip()
            if not item:
                continue
            if " as " in item:
                _, alias = item.split(" as ", 1)
                name = alias.strip()
            else:
                name = item
            if name:
                symbols.setdefault(name, "import")
    return symbols
