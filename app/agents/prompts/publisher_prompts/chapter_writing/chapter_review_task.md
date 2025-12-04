# Task: Content Compliance & Quality Review

Please review the provided draft against the following project constraints and chapter specifications.

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
    <guidance>
    {{ chapter_outline.writing_guidance }}
    </guidance>
    {% endif %}

    {% if chapter_outline.content_requirements %}
    <content_requirements>
    {{ chapter_outline.content_requirements }}
    </content_requirements>
    {% endif %}

    {% if chapter_outline.subsections %}
    <subsection_structure>
    {% for sub in chapter_outline.subsections %}
        <subsection index="{{ loop.index }}">
            <title>{{ sub.sub_section_title }}</title>
            {% if sub.description %}<desc>{{ sub.description }}</desc>{% endif %}
            {% if sub.writing_guidance %}<guide>{{ sub.writing_guidance }}</guide>{% endif %}
            {% if sub.estimated_word_count %}<words>{{ sub.estimated_word_count }}</words>{% endif %}
        </subsection>
    {% endfor %}
    </subsection_structure>
    {% endif %}
</chapter_specifications>

<target_draft_to_review>
{{ draft }}
</target_draft_to_review>

---
**Instruction:**
Based on the **System Prompt** rules and the **Context/Specifications** provided above, evaluate the content in `<target_draft_to_review>`. 
Output the result in the strictly defined **JSON format**.