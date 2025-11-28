## Writing Task

Complete {% if revision_needed %}revision{% else %}writing{% endif %} of **Chapter {{ chapter_id }}** for "{{ document_outline.title }}".

---

## Document Information

| Item | Content |
|------|---------|
| Target Audience | {{ document_outline.target_audience }} |
| Writing Style | {{ document_outline.writing_style }} |
| Tone | {{ document_outline.writing_tone }} |
| Core Purpose | {{ document_outline.writing_purpose }} |
| Language | {{ document_outline.language }} |
{% if document_outline.key_themes and document_outline.key_themes|length > 0 %}
| Key Themes | {{ document_outline.key_themes|join(', ') }} |
{% endif %}

---

## Chapter Context

This document contains {{ document_outline.sections|length }} chapters. You are writing **Chapter {{ chapter_id }}**.

{% if chapter_id > 1 %}
**Previous Chapter**: {{ document_outline.sections[chapter_id - 2].title }}
{% if document_outline.sections[chapter_id - 2].subsections %}
{% for subsec in document_outline.sections[chapter_id - 2].subsections %}- {{ subsec.sub_section_title }}
{% endfor %}{% endif %}
{% endif %}

**Current Chapter**: {{ chapter_outline.title }}
{% if chapter_outline.subsections %}
{% for subsec in chapter_outline.subsections %}- {{ subsec.sub_section_title }}
{% endfor %}{% endif %}

{% if chapter_id < document_outline.sections|length %}
**Next Chapter**: {{ document_outline.sections[chapter_id].title }}
{% if document_outline.sections[chapter_id].subsections %}
{% for subsec in document_outline.sections[chapter_id].subsections %}- {{ subsec.sub_section_title }}
{% endfor %}{% endif %}
{% endif %}

---

## Chapter Requirements

**Title**: {{ chapter_outline.title }}

**Positioning**: {{ chapter_outline.description }}

**Word Count**: {{ target_word_count }} words (±10% tolerance: {{ (chapter_outline.estimated_words * 0.9)|int }} - {{ (chapter_outline.estimated_words * 1.1)|int }} words)

{% if chapter_outline.writing_guidance %}
**Writing Guidance**: {{ chapter_outline.writing_guidance }}
{% endif %}

{% if chapter_outline.content_requirements %}
**Content Requirements**: {{ chapter_outline.content_requirements }}
{% endif %}

{% if chapter_outline.visual_elements %}
**Visualization**: Use `generate_chart` tool to create data visualizations
{% endif %}

{% if chapter_outline.subsections and chapter_outline.subsections|length > 0 %}
### Subsection Structure

Complete the following {{ chapter_outline.subsections|length }} subsections in order:

{% for subsec in chapter_outline.subsections %}
{{ loop.index }}. **{{ subsec.sub_section_title }}**{% if subsec.estimated_word_count %} (~{{ subsec.estimated_word_count }} words){% endif %}
{% if subsec.description %}   {{ subsec.description }}{% endif %}
{% if subsec.writing_guidance %}   Guidance: {{ subsec.writing_guidance }}{% endif %}

{% endfor %}

> ⚠️ Follow the exact subsection structure above. Do NOT add extra subsections (e.g., "Conclusion", "Summary"). Do NOT skip any subsection.
{% endif %}

---

{% if revision_needed and draft %}
## Current Draft

The following is your previous draft that needs improvement based on new search results:

<current_draft>
{{ draft }}
</current_draft>

---

## New Search Results

Use these new materials to supplement and improve the draft above:

<materials>
{{ search_results_text }}
</materials>

---

## Focus Areas

1. Supplement the missing or weak areas with new information
2. Integrate new content seamlessly into the existing draft
3. Ensure all content requirements are well-covered
4. Maintain paragraph quality (3-4 sentences minimum)
5. Add source references for new content
{% if visual_elements %}
6. Add or update charts to visualize key data using `generate_chart` tool
{% endif %}

{% elif search_results_text %}

## Research Materials

Cite selectively, integrate into argumentation, avoid info-dumping:

<materials>
{{ search_results_text }}
</materials>
{% endif %}

---

## Constraints

1. Word count MUST be within {{ (chapter_outline.estimated_words * 0.9)|int }} - {{ (chapter_outline.estimated_words * 1.1)|int }} range
2. Ensure smooth transitions with adjacent chapters
3. Facts must be accurate; content must be original
4. **MANDATORY**: End the chapter with a "### References" section listing all sources used
{% if revision_needed %}
5. **IMPORTANT**: Focus on supplementing weak areas with new search results
6. Integrate new content seamlessly - do not simply append
7. Preserve good content from the original draft
{% endif %}
{% if visual_elements %}
- Do NOT output Python code or tool invocation details in the final content
{% endif %}

---

## Expected Output Structure

```
## {{ chapter_outline.title }}

[Chapter content with subsections...]

### References

1. [Source Title](URL). *Source Name*.
2. [Source Title](URL). *Source Name*.
```

---

Output {% if revision_needed %}the improved{% endif %} chapter content directly in Markdown format.
