# CLI Usage

## Purpose

This skill should normally call the bundled CLI instead of rebuilding conversion logic in the skill instructions.

## Installation

Core converter only:

```bash
pip install -r requirements.txt
```

If you also need the LangChain wrapper from `scripts/langchain_tool.py`:

```bash
pip install -r requirements-langchain.txt
```

CLI entry:

```bash
python -m scripts.cli
```

## Common command templates

### Single-file output

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output outputs/generated.types.ts
```

### Rule-based project output

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output-config ./openapi-ts.config.yaml
```

### Suggest JSON for agent handoff

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output-config ./openapi-ts.config.yaml \
  --suggest-json
```

### Filter by tag

```bash
python -m scripts.cli \
  --input <source> \
  --include-tags user,auth \
  --output outputs/generated.types.ts
```

### Filter by operationId

```bash
python -m scripts.cli \
  --input <source> \
  --operation-id post_user_login \
  --operation-id post_user_refresh \
  --output outputs/generated.types.ts
```

### Filter by path

```bash
python -m scripts.cli \
  --input <source> \
  --path /user/login,/user/refresh \
  --output outputs/generated.types.ts
```

## Supported sources

- Local JSON file
- Local YAML file
- Remote OpenAPI URL
- Redoc page URL
- Swagger UI page URL

The bundled loader already normalizes viewer URLs into the actual spec URL.

## Default output location

Unless the user requests a different path, write generated artifacts into:

```text
outputs/
```

Recommended names:

- `outputs/generated.types.ts`

## Example config template

You can copy the bundled example project config from:

- `assets/examples/openapi-ts.config.yaml`

## Notes

- Prefer `--output` for a single file result.
- Prefer `--output-config` when the project wants to route different interfaces into different files.
- Prefer `--suggest-json` when the next step will be performed by an agent that reads target files and applies patches.
- `--operation-id` keeps its OpenAPI meaning and matches real `operationId`.
- Use `--path` when the user wants to filter by request path.
- The current CLI focuses on generating request types, response types, and referenced shared models in one file.
- When `--output-config` is omitted, the CLI will also try to auto-discover a project config file from the current directory upward.
- `--suggest-json` does not write target files; it outputs a stable package with `schema_version`, `generator`, `mode`, and `items`.
- Each suggestion item contains `file + content + symbols + source_paths + operation_ids + tags + style + warnings + merge_hint`.
- If you use `--output-config` without `--suggest-json`, the routed files are written directly from generated output.
