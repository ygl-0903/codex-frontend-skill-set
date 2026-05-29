---
name: module-api
description: 接真实接口阶段使用的通用模版。根据需求说明与真实契约补齐 types、service 和页面真实请求，禁止臆测字段。
---

# 模块接接口

## 适用时机

- 页面壳子已存在
- 后端契约、Swagger、接口表或真实 JSON 样例已可用

## 目标与边界

- 目标是把现有页面从占位数据切到真实接口
- 只处理接口接入相关内容，不扩展到需求拆解、页面搭建或交互抛光

## 执行步骤

1. 读取 `docs/modules/<feature>.md` 中的接口说明。
2. 读取 `AGENTS.md`、`bd-fe-conventions` 以及 `<project_request_entry-src/utils/requests.ts>`。
3. 在 `<project_service_dir-src/service/>` 中新增或扩展接口方法。
4. 在 `<project_types_dir-src/models/typings/>` 或既有 model 文件中补齐类型定义。
5. 页面端使用项目现有的 `<request_library-Alova>` / `<frontend_framework-React>` 请求模式接入真实数据。
6. 替换上一轮的 mock 或占位数据。

## 硬规则

- 没有真实字段定义时，不要猜。
- 如果需求说明缺字段，而且没有真实 JSON 样例或后端契约，必须停下来要求补充。
- 错误提示与异常处理遵循项目既有 `<project_error_handling_pattern-message / 全局错误处理习惯>`。
- 单页只消费接口时，优先直接保存后端对象，不要为了中间层统一感额外搬运字段。
- 当前页面围绕某个选中对象展开时，优先直接保存 `selectedXxx` 对象，不要只存 id 再反查。
- 字段属于同一个业务对象时，保持对象归属，不要拆成多个顶层 `data` 状态。例如 `currentRound.passwordContent`、`currentRound.passwordObtainedTime`、`currentRound.passwordButtonEnabled` 应留在 `currentRound` 中；需要简化取值时用 `computed` 派生，不要复制字段导致状态不同步。
- 只有同一段接口解析逻辑在多个页面重复时，才考虑抽到 `utils/`。
- 添加必要注释，注释可以丰富一些

## 收尾建议

- 完成后列出本轮改动涉及的 service、types、页面文件路径。
- 如果还有未落地字段、联调阻塞项或契约缺口，明确标注并交给下一阶段处理。
