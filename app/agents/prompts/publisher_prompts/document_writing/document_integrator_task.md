# Integration Task

Integrate {{ total_chapters }} chapters into a complete document.

## Document Configuration

**Title**: {{ outline.title }}
{% if outline.subtitle %}
**Subtitle**: {{ outline.subtitle }}
{% endif %}

**Specifications**:
- Language: {{ outline.language }}
- Writing Style: {{ outline.writing_style }}
- Writing Tone: {{ outline.writing_tone }}
{% if outline.target_audience %}
- Target Audience: {{ outline.target_audience }}
{% endif %}
{% if outline.writing_purpose %}
- Purpose: {{ outline.writing_purpose }}
{% endif %}

---

## Chapter Content

{{ combined_chapters }}

## Execution

Follow your core workflow to:
1. Generate table of contents (TOC_LEVELS: 3)
2. Integrate all {{ total_chapters }} chapters with appropriate transitions
3. Consolidate references (CITATION_STYLE: APA-7-Hybrid)
4. Output the complete document directly (no meta-commentary)

Begin now.