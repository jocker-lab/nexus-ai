

请对以下章节草稿进行专业审查，评估其是否符合写作要求与质量标准。
---

## 写作背景
---

## 文档信息

- **文档标题**: {{ document_outline.title }}
- **目标读者**: {{ document_outline.target_audience }}
- **写作风格**: {{ document_outline.writing_style }}
- **写作语调**: {{ document_outline.writing_tone }}
- **写作目的**: {{ document_outline.writing_purpose }}

---

## 章节要求

### {{ chapter_outline.title }}

**章节定位**: {{ chapter_outline.description }}

{% if chapter_outline.writing_guidance %}
**写作指导**: {{ chapter_outline.writing_guidance }}
{% endif %}

{% if chapter_outline.content_requirements %}
**内容要求**: {{ chapter_outline.content_requirements }}
{% endif %}

**目标字数**: {{ chapter_outline.estimated_words }} 字
**优先级**: {{ chapter_outline.writing_priority }}
{% if chapter_outline.visual_elements %}
**需要图表**: 是
{% endif %}

{% if chapter_outline.subsections %}
### 子章节结构
{% for sub in chapter_outline.subsections %}
#### {{ loop.index }}. {{ sub.sub_section_title }}
{% if sub.description %}- 定位: {{ sub.description }}{% endif %}
{% if sub.writing_guidance %}- 指导: {{ sub.writing_guidance }}{% endif %}
{% if sub.estimated_word_count %}- 字数: {{ sub.estimated_word_count }}{% endif %}
{% endfor %}
{% endif %}

---

## 待审查草稿
```
{{ draft }}
```
请直接输出结构化的审查结果。