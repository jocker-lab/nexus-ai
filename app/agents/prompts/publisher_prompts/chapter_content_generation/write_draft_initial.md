# Writing Task: Chapter {{ chapter_id }}

You are writing **Chapter {{ chapter_id }}: {{ chapter_outline.title }}** for the document "{{ document_outline.title }}".

---

## 1. Context & Scope

<document_info>
* **Purpose**: {{ document_outline.writing_purpose }}
* **Target Audience**: {{ document_outline.target_audience }}
* **Key Themes**: {{ document_outline.key_themes|join(', ') }}
* **Time Perspective**: Current date is **{{ CURRENT_TIME }}**. Treat current quarter data as the latest fact.
</document_info>

<chapter_flow>
* **Current Chapter**: {{ chapter_outline.title }}
* **Positioning**: {{ chapter_outline.description }}
</chapter_flow>

---

## 2. Structure Requirements

**Target Length**: Aim for approximately **{{ target_word_count }} words**.

<subsection_plan>
Please strictly follow this outline:
{% for subsec in chapter_outline.subsections %}
### {{ loop.index }}. {{ subsec.sub_section_title }}
* **Guidance**: {{ subsec.description }} {{ subsec.writing_guidance }}
{% if subsec.estimated_word_count %}* **Est. Length**: ~{{ subsec.estimated_word_count }} words{% endif %}
{% endfor %}
</subsection_plan>

---

## 3. Reference Materials

<instruction>
Use the materials below.
* **Filter**: Ignore ads, navigation text, and irrelevant boilerplate.
* **URL Preservation**: Keep the URLs from these results for the References section.
</instruction>

{% if revision_needed and draft %}
<current_draft>
{{ draft }}
</current_draft>

<new_search_results>
{{ search_results_text }}
</new_search_results>

{% elif search_results_text %}
<search_results>
{{ search_results_text }}
</search_results>
{% endif %}

---

## 4. Final Checklist

1.  **Structure**: Did you start with `## {{ chapter_outline.title }}`?
2.  **Visualization**:
    {% if visual_elements %}
    * Call `generate_chart` for key data.
    * Embed the returned URL: `![Alt Text](url)`.
    * **NO Python code in text.**
    {% else %}
    * Text only.
    {% endif %}
3.  **References**: Ensure every reference includes its **Markdown Link** `[Title](URL)`.

## 5. Response Output (Mandatory Template)

**Step 1**: Write the Chapter Title: `## {{ chapter_outline.title }}`.
**Step 2**: Write the complete content following the `<subsection_plan>`.
**Step 3**: Append the `### References` section.

**Start writing now:**