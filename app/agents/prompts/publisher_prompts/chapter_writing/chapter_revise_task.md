# Revision Task Input Data

<project_context>
    <title>{{ document_outline.title }}</title>
    <target_audience>{{ document_outline.target_audience }}</target_audience>
    <style>{{ document_outline.writing_style }}</style>
    <tone>{{ document_outline.writing_tone }}</tone>
    <purpose>{{ document_outline.writing_purpose }}</purpose>
</project_context>

<chapter_specifications>
    <title>{{ chapter_outline.title }}</title>
    <description>{{ chapter_outline.description }}</description>
    <priority>{{ chapter_outline.writing_priority }}</priority>
    <target_word_count>{{ chapter_outline.estimated_words }}</target_word_count>
    <visuals_required>{% if chapter_outline.visual_elements %}Yes{% else %}No{% endif %}</visuals_required>
    
    {% if chapter_outline.writing_guidance %}
    <guidance>{{ chapter_outline.writing_guidance }}</guidance>
    {% endif %}

    {% if chapter_outline.content_requirements %}
    <content_requirements>{{ chapter_outline.content_requirements }}</content_requirements>
    {% endif %}

    {% if chapter_outline.subsections %}
    <subsection_structure>
    {% for sub in chapter_outline.subsections %}
        <subsection index="{{ loop.index }}">
            <title>{{ sub.sub_section_title }}</title>
            <desc>{{ sub.description }}</desc>
        </subsection>
    {% endfor %}
    </subsection_structure>
    {% endif %}
</chapter_specifications>

<target_draft_to_review>
{{ draft }}
</target_draft_to_review>

<review_feedback>
    <overall_assessment>
        {{ review_result.general_feedback }}
    </overall_assessment>

    <actionable_checklist>
    {% for suggestion in review_result.actionable_suggestions %}
        <item index="{{ loop.index }}">{{ suggestion }}</item>
    {% endfor %}
    </actionable_checklist>
</review_feedback>

---
**Instruction:** 1. Read the `<overall_assessment>` to understand the revision context.
2. STRICTLY execute every item in the `<actionable_checklist>` to revise the `<target_draft_to_review>`.
3. Ensure the result aligns with `<project_context>` and `<chapter_specifications>`.
4. Output the revised text directly.