## 写作任务

请根据以下写作需求，生成匹配的专家角色与写作原则配置。

### 内容主题
- **标题**: {{ outline.title }}
{% if outline.subtitle %}- **副标题**: {{ outline.subtitle }}{% endif %}

### 核心主题
{% for theme in outline.key_themes %}
- {{ theme }}
{% endfor %}


### 写作规格
| 维度 | 要求 |
|------|------|
| 语言 | {{ outline.language }} |
| 风格 | {{ outline.writing_style }} |
| 语调 | {{ outline.writing_tone }} |
{% if outline.target_audience %}| 目标读者 | {{ outline.target_audience }} |{% endif %}
{% if outline.writing_purpose %}| 写作目的 | {{ outline.writing_purpose }} |{% endif %}

### 输出要求
根据上述写作任务，按照系统指定的JSON格式输出：
1. **role** - 最适配此任务的专家角色定位
2. **profile** - 该专家的背景、能力与优势（200-300字）
3. **writing_principles** - 3-7条该领域的核心写作原则