---
name: "openapi-ts-converter"
description: "Use when the user wants to convert Swagger/OpenAPI docs, Redoc pages, or Swagger UI pages into TypeScript types, extract endpoints/request-response schemas, choose interface vs type output, or decide when to use extends, intersection (&), or union (|) types."
---

# OpenAPI TS Converter

Convert Swagger/OpenAPI input into TypeScript by using the bundled Python toolchain in `scripts/`.

## Installation

Core converter dependencies:

```bash
pip install -r requirements.txt
```

Optional LangChain wrapper dependencies:

```bash
pip install -r requirements-langchain.txt
```

## When to use

Use this skill when the user wants to:

- Convert Swagger/OpenAPI docs into TypeScript
- Use a Redoc or Swagger UI page URL as the source
- Extract request DTOs, response DTOs, and shared model types
- Choose `interface` vs `type`
- Improve generated TS with `extends`, intersection `&`, or union `|`

## Execution order

1. Identify the source:
   - local `json` / `yaml`
   - remote OpenAPI URL
   - Redoc / Swagger UI page URL
2. Prefer the bundled CLI in `scripts/cli.py`
 3. For project routing, prefer a project config file and pass it with `--output-config`
 4. If no config is passed, the CLI may auto-discover a project config file from the current directory upward
4. If the user asks about composition strategy, read `references/type-composition.md`
5. If the user asks how to run or integrate the converter, read `references/cli-usage.md`

## Core rule

This skill orchestrates the bundled converter. Do not re-implement OpenAPI parsing or TS rendering in the skill instructions.

Use the code in:

- `scripts/cli.py`
- `scripts/langchain_tool.py`
- `scripts/loader.py`
- `scripts/parser.py`
- `scripts/schema_resolver.py`
- `scripts/ts_generator.py`

## Default command pattern

Single-file output:

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output outputs/generated.types.ts
```

Rule-based project output:

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output-config ./openapi-ts.config.yaml
```

Suggestion JSON for agent handoff:

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output-config ./openapi-ts.config.yaml \
  --suggest-json
```

## Reference map

Read only what is needed for the current task:

- `references/cli-usage.md` -> command templates, output locations, runtime notes
- `references/agent-handoff.md` -> how an agent should consume `--suggest-json` output and patch target files
- `references/codex-agent-playbook.md` -> a concrete Codex-oriented workflow and prompt template for consuming suggestion packages
- `references/type-composition.md` -> when to use `extends`, `&`, `|`
- `references/development-conventions.md` -> internal maintenance rules

## Quality rules

- Prefer the bundled CLI over ad-hoc snippets.
- Keep generated outputs deterministic and written to disk.
- If the user explicitly asks for `type`, do not force `interface`.
- Do not map every `allOf` to `extends`; choose based on composition semantics.
- When the source is a viewer page URL, rely on the bundled loader normalization unless debugging the source itself.
- The current default output is one file containing request types, response types, and referenced shared models.
- Project-specific routing rules belong in a project config file, not in the skill itself.
- When the downstream step is handled by an agent, prefer `--suggest-json` so the skill only returns structured modification suggestions instead of writing files directly.
