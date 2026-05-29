from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

import yaml


def load_openapi_document(source: str) -> dict:
    """加载本地或远程 OpenAPI 文档，并统一返回 Python 字典。"""
    if _is_url(source):
        raw_text = _load_from_url(_normalize_source_url(source))
    else:
        raw_text = _load_from_file(source)
    document = _parse_document(raw_text, source)
    if not isinstance(document, dict):
        raise ValueError(f"OpenAPI document must be a JSON/YAML object: {source}")
    return document


def _is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _load_from_file(source: str) -> str:
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"OpenAPI document not found: {source}")
    return path.read_text(encoding="utf-8")


def _load_from_url(source: str) -> str:
    request = Request(source, headers={"User-Agent": "TSTypeConversion/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _normalize_source_url(source: str) -> str:
    parsed = urlparse(source)
    query = parse_qs(parsed.query)

    # Redoc / Swagger UI 页面通常会把真实的 spec 地址放在查询参数里。
    # 这里先归一化地址，调用方就可以直接传页面地址，而不用手动改成 JSON/YAML 地址。
    if _looks_like_viewer_page(parsed.path):
        for key in ("spec", "url"):
            raw_target = query.get(key, [])
            if raw_target and raw_target[0]:
                return urljoin(source, raw_target[0])
    return source


def _looks_like_viewer_page(path: str) -> bool:
    lowered = path.lower()
    return (
        lowered.endswith(".html")
        or "redoc" in lowered
        or "swagger-ui" in lowered
        or "swaggerui" in lowered
    )


def _parse_document(raw_text: str, source: str) -> dict:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # 很多 OpenAPI 文档直接使用 yaml/yml，因此 JSON 失败后继续尝试 YAML。
        try:
            parsed = yaml.safe_load(raw_text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse OpenAPI document: {source}") from exc
        if parsed is None:
            raise ValueError(f"OpenAPI document is empty: {source}")
        return parsed
