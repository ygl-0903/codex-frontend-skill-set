# API 与错误处理（<project_name-bd-frontend>）

## 使用边界

- 本文件只约束请求封装、service、接口契约、错误展示和敏感信息处理；不规定页面结构、CSS 命名或 UI 组件选型。
- 先以 `AGENTS.md` 和目标项目真实请求入口为准。这里的 `<placeholder-source_example>` 只用于提示替换位置，不能当成项目事实。
- 如果目标项目没有统一请求入口，先向用户指出缺口；不要在业务代码里临时新建第二套全局封装。

- 实例：`<project_request_entry-src/utils/requests.ts>` 导出默认 `<request_library-Alova>` 实例；`<project_service_glob-src/service/*.ts>` 中通过 `<request_import_alias-@/utils/requests>` 导入。
- 业务错误展示：项目内对 HTTP 状态已有映射；常见交互为 `<project_error_feedback-antd message>`，以现有实现为准。
- 新增接口：service 中的方法、路径、参数与后端契约保持一致，路径前缀与 `<build_config_file-vite.config.ts>` 的 `<dev_proxy_config-server.proxy>` 对齐。
- 不要提交真实 Token；环境相关信息仅保留在本地或 CI 密钥管理中。

## 停止条件

- 缺少接口 method、url、入参、返回字段或错误码契约时，不要猜字段；在需求卡、交付说明或待确认项中标明缺口。
- 现有项目存在多套请求封装且无法判断应沿用哪套时，先停止并请用户或项目维护者确认。
