# UI 与样式习惯（bd-frontend）

本仓库**未单独维护 Design Token 文件**；从 Figma 还原时请：

1. **组件**：优先 Ant Design 5 默认值与现有页面的 `Space`、`Card`、`Button`、`Typography` 等组合。
2. **局部样式**：与同域页面一致，使用 `styled-components`，抽在页面目录下的 `style.ts`（参考 `src/pages/Home/style.ts`、`src/Layout/style.ts`）。
3. **图标**：`@ant-design/icons`。
4. **图表**：已有 `@ant-design/charts`；新图表对齐现有 `DeployGraphs` 等页面的用法。

若设计稿有明确色值/间距，以 Figma Dev Mode 或需求卡中的标注为准，避免凭感觉硬编码与全局主题冲突的值。
