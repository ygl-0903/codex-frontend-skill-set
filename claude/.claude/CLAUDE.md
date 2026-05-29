# bd-frontend（Building Deployment 前端）— AI 协作记忆

> 主维护入口已迁移到 `AGENTS.md`。本文件保留给历史 Claude 工作流和兼容场景使用。

本文件是「项目级事实源」的补充：技术栈、目录与禁忌。模块级需求（Figma、接口表、验收清单）放在 `docs/modules/<feature>.md`，对话里优先发该文件路径而非全文粘贴。

## 技术栈

- **框架**：React 18 + TypeScript + Vite 5
- **路由**：`react-router-dom` v6，`createBrowserRouter`，路由定义在 `src/router/index.tsx`
- **请求**：Alova（`createAlova` + `ReactHook` + `GlobalFetch`），**唯一入口** `src/utils/requests.ts`（通过 `@/utils/requests` 引用）
- **UI**：Ant Design 5、`@ant-design/icons`，样式以 `styled-components` + 页面内 `style.ts` 为主
- **状态**：Zustand、ahooks、部分 `@alova/scene-react`

## 目录约定

| 内容 | 路径 |
|------|------|
| 页面 | `src/pages/`（按域分子目录，如 `User/`、`Home/`） |
| 布局与侧边栏 | `src/Layout/` |
| 路由与鉴权包裹 | `src/router/`（含 `WithGuard`） |
| API 方法与业务请求封装 | `src/service/*.ts`（内部使用 `@/utils/requests` 导出的实例） |
| 类型与领域模型 | `src/models/`、`src/models/typings/` |
| 通用组件与基础样式 | `src/components/`、`src/components/Base/` |
| 工具 | `src/utils/` |

## 本地开发

- 安装依赖：`yarn`
- 启动：`yarn dev`（Vite；`vite.config.ts` 中配置了 `/buildapi`、`/projectapi`、`/userapi` 等代理，需本地后端或按需改 target）
- 构建与检查：`yarn build`、`yarn lint`

## 禁忌（除非产品/架构明确要求）

- **不要**新建第二套全局 HTTP 客户端；新接口走现有 Alova 实例与 `src/service/` 模式。
- **不要**在未评审的情况下引入新的 UI 框架或替换 Ant Design 体系。
- **不要**用 `any` 糊弄接口类型；类型以 `src/models/typings` 与后端契约为准，禁止臆测字段。

## 找「最像新模块」的参考页（复制结构时优先看）

- **带详情 + 子区块的页面**：`src/pages/Application/AppDetail`、`src/pages/Iteration/IterationDetail`
- **创建类表单**：`src/pages/Application/AppCreate`
- **复杂可视化/迭代内页**：`src/pages/Iteration/DeployGraphs`（含 `internals/`、`components/` 拆分）

