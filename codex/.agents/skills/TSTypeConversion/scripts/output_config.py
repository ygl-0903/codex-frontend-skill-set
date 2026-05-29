from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import ApiTypeTask


CONFIG_ENV_VAR = "TS_TYPE_CONVERSION_CONFIG"
DEFAULT_CONFIG_FILE_NAMES = (
    "openapi-ts.config.yaml",
    "openapi-ts.config.yml",
    "ts-type-conversion.config.yaml",
    "ts-type-conversion.config.yml",
)


@dataclass(slots=True)
class OutputRule:
    output: str
    tags: set[str] = field(default_factory=set)
    operation_ids: set[str] = field(default_factory=set)
    path_prefixes: tuple[str, ...] = ()

    def matches(self, task: ApiTypeTask) -> bool:
        if self.operation_ids and task.operation_id not in self.operation_ids:
            return False
        if self.tags and not self.tags.intersection(set(task.tags)):
            return False
        if self.path_prefixes and not any(task.path.startswith(prefix) for prefix in self.path_prefixes):
            return False
        return True

    def priority(self) -> tuple[int, int, int]:
        # operationId 的确定性最高，其次是 path 前缀，最后是 tag。
        return (
            0 if self.operation_ids else 1,
            0 if self.path_prefixes else 1,
            0 if self.tags else 1,
        )


@dataclass(slots=True)
class OutputConfig:
    config_path: Path
    default_output: str | None = None
    rules: list[OutputRule] = field(default_factory=list)

    @property
    def base_dir(self) -> Path:
        return self.config_path.parent

    def resolve_output_for_task(self, task: ApiTypeTask) -> Path:
        matched_rules = [
            (index, rule)
            for index, rule in enumerate(self.rules)
            if rule.matches(task)
        ]
        if matched_rules:
            _, rule = min(
                matched_rules,
                key=lambda item: (item[1].priority(), item[0]),
            )
            return _resolve_output_path(self.base_dir, rule.output)
        if self.default_output:
            return _resolve_output_path(self.base_dir, self.default_output)
        raise ValueError(
            f"No output rule matched {task.method.upper()} {task.path} "
            f"and no default_output was configured"
        )


def resolve_output_config(
    explicit_path: str | None,
    *,
    start_dir: Path | None = None,
) -> OutputConfig | None:
    """按 CLI 参数、环境变量、自动发现的顺序解析项目级输出配置。"""
    if explicit_path:
        return load_output_config_file(explicit_path)

    env_path = os.environ.get(CONFIG_ENV_VAR)
    if env_path:
        return load_output_config_file(env_path)

    discovered_path = discover_output_config(start_dir or Path.cwd())
    if discovered_path:
        return load_output_config_file(str(discovered_path))
    return None


def discover_output_config(start_dir: Path) -> Path | None:
    current = start_dir.resolve()
    for directory in (current, *current.parents):
        for file_name in DEFAULT_CONFIG_FILE_NAMES:
            candidate = directory / file_name
            if candidate.exists():
                return candidate
    return None


def load_output_config_file(path: str) -> OutputConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Output config not found: {path}")

    raw_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw_payload is None:
        raise ValueError(f"Output config is empty: {path}")
    if not isinstance(raw_payload, dict):
        raise ValueError(f"Output config must be a YAML object: {path}")

    return OutputConfig(
        config_path=config_path,
        default_output=_read_optional_string(raw_payload, "default_output"),
        rules=_parse_rules(raw_payload.get("rules", []), path),
    )


def _parse_rules(raw_rules: Any, source_path: str) -> list[OutputRule]:
    if raw_rules in (None, []):
        return []
    if not isinstance(raw_rules, list):
        raise ValueError(f"rules must be a list in output config: {source_path}")

    parsed_rules: list[OutputRule] = []
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise ValueError(f"Each rule must be an object in output config: {source_path}")
        match = raw_rule.get("match", {})
        if not isinstance(match, dict):
            raise ValueError(f"rule.match must be an object in output config: {source_path}")

        output = _read_required_string(raw_rule, "output", source_path)
        parsed_rules.append(
            OutputRule(
                output=output,
                tags=_read_string_set(match, "tags", source_path),
                operation_ids=_read_string_set(match, "operation_ids", source_path),
                path_prefixes=_read_string_tuple(match, "path_prefix", source_path),
            )
        )
    return parsed_rules


def _resolve_output_path(base_dir: Path, raw_output: str) -> Path:
    output_path = Path(raw_output)
    if output_path.is_absolute():
        return output_path
    return (base_dir / output_path).resolve()


def _read_required_string(payload: dict[str, Any], key: str, source_path: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string in output config: {source_path}")
    return value.strip()


def _read_optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string when provided")
    return value.strip()


def _read_string_set(payload: dict[str, Any], key: str, source_path: str) -> set[str]:
    value = payload.get(key)
    if value is None:
        return set()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a string array in output config: {source_path}")
    return {item.strip() for item in value if item.strip()}


def _read_string_tuple(payload: dict[str, Any], key: str, source_path: str) -> tuple[str, ...]:
    value = payload.get(key)
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(item.strip() for item in value if item.strip())
    raise ValueError(f"{key} must be a string or string array in output config: {source_path}")
