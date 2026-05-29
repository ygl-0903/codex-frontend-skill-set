---
name: skill-template-fill
description: 将通用 skill 模版落地到一个新项目时使用。读取目标项目结构、配置、依赖、现有文档和代码约定，填充 `<placeholder-source_example>` 占位符，生成可直接使用的项目级 AGENTS.md 与 .agents/skills/*/SKILL.md。
---

# Skill 模版落地

## 适用时机

- 已经把一组通用 skill 模版复制到新项目中。
- 模版里包含 `<placeholder_name-source_example>` 这类占位符，需要根据当前项目填成真实路径、框架、命令和约定。
- 目标是让这些 skills 成为当前项目可直接使用的项目级工作流。

## 目标与边界

- 目标是读取当前项目，整理占位符映射，并生成或更新可用的 `AGENTS.md` 与 `.agents/skills/*/SKILL.md`。
- 只做 skill 和项目指引的落地，不改业务代码。
- 不猜不存在的目录、接口、命令或团队约定；无法确认时保留占位符并列入待确认。
- 不把一个项目的约定写成通用事实，只写当前项目能从文件中验证或由用户明确提供的内容。

## 输入形式

支持以下任一输入：

1. 当前项目根目录。
2. 一个 `.agents/` 目录。
3. 一个或多个 template 文件，例如 `AGENTS-template.md`、`.agents/skills/module-api-template/SKILL.md`。
4. 用户直接说明“把这些模板 skills 落地到当前项目”。

如果用户没有指定路径，默认以当前工作目录作为目标项目根目录。

## 模版识别

优先识别这些文件：

- `AGENTS-template.md`
- `.agents/skills/*-template/SKILL.md`
- `.agents/skills/*/SKILL.template.md`
- `.agents/skills/*/SKILL.md` 中仍包含 `<placeholder_name-source_example>` 的文件

不要处理已经没有占位符的普通 skill，除非用户明确要求重写。

## 项目扫描顺序

1. 读取项目根目录文件列表，确认框架和包管理器：
   - `package.json`
   - lockfile，例如 `yarn.lock`、`pnpm-lock.yaml`、`package-lock.json`
   - 构建配置，例如 `vite.config.*`、`webpack.config.*`、`next.config.*`、`vue.config.*`
2. 读取项目级指引和文档入口：
   - `AGENTS.md`
   - `README.md`
   - `docs/`
   - 现有 `.agents/skills/`
3. 读取关键源码目录，确认真实结构：
   - 页面目录
   - 路由文件
   - 请求封装入口
   - service/API 目录
   - 类型/model 目录
   - 组件目录
   - 样式方案
4. 读取 1 到 3 个最相近的已有页面或模块，只用于确认命名习惯、拆分方式和错误处理模式。

## 占位符填充规则

- 占位符格式为 `<placeholder_name-source_example>`。
- `placeholder_name` 表示语义职责，优先按职责匹配当前项目真实文件。
- `source_example` 只是来源项目示例，不能直接照抄到新项目。
- 如果当前项目存在等价项，用真实值替换整个占位符。
- 如果当前项目没有等价项，但可以从框架配置中确认替代路径，使用替代路径。
- 如果无法确认，保留占位符，并在结果说明里列为待确认。

示例：

- `<project_pages_dir-src/pages/>` 在新项目中可能填成 `src/views/`、`src/pages/` 或 `app/`
- `<project_router_file-src/router/index.tsx>` 可能填成 `src/router/index.ts`、`src/routes.tsx` 或 `app` 路由约定
- `<project_request_entry-src/utils/requests.ts>` 可能填成 `src/api/request.ts`、`src/utils/request.ts` 或项目现有请求实例
- `<ui_library-Ant Design>` 可能填成 `Element Plus`、`Naive UI`、`Ant Design` 或“无统一 UI 库”

## 常见映射来源

- 技术栈：从 `package.json` 的 dependencies/devDependencies 判断。
- 命令：从 `package.json` 的 scripts 判断，不要臆造 `yarn lint` 或 `yarn build`。
- 包管理器：优先看 lockfile，再看用户命令。
- 路由：从路由依赖、配置文件、`src/router`、`src/routes`、`app` 目录判断。
- 请求封装：搜索 `axios.create`、`fetch` wrapper、`request`、`service`、`alova`、`ky`、`ofetch` 等。
- 类型目录：搜索 `types`、`models`、`interface`、`typings`。
- 样式方案：从依赖和代码中判断 CSS Modules、Sass、Less、styled-components、Tailwind、UnoCSS 等。
- 错误处理：搜索 `message`、`toast`、`notification`、全局拦截器和请求错误映射。
- 参考页：优先选同业务域、同页面类型、最近维护的页面。

## 生成规则

1. 先建立占位符映射表。
2. 再逐个模板文件生成目标文件：
   - `AGENTS-template.md` -> `AGENTS.md`
   - `.agents/skills/<name>-template/SKILL.md` -> `.agents/skills/<name>/SKILL.md`
   - `.agents/skills/<name>/SKILL.template.md` -> `.agents/skills/<name>/SKILL.md`
3. 如果目标文件已存在：
   - 先读取并判断是否包含用户已有约定。
   - 默认不要覆盖，除非用户明确要求。
   - 推荐生成到旁边的候选文件，例如 `SKILL.generated.md` 或 `AGENTS.generated.md`，并说明差异。
4. 删除 frontmatter name 中的 `-template` 后缀。
5. description 中去掉“通用模版”措辞，改成当前项目可用的描述。
6. 保留无法确认的占位符，不要编造。

## 硬规则

- 不改业务源码。
- 不安装依赖。
- 不运行会修改项目产物的命令。
- 不用源项目示例值冒充新项目真实值。
- 不覆盖已有 `AGENTS.md` 或 skill，除非用户明确要求。
- 如果项目扫描结果互相矛盾，停下来列出冲突，不要强行选一个。
- 对于无法从文件确认的团队流程、联调联系人、接口契约来源，保留待确认。

## 输出要求

完成后必须说明：

- 读取了哪些项目文件来判断技术栈和目录。
- 生成或更新了哪些文件。
- 主要占位符映射表。
- 哪些占位符未能填充，为什么。
- 哪些内容建议人工复核。

## 推荐后续

- 先让用户审阅生成的 `AGENTS.generated.md` 和 `SKILL.generated.md`。
- 用户确认后，再覆盖正式 `AGENTS.md` 或 `.agents/skills/*/SKILL.md`。
- 落地完成后，用一个小模块需求测试 `module-demand` -> `module-kickoff` -> `module-scaffold` 的链路是否顺畅。
