# 占位符目录

本文件只在生成通用模版时按需参考。目标是统一占位符命名，避免同类信息在不同模版里出现多套写法。

## 命名规则

- 统一写成 `<snake_case_name>`
- 优先表达语义，不表达实现偏好
- 能抽象成“职责”就不要抽象成“框架名”

## 常用占位符

### 路径与目录

- `<project_pages_dir>`
- `<project_router_file>`
- `<project_service_dir>`
- `<project_types_dir>`
- `<project_layout_dir>`
- `<feature_doc_path>`
- `<feature_doc_glob>`
- `<project_request_entry>`

### 技术栈与基础设施

- `<frontend_framework>`
- `<router_library>`
- `<request_library>`
- `<state_library>`
- `<ui_library>`
- `<style_solution>`
- `<build_tool>`

### 参考实现

- `<reference_list_page_pattern>`
- `<reference_detail_page_pattern>`
- `<reference_form_page_pattern>`
- `<reference_complex_page_pattern>`

### 约束与约定

- `<api_contract_source>`
- `<project_error_handling_pattern>`
- `<project_route_registration_pattern>`
- `<project_component_split_rule>`

## 改写示例

- `src/pages/` -> `<project_pages_dir>`
- `src/router/index.tsx` -> `<project_router_file>`
- `src/utils/requests.ts` -> `<project_request_entry>`
- `docs/modules/<feature>.md` -> `<feature_doc_path>`
- `Ant Design + styled-components` -> `<ui_library> + <style_solution>`
- `Application/**` 中找参考页 -> `<reference_list_page_pattern>` 中找参考页

## 何时不要抽象

- “不要猜接口字段”
- “没有契约时先停下来补信息”
- “只列路径和理由，不贴大段代码”
- “结束时给出下一阶段建议”

这类是流程约束，不是项目绑定项，通常应直接保留。
