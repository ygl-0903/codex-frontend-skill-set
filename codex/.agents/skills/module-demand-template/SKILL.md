---
name: module-demand-template
description: 需求整理阶段使用的通用模版。根据接口说明、前端需求、原型图、截图或 Figma 链接，先读取并沿用项目需求卡模板，生成或更新需求卡，不写业务代码。
---

# 需求整理通用模版

## 适用时机

- 用户给了后端接口文档、接口样例、字段说明或联调口径，需要整理成前端需求卡。
- 用户给了简单需求描述、页面效果图、原型截图或 Figma 链接，需要拆成可开发的页面需求。
- 用户给了多个页面或多个入口，需要按页面 / 流程拆分 `<feature_doc_path-docs/modules/<feature>.md>`。
- 后续准备进入 `module-kickoff`、`module-scaffold`、`module-api` 前，需要先沉淀需求文档。

## 目标与边界

- 目标是把零散材料整理成可执行的需求卡。
- 只整理需求文档，不写页面代码、不改接口封装、不注册路由。
- 信息不足时先沉淀已知内容，并在需求卡中标明待确认项。

## 模板规则

- 生成或更新需求卡前，必须先读取 `<feature_doc_template_path-docs/modules/_TEMPLATE.md>`。
- `<feature_doc_template_path-docs/modules/_TEMPLATE.md>` 是需求卡的唯一结构来源；不要在本 skill 中复刻模板标题、固定文案或占位字段。
- 新增需求卡时，以 `<feature_doc_template_path-docs/modules/_TEMPLATE.md>` 为骨架生成 `<feature_doc_path-docs/modules/<feature>.md>`。
- 更新已有需求卡时，先保留旧文档有效信息，再整理到当前模板结构下。
- 模板中的占位符必须替换为当前需求内容或“待确认”，不要把 `<...>` 原样留在最终需求卡中。
- 如果 `<feature_doc_template_path-docs/modules/_TEMPLATE.md>` 不存在或不可读，先停止生成需求卡，并向用户说明模板缺失或不可读。

## 输入来源

按用户实际提供的材料取用，不强行补齐所有项：

- 文字需求：业务目标、入口、按钮、状态、跳转、限制条件。
- 视觉材料：Figma、截图、原型图、标注图。
- 接口材料：接口路径、请求方法、请求参数、返回字段、状态码、错误文案、登录态依赖。
- 项目上下文：路由、相似旧页面、已有 `<feature_doc_glob-docs/modules/*.md>`。

## 执行步骤

1. 读取 `<feature_doc_template_path-docs/modules/_TEMPLATE.md>`，确认当前模板结构。
2. 判断用户提供的是单页面、单流程还是多页面模块。
3. 确定输出文件名，默认写入 `<feature_doc_path-docs/modules/<feature>.md>`。
4. 如果已有同名需求卡，先读取旧文档，按模板结构增量整理，不覆盖无关有效内容。
5. 必要时读取路由、相似页面或旧需求卡，只用于确认入口、页面归属和项目命名习惯。
6. 将材料归入模板对应位置；具体栏目以 `<feature_doc_template_path-docs/modules/_TEMPLATE.md>` 为准，不在 skill 中硬编码。
7. 写入或更新需求卡。
8. 最后说明生成 / 更新了哪些文档、哪些字段或流程仍待确认，并确认已使用需求卡模板。

## 拆分规则

- 单入口单页面：写一个 `<feature_doc_path-docs/modules/<feature>.md>`。
- 同一模块下多个明确页面：按页面拆分，主入口保留总览，子页面单独成文档。
- 同一页面包含列表、详情、弹窗、提交结果等复杂流程：优先写在同一需求卡内，用小节区分；只有成为独立页面时再拆文件。
- 接口文档很长但前端只用其中一部分：需求卡只摘当前页面需要的接口，并保留原接口文档路径或来源说明。

## 硬规则

- 不要凭空猜字段。接口材料没给出字段时，在需求卡里标为“待后端确认”。
- 不要把设计稿里不存在、用户也没描述的功能扩写成开发范围。
- 页面样式类需求要落到具体页面或区块；如果需求过多，按一个页面效果一张需求卡拆分。
- 如果用户提供 Figma 链接，只记录到需求卡；本技能不做设计稿回填，后续交给 `module-handUI` 或项目内对应视觉回填 skill。
- 接口内容按原文保留 `method`、`url`、字段名、枚举值和示例 JSON，不翻译字段名。

## 不负责的内容

- 页面开发、页面壳子、样式回填、接口接入、联调修复。
- 修改 `<project_router_file-src/router/index.js>`、`<project_router_modules_glob-src/router/modules/*.js>`、`<project_request_entry-src/utils/request.js>` 或业务页面。
- 根据不完整接口材料自行实现 mock 字段或前端字段映射。

## 收尾建议

- 给出已新增 / 更新的需求卡路径。
- 简要列出需求卡覆盖范围和待确认项。
- 下一步通常进入 `module-kickoff`；如果用户已经明确要开发，再按模块工作流继续。
