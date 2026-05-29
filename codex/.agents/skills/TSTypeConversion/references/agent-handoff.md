# Agent Handoff

## Purpose

Use this flow when the converter should not edit project files directly, and the downstream file merge should be handled by a coding agent.

## Recommended flow

1. Run the converter with `--suggest-json`
2. Parse the returned package
3. For each item:
   - open the target file from `file`
   - inspect existing symbols and local structure
   - merge or patch using `content` as the generated source of truth
   - preserve unrelated manual code
4. Verify the edited file before moving on

## CLI example

```bash
python -m scripts.cli \
  --input <source> \
  --style interface \
  --output-config ./openapi-ts.config.yaml \
  --suggest-json
```

## Suggestion package shape

```json
{
  "schema_version": 1,
  "generator": "TSTypeConversion",
  "mode": "suggest_json",
  "items": [
    {
      "file": "src/api/user/types.ts",
      "content": "export interface ILoginReq {\\n  password: string;\\n}\\n",
      "symbols": ["ILoginReq", "IUserLoginResp"],
      "source_paths": ["/user/login"],
      "operation_ids": ["login"],
      "tags": ["user"],
      "style": "interface",
      "warnings": [],
      "merge_hint": {
        "preferred_action": "agent_inspect_and_patch",
        "conflict_policy": "agent_reads_target_file_before_edit"
      }
    }
  ]
}
```

## Agent guidance

- Treat `content` as generated truth for the listed `symbols`
- Do not assume the target file is empty
- Preserve unrelated declarations whenever possible
- Read the file before editing; do not blindly append in complex files
- If the target file contains conflicting manual declarations, stop and review before patching

## Minimal merge strategy

For the first usable agent flow, this is enough:

1. If the file does not exist, create it with `content`
2. If the file exists and the generated symbols are absent, append `content`
3. If the file exists and matching symbols already exist, inspect and patch manually

More advanced symbol ownership or AST merging can be added later if needed.

## Next reference

If the downstream agent is Codex, also read:

- `references/codex-agent-playbook.md`
