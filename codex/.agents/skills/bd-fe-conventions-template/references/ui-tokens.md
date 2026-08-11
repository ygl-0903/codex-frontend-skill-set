# UI 与样式习惯（<project_name-bd-frontend>）

## 使用边界

- 本文件只约束 UI 组件复用、图标来源、样式 token 和设计稿标注优先级；不规定接口、路由或业务拆分。
- `<ui_library-Ant Design 5>`、`<style_solution-styled-components>`、`<icon_library-@ant-design/icons>` 都是源项目示例。落地到目标项目时必须替换成真实技术栈；没有对应能力时删除相关规则。
- 如果目标项目有 Design Token、主题变量、组件库文档或视觉规范，优先使用那些资料；本文件只补充没有专门规范时的默认处理方式。

本仓库未单独维护一份 Design Token 文件时，默认遵循以下习惯：

1. 组件优先复用 `<ui_library-Ant Design 5>` 默认能力，与现有页面中的 `<ui_component_examples-Space、Card、Button、Typography>` 等组合保持一致。
2. 局部样式使用 `<style_solution-styled-components>`，抽到页面目录下的 `<page_style_file-style.ts>`。
3. 图标使用 `<icon_library-@ant-design/icons>`。
4. 新图表对齐现有图表页面的实现方式，例如 `<reference_chart_component-DeployGraphs>`。

如果 Figma 或需求卡中给了明确色值、间距、尺寸，以设计稿标注为准，不要凭感觉硬编码。

如果设计稿标注与目标项目已有 token 冲突，优先说明冲突并选择可维护的项目内方案；不要为了单页还原引入一套新的全局 token。
