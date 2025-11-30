# TODO List

## 待解决问题

### 1. TEMPLATE_SEARCH 的用户选择交互问题

**问题描述：**
当 `execute_template_search_node` 搜到多个模版时，需要让用户选择。但目前的流程是：
1. `TEMPLATE_SEARCH` 执行完，结果存到 `completed_steps`
2. Planner 规划一个 `HUMAN_INVOLVEMENT` 让用户选
3. `execute_human_involvement_node` 只是用 LLM 生成一段对话文字

**问题：**
- 用户看到的只是 LLM 生成的描述性文字
- 没有结构化的选项供用户选择
- 前端无法渲染成可点击的模版卡片

**可选方案：**

**方案 A：在 `execute_template_search_node` 里直接 interrupt（推荐）**
- 如果搜到多个模版，直接在这个节点里 `interrupt`
- 把模版列表作为结构化数据传给前端
- 前端渲染成卡片让用户点选
- 优点：简单直接，模版选择是 TEMPLATE_SEARCH 步骤的一部分

```python
interrupt_payload = {
    "type": "template_selection",
    "templates": templates,  # 完整的模版列表
    "message": "找到了多个匹配模版，请选择一个",
}
user_choice = interrupt(interrupt_payload)
```

**方案 B：保持现有流程，HUMAN_INVOLVEMENT 传递结构化数据**
- `execute_template_search_node` 的 `execution_res` 里存 JSON
- `execute_human_involvement_node` 检测到是模版选择场景时，解析 JSON 传给前端
- 缺点：流程复杂，需要两个节点配合

**状态：** 待讨论决定

---

## 已完成

### 模版系统 v1.0
- [x] 模版提取（LLM 提取结构 + 百分比）
- [x] 模版存储（Milvus + SQL）
- [x] 模版搜索（语义检索）
- [x] `TEMPLATE_SEARCH` StepType 和执行节点
- [x] Planner prompt 更新
- [x] `estimated_words` 改为 `estimated_percentage`
