# API 与错误处理（bd-frontend）

- **实例**：`src/utils/requests.ts` 导出默认 Alova 实例；`src/service/*.ts` 中 `import alovaInstance from "@/utils/requests"`。
- **业务错误展示**：项目内对 HTTP 状态做了 `handleNetworkError` 映射；全局行为以实现为准（常见为 antd `message`）。
- **新增接口**：在 service 中方法与路径需与后端一致；路径前缀与 `vite.config.ts` 的 `server.proxy` 一致（如 `/projectapi`、`/userapi`、`/buildapi`）。
- **不要**在仓库中提交真实 Token；环境相关仅本地或 CI 密钥管理。
