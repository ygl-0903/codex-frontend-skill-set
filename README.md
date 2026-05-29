# AI 开发流程化工具包

这个仓库用于沉淀一套可迁移的 AI 开发工作流。核心思路是把项目协作规则、模块开发流程和常用检查项写成 skills，再复制到具体项目中使用。

目前主要覆盖两类场景：

- Codex：使用 `AGENTS.md`、`.codex/` 和 `.agents/skills/`
- Claude Code：使用 `CLAUDE.md`、`.claude/commands/` 和 `.claude/skills/`

## 目录结构

```text
.
├── codex/
│   ├── AGENTS.md
│   ├── AGENTS-template.md
│   ├── .codex/
│   └── .agents/skills/
├── claude/
│   └── .claude/
└── .agents/skills/
    └── skill-generalize-template/
```

## Codex 使用方式

把 `codex/` 下这些内容复制到目标项目根目录：

```text
AGENTS.md
AGENTS-template.md
.codex/
.agents/
```

如果目标项目还没有自己的约定，可以先使用 `AGENTS-template.md` 和 `*-template` skills，再调用 `skill-template-fill` 让 AI 读取项目结构并填充占位符。

如果目标项目已经有 `AGENTS.md` 或 `.agents/skills/`，不要直接覆盖。建议先生成 `*.generated.md`，人工确认后再合并。

## Claude Code 使用方式

把 `claude/.claude/` 复制到目标项目根目录。

如果要复用 Codex 侧的 skills，可以把 `.agents/skills/` 中的内容按需复制到：

```text
.claude/skills/
.claude/commands/
```

`AGENTS.md` 中的项目规则也可以整理成 `CLAUDE.md` 使用，但需要人工检查命令格式和 Claude Code 的触发方式。

## 模板与落地

仓库里有两类辅助 skill：

- `skill-generalize-template`：把某个项目里的 skill 抽象成通用模板。
- `skill-template-fill`：把通用模板放到新项目后，读取项目内容并填充占位符。

典型流程：

1. 从已有项目中抽取 skill。
2. 使用 `skill-generalize-template` 生成 `*-template`。
3. 把模板复制到新项目。
4. 在新项目中调用 `skill-template-fill`。
5. 人工检查生成的 `AGENTS.generated.md` 和 `SKILL.generated.md`。
6. 确认后再覆盖正式文件。

占位符格式约定为：

```text
<placeholder_name-source_example>
```

例如：

```text
<project_pages_dir-src/pages/>
<project_request_entry-src/utils/requests.ts>
<ui_library-Ant Design>
```

`source_example` 只是来源项目示例，落地到新项目时不能直接照抄。

## 当前包含的模块 skills

Codex 侧已经整理了这些模块工作流模板：

- `bd-fe-conventions-template`：前端项目规范与复用指南
- `module-demand-template`：需求整理
- `module-kickoff-template`：模块启动
- `module-scaffold-template`：页面壳子
- `module-api-template`：接口接入
- `module-api-param-change-template`：接口参数变更
- `module-handUI-template`：设计稿回填
- `module-polish-template`：模块收口
- `module-handoff-template`：交接文档
- `skill-template-fill`：在新项目中填充模板占位符

这些模板默认不应该直接当成项目最终规则使用。先让 AI 根据目标项目填充，再人工复核。

