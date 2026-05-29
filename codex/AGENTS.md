# bd-frontend 项目指引（Codex）

本文件是 Codex 在本仓库的主入口。历史上的 Claude 相关配置保留在 `.claude/` 和 `CLAUDE.md` 中，只作为兼容参考，不再作为主维护入口。

## 默认协作方式

- 默认使用中文沟通。
- 代码、命令、路径、类型名、接口字段名保持原文。
- 做模块开发时，先读 `docs/modules/<feature>.md`，聊天里优先发文件路径，不要粘贴大段全文。
- 使用`.agents/skills/` 中的技能；

## 技术栈

- 框架：React 18 + TypeScript + Vite 5
- 路由：`react-router-dom` v6，`createBrowserRouter`，定义在 `src/router/index.tsx`
- 请求：Alova，唯一入口是 `src/utils/requests.ts`
- UI：Ant Design 5、`@ant-design/icons`、`styled-components`
- 状态：Zustand、ahooks、部分 `@alova/scene-react`

## 目录约定

- 页面：`src/pages/`，按业务域分目录，如 `User/`、`Home/`
- 布局与侧边栏：`src/Layout/`
- 路由与鉴权：`src/router/`
- 业务请求封装：`src/service/*.ts`
- 类型与领域模型：`src/models/`、`src/models/typings/`
- 公共组件与基础样式：`src/components/`、`src/components/Base/`
- 工具：`src/utils/`

## 本地开发

- 安装依赖：`yarn`
- 启动：`yarn dev`
- 构建：`yarn build`
- 检查：`yarn lint`

`vite.config.ts` 中配置了 `/buildapi`、`/projectapi`、`/userapi` 等代理，本地联调时需要后端可用或自行调整目标地址。

## 强约束

1. 新模块开始前，先找最像的旧页面，优先看 `src/pages/Application/**` 和 `src/pages/Iteration/**`。
2. 所有 HTTP 请求都必须经过 `src/utils/requests.ts`；业务方法写在 `src/service/*.ts`。
3. 类型放在 `src/models/typings/` 或该功能既有的 model 文件中。
4. 新路由在 `src/router/index.tsx` 中按现有 `RouteObject` / `TRouteItem` 风格注册。
5. 页面样式沿用 Ant Design + 同目录 `style.ts` + `styled-components` 的现有模式。

## 禁止事项

- 不要新增第二套全局请求封装，不要绕过 `@/utils/requests`。
- 不要用 `any` 掩盖接口结构。
- 不要在缺少接口契约时猜字段。
- 不要在未评审的情况下引入新的重型 UI 库。

## API 与错误处理

- 在 `src/service/*.ts` 中通过 `@/utils/requests` 导入默认 Alova 实例。
- 路径前缀与 `vite.config.ts` 的代理配置保持一致。
- 错误处理遵循项目已有的网络错误映射与 antd `message` 习惯。
- 不要提交真实 Token、密钥或敏感环境变量。

## UI 与样式习惯

- 优先复用 Ant Design 5 默认能力和现有页面布局组合。
- 页面局部样式放在页面目录下的 `style.ts`。
- 图标使用 `@ant-design/icons`。
- 图表对齐已有页面，例如 `DeployGraphs`。
- 如果 Figma 给了明确尺寸、色值、间距，按设计稿或需求卡标注实现，不要凭感觉猜。

## 高价值参考页

- 详情 + 子区块页面：`src/pages/Application/AppDetail`、`src/pages/Iteration/IterationDetail`
- 创建类表单：`src/pages/Application/AppCreate`
- 复杂内页：`src/pages/Iteration/DeployGraphs`

## 模块工作流

模块开发默认分五阶段：

1. Kickoff：阅读需求卡，找参考页，梳理路由、页面、service、types 的变更点，不写代码。
2. Scaffold：先搭页面壳子、路由占位、loading/empty、mock 数据。
3. API：补 types、service，并用真实接口替换 mock。
4. Polish：检查 loading / error / empty / success、文案、基本可访问性、lint，必要时 build。
5. Handoff：生成 `docs/modules/<feature>-handoff.md`，交代路由、主要文件、接口、限制和验证方式。

如果需求卡没有字段定义，且没有真实 JSON 样例、Swagger 或后端契约，必须先停下来补信息，再写类型。

## 技能入口

仓库级技能位于 `.agents/skills/`：

- `bd-fe-conventions`：项目规范
- `module-kickoff`：新模块启动
- `module-scaffold`：页面壳子阶段
- `module-api`：接口对接阶段
- `module-polish`：收口阶段
- `module-handoff`：交接文档阶段

