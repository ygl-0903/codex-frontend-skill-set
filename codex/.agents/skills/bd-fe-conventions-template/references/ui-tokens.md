# UI 与样式习惯（<project_name-bd-frontend>）

本仓库未单独维护一份 Design Token 文件时，默认遵循以下习惯：

1. 组件优先复用 `<ui_library-Ant Design 5>` 默认能力，与现有页面中的 `<ui_component_examples-Space、Card、Button、Typography>` 等组合保持一致。
2. 局部样式使用 `<style_solution-styled-components>`，抽到页面目录下的 `<page_style_file-style.ts>`。
3. 图标使用 `<icon_library-@ant-design/icons>`。
4. 新图表对齐现有图表页面的实现方式，例如 `<reference_chart_component-DeployGraphs>`。

如果 Figma 或需求卡中给了明确色值、间距、尺寸，以设计稿标注为准，不要凭感觉硬编码。
