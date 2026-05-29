---
name: bd-fe-conventions
description: bd-frontend 前端规范与复用指南。在用户新增页面、从 Figma 实现 UI、对接后端 API、查找可复用组件时使用。
---

# bd-frontend 协作方式

## 必须先做

1. 用 Glob/Grep 找**最像的旧页面**，路径优先：`src/pages/Application/**`、`src/pages/Iteration/**`。
2. 所有 HTTP 请求必须经过 **`src/utils/requests.ts`** 创建的 Alova 实例；业务方法写在 **`src/service/*.ts`**，类型放在 **`src/models/typings/`**（或现有 `src/models` 中的约定文件）。
3. 新路由在 **`src/router/index.tsx`** 中按现有 `RouteObject`/`TRouteItem` 方式挂载；需鉴权时外层仍为 `WithGuard` 包裹的 `Layout`。
4. 页面样式与现有模块一致：Ant Design 组件 + **`styled-components`**，同目录 `style.ts` 可参考 `src/pages/Home`、`src/pages/Application/AppDetail`。

## 禁止

- 不新增第二套全局请求封装（禁止绕过 `@/utils/requests`）。
- 不使用 `any` 掩盖接口形状；无类型时从后端契约或现有 service typings 补齐，禁止猜测字段。
- 不引入新的重型 UI 库；沿用 Ant Design 5。

## references（需要时再 Read）

- `references/api-errors.md` — Alova 错误与 `message` 提示约定
- `references/ui-tokens.md` — 与本仓库一致的 UI/样式习惯

## 模块需求

单模块的需求卡、Figma 与接口表写在 **`docs/modules/<feature>.md`**；实现前优先 Read 该文件，不在对话中粘贴长文。

修改规范时**只改本 Skill 与 `references/`**。
