# Writing Task: Chapter {{ chapter_id }}

You are writing **Chapter {{ chapter_id }}: {{ chapter_outline.title }}** for the document "{{ document_outline.title }}".

---

## 1. Context & Scope
<info>
* **Purpose**: {{ document_outline.writing_purpose }}
* **Time**: {{ CURRENT_TIME }}
</info>

---

## 2. Structure Requirements
**Target Length**: ~{{ target_word_count }} words.

<subsection_plan>
{% for subsec in chapter_outline.subsections %}
### {{ loop.index }}. {{ subsec.sub_section_title }}
* **Guidance**: {{ subsec.description }}
{% endfor %}
</subsection_plan>

---

## 3. Reference Materials
<instruction>
Use the materials below. Keep URLs for the References section.
</instruction>

<search_results>
{{ search_results_text }}
</search_results>

---

## 4. Final Checklist
1.  **Start with Title**: The response **MUST** begin with `## {{ chapter_outline.title }}`.
2.  **Chart Position**: Charts must appear **inside** the relevant subsections, NOT at the top of the file.
3.  **Tool Output**: When `generate_chart` returns a JSON, extract the URL and embed it.

---

## 5. Response Output (Mandatory Template)

**Instruction**: You MUST strictly follow the structure below. Fill in the content where indicated.

```markdown
## {{ chapter_outline.title }}

[Write a brief introduction to the chapter here (100-200 words)...]

### 1. （一）[Subsection 1 Title]
[Write content for subsection 1...]
[If a chart is needed, insert it here: ![Title](url)]

### 2. （二）[Subsection 2 Title]
[Write content for subsection 2...]

... [Continue for all subsections] ...

### References
- [Source 1](url)
- [Source 2](url)
```

**Action**: Fill the template above to generate the complete chapter content.