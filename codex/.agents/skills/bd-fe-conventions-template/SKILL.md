---
name: bd-fe-conventions
description: 前端项目规范与复用指南的通用模版。在新增页面、实现 Figma、对接后端 API、查找可复用组件时使用。
---

# <project_name-bd-frontend> 项目规范

## 适用时机

- 新增页面、模块或路由前，需要确认当前项目约定。
- 实现 Figma 或原型图前，需要查找同域参考页面和样式习惯。
- 对接后端 API 前，需要确认请求入口、service、类型和错误处理模式。
- 查找可复用组件、布局、图表或表单模式时使用。

## 先做什么

1. 先在 `<reference_detail_page_pattern-src/pages/Application/**>`、`<reference_complex_page_pattern-src/pages/Iteration/**>` 中找最像的旧页面。
2. 先读 `AGENTS.md` 与 `docs/modules/<feature>.md`。
3. 涉及接口时先读 `<project_request_entry-src/utils/requests.ts>`，确认请求入口与现有模式。

## 必须遵守

- 所有 HTTP 请求都必须经过 `<project_request_entry-src/utils/requests.ts>` 创建的 `<request_library-Alova>` 实例。
- 业务请求方法写在 `<project_service_glob-src/service/*.ts>`。
- 类型放在 `<project_types_dir-src/models/typings/>` 或该功能既有的 model 文件。
- 路由在 `<project_router_file-src/router/index.tsx>` 中按现有模式注册。
- 页面样式沿用 `<ui_library-Ant Design>` + `<style_solution-styled-components>` + 同目录 `<page_style_file-style.ts>`。
- 页面区块拆分、`className` 命名和 CSS 组织优先遵循 `references/page-structure-and-css.md`，不要在不同页面各起一套局部规则。


## 明确禁止

- 不新增第二套全局请求封装。
- 不使用 `any` 掩盖接口结构。
- 不在缺少契约时猜字段。
- 不引入新的重型 UI 库。

## 参考资料

按需再读：

- `references/api-errors.md`
- `references/page-structure-and-css.md`
- `references/ui-tokens.md`

## 模块需求卡

单模块需求写在 `docs/modules/<feature>.md`。实现前优先读文件，不在对话中粘贴长文。
