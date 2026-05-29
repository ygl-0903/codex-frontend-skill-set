---
name: skill-generalize-template
description: 将一个或多个现有 skill 转成可跨 React/Vue 项目复用的通用模版。适用于输入 skill 名或 skill 目录路径，抽离项目绑定规则并在源 skill 旁边一对一产出占位符版 SKILL.md。
---

# skill 通用化模版生成

## 适用时机

- 现有 skill 是从某个具体项目复制出来的
- 需要把项目绑定规则抽离成可复用模版
- 需要一次处理一个或多个 skill
- 输出目标是每个源 skill 对应一个占位符版 `SKILL.md`

## 输入要求

支持两种输入：

1. skill 名列表，例如 `module-api`、`module-kickoff`
2. skill 目录路径列表，例如 `.agents/skills/module-api`

如果两种输入混用，先统一解析成实际目录路径再处理。

## 输出要求

- 一次处理多个 skill 时，必须一对一输出多个模版
- 输出目录必须创建在源 skill 旁边
- 默认命名为 `<source-skill-dir>-template/`
- 每个输出目录里只放一个 `SKILL.md`
- 不要覆盖源 skill，除非用户明确要求

示例：

- `.agents/skills/module-api` -> `.agents/skills/module-api-template/SKILL.md`
- `.agents/skills/module-kickoff` -> `.agents/skills/module-kickoff-template/SKILL.md`

## 执行步骤

1. 解析输入。
   - 如果是 skill 名，到当前项目常用 skill 目录中定位，例如 `.agents/skills/<name>/SKILL.md`
   - 如果是路径，确认目录下存在 `SKILL.md`
   - 任一输入无法定位时，明确指出失败项，不要臆测
2. 读取源 `SKILL.md`。
   - 只在必要时继续读取源 skill 引用的本地参考文件
   - 优先抽取真正影响执行的约束，不要把参考资料整段搬进模版
3. 将内容拆成三类：
   - 可复用工作流：保留
   - 项目绑定规则：改为占位符
   - 纯项目示例：删除或压缩成一句泛化说明
4. 按统一占位符规则改写。
   - 占位符统一使用 `<snake_case_name>`
   - 优先使用语义占位符，不要保留源项目名
   - 占位符命名参考 `references/placeholder-catalog.md`
   - 已经存在且本身具有可复用语义的 skill 名、规范文档名或通用约束入口默认保留，例如 `AGENTS.md`、`bd-fe-conventions`、`docs/modules/<feature>.md`
   - 发生替换时，优先写成“占位符 + 一个源值示例”的形式，例如 `<project_service_dir-src/service/>`、`<project_request_entry-src/utils/requests.ts>`
5. 生成目标 `SKILL.md`。
   - frontmatter 中的 `name` 改为 `<source-skill-name>-template`
   - `description` 明确写出这是“通用模版”
   - 正文保持原 skill 的阶段目标和步骤结构，但去掉特定项目耦合
6. 自检输出。
   - 检查是否仍残留源项目专名、固定目录、固定框架或固定文件路径
   - 检查是否出现无法理解的空洞占位符
   - 检查替换项是否附了足够短的源值示例
   - 检查 `AGENTS.md`、`bd-fe-conventions`、`docs/modules/<feature>.md` 这类应保留项没有被误替换
   - 检查步骤是否仍然可执行，而不是只剩原则描述

## 通用化判断规则

以下内容通常应改成占位符：

- 固定目录，如 `src/pages/`、`src/service/`
- 固定文件，如 `src/router/index.tsx`、`src/utils/requests.ts`
- 固定技术栈，如 React、Vue、Vite、Ant Design、styled-components、Alova
- 固定业务域路径，如 `src/pages/Application/**`
- 固定需求文档位置，如 `docs/modules/<feature>.md`
- 固定流程名称或团队约定，如“handoff 文档必须放在某目录”

以下内容通常应保留：

- 阶段目标
- 执行顺序
- 风险约束，例如“没有契约时不要猜字段”
- 输出物要求，例如“只列路径和理由，不粘贴大段代码”
- 已存在的 skill 名、团队规范名或通用文档入口，例如 `AGENTS.md`、`bd-fe-conventions`、`docs/modules/<feature>.md`

## 占位符写法

- 默认格式：`<placeholder_name-source_example>`
- `source_example` 用源 skill 里的原值，帮助读者快速理解占位符落点
- 示例应短小，只保留识别该项所需的最小信息，不要把整段项目上下文塞进去
- 如果原值里本身含有占位片段，可以保留，例如 `<feature_doc_path-docs/modules/<feature>.md>`

示例：

- `src/service/` -> `<project_service_dir-src/service/>`
- `src/utils/requests.ts` -> `<project_request_entry-src/utils/requests.ts>`
- `React` -> `<frontend_framework-React>`
- `Alova` -> `<request_library-Alova>`
- `src/pages/Application/**` -> `<reference_complex_page_pattern-src/pages/Application/**>`

## 改写原则

- 保留能力边界，不要把 `kickoff`、`scaffold`、`api`、`polish` 混成一个 skill
- 保留硬约束语气，避免模版化后失去执行力
- 少造新抽象；只有在源内容确实依赖项目上下文时才引入占位符
- 不要把“某项目的最佳实践”伪装成“所有项目通用事实”
- 不要为了统一格式而替换掉已经可复用的 skill 名、规范文档名或团队约定入口

## 输出格式建议

生成后的 `SKILL.md` 建议保留这几段：

1. 适用时机
2. 目标或边界
3. 执行步骤
4. 约束或硬规则
5. 收尾或下一步建议

## 失败与停机条件

- 用户没有给 skill 名或路径，且仓库里也无法定位目标 skill
- 源 skill 缺少 `SKILL.md`
- 源 skill 的关键约束全部藏在外部文件里，但这些文件不存在
- 需要猜测项目特定字段、目录或流程含义才能继续

遇到这些情况时，先说明缺口，再停止生成，不要硬写模版。

## 结果说明

完成后必须说明：

- 处理了哪些源 skill
- 为每个源 skill 产出了哪个模版目录
- 抽离了哪些主要项目绑定项
- 哪些内容仍建议人工复核
