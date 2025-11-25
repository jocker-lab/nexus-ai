---
CURRENT_TIME: {{ CURRENT_TIME }}
---

# Write Initial Draft

## Chapter Information

**Chapter Title**: {{ chapter_title }}

**Chapter Description**:
{{ description }}

**Content Requirements**:
{{ content_requirements }}

**Writing Guidance**:
{{ writing_guidance }}

---

## Search Results

{{ search_results_text }}

---

## Task

Write the initial draft for this chapter.

**Target Word Count**: Approximately {{ target_word_count }} words

## Requirements

1. Cover all content requirements comprehensively
2. Follow the writing guidance for style and focus
3. Use Markdown format with proper headings (##, ###)
4. Each paragraph must have 3-4 sentences minimum
5. Base content on search results; mark gaps as "【To be supplemented】"
6. Include source references where applicable
7. Target approximately {{ target_word_count }} words
{% if visual_elements %}
8. **Charts**: Use `generate_chart` tool to create visualizations for key data points, trends, or comparisons
{% endif %}

{% if visual_elements %}
## Chart Generation

When appropriate, create charts to visualize:
- Statistical data and trends
- Comparisons between different items
- Distribution or composition data
- Timeline or progression data

Use the `generate_chart` tool and embed the resulting URL in your content using Markdown image syntax.
{% endif %}

Output the draft content now.
