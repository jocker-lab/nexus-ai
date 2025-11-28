## Original Document

{{ document }}

---

## Review Summary

{{ general_feedback }}

## Specific Revision Suggestions

{% for suggestion in actionable_suggestions %}
{{ loop.index }}. {{ suggestion }}
{% endfor %}

---

## Task

Please revise the document based on the review feedback above.

**Requirements:**
- Address ALL the suggestions listed above
- Maintain the original chapter structure and formatting
- Keep the content in {{ language }}
- Output ONLY the revised complete document
