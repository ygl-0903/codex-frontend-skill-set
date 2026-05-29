---
name: module-kickoff
description: 新模块启动阶段使用的通用模版。读取需求卡、项目规范和参考页面，只做对齐、拆解和实施计划，不写业务代码。
---

# 模块启动

## 适用时机

- 新增一个模块或页面
- 从 Figma 和需求卡开始做第一轮对齐
- 需要先确认参考页、路由、service、types 的变更范围

## 目标与边界

- 目标是完成开工前的上下文对齐、参考页确认和实施范围拆解
- 这一轮只产出计划和风险提示，不写业务代码

## 执行步骤

1. 读取 `docs/modules/<feature>.md`。如果路径未知，先让用户给出路径。
2. 读取 `AGENTS.md` 与 `bd-fe-conventions` skill。
3. 在 `<project_pages_dir-src/pages/>` 下找最相近的旧模块，至少给出一类列表/表单参考和一类详情参考。
4. 输出实施计划：
   - `<project_router_file-src/router/index.tsx>` 可能的改动
   - 页面入口路径
   - `<project_service_dir-src/service/>` 与 `<project_types_dir-src/models/typings/>` 可能新增的位置
   - 可复用组件清单
5. 这一轮不写业务代码。

## 硬规则

- 只列路径和理由，不要粘贴大段代码。
- 如果 Figma 只有链接没有 node-id 或 frame 标识，要提醒补充。
- 不要把启动阶段扩展成页面搭建、接口接入或交互抛光。

## 收尾建议

- 结束时给出下一轮建议，通常进入 `module-scaffold`。
- 如果需求卡、Figma 标识、参考页或路由边界缺失，明确列为阻塞项。
