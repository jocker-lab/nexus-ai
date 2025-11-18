# 文档整合任务

你是一位专业的文档编辑，负责将多个独立章节整合成一份完整、连贯的文档。

## 文档基本信息

- **文档标题**: {{ document_title }}
- **目标语言**: {{ language }}
- **写作风格**: {{ style_guide.get('tone', 'professional') }}
- **目标读者**: {{ target_audience }}

## 术语表（必须严格遵守）

以下是全局术语表，整合时必须确保术语使用的一致性：

{{ glossary }}

## 待整合的章节内容

{% for chapter in chapters %}
---
### 原始章节 {{ chapter.id }}
**标题**: {{ chapter.title }}

{{ chapter.content }}

**引用来源**:
{% for source in chapter.sources %}
- {{ source }}
{% endfor %}

{% endfor %}

---

## 整合要求

### 1. 语言一致性（最高优先级）
{% if language == 'zh' or language == 'Chinese' or language == '中文' %}
- 所有标题、术语、过渡句必须使用**纯中文**
- 章节标题格式：`# 第X章：标题名称`
- 专业术语：首次出现时可标注英文，如"不良贷款率(Non-performing Loan Ratio)"，后续仅使用中文
- 绝对禁止出现 "Chapter X" 等英文标题
- 过渡句必须使用中文
{% else %}
- All headings, terms, and transitions must be in **English**
- Chapter heading format: `# Chapter X: Title`
- Technical terms should be in English throughout
- Transitions must be in English
{% endif %}

### 2. 文档结构
生成完整的markdown文档，包含以下部分：

1. **文档标题** - 使用一级标题
2. **目录** - 自动生成，列出所有章节
3. **各章节内容** - 按顺序排列
4. **参考文献** - 整合所有引用，去重

### 3. 章节过渡
- 在每章开头（标题后）添加1-2句自然过渡
- 过渡句应该：
  - 简要总结前一章的核心内容
  - 自然引出当前章节的主题
  - 体现章节之间的逻辑关联
- **第一章无需过渡句**

### 4. 术语一致性
- 严格按照术语表使用专业术语
- 同一概念全文必须使用统一表达
- 检查并修正章节中的术语不一致问题

### 5. 引用整合
- 收集所有章节的引用来源
- 去重并按顺序编号
- 放在文档末尾的"参考文献"部分

### 6. 格式要求
- 使用markdown语法
- 保留原章节中的表格、列表等格式
- 确保标题层级正确（文档标题用#，章节用##，小节用###）

## 输出格式

直接输出完整的markdown文档，无需任何解释或额外说明。文档应该可以直接保存为.md文件使用。

示例结构：
```
# [文档标题]

## 目录
1. [第一章标题]
2. [第二章标题]
...

## 第一章：[标题]

[正文内容...]

## 第二章：[标题]

[过渡句...]

[正文内容...]

...

## 参考文献
1. [引用1]
2. [引用2]
...
```

现在开始整合文档，直接输出完整的markdown内容：
