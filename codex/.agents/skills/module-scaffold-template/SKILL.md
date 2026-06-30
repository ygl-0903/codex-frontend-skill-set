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
3. 在开始写页面结构前，先判断设计中的视觉元素哪些适合直接用 CSS 还原，哪些即使用 CSS 也会还原度较低，或明显更适合走图片/资源方案。
4. 把这类“纯 CSS 难以高质量还原”的元素清单补充到 `docs/modules/<feature>.md`，至少写明元素名称、所在区域、原因；如果文档不存在，先按当前模块名创建对应需求卡再补充。
5. 只实现页面骨架、loading、empty 和必要的 mock 数据。
6. mock 可放在页面目录下，例如 `<page_mock_file-internals/mock.ts>`，并标注后续要替换为 `<project_service_dir-src/service/>` 调用。
7. 超过 3 个复杂组件时，按 `<project_component_split_rule-拆分组件文件>` 拆分，不要把所有内容塞进一个页面文件。

## 硬规则

- 不接真实接口。
- 不新增第二套请求封装。
- 风格对齐同域页面的 `<ui_library-Ant Design>` + `<style_solution-styled-components>` 模式。
- 涉及 UI 还原时，必须先做一次“CSS 可还原性判断”，并把低还原度元素记录到 `docs/modules/<feature>.md`，不能只在脑中判断不落文档。
- 页面结构、`className` 命名和 CSS 组织细则统一以 `../bd-fe-conventions/references/page-structure-and-css.md` 为准，不在当前 skill 重复维护一整套。

## 任务特有提醒

- 页面壳子阶段就要先确定页面根 block、主区块 block 和核心 element 命名，不要等回填设计稿时再补命名结构。
- 页面初版样式先解决布局、间距、基础状态和空态骨架，不要为了壳子页面过早堆复杂视觉细节。
- 如果一个区块未来大概率会拆成子组件，从壳子阶段就把它当独立 block 处理，避免后续模板和样式整体翻修。


## 收尾建议

- 跑 `<lint_command-yarn lint>`。
- 需要时再跑 `<build_command-yarn build>`。
- 结束时提示下一轮进入 `module-api`。
