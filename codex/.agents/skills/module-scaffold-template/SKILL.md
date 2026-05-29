---
name: module-scaffold
description: 页面壳子阶段使用的通用模版。创建页面目录、路由占位、loading/empty 和 mock 数据，不接真实接口。
---

# 模块搭壳子

## 适用时机

- kickoff 阶段已经完成，需求卡和实施范围已经对齐
- 需要先创建页面骨架、路由入口、基础状态和 mock 数据
- 真实接口契约尚未接入，或本轮明确不做接口联调

## 目标与边界

- 在不接真实接口的前提下，完成页面骨架、路由、基础状态和 mock
- 这一轮只搭可运行页面壳子，不实现真实请求、不新增请求封装

## 执行步骤

1. 基于需求卡和 kickoff 结论，在 `<project_pages_dir-src/pages/>` 下创建页面目录。
2. 在 `<project_router_file-src/router/index.tsx>` 中注册路由，保持与现有 `<project_layout_pattern-Layout / 侧边栏模式>` 一致。
3. 只实现页面骨架、loading、empty 和必要的 mock 数据。
4. mock 可放在页面目录下，例如 `<page_mock_file-internals/mock.ts>`，并标注后续要替换为 `<project_service_dir-src/service/>` 调用。
5. 超过 3 个复杂组件时，按 `<project_component_split_rule-拆分组件文件>` 拆分，不要把所有内容塞进一个页面文件。

## 硬规则

- 不接真实接口。
- 不新增第二套请求封装。
- 风格对齐同域页面的 `<ui_library-Ant Design>` + `<style_solution-styled-components>` 模式。

## 收尾建议

- 跑 `<lint_command-yarn lint>`。
- 需要时再跑 `<build_command-yarn build>`。
- 结束时提示下一轮进入 `module-api`。
