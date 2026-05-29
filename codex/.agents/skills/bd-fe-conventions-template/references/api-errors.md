# API 与错误处理（<project_name-bd-frontend>）

- 实例：`<project_request_entry-src/utils/requests.ts>` 导出默认 `<request_library-Alova>` 实例；`<project_service_glob-src/service/*.ts>` 中通过 `<request_import_alias-@/utils/requests>` 导入。
- 业务错误展示：项目内对 HTTP 状态已有映射；常见交互为 `<project_error_feedback-antd message>`，以现有实现为准。
- 新增接口：service 中的方法、路径、参数与后端契约保持一致，路径前缀与 `<build_config_file-vite.config.ts>` 的 `<dev_proxy_config-server.proxy>` 对齐。
- 不要提交真实 Token；环境相关信息仅保留在本地或 CI 密钥管理中。
