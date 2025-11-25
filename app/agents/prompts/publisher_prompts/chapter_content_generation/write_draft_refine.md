---
CURRENT_TIME: {{ CURRENT_TIME }}
---

# Refine Draft

## Chapter Information

**Chapter Title**: {{ chapter_title }}

**Chapter Description**:
{{ description }}

**Content Requirements**:
{{ content_requirements }}

---

## Current Draft

{{ draft }}

---

## New Search Results

Use these to supplement the draft:

{{ search_results_text }}

---

## Task

Improve and expand the current draft using the new search results.

**Target Word Count**: Approximately {{ target_word_count }} words

## Focus Areas

1. Supplement the missing or weak areas with new information
2. Integrate new content seamlessly into the existing draft
3. Ensure all content requirements are well-covered
4. Maintain paragraph quality (3-4 sentences minimum)
5. Add source references for new content
{% if visual_elements %}
6. Add or update charts to visualize key data using `generate_chart` tool
{% endif %}

{% if visual_elements %}
## Chart Generation

If the new search results contain data suitable for visualization:
- Create new charts for important statistics or comparisons
- Update existing charts if more accurate data is available
- Place charts at relevant positions within the content

Use the `generate_chart` tool and embed the resulting URL in your content using Markdown image syntax.
{% endif %}

Output the improved draft.
