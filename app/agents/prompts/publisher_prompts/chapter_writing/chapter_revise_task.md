## Original Draft

{{ draft }}

---

## Review Summary

{{ general_feedback }}

## Specific Revision Suggestions

{% for suggestion in actionable_suggestions %}
{{ loop.index }}. {{ suggestion }}
{% endfor %}

---

## Task

Please revise the draft based on the review feedback above.

**Requirements:**
- Address ALL the suggestions listed above
- Maintain the original structure and formatting
- Keep the content in {{ language | default('zh-CN') }}
- Output ONLY the revised complete chapter content
