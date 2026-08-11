---
name: bd-fe-conventions
description: 前端项目规范与复用指南的可落地通用模版。在新增页面、实现 Figma、对接后端 API、查找可复用组件时使用；与 AGENTS.md 配合作为项目内约束入口。
---

# <project_name-bd-frontend> 前端项目规范

## 适用时机

- 新增页面、模块或路由前，需要确认当前项目约定。
- 实现 Figma 或原型图前，需要查找同域参考页面和样式习惯。
- 对接后端 API 前，需要确认请求入口、service、类型和错误处理模式。
- 查找可复用组件、布局、图表或表单模式时使用。

## 先做什么

1. 先读 `AGENTS.md`，确认仓库级约束和当前项目是否采用这些模板流程。
2. 如果任务有需求卡，读取 `docs/modules/<feature>.md`；如果没有需求卡，读取用户需求、接口契约、设计稿或目标页面说明。
3. 找最像的旧页面；参考路径必须替换成目标项目真实存在的路径，例如 `<reference_detail_page_pattern-src/pages/Application/**>`、`<reference_complex_page_pattern-src/pages/Iteration/**>`。
4. 涉及接口时先读 `<project_request_entry-src/utils/requests.ts>` 和已有 `<project_service_glob-src/service/*.ts>`，确认请求入口与现有模式。
5. 涉及页面结构、CSS 或 UI 细节时，再按需读取 `references/page-structure-and-css.md`、`references/ui-tokens.md`。

## 必须遵守

- 所有 HTTP 请求都必须经过 `<project_request_entry-src/utils/requests.ts>` 创建的 `<request_library-Alova>` 实例。
- 业务请求方法写在 `<project_service_glob-src/service/*.ts>`。
- 类型放在 `<project_types_dir-src/models/typings/>` 或该功能既有的 model 文件。
- 路由在 `<project_router_file-src/router/index.tsx>` 中按现有模式注册。
- 页面样式沿用 `<ui_library-Ant Design>` + `<style_solution-styled-components>` + 同目录 `<page_style_file-style.ts>`。
- 页面区块拆分、`className` 命名和 CSS 组织优先遵循 `references/page-structure-and-css.md`，不要在不同页面各起一套局部规则。
- 如果目标项目已经采用其他 UI 库、样式方案、请求库或路由方案，必须把本 skill 的示例替换为目标项目真实方案后再使用。

## 明确禁止

- 不新增第二套全局请求封装。
- 不使用 `any` 掩盖接口结构。
- 不在缺少契约时猜字段。
- 不引入新的重型 UI 库。

## 参考资料

按任务边界按需再读，不要无关预读：

- `references/api-errors.md`：只用于请求封装、service、错误处理和敏感信息边界。
- `references/page-structure-and-css.md`：只用于页面结构、组件拆分、className 和 CSS 组织。
- `references/ui-tokens.md`：只用于 UI 组件、图标、样式 token、Figma 标注优先级。

## 模块需求卡

如果目标项目采用模块需求卡流程，单模块需求写在 `docs/modules/<feature>.md`。实现前优先读文件，不在对话中粘贴长文。

如果目标项目没有需求卡流程，本 skill 仍可用于查约定，但不能要求先创建或读取不存在的 `docs/modules/<feature>.md`。

## 收尾要求

- 说明本次参考了 `AGENTS.md`、需求卡或哪些 `references/` 文件。
- 说明采用了哪些既有页面、组件、请求或样式模式。
- 如发现模板示例与目标项目事实不一致，列出需要人工更新的规则，不要静默沿用示例。
